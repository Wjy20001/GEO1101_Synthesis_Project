import React, { useRef } from "react";
import * as THREE from "three";
import { Sphere } from "@react-three/drei";
import { useSpring, a } from "@react-spring/three";

type AnimatedPulseProps = {
  color?: string;
  opacity?: number;
  position?: [number, number, number];
};

const AnimatedPulse = ({ color = "#00aaff", position }: AnimatedPulseProps) => {
  const outerSphereRef = useRef<THREE.Mesh>(null);

  const { scale, opacity } = useSpring({
    scale: [1.5, 1.5, 1.5],
    opacity: 0.2,
    config: { tension: 80, friction: 20 },
    loop: { reverse: true },
    from: { scale: [1, 1, 1], opacity: 0.4 },
  });

  return (
    <a.mesh ref={outerSphereRef} scale={scale}>
      <Sphere args={[0.5, 32, 32]} position={position}>
        <a.meshBasicMaterial
          attach="material"
          color={color}
          opacity={opacity}
          transparent={true}
        />
      </Sphere>
    </a.mesh>
  );
};

export type UserLocationPointProps = {
  coordinates: [number, number, number];
  innerColor?: string;
  outerColor?: string;
};

const UserLocationPoint = ({
  coordinates,
  innerColor = "#007bff",
  outerColor = "#00aaff",
}: UserLocationPointProps) => {
  const innerSphereRef = useRef<THREE.Mesh>(null);

  return (
    <>
      <mesh ref={innerSphereRef} position={coordinates}>
        <Sphere args={[0.3, 32, 32]}>
          <meshBasicMaterial color={innerColor} />
        </Sphere>
      </mesh>

      <AnimatedPulse color={outerColor} position={coordinates} />
    </>
  );
};

export default UserLocationPoint;
