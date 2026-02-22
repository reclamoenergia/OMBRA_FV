import { useMemo, useState } from 'react';
import { MapContainer, TileLayer, Polygon, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

type Turbine = { id: string; x: number; y: number; hub_height_m: number; rotor_diameter_m: number };

export function App() {
  const [epsg, setEpsg] = useState('32633');
  const [minEl, setMinEl] = useState(0);
  const [turbines, setTurbines] = useState<Turbine[]>([]);
  const [status, setStatus] = useState('idle');
  const [aoi, setAoi] = useState<[number, number][]>([[41.95, 12.45], [41.95, 12.52], [41.99, 12.52], [41.99, 12.45]]);

  const csvTemplate = 'id;x;y;hub_height_m;rotor_diameter_m\nT1;500200;4649800;110;140';
  const mapCenter = useMemo<[number, number]>(() => [41.97, 12.48], []);

  const onCsv = async (f: File) => {
    const txt = await f.text();
    const rows = txt.trim().split(/\r?\n/);
    const parsed = rows.slice(1).map((r) => {
      const [id, x, y, hub, rotor] = r.split(';');
      return { id, x: Number(x), y: Number(y), hub_height_m: Number(hub), rotor_diameter_m: Number(rotor) };
    });
    setTurbines(parsed.slice(0, 20));
  };

  return (
    <div className='h-full grid grid-cols-3'>
      <div className='p-4 space-y-3 border-r overflow-auto'>
        <h1 className='text-xl font-semibold'>Wind Shadow Calendar Studio</h1>
        <label className='block'>EPSG<input className='border ml-2' value={epsg} onChange={(e) => setEpsg(e.target.value)} /></label>
        <label className='block'>min_solar_elevation_deg<input className='border ml-2' type='number' value={minEl} onChange={(e) => setMinEl(Number(e.target.value))} /></label>
        <div>
          <div className='font-medium'>Carica turbine CSV (;)</div>
          <input type='file' accept='.csv' onChange={(e) => e.target.files && onCsv(e.target.files[0])} />
          <pre className='text-xs bg-gray-100 p-2 mt-2'>{csvTemplate}</pre>
        </div>
        <button className='px-3 py-2 bg-blue-600 text-white rounded' onClick={() => setStatus('would call POST /calendar/run')}>Avvia calcolo</button>
        <button className='px-3 py-2 bg-emerald-600 text-white rounded' onClick={() => {
          const c = document.createElement('canvas'); c.width = 1280; c.height = 720; const ctx = c.getContext('2d')!; ctx.fillStyle = '#111'; ctx.fillRect(0,0,c.width,c.height); ctx.fillStyle='#fff'; ctx.fillText('Wind Shadow Calendar Studio export placeholder', 50, 50); c.toBlob((b)=>{if(!b)return;const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download='animation-frame.png';a.click();},'image/png');
        }}>Export video</button>
        <div className='text-xs text-gray-600'>Status: {status}</div>
        <div className='text-xs'>Turbine: {turbines.length}/20</div>
      </div>
      <div className='col-span-2 h-full'>
        <MapContainer center={mapCenter} zoom={13} style={{ height: '100%', width: '100%' }}>
          <TileLayer attribution='© OpenStreetMap contributors' url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' />
          <Polygon positions={aoi} pathOptions={{ color: 'orange' }} />
          {turbines.map((t) => (
            <Marker key={t.id} position={mapCenter}>
              <Popup>{t.id}</Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}
