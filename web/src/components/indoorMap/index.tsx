import { Environment, OrbitControls, useGLTF } from '@react-three/drei';
import { Canvas } from '@react-three/fiber';
import React, { Suspense, useEffect, useMemo, useState } from 'react';
import UserLocationPoint from '../userLocation';
import Model from '../model';
import AxisHelper from '../axisHelper';

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
  bgColor = '#2F2F2F',
  cameraFov = 90,
  // cameraPose = [-2, 0, -3],
  cameraPosition = [-2, 2, -3],
}: FloorMapProps) => {
  const [modelOffest, setModelOffest] = useState<[number, number, number]>([
    0, 0, 0,
  ]);

  const offsetUserLocation: [number, number, number] = useMemo(() => {
    return [
      userLocation[0] + modelOffest[0],
      2,
      userLocation[1] + modelOffest[2],
    ];
  }, [userLocation, modelOffest]);

  return (
    <div
      id="canvas-container"
      style={{ width: '100vw', height: '100vh', margin: '0' }}
    >
      <Canvas
        gl={{ antialias: true }}
        style={{ backgroundColor: bgColor }}
        camera={{
          position: cameraPosition,
          fov: cameraFov,
          near: 0.1,
          far: 100000,
        }}
      >
        <Suspense fallback={null}>
          <Model url={floormapUrl} onModelOffest={setModelOffest} />

          <Environment preset="sunset" />
          <ambientLight intensity={0.5} />
          <directionalLight position={[10, 10, 5]} intensity={1} />
        </Suspense>
        <UserLocationPoint coordinates={offsetUserLocation} />

        <OrbitControls
          autoRotateSpeed={1}
          autoRotate
          // minDistance={3}
          // maxDistance={50}
        />
        <AxisHelper />
      </Canvas>
    </div>
  );
};

export default IndoorMap;
