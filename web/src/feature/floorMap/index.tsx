import React from 'react';
import useHooks from './hooks';
import MapLibre from '../../components/maplibre';
import { GeoJSON } from 'geojson';

export type FloorMapProps = {
  onRoomSelect?: (room: string) => void;
  route?: GeoJSON;
};

const FloorMap = React.memo(({ onRoomSelect, route }: FloorMapProps) => {
  const { userLocation, camera, maxBounds, indoorMap } = useHooks();

  return (
    <MapLibre
      initialCamerea={camera}
      maxBounds={maxBounds}
      userLocation={userLocation}
      indoorMap={indoorMap}
      onRoomClick={onRoomSelect}
      route={route}
    ></MapLibre>
  );
});

export default FloorMap;
