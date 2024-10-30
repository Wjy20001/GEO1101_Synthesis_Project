import { create } from 'zustand';

interface Position {
  lat: number;
  lng: number;
}

interface UserGPS {
  position?: Position;
  setLocation: (position: Position) => void;
}

const useUserLocation = create<UserGPS>((set) => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        set({
          position: { lat: latitude, lng: longitude },
        });
      },
      (error) => {
        console.error('Geolocation error:', error);
      }
    );
  } else {
    console.warn('Geolocation is not supported by this browser.');
  }

  return {
    position: {
      lat: 52.01585831525125,
      lng: 4.370286572894657,
      room: 'main_entrance',
    },
    setLocation: (position) => set({ position }),
  };
});

export default useUserLocation;
