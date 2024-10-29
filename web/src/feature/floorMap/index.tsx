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
    userRoom,
  } = useHooks();

  return (
    <MapLibre
      initialCamerea={camera}
      maxBounds={maxBounds}
      userLocation={userLocation}
      indoorMap={indoorMap}
      onRoomClick={handleRoomSelect}
      route={route}
      userRoom={userRoom}
    ></MapLibre>
  );
});

export default FloorMap;
