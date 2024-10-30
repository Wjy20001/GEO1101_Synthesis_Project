import { useCallback } from 'react';
import {
  useDestination,
  useLoading,
  useRoute,
  useUserLocation,
} from '../state';

const BASE_URL =
  process.env.NODE_ENV === 'production'
    ? 'https://synthesis-api-264879243442.europe-west1.run.app'
    : 'http://127.0.0.1:8000';

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
        formData.append('files', photo);
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
    if (!selectedRoom || !userLocations.room) return;

    setLoading(true);
    const response = await fetch(
      `${BASE_URL}/navigate?start_room_name=${userLocations.room}&end_room_name=${selectedRoom}`
    );

    setRoute(await response.json());
    setLoading(false);
  }, [setLoading, setRoute, selectedRoom, userLocations.room]);

  return { uploadPhotos, searchRoute };
};
