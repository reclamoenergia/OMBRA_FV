from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import csv
import json

import fiona
from shapely.geometry import shape
from shapely.ops import unary_union

from .geometry import build_transformer, to_latlon
from .shadow_footprint import shadow_ellipse
from .solar import sun_position

TZ = ZoneInfo('Europe/Rome')


@dataclass
class Turbine:
    turbine_id: str
    x: float
    y: float
    hub_height_m: float
    rotor_diameter_m: float


def load_aoi_polygon(shp_path: str):
    geoms = []
    with fiona.open(shp_path) as src:
        for feat in src:
            geoms.append(shape(feat['geometry']))
    return unary_union(geoms)


def run_calendar(
    project_dir: Path,
    aoi_path: str,
    project_epsg: int,
    turbines: list[Turbine],
    min_solar_elevation_deg: float,
    year: int = 2025,
    on_progress=None,
):
    outputs_dir = project_dir / 'outputs'
    outputs_dir.mkdir(parents=True, exist_ok=True)
    csv_path = outputs_dir / 'shadow_calendar.csv'
    anim_path = outputs_dir / 'animation_data.json'

    aoi = load_aoi_polygon(aoi_path)
    bbox = aoi.bounds
    transformer = build_transformer(project_epsg)

    start = datetime(year, 1, 1, 0, 0, tzinfo=TZ)
    end = datetime(year + 1, 1, 1, 0, 0, tzinfo=TZ)
    total_steps = int((end - start).total_seconds() // (15 * 60))
    hits = []
    anim = {'days': {}, 'meta': {'year': year, 'min_solar_elevation_deg': min_solar_elevation_deg, 'project_epsg': project_epsg}}

    ts = start
    step = 0
    while ts < end:
        for t in turbines:
            lat, lon = to_latlon(transformer, t.x, t.y)
            az, el = sun_position(lat, lon, ts)
            if el <= min_solar_elevation_deg:
                continue
            poly, center, major, minor, rot_deg = shadow_ellipse(
                t.x, t.y, t.hub_height_m, t.rotor_diameter_m, az, el
            )
            pb = poly.bounds
            intersects = not (pb[2] < bbox[0] or pb[0] > bbox[2] or pb[3] < bbox[1] or pb[1] > bbox[3]) and poly.intersects(aoi)
            day = ts.strftime('%Y-%m-%d')
            day_obj = anim['days'].setdefault(day, {'timesteps': {}, 'has_hit': False})
            tkey = ts.isoformat()
            frame = day_obj['timesteps'].setdefault(tkey, {'sun': {'azimuth_deg': az, 'elevation_deg': el}, 'turbines': []})
            frame['turbines'].append({
                'turbine_id': t.turbine_id,
                'center': [center[0], center[1]],
                'major_m': major,
                'minor_m': minor,
                'rotation_deg': rot_deg,
                'intersects_aoi': intersects,
            })
            if intersects:
                day_obj['has_hit'] = True
                hits.append(
                    {
                        'turbine_id': t.turbine_id,
                        'timestamp_local': ts.isoformat(),
                        'date': ts.strftime('%Y-%m-%d'),
                        'time': ts.strftime('%H:%M'),
                        'sun_azimuth_deg': round(az, 5),
                        'sun_elevation_deg': round(el, 5),
                    }
                )
        step += 1
        if on_progress and step % 200 == 0:
            on_progress(min(99, int(step * 100 / total_steps)), f'Processed {step}/{total_steps} timesteps')
        ts += timedelta(minutes=15)

    with csv_path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['turbine_id', 'timestamp_local', 'date', 'time', 'sun_azimuth_deg', 'sun_elevation_deg'])
        w.writeheader()
        w.writerows(hits)

    computed_days = []
    filtered_days = {}
    for d, payload in anim['days'].items():
        if payload['has_hit']:
            computed_days.append(d)
            filtered_days[d] = payload
    anim['days'] = filtered_days
    computed_days.sort()

    with anim_path.open('w', encoding='utf-8') as f:
        json.dump(anim, f)

    if on_progress:
        on_progress(100, 'Completed')
    return {'csv_path': str(csv_path), 'animation_data_path': str(anim_path), 'computed_days': computed_days, 'rows': len(hits)}
