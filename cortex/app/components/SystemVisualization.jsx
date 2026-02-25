// 3D vizualizace stavu systému LONGIN EGO
// Využívá React Three Fiber pro vykreslování 3D scény

import React, { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Html, Sphere, Line, Box } from '@react-three/drei';
import * as THREE from 'three';

// Komponenta reprezentující uzel systému (Modul, Sentinel, Connector, Adapter)
const SystemNode = ({ position, type, name, status, metrics, onClick }) => {
  const mesh = useRef();
  const [hovered, setHover] = useState(false);
  
  // Barva podle typu a statusu
  const color = useMemo(() => {
    if (status === 'error') return '#ff4444';
    if (status === 'warning') return '#ffbb33';
    
    switch(type) {
      case 'module': return '#33b5e5';
      case 'sentinel': return '#00C851';
      case 'connector': return '#aa66cc';
      case 'adapter': return '#ff8800';
      default: return '#cccccc';
    }
  }, [type, status]);
  
  // Animace pulsace pro aktivní uzly
  useFrame((state) => {
    if (status === 'active' || status === 'warning' || status === 'error') {
      const t = state.clock.getElapsedTime();
      mesh.current.scale.x = 1 + Math.sin(t * 2) * 0.1;
      mesh.current.scale.y = 1 + Math.sin(t * 2) * 0.1;
      mesh.current.scale.z = 1 + Math.sin(t * 2) * 0.1;
    }
  });

  return (
    <group position={position}>
      <mesh
        ref={mesh}
        onClick={(e) => { e.stopPropagation(); onClick(); }}
        onPointerOver={() => setHover(true)}
        onPointerOut={() => setHover(false)}
      >
        {type === 'module' ? (
          <boxGeometry args={[1, 1, 1]} />
        ) : type === 'sentinel' ? (
          <sphereGeometry args={[0.6, 32, 32]} />
        ) : (
          <octahedronGeometry args={[0.5]} />
        )}
        <meshStandardMaterial color={hovered ? '#ffffff' : color} transparent opacity={0.8} />
      </mesh>
      
      {/* Label */}
      <Html position={[0, 1.2, 0]} center distanceFactor={10}>
        <div style={{ 
          background: 'rgba(0,0,0,0.8)', 
          color: 'white', 
          padding: '4px 8px', 
          borderRadius: '4px',
          fontSize: '12px',
          whiteSpace: 'nowrap',
          pointerEvents: 'none',
          border: `1px solid ${color}`
        }}>
          {name}
          {metrics && <div style={{ fontSize: '10px', color: '#aaa' }}>{metrics}</div>}
        </div>
      </Html>
    </group>
  );
};

// Komponenta pro spojení mezi uzly
const Connection = ({ start, end, active }) => {
  const points = useMemo(() => [start, end], [start, end]);
  const ref = useRef();
  
  useFrame((state) => {
    if (active && ref.current) {
      ref.current.material.dashOffset -= 0.05;
    }
  });

  return (
    <Line
      ref={ref}
      points={points}
      color={active ? '#00ff00' : '#444444'}
      lineWidth={active ? 2 : 1}
      dashed={active}
      dashScale={active ? 20 : 1}
      dashSize={0.5}
      gapSize={0.5}
    />
  );
};

// Hlavní scéna
const SystemScene = ({ data }) => {
  // Rozmístění uzlů do kruhu/vrstev
  const nodes = useMemo(() => {
    const items = [];
    const radius = 5;
    
    // Core (Kernel)
    items.push({ 
      id: 'kernel', 
      type: 'module', 
      name: 'Kernel', 
      position: [0, 0, 0], 
      status: 'active',
      metrics: `CPU: ${data?.system?.cpu_percent}%` 
    });
    
    // Sentinels (Inner circle)
    const sentinelCount = data?.msca?.sentinel_count || 4;
    for (let i = 0; i < sentinelCount; i++) {
      const angle = (i / sentinelCount) * Math.PI * 2;
      items.push({
        id: `sentinel-${i}`,
        type: 'sentinel',
        name: `Sentinel ${i+1}`,
        position: [Math.cos(angle) * 3, 0, Math.sin(angle) * 3],
        status: 'active'
      });
    }
    
    // Modules (Outer circle)
    const moduleCount = data?.msca?.module_count || 6;
    for (let i = 0; i < moduleCount; i++) {
      const angle = (i / moduleCount) * Math.PI * 2 + 0.5;
      items.push({
        id: `module-${i}`,
        type: 'module',
        name: `Module ${i+1}`,
        position: [Math.cos(angle) * 6, Math.sin(i) * 2, Math.sin(angle) * 6],
        status: i % 3 === 0 ? 'warning' : 'active'
      });
    }
    
    return items;
  }, [data]);

  // Vytvoření spojení
  const connections = useMemo(() => {
    const conns = [];
    // Spojení Kernel -> Sentinels
    nodes.filter(n => n.type === 'sentinel').forEach(sentinel => {
      conns.push({
        start: [0, 0, 0],
        end: sentinel.position,
        active: true
      });
      
      // Spojení Sentinel -> Modules (náhodně pro demo)
      nodes.filter(n => n.type === 'module').forEach((module, idx) => {
        if (idx % 2 === 0) { // Zjednodušená logika
           conns.push({
            start: sentinel.position,
            end: module.position,
            active: Math.random() > 0.5
          });
        }
      });
    });
    return conns;
  }, [nodes]);

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      
      {/* Stars background */}
      <points>
        <sphereGeometry args={[50, 64, 64]} />
        <pointsMaterial color="#ffffff" size={0.1} transparent opacity={0.5} />
      </points>
      
      {/* Grid */}
      <gridHelper args={[20, 20, 0x444444, 0x222222]} position={[0, -5, 0]} />

      {/* Nodes */}
      {nodes.map((node) => (
        <SystemNode
          key={node.id}
          {...node}
          onClick={() => console.log('Clicked:', node.name)}
        />
      ))}

      {/* Connections */}
      {connections.map((conn, i) => (
        <Connection key={i} {...conn} />
      ))}

      <OrbitControls autoRotate autoRotateSpeed={0.5} />
    </>
  );
};

// Hlavní komponenta
export default function SystemVisualization({ data }) {
  return (
    <div style={{ width: '100%', height: '100%', minHeight: '500px', background: '#111' }}>
      <Canvas camera={{ position: [10, 10, 10], fov: 60 }}>
        <SystemScene data={data} />
      </Canvas>
    </div>
  );
}
