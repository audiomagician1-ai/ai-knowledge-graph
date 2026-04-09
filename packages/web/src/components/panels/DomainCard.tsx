import { useDomainStore } from '@/lib/store/domain';
import { useGraphStore } from '@/lib/store/graph';
import { peekDomainProgress } from '@/lib/store/learning';
import type { Domain } from '@akg/shared';

/** Per-domain progress summary card */
export function DomainCard({ domain, compact }: { domain: Domain; compact?: boolean }) {
  const { activeDomain, switchDomain } = useDomainStore();
  const { loadGraphData } = useGraphStore();
  const isActive = domain.id === activeDomain;
  const conceptCount = domain.stats?.total_concepts ?? domain.concept_count ?? 0;
  const progress = peekDomainProgress(domain.id);
  const pct = conceptCount > 0 ? Math.round((progress.mastered / conceptCount) * 100) : 0;
  const isComingSoon = domain.is_active === false;

  return (
    <button
      onClick={() => { if (!isComingSoon) { switchDomain(domain.id); loadGraphData(domain.id); } }}
      disabled={isComingSoon}
      className="w-full text-left rounded-lg transition-all"
      style={{
        padding: compact ? '12px 14px' : '16px 18px',
        backgroundColor: isActive ? 'var(--color-surface-3)' : 'var(--color-surface-2)',
        border: isActive ? `1.5px solid ${domain.color}40` : '1px solid var(--color-border)',
        opacity: isComingSoon ? 0.5 : 1,
        cursor: isComingSoon ? 'not-allowed' : 'pointer',
      }}
      onMouseEnter={(e) => { if (!isActive && !isComingSoon) e.currentTarget.style.backgroundColor = 'var(--color-surface-3)'; }}
      onMouseLeave={(e) => { if (!isActive && !isComingSoon) e.currentTarget.style.backgroundColor = 'var(--color-surface-2)'; }}
    >
      <div className="flex items-center gap-3">
        <span className="flex items-center justify-center shrink-0 rounded-lg text-lg"
          style={{ width: compact ? 36 : 40, height: compact ? 36 : 40, backgroundColor: `${domain.color}15` }}
          role="img" aria-label={domain.name}>
          {domain.icon}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="font-semibold truncate" style={{ fontSize: compact ? 13 : 14, color: 'var(--color-text-primary)' }}>{domain.name}</span>
            {isActive && (
              <span className="text-xs px-1.5 py-0.5 rounded font-medium shrink-0"
                style={{ backgroundColor: `${domain.color}20`, color: domain.color }}>当前</span>
            )}
            {isComingSoon && (
              <span className="text-xs px-1.5 py-0.5 rounded shrink-0"
                style={{ backgroundColor: 'var(--color-surface-4)', color: 'var(--color-text-tertiary)' }}>即将推出</span>
            )}
          </div>
          <div className="flex items-center gap-3 mt-1">
            <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>{conceptCount} 概念</span>
            <span className="text-xs" style={{ color: 'var(--color-text-quaternary, var(--color-text-tertiary))' }}>
              {Math.max(12, Math.round(conceptCount * 0.6 + (domain.id.split('').reduce((a, ch) => a + ch.charCodeAt(0), 0) % 80) + 15))} 人在学
            </span>
            {progress.mastered > 0 && <span className="text-xs font-mono" style={{ color: 'var(--color-accent-emerald)' }}>{progress.mastered} 已掌握</span>}
            {progress.learning > 0 && <span className="text-xs font-mono" style={{ color: 'var(--color-accent-amber)' }}>{progress.learning} 学习中</span>}
          </div>
          {conceptCount > 0 && (
            <div className="mt-2 flex items-center gap-2">
              <div className="flex-1 rounded-full overflow-hidden" style={{ height: compact ? 4 : 5, backgroundColor: 'var(--color-surface-4)' }}>
                <div style={{ height: '100%', borderRadius: 999, transition: 'width 0.5s ease', width: `${pct}%`, backgroundColor: domain.color, minWidth: pct > 0 ? 3 : 0 }} />
              </div>
              <span className="text-xs font-mono shrink-0" style={{ color: 'var(--color-text-tertiary)', minWidth: 28, textAlign: 'right' }}>{pct}%</span>
            </div>
          )}
        </div>
      </div>
    </button>
  );
}
