import { useRef, useMemo, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import useStore from '../../store/useStore';

function AvatarHead({ isSpeaking }) {
  const meshRef = useRef();
  const lipRef = useRef();
  const eyeLRef = useRef();
  const eyeRRef = useRef();
  const timeRef = useRef(0);

  useFrame((state, delta) => {
    if (!meshRef.current) return;
    timeRef.current += delta;

    // Gentle idle sway
    meshRef.current.position.y = Math.sin(timeRef.current * 0.5) * 0.05;
    meshRef.current.rotation.y = Math.sin(timeRef.current * 0.3) * 0.1;

    // Blink
    const blinkCycle = timeRef.current % 4;
    if (blinkCycle > 3.9) {
      if (eyeLRef.current) eyeLRef.current.scale.y = 0.1;
      if (eyeRRef.current) eyeRRef.current.scale.y = 0.1;
    } else {
      if (eyeLRef.current) eyeLRef.current.scale.y = 1;
      if (eyeRRef.current) eyeRRef.current.scale.y = 1;
    }

    // Lip sync when speaking
    if (lipRef.current && isSpeaking) {
      lipRef.current.position.y = -0.25 + Math.sin(timeRef.current * 15) * 0.04;
      lipRef.current.scale.x = 0.6 + Math.sin(timeRef.current * 12) * 0.1;
    } else if (lipRef.current) {
      lipRef.current.position.y = -0.25;
      lipRef.current.scale.x = 0.6;
    }

    // Head nod when speaking
    if (isSpeaking) {
      meshRef.current.rotation.x = Math.sin(timeRef.current * 2) * 0.03;
    }
  });

  return (
    <group ref={meshRef}>
      {/* Head base */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.6, 32, 32]} />
        <meshStandardMaterial color="#2d1b69" roughness={0.3} metalness={0.1} />
      </mesh>

      {/* Neck */}
      <mesh position={[0, -0.7, 0]}>
        <cylinderGeometry args={[0.25, 0.35, 0.3, 16]} />
        <meshStandardMaterial color="#1a1040" roughness={0.5} />
      </mesh>

      {/* Eyes - Left */}
      <group ref={eyeLRef} position={[-0.2, 0.15, 0.55]}>
        <mesh>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshBasicMaterial color="#00f0ff" />
        </mesh>
        <mesh position={[0, 0, 0.04]}>
          <sphereGeometry args={[0.04, 8, 8]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
      </group>

      {/* Eyes - Right */}
      <group ref={eyeRRef} position={[0.2, 0.15, 0.55]}>
        <mesh>
          <sphereGeometry args={[0.08, 16, 16]} />
          <meshBasicMaterial color="#00f0ff" />
        </mesh>
        <mesh position={[0, 0, 0.04]}>
          <sphereGeometry args={[0.04, 8, 8]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
      </group>

      {/* Lips */}
      <mesh ref={lipRef} position={[0, -0.25, 0.58]}>
        <boxGeometry args={[0.25, 0.04, 0.02]} />
        <meshBasicMaterial color="#7c3aed" />
      </mesh>

      {/* Eyebrows */}
      <mesh position={[-0.2, 0.32, 0.55]}>
        <boxGeometry args={[0.15, 0.02, 0.02]} />
        <meshBasicMaterial color="#7c3aed" />
      </mesh>
      <mesh position={[0.2, 0.32, 0.55]}>
        <boxGeometry args={[0.15, 0.02, 0.02]} />
        <meshBasicMaterial color="#7c3aed" />
      </mesh>

      {/* Holographic ring */}
      <mesh rotation={[Math.PI / 2, 0, 0]} position={[0, -0.5, 0]}>
        <ringGeometry args={[0.5, 0.7, 32]} />
        <meshBasicMaterial color="#00f0ff" transparent opacity={0.2} side={THREE.DoubleSide} />
      </mesh>

      {/* HUD elements around head */}
      {[-0.7, 0.7].map((x, i) => (
        <mesh key={`hud-${i}`} position={[x, 0.3, 0]} rotation={[0, 0, Math.PI / 2]}>
          <planeGeometry args={[0.4, 0.02]} />
          <meshBasicMaterial color="#00f0ff" transparent opacity={0.4} />
        </mesh>
      ))}
    </group>
  );
}

export default function CyberAvatar() {
  const isProcessing = useStore((s) => s.isProcessing);

  return (
    <div className="absolute top-0 left-0 right-0 z-20 flex justify-center pointer-events-none" style={{ height: '220px' }}>
      <div className="relative w-48 h-48 mt-2">
        <Canvas camera={{ position: [0, 0, 3], fov: 30 }}>
          <ambientLight intensity={0.8} />
          <pointLight position={[5, 5, 5]} intensity={0.5} />
          <AvatarHead isSpeaking={isProcessing} />
        </Canvas>

        <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 bg-cyber-primary/10 border border-cyber-primary/30 rounded-full px-4 py-1">
          <span className="text-xs text-cyber-primary font-mono glow-text">
            {isProcessing ? '▸ PROCESANDO...' : '▸ EN ESPERA'}
          </span>
        </div>
      </div>
    </div>
  );
}
