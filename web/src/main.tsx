import React, { useState } from "react";
import "./main.css";
import FarmLogo from "./assets/logo.png";
import floorMapUrl from "./assets/bk.gltf";
import AppProvider from "./provider";
import { Button } from "@mantine/core";
import FloorMap from "./feature/floorMap";

export function Main() {
  return (
    <AppProvider>
      <div>hoge</div>
      <FloorMap floormapUrl={floorMapUrl} userLocation={[0, 0, 0]} />
    </AppProvider>
  );
}
