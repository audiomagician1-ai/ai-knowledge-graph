/**
 * home-canvas-utils.ts — Canvas rendering utilities for HomePage honeycomb grid.
 * Extracted from HomePage.tsx (V2.4 Code Health sprint).
 */
import type { Domain } from '@akg/shared';

/* ─── Demo fallback — 61 domains = hex ring layout ─── */
export const DEMO_DOMAINS: Domain[] = [
  { id: 'ai-engineering', name: 'AI编程', icon: '', description: '', color: '#8B7EC8', is_active: true, stats: { total_concepts: 400, total_edges: 615, subdomains: 15 } },
  { id: 'game-engine', name: '游戏引擎', icon: '', description: '', color: '#7BB5A3', is_active: true, stats: { total_concepts: 300, total_edges: 319, subdomains: 15 } },
  { id: 'mathematics', name: '数学', icon: '', description: '', color: '#7FA4C9', is_active: true, stats: { total_concepts: 269, total_edges: 366, subdomains: 12 } },
  { id: 'game-design', name: '游戏设计', icon: '', description: '', color: '#D4A882', is_active: true, stats: { total_concepts: 250, total_edges: 274, subdomains: 12 } },
  { id: 'machine-learning', name: '机器学习', icon: '', description: '', color: '#9B93C4', is_active: true, stats: { total_concepts: 350, total_edges: 500, subdomains: 14 } },
  { id: 'data-science', name: '数据科学', icon: '', description: '', color: '#6DA89B', is_active: true, stats: { total_concepts: 220, total_edges: 250, subdomains: 10 } },
  { id: 'algorithms', name: '算法', icon: '', description: '', color: '#A89BC4', is_active: true, stats: { total_concepts: 280, total_edges: 300, subdomains: 12 } },
  { id: 'english', name: '英语', icon: '', description: '', color: '#C9B87A', is_active: true, stats: { total_concepts: 200, total_edges: 229, subdomains: 10 } },
  { id: 'physics', name: '物理', icon: '', description: '', color: '#7AB5AD', is_active: true, stats: { total_concepts: 194, total_edges: 232, subdomains: 10 } },
  { id: 'psychology', name: '心理学', icon: '', description: '', color: '#B89DBF', is_active: true, stats: { total_concepts: 183, total_edges: 203, subdomains: 8 } },
  { id: 'economics', name: '经济学', icon: '', description: '', color: '#7DB5A0', is_active: true, stats: { total_concepts: 180, total_edges: 170, subdomains: 9 } },
  { id: 'graphics', name: '图形学', icon: '', description: '', color: '#8E9DC0', is_active: true, stats: { total_concepts: 200, total_edges: 190, subdomains: 10 } },
  { id: 'history', name: '历史', icon: '', description: '', color: '#C2AB8F', is_active: true, stats: { total_concepts: 170, total_edges: 160, subdomains: 9 } },
  { id: 'statistics', name: '统计学', icon: '', description: '', color: '#85B8C5', is_active: true, stats: { total_concepts: 170, total_edges: 160, subdomains: 8 } },
  { id: 'finance', name: '金融理财', icon: '', description: '', color: '#C4A3B5', is_active: true, stats: { total_concepts: 160, total_edges: 180, subdomains: 8 } },
  { id: 'qa-testing', name: 'QA测试', icon: '', description: '', color: '#7AAEC5', is_active: true, stats: { total_concepts: 160, total_edges: 150, subdomains: 8 } },
  { id: 'security', name: '信息安全', icon: '', description: '', color: '#C49A9A', is_active: true, stats: { total_concepts: 160, total_edges: 150, subdomains: 8 } },
  { id: 'biology', name: '生物学', icon: '', description: '', color: '#7DB89A', is_active: true, stats: { total_concepts: 155, total_edges: 145, subdomains: 7 } },
  { id: 'os', name: '操作系统', icon: '', description: '', color: '#8AAEBB', is_active: true, stats: { total_concepts: 150, total_edges: 140, subdomains: 7 } },
  { id: 'database', name: '数据库', icon: '', description: '', color: '#80BEC5', is_active: true, stats: { total_concepts: 145, total_edges: 135, subdomains: 7 } },
  { id: 'project-mgmt', name: '项目管理', icon: '', description: '', color: '#9AA5B3', is_active: true, stats: { total_concepts: 140, total_edges: 135, subdomains: 8 } },
  { id: 'chemistry', name: '化学', icon: '', description: '', color: '#72C0C5', is_active: true, stats: { total_concepts: 140, total_edges: 130, subdomains: 7 } },
  { id: 'law', name: '法学', icon: '', description: '', color: '#97A3AF', is_active: true, stats: { total_concepts: 135, total_edges: 125, subdomains: 7 } },
  { id: 'networking', name: '计算机网络', icon: '', description: '', color: '#7BBEA8', is_active: true, stats: { total_concepts: 130, total_edges: 120, subdomains: 6 } },
  { id: 'narrative', name: '叙事设计', icon: '', description: '', color: '#D0A0AF', is_active: true, stats: { total_concepts: 130, total_edges: 120, subdomains: 6 } },
  { id: 'literature', name: '文学', icon: '', description: '', color: '#B89CC0', is_active: true, stats: { total_concepts: 120, total_edges: 110, subdomains: 6 } },
  { id: 'robotics', name: '机器人学', icon: '', description: '', color: '#78B5A3', is_active: true, stats: { total_concepts: 115, total_edges: 105, subdomains: 6 } },
  { id: 'ux-design', name: 'UX设计', icon: '', description: '', color: '#CCA5A8', is_active: true, stats: { total_concepts: 110, total_edges: 100, subdomains: 6 } },
  { id: 'philosophy', name: '哲学', icon: '', description: '', color: '#9BA5B0', is_active: true, stats: { total_concepts: 110, total_edges: 100, subdomains: 5 } },
  { id: 'sociology', name: '社会学', icon: '', description: '', color: '#A299B2', is_active: true, stats: { total_concepts: 105, total_edges: 95, subdomains: 5 } },
  { id: 'art', name: '美术', icon: '', description: '', color: '#D0B090', is_active: true, stats: { total_concepts: 100, total_edges: 90, subdomains: 5 } },
  { id: 'education', name: '教育学', icon: '', description: '', color: '#95B5A0', is_active: true, stats: { total_concepts: 98, total_edges: 88, subdomains: 5 } },
  { id: 'linguistics', name: '语言学', icon: '', description: '', color: '#89B8A5', is_active: true, stats: { total_concepts: 95, total_edges: 85, subdomains: 5 } },
  { id: 'architecture', name: '建筑学', icon: '', description: '', color: '#C5AB9A', is_active: true, stats: { total_concepts: 92, total_edges: 82, subdomains: 4 } },
  { id: 'music', name: '音乐', icon: '', description: '', color: '#A895B5', is_active: true, stats: { total_concepts: 90, total_edges: 80, subdomains: 5 } },
  { id: 'astronomy', name: '天文学', icon: '', description: '', color: '#8A9AB5', is_active: true, stats: { total_concepts: 88, total_edges: 78, subdomains: 4 } },
  { id: 'geography', name: '地理学', icon: '', description: '', color: '#85B8AE', is_active: true, stats: { total_concepts: 85, total_edges: 75, subdomains: 4 } },
  { id: 'compiler', name: '编译原理', icon: '', description: '', color: '#8AA3B5', is_active: true, stats: { total_concepts: 82, total_edges: 72, subdomains: 4 } },
  { id: 'electronics', name: '电子工程', icon: '', description: '', color: '#7AB0B8', is_active: true, stats: { total_concepts: 80, total_edges: 70, subdomains: 4 } },
  { id: 'marketing', name: '市场营销', icon: '', description: '', color: '#C0A5BB', is_active: true, stats: { total_concepts: 78, total_edges: 68, subdomains: 4 } },
  { id: 'materials', name: '材料科学', icon: '', description: '', color: '#99B5A5', is_active: true, stats: { total_concepts: 76, total_edges: 66, subdomains: 4 } },
  { id: 'film', name: '电影学', icon: '', description: '', color: '#B5A0AA', is_active: true, stats: { total_concepts: 75, total_edges: 65, subdomains: 4 } },
  { id: 'nutrition', name: '营养学', icon: '', description: '', color: '#8DC0A0', is_active: true, stats: { total_concepts: 73, total_edges: 63, subdomains: 3 } },
  { id: 'journalism', name: '新闻学', icon: '', description: '', color: '#A5A0B8', is_active: true, stats: { total_concepts: 72, total_edges: 62, subdomains: 3 } },
  { id: 'anthropology', name: '人类学', icon: '', description: '', color: '#BBAA9E', is_active: true, stats: { total_concepts: 70, total_edges: 60, subdomains: 3 } },
  { id: 'env-science', name: '环境科学', icon: '', description: '', color: '#80B8AC', is_active: true, stats: { total_concepts: 68, total_edges: 58, subdomains: 3 } },
  { id: 'medicine', name: '医学', icon: '', description: '', color: '#CCA5A5', is_active: true, stats: { total_concepts: 150, total_edges: 140, subdomains: 8 } },
  { id: 'crypto', name: '密码学', icon: '', description: '', color: '#869DB5', is_active: true, stats: { total_concepts: 65, total_edges: 55, subdomains: 3 } },
  { id: 'aerospace', name: '航空航天', icon: '', description: '', color: '#7DA5C0', is_active: true, stats: { total_concepts: 63, total_edges: 53, subdomains: 3 } },
  { id: 'agriculture', name: '农业科学', icon: '', description: '', color: '#95BD90', is_active: true, stats: { total_concepts: 60, total_edges: 50, subdomains: 3 } },
  { id: 'theater', name: '戏剧', icon: '', description: '', color: '#BF9AAA', is_active: true, stats: { total_concepts: 58, total_edges: 48, subdomains: 3 } },
  { id: 'archaeology', name: '考古学', icon: '', description: '', color: '#B5AA98', is_active: true, stats: { total_concepts: 56, total_edges: 46, subdomains: 3 } },
  { id: 'political', name: '政治学', icon: '', description: '', color: '#9A9AB2', is_active: true, stats: { total_concepts: 55, total_edges: 45, subdomains: 3 } },
  { id: 'sports', name: '体育科学', icon: '', description: '', color: '#82B0C0', is_active: true, stats: { total_concepts: 53, total_edges: 43, subdomains: 3 } },
  { id: 'theology', name: '神学', icon: '', description: '', color: '#A5A0AC', is_active: true, stats: { total_concepts: 50, total_edges: 40, subdomains: 2 } },
  { id: 'veterinary', name: '兽医学', icon: '', description: '', color: '#88B5A5', is_active: true, stats: { total_concepts: 48, total_edges: 38, subdomains: 2 } },
  { id: 'dance', name: '舞蹈', icon: '', description: '', color: '#C5A3B2', is_active: true, stats: { total_concepts: 45, total_edges: 35, subdomains: 2 } },
  { id: 'oceanography', name: '海洋学', icon: '', description: '', color: '#78ABBD', is_active: true, stats: { total_concepts: 43, total_edges: 33, subdomains: 2 } },
  { id: 'library', name: '图书馆学', icon: '', description: '', color: '#9AA5B0', is_active: true, stats: { total_concepts: 40, total_edges: 30, subdomains: 2 } },
  { id: 'forestry', name: '林学', icon: '', description: '', color: '#88B59A', is_active: true, stats: { total_concepts: 38, total_edges: 28, subdomains: 2 } },
  { id: 'logistics', name: '物流学', icon: '', description: '', color: '#92A8BD', is_active: true, stats: { total_concepts: 36, total_edges: 26, subdomains: 2 } },
];

export const NAME_MAP: Record<string, string> = { 'ai-engineering': 'AI编程' };

/* ─── Canvas Constants ─── */
export const BG = '#f0f0ec';
export const TRANSITION_MS = 900;
export const DPR = typeof window !== 'undefined' ? Math.min(window.devicePixelRatio || 1, 2) : 1;
export const BASE_R = 48;
export const HEX_SPACING = 114;
export const FISH_MAX = 2.4;
export const FISH_MIN = 0.05;
export const FISH_POWER = 3.2;
export const FISH_PUSH = 0.9;
export const FISH_R_FACTOR = 0.58;
export const INITIAL_PAN_Y = 25;
export const FRICTION = 0.93;
export const VEL_THRESHOLD = 0.3;
export const VEL_CAP = 35;
export const TAP_THRESHOLD_DESKTOP = 6;
export const TAP_THRESHOLD_MOBILE = 20;
export const TAP_HIT_PADDING_MOBILE = 8;

export function completeness(c: number, e: number, s: number) { return c + e * 0.5 + s * 5; }

export interface DomainItem {
  id: string; name: string; color: string;
  concepts: number; subs: number; comp: number;
  learners: number;
}

/** Generate RECTANGULAR hex grid (offset coords) for seamless tiling */
export function buildRectHexGrid(count: number, spacing: number): {
  positions: { x: number; y: number }[];
  totalSlots: number;
  wrapW: number;
  wrapH: number;
} {
  const rowH = spacing * 0.866;
  let cols = Math.ceil(Math.sqrt(count * 1.15));
  let rows = Math.ceil(count / cols);
  while (cols * rows < count) rows++;
  const wrapW = cols * spacing;
  const wrapH = rows * rowH;
  const allPos: { x: number; y: number; distSq: number }[] = [];
  const cx = (cols - 1) * spacing / 2;
  const cy = (rows - 1) * rowH / 2;
  for (let row = 0; row < rows; row++) {
    for (let col = 0; col < cols; col++) {
      const xOff = (row % 2 === 1) ? spacing * 0.5 : 0;
      const x = col * spacing + xOff - cx;
      const y = row * rowH - cy;
      allPos.push({ x, y, distSq: x * x + y * y });
    }
  }
  allPos.sort((a, b) => a.distSq - b.distSq);
  return {
    positions: allPos.map(p => ({ x: p.x, y: p.y })),
    totalSlots: cols * rows,
    wrapW,
    wrapH,
  };
}

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

/** Flat bubble — pure solid color, hover = scale up + lift */
export function drawBubble(
  ctx: CanvasRenderingContext2D,
  name: string, color: string, concepts: number, subs: number,
  cx: number, cy: number, r: number, alpha: number, hovered: boolean,
  learners?: number,
) {
  if (r < 3 || alpha < 0.02) return;
  const hoverScale = hovered ? 1.22 : 1;
  const dr = r * hoverScale;
  const drawAlpha = hovered ? Math.min(1, alpha * 1.4) : alpha;

  ctx.save();
  ctx.globalAlpha = drawAlpha;

  if (dr > 16) {
    ctx.shadowColor = hovered ? 'rgba(0,0,0,0.22)' : 'rgba(0,0,0,0.06)';
    ctx.shadowBlur = hovered ? dr * 0.5 : dr * 0.15;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = hovered ? dr * 0.15 : dr * 0.04;
  }

  if (hovered) {
    const [cr, cg, cb] = hexToRgb(color);
    const avg = (cr + cg + cb) / 3;
    const satBoost = 1.5;
    const brighten = 25;
    const nr = Math.min(255, Math.round((cr - avg) * satBoost + avg) + brighten);
    const ng = Math.min(255, Math.round((cg - avg) * satBoost + avg) + brighten);
    const nb = Math.min(255, Math.round((cb - avg) * satBoost + avg) + brighten);
    ctx.fillStyle = `rgb(${nr},${ng},${nb})`;
  } else {
    ctx.fillStyle = color;
  }
  ctx.beginPath();
  ctx.arc(cx, cy, dr, 0, Math.PI * 2);
  ctx.fill();
  ctx.shadowColor = 'transparent';
  ctx.shadowBlur = 0;

  if (hovered) {
    ctx.globalAlpha = 0.35;
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(cx, cy, dr + 3, 0, Math.PI * 2);
    ctx.stroke();
    ctx.globalAlpha = drawAlpha;
  }

  if (dr < 28) { ctx.restore(); return; }
  ctx.globalAlpha = drawAlpha;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  const nameFontSize = Math.max(9, Math.round(dr * 0.30));
  ctx.font = `600 ${nameFontSize}px -apple-system,"SF Pro Display","Helvetica Neue","PingFang SC","Noto Sans SC",sans-serif`;
  ctx.fillStyle = 'rgba(255,255,255,0.95)';
  const showSub = dr >= 40;
  ctx.fillText(name, cx, showSub ? cy - nameFontSize * 0.35 : cy, dr * 1.6);
  if (showSub) {
    const subSize = Math.max(7, Math.round(dr * 0.18));
    const parts: string[] = [];
    if (concepts) parts.push(concepts + ' 知识点');
    if (subs) parts.push(subs + ' 子领域');
    if (parts.length) {
      ctx.font = `400 ${subSize}px -apple-system,"SF Pro Text","PingFang SC",sans-serif`;
      ctx.fillStyle = 'rgba(255,255,255,0.55)';
      ctx.fillText(parts.join(' · '), cx, cy + nameFontSize * 0.55, dr * 1.6);
    }
    if (learners && dr >= 52) {
      const lpSize = Math.max(6, Math.round(dr * 0.14));
      ctx.font = `400 ${lpSize}px -apple-system,"SF Pro Text","PingFang SC",sans-serif`;
      ctx.fillStyle = 'rgba(180,255,200,0.50)';
      ctx.fillText(learners + ' 人在学', cx, cy + nameFontSize * 0.55 + subSize + 4, dr * 1.6);
    }
  }
  ctx.restore();
}

