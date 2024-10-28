import { create } from 'zustand';

interface Position {
  lat: number;
  lng: number;
  room: string;
}

interface UserLocation {
  position: Position;
  setLocation: (position: Position) => void;
}

const useUserLocation = create<UserLocation>((set) => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const { latitude, longitude } = pos.coords;
        set({
          position: { lat: latitude, lng: longitude, room: 'main_entrance' },
        });
        console.log('User location:', { lat: latitude, lng: longitude });
      },
      (error) => {
        console.error('Geolocation error:', error);
        // Optionally handle the error or keep the default position
      }
    );
  } else {
    console.warn('Geolocation is not supported by this browser.');
  }

  // Set the default position
  return {
    position: {
      lat: 52.005668180596146,
      lng: 4.37070135981498,
      room: 'hall_p',
    },
    setLocation: (position) => set({ position }),
  };
});

export default useUserLocation;
