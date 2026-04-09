import * as THREE from 'three';
import type { NodeObject, LinkObject } from '3d-force-graph';
import { GRAPH_VISUAL } from '@akg/shared';

/* ── Extended node / link with our fields ── */
export interface GNode extends NodeObject {
  id: string;
  label: string;
  domain_id: string;
  subdomain_id: string;
  difficulty: number;
  status: string;
  is_milestone: boolean;
  is_recommended?: boolean;
  estimated_minutes?: number;
  content_type?: string;
  x?: number; y?: number; z?: number;
}

export interface GLink extends LinkObject<GNode> {
  relation_type: string;
  strength: number;
}

export const DIFFICULTY_COLORS = GRAPH_VISUAL.DIFFICULTY_COLORS;
export const BG_COLOR = '#e8e8e4';
export const SPHERE_R = 480;

/* ── Node size: small dots ── */
export function baseSize(n: GNode): number {
  const s = 0.6 + n.difficulty * 0.13;
  return n.is_milestone ? s * 1.5 : s;
}

export function nodeColor(n: GNode): string {
  if (n.status === 'mastered') return '#10b981';
  if (n.status === 'learning') return '#f59e0b';
  if (n.is_recommended) return '#06b6d4';
  return DIFFICULTY_COLORS[n.difficulty] || '#94a3b8';
}

/* ── Label texture cache ── */
const _labelCache = new Map<string, THREE.Texture>();

export function makeLabelTexture(text: string, color: string, isMilestone: boolean): THREE.Texture {
  const key = `${text}|${color}|${isMilestone}`;
  if (_labelCache.has(key)) return _labelCache.get(key)!;

  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d')!;
  const fontSize = isMilestone ? 72 : 56;
  const fontFamily = '"Microsoft YaHei", "PingFang SC", "Noto Sans SC", system-ui, sans-serif';
  ctx.font = `700 ${fontSize}px ${fontFamily}`;
  const metrics = ctx.measureText(text);
  const pad = 24;
  const w = Math.ceil(metrics.width) + pad * 2;
  const h = fontSize + pad;
  canvas.width = w;
  canvas.height = h;

  ctx.font = `700 ${fontSize}px ${fontFamily}`;
  ctx.textBaseline = 'middle';
  ctx.textAlign = 'center';

  ctx.strokeStyle = 'rgba(242, 241, 239, 0.9)';
  ctx.lineWidth = 5;
  ctx.lineJoin = 'round';
  ctx.strokeText(text, w / 2, h / 2);

  ctx.fillStyle = isMilestone ? '#b45309' : color;
  ctx.fillText(text, w / 2, h / 2);

  const tex = new THREE.CanvasTexture(canvas);
  tex.minFilter = THREE.LinearFilter;
  tex.magFilter = THREE.LinearFilter;
  _labelCache.set(key, tex);
  return tex;
}

/** Dispose all cached textures — call on unmount */
export function disposeLabelCache(): void {
  for (const tex of _labelCache.values()) tex.dispose();
  _labelCache.clear();
}

/* ── Celebration particles for mastered nodes ── */
export function spawnCelebration(scene: THREE.Scene, x: number, y: number, z: number): void {
  const PARTICLE_COUNT = 24;
  const colors = [0x10b981, 0xf59e0b, 0x06b6d4, 0x6366f1, 0xec4899];
  const particles: { mesh: THREE.Mesh; vx: number; vy: number; vz: number; life: number }[] = [];

  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const color = colors[i % colors.length];
    const geo = new THREE.SphereGeometry(0.6 + Math.random() * 0.8, 6, 6);
    const mat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 1 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(x, y, z);

    const speed = 1.5 + Math.random() * 3;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.random() * Math.PI;

    scene.add(mesh);
    particles.push({
      mesh,
      vx: speed * Math.sin(phi) * Math.cos(theta),
      vy: speed * Math.sin(phi) * Math.sin(theta),
      vz: speed * Math.cos(phi),
      life: 1.0,
    });
  }

  let frame = 0;
  const maxFrames = 60;
  const animate = () => {
    frame++;
    if (frame > maxFrames) {
      for (const p of particles) {
        scene.remove(p.mesh);
        p.mesh.geometry.dispose();
        (p.mesh.material as THREE.MeshBasicMaterial).dispose();
      }
      return;
    }
    for (const p of particles) {
      p.mesh.position.x += p.vx;
      p.mesh.position.y += p.vy;
      p.mesh.position.z += p.vz;
      p.life -= 1 / maxFrames;
      (p.mesh.material as THREE.MeshBasicMaterial).opacity = Math.max(0, p.life);
      p.vx *= 0.96; p.vy *= 0.96; p.vz *= 0.96;
    }
    requestAnimationFrame(animate);
  };
  requestAnimationFrame(animate);
}