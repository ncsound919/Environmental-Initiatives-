'use client';
import { useEffect, useMemo, useRef, useState } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

interface Refs {
  rotation: { current: number };
  dragging: { current: boolean };
  hover: { current: boolean };
  reduced: { current: boolean };
}

function Core({ color }: { color: string }) {
  const ref = useRef<THREE.Mesh>(null);
  useFrame((_, d) => {
    if (ref.current) ref.current.rotation.y += d * 0.6;
  });
  return (
    <mesh ref={ref}>
      <icosahedronGeometry args={[0.72, 1]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.35} wireframe />
    </mesh>
  );
}

function Scene({ sensors, actuators, color, refs }: { sensors: string[]; actuators: string[]; color: string } & { refs: Refs }) {
  const group = useRef<THREE.Group>(null);

  const nodes = useMemo<[number, number, number][]>(() => {
    const all = [...sensors, ...actuators];
    const n = all.length || 1;
    return all.map((_, i) => {
      const a = (i / n) * Math.PI * 2;
      const r = 2.2;
      return [Math.cos(a) * r, i % 2 === 0 ? 0.45 : -0.45, Math.sin(a) * r] as [number, number, number];
    });
  }, [sensors, actuators]);

  const isActuator = useMemo(
    () => [...sensors.map(() => false), ...actuators.map(() => true)],
    [sensors, actuators],
  );

  const lines = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    nodes.forEach((p) => {
      pts.push(new THREE.Vector3(0, 0, 0), new THREE.Vector3(p[0], p[1], p[2]));
    });
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.35 });
    return new THREE.LineSegments(geo, mat);
  }, [nodes, color]);

  const packets = useRef<(THREE.Mesh | null)[]>([]);
  useFrame(({ clock }, delta) => {
    const { rotation, dragging, hover, reduced } = refs;
    if (!dragging.current && !hover.current && !reduced.current) rotation.current += delta * 0.18;
    if (group.current) group.current.rotation.y = rotation.current;
    if (reduced.current) return;
    const t = (clock.elapsedTime * 0.5) % 1;
    nodes.forEach((p, i) => {
      const m = packets.current[i];
      if (m) m.position.set(p[0] * t, p[1] * t, p[2] * t);
    });
  });

  return (
    <group ref={group}>
      <gridHelper args={[12, 12, '#1e293b', '#0f172a']} position={[0, -1.7, 0]} />
      <Core color={color} />
      <primitive object={lines} />
      {nodes.map((p, i) => (
        <mesh key={i} position={p}>
          {isActuator[i] ? <boxGeometry args={[0.3, 0.3, 0.3]} /> : <sphereGeometry args={[0.18, 16, 16]} />}
          <meshStandardMaterial
            color={isActuator[i] ? '#f59e0b' : '#22d3ee'}
            emissive={isActuator[i] ? '#f59e0b' : '#22d3ee'}
            emissiveIntensity={0.4}
          />
        </mesh>
      ))}
      {nodes.map((_, i) => (
        <mesh
          key={`p${i}`}
          ref={(el) => {
            packets.current[i] = el;
          }}
          position={[0, 0, 0]}
        >
          <sphereGeometry args={[0.07, 8, 8]} />
          <meshBasicMaterial color={color} />
        </mesh>
      ))}
    </group>
  );
}

export default function InitiativeScene({
  sensors,
  actuators,
  color,
  label,
}: {
  sensors: string[];
  actuators: string[];
  color: string;
  label: string;
}) {
  const rotation = useRef(0);
  const dragging = useRef(false);
  const hover = useRef(false);
  const reduced = useRef(false);
  const lastX = useRef(0);
  const wrap = useRef<HTMLDivElement>(null);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    reduced.current = mq.matches;
    setReducedMotion(mq.matches);
    const onChange = () => {
      reduced.current = mq.matches;
      setReducedMotion(mq.matches);
    };
    mq.addEventListener('change', onChange);

    const el = wrap.current;
    const down = (e: PointerEvent) => {
      dragging.current = true;
      lastX.current = e.clientX;
      if (el) el.style.cursor = 'grabbing';
    };
    const up = () => {
      dragging.current = false;
      if (el) el.style.cursor = 'grab';
    };
    const move = (e: PointerEvent) => {
      if (dragging.current) {
        rotation.current += (e.clientX - lastX.current) * 0.01;
        lastX.current = e.clientX;
      }
    };
    el?.addEventListener('pointerdown', down);
    window.addEventListener('pointerup', up);
    el?.addEventListener('pointermove', move);
    return () => {
      mq.removeEventListener('change', onChange);
      el?.removeEventListener('pointerdown', down);
      window.removeEventListener('pointerup', up);
      el?.removeEventListener('pointermove', move);
    };
  }, []);

  return (
    <div>
      <div
        ref={wrap}
        role="img"
        aria-label={`Interactive 3D schematic of the ${label} device, its ${sensors.length} sensor(s) and ${actuators.length} actuator(s)`}
        onMouseEnter={() => {
          hover.current = true;
        }}
        onMouseLeave={() => {
          hover.current = false;
        }}
        style={{ width: '100%', height: 320, borderRadius: 10, overflow: 'hidden', background: 'rgba(2,6,23,0.5)', cursor: 'grab' }}
      >
        <Canvas camera={{ position: [0, 3, 6.2], fov: 45 }} dpr={[1, 2]} style={{ background: 'transparent' }}>
          <ambientLight intensity={0.75} />
          <pointLight position={[5, 5, 5]} intensity={1.3} />
          <pointLight position={[-5, -3, -5]} intensity={0.6} color={color} />
          <Scene sensors={sensors} actuators={actuators} color={color} refs={{ rotation, dragging, hover, reduced }} />
        </Canvas>
      </div>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
        <span><span style={{ display: 'inline-block', width: 10, height: 10, borderRadius: '50%', background: '#22d3ee', marginRight: 6 }} />Sensor</span>
        <span><span style={{ display: 'inline-block', width: 10, height: 10, background: '#f59e0b', marginRight: 6 }} />Actuator</span>
        <span style={{ color: 'var(--text-dim)' }}>drag to rotate · hover to pause{reducedMotion ? ' · reduced-motion on' : ''}</span>
      </div>
    </div>
  );
}
