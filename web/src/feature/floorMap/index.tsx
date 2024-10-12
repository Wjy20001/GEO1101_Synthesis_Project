import useHooks from "./hooks";
import floormapUrl from "../../assets/bk.gltf";
import IndoorMap from "../../components/indoorMap";
import React, { useEffect } from "react";

export type FloorMapProps = {};

const FloorMap = ({}: FloorMapProps) => {
  const { userLocation } = useHooks();

  navigator.geolocation.watchPosition((position) => {
    console.log("position", position);
  });
  return (
    <IndoorMap
      floorMapUrl={floormapUrl}
      userLocation={userLocation}
    ></IndoorMap>
  );
};

export default FloorMap;
