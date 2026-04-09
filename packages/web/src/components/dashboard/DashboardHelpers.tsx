import type { Domain } from '@akg/shared';

/* ── StatCard ── */
interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: number;
  sub?: string;
  color: string;
}

export function StatCard({ icon, label, value, sub, color }: StatCardProps) {
  return (
    <div className="rounded-xl p-4 flex items-center gap-3" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="p-2 rounded-lg" style={{ backgroundColor: color + '20', color }}>{icon}</div>
      <div>
        <div className="text-2xl font-bold">{value}<span className="text-sm font-normal opacity-50 ml-1">{sub}</span></div>
        <div className="text-sm opacity-60">{label}</div>
      </div>
    </div>
  );
}

/* ── DomainCard ── */
export interface DomainStatEntry {
  domain: Domain;
  mastered: number;
  learning: number;
  total: number;
  pct: number;
  avgMastery: number;
  started: boolean;
}

export function DomainCard({ ds, onClick }: { ds: DomainStatEntry; onClick: () => void }) {
  const { domain, mastered, learning, total, pct } = ds;
  const hashSeed = domain.id.split('').reduce((a, ch) => a + ch.charCodeAt(0), 0);
  const learners = Math.max(12, Math.round(total * 0.6 + (hashSeed % 80) + 15));
  return (
    <button onClick={onClick} className="rounded-xl p-4 text-left hover:ring-1 transition-all w-full" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{domain.icon}</span>
        <span className="font-medium">{domain.name}</span>
        <span className="ml-auto text-sm font-bold" style={{ color: domain.color }}>{pct}%</span>
      </div>
      <div className="w-full h-2 rounded-full overflow-hidden mb-2" style={{ backgroundColor: 'var(--color-surface-0)' }}>
        <div className="h-full rounded-full transition-all duration-500" style={{ width: `${pct}%`, backgroundColor: domain.color, minWidth: pct > 0 ? '4px' : '0' }} />
      </div>
      <div className="flex gap-4 text-xs opacity-60">
        <span>✅ {mastered}</span>
        <span>📖 {learning}</span>
        <span>共 {total}</span>
        <span className="ml-auto">{learners} 人在学</span>
      </div>
    </button>
  );
}

/* ── WidgetSkeleton ── */
export function WidgetSkeleton() {
  return (
    <div className="rounded-xl p-5 animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="h-4 w-32 rounded bg-white/10 mb-4" />
      <div className="h-24 rounded bg-white/5" />
    </div>
  );
}