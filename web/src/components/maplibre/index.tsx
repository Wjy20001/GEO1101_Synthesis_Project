import React, { useEffect, useRef } from 'react';
import maplibregl, { GetResourceResponse } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
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
  route?: GeoJSON;
  indoorMap?: GeoJSON;
}

const MapLibre: React.FC<MapLibreProps> = ({
  initialCamerea,
  maxBounds,
  userLocation,
  route,
  indoorMap,
}) => {
  const {
    center: initialCenter,
    zoom: initialZoom,
    pitch: initialPitch,
    bearing: initialBearing,
  } = initialCamerea || {};

  const mapContainer = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (mapContainer.current) {
      const map = new maplibregl.Map({
        container: mapContainer.current,
        style:
          'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        center: initialCenter, // Initial center
        zoom: initialZoom, // Initial zoom
        pitch: initialPitch, // Initial pitch
        bearing: initialBearing, // Initial bearing
        maxBounds: maxBounds, // Constrain the map view to the specified bounds
      });

      let animationFrameId: number;

      map.on('load', () => {
        // Add line string
        if (route) {
          map.addSource('route', {
            type: 'geojson',
            data: route,
          });
          map.addLayer({
            id: 'route',
            type: 'line',
            source: 'route',
            paint: {
              'line-color': '#349ACD',
              'line-width': 5,
            },
          });
        }

        if (indoorMap) {
          map.addSource('floor-map', {
            type: 'geojson',
            data: indoorMap,
          });
          map.addLayer({
            id: 'floor-map',
            type: 'fill',
            source: 'floor-map', // Corrected source ID
            paint: {
              'fill-color': '#ff00ff', //TODO: change later
              'fill-opacity': 0.8,
            },
          });
        }

        // Change cursor to pointer on hover
        map.on('mouseenter', 'floor-map', () => {
          // Corrected layer ID
          map.getCanvas().style.cursor = 'pointer';
        });

        map.on('mouseleave', 'floor-map', () => {
          // Corrected layer ID
          map.getCanvas().style.cursor = '';
        });

        // Add User Location Layer
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

            // Optionally, update circle-opacity for a fading effect
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
        }

        // Add Orientation Indicator Layer
        map
          .loadImage(locationImage)
          .then(
            (image: GetResourceResponse<HTMLImageElement | ImageBitmap>) => {
              if (!map.hasImage('arrow-15')) {
                map.addImage('arrow-15', image.data, { sdf: true });
              }

              // Add the symbol layer after the image is added
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
    userLocation, // Added userLocation to dependency array
  ]);

  return (
    <div ref={mapContainer} style={{ width: '100vw', height: '100vh' }}>
      {/* MapLibre map */}
    </div>
  );
};

export default MapLibre;
