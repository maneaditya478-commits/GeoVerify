import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, GeoJSON, CircleMarker, useMap } from 'react-leaflet';
import L from 'leaflet';
import { Coordinates, NearbyPlace } from '../types';
import { Layers, Crosshair, Navigation } from 'lucide-react';

// Fix Leaflet marker icon asset paths
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom main location icon
const primaryIcon = new L.DivIcon({
  className: 'custom-pin-container',
  html: `<div class="relative flex items-center justify-center">
          <div class="absolute w-8 h-8 bg-emerald-500 rounded-full animate-ping opacity-30"></div>
          <div class="relative w-7 h-7 bg-emerald-600 border-2 border-white rounded-full flex items-center justify-center shadow-lg text-white font-bold">
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
          </div>
        </div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14],
  popupAnchor: [0, -14],
});

interface MapUpdaterProps {
  center: Coordinates;
}

const MapUpdater: React.FC<MapUpdaterProps> = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    map.setView([center.latitude, center.longitude], 13);
  }, [center, map]);
  return null;
};

interface MapViewProps {
  center?: Coordinates;
  displayName?: string;
  boundaryGeoJson?: any;
  nearbyPlaces?: NearbyPlace[];
}

export const MapView: React.FC<MapViewProps> = ({
  center = { latitude: 18.5514, longitude: 73.9405 },
  displayName = 'Verified Coordinate Point',
  boundaryGeoJson,
  nearbyPlaces = [],
}) => {
  const [showBoundaries, setShowBoundaries] = useState(true);
  const [showNearby, setShowNearby] = useState(true);

  const getGeoJsonStyle = (feature: any) => {
    const level = feature?.properties?.level;
    if (level === 'locality') {
      return { color: '#10b981', weight: 2, fillOpacity: 0.2, dashArray: '4, 4' };
    }
    if (level === 'district') {
      return { color: '#0284c7', weight: 2.5, fillOpacity: 0.1 };
    }
    return { color: '#6366f1', weight: 3, fillOpacity: 0.05 };
  };

  const getPoiColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'hospital':
        return '#ef4444'; // Red
      case 'transit':
        return '#3b82f6'; // Blue
      case 'police':
        return '#eab308'; // Yellow
      case 'commercial':
        return '#8b5cf6'; // Purple
      case 'post_office':
        return '#ec4899'; // Pink
      default:
        return '#10b981'; // Emerald
    }
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-xl backdrop-blur-sm relative flex flex-col h-[520px]">
      {/* Map Header Controls */}
      <div className="bg-slate-950/90 px-4 py-2.5 border-b border-slate-800 flex items-center justify-between z-10">
        <div className="flex items-center gap-2 text-xs font-mono text-slate-300">
          <Navigation className="w-3.5 h-3.5 text-emerald-400" />
          <span>
            {center.latitude.toFixed(5)}° N, {center.longitude.toFixed(5)}° E
          </span>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowBoundaries(!showBoundaries)}
            className={`text-xs px-2.5 py-1 rounded border font-mono transition-colors flex items-center gap-1.5 ${
              showBoundaries
                ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            <Layers className="w-3 h-3" />
            <span>Boundaries</span>
          </button>

          <button
            onClick={() => setShowNearby(!showNearby)}
            className={`text-xs px-2.5 py-1 rounded border font-mono transition-colors flex items-center gap-1.5 ${
              showNearby
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
                : 'bg-slate-800 text-slate-400 border-slate-700'
            }`}
          >
            <Crosshair className="w-3 h-3" />
            <span>Nearby POIs ({nearbyPlaces.length})</span>
          </button>
        </div>
      </div>

      {/* Leaflet Interactive Map */}
      <div className="flex-1 w-full h-full relative">
        <MapContainer
          center={[center.latitude, center.longitude]}
          zoom={13}
          scrollWheelZoom={true}
          className="w-full h-full"
          style={{ background: '#020617' }}
        >
          <MapUpdater center={center} />

          {/* High-quality Carto Dark Tile Layer */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />

          {/* GeoJSON Administrative Boundary Layers */}
          {showBoundaries && boundaryGeoJson && (
            <GeoJSON
              key={JSON.stringify(boundaryGeoJson)}
              data={boundaryGeoJson}
              style={getGeoJsonStyle}
              onEachFeature={(feature, layer) => {
                const name = feature?.properties?.name || 'Boundary';
                const level = feature?.properties?.level || 'Region';
                layer.bindPopup(
                  `<div class="text-slate-900 font-sans p-1">
                    <strong class="text-xs uppercase text-slate-600">${level}</strong>
                    <div class="font-bold text-sm text-slate-900">${name}</div>
                  </div>`
                );
              }}
            />
          )}

          {/* Main Verified Location Marker */}
          <Marker position={[center.latitude, center.longitude]} icon={primaryIcon}>
            <Popup className="custom-popup">
              <div className="p-1 text-slate-900 font-sans">
                <div className="text-[10px] uppercase font-bold text-emerald-700 tracking-wider">
                  Verified Point
                </div>
                <div className="font-bold text-sm mt-0.5">{displayName}</div>
                <div className="text-xs text-slate-600 mt-1 font-mono">
                  {center.latitude.toFixed(4)}, {center.longitude.toFixed(4)}
                </div>
              </div>
            </Popup>
          </Marker>

          {/* Nearby POI Circle Markers */}
          {showNearby &&
            nearbyPlaces.map((poi, idx) => (
              <CircleMarker
                key={idx}
                center={[poi.coordinates.latitude, poi.coordinates.longitude]}
                radius={6}
                pathOptions={{
                  fillColor: getPoiColor(poi.category),
                  fillOpacity: 0.9,
                  color: '#ffffff',
                  weight: 1.5,
                }}
              >
                <Popup>
                  <div className="p-1 text-slate-900 font-sans">
                    <span className="text-[10px] uppercase font-bold text-slate-500">
                      {poi.category} {poi.subtype ? `• ${poi.subtype}` : ''}
                    </span>
                    <div className="font-bold text-sm">{poi.name}</div>
                    <div className="text-xs text-slate-600 mt-0.5">
                      Distance: <span className="font-semibold text-emerald-700">{poi.distance_km} km</span>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
        </MapContainer>
      </div>
    </div>
  );
};
