/**
 * DomainOverview — Galaxy overview showing all knowledge domains with per-domain progress.
 * Phase 7.6: Displays each domain's icon, name, concept count, and mastered/learning progress.
 */
import { useDomainStore } from '@/lib/store/domain';
import { peekDomainProgress } from '@/lib/store/learning';
import { Globe, Sparkles } from 'lucide-react';
import { DomainCard } from './DomainCard';

interface DomainOverviewProps {
  /** Compact mode for modal panels (less padding, smaller text) */
  compact?: boolean;
}

export function DomainOverview({ compact }: DomainOverviewProps) {
  const { domains, loading } = useDomainStore();

  // Separate active domains from coming-soon
  const activeDomains = domains.filter((d) => d.is_active !== false);
  const comingSoonDomains = domains.filter((d) => d.is_active === false);

  // Compute overall stats across all active domains
  const overallStats = activeDomains.reduce(
    (acc, d) => {
      const p = peekDomainProgress(d.id);
      acc.totalConcepts += d.stats?.total_concepts ?? d.concept_count ?? 0;
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
