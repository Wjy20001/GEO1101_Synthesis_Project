import { create } from 'zustand';

type UserLocation = {
  position: {
    lat: number;
    lng: number;
  };
  setLocation: (position: { lat: number; lng: number }) => void;
};

type Loading = {
  loading: boolean;
  setLoading: (loading: boolean) => void;
};

const useUserLocation = create<UserLocation>((set) => ({
  position: { lat: 0, lng: 0 },
  setLocation: (position) => set(() => ({ position })),
}));

const useLoading = create<Loading>((set) => ({
  loading: false,
  setLoading: (loading) => set(() => ({ loading })),
}));

export { useUserLocation, useLoading };
