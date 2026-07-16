import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import * as THREE from 'three'
import { useStore } from '../../store/useStore'

function AvatarModel({ isSpeaking }: { isSpeaking: boolean }) {
  const groupRef = useRef<THREE.Group>(null!)
  const headRef = useRef<THREE.Mesh>(null!)
  const lipRef = useRef<THREE.Mesh>(null!)
  const eyeLRef = useRef<THREE.Group>(null!)
  const eyeRRef = useRef<THREE.Group>(null!)
  const eyebrowLRef = useRef<THREE.Mesh>(null!)
  const eyebrowRRef = useRef<THREE.Mesh>(null!)
  const bodyRef = useRef<THREE.Mesh>(null!)
  const hairRef = useRef<THREE.Group>(null!)
  const glowRingRef = useRef<THREE.Mesh>(null!)
  const timeRef = useRef(0)

  const isCallActive = useStore((s) => s.isCallActive)
  const isCallStarting = useStore((s) => s.isCallStarting)

  useFrame((state, delta) => {
    if (!groupRef.current) return
    timeRef.current += delta

    // Floating animation
    groupRef.current.position.y = Math.sin(timeRef.current * 0.6) * 0.08

    // Body breathing
    if (bodyRef.current) {
      bodyRef.current.scale.y = 1 + Math.sin(timeRef.current * 0.8) * 0.005
      bodyRef.current.scale.x = 1 + Math.sin(timeRef.current * 0.8 + 1) * 0.003
    }

    // Head rotation - idle sway
    if (headRef.current) {
      headRef.current.rotation.y = Math.sin(timeRef.current * 0.3) * 0.08
      headRef.current.rotation.x = Math.sin(timeRef.current * 0.4) * 0.02
    }

    // Eye blink
    const blinkCycle = timeRef.current % 3.5
    const isBlinking = blinkCycle > 3.3
    if (eyeLRef.current) {
      eyeLRef.current.scale.y = isBlinking ? 0.1 : 1
    }
    if (eyeRRef.current) {
      eyeRRef.current.scale.y = isBlinking ? 0.1 : 1
    }

    // Eye movement - look around
    if (eyeLRef.current && eyeRRef.current) {
      const lookX = Math.sin(timeRef.current * 0.5) * 0.02
      const lookY = Math.sin(timeRef.current * 0.4) * 0.01
      eyeLRef.current.position.x = 0.02 + lookX
      eyeLRef.current.position.y = 0.02 + lookY
      eyeRRef.current.position.x = -0.02 + lookX
      eyeRRef.current.position.y = 0.02 + lookY
    }

    // Eyebrow animation
    if (eyebrowLRef.current && eyebrowRRef.current) {
      const browRaise = isSpeaking ? 0.1 : 0
      const browMove = Math.sin(timeRef.current * 0.5) * 0.02 + browRaise
      eyebrowLRef.current.position.y = 0.38 + browMove
      eyebrowRRef.current.position.y = 0.38 + browMove
    }

    // Lip sync
    if (lipRef.current) {
      if (isSpeaking) {
        const lipOpen = 0.06 + Math.abs(Math.sin(timeRef.current * 18)) * 0.04
        lipRef.current.position.y = -0.28 + lipOpen * 0.3
        lipRef.current.scale.x = 0.5 + Math.abs(Math.sin(timeRef.current * 15)) * 0.08
      } else {
        lipRef.current.position.y = -0.28
        lipRef.current.scale.x = 0.5
      }
    }

    // Glowing ring rotation
    if (glowRingRef.current) {
      glowRingRef.current.rotation.z += delta * 0.3
    }

    // Hair animation
    if (hairRef.current) {
      hairRef.current.children.forEach((child, i) => {
        child.rotation.z = Math.sin(timeRef.current * 0.5 + i) * 0.02
      })
    }

    // When thinking - look up slightly
    if (isCallStarting && headRef.current) {
      headRef.current.rotation.x = -0.08 + Math.sin(timeRef.current) * 0.02
    }
  })

  return (
    <group ref={groupRef}>
      {/* Holographic glow ring */}
      <mesh ref={glowRingRef} rotation={[Math.PI / 2, 0, 0]} position={[0, -1.2, 0]}>
        <ringGeometry args={[0.8, 1.2, 64]} />
        <meshBasicMaterial
          color="#00f0ff"
          transparent
          opacity={isCallActive ? 0.15 : 0.05}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Body */}
      <mesh ref={bodyRef} position={[0, -1, 0]}>
        <capsuleGeometry args={[0.4, 0.8, 8, 16]} />
        <meshStandardMaterial
          color="#1a1040"
          roughness={0.4}
          metalness={0.6}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Shoulders */}
      <mesh position={[-0.55, -0.6, 0]} rotation={[0, 0, -0.3]}>
        <sphereGeometry args={[0.25, 12, 12]} />
        <meshStandardMaterial color="#1a1040" roughness={0.4} metalness={0.5} />
      </mesh>
      <mesh position={[0.55, -0.6, 0]} rotation={[0, 0, 0.3]}>
        <sphereGeometry args={[0.25, 12, 12]} />
        <meshStandardMaterial color="#1a1040" roughness={0.4} metalness={0.5} />
      </mesh>

      {/* Neck */}
      <mesh position={[0, -0.25, 0]}>
        <cylinderGeometry args={[0.18, 0.25, 0.25, 12]} />
        <meshStandardMaterial color="#2d1b69" roughness={0.3} />
      </mesh>

      {/* Head */}
      <mesh ref={headRef} position={[0, 0.1, 0]}>
        <sphereGeometry args={[0.35, 32, 32]} />
        <meshStandardMaterial
          color="#2d1b69"
          roughness={0.2}
          metalness={0.1}
        />
      </mesh>

      {/* Hair */}
      <group ref={hairRef} position={[0, 0.4, 0]}>
        {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => {
          const angle = (i / 8) * Math.PI * 2
          return (
            <mesh key={i} position={[Math.cos(angle) * 0.38, -0.05, Math.sin(angle) * 0.38]}
              rotation={[0.2, -angle, 0]}
            >
              <boxGeometry args={[0.02, 0.15 + Math.random() * 0.05, 0.02]} />
              <meshBasicMaterial color="#0a0e17" />
            </mesh>
          )
        })}
        {/* Top hair */}
        <mesh position={[0, 0.08, 0]}>
          <sphereGeometry args={[0.36, 16, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
          <meshBasicMaterial color="#0a0e17" />
        </mesh>
      </group>

      {/* Face features */}
      {/* Eyes - Left */}
      <group ref={eyeLRef} position={[-0.12, 0.12, 0.32]}>
        <mesh>
          <sphereGeometry args={[0.05, 12, 12]} />
          <meshBasicMaterial color="#111827" />
        </mesh>
        <mesh position={[0, 0, 0.03]}>
          <sphereGeometry args={[0.025, 8, 8]} />
          <meshBasicMaterial color="#00f0ff" />
        </mesh>
        <mesh position={[0, 0, 0.045]}>
          <sphereGeometry args={[0.01, 6, 6]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
      </group>

      {/* Eyes - Right */}
      <group ref={eyeRRef} position={[0.12, 0.12, 0.32]}>
        <mesh>
          <sphereGeometry args={[0.05, 12, 12]} />
          <meshBasicMaterial color="#111827" />
        </mesh>
        <mesh position={[0, 0, 0.03]}>
          <sphereGeometry args={[0.025, 8, 8]} />
          <meshBasicMaterial color="#00f0ff" />
        </mesh>
        <mesh position={[0, 0, 0.045]}>
          <sphereGeometry args={[0.01, 6, 6]} />
          <meshBasicMaterial color="#ffffff" />
        </mesh>
      </group>

      {/* Eyebrows */}
      <mesh ref={eyebrowLRef} position={[-0.12, 0.38, 0.32]}>
        <boxGeometry args={[0.12, 0.015, 0.02]} />
        <meshBasicMaterial color="#7c3aed" />
      </mesh>
      <mesh ref={eyebrowRRef} position={[0.12, 0.38, 0.32]}>
        <boxGeometry args={[0.12, 0.015, 0.02]} />
        <meshBasicMaterial color="#7c3aed" />
      </mesh>

      {/* Nose */}
      <mesh position={[0, 0.05, 0.35]}>
        <sphereGeometry args={[0.015, 6, 6]} />
        <meshBasicMaterial color="#3d1f7a" />
      </mesh>

      {/* Lips */}
      <mesh ref={lipRef} position={[0, -0.1, 0.34]}>
        <boxGeometry args={[0.2, 0.025, 0.015]} />
        <meshBasicMaterial color="#7c3aed" />
      </mesh>

      {/* Lip bottom */}
      <mesh position={[0, -0.13, 0.34]}>
        <boxGeometry args={[0.16, 0.02, 0.01]} />
        <meshBasicMaterial color="#6d28d9" />
      </mesh>

      {/* Holographic HUD elements */}
      {[-0.5, 0.5].map((x, i) => (
        <mesh key={`hud-${i}`} position={[x, 0.5, 0]} rotation={[0, 0, Math.PI / 2]}>
          <planeGeometry args={[0.3, 0.01]} />
          <meshBasicMaterial color="#00f0ff" transparent opacity={isCallActive ? 0.3 : 0.1} />
        </mesh>
      ))}

      {/* Ring particles */}
      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => {
        const angle = (i / 8) * Math.PI * 2
        return (
          <mesh key={`ring-${i}`} position={[Math.cos(angle) * 0.5, -0.3, Math.sin(angle) * 0.5]}>
            <sphereGeometry args={[0.01, 4, 4]} />
            <meshBasicMaterial color="#00f0ff" transparent opacity={0.4} />
          </mesh>
        )
      })}
    </group>
  )
}

export default function CyberAvatar() {
  const isSpeaking = useStore((s) => s.isSpeaking)
  const isCallActive = useStore((s) => s.isCallActive)

  return (
    <div className="relative w-full h-full flex items-center justify-center">
      <div className="relative" style={{ width: '55vh', height: '55vh', maxWidth: '500px', maxHeight: '500px' }}>
        <Canvas
          camera={{ position: [0, 0.5, 2.5], fov: 20 }}
          dpr={[1, 2]}
          gl={{ antialias: true, alpha: true }}
        >
          <ambientLight intensity={0.8} />
          <pointLight position={[2, 3, 4]} intensity={0.6} color="#00f0ff" />
          <pointLight position={[-2, 1, 3]} intensity={0.3} color="#7c3aed" />
          <directionalLight position={[1, 2, 3]} intensity={0.4} />

          <AvatarModel isSpeaking={isSpeaking} />
        </Canvas>

        {/* Glow effect around avatar */}
        <div className={`absolute inset-0 rounded-full transition-all duration-700 pointer-events-none ${
          isCallActive
            ? 'opacity-100'
            : 'opacity-30'
        }`}
          style={{
            background: 'radial-gradient(circle at center, rgba(0,240,255,0.06) 0%, transparent 70%)',
            boxShadow: 'inset 0 0 80px rgba(0,240,255,0.05)',
          }}
        />
      </div>
    </div>
  )
}
