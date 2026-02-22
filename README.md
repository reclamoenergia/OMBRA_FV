# Wind Shadow Calendar Studio

Desktop app (Tauri v2 + React + TypeScript + Tailwind) with local Python engine (FastAPI) to compute wind-turbine shadow calendar on a flat surface.

## Main flow
1. Create/open project (`*.wscsproj.json`).
2. Load AOI shapefile (`.shp/.shx/.dbf/.prj`).
3. Import turbines CSV with separator `;` and headers `id;x;y;hub_height_m;rotor_diameter_m`.
4. Set `min_solar_elevation_deg`.
5. Run calendar (15-minute timestep, timezone Europe/Rome, fixed year=2025).
6. Export CSV results and view animation.
7. Export animation video (WebM strategy; minimal placeholder in current UI scaffold).

## Limits
- Max 20 turbines.
- Fixed timestep: 15 minutes.
- Timezone fixed to Europe/Rome.

## OSM attribution
Map tiles use OpenStreetMap and attribution must always be visible:
`© OpenStreetMap contributors`.

## Demo mode
Per evitare errori PR web con file binari, i file demo shapefile vengono **generati localmente** da script.

Demo files in repo:
- `engine/demo/generate_demo_data.py`
- `engine/demo/turbines_demo.csv`
- `engine/demo/project_demo.wscsproj.json`

Genera shapefile demo (`aoi_demo.shp/.shx/.dbf/.prj`):
```bash
cd engine
python demo/generate_demo_data.py
```

Run smoke demo:
```bash
cd engine
python tests/smoke_demo.py
```

## Windows installer from GitHub Actions
Use workflow `.github/workflows/windows-build.yml`.
Artifacts include:
- Tauri installer (`.msi`/`.exe`)
- `checksums.txt`

Download artifacts from Actions run page.
