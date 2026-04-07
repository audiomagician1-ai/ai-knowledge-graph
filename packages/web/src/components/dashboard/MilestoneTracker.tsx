/**
 * MilestoneTracker — Shows milestone concepts approaching/completed per domain.
 * Milestones are special concepts marked is_milestone=true in seed data.
 * Shows: next upcoming milestones + recently completed milestones.
 */
import { useMemo, useEffect, useState } from 'react';
import { useDomainStore } from '@/lib/store/domain';
import { useLearningStore } from '@/lib/store/learning';
import { Flag, CheckCircle, Target } from 'lucide-react';

interface MilestoneInfo {
  conceptId: string;
  name: string;
  domainName: string;
  domainColor: string;
  difficulty: number;
  completed: boolean;
}

export function MilestoneTracker() {
  const domains = useDomainStore((s) => s.domains);
  const progress = useLearningStore((s) => s.progress);
  const [allProgress, setAllProgress] = useState<Record<string, Record<string, { status: string }>>>({});

  useEffect(() => {
    const result: typeof allProgress = {};
    for (const d of domains) {
      try {
        const key = `akg-learning:${d.id}`;
        const raw = localStorage.getItem(key);
        if (raw) {
          const parsed = JSON.parse(raw);
          result[d.id] = parsed?.progress || {};
        }
      } catch { /* skip */ }
    }
    const activeDomain = useDomainStore.getState().activeDomain;
    if (Object.keys(progress).length > 0) {
      result[activeDomain] = Object.fromEntries(
        Object.entries(progress).map(([id, p]) => [id, { status: p.status }])
      );
    }
    setAllProgress(result);
  }, [domains, progress]);

  const milestones = useMemo((): MilestoneInfo[] => {
    // Milestones are tracked via domain stats — we'll simulate from domain metadata
    // In the future this can be powered by /api/graph/topology endpoint
    const results: MilestoneInfo[] = [];

    // Show milestone counts from progress — check mastered vs total concepts
    for (const d of domains) {
      const dp = allProgress[d.id] || {};
      const total = d.stats?.total_concepts || 0;
      if (total === 0) continue;

      const mastered = Object.values(dp).filter((p) => p.status === 'mastered').length;
      const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;

      // Milestone triggers at 25%, 50%, 75%, 100%
      const thresholds = [25, 50, 75, 100];
      for (const t of thresholds) {
        const needed = Math.ceil((t / 100) * total);
        results.push({
          conceptId: `${d.id}-${t}`,
          name: `${d.name} ${t}%`,
          domainName: d.name,
          domainColor: d.color || '#6366f1',
          difficulty: t / 10,
          completed: pct >= t,
        });
      }
    }

    // Sort: incomplete first (upcoming), then completed
    results.sort((a, b) => {
      if (a.completed !== b.completed) return a.completed ? 1 : -1;
      return a.difficulty - b.difficulty;
    });

    return results;
  }, [domains, allProgress]);

  const upcoming = milestones.filter((m) => !m.completed).slice(0, 5);
  const completed = milestones.filter((m) => m.completed).slice(0, 5);

  if (upcoming.length === 0 && completed.length === 0) {
    return (
      <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
        <h3 className="text-sm font-semibold flex items-center gap-2 mb-2">
          <Flag size={16} style={{ color: 'var(--color-accent)' }} />
          学习里程碑
        </h3>
        <p className="text-xs opacity-40 text-center py-4">开始学习后解锁里程碑追踪</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h3 className="text-sm font-semibold flex items-center gap-2 mb-3">
        <Flag size={16} style={{ color: 'var(--color-accent)' }} />
        学习里程碑
      </h3>

      {/* Upcoming milestones */}
      {upcoming.length > 0 && (
        <div className="mb-3">
          <p className="text-[10px] uppercase tracking-wider opacity-40 mb-2">即将达成</p>
          <div className="space-y-1.5">
            {upcoming.map((m) => (
              <div key={m.conceptId} className="flex items-center gap-2">
                <Target size={12} style={{ color: m.domainColor }} />
                <span className="text-xs flex-1 truncate">{m.name}</span>
                <span
                  className="text-[10px] px-1.5 py-0.5 rounded"
                  style={{ backgroundColor: m.domainColor + '22', color: m.domainColor }}
                >
                  {m.domainName.slice(0, 6)}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Completed milestones */}
      {completed.length > 0 && (
        <div>
          <p className="text-[10px] uppercase tracking-wider opacity-40 mb-2">已达成</p>
          <div className="space-y-1.5">
            {completed.map((m) => (
              <div key={m.conceptId} className="flex items-center gap-2 opacity-60">
                <CheckCircle size={12} style={{ color: '#22c55e' }} />
                <span className="text-xs flex-1 truncate line-through">{m.name}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
