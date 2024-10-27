import { create } from 'zustand';

interface Destination {
  destination: string | undefined;
  setDestination: (destination: string | undefined) => void;
}
const useDestination = create<Destination>((set) => {
  return {
    destination: undefined,
    setDestination: (destination) => set(() => ({ destination })),
  };
});

export default useDestination;
