import { useEffect, useRef, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { Loader } from 'lucide-react';

/* ─── Demo fallback — 37 domains = 4 complete hex rings (1+6+12+18) ─── */
/* Refined palette: low saturation (~25-35%), lightness ~65-75%, sophisticated muted tones */
const DEMO_DOMAINS: import('@akg/shared').Domain[] = [
  // Ring 0 (center)
  { id: 'ai-engineering', name: 'AI编程', icon: '', description: '', color: '#8B7EC8', is_active: true, stats: { total_concepts: 400, total_edges: 615, subdomains: 15 } },
  // Ring 1 (6)
  { id: 'game-engine', name: '游戏引擎', icon: '', description: '', color: '#7BB5A3', is_active: true, stats: { total_concepts: 300, total_edges: 319, subdomains: 15 } },
  { id: 'mathematics', name: '数学', icon: '', description: '', color: '#7FA4C9', is_active: true, stats: { total_concepts: 269, total_edges: 366, subdomains: 12 } },
  { id: 'game-design', name: '游戏设计', icon: '', description: '', color: '#D4A882', is_active: true, stats: { total_concepts: 250, total_edges: 274, subdomains: 12 } },
  { id: 'machine-learning', name: '机器学习', icon: '', description: '', color: '#9B93C4', is_active: true, stats: { total_concepts: 350, total_edges: 500, subdomains: 14 } },
  { id: 'data-science', name: '数据科学', icon: '', description: '', color: '#6DA89B', is_active: true, stats: { total_concepts: 220, total_edges: 250, subdomains: 10 } },
  { id: 'algorithms', name: '算法', icon: '', description: '', color: '#A89BC4', is_active: true, stats: { total_concepts: 280, total_edges: 300, subdomains: 12 } },
  // Ring 2 (12)
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
  // Ring 3 (18)
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
  // Ring 4 (24)
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

const NAME_MAP: Record<string, string> = { 'ai-engineering': 'AI编程' };

/* ─── Constants ─── */
const BG = '#f0f0ec';          // slightly brighter warm grey
const TRANSITION_MS = 900;
const DPR = typeof window !== 'undefined' ? Math.min(window.devicePixelRatio || 1, 2) : 1;

/* ─── Layout & Fisheye (Tight circular 3-ring lens, 150% scale) ─── */
const BASE_R = 48;             // base bubble radius at scale=1 (was 32, +50%)
const HEX_SPACING = 114;      // hex grid spacing (was 76, +50%)
const FISH_MAX = 2.4;         // scale at center (large!)
const FISH_MIN = 0.05;        // scale at outer edge (tiny dots, no text)
const FISH_POWER = 3.2;       // very steep curve: huge center → tiny edge
const FISH_PUSH = 0.9;        // push center bubbles apart more
const FISH_R_FACTOR = 0.58;   // fishR = min(W,H) * factor → 150% bigger circle
const INITIAL_PAN_Y = 25;     // shift grid down for header
const FRICTION = 0.93;
const VEL_THRESHOLD = 0.3;
const VEL_CAP = 35;

/* ─── Helpers ─── */
function completeness(c: number, e: number, s: number) { return c + e * 0.5 + s * 5; }

/* ─── Generate RECTANGULAR hex grid (offset coords) for seamless tiling ─── */
/* Returns positions centered at origin + exact tile dimensions (wrapW, wrapH) */
function buildRectHexGrid(count: number, spacing: number): {
  positions: { x: number; y: number }[];
  totalSlots: number;
  wrapW: number;
  wrapH: number;
} {
  // Find smallest cols×rows rectangle that holds ≥ count cells
  const rowH = spacing * 0.866;
  let cols = Math.ceil(Math.sqrt(count * 1.15)); // slightly wider than tall
  let rows = Math.ceil(count / cols);
  while (cols * rows < count) rows++;

  // Exact tile repeat period
  const wrapW = cols * spacing;
  const wrapH = rows * rowH;

  // Generate ALL grid positions, then sort by distance from center
  // Even rows flush; odd rows offset by spacing/2
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

  // Sort by distance from center so item[0] (most important) gets center position
  allPos.sort((a, b) => a.distSq - b.distSq);

  // Return ALL positions (cols×rows) to fill the entire tile — no holes
  // Caller maps index % count to get the domain data
  return {
    positions: allPos.map(p => ({ x: p.x, y: p.y })),
    totalSlots: cols * rows,
    wrapW,
    wrapH,
  };
}

/* ─── Parse color to RGB components ─── */
function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}

/* ─── Flat bubble — pure solid color, hover = scale up + lift ─── */
function drawBubble(
  ctx: CanvasRenderingContext2D,
  name: string, color: string, concepts: number, subs: number,
  cx: number, cy: number, r: number, alpha: number, hovered: boolean,
) {
  if (r < 3 || alpha < 0.02) return;

  // Hover: enlarge + saturate + brighten + stronger shadow for "float up" feel
  const hoverScale = hovered ? 1.22 : 1;
  const dr = r * hoverScale;
  const drawAlpha = hovered ? Math.min(1, alpha * 1.4) : alpha;

  ctx.save();
  ctx.globalAlpha = drawAlpha;

  // Drop shadow — larger on hover for lift effect
  if (dr > 16) {
    ctx.shadowColor = hovered ? 'rgba(0,0,0,0.22)' : 'rgba(0,0,0,0.06)';
    ctx.shadowBlur = hovered ? dr * 0.5 : dr * 0.15;
    ctx.shadowOffsetX = 0;
    ctx.shadowOffsetY = hovered ? dr * 0.15 : dr * 0.04;
  }

  // Solid flat fill — boost saturation + brightness on hover
  if (hovered) {
    const [cr, cg, cb] = hexToRgb(color);
    // Boost saturation: push each channel away from grey average, then brighten
    const avg = (cr + cg + cb) / 3;
    const satBoost = 1.5; // 50% more saturation
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

  // Reset shadow
  ctx.shadowColor = 'transparent';
  ctx.shadowBlur = 0;

  // Hover: soft white glow ring
  if (hovered) {
    ctx.globalAlpha = 0.35;
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.arc(cx, cy, dr + 3, 0, Math.PI * 2);
    ctx.stroke();
    ctx.globalAlpha = drawAlpha;
  }

  // Text — progressive disclosure based on radius
  // r < 16: no text (tiny dot)
  // 16 ≤ r < 28: no text (small colored ball)
  // 28 ≤ r < 40: name only
  // r ≥ 40: name + stats
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
  }
  ctx.restore();
}

/* ═════════════════════════════════════════════════════
   HomePage — Apple Watch Style 2D Honeycomb
   Flat bubbles · Fish-eye lens · Free 2D drag
   ═════════════════════════════════════════════════════ */
export function HomePage() {
  const nav = useNavigate();
  const { domains, loading, fetchDomains } = useDomainStore();
  const active = domains.filter(d => d.is_active !== false);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [trans, setTrans] = useState<{ id: string; cx: number; cy: number; color: string } | null>(null);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const alive = useRef(true);
  const navRef = useRef(nav); navRef.current = nav;

  useEffect(() => {
    fetchDomains().then(() => {
      if (useDomainStore.getState().domains.length === 0)
        useDomainStore.setState({ domains: DEMO_DOMAINS, loading: false, error: null });
    });
  }, [fetchDomains]);

  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; if (timerRef.current) clearTimeout(timerRef.current); };
  }, []);

  /* ─── Sorted domain list ─── */
  interface DomainItem {
    id: string; name: string; color: string;
    concepts: number; subs: number; comp: number;
  }
  const sorted = useMemo<DomainItem[]>(() => {
    if (!active.length) return [];
    const items = active.map(d => {
      const c = d.stats?.total_concepts ?? 0, e = d.stats?.total_edges ?? 0, s = d.stats?.subdomains ?? 0;
      return { id: d.id, name: NAME_MAP[d.id] || d.name, color: d.color, concepts: c, subs: s, comp: completeness(c, e, s) };
    });
    items.sort((a, b) => b.comp - a.comp);
    return items;
  }, [active]);

  const N = sorted.length;

  /* ─── Precompute rectangular hex grid for seamless tiling ─── */
  const gridData = useMemo(() => buildRectHexGrid(N, HEX_SPACING), [N]);
  const hexGrid = gridData.positions;
  const totalSlots = gridData.totalSlots;
  const wrapW = gridData.wrapW;
  const wrapH = gridData.wrapH;

  /* ─── Animation state (2D pan) ─── */
  const st = useRef({
    panX: 0, panY: INITIAL_PAN_Y,  // current pan offset (world coords, shifted for header)
    velX: 0, velY: 0,       // velocity px/frame
    dragging: false,
    dragStartX: 0, dragStartY: 0,
    dragStartPanX: 0, dragStartPanY: 0,
    lastX: 0, lastY: 0, lastT: 0,
    mx: -9999, my: -9999,   // mouse position for hover
  });

  /* ─── Canvas loop ─── */
  useEffect(() => {
    const cvs = canvasRef.current;
    if (!cvs || N === 0) return;
    const ctx = cvs.getContext('2d')!;
    let raf = 0, dead = false;
    const s = st.current;

    const resize = () => {
      const r = cvs.parentElement!.getBoundingClientRect();
      cvs.width = r.width * DPR;
      cvs.height = r.height * DPR;
      cvs.style.width = r.width + 'px';
      cvs.style.height = r.height + 'px';
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(cvs.parentElement!);

    /* ─── Pointer handlers (2D drag) ─── */
    const onDown = (e: PointerEvent) => {
      s.dragging = true;
      s.velX = 0; s.velY = 0;
      s.dragStartX = e.clientX;
      s.dragStartY = e.clientY;
      s.dragStartPanX = s.panX;
      s.dragStartPanY = s.panY;
      s.lastX = e.clientX; s.lastY = e.clientY;
      s.lastT = performance.now();
      cvs.setPointerCapture(e.pointerId);
    };

    const onMove = (e: PointerEvent) => {
      const rect = cvs.getBoundingClientRect();
      s.mx = e.clientX - rect.left;
      s.my = e.clientY - rect.top;
      if (!s.dragging) return;
      s.panX = s.dragStartPanX + (e.clientX - s.dragStartX);
      s.panY = s.dragStartPanY + (e.clientY - s.dragStartY);
      const now = performance.now();
      const dt = now - s.lastT;
      if (dt > 0) {
        s.velX = (e.clientX - s.lastX) / dt * 16;
        s.velY = (e.clientY - s.lastY) / dt * 16;
      }
      s.lastX = e.clientX; s.lastY = e.clientY;
      s.lastT = now;
    };

    const onUp = (e: PointerEvent) => {
      const wasDrag = Math.abs(e.clientX - s.dragStartX) > 6 || Math.abs(e.clientY - s.dragStartY) > 6;
      s.dragging = false;
      cvs.releasePointerCapture(e.pointerId);
      // Cap velocity
      const vLen = Math.sqrt(s.velX * s.velX + s.velY * s.velY);
      if (vLen > VEL_CAP) { const sc = VEL_CAP / vLen; s.velX *= sc; s.velY *= sc; }

      if (!wasDrag) {
        // Click: hit-test bubbles (nearest to front = largest first)
        const W = cvs.width / DPR, H = cvs.height / DPR;
        const centerX = W / 2, centerY = H / 2;
        const fishR = Math.min(W, H) * FISH_R_FACTOR;

        // Build screen positions + radii using same fisheye as render
        const hits: { idx: number; sx: number; sy: number; sr: number }[] = [];
        const _wW = wrapW, _wH = wrapH;
        for (let i = 0; i < totalSlots; i++) {
          const bx = hexGrid[i].x + s.panX;
          const by = hexGrid[i].y + s.panY;
          let bestDx = bx, bestDy = by;
          for (const ox of [-_wW, 0, _wW]) {
            for (const oy of [-_wH, 0, _wH]) {
              const cx = bx + ox, cy = by + oy;
              if (cx * cx + cy * cy < bestDx * bestDx + bestDy * bestDy) { bestDx = cx; bestDy = cy; }
            }
          }
          const ddx = bestDx, ddy = bestDy;
          const sd = Math.sqrt(ddx * ddx + ddy * ddy);
          const t = Math.max(0, 1 - sd / fishR);
          if (t <= 0) continue;
          const curve = Math.pow(t, FISH_POWER);
          const scale = FISH_MIN + (FISH_MAX - FISH_MIN) * curve;
          const push = 1 + curve * FISH_PUSH;
          const sx = centerX + ddx * push;
          const sy = centerY + ddy * push;
          const sr = BASE_R * scale;
          hits.push({ idx: i, sx, sy, sr });
        }
        hits.sort((a, b) => b.sr - a.sr); // biggest first

        for (const h of hits) {
          const dx = s.mx - h.sx, dy = s.my - h.sy;
          if (dx * dx + dy * dy <= h.sr * h.sr) {
            const d = sorted[h.idx % N];
            const rect = cvs.getBoundingClientRect();
            setTrans({ id: d.id, cx: rect.left + h.sx, cy: rect.top + h.sy, color: d.color });
            timerRef.current = setTimeout(() => { if (alive.current) navRef.current('/domain/' + d.id); }, TRANSITION_MS);
            return;
          }
        }
      }
    };

    const onLeave = () => { s.mx = -9999; s.my = -9999; };

    cvs.addEventListener('pointerdown', onDown);
    cvs.addEventListener('pointermove', onMove);
    cvs.addEventListener('pointerup', onUp);
    cvs.addEventListener('pointerleave', onLeave);

    /* ─── Frame ─── */
    const frame = () => {
      if (dead) return;
      const W = cvs.width / DPR, H = cvs.height / DPR;
      const centerX = W / 2, centerY = H / 2;

      /* ─── Fisheye radius: circular, based on shorter dimension ─── */
      const fishR = Math.min(W, H) * FISH_R_FACTOR;

      /* Inertia (no limits — infinite scroll) */
      if (!s.dragging) {
        if (Math.abs(s.velX) > VEL_THRESHOLD || Math.abs(s.velY) > VEL_THRESHOLD) {
          s.panX += s.velX;
          s.panY += s.velY;
          s.velX *= FRICTION;
          s.velY *= FRICTION;
        } else {
          s.velX = 0; s.velY = 0;
        }
      }

      /* Wrap pan into grid period for numerical stability */
      // wrapW, wrapH already available from gridData
      s.panX = ((s.panX % wrapW) + wrapW) % wrapW;
      s.panY = ((s.panY % wrapH) + wrapH) % wrapH;

      /* Clear */
      ctx.save();
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
      ctx.fillStyle = BG;
      ctx.fillRect(0, 0, W, H);

      /* Clip to perfect circle — enforces round shape on widescreen */
      ctx.save();
      ctx.beginPath();
      ctx.arc(centerX, centerY, fishR * 1.05, 0, Math.PI * 2);
      ctx.clip();

      /* Build draw list with SCREEN-CENTERED fisheye */
      interface DrawItem {
        idx: number; sx: number; sy: number; sr: number;
        alpha: number; screenDist: number;
      }
      const drawItems: DrawItem[] = [];

      // For each grid slot (totalSlots fills entire rect), find nearest tile copy
      for (let i = 0; i < totalSlots; i++) {
        const baseX = hexGrid[i].x + s.panX;
        const baseY = hexGrid[i].y + s.panY;

        // Pick the wrap offset that places this bubble nearest to (0,0) relative to center
        let bestDx = baseX, bestDy = baseY;
        // Try shifting by ±wrapW, ±wrapH, pick shortest distance
        for (const ox of [-wrapW, 0, wrapW]) {
          for (const oy of [-wrapH, 0, wrapH]) {
            const cx = baseX + ox, cy = baseY + oy;
            if (cx * cx + cy * cy < bestDx * bestDx + bestDy * bestDy) {
              bestDx = cx; bestDy = cy;
            }
          }
        }

        const screenDist = Math.sqrt(bestDx * bestDx + bestDy * bestDy);
        const t = Math.max(0, 1 - screenDist / fishR);
        if (t <= 0) continue;

        const curve = Math.pow(t, FISH_POWER);
        const scale = FISH_MIN + (FISH_MAX - FISH_MIN) * curve;
        const push = 1 + curve * FISH_PUSH;
        const sx = centerX + bestDx * push;
        const sy = centerY + bestDy * push;
        const sr = BASE_R * scale;
        // Alpha: steep falloff — center bright, edge nearly invisible
        const alpha = Math.pow(t, 3.0);

        if (sx + sr < -20 || sx - sr > W + 20 || sy + sr < -20 || sy - sr > H + 20) continue;
        if (alpha < 0.02) continue;

        drawItems.push({ idx: i, sx, sy, sr, alpha, screenDist });
      }

      // Sort: far (small) drawn first → center (big) on top
      drawItems.sort((a, b) => b.screenDist - a.screenDist);

      // Hover detect (from front = largest)
      let hovIdx = -1;
      for (let i = drawItems.length - 1; i >= 0; i--) {
        const d = drawItems[i];
        const dx = s.mx - d.sx, dy = s.my - d.sy;
        if (dx * dx + dy * dy <= d.sr * d.sr) { hovIdx = d.idx; break; }
      }
      cvs.style.cursor = s.dragging ? 'grabbing' : hovIdx >= 0 ? 'pointer' : 'grab';

      // Draw bubbles — map grid slot idx to domain data with % N
      for (const d of drawItems) {
        const dd = sorted[d.idx % N];
        drawBubble(ctx, dd.name, dd.color, dd.concepts, dd.subs, d.sx, d.sy, d.sr, d.alpha, d.idx === hovIdx);
      }

      /* End clip */
      ctx.restore();

      /* ─── Circular vignette: smooth fade inside the clipped circle ─── */
      const vigInner = fishR * 0.40;
      const vigOuter = fishR * 1.05;
      const vigGrad = ctx.createRadialGradient(centerX, centerY, vigInner, centerX, centerY, vigOuter);
      vigGrad.addColorStop(0, 'rgba(240,240,236,0)');
      vigGrad.addColorStop(0.25, 'rgba(240,240,236,0)');
      vigGrad.addColorStop(0.5, 'rgba(240,240,236,0.25)');
      vigGrad.addColorStop(0.7, 'rgba(240,240,236,0.65)');
      vigGrad.addColorStop(0.85, 'rgba(240,240,236,0.92)');
      vigGrad.addColorStop(1, BG);
      ctx.fillStyle = vigGrad;
      ctx.fillRect(0, 0, W, H);

      /* ─── Hover tooltip removed — info already shown on bubble ─── */

      ctx.restore();
      raf = requestAnimationFrame(frame);
    };
    raf = requestAnimationFrame(frame);

    return () => {
      dead = true; cancelAnimationFrame(raf); ro.disconnect();
      cvs.removeEventListener('pointerdown', onDown);
      cvs.removeEventListener('pointermove', onMove);
      cvs.removeEventListener('pointerup', onUp);
      cvs.removeEventListener('pointerleave', onLeave);
    };
  }, [sorted, N, hexGrid, totalSlots, wrapW, wrapH, gridData]);

  return (
    <div className="h-dvh w-full relative overflow-hidden" style={{ backgroundColor: BG }}>
      <canvas ref={canvasRef} className="absolute inset-0 w-full h-full" style={{ touchAction: 'none' }} />
      {/* Header */}
      <div className="absolute left-0 right-0 text-center pointer-events-none select-none" style={{ top: 32, zIndex: 10 }}>
        <h1 style={{ fontSize: 20, fontWeight: 600, color: '#1a1a1a', letterSpacing: '0.04em', marginBottom: 6, fontFamily: '-apple-system,"SF Pro Display","Helvetica Neue","PingFang SC",sans-serif', textShadow: '0 1px 12px rgba(240,240,236,0.95)' }}>
          选择你的知识领域
        </h1>
        <p style={{ fontSize: 12, color: '#999', letterSpacing: '0.06em', fontFamily: '-apple-system,"SF Pro Text","PingFang SC",sans-serif', textShadow: '0 1px 8px rgba(240,240,236,0.9)' }}>
          拖动浏览 · 点击进入 3D 知识图谱
        </p>
      </div>
      {loading && active.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center" style={{ zIndex: 20 }}>
          <Loader size={28} className="animate-spin" style={{ color: '#888' }} />
        </div>
      )}
      {trans && (
        <div className="fixed inset-0" style={{ zIndex: 50, pointerEvents: 'none' }}>
          <div style={{ position: 'absolute', left: trans.cx, top: trans.cy, width: 0, height: 0, borderRadius: '50%', backgroundColor: trans.color, transform: 'translate(-50%,-50%)', animation: 'orb-expand ' + TRANSITION_MS + 'ms cubic-bezier(0.4,0,0.2,1) forwards', opacity: 0.85 }} />
        </div>
      )}
      <style>{`@keyframes orb-expand { 0% { width:0;height:0;opacity:0.9 } 100% { width:300vmax;height:300vmax;opacity:0.4 } }`}</style>
    </div>
  );
}
