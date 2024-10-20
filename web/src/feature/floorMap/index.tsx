import useHooks from './hooks';
import MapLibre from '../../components/maplibre';

export type FloorMapProps = {};

const FloorMap = ({}: FloorMapProps) => {
  const { userLocation, camera, maxBounds } = useHooks();

  return (
    <MapLibre
      initialCamerea={camera}
      maxBounds={maxBounds}
      userLocation={userLocation}
    ></MapLibre>
  );
};

export default FloorMap;
