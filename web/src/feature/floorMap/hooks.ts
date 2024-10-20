import { useMemo } from 'react';
import { useUserLocation } from '../../state/userLocation';
import { Camerea, UserLocation } from '../../components/maplibre';

const useFloorMap = () => {
  const { position } = useUserLocation();
  const userLocation: UserLocation = useMemo(
    () => ({
      longitude: position.lng,
      latitude: position.lat,
      heading: 0,
    }),
    [position]
  );
  const camera: Camerea = {
    center: [4.370632073495202, 52.005614398576945],
    zoom: 17,
    pitch: 0,
    bearing: 0,
  };

  const maxBounds: [[number, number], [number, number]] = [
    [4.367417989524314, 52.00093467046407],
    [4.475395988362235, 52.00736618403458],
  ];

  return { userLocation, camera, maxBounds };
};

export default useFloorMap;
