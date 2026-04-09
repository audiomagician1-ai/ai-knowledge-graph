import { useEffect, useRef } from 'react';
import { createLogger } from '@/lib/utils/logger';
import * as THREE from 'three';
import type { GraphData, GraphNode } from '@akg/shared';
import type { ForceGraph3DInstance } from '3d-force-graph';
import type { NodeObject } from '3d-force-graph';
import {
  type GNode, type GLink, BG_COLOR, SPHERE_R,
  baseSize, nodeColor, makeLabelTexture, disposeLabelCache,
} from './graph-visual-utils';
import { useGraphEffects } from '@/lib/hooks/useGraphEffects';

const log = createLogger('KnowledgeGraph');

interface KnowledgeGraphProps {
  data: GraphData;
  onNodeClick: (node: GraphNode) => void;
  selectedNodeId?: string | null;
  activeSubdomain?: string | null;
  domainColor?: string;
  domainId?: string;
}

const DEFAULT_DOMAIN_COLOR = '#8b5cf6';
const DEFAULT_DOMAIN_ID = 'ai-engineering';

export function KnowledgeGraph({ data, onNodeClick, selectedNodeId, activeSubdomain, domainColor, domainId }: KnowledgeGraphProps) {
  const effectiveDomainColor = domainColor || DEFAULT_DOMAIN_COLOR;
  const effectiveDomainId = domainId || DEFAULT_DOMAIN_ID;
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<ForceGraph3DInstance | null>(null);
  const hoveredRef = useRef<GNode | null>(null);
  const prevMasteredRef = useRef<Set<string>>(new Set(data.nodes.filter(n => n.status === 'mastered').map(n => n.id)));
  const onNodeClickRef = useRef(onNodeClick);
  onNodeClickRef.current = onNodeClick;
  const dataRef = useRef(data);
  dataRef.current = data;
  const domainColorRef = useRef(effectiveDomainColor);
  domainColorRef.current = effectiveDomainColor;
  const domainIdRef = useRef(effectiveDomainId);
  domainIdRef.current = effectiveDomainId;

  const buildPayload = () => {
    const d = dataRef.current;
    const nodes: GNode[] = d.nodes.map((n) => ({
      id: n.id, label: n.label, domain_id: n.domain_id, subdomain_id: n.subdomain_id,
      difficulty: n.difficulty, status: n.status, is_milestone: n.is_milestone,
      is_recommended: n.is_recommended, estimated_minutes: n.estimated_minutes, content_type: n.content_type,
    }));
    const links: GLink[] = d.edges.map((e) => ({ source: e.source, target: e.target, relation_type: e.relation_type, strength: e.strength }));
    return { nodes, links };
  };

  /* ── Init graph ONCE ── */
  useEffect(() => {
    if (!containerRef.current || !dataRef.current.nodes.length) return;
    let destroyed = false;
    import('3d-force-graph').then(({ default: ForceGraph3D }) => {
      if (destroyed || !containerRef.current) return;
      const Graph = new ForceGraph3D(containerRef.current, { controlType: 'orbit' });
      Graph.backgroundColor(BG_COLOR).showNavInfo(false).graphData(buildPayload());
      const scene = Graph.scene();
      scene.fog = new THREE.FogExp2(0xe8e8e4, 0.0003);
      const domainThreeColor = new THREE.Color(domainColorRef.current);
      Graph.lights([
        new THREE.AmbientLight(0xffffff, 1.1),
        (() => { const l = new THREE.PointLight(0xffffff, 0.3, 1200); l.position.set(200, 300, 200); return l; })(),
        (() => { const l = new THREE.PointLight(domainThreeColor, 0.25, 1400); l.position.set(-300, -100, 300); return l; })(),
      ]);
      // @ts-ignore d3Force
      Graph.d3Force('radial', null);
      // @ts-ignore d3Force
      Graph.d3Force('charge')?.strength(-120);
      // @ts-ignore d3Force
      Graph.d3Force('link')?.distance((link: GLink) => link.relation_type === 'prerequisite' ? 80 : 110);
      Graph.onEngineTick(() => {
        const nodes = Graph.graphData().nodes as GNode[];
        nodes.forEach((n) => {
          if (n.x == null || n.y == null || n.z == null) return;
          const dist = Math.sqrt(n.x * n.x + n.y * n.y + n.z * n.z) || 1;
          const scale = SPHERE_R / dist, pull = 0.02;
          n.x! += (n.x! * scale - n.x!) * pull;
          n.y! += (n.y! * scale - n.y!) * pull;
          n.z! += (n.z! * scale - n.z!) * pull;
        });
      });
      Graph.nodeVal((n: object) => { const s = baseSize(n as GNode); return s * s; })
        .nodeColor((n: object) => nodeColor(n as GNode)).nodeOpacity(0.85).nodeResolution(12).nodeRelSize(3).nodeLabel('')
        .nodeThreeObjectExtend(true).nodeThreeObject((obj: object) => {
          const n = obj as GNode;
          const group = new THREE.Group(), color = nodeColor(n);
          const tex = makeLabelTexture(n.label, color, n.is_milestone);
          const spriteMat = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: n.is_milestone ? 1.0 : 0.9, depthWrite: false, sizeAttenuation: true });
          const labelSprite = new THREE.Sprite(spriteMat);
          const img = tex.image as { width: number; height: number };
          const aspect = img.width / img.height, labelH = n.is_milestone ? 8 : 6;
          labelSprite.scale.set(labelH * aspect, labelH, 1);
          labelSprite.position.set(0, -(baseSize(n) * 2.5 + 3), 0);
          group.add(labelSprite);
          return group;
        });
      Graph.linkWidth((l: object) => (l as GLink).relation_type === 'prerequisite' ? 1.2 : 0.6).linkOpacity(0.3)
        .linkColor((l: object) => (l as GLink).relation_type === 'prerequisite' ? '#94a3b8' : '#cbd5e1')
        .linkDirectionalParticles((l: object) => (l as GLink).relation_type === 'prerequisite' ? 2 : 0)
        .linkDirectionalParticleWidth(1.5).linkDirectionalParticleSpeed(0.004).linkDirectionalParticleColor(() => domainColorRef.current);
      Graph.onNodeClick((n: NodeObject) => {
        const node = n as GNode;
        const ctrl = Graph.controls() as { autoRotate?: boolean };
        if (ctrl) ctrl.autoRotate = false;
        Graph.cooldownTime(0);
        onNodeClickRef.current({ id: node.id, label: node.label, domain_id: node.domain_id || domainIdRef.current, subdomain_id: node.subdomain_id, difficulty: node.difficulty, status: node.status, is_milestone: node.is_milestone, is_recommended: node.is_recommended, estimated_minutes: node.estimated_minutes, content_type: node.content_type } as GraphNode);
        const dist = 140, nx = node.x || 0, ny = node.y || 0, nz = node.z || 0, len = Math.sqrt(nx * nx + ny * ny + nz * nz) || 1;
        Graph.cameraPosition({ x: nx + (nx / len) * dist, y: ny + (ny / len) * dist * 0.3, z: nz + (nz / len) * dist }, { x: nx, y: ny, z: nz }, 1200);
      });
      Graph.onNodeHover((n: NodeObject | null) => { hoveredRef.current = n as GNode | null; if (containerRef.current) containerRef.current.style.cursor = n ? 'pointer' : 'default'; });
      Graph.onBackgroundClick(() => {
        const ctrl = Graph.controls() as { autoRotate?: boolean; target?: { set: (x: number, y: number, z: number) => void } };
        if (ctrl) { ctrl.autoRotate = true; if (ctrl.target) ctrl.target.set(0, 0, 0); }
        onNodeClickRef.current(null as unknown as GraphNode);
      });
      const ctrl = Graph.controls() as { autoRotate?: boolean; autoRotateSpeed?: number; enableDamping?: boolean; dampingFactor?: number };
      if (ctrl) { ctrl.autoRotate = true; ctrl.autoRotateSpeed = 0.15; ctrl.enableDamping = true; ctrl.dampingFactor = 0.12; }
      Graph.cameraPosition({ x: 0, y: 100, z: 700 });
      const ro = new ResizeObserver((entries) => { for (const e of entries) { const { width, height } = e.contentRect; if (width && height) Graph.width(width).height(height); } });
      ro.observe(containerRef.current);
      graphRef.current = Graph;
      return () => { destroyed = true; ro.disconnect(); Graph._destructor(); graphRef.current = null; };
    });
    return () => { destroyed = true; if (graphRef.current) { graphRef.current._destructor(); graphRef.current = null; } disposeLabelCache(); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useGraphEffects(graphRef, data, selectedNodeId, activeSubdomain, prevMasteredRef);

  return <div ref={containerRef} className="w-full h-full graph-container" style={{ backgroundColor: BG_COLOR }} />;
}