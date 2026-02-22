import math
from shapely.geometry import Polygon


def shadow_ellipse(
    x: float,
    y: float,
    hub_height_m: float,
    rotor_diameter_m: float,
    sun_azimuth_deg: float,
    sun_elevation_deg: float,
    vertices: int = 48,
) -> tuple[Polygon, tuple[float, float], float, float, float]:
    elev_rad = math.radians(max(sun_elevation_deg, 0.01))
    r = rotor_diameter_m / 2.0
    major = max(rotor_diameter_m, rotor_diameter_m / max(math.sin(elev_rad), 1e-3))
    minor = rotor_diameter_m
    shadow_len = hub_height_m / math.tan(elev_rad)
    theta = math.radians((sun_azimuth_deg + 180.0) % 360.0)
    cx = x + shadow_len * math.sin(theta)
    cy = y + shadow_len * math.cos(theta)
    rot = math.radians((sun_azimuth_deg + 90.0) % 360.0)

    pts = []
    a = major / 2.0
    b = minor / 2.0
    for i in range(vertices):
        t = 2 * math.pi * i / vertices
        ex = a * math.cos(t)
        ey = b * math.sin(t)
        px = cx + ex * math.cos(rot) - ey * math.sin(rot)
        py = cy + ex * math.sin(rot) + ey * math.cos(rot)
        pts.append((px, py))
    return Polygon(pts), (cx, cy), major, minor, math.degrees(rot)
