"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

/** RoomEnvironment (bundled, tarmoqsiz) — emalga yaltiroq aks-ettirish beradi. */
function Environment() {
  const { gl, scene } = useThree();
  useMemo(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const env = pmrem.fromScene(new RoomEnvironment(), 0.04);
    scene.environment = env.texture;
    return () => {
      env.texture.dispose();
      pmrem.dispose();
    };
  }, [gl, scene]);
  return null;
}

/** Molar tish: yumaloq toj + 2 ta ildiz (bitta material bilan guruh). */
function Tooth() {
  const group = useRef<THREE.Group>(null);

  const material = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        color: new THREE.Color("#f3f7f7"),
        roughness: 0.28,
        metalness: 0,
        clearcoat: 1,
        clearcoatRoughness: 0.18,
        ior: 1.5,
        sheen: 0.4,
        sheenColor: new THREE.Color("#ffffff"),
        envMapIntensity: 1.1,
      }),
    [],
  );

  const crown = useMemo(() => {
    const g = new THREE.SphereGeometry(0.62, 64, 48);
    g.scale(1.12, 0.82, 1.0); // kengroq, pastroq — toj
    g.translate(0, 0.42, 0);
    // tepani biroz yassilaymiz (toj yuzasi)
    const pos = g.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      const y = pos.getY(i);
      if (y > 0.75) pos.setY(i, 0.75 + (y - 0.75) * 0.5);
    }
    g.computeVertexNormals();
    return g;
  }, []);

  const root = useMemo(() => {
    // Yo'g'on, biroz egilgan ildiz: silindr(tepa keng)→konus(pastki uch).
    const g = new THREE.CylinderGeometry(0.3, 0.11, 1.0, 32, 1, false);
    // pastki uchini yumaloqlash uchun vertexlarni biroz siqamiz
    g.translate(0, -0.42, 0);
    return g;
  }, []);

  useFrame((state, dt) => {
    const g = group.current;
    if (!g) return;
    g.rotation.y += dt * 0.3;
    g.rotation.x = THREE.MathUtils.lerp(g.rotation.x, -0.1 + state.pointer.y * 0.16, 0.05);
    g.rotation.z = THREE.MathUtils.lerp(g.rotation.z, state.pointer.x * 0.1, 0.05);
    g.position.y = Math.sin(state.clock.elapsedTime * 0.8) * 0.06; // yumshoq suzish
  });

  return (
    <group ref={group}>
      <mesh geometry={crown} material={material} />
      <mesh geometry={root} material={material} position={[-0.19, 0.15, 0.05]} rotation={[0, 0, 0.12]} />
      <mesh geometry={root} material={material} position={[0.19, 0.15, -0.05]} rotation={[0, 0, -0.12]} />
    </group>
  );
}

export function HeroTooth() {
  return (
    <div
      className="hero-scene-in absolute inset-0 overflow-hidden rounded-2xl bg-gradient-to-br from-brand-600 via-brand to-brand-700"
      aria-hidden="true"
    >
      <Canvas
        camera={{ position: [0, 0.1, 4.6], fov: 40 }}
        dpr={[1, 2]}
        gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
        onCreated={({ gl }) => {
          gl.domElement.addEventListener("webglcontextlost", (e) => e.preventDefault(), false);
        }}
      >
        <Environment />
        <ambientLight intensity={0.4} />
        <directionalLight position={[3, 5, 4]} intensity={1.4} />
        <directionalLight position={[-4, 1, -2]} intensity={0.6} color="#7fd8de" />
        <pointLight position={[0, -2, 3]} intensity={0.5} color="#f2a65a" />
        <Tooth />
      </Canvas>
    </div>
  );
}
