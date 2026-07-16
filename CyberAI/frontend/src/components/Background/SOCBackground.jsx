import { useRef, useMemo, useEffect } from 'react';
import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';

function DigitalRain() {
  const count = 100;
  const positions = useMemo(() => {
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 30;
      pos[i * 3 + 1] = (Math.random() - 0.5) * 20;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 20 - 10;
    }
    return pos;
  }, []);

  const meshRef = useRef();
  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.0005;
    }
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
      </bufferGeometry>
      <pointsMaterial
        size={0.08}
        color="#00f0ff"
        transparent
        opacity={0.6}
        sizeAttenuation
      />
    </points>
  );
}

function GridFloor() {
  return (
    <gridHelper args={[30, 30, '#00f0ff', '#1e293b']} position={[0, -5, 0]} />
  );
}

function ConnectionLines() {
  const lineRef = useRef();
  const positions = useMemo(() => {
    const pts = [];
    for (let i = 0; i < 20; i++) {
      const x = (Math.random() - 0.5) * 25;
      const y = (Math.random() - 0.5) * 15;
      const z = (Math.random() - 0.5) * 15 - 5;
      pts.push(new THREE.Vector3(x, y, z));
    }
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    return geo;
  }, []);

  useFrame((state) => {
    if (lineRef.current) {
      lineRef.current.rotation.y += 0.0003;
    }
  });

  return (
    <lineSegments ref={lineRef} geometry={positions}>
      <lineBasicMaterial color="#00f0ff" opacity={0.15} transparent />
    </lineSegments>
  );
}

function HexNodes() {
  const groupRef = useRef();
  const nodes = useMemo(() => {
    const n = [];
    for (let i = 0; i < 8; i++) {
      n.push({
        position: [(Math.random() - 0.5) * 20, (Math.random() - 0.5) * 12, (Math.random() - 0.5) * 15 - 5],
        scale: 0.2 + Math.random() * 0.3,
      });
    }
    return n;
  }, []);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.children.forEach((child, i) => {
        child.rotation.x += 0.005;
        child.rotation.y += 0.01;
      });
    }
  });

  return (
    <group ref={groupRef}>
      {nodes.map((n, i) => (
        <mesh key={i} position={n.position} scale={n.scale}>
          <octahedronGeometry />
          <meshBasicMaterial color="#7c3aed" wireframe transparent opacity={0.3} />
        </mesh>
      ))}
    </group>
  );
}

function MonitoringScreens() {
  return (
    <group position={[8, 2, -8]}>
      {[0, 1, 2].map((i) => (
        <mesh key={i} position={[i * 2.5 - 2.5, 0, 0]}>
          <planeGeometry args={[2, 1.5]} />
          <meshBasicMaterial color="#0a0e17" />
        </mesh>
      ))}
      {[0, 1, 2].map((i) => (
        <mesh key={`border-${i}`} position={[i * 2.5 - 2.5, 0, 0.01]}>
          <planeGeometry args={[2.1, 1.6]} />
          <meshBasicMaterial color="#00f0ff" transparent opacity={0.15} wireframe />
        </mesh>
      ))}
    </group>
  );
}

export default function SOCBackground() {
  return (
    <div className="absolute inset-0 z-0">
      <Canvas camera={{ position: [0, 2, 12], fov: 60 }}>
        <ambientLight intensity={0.3} />
        <DigitalRain />
        <GridFloor />
        <ConnectionLines />
        <HexNodes />
        <MonitoringScreens />
        <fog attach="fog" args={['#0a0e17', 15, 25]} />
      </Canvas>
    </div>
  );
}
