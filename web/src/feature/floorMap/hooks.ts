import { useEffect, useMemo, useState } from "react";
import useGeolocation from "../../hooks/geolocation";
import { useUserLocation } from "../../state/userLocation";
import projection from "../../utils/proj";

const useFloorMap = () => {
  // const { position, setLocation } = useUserLocation();
  // const { error } = useGeolocation({ setLocation });
  const [position, setPosition] = useState({ lat: 0, lng: 0 });
  useEffect(() => {
    setPosition({ lat: 52.00569074902927, lng: 4.370753588519562 });
  }, []);

  const userLocation: [number, number, number] = useMemo(() => {
    if (position.lat && position.lng) {
      const { x, y } = projection(position.lng, position.lat);
      return [x, y, 0];
    }
    return [0, 0, 0];
  }, [position]);

  return { userLocation };
};

export default useFloorMap;
