import React, { useEffect, useRef } from 'react';
import maplibregl, {
  GetResourceResponse,
  NavigationControl,
  ScaleControl,
} from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import './maplibre.css';
import locationImage from '../../assets/location.png';
import { GeoJSON } from 'geojson';

export type Camerea = {
  center: [number, number];
  zoom: number;
  pitch: number;
  bearing: number;
};

export type UserLocation = {
  longitude: number;
  latitude: number;
  heading: number; // In degrees
};

interface MapLibreProps {
  initialCamerea?: Camerea;
  maxBounds?: [[number, number], [number, number]];
  userLocation?: UserLocation;
  userRoom?: string;
  route?: GeoJSON;
  indoorMap?: GeoJSON;
  onRoomClick?: (room: string) => void;
  userGPS?: { lat: number; lng: number };
}

const MapLibre: React.FC<MapLibreProps> = React.memo(
  ({
    initialCamerea,
    maxBounds,
    userLocation,
    route,
    indoorMap,
    onRoomClick,
    userRoom,
    userGPS,
  }) => {
    const {
      center: initialCenter,
      zoom: initialZoom,
      pitch: initialPitch,
      bearing: initialBearing,
    } = initialCamerea || {};

    const mapInstance = useRef<maplibregl.Map | null>(null);
    const mapContainer = useRef<HTMLDivElement>(null);
    const locationPopup = useRef<maplibregl.Popup | null>(null);

    useEffect(() => {
      if (mapContainer.current) {
        const map = new maplibregl.Map({
          container: mapContainer.current,
          style:
            'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
          center: initialCenter,
          zoom: initialZoom,
          pitch: initialPitch,
          bearing: initialBearing,
          maxBounds: maxBounds,
        });

        mapInstance.current = map;

        let animationFrameId: number;

        map.on('load', () => {
          const scale = new ScaleControl({
            maxWidth: 100,
            unit: 'metric',
          });
          map.addControl(scale, 'bottom-left');

          if (route) {
            map.addSource('route', {
              type: 'geojson',
              data: route,
            });
            map.addLayer({
              id: 'route',
              type: 'line',
              source: 'route',
              layout: {
                'line-cap': 'round',
                'line-join': 'round',
              },
              paint: {
                'line-color': '#FFA500',
                'line-width': 5,
                'line-opacity': 0.5,
              },
            });

            const minOpacity = 0.5;
            const maxOpacity = 1.0;
            const opacityRange = maxOpacity - minOpacity;
            const duration = 2000;
            const startTime = performance.now();

            function animate(currentTime: number) {
              const elapsed = (currentTime - startTime) % duration;
              const progress = elapsed / duration;

              const opacity =
                minOpacity +
                (opacityRange * (Math.sin(progress * Math.PI * 2) + 1)) / 2;

              map.setPaintProperty('route', 'line-opacity', opacity);
              animationFrameId = requestAnimationFrame(animate);
            }

            animationFrameId = requestAnimationFrame(animate);
          }
          if (indoorMap) {
            map.addSource('floor-map', {
              type: 'geojson',
              data: indoorMap,
            });
            map.addLayer({
              id: 'floor-map',
              type: 'fill',
              source: 'floor-map',
              paint: {
                'fill-color': [
                  'case',
                  ['boolean', ['feature-state', 'selected'], false],
                  '#FF9900', // Highlight color for selected room
                  '#349ACD', // Default color
                ],
                'fill-opacity': [
                  'case',
                  ['boolean', ['feature-state', 'selected'], false],
                  0.8,
                  0.4,
                ],
              },
            });
            map.addLayer({
              id: 'floor-map-labels',
              type: 'symbol',
              source: 'floor-map',
              layout: {
                'text-field': ['get', 'room'],
                'text-anchor': 'center',
                'text-size': 12,
              },
              paint: {
                'text-color': '#ffffff',
              },
            });

            map.on('click', 'floor-map', (e) => {
              if (e.features && e.features.length > 0) {
                const feature = e.features[0];
                const properties = feature.properties;
                if (onRoomClick) {
                  onRoomClick(properties.room);
                }
              }
            });
          }

          map.on('mouseenter', 'floor-map', () => {
            map.getCanvas().style.cursor = 'pointer';
          });

          map.on('mouseleave', 'floor-map', () => {
            map.getCanvas().style.cursor = '';
          });

          if (userGPS) {
            map.addSource('user-gps', {
              type: 'geojson',
              data: {
                type: 'FeatureCollection',
                features: [
                  {
                    type: 'Feature',
                    geometry: {
                      type: 'Point',
                      coordinates: [userGPS.lng, userGPS.lat],
                    },
                    properties: {},
                  },
                ],
              },
            });
            map.addLayer({
              id: 'user-gps',
              type: 'circle',
              source: 'user-gps',
              paint: {
                'circle-radius': 10,
                'circle-color': '#FF9900',
                'circle-opacity': 0.6,
                'circle-blur': 1,
              },
            });
            map.addLayer({
              id: 'user-gps-label',
              type: 'symbol',
              source: 'user-gps',
              layout: {
                'text-field': ['concat', 'GNSS Location'],
                'text-anchor': 'top',
                'text-offset': [0, 1.5],
                'text-size': 14,
              },
              paint: {
                'text-color': '#ffffff',
                'text-halo-color': '#000000',
                'text-halo-width': 1,
              },
            });
          }

          if (userLocation) {
            map.addSource('user-location', {
              type: 'geojson',
              data: {
                type: 'FeatureCollection',
                features: [
                  {
                    type: 'Feature',
                    geometry: {
                      type: 'Point',
                      coordinates: [
                        userLocation.longitude,
                        userLocation.latitude,
                      ],
                    },
                    properties: {
                      heading: userLocation.heading,
                    },
                  },
                ],
              },
            });

            // Add Pulsing Marker Layer
            map.addLayer({
              id: 'user-location-pulse',
              type: 'circle',
              source: 'user-location',
              paint: {
                'circle-radius': 10,
                'circle-color': '#349ACD',
                'circle-opacity': 0.6,
                'circle-blur': 1,
              },
            });

            // Initialize animation variables
            let pulseRadius = 10;
            let expanding = true;

            // Animation function
            const animatePulse = () => {
              if (expanding) {
                pulseRadius += 0.2; // Reduced step size for slower expansion
                if (pulseRadius >= 20) expanding = false;
              } else {
                pulseRadius -= 0.2; // Reduced step size for slower contraction
                if (pulseRadius <= 10) expanding = true;
              }

              // Update the circle-radius paint property
              map.setPaintProperty(
                'user-location-pulse',
                'circle-radius',
                pulseRadius
              );

              const newOpacity = expanding
                ? Math.min(1, 0.6 + (pulseRadius - 10) / 20)
                : Math.max(0, 0.6 - (pulseRadius - 10) / 20);
              map.setPaintProperty(
                'user-location-pulse',
                'circle-opacity',
                newOpacity
              );

              // Continue the animation
              animationFrameId = requestAnimationFrame(animatePulse);
            };

            // Start the animation
            animatePulse();

            if (locationPopup.current) locationPopup.current.remove();

            locationPopup.current = new maplibregl.Popup({
              closeButton: false,
              closeOnClick: false,
              offset: [0, -15],
              className: 'user-location-popup',
            })
              .setLngLat([userLocation.longitude, userLocation.latitude])
              .setHTML(
                `<div style="color: white;">You are in ${userRoom}</div>`
              )
              .addTo(map);
          }

          map
            .loadImage(locationImage)
            .then(
              (image: GetResourceResponse<HTMLImageElement | ImageBitmap>) => {
                if (!map.hasImage('arrow-15')) {
                  map.addImage('arrow-15', image.data, { sdf: true });
                }

                map.addLayer({
                  id: 'user-orientation',
                  type: 'symbol',
                  source: 'user-location',
                  layout: {
                    'icon-image': 'arrow-15',
                    'icon-size': 1,
                    'icon-allow-overlap': true,
                    'icon-rotate': ['get', 'heading'],
                    'icon-anchor': 'center',
                  },
                  paint: {
                    'icon-color': '#349ACD',
                  },
                });
              }
            )
            .catch((error: Error) => {
              throw error;
            });

          map.addControl(
            new NavigationControl({
              showCompass: true,
              showZoom: false,
              visualizePitch: true,
            }),
            'bottom-left'
          );
        });

        // Clean up on unmount
        return () => {
          map.remove();
          cancelAnimationFrame(animationFrameId);
        };
      }
    }, [
      initialCenter,
      initialZoom,
      initialPitch,
      initialBearing,
      maxBounds,
      userLocation,
      indoorMap,
      userRoom,
      onRoomClick,
      userGPS,
      route,
    ]);

    return (
      <div ref={mapContainer} style={{ width: '100vw', height: '100vh' }}>
        {/* MapLibre map */}
      </div>
    );
  }
);

export default MapLibre;
