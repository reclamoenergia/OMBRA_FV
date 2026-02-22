"""Generate demo AOI shapefile set locally (not committed as binary)."""
from __future__ import annotations

import struct
import datetime as dt
from pathlib import Path


def write_demo_shapefile(out_dir: Path, stem: str = 'aoi_demo') -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pts = [
        (500000.0, 4649700.0),
        (501100.0, 4649700.0),
        (501100.0, 4650400.0),
        (500000.0, 4650400.0),
        (500000.0, 4649700.0),
    ]
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    num_parts = 1
    num_points = len(pts)
    content = struct.pack('<i', 5)
    content += struct.pack('<4d', xmin, ymin, xmax, ymax)
    content += struct.pack('<2i', num_parts, num_points)
    content += struct.pack('<i', 0)
    for x, y in pts:
        content += struct.pack('<2d', x, y)
    content_len_words = len(content) // 2

    shp_header = struct.pack('>6i', 9994, 0, 0, 0, 0, 0)
    shp_header += struct.pack('>i', 50 + 4 + content_len_words)
    shp_header += struct.pack('<2i', 1000, 5)
    shp_header += struct.pack('<4d', xmin, ymin, xmax, ymax)
    shp_header += struct.pack('<4d', 0, 0, 0, 0)

    shp_path = out_dir / f'{stem}.shp'
    with shp_path.open('wb') as f:
        f.write(shp_header)
        f.write(struct.pack('>2i', 1, content_len_words))
        f.write(content)

    shx_header = struct.pack('>6i', 9994, 0, 0, 0, 0, 0)
    shx_header += struct.pack('>i', 50 + 4)
    shx_header += struct.pack('<2i', 1000, 5)
    shx_header += struct.pack('<4d', xmin, ymin, xmax, ymax)
    shx_header += struct.pack('<4d', 0, 0, 0, 0)

    shx_path = out_dir / f'{stem}.shx'
    with shx_path.open('wb') as f:
        f.write(shx_header)
        f.write(struct.pack('>2i', 50, content_len_words))

    now = dt.datetime.now()
    num_records = 1
    header_len = 32 + 32 + 1
    rec_len = 1 + 5
    dbf_path = out_dir / f'{stem}.dbf'
    with dbf_path.open('wb') as f:
        f.write(struct.pack('<BBBBIHH20x', 3, now.year - 1900, now.month, now.day, num_records, header_len, rec_len))
        field_name = b'ID' + b'\x00' * 9
        f.write(struct.pack('<11sc4xBB14x', field_name, b'N', 5, 0))
        f.write(b'\r')
        f.write(b' ' + b'1'.rjust(5))

    prj_path = out_dir / f'{stem}.prj'
    prj_path.write_text(
        'PROJCS["WGS 84 / UTM zone 33N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",15],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1]]',
        encoding='utf-8',
    )


if __name__ == '__main__':
    write_demo_shapefile(Path(__file__).resolve().parent)
    print('Demo shapefile generated.')
