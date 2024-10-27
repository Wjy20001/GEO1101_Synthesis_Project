import React from 'react';
import useHooks from './hooks';
import MapLibre from '../../components/maplibre';

export type FloorMapProps = {};

const FloorMap = React.memo(({}: FloorMapProps) => {
  const {
    userLocation,
    camera,
    maxBounds,
    indoorMap,
    route,
    handleRoomSelect,
  } = useHooks();

  return (
    <MapLibre
      initialCamerea={camera}
      maxBounds={maxBounds}
      userLocation={userLocation}
      indoorMap={indoorMap}
      onRoomClick={handleRoomSelect}
      route={route}
    ></MapLibre>
  );
});

export default FloorMap;
