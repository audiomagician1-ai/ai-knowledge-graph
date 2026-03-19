/**
 * DomainOverview — Galaxy overview showing all knowledge domains with per-domain progress.
 * Phase 7.6: Displays each domain's icon, name, concept count, and mastered/learning progress.
 */
import { useDomainStore } from '@/lib/store/domain';
import { useGraphStore } from '@/lib/store/graph';
import { peekDomainProgress } from '@/lib/store/learning';
import { Globe, Sparkles } from 'lucide-react';
import type { Domain } from '@akg/shared';

interface DomainOverviewProps {
  /** Compact mode for modal panels (less padding, smaller text) */
  compact?: boolean;
}

/** Per-domain progress summary card */
function DomainCard({ domain, compact }: { domain: Domain; compact?: boolean }) {
  const { activeDomain, switchDomain } = useDomainStore();
  const { loadGraphData } = useGraphStore();
  const isActive = domain.id === activeDomain;
  const conceptCount = domain.concept_count || 0;
  const progress = peekDomainProgress(domain.id);
  const pct = conceptCount > 0 ? Math.round((progress.mastered / conceptCount) * 100) : 0;
  const isComingSoon = !(domain as any).is_active;

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
        {/* Icon */}
        <span
          className="flex items-center justify-center shrink-0 rounded-lg text-lg"
          style={{
            width: compact ? 36 : 40,
            height: compact ? 36 : 40,
            backgroundColor: `${domain.color}15`,
          }}
          role="img"
          aria-label={domain.name}
        >
          {domain.icon}
        </span>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span
              className="font-semibold truncate"
              style={{ fontSize: compact ? 13 : 14, color: 'var(--color-text-primary)' }}
            >
              {domain.name}
            </span>
            {isActive && (
              <span
                className="text-xs px-1.5 py-0.5 rounded font-medium shrink-0"
                style={{ backgroundColor: `${domain.color}20`, color: domain.color }}
              >
                当前
              </span>
            )}
            {isComingSoon && (
              <span
                className="text-xs px-1.5 py-0.5 rounded shrink-0"
                style={{ backgroundColor: 'var(--color-surface-4)', color: 'var(--color-text-tertiary)' }}
              >
                即将推出
              </span>
            )}
          </div>

          {/* Stats row */}
          <div className="flex items-center gap-3 mt-1">
            <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
              {conceptCount} 概念
            </span>
            {progress.mastered > 0 && (
              <span className="text-xs font-mono" style={{ color: 'var(--color-accent-emerald)' }}>
                {progress.mastered} 已掌握
              </span>
            )}
            {progress.learning > 0 && (
              <span className="text-xs font-mono" style={{ color: 'var(--color-accent-amber)' }}>
                {progress.learning} 学习中
              </span>
            )}
          </div>

          {/* Progress bar */}
          {conceptCount > 0 && (
            <div className="mt-2 flex items-center gap-2">
              <div
                className="flex-1 rounded-full overflow-hidden"
                style={{ height: compact ? 4 : 5, backgroundColor: 'var(--color-surface-4)' }}
              >
                <div
                  style={{
                    height: '100%',
                    borderRadius: 999,
                    transition: 'width 0.5s ease',
                    width: `${pct}%`,
                    backgroundColor: domain.color,
                    minWidth: pct > 0 ? 3 : 0,
                  }}
                />
              </div>
              <span className="text-xs font-mono shrink-0" style={{ color: 'var(--color-text-tertiary)', minWidth: 28, textAlign: 'right' }}>
                {pct}%
              </span>
            </div>
          )}
        </div>
      </div>
    </button>
  );
}

export function DomainOverview({ compact }: DomainOverviewProps) {
  const { domains, loading } = useDomainStore();

  // Separate active domains from coming-soon
  const activeDomains = domains.filter((d) => (d as any).is_active !== false);
  const comingSoonDomains = domains.filter((d) => (d as any).is_active === false);

  // Compute overall stats across all active domains
  const overallStats = activeDomains.reduce(
    (acc, d) => {
      const p = peekDomainProgress(d.id);
      acc.totalConcepts += d.concept_count || 0;
      acc.mastered += p.mastered;
      acc.learning += p.learning;
      return acc;
    },
    { totalConcepts: 0, mastered: 0, learning: 0 },
  );
  const overallPct = overallStats.totalConcepts > 0
    ? Math.round((overallStats.mastered / overallStats.totalConcepts) * 100)
    : 0;

  if (loading && domains.length === 0) {
    return (
      <div style={{ padding: compact ? '12px 0' : '16px 0' }}>
        <div className="flex items-center gap-2" style={{ color: 'var(--color-text-tertiary)' }}>
          <Globe size={14} className="animate-pulse" />
          <span className="text-sm">加载知识星系...</span>
        </div>
      </div>
    );
  }

  if (domains.length === 0) return null;

  return (
    <div style={{ marginBottom: compact ? 16 : 20 }}>
      {/* Header */}
      <div className="flex items-center justify-between" style={{ marginBottom: compact ? 10 : 14 }}>
        <div className="flex items-center gap-2">
          <Sparkles size={compact ? 14 : 15} style={{ color: 'var(--color-accent-primary)' }} />
          <span style={{ fontSize: compact ? 13 : 14, fontWeight: 600, color: 'var(--color-text-primary)' }}>
            知识星系
          </span>
          <span
            className="font-mono text-xs px-1.5 py-0.5 rounded"
            style={{ backgroundColor: 'var(--color-surface-3)', color: 'var(--color-text-tertiary)' }}
          >
            {activeDomains.length} 球体
          </span>
        </div>
        {overallStats.totalConcepts > 0 && (
          <span className="text-xs font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
            总进度 {overallStats.mastered}/{overallStats.totalConcepts} ({overallPct}%)
          </span>
        )}
      </div>

      {/* Domain cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: compact ? 8 : 10 }}>
        {activeDomains.map((domain) => (
          <DomainCard key={domain.id} domain={domain} compact={compact} />
        ))}
        {comingSoonDomains.map((domain) => (
          <DomainCard key={domain.id} domain={domain} compact={compact} />
        ))}
      </div>

      {/* Coming soon hint when only 1 domain */}
      {activeDomains.length <= 1 && comingSoonDomains.length === 0 && (
        <div
          className="flex items-center gap-2 mt-3 rounded-lg"
          style={{
            padding: compact ? '10px 12px' : '12px 16px',
            backgroundColor: 'var(--color-surface-2)',
            border: '1px dashed var(--color-border)',
          }}
        >
          <Globe size={14} style={{ color: 'var(--color-text-tertiary)' }} />
          <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
            更多知识球体即将推出 — 数学、英语、物理...
          </span>
        </div>
      )}
    </div>
  );
}
