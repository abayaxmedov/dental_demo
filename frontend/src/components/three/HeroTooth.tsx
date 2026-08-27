"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

// Tish profili (radius, balandlik) — pastdagi ildiz uchidan yuqori tojgacha. Lathe Y atrofida.
const PROFILE: [number, number][] = [
  [0.03, -1.4],
  [0.16, -0.95],
  [0.27, -0.45],
  [0.4, 0.0], // boʻyin
  [0.5, 0.4],
  [0.54, 0.72], // toj eng keng
  [0.52, 0.95],
  [0.44, 1.12], // toj yelkasi
  [0.3, 1.25],
  [0.14, 1.32], // gumbaz
  [0.0, 1.34],
];

function Tooth() {
  const group = useRef<THREE.Group>(null);
  const geometry = useMemo(() => {
    const g = new THREE.LatheGeometry(
      PROFILE.map(([x, y]) => new THREE.Vector2(x, y)),
      96,
    );
    g.computeVertexNormals();
    return g;
  }, []);

  useFrame((state, dt) => {
    const g = group.current;
    if (!g) return;
    g.rotation.y += dt * 0.35; // sekin aylanish
    // sichqonchaga yumshoq egilish
    g.rotation.x = THREE.MathUtils.lerp(g.rotation.x, -0.15 + state.pointer.y * 0.18, 0.05);
    g.rotation.z = THREE.MathUtils.lerp(g.rotation.z, state.pointer.x * 0.12, 0.05);
  });

  return (
    <group ref={group}>
      <mesh geometry={geometry} castShadow>
        <meshPhysicalMaterial
          color="#eef6f6"
          roughness={0.18}
          metalness={0}
          clearcoat={1}
          clearcoatRoughness={0.14}
          ior={1.5}
          sheen={0.5}
          sheenColor="#ffffff"
          envMapIntensity={0.6}
        />
      </mesh>
    </group>
  );
}

export function HeroTooth() {
  return (
    <div
      className="absolute inset-0 overflow-hidden rounded-2xl bg-gradient-to-br from-brand-600 via-brand to-brand-700"
      aria-hidden="true"
    >
      <Canvas
        camera={{ position: [0, 0, 4.2], fov: 42 }}
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
        onCreated={({ gl }) => {
          gl.domElement.addEventListener(
            "webglcontextlost",
            (e) => e.preventDefault(),
            false,
          );
        }}
      >
        <ambientLight intensity={0.7} />
        <directionalLight position={[3, 5, 4]} intensity={1.6} />
        <directionalLight position={[-4, 2, -3]} intensity={0.5} color="#0e7c86" />
        <pointLight position={[0, -3, 2]} intensity={0.4} color="#f2a65a" />
        <Tooth />
      </Canvas>
    </div>
  );
}
