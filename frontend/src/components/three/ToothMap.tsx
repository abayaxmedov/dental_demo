"use client";

import { useMemo, useRef, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

export type ToothItem = { slug: string; title: string };

function Env() {
  const { gl, scene } = useThree();
  useMemo(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    return () => pmrem.dispose();
  }, [gl, scene]);
  return null;
}

function useToothGeometry() {
  return useMemo(() => {
    const crown = new THREE.SphereGeometry(0.42, 40, 28);
    crown.scale(1.05, 0.85, 1);
    crown.translate(0, 0.3, 0);
    const root = new THREE.CylinderGeometry(0.2, 0.08, 0.6, 24);
    root.translate(0, -0.2, 0);
    return { crown, root };
  }, []);
}

function OneTooth({
  x,
  active,
  onOver,
  onOut,
  onClick,
}: {
  x: number;
  active: boolean;
  onOver: () => void;
  onOut: () => void;
  onClick: () => void;
}) {
  const ref = useRef<THREE.Group>(null);
  const { crown, root } = useToothGeometry();
  const mat = useMemo(
    () =>
      new THREE.MeshPhysicalMaterial({
        color: new THREE.Color("#f3f7f7"),
        roughness: 0.3,
        clearcoat: 1,
        clearcoatRoughness: 0.2,
        envMapIntensity: 1,
      }),
    [],
  );
  useFrame(() => {
    const g = ref.current;
    if (!g) return;
    const target = active ? 1.18 : 1;
    g.scale.x = THREE.MathUtils.lerp(g.scale.x, target, 0.18);
    g.scale.y = g.scale.z = g.scale.x;
    g.position.y = THREE.MathUtils.lerp(g.position.y, active ? 0.16 : 0, 0.18);
    mat.color.lerp(new THREE.Color(active ? "#0e7c86" : "#f3f7f7"), 0.18);
  });
  return (
    <group
      ref={ref}
      position={[x, -Math.abs(x) * 0.06, 0]}
      onPointerOver={(e) => {
        e.stopPropagation();
        onOver();
        document.body.style.cursor = "pointer";
      }}
      onPointerOut={() => {
        onOut();
        document.body.style.cursor = "";
      }}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
    >
      <mesh geometry={crown} material={mat} />
      <mesh geometry={root} material={mat} />
    </group>
  );
}

export function ToothMap({
  items,
  onHover,
  onSelect,
}: {
  items: ToothItem[];
  onHover: (i: number | null) => void;
  onSelect: (slug: string) => void;
}) {
  const [active, setActive] = useState<number | null>(null);
  const n = items.length;
  const gap = 1.15;
  const start = -((n - 1) * gap) / 2;
  return (
    <Canvas camera={{ position: [0, 0, 7], fov: 42 }} dpr={[1, 2]} gl={{ antialias: true, alpha: true }}>
      <Env />
      <ambientLight intensity={0.5} />
      <directionalLight position={[3, 5, 4]} intensity={1.3} />
      <directionalLight position={[-4, 2, -2]} intensity={0.5} color="#7fd8de" />
      {items.map((it, i) => (
        <OneTooth
          key={it.slug + i}
          x={start + i * gap}
          active={active === i}
          onOver={() => {
            setActive(i);
            onHover(i);
          }}
          onOut={() => {
            setActive((cur) => (cur === i ? null : cur));
            onHover(null);
          }}
          onClick={() => onSelect(it.slug)}
        />
      ))}
    </Canvas>
  );
}
