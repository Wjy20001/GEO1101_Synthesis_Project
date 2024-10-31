import { create } from 'zustand';

interface Position {
  lat: number;
  lng: number;
}

interface UserGPS {
  position?: Position;
  setLocation: (position: Position) => void;
  startWatching: () => void;
  stopWatching: () => void;
}

const useUserLocation = create<UserGPS>((set) => {
  let watchId: number | null = null;

  const startWatching = () => {
    if (!navigator.geolocation) {
      console.warn('Geolocation is not supported by this browser.');
      return;
    }

    watchId = navigator.geolocation.watchPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        set({
          position: { lat: latitude, lng: longitude },
        });
      },
      (error) => {
        console.error('Geolocation error:', error);
      },
      {
        enableHighAccuracy: true,
        timeout: 5000,
        maximumAge: 0,
      }
    );
  };

  const stopWatching = () => {
    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId);
      watchId = null;
    }
  };

  // Get initial position
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        set({
          position: { lat: latitude, lng: longitude },
        });
      },
      (error) => {
        console.error('Initial geolocation error:', error);
      }
    );
  }

  return {
    position: {
      lat: 52.01585831525125,
      lng: 4.370286572894657,
      room: 'main_entrance',
    },
    setLocation: (position) => set({ position }),
    startWatching,
    stopWatching,
  };
});

export default useUserLocation;
