import { create } from "zustand";

type UserLocation = {
  position: {
    lat: number;
    lng: number;
  };
  setLocation: (position: { lat: number; lng: number }) => void;
};

const useUserLocation = create<UserLocation>((set) => ({
  position: { lat: 0, lng: 0 },
  setLocation: ({ lat, lng }) => set(() => ({ position: { lat, lng } })),
}));

export { useUserLocation };
