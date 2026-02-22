from pyproj import CRS, Transformer


def build_transformer(project_epsg: int) -> Transformer:
    src = CRS.from_epsg(project_epsg)
    dst = CRS.from_epsg(4326)
    return Transformer.from_crs(src, dst, always_xy=True)


def to_latlon(transformer: Transformer, x: float, y: float) -> tuple[float, float]:
    lon, lat = transformer.transform(x, y)
    return lat, lon
