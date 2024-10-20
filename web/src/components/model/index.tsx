import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { useGLTF } from '@react-three/drei';
import { useThree } from '@react-three/fiber';

type ModelProps = {
  url: string;
  color?: string;
  opacity?: number;
  onModelOffest?: (center: [number, number, number]) => void;
};

const Model = ({
  url,
  color = '#0D0D0D',
  opacity = 0.8,
  onModelOffest,
}: ModelProps) => {
  const { scene } = useGLTF(url);
  const modelRef = useRef();
  const { camera } = useThree();

  useEffect(() => {
    scene.rotation.x = THREE.MathUtils.degToRad(270);
    const box = new THREE.Box3().setFromObject(scene);
    const center = box.getCenter(new THREE.Vector3());
    if (center.z < 0) {
      scene.position.z += Math.abs(center.z);
    }

    scene.position.set(-center.x, -center.y, -center.z);

    scene.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        child.material.transparent = true;
        child.material.opacity = opacity;
        child.material.color = new THREE.Color(color);
      }
    });

    onModelOffest && onModelOffest([-center.x, -center.y, -Math.abs(center.z)]);
  }, [url, color, opacity, scene, modelRef, camera]);

  return <primitive object={scene} ref={modelRef} />;
};

export default Model;
