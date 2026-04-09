import { useEffect, useMemo, useState } from 'react';
import { useDomainStore } from '@/lib/store/domain';
import type { Domain } from '@akg/shared';
import type { DomainStatEntry } from '@/components/dashboard/DashboardHelpers';

type ProgressMap = Record<string, { status: string; mastery_score: number }>;

/**
 * Aggregates all-domain progress from localStorage + current store progress.
 * Returns domainStats, globalStats, masteryDistribution, and recentActivity.
 */
export function useDashboardProgress(
  domains: Domain[],
  progress: Record<string, { status: string; mastery_score: number }>,
  history: Array<{ timestamp: number }>,
) {
  const [allDomainProgress, setAllDomainProgress] = useState<Record<string, ProgressMap>>({});

  useEffect(() => {
    const result: Record<string, ProgressMap> = {};
    for (const d of domains) {
      try {
        const raw = localStorage.getItem(`akg-learning:${d.id}`);
        if (raw) { const parsed = JSON.parse(raw); result[d.id] = parsed?.progress || {}; }
      } catch { /* skip */ }
    }
    const activeDomain = useDomainStore.getState().activeDomain;
    if (Object.keys(progress).length > 0) {
      result[activeDomain] = Object.fromEntries(
        Object.entries(progress).map(([id, p]) => [id, { status: p.status, mastery_score: p.mastery_score }])
      );
    }
    setAllDomainProgress(result);
  }, [domains, progress]);

  const domainStats: DomainStatEntry[] = useMemo(() => {
    return domains.map((d) => {
      const dp = allDomainProgress[d.id] || {};
      const entries = Object.values(dp);
      const mastered = entries.filter((e) => e.status === 'mastered').length;
      const learning = entries.filter((e) => e.status === 'learning').length;
      const total = d.stats?.total_concepts || 0;
      const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;
      const avgMastery = entries.length > 0 ? Math.round(entries.reduce((s, e) => s + (e.mastery_score || 0), 0) / entries.length) : 0;
      return { domain: d, mastered, learning, total, pct, avgMastery, started: entries.length > 0 };
    });
  }, [domains, allDomainProgress]);

  const globalStats = useMemo(() => {
    let totalMastered = 0, totalLearning = 0, totalConcepts = 0;
    for (const ds of domainStats) { totalMastered += ds.mastered; totalLearning += ds.learning; totalConcepts += ds.total; }
    return { totalMastered, totalLearning, totalConcepts, domainsStarted: domainStats.filter((d) => d.started).length };
  }, [domainStats]);

  const masteryDistribution = useMemo(() => {
    const buckets = [0, 0, 0, 0, 0];
    for (const dp of Object.values(allDomainProgress)) {
      for (const entry of Object.values(dp)) {
        if (entry.status !== 'not_started') { const idx = Math.min(4, Math.floor((entry.mastery_score || 0) / 20)); buckets[idx]++; }
      }
    }
    return buckets;
  }, [allDomainProgress]);

  const recentActivity = useMemo(() => {
    const days: Record<string, number> = {};
    const now = Date.now();
    for (let i = 6; i >= 0; i--) { const date = new Date(now - i * 86400_000); days[date.toISOString().slice(5, 10)] = 0; }
    for (const h of history) { const key = new Date(h.timestamp || 0).toISOString().slice(5, 10); if (key in days) days[key]++; }
    return Object.entries(days).map(([label, count]) => ({ label, count }));
  }, [history]);

  return { domainStats, globalStats, masteryDistribution, recentActivity };
}