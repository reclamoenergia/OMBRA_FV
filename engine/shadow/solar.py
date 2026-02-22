from datetime import datetime
from zoneinfo import ZoneInfo
from pysolar.solar import get_azimuth, get_altitude

TZ = ZoneInfo('Europe/Rome')


def sun_position(lat: float, lon: float, ts_local: datetime) -> tuple[float, float]:
    if ts_local.tzinfo is None:
        ts_local = ts_local.replace(tzinfo=TZ)
    ts_utc = ts_local.astimezone(ZoneInfo('UTC'))
    az = float(get_azimuth(lat, lon, ts_utc))
    el = float(get_altitude(lat, lon, ts_utc))
    return az % 360.0, el
