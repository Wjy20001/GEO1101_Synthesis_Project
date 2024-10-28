import { useMemo, useState, useEffect, useCallback } from 'react';
import { useDestination, useRoute, useUserLocation } from '../../state';
import { Camerea, UserLocation } from '../../components/maplibre';
import indoorMap from '../../assets/floorplan.geojson';
import { GeoJSON } from 'geojson';

const useFloorMap = () => {
  const position = useUserLocation((state) => state.position);
  const selectRoom = useDestination((state) => state.setDestination);
  const selectedRoom = useDestination((state) => state.destination);
  const route = useRoute((state) => state.route);
  const handleRoomSelect = useCallback(
    (roomId: string | null) => {
      console.log('room id: ', roomId);
      if (!roomId) return;
      selectRoom(roomId);
    },
    [selectRoom]
  );

  const userLocation: UserLocation = useMemo(
    () => ({
      longitude: position.lng,
      latitude: position.lat,
      heading: 0,
    }),
    [position]
  );

  useEffect(() => {
    console.log('rooooooooooooo', selectedRoom);
  }, [selectedRoom]);

  const [floorMap, setFloorMap] = useState<GeoJSON | undefined>(undefined);

  useEffect(() => {
    const fetchGeoJSON = async () => {
      try {
        const response = await fetch(indoorMap);
        const data: GeoJSON = await response.json();
        setFloorMap(data);
      } catch (error) {
        console.error('Error fetching GeoJSON:', error);
      }
    };

    fetchGeoJSON();
  }, []);

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

  return {
    userLocation,
    camera,
    maxBounds,
    indoorMap: floorMap,
    route,
    handleRoomSelect,
  };
};

export default useFloorMap;
