import React from "react";
import * as THREE from "three";
import { useLoader } from "@react-three/fiber";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

type ModelProps = {
  url: string;
  color?: string;
  opacity?: number;
};

const Model = ({ url, color = "#000", opacity = 0.8 }: ModelProps) => {
  const gltf = useLoader(GLTFLoader, url);

  const box = new THREE.Box3().setFromObject(gltf.scene);
  const center = box.getCenter(new THREE.Vector3());
  gltf.scene.position.set(-center.x, -center.y, -center.z);
  console.log("model: gltf scene position", gltf.scene.position);

  // TODO: generalise this rotation
  gltf.scene.rotation.x = THREE.MathUtils.degToRad(-90);
  gltf.scene.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.material.transparent = true;
      child.material.opacity = opacity;
      child.material.color = new THREE.Color(color);
    }
  });

  return <primitive object={gltf.scene} />;
};

export default Model;
