import { Sphere } from "@react-three/drei";
import { useSpring, animated } from "@react-spring/three";

type AnimatedPulseProps = {
  color?: string;
  position: [number, number, number];
};

const AnimatedPulse = ({ color = "#00aaff", position }: AnimatedPulseProps) => {
  const { scale } = useSpring({
    scale: [1.5, 1.5, 1.5],
    config: { tension: 80, friction: 20 },
    loop: { reverse: true },
    from: { scale: [1, 1, 1] },
  });

  return (
    <animated.mesh position={position} scale={scale}>
      <Sphere args={[0.5, 32, 32]}>
        <meshBasicMaterial
          attach="material"
          color={color}
          opacity={0.2}
          transparent={true}
        />
      </Sphere>
    </animated.mesh>
  );
};

type UserLocationPointProps = {
  coordinates: [number, number, number];
  innerColor?: string;
  outerColor?: string;
};

const UserLocationPoint = ({
  coordinates,
  innerColor = "#007bff",
  outerColor = "#00aaff",
}: UserLocationPointProps) => {
  return (
    <>
      <mesh position={coordinates}>
        <Sphere args={[0.3, 32, 32]}>
          <meshBasicMaterial color={innerColor} />
        </Sphere>
      </mesh>

      <AnimatedPulse color={outerColor} position={coordinates} />
    </>
  );
};

export default UserLocationPoint;
