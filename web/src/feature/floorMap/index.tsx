import useHooks from "./hooks";
import IndoorMap from "../../components/indoorMap";
import floorMapUrl from "../../assets/bk.gltf";
export type FloorMapProps = {};

const FloorMap = ({}: FloorMapProps) => {
  const { userLocation } = useHooks();

  return (
    <IndoorMap
      floorMapUrl={floorMapUrl}
      userLocation={userLocation}
    ></IndoorMap>
  );
};

export default FloorMap;
