import { useState, useEffect } from 'react';

const useGeolocation = ({
  setLocation,
}: {
  setLocation: (position: { lat: number; lng: number }) => void;
}) => {
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }

    const success = (position: GeolocationPosition) => {
      const { latitude, longitude } = position.coords;
      setLocation({ lat: latitude, lng: longitude });
    };

    const error = () => {
      setError('Unable to retrieve your location');
    };

    navigator.geolocation.watchPosition(success, error);
  }, []);
  return { error };
};

export default useGeolocation;
