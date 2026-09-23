"use client";

import { useMemo, useRef, useState } from "react";
import { Canvas, useFrame, useThree, type ThreeEvent } from "@react-three/fiber";
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

type PointerKind = "mouse" | "touch";

function OneTooth({
  x,
  y,
  active,
  onOver,
  onOut,
  onClick,
}: {
  x: number;
  y: number;
  active: boolean;
  onOver: () => void;
  onOut: () => void;
  onClick: (kind: PointerKind) => void;
}) {
  const ref = useRef<THREE.Group>(null);
  const kind = useRef<PointerKind>("mouse");
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
  // Hover faqat sichqonchada: touch'da pointerover/out bosish atrofida "soxta" otiladi.
  const isMouse = (e: ThreeEvent<PointerEvent>) => e.nativeEvent.pointerType === "mouse";
  return (
    <group position={[x, y, 0]}>
      <group
        ref={ref}
        onPointerDown={(e) => {
          kind.current = isMouse(e) ? "mouse" : "touch";
        }}
        onPointerOver={(e) => {
          if (!isMouse(e)) return;
          e.stopPropagation();
          onOver();
          document.body.style.cursor = "pointer";
        }}
        onPointerOut={(e) => {
          if (!isMouse(e)) return;
          onOut();
          document.body.style.cursor = "";
        }}
        onClick={(e) => {
          e.stopPropagation();
          onClick(kind.current);
        }}
      >
        <mesh geometry={crown} material={mat} />
        <mesh geometry={root} material={mat} />
      </group>
    </group>
  );
}

/** Tor (telefon) kanvasda 7 ta tish bir qatorga sigʻmaydi → 4+3 ikki qator (har biri ≥ 44 px). */
const NARROW_ASPECT = 1.6;
const GAP_X = 1.15;
const GAP_Y = 1.7;

function useLayout(n: number) {
  const aspect = useThree((s) => s.size.width / s.size.height);
  return useMemo(() => {
    const cols = aspect < NARROW_ASPECT ? Math.min(4, n) : n;
    const rows = Math.ceil(n / cols);
    return Array.from({ length: n }, (_, i) => {
      const row = Math.floor(i / cols);
      const inRow = row === rows - 1 ? n - row * cols : cols;
      const col = i - row * cols;
      return {
        x: (col - (inRow - 1) / 2) * GAP_X,
        y: ((rows - 1) / 2 - row) * GAP_Y + (rows > 1 ? 0.25 : 0),
      };
    });
  }, [aspect, n]);
}

/** Tishlarni kanvas nisbatiga qarab joylaydi (useThree faqat Canvas ichida ishlaydi). */
function Teeth({
  items,
  active,
  onPick,
  onOver,
  onOut,
}: {
  items: ToothItem[];
  active: number | null;
  onPick: (i: number, kind: PointerKind) => void;
  onOver: (i: number) => void;
  onOut: (i: number) => void;
}) {
  const layout = useLayout(items.length);
  return items.map((it, i) => (
    <OneTooth
      key={it.slug + i}
      x={layout[i].x}
      y={layout[i].y}
      active={active === i}
      onOver={() => onOver(i)}
      onOut={() => onOut(i)}
      onClick={(kind) => onPick(i, kind)}
    />
  ));
}

/**
 * Sichqoncha: hover → nom, bosish → xizmat sahifasi (oldingidek).
 * Touch: 1-bosish → tish tanlanadi va nomi chiqadi, xuddi shu tishga 2-bosish → sahifa ochiladi;
 * boʻsh joyga bosish → tanlov bekor.
 */
export function ToothMap({
  items,
  onHover,
  onSelect,
}: {
  items: ToothItem[];
  onHover: (i: number | null, touch: boolean) => void;
  onSelect: (slug: string) => void;
}) {
  const [active, setActive] = useState<number | null>(null);
  return (
    <Canvas
      camera={{ position: [0, 0, 7], fov: 42 }}
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true }}
      onPointerMissed={() => {
        setActive(null);
        onHover(null, false);
      }}
    >
      <Env />
      <ambientLight intensity={0.5} />
      <directionalLight position={[3, 5, 4]} intensity={1.3} />
      <directionalLight position={[-4, 2, -2]} intensity={0.5} color="#7fd8de" />
      <Teeth
        items={items}
        active={active}
        onOver={(i) => {
          setActive(i);
          onHover(i, false);
        }}
        onOut={(i) => {
          setActive((cur) => (cur === i ? null : cur));
          onHover(null, false);
        }}
        onPick={(i, kind) => {
          if (kind === "mouse" || active === i) return onSelect(items[i].slug);
          setActive(i);
          onHover(i, true);
        }}
      />
    </Canvas>
  );
}
