import { useState, useRef, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import { HiOutlineGlobeAlt, HiOutlineCheck, HiOutlinePencil, HiOutlineX } from 'react-icons/hi';
import toast from 'react-hot-toast';

// Fix default leaflet marker icon in Vite
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: markerIcon,
  iconRetinaUrl: markerIcon2x,
  shadowUrl: markerShadow,
});

// Helper component to center map dynamically when coords change in view mode
function MapRecenter({ center }) {
  const map = useMap();
  useEffect(() => {
    if (center && center.lat && center.lng) {
      map.setView([center.lat, center.lng], map.getZoom() || 15);
    }
  }, [center, map]);
  return null;
}

// Controller component to grab map instance in Change Location mode
function ChangeLocationController({ isChanging, onConfirmLocation, setCenterAddressPreview }) {
  const map = useMap();

  useEffect(() => {
    if (!isChanging) return;

    let timer = null;

    const handleMove = () => {
      const center = map.getCenter();
      if (timer) clearTimeout(timer);
      // Fetch address preview for center
      timer = setTimeout(async () => {
        try {
          const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${center.lat}&lon=${center.lng}`,
            { headers: { 'Accept-Language': 'en' } }
          );
          const data = await res.json();
          if (data && data.display_name) {
            setCenterAddressPreview(data.display_name);
          }
        } catch {
          setCenterAddressPreview(`${center.lat.toFixed(5)}, ${center.lng.toFixed(5)}`);
        }
      }, 400);
    };

    map.on('move', handleMove);
    handleMove(); // Initial check

    return () => {
      if (timer) clearTimeout(timer);
      map.off('move', handleMove);
    };
  }, [isChanging, map, setCenterAddressPreview]);

  return null;
}

export default function LocationPickerMap({ locationData, onChange, error }) {
  const [coords, setCoords] = useState(
    locationData?.latitude && locationData?.longitude
      ? { lat: locationData.latitude, lng: locationData.longitude }
      : null
  );
  const [addressText, setAddressText] = useState(locationData?.text || '');
  const [geoLoading, setGeoLoading] = useState(false);
  const [isChanging, setIsChanging] = useState(false);
  const [centerAddressPreview, setCenterAddressPreview] = useState('');
  const mapRef = useRef(null);

  // Sync internal state when parent props change
  useEffect(() => {
    if (locationData?.text !== undefined && locationData.text !== addressText) {
      setAddressText(locationData.text);
    }
    if (locationData?.latitude && locationData?.longitude) {
      setCoords({ lat: locationData.latitude, lng: locationData.longitude });
    }
  }, [locationData?.text, locationData?.latitude, locationData?.longitude]);

  const reverseGeocode = async (lat, lng) => {
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
        { headers: { 'Accept-Language': 'en' } }
      );
      const data = await res.json();
      if (data && data.display_name) {
        return data.display_name;
      }
    } catch (err) {
      console.error('Reverse geocode error:', err);
    }
    return `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
  };

  const handleGetCurrentLocation = () => {
    if (!navigator.geolocation) {
      toast.error('Geolocation is not supported by your browser');
      return;
    }
    setGeoLoading(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = pos.coords.latitude;
        const lng = pos.coords.longitude;
        setCoords({ lat, lng });
        const fetchedAddress = await reverseGeocode(lat, lng);
        setAddressText(fetchedAddress);
        onChange({ text: fetchedAddress, latitude: lat, longitude: lng });
        setGeoLoading(false);
        setIsChanging(false);
        toast.success('Current location retrieved successfully!');
      },
      (err) => {
        setGeoLoading(false);
        toast.error('Unable to retrieve location. Please allow browser location access.');
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 0 }
    );
  };

  const handleConfirmCenterLocation = async () => {
    if (!mapRef.current) return;
    const center = mapRef.current.getCenter();
    const lat = center.lat;
    const lng = center.lng;
    setCoords({ lat, lng });
    const fetchedAddress = await reverseGeocode(lat, lng);
    setAddressText(fetchedAddress);
    onChange({ text: fetchedAddress, latitude: lat, longitude: lng });
    setIsChanging(false);
    toast.success('New location set!');
  };

  return (
    <div className="space-y-3">
      {/* Address Input + Get Current Address Button */}
      <div className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <input
            id="complaint-location"
            type="text"
            value={addressText}
            onChange={(e) => {
              const val = e.target.value;
              setAddressText(val);
              onChange({ text: val, latitude: coords?.lat || null, longitude: coords?.lng || null });
            }}
            className={error ? 'input-error pr-20' : 'input pr-20'}
            placeholder="Address or click 'Get Current Location'"
          />
          {coords && (
            <span className="absolute right-3 top-1/2 -translate-y-1/2 text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
              Pinned 📍
            </span>
          )}
        </div>

        <button
          type="button"
          onClick={handleGetCurrentLocation}
          disabled={geoLoading}
          className="btn-primary text-xs px-4 py-2.5 flex items-center justify-center gap-1.5 whitespace-nowrap shadow-sm"
          title="Get current GPS location"
        >
          {geoLoading ? (
            <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <HiOutlineGlobeAlt className="w-4 h-4" />
          )}
          <span>{geoLoading ? 'Getting Location...' : 'Get Current Location'}</span>
        </button>
      </div>

      {/* Inline Map Container when Coords are available */}
      {coords && (
        <div className="rounded-2xl border border-slate-200 overflow-hidden shadow-sm bg-white space-y-0">
          {/* Top Control Bar */}
          <div className="px-4 py-2.5 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-semibold text-slate-700">
                {isChanging ? 'Move map to position center pin' : 'Location Map (View Mode)'}
              </span>
            </div>

            {!isChanging ? (
              <button
                type="button"
                onClick={() => setIsChanging(true)}
                className="btn-outline text-xs px-3 py-1 flex items-center gap-1 bg-white hover:bg-slate-50"
              >
                <HiOutlinePencil className="w-3.5 h-3.5 text-primary-600" />
                <span>Change Location</span>
              </button>
            ) : (
              <button
                type="button"
                onClick={() => setIsChanging(false)}
                className="text-xs text-slate-500 hover:text-slate-700 font-medium flex items-center gap-1 px-2 py-1"
              >
                <HiOutlineX className="w-3.5 h-3.5" />
                Cancel
              </button>
            )}
          </div>

          {/* Map Display */}
          <div className="h-64 w-full relative z-0">
            <MapContainer
              center={[coords.lat, coords.lng]}
              zoom={15}
              style={{ height: '100%', width: '100%' }}
              ref={mapRef}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />

              {!isChanging && <MapRecenter center={coords} />}

              {/* View Mode: Normal Fixed Marker */}
              {!isChanging && (
                <Marker position={[coords.lat, coords.lng]}>
                  <Popup>
                    <div className="text-xs font-medium text-slate-800">
                      {addressText}
                    </div>
                  </Popup>
                </Marker>
              )}

              {/* Change Location Controller */}
              <ChangeLocationController
                isChanging={isChanging}
                onConfirmLocation={handleConfirmCenterLocation}
                setCenterAddressPreview={setCenterAddressPreview}
              />
            </MapContainer>

            {/* Change Location Mode: Fixed Center Pin Overlay */}
            {isChanging && (
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-full z-[1000] pointer-events-none flex flex-col items-center">
                <div className="w-8 h-8 text-red-600 filter drop-shadow-md animate-bounce">
                  📍
                </div>
                <div className="w-2.5 h-1 bg-black/30 rounded-full blur-[1px]" />
              </div>
            )}
          </div>

          {/* Bottom Confirmation Bar when in Change Location Mode */}
          {isChanging && (
            <div className="p-3 bg-amber-50 border-t border-amber-200 flex flex-col sm:flex-row items-center justify-between gap-2">
              <div className="text-xs text-amber-900 truncate max-w-md">
                <strong>Target Address:</strong> {centerAddressPreview || 'Move map to select...'}
              </div>
              <button
                type="button"
                onClick={handleConfirmCenterLocation}
                className="btn-primary text-xs px-4 py-1.5 flex items-center justify-center gap-1.5 w-full sm:w-auto"
              >
                <HiOutlineCheck className="w-4 h-4" />
                Set Location Here
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
