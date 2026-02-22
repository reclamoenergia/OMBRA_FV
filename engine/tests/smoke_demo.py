import sys
from pathlib import Path
import csv

root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

from demo.generate_demo_data import write_demo_shapefile
from shadow.calendar import Turbine, run_calendar

project_dir = root / 'demo'
write_demo_shapefile(project_dir)
out = run_calendar(
    project_dir=project_dir,
    aoi_path=str(project_dir / 'aoi_demo.shp'),
    project_epsg=32633,
    turbines=[
        Turbine('T1', 500200, 4649800, 110, 140),
        Turbine('T2', 500450, 4649850, 100, 130),
    ],
    min_solar_elevation_deg=0,
)
assert Path(out['csv_path']).exists()
assert Path(out['animation_data_path']).exists()
with open(out['csv_path'], encoding='utf-8') as f:
    rows = list(csv.DictReader(f))
assert len(rows) > 0
print('smoke ok', len(rows))
