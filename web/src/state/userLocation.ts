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
  return {
    position: {
      lat: 52.00585831525125,
      lng: 4.370286572894657,
      room: 'main_entrance',
    },
    setLocation: (position) => set({ position }),
  };
});

export default useUserLocation;
