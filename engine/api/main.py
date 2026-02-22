from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from pathlib import Path
from uuid import uuid4
from threading import Thread, Lock
from datetime import datetime

from shadow.calendar import Turbine, run_calendar

app = FastAPI(title='Wind Shadow Calendar Engine')

jobs = {}
lock = Lock()


class TurbineIn(BaseModel):
    turbine_id: str = Field(alias='id')
    x: float
    y: float
    hub_height_m: float
    rotor_diameter_m: float


class RunRequest(BaseModel):
    project_dir: str
    aoi_path: str
    project_epsg: int
    min_solar_elevation_deg: float = 0.0
    turbines: list[TurbineIn]


@app.get('/health')
def health():
    return {'status': 'ok', 'time': datetime.utcnow().isoformat()}


@app.post('/calendar/run')
def run(req: RunRequest):
    if len(req.turbines) > 20:
        raise HTTPException(400, 'max 20 turbines')
    job_id = str(uuid4())
    with lock:
        jobs[job_id] = {'status': 'running', 'progress_pct': 0, 'progress_message': 'Queued', 'logs': [], 'outputs': {}, 'error': None, 'computed_days': []}

    def worker():
        try:
            def progress(pct, msg):
                with lock:
                    jobs[job_id]['progress_pct'] = pct
                    jobs[job_id]['progress_message'] = msg
                    jobs[job_id]['logs'].append(msg)

            out = run_calendar(
                project_dir=Path(req.project_dir),
                aoi_path=req.aoi_path,
                project_epsg=req.project_epsg,
                turbines=[Turbine(**t.model_dump()) for t in req.turbines],
                min_solar_elevation_deg=req.min_solar_elevation_deg,
                on_progress=progress,
            )
            with lock:
                jobs[job_id]['status'] = 'done'
                jobs[job_id]['outputs'] = out
                jobs[job_id]['computed_days'] = out['computed_days']
        except Exception as e:
            with lock:
                jobs[job_id]['status'] = 'error'
                jobs[job_id]['error'] = str(e)
                jobs[job_id]['logs'].append(str(e))

    Thread(target=worker, daemon=True).start()
    return {'job_id': job_id}


@app.get('/calendar/jobs/{job_id}')
def status(job_id: str):
    with lock:
        j = jobs.get(job_id)
    if not j:
        raise HTTPException(404, 'job not found')
    return j


@app.get('/files/{job_id}/{kind}')
def files(job_id: str, kind: str):
    with lock:
        j = jobs.get(job_id)
    if not j:
        raise HTTPException(404, 'job not found')
    mapping = {'csv': 'csv_path', 'animation': 'animation_data_path'}
    key = mapping.get(kind)
    if not key:
        raise HTTPException(400, 'kind must be csv|animation')
    path = j.get('outputs', {}).get(key)
    if not path:
        raise HTTPException(404, 'file missing')
    return FileResponse(path)
