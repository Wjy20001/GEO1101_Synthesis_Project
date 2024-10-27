import { create } from 'zustand';
import { GeoJSON } from 'geojson';

type Route = {
  route: GeoJSON | undefined;
  setRoute: (route: GeoJSON) => void;
};

const useRoute = create<Route>((set) => ({
  route: undefined,
  setRoute: (route) => set(() => ({ route })),
}));

export default useRoute;
