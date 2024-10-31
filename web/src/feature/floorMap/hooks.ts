import { useMemo, useState, useEffect, useCallback } from 'react';
import {
  useDestination,
  useRoute,
  useUserGPS,
  useUserLocation,
} from '../../state';
import { Camerea, UserLocation } from '../../components/maplibre';
import indoorMap from '../../assets/floorplan.geojson';
import { GeoJSON } from 'geojson';

const useFloorMap = () => {
  const position = useUserLocation((state) => state.position);
  const userGPS = useUserGPS((state) => state.position);
  const watchGPS = useUserGPS((state) => state.startWatching);
  const stopWatchGPS = useUserGPS((state) => state.stopWatching);
  const selectRoom = useDestination((state) => state.setDestination);
  const route = useRoute((state) => state.route);

  useEffect(() => {
    watchGPS();
    return () => {
      stopWatchGPS();
    };
  }, []);

  const handleRoomSelect = useCallback(
    (roomId: string | null) => {
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
    [4.369105271117121, 52.00440918787575],
    [4.371939161759968, 52.007189541331286],
  ];

  return {
    userLocation,
    camera,
    maxBounds,
    indoorMap: floorMap,
    route,
    handleRoomSelect,
    userRoom: position.room,
    userGPS,
  };
};

export default useFloorMap;
