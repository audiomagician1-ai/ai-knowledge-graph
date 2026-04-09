const SIZE = 240;
const CENTER = SIZE / 2;
const RADIUS = 90;
const RINGS = 4;

export interface RadarPoint {
  label: string;
  value: number; // 0-100
  color: string;
  domainId: string;
}

const getXY = (i: number, r: number, n: number): [number, number] => {
  const angleStep = (2 * Math.PI) / n;
  const angle = -Math.PI / 2 + i * angleStep;
  return [CENTER + r * Math.cos(angle), CENTER + r * Math.sin(angle)];
};

export function RadarSVG({ points }: { points: RadarPoint[] }) {
  const n = points.length;
  const rings = Array.from({ length: RINGS }, (_, i) => {
    const r = (RADIUS / RINGS) * (i + 1);
    const pts = Array.from({ length: n }, (_, j) => getXY(j, r, n));
    return pts.map(([x, y]) => `${x},${y}`).join(' ');
  });
  const axes = Array.from({ length: n }, (_, i) => getXY(i, RADIUS, n));
  const dataPoints = points.map((p, i) => getXY(i, Math.max((p.value / 100) * RADIUS, 4), n));
  const dataPath = dataPoints.map(([x, y]) => `${x},${y}`).join(' ');

  return (
    <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`}>
      {rings.map((pts, i) => <polygon key={`ring-${i}`} points={pts} fill="none" stroke="var(--color-border)" strokeWidth={0.5} opacity={0.3 + i * 0.1} />)}
      {axes.map(([x, y], i) => <line key={`axis-${i}`} x1={CENTER} y1={CENTER} x2={x} y2={y} stroke="var(--color-border)" strokeWidth={0.5} opacity={0.4} />)}
      <polygon points={dataPath} fill="var(--color-accent)" fillOpacity={0.15} stroke="var(--color-accent)" strokeWidth={1.5} />
      {dataPoints.map(([x, y], i) => <circle key={`dot-${i}`} cx={x} cy={y} r={3} fill={points[i].color} stroke="var(--color-surface-0)" strokeWidth={1} />)}
      {points.map((p, i) => {
        const [x, y] = getXY(i, RADIUS + 18, n);
        const anchor = x < CENTER - 5 ? 'end' : x > CENTER + 5 ? 'start' : 'middle';
        return <text key={`label-${i}`} x={x} y={y} textAnchor={anchor} dominantBaseline="central" fill="currentColor" opacity={0.6} fontSize={9}>{p.label}</text>;
      })}
      {[25, 50, 75, 100].map((pct, i) => <text key={`pct-${i}`} x={CENTER + 2} y={CENTER - (pct / 100) * RADIUS - 1} fill="currentColor" opacity={0.25} fontSize={7}>{pct}%</text>)}
    </svg>
  );
}
