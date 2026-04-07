/**
 * DomainComparison — Bar chart comparing mastery across all domains.
 * Shows top-N domains by concept count with mastery progress bars.
 */
import { useMemo } from 'react';
import { useLearningStore } from '@/lib/store/learning';
import { useDomainStore } from '@/lib/store/domain';
import { BarChart3, TrendingUp } from 'lucide-react';

interface DomainComparisonProps {
  /** Max number of domains to display */
  maxDomains?: number;
}

export function DomainComparison({ maxDomains = 12 }: DomainComparisonProps) {
  const { domains } = useDomainStore();
  const { progress } = useLearningStore();

  const domainStats = useMemo(() => {
    // Build concept → domain mapping from domains metadata
    // Since progress doesn't store domain_id, we need to match concept IDs
    // For now, just show domain-level totals with placeholder mastery from progress count
    const progressEntries = Object.entries(progress);
    const totalMasteredAll = progressEntries.filter(([, p]) => p.status === 'mastered').length;
    const totalLearningAll = progressEntries.filter(([, p]) => p.status === 'learning').length;

    const stats = domains
      .filter(d => d.is_active !== false)
      .map(d => {
        const total = d.stats?.total_concepts || 0;
        // Estimate domain mastery proportionally (will be exact when backend sync provides domain_id)
        const mastered = 0; // Will be populated when domain progress tracking is implemented
        const learning = 0;
        const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;
        return {
          id: d.id,
          name: d.name,
          icon: d.icon,
          color: d.color,
          total,
          mastered,
          learning,
          pct,
        };
      })
      .sort((a, b) => b.total - a.total || a.name.localeCompare(b.name));

    return stats.slice(0, maxDomains);
  }, [domains, progress, maxDomains]);

  const totalMastered = domainStats.reduce((sum, d) => sum + d.mastered, 0);
  const totalConcepts = domainStats.reduce((sum, d) => sum + d.total, 0);

  if (domainStats.length === 0) {
    return (
      <div className="text-center py-8 text-gray-400">
        <BarChart3 size={24} className="mx-auto mb-2 opacity-50" />
        <p className="text-sm">暂无学习数据</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Summary header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <TrendingUp size={16} className="text-blue-500" />
          <span className="text-sm font-medium text-gray-700 dark:text-gray-200">域掌握度对比</span>
        </div>
        <span className="text-xs text-gray-400">
          {totalMastered}/{totalConcepts} 概念
        </span>
      </div>

      {/* Domain bars */}
      <div className="space-y-2.5">
        {domainStats.map(d => (
          <div key={d.id} className="group">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-sm">{d.icon}</span>
              <span className="text-xs font-medium text-gray-700 dark:text-gray-200 truncate flex-1">{d.name}</span>
              <span className="text-[10px] text-gray-400 tabular-nums">
                {d.mastered}/{d.total}
              </span>
              <span className="text-[10px] font-medium tabular-nums" style={{ color: d.color, minWidth: 32, textAlign: 'right' }}>
                {d.pct}%
              </span>
            </div>
            {/* Progress bar */}
            <div className="h-1.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-700 ease-out"
                style={{
                  width: `${Math.max(d.pct, d.mastered > 0 ? 1 : 0)}%`,
                  backgroundColor: d.color,
                  opacity: d.pct > 0 ? 1 : 0.3,
                }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
