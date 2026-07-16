import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'

function ParticleField() {
  const count = 2000
  const meshRef = useRef<THREE.Points>(null!)

  const [positions, sizes] = useMemo(() => {
    const pos = new Float32Array(count * 3)
    const siz = new Float32Array(count)
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 60
      pos[i * 3 + 1] = (Math.random() - 0.5) * 40
      pos[i * 3 + 2] = (Math.random() - 0.5) * 40 - 10
      siz[i] = Math.random() * 2 + 0.5
    }
    return [pos, siz]
  }, [])

  useFrame((state) => {
    if (meshRef.current) {
      meshRef.current.rotation.y = state.clock.elapsedTime * 0.02
    }
  })

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-position" count={count} array={positions} itemSize={3} />
        <bufferAttribute attach="attributes-size" count={count} array={sizes} itemSize={1} />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        color="#00f0ff"
        transparent
        opacity={0.4}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
        depthWrite={false}
      />
    </points>
  )
}

function GridFloor() {
  return (
    <gridHelper
      args={[40, 40, '#00f0ff', '#1e293b']}
      position={[0, -7, 0]}
    />
  )
}

function ConnectionNetwork() {
  const groupRef = useRef<THREE.Group>(null!)
  const nodes = useMemo(() => {
    const n = []
    for (let i = 0; i < 50; i++) {
      n.push(new THREE.Vector3(
        (Math.random() - 0.5) * 35,
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 25 - 5
      ))
    }
    return n
  }, [])

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.001
    }
  })

  return (
    <group ref={groupRef}>
      {nodes.map((pos, i) => (
        <mesh key={i} position={pos}>
          <sphereGeometry args={[0.04, 6, 6]} />
          <meshBasicMaterial color="#00f0ff" transparent opacity={0.3} />
        </mesh>
      ))}
    </group>
  )
}

function HexGrid() {
  const groupRef = useRef<THREE.Group>(null!)

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += 0.002
    }
  })

  const hexes = useMemo(() => {
    const h = []
    for (let i = 0; i < 15; i++) {
      h.push({
        pos: [(Math.random() - 0.5) * 30, (Math.random() - 0.5) * 18, (Math.random() - 0.5) * 20 - 8] as [number, number, number],
        rot: Math.random() * Math.PI,
        scale: 0.3 + Math.random() * 0.4,
        color: Math.random() > 0.5 ? '#00f0ff' : '#7c3aed',
      })
    }
    return h
  }, [])

  return (
    <group ref={groupRef}>
      {hexes.map((h, i) => (
        <mesh key={i} position={h.pos} rotation={[0, h.rot, 0]} scale={h.scale}>
          <ringGeometry args={[0.4, 0.5, 6]} />
          <meshBasicMaterial color={h.color} transparent opacity={0.12} side={THREE.DoubleSide} />
        </mesh>
      ))}
    </group>
  )
}

function SOCMonitors() {
  return (
    <group position={[10, 2, -12]}>
      {[-1, 0, 1].map((x, i) => (
        <group key={i} position={[x * 3, 0, 0]}>
          <mesh>
            <planeGeometry args={[2.5, 1.8]} />
            <meshBasicMaterial color="#0a0e17" />
          </mesh>
          <mesh position={[0, 0, 0.01]}>
            <planeGeometry args={[2.6, 1.9]} />
            <meshBasicMaterial color="#00f0ff" transparent opacity={0.08} wireframe />
          </mesh>
          {/* Screen content lines */}
          {[0.4, 0.2, 0, -0.2, -0.4].map((y, j) => (
            <mesh key={j} position={[-0.6, y, 0.02]}>
              <planeGeometry args={[1.2 + Math.random() * 0.5, 0.02]} />
              <meshBasicMaterial color="#00f0ff" transparent opacity={0.08} />
            </mesh>
          ))}
        </group>
      ))}
    </group>
  )
}

export default function SOCBackground() {
  return (
    <Canvas
      camera={{ position: [0, 2, 15], fov: 55 }}
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true }}
      style={{ background: '#05080f' }}
    >
      <ambientLight intensity={0.2} />
      <pointLight position={[10, 10, 10]} intensity={0.3} color="#00f0ff" />
      <pointLight position={[-10, -5, -5]} intensity={0.15} color="#7c3aed" />

      <ParticleField />
      <GridFloor />
      <ConnectionNetwork />
      <HexGrid />
      <SOCMonitors />

      <fog attach="fog" args={['#05080f', 18, 30]} />
    </Canvas>
  )
}
