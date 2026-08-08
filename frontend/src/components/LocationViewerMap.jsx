import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import { HiOutlineLocationMarker } from 'react-icons/hi';

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

function MapRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center && center[0] && center[1]) {
      map.setView(center, 15);
    }
  }, [center, map]);
  return null;
}

export default function LocationViewerMap({ location }) {
  if (!location) return null;

  const hasCoords = location.latitude !== null && location.latitude !== undefined && location.longitude !== null && location.longitude !== undefined;

  return (
    <div className="card p-5 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wider flex items-center gap-1">
          <HiOutlineLocationMarker className="w-4 h-4 text-primary-600" />
          Location & Pinned Map
        </h3>
        {hasCoords && (
          <span className="text-[11px] font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">
            GPS Verified
          </span>
        )}
      </div>

      <p className="text-sm font-medium text-slate-800 leading-snug">{location.text || 'Location provided'}</p>

      {hasCoords ? (
        <div className="h-56 w-full rounded-xl overflow-hidden border border-slate-200 shadow-inner mt-2 relative z-0">
          <MapContainer
            center={[location.latitude, location.longitude]}
            zoom={15}
            style={{ height: '100%', width: '100%' }}
            scrollWheelZoom={false}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            <MapRecenter center={[location.latitude, location.longitude]} />
            <Marker position={[location.latitude, location.longitude]}>
              <Popup>
                <div className="text-xs font-medium text-slate-800">
                  {location.text}
                </div>
              </Popup>
            </Marker>
          </MapContainer>
        </div>
      ) : (
        <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-500 flex items-center gap-2">
          <span>📍</span>
          <span>No GPS coordinates pinned for this complaint. Address text: <strong>{location.text}</strong></span>
        </div>
      )}
    </div>
  );
}
