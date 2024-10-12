import { Environment, OrbitControls, useGLTF } from "@react-three/drei";
import { Canvas } from "@react-three/fiber";
import React, { Suspense } from "react";
import * as THREE from "three";
import UserLocationPoint from "../userLocation";
import Model from "../model";
import AxisHelper from "../axisHelper";

export type FloorMapProps = {
  floorMapUrl: string;
  userLocation: [number, number, number];
  bgColor?: string;
  cameraPosition?: [number, number, number];
  cameraFov?: number;
  cameraPose?: [number, number, number];
};

const IndoorMap = ({
  floorMapUrl: floormapUrl,
  userLocation,
  bgColor = "#2F2F2F",
  cameraFov = 90,
  // cameraPose = [-2, 0, -3],
  cameraPosition = [-2, 2, -3],
}: FloorMapProps) => {
  // TODO: fix this lines
  const gltf = useGLTF(floormapUrl);
  const box = new THREE.Box3().setFromObject(gltf.scene);
  const center = box.getCenter(new THREE.Vector3());
  console.log("center", center);
  // gltf.scene.position.set(-center.x, -center.y, -center.z);
  console.log("indoor: gltf.scene.position", gltf.scene.position);

  return (
    <div
      id="canvas-container"
      style={{ width: "100vw", height: "100vh", margin: "0" }}
    >
      <Canvas
        gl={{ antialias: true }}
        style={{ backgroundColor: bgColor }}
        camera={{
          position: center,
          fov: cameraFov,
          near: 0.1,
          far: 1000,
        }}
      >
        <Suspense fallback={null}>
          <Model url={floormapUrl} />

          <Environment preset="sunset" />
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
        </Suspense>
        <UserLocationPoint coordinates={[0, 0, 0]} />

        <OrbitControls
          autoRotateSpeed={1}
          autoRotate
          minDistance={3}
          maxDistance={50}
        />
        <AxisHelper />
      </Canvas>
    </div>
  );
};

export default IndoorMap;
