/**
 * Interactive Geospatial Map Dashboard â€” Mapbox GL JS
 * Owner: Harshit
 *
 * Renders a 3D globe with satellite basemap, cyclone track visualization,
 * forecast cone of uncertainty, GEE layer overlays, and infrastructure markers.
 */

import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { Layers, Wind, CloudRain, Building2, Eye, Navigation, Navigation2, Droplets } from 'lucide-react';
import { fetchMarineWeather } from '../services/api';

mapboxgl.accessToken = import.meta.env?.VITE_MAPBOX_TOKEN || '';


/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   Geometry Builders
   â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */

/**
 * Builds a cone-of-uncertainty polygon from the current position
 * fanning outward through each forecast point's uncertainty radius.
 */
function buildForecastCone(cyclone) {
  if (!cyclone?.forecast_track?.length) {
    return { type: 'Feature', geometry: { type: 'Polygon', coordinates: [[]] } };
  }

  const origin = [cyclone.current_position.lon, cyclone.current_position.lat];
  const rightEdge = [];
  const leftEdge = [];
  let prev = origin;

  for (const pt of cyclone.forecast_track) {
    const curr = [pt.lon, pt.lat];
    const rKm = pt.uncertainty_radius_km || 20;

    const dx = curr[0] - prev[0];
    const dy = curr[1] - prev[1];
    const bearing = Math.atan2(dx, dy);
    const perp = bearing + Math.PI / 2;

    const latDeg = rKm / 111.0;
    const lonDeg = rKm / (111.0 * Math.cos(curr[1] * Math.PI / 180));

    rightEdge.push([
      curr[0] + lonDeg * Math.sin(perp),
      curr[1] + latDeg * Math.cos(perp)
    ]);
    leftEdge.push([
      curr[0] - lonDeg * Math.sin(perp),
      curr[1] - latDeg * Math.cos(perp)
    ]);

    prev = curr;
  }

  return {
    type: 'Feature',
    geometry: {
      type: 'Polygon',
      coordinates: [[origin, ...rightEdge, ...leftEdge.reverse(), origin]]
    }
  };
}

/**
 * Simulated SAR flood inundation zone along the Andhra coast.
 * Will be replaced by real GEE Sentinel-1 SAR data from Vikash's pipeline.
 */
function buildFloodZone() {
  return {
    type: 'Feature',
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [80.10, 14.10], [80.75, 14.25], [80.95, 14.80],
        [80.60, 15.40], [80.05, 15.20], [79.85, 14.55], [80.10, 14.10]
      ]]
    }
  };
}

/**
 * Simulated GPM rainfall accumulation zone (wider coverage).
 * Will be replaced by real NASA GPM IMERG data from Vikash's pipeline.
 */
function buildRainfallZone() {
  return {
    type: 'Feature',
    geometry: {
      type: 'Polygon',
      coordinates: [[
        [79.5, 13.5], [82.5, 13.5], [83.0, 15.0],
        [82.0, 16.5], [79.5, 16.0], [79.0, 14.5], [79.5, 13.5]
      ]]
    }
  };
}


/* â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
   Map Dashboard Component
   â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• */

export default function MapDashboard({ cyclone, risk, onPhaseChange, mode, shelters, geospatialLayers, forecastCone, windBuffers }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const eyeMarkerRef = useRef(null);
  const animFrameRef = useRef(null);
  const layersAddedRef = useRef(false);
  const cycloneRef = useRef(cyclone); // Always holds latest cyclone prop
  const [mapReady, setMapReady] = useState(false);
  const [telemetry, setTelemetry] = useState({ show: false, loading: false, data: null, error: null, coords: null });

  // Keep cycloneRef in sync with latest prop
  useEffect(() => {
    cycloneRef.current = cyclone;
  }, [cyclone]);

  const [activeLayers, setActiveLayers] = useState({
    track: true,
    cone: true,
    sarFlood: true,
    gpmRain: false,
    shelters: true
  });

  /* â”€â”€ 1. Map Initialization â”€â”€ */
  useEffect(() => {
    if (mapRef.current) return;

    const map = new mapboxgl.Map({
      container: containerRef.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: [82.1, 14.5],
      zoom: 5.5,
      pitch: 45,
      bearing: -15,
      projection: 'globe',
      antialias: true
    });

    // Navigation controls with pitch visualization
    map.addControl(
      new mapboxgl.NavigationControl({ visualizePitch: true }),
      'top-right'
    );
    map.addControl(
      new mapboxgl.ScaleControl({ maxWidth: 150 }),
      'bottom-right'
    );

    // Globe atmosphere
    map.on('style.load', () => {
      map.setFog({
        color: 'rgb(10, 15, 30)',
        'high-color': 'rgb(20, 30, 60)',
        'horizon-blend': 0.08,
        'space-color': 'rgb(5, 8, 16)',
        'star-intensity': 0.6
      });
    });

    // 3D terrain + signal ready
    map.on('load', () => {
      map.addSource('mapbox-dem', {
        type: 'raster-dem',
        url: 'mapbox://mapbox.mapbox-terrain-dem-v1',
        tileSize: 512,
        maxzoom: 14
      });
      map.setTerrain({ source: 'mapbox-dem', exaggeration: 1.5 });
      setMapReady(true);
    });

    mapRef.current = map;

    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current);
      if (eyeMarkerRef.current) eyeMarkerRef.current.remove();
      map.remove();
      mapRef.current = null;
    };
  }, []);


  /* â”€â”€ 2. Add GeoJSON Data Layers â”€â”€ */
  useEffect(() => {
    if (!mapReady || !mapRef.current || !cyclone || layersAddedRef.current) return;
    const map = mapRef.current;
    layersAddedRef.current = true;

    // â”€â”€â”€â”€â”€â”€â”€â”€ GPM Rainfall Zone (bottom layer) â”€â”€â”€â”€â”€â”€â”€â”€
    if (mode === 'demo' || geospatialLayers?.layers?.gpm_rainfall?.status !== 'available') { map.addSource('gpm-rain', { type: 'geojson', data: mode === 'demo' ? buildRainfallZone() : {type: 'FeatureCollection', features: []} }); } else { map.addSource('gpm-rain', { type: 'raster', tiles: [geospatialLayers.layers.gpm_rainfall.tile_url], tileSize: 256 }); }
    map.addLayer({
      id: 'gpm-rain-fill', type: 'fill', source: 'gpm-rain',
      layout: { visibility: activeLayers.gpmRain ? 'visible' : 'none' },
      paint: { 'fill-color': '#a855f7', 'fill-opacity': 0.18 }
    });
    if (mode === 'demo' || geospatialLayers?.layers?.gpm_rainfall?.status !== 'available') { map.addLayer({ id: 'gpm-rain-border', type: 'line', source: 'gpm-rain', layout: { visibility: activeLayers.gpmRain ? 'visible' : 'none' }, paint: { 'line-color': '#c084fc', 'line-width': 1.5, 'line-dasharray': [4, 3] } }); }

    // â”€â”€â”€â”€â”€â”€â”€â”€ SAR Flood Inundation Zone â”€â”€â”€â”€â”€â”€â”€â”€
    if (mode === 'demo' || geospatialLayers?.layers?.sar_flood?.status !== 'available') { map.addSource('sar-flood', { type: 'geojson', data: mode === 'demo' ? buildFloodZone() : {type: 'FeatureCollection', features: []} }); } else { map.addSource('sar-flood', { type: 'raster', tiles: [geospatialLayers.layers.sar_flood.tile_url], tileSize: 256 }); }
    if (mode === 'demo' || geospatialLayers?.layers?.sar_flood?.status !== 'available') { map.addLayer({ id: 'sar-flood-fill', type: 'fill', source: 'sar-flood', layout: { visibility: activeLayers.sarFlood ? 'visible' : 'none' }, paint: { 'fill-color': '#06b6d4', 'fill-opacity': 0.22 } }); } else { map.addLayer({ id: 'sar-flood-raster', type: 'raster', source: 'sar-flood', layout: { visibility: activeLayers.sarFlood ? 'visible' : 'none' }, paint: { 'raster-opacity': 0.75 } }); }
    if (mode === 'demo' || geospatialLayers?.layers?.sar_flood?.status !== 'available') { map.addLayer({ id: 'sar-flood-border', type: 'line', source: 'sar-flood', layout: { visibility: activeLayers.sarFlood ? 'visible' : 'none' }, paint: { 'line-color': '#22d3ee', 'line-width': 1.5, 'line-dasharray': [4, 2] } }); }

    // â”€â”€â”€â”€â”€â”€â”€â”€ Forecast Cone of Uncertainty â”€â”€â”€â”€â”€â”€â”€â”€
    map.addSource('forecast-cone', { type: 'geojson', data: mode === 'live' && forecastCone ? forecastCone : buildForecastCone(cyclone) });

      // 🔴🔴🔴 Wind Hazard Buffers 🔴🔴🔴
      map.addSource('wind-buffers', { type: 'geojson', data: mode === 'live' && windBuffers ? windBuffers : { type: 'FeatureCollection', features: [] } });
      map.addLayer({
        id: 'wind-buffers-fill', type: 'fill', source: 'wind-buffers',
        paint: { 'fill-color': ['match', ['get', 'wind_speed_kt'], 64, '#991b1b', 50, '#c2410c', 34, '#f59e0b', '#f59e0b'], 'fill-opacity': 0.2 }
      }, 'cone-border');
      map.addLayer({
        id: 'wind-buffers-line', type: 'line', source: 'wind-buffers',
        paint: { 'line-color': ['match', ['get', 'wind_speed_kt'], 64, '#991b1b', 50, '#c2410c', 34, '#f59e0b', '#f59e0b'], 'line-width': 1, 'line-opacity': 0.6 }
      }, 'cone-border');
    map.addLayer({
      id: 'cone-fill', type: 'fill', source: 'forecast-cone',
      paint: { 'fill-color': '#ef4444', 'fill-opacity': 0.14 }
    });
    map.addLayer({
      id: 'cone-border', type: 'line', source: 'forecast-cone',
      paint: { 'line-color': '#ef4444', 'line-width': 1.5, 'line-dasharray': [6, 3], 'line-opacity': 0.6 }
    });

    // â”€â”€â”€â”€â”€â”€â”€â”€ Past Track Line â”€â”€â”€â”€â”€â”€â”€â”€
    const pastCoords = cyclone.past_track?.map(p => [p.lon, p.lat]) || [];
    map.addSource('past-track', {
      type: 'geojson',
      data: { type: 'Feature', geometry: { type: 'LineString', coordinates: pastCoords } }
    });
    map.addLayer({
      id: 'past-track-line', type: 'line', source: 'past-track',
      layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-color': '#f59e0b', 'line-width': 3, 'line-opacity': 0.9 }
    });

    // â”€â”€â”€â”€â”€â”€â”€â”€ Past Track Points â”€â”€â”€â”€â”€â”€â”€â”€
    map.addSource('past-points', {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: cyclone.past_track?.map(p => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [p.lon, p.lat] },
          properties: { wind: p.wind_kmh }
        })) || []
      }
    });
    map.addLayer({
      id: 'past-track-dots', type: 'circle', source: 'past-points',
      paint: {
        'circle-radius': 5,
        'circle-color': '#f59e0b',
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 1.5
      }
    });

    // â”€â”€â”€â”€â”€â”€â”€â”€ Forecast Track Line (dashed) â”€â”€â”€â”€â”€â”€â”€â”€
    const fcastCoords = [
      [cyclone.current_position.lon, cyclone.current_position.lat],
      ...(cyclone.forecast_track?.map(p => [p.lon, p.lat]) || [])
    ];
    map.addSource('forecast-track', {
      type: 'geojson',
      data: { type: 'Feature', geometry: { type: 'LineString', coordinates: fcastCoords } }
    });
    map.addLayer({
      id: 'forecast-track-line', type: 'line', source: 'forecast-track',
      layout: { 'line-cap': 'round', 'line-join': 'round' },
      paint: { 'line-color': '#ef4444', 'line-width': 2.5, 'line-dasharray': [4, 3], 'line-opacity': 0.8 }
    });

    // â”€â”€â”€â”€â”€â”€â”€â”€ Forecast Points â”€â”€â”€â”€â”€â”€â”€â”€
    map.addSource('forecast-points', {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: cyclone.forecast_track?.map(p => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [p.lon, p.lat] },
          properties: { wind: p.wind_kmh, uncertainty: p.uncertainty_radius_km }
        })) || []
      }
    });
    map.addLayer({
      id: 'forecast-track-dots', type: 'circle', source: 'forecast-points',
      paint: {
        'circle-radius': 6,
        'circle-color': '#ef4444',
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 2
      }
    });

    // â”€â”€â”€â”€â”€â”€â”€â”€ Shelter & Infrastructure Markers â”€â”€â”€â”€â”€â”€â”€â”€
    map.addSource('shelters', {
      type: 'geojson',
      data: {
        type: 'FeatureCollection',
        features: (shelters && shelters.length > 0 ? shelters : [
          { name: 'Nellore Shelter #4', capacity: 1200, lat: 14.44, lon: 79.98 },
          { name: 'Prakasam Shelter #12', capacity: 800, lat: 15.35, lon: 80.05 },
          { name: 'Bapatla Relief Camp', capacity: 600, lat: 15.90, lon: 80.47 },
          { name: 'Ongole District Hospital', capacity: 450, lat: 15.50, lon: 80.64 }
        ]).map(s => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [s.lon, s.lat] },
          properties: { name: s.name, capacity: s.capacity }
        }))
      }
    });
    map.addLayer({
      id: 'shelter-circles', type: 'circle', source: 'shelters',
      paint: {
        'circle-radius': 7,
        'circle-color': '#10b981',
        'circle-stroke-color': '#ffffff',
        'circle-stroke-width': 2,
        'circle-opacity': 0.9
      }
    });
    map.addLayer({
      id: 'shelter-labels', type: 'symbol', source: 'shelters',
      layout: {
        'text-field': ['get', 'name'],
        'text-size': 10,
        'text-offset': [0, 1.6],
        'text-anchor': 'top',
        'text-allow-overlap': false
      },
      paint: {
        'text-color': '#a7f3d0',
        'text-halo-color': '#000000',
        'text-halo-width': 1.2
      }
    });

    // â”€â”€â”€â”€â”€â”€â”€â”€ Interactive Popups â”€â”€â”€â”€â”€â”€â”€â”€
    const popupConfig = [
      {
        layer: 'forecast-track-dots',
        color: '#ef4444',
        html: (p) => `
          <div style="font-weight:700;color:#ef4444;margin-bottom:3px;">Forecast Point</div>
          <div>Wind: ${p.wind} km/h</div>
          <div>Uncertainty: \u00B1${p.uncertainty} km</div>
        `
      },
      {
        layer: 'past-track-dots',
        color: '#f59e0b',
        html: (p) => `
          <div style="font-weight:700;color:#f59e0b;margin-bottom:3px;">Historical Track</div>
          <div>Wind: ${p.wind} km/h</div>
        `
      },
      {
        layer: 'shelter-circles',
        color: '#10b981',
        html: (p) => `
          <div style="font-weight:700;color:#10b981;margin-bottom:3px;">${p.name}</div>
          <div>Capacity: ${p.capacity} persons</div>
        `
      }
    ];

    popupConfig.forEach(({ layer, html }) => {
      map.on('click', layer, (e) => {
        const props = e.features[0].properties;
        new mapboxgl.Popup({ closeButton: true, className: 'dark-popup', maxWidth: '240px' })
          .setLngLat(e.lngLat)
          .setHTML(`<div style="color:#e2e8f0;font-size:12px;line-height:1.6;">${html(props)}</div>`)
          .addTo(map);
      });
      map.on('mouseenter', layer, () => { map.getCanvas().style.cursor = 'pointer'; });
      map.on('mouseleave', layer, () => { map.getCanvas().style.cursor = ''; });
    });

    // â”€â”€â”€â”€â”€â”€â”€â”€ Cyclone Eye â€” Clickable Dot â”€â”€â”€â”€â”€â”€â”€â”€
    const eyeEl = document.createElement('div');
    eyeEl.className = 'cyclone-eye-dot';
    eyeEl.innerHTML = [
      '<div class="dot-ping"></div>',
      '<div class="dot-core"></div>'
    ].join('');

    const eyePopup = new mapboxgl.Popup({ offset: 15, className: 'dark-popup', maxWidth: '260px' })
      .setHTML(`
        <div style="color:#e2e8f0;font-size:12px;line-height:1.7;">
          <div style="font-weight:800;color:#ef4444;font-size:15px;margin-bottom:4px;">
            ${cyclone.name}
          </div>
          <div>Category ${cyclone.category} \u2014 Severe Cyclonic Storm</div>
          <div>Sustained Wind: ${cyclone.max_sustained_wind_kmh} km/h</div>
          <div>Central Pressure: ${cyclone.central_pressure_mb} hPa</div>
          <div style="color:#94a3b8;margin-top:6px;font-family:monospace;">
            ${cyclone.current_position.lat}\u00B0N, ${cyclone.current_position.lon}\u00B0E
          </div>
        </div>
      `);

    const marker = new mapboxgl.Marker({ element: eyeEl, anchor: 'center' })
      .setLngLat([cyclone.current_position.lon, cyclone.current_position.lat])
      .setPopup(eyePopup)
      .addTo(map);

    eyeMarkerRef.current = marker;

    // â”€â”€â”€â”€â”€â”€â”€â”€ Cyclone Raster Overlay (Transparent + Spinning) â”€â”€â”€â”€â”€â”€â”€â”€
    // Toggle this to test different visual styles! Options: 'infrared' or 'true-color'
    const CYCLONE_STYLE = 'true-color'; 
    const spriteUrl = CYCLONE_STYLE === 'infrared' 
      ? '/assets/cyclone-sprite.jpg' 
      : '/assets/cyclone-clouds.jpg';

    map.loadImage(spriteUrl, (err, image) => {
      if (err || !mapRef.current) return;
      
      // Remove black background using canvas
      const canvas = document.createElement('canvas');
      canvas.width = image.width;
      canvas.height = image.height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(image, 0, 0);
      const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const data = imgData.data;
      for (let i = 0; i < data.length; i += 4) {
        // If pixel is very dark, make it fully transparent
        if (data[i] < 30 && data[i+1] < 30 && data[i+2] < 30) {
          data[i+3] = 0;
        } else {
          // Soften the edges of dark pixels to blend smoothly
          const brightness = (data[i] + data[i+1] + data[i+2]) / 3;
          if (brightness < 60) {
            data[i+3] = Math.floor((brightness - 30) / 30 * 255);
          }
        }
      }
      ctx.putImageData(imgData, 0, 0);

      if (map.hasImage('cyclone-vortex')) map.removeImage('cyclone-vortex');
      map.addImage('cyclone-vortex', imgData);

      // Define storm radius (degrees, ~130km radius, 260km diameter for dense core)
      const radiusDeg = 1.2;
      
      function getRotatedCoordinates(cx, cy, angle) {
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        const latScale = Math.cos(cy * Math.PI / 180); // Adjust for mercator distortion
        
        // tl, tr, br, bl
        const pts = [ [-radiusDeg, radiusDeg], [radiusDeg, radiusDeg], [radiusDeg, -radiusDeg], [-radiusDeg, -radiusDeg] ];
        return pts.map(([dx, dy]) => {
          const rx = dx * cos - dy * sin;
          const ry = dx * sin + dy * cos;
          return [cx + rx / latScale, cy + ry];
        });
      }

      const startLng = cyclone.current_position.lon;
      const startLat = cyclone.current_position.lat;
      const nextLng = cyclone.forecast_track?.[0]?.lon || startLng;
      const nextLat = cyclone.forecast_track?.[0]?.lat || startLat;

      const initialCoords = getRotatedCoordinates(startLng, startLat, 0);

      map.addSource('cyclone-overlay', {
        type: 'image',
        url: canvas.toDataURL(),
        coordinates: initialCoords
      });

      map.addLayer({
        id: 'cyclone-overlay-layer',
        type: 'raster',
        source: 'cyclone-overlay',
        paint: {
          'raster-opacity': 0.85,
          'raster-fade-duration': 0
        }
      });

      // Animation Loop: Rotation (fast) + Drift (slow)
      const START_TIME = performance.now();
      const ROTATE_SPEED = 0.001; // rad/ms
      const DRIFT_DUR = 300000;   // 5 minutes to next point
      
      let lastPhase = '';

      function animateRaster(now) {
        if (!mapRef.current) return;
        
        const elapsed = now - START_TIME;
        const angle = -(elapsed * ROTATE_SPEED) % (Math.PI * 2);
        
        if (mode === 'demo') {
          // In demo mode: rotate at the LATEST position from cycloneRef
          const c = cycloneRef.current;
          if (!c?.current_position) return;
          const cLng = c.current_position.lon;
          const cLat = c.current_position.lat;
          
          const coords = getRotatedCoordinates(cLng, cLat, angle);
          const source = map.getSource('cyclone-overlay');
          if (source) source.setCoordinates(coords);
          if (eyeMarkerRef.current) eyeMarkerRef.current.setLngLat([cLng, cLat]);
        } else {
          // In live mode: drift toward next forecast point
          const driftT = Math.min(elapsed / DRIFT_DUR, 1);
          const ease = 1 - Math.pow(1 - driftT, 3);
          const curLng = startLng + ease * (nextLng - startLng);
          const curLat = startLat + ease * (nextLat - startLat);
          
          const coords = getRotatedCoordinates(curLng, curLat, angle);
          const source = map.getSource('cyclone-overlay');
          if (source) source.setCoordinates(coords);
          if (eyeMarkerRef.current) eyeMarkerRef.current.setLngLat([curLng, curLat]);
          
          // Emit dynamic phase
          if (onPhaseChange) {
            let currentPhase = 'PRE_LANDFALL';
            if (driftT > 0.6 && driftT < 0.8) currentPhase = 'LANDFALL';
            else if (driftT >= 0.8) currentPhase = 'POST_LANDFALL';
            
            if (currentPhase !== lastPhase) {
              lastPhase = currentPhase;
              onPhaseChange(currentPhase);
            }
          }
          
          if (driftT >= 1) return; // Stop after drift completes
        }

        animFrameRef.current = requestAnimationFrame(animateRaster);
      }
      
      animFrameRef.current = requestAnimationFrame(animateRaster);
    });
  }, [mapReady, cyclone]);


  /* â”€â”€ 2b. Demo Mode: Live Track & Cone Updates â”€â”€ */
  useEffect(() => {
    if (!mapReady || !mapRef.current || mode !== 'demo' || !cyclone) return;
    const map = mapRef.current;

    // Update past track line
    const pastSrc = map.getSource('past-track');
    if (pastSrc && cyclone.past_track?.length) {
      pastSrc.setData({
        type: 'Feature',
        geometry: {
          type: 'LineString',
          coordinates: cyclone.past_track.map(p => [p.lon, p.lat])
        }
      });
    }

    // Update past track dots
    const pastDotsSrc = map.getSource('past-points');
    if (pastDotsSrc && cyclone.past_track?.length) {
      pastDotsSrc.setData({
        type: 'FeatureCollection',
        features: cyclone.past_track.map(p => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [p.lon, p.lat] },
          properties: { wind: p.wind_kmh, time: p.timestamp }
        }))
      });
    }

    // Update forecast track line
    const fcSrc = map.getSource('forecast-track');
    if (fcSrc && cyclone.forecast_track?.length) {
      const coords = [
        [cyclone.current_position.lon, cyclone.current_position.lat],
        ...cyclone.forecast_track.map(p => [p.lon, p.lat])
      ];
      fcSrc.setData({
        type: 'Feature',
        geometry: { type: 'LineString', coordinates: coords }
      });
    }

    // Update forecast dots
    const fcDotsSrc = map.getSource('forecast-points');
    if (fcDotsSrc && cyclone.forecast_track?.length) {
      fcDotsSrc.setData({
        type: 'FeatureCollection',
        features: cyclone.forecast_track.map(p => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [p.lon, p.lat] },
          properties: { wind: p.wind_kmh, time: p.timestamp }
        }))
      });
    }

    // Update cone of uncertainty
    const coneSrc = map.getSource('forecast-cone');
    if (coneSrc) {
      coneSrc.setData(buildForecastCone(cyclone));
    }

  }, [mapReady, cyclone, mode]);

  /* â”€â”€ 2c. Update Shelters Layer â”€â”€ */
  useEffect(() => {
    if (!mapReady || !mapRef.current || !shelters || shelters.length === 0) return;
    const map = mapRef.current;
    
    const shelterSrc = map.getSource('shelters');
    if (shelterSrc) {
      shelterSrc.setData({
        type: 'FeatureCollection',
        features: shelters.map(s => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [s.lon, s.lat] },
          properties: { name: s.name, capacity: s.capacity }
        }))
      });
    }
  }, [mapReady, shelters]);

  /* â”€â”€ 3. Layer Visibility Toggle â”€â”€ */
  useEffect(() => {
    if (!mapReady || !mapRef.current) return;
    const map = mapRef.current;

    const groups = {
      track: ['past-track-line', 'past-track-dots', 'forecast-track-line', 'forecast-track-dots'],
      cone: ['cone-fill', 'cone-border', 'wind-buffers-fill', 'wind-buffers-line'],
      sarFlood: ['sar-flood-fill', 'sar-flood-border', 'sar-flood-raster'],
      gpmRain: ['gpm-rain-fill', 'gpm-rain-border', 'gpm-rain-raster'],
      shelters: ['shelter-circles', 'shelter-labels'],
    };

    Object.entries(groups).forEach(([key, layerIds]) => {
      layerIds.forEach(id => {
        if (map.getLayer(id)) {
          map.setLayoutProperty(id, 'visibility', activeLayers[key] ? 'visible' : 'none');
        }
      });
    });
  }, [activeLayers, mapReady]);


  const toggle = (key) => setActiveLayers(prev => ({ ...prev, [key]: !prev[key] }));


  /* â”€â”€ Render â”€â”€ */
  return (
    <div className="relative w-full h-full bg-[#0b1120] rounded-xl overflow-hidden border border-gray-800 shadow-2xl flex flex-col">

      {/* Mapbox GL Canvas */}
      <div ref={containerRef} className="flex-1" />

      {/* Coordinate & Mode HUD */}
      <div className="absolute bottom-[72px] left-4 bg-gray-950/90 border border-gray-800 px-3 py-1.5 rounded-lg text-xs font-mono text-gray-400 flex items-center space-x-3 z-10 backdrop-blur-sm">
        <Navigation className="w-3.5 h-3.5 text-sky-400" />
        <span>
          Eye: {cyclone?.current_position?.lat?.toFixed(2) || '14.50'}&deg;N,{' '}
          {cyclone?.current_position?.lon?.toFixed(2) || '82.10'}&deg;E
        </span>
        <span className="text-gray-700">|</span>
        <Navigation className="w-3.5 h-3.5 text-purple-400" />
        <span>3D Globe + Terrain</span>
      </div>

      {/* Layer Control Bar */}
      <div className="h-14 bg-gray-950 border-t border-gray-800 px-4 flex items-center justify-between text-xs z-10">
        <div className="flex items-center space-x-2 text-gray-400 font-medium">
          <Layers className="w-4 h-4 text-sky-400" />
          <span>GIS Layers</span>
        </div>

        <div className="flex items-center space-x-3">
          {/* Track & Cone */}
          <button
            onClick={() => toggle('cone')}
            className={`px-3 py-1.5 rounded-md border flex items-center space-x-1.5 transition-colors ${
              activeLayers.cone
                ? 'bg-red-500/20 border-red-500/50 text-red-300'
                : 'bg-gray-900 border-gray-800 text-gray-500'
            }`}
          >
            <Wind className="w-3.5 h-3.5" />
            <span>Forecast Cone</span>
          </button>

          {/* SAR Flood */}
          <button
            onClick={() => toggle('sarFlood')}
            className={`px-3 py-1.5 rounded-md border flex items-center space-x-1.5 transition-colors ${
              activeLayers.sarFlood
                ? 'bg-cyan-500/20 border-cyan-500/50 text-cyan-300'
                : 'bg-gray-900 border-gray-800 text-gray-500'
            }`}
          >
            <Eye className="w-3.5 h-3.5" />
            <span>SAR Flood</span>
          </button>

          {/* GPM Rainfall */}
          <button
            onClick={() => toggle('gpmRain')}
            className={`px-3 py-1.5 rounded-md border flex items-center space-x-1.5 transition-colors ${
              activeLayers.gpmRain
                ? 'bg-purple-500/20 border-purple-500/50 text-purple-300'
                : 'bg-gray-900 border-gray-800 text-gray-500'
            }`}
          >
            <CloudRain className="w-3.5 h-3.5" />
            <span>GPM Rainfall</span>
          </button>

          {/* Shelters & POIs */}
          <button
            onClick={() => toggle('shelters')}
            className={`px-3 py-1.5 rounded-md border flex items-center space-x-1.5 transition-colors ${
              activeLayers.shelters
                ? 'bg-emerald-500/20 border-emerald-500/50 text-emerald-300'
                : 'bg-gray-900 border-gray-800 text-gray-500'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Shelters</span>
          </button>
        </div>
      </div>
    </div>
  );
}








