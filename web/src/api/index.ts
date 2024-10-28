import { useCallback } from 'react';
import {
  useDestination,
  useLoading,
  useRoute,
  useUserLocation,
} from '../state';
import { GeoJSON } from 'geojson';

const BASE_URL = 'https://http://127.0.0.1:8000';

export const useAPI = () => {
  const setLoading = useLoading((state) => state.setLoading);
  const setRoute = useRoute((state) => state.setRoute);
  const userLocations = useUserLocation((state) => state.position);
  const selectedRoom = useDestination((state) => state.destination);
  const uploadPhotos = useCallback(
    async (
      photos: File[]
    ): Promise<{ user_coordinate: [number, number]; user_room: string }> => {
      setLoading(true);
      const formData = new FormData();
      photos.forEach((photo) => {
        formData.append('photos', photo);
      });

      const response = await fetch(`${BASE_URL}/localize`, {
        method: 'POST',
        body: formData,
      });
      setLoading(false);
      if (!response.ok) {
        throw new Error('Failed to upload photos');
      }

      return response.json();
    },
    []
  );

  const searchRoute = useCallback(async () => {
    setLoading(true);
    // const response = await fetch(
    //   `${BASE_URL}/navigate?roomName=${roomName}&userLocation=${userLocation.room}
    // );

    // if (!response.ok) {
    //   throw new Error('Failed to search route');
    // }
    // Simulating a delay of 1 second for debugging purposes
    await new Promise((resolve) => setTimeout(resolve, 1000));

    // Mocking the API response for debugging
    const response = {
      ok: true,
      json: () =>
        Promise.resolve({
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              geometry: {
                type: 'LineString',
                coordinates: [
                  [userLocation.lng, userLocation.lat],
                  [userLocation.lng + 0.0001, userLocation.lat + 0.0001],
                  [userLocation.lng + 0.0002, userLocation.lat + 0.0002],
                ],
              },
              properties: {},
            },
          ],
        } as GeoJSON),
    };
    setRoute(await response.json());
    setLoading(false);
  }, []);

  return { uploadPhotos, searchRoute };
};
