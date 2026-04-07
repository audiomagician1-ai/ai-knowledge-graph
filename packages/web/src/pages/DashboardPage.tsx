import { useEffect, useMemo, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLearningStore } from '@/lib/store/learning';
import { useDomainStore } from '@/lib/store/domain';
import { ArrowLeft, BarChart3, BookOpen, Trophy, TrendingUp, Flame, Clock, AlertTriangle, Zap } from 'lucide-react';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import { readLearningTime } from '@/lib/hooks/useLearningTimer';
import { StudyGoalWidget } from '@/components/common/StudyGoalWidget';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { DomainComparison } from '@/components/dashboard/DomainComparison';
import { RecentActivity } from '@/components/dashboard/RecentActivity';
import type { Domain } from '@akg/shared';

/**
 * Learning Analytics Dashboard (#46)
 * Shows domain progress cards, mastery distribution, and learning activity.
 */
export function DashboardPage() {
  const navigate = useNavigate();
  const domains = useDomainStore((s) => s.domains);
  const fetchDomains = useDomainStore((s) => s.fetchDomains);
  const switchDomain = useDomainStore((s) => s.switchDomain);
  const progress = useLearningStore((s) => s.progress);
  const history = useLearningStore((s) => s.history);
  const streak = useLearningStore((s) => s.streak);

  /* Keyboard shortcuts: Escape → home, H → home */
  useKeyboardShortcuts([
    { key: 'Escape', handler: () => navigate('/'), description: 'Back to home' },
    { key: 'h', handler: () => navigate('/'), description: 'Go to home' },
  ]);

  // Load all domain progress from localStorage
  const [allDomainProgress, setAllDomainProgress] = useState<
    Record<string, Record<string, { status: string; mastery_score: number }>>
  >({});

  useEffect(() => {
    fetchDomains();
  }, [fetchDomains]);

  // Load progress for all domains from localStorage
  useEffect(() => {
    const result: typeof allDomainProgress = {};
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
    // Also include current domain's progress from store
    const activeDomain = useDomainStore.getState().activeDomain;
    if (Object.keys(progress).length > 0) {
      result[activeDomain] = Object.fromEntries(
        Object.entries(progress).map(([id, p]) => [id, { status: p.status, mastery_score: p.mastery_score }])
      );
    }
    setAllDomainProgress(result);
  }, [domains, progress]);

  // Compute stats per domain
  const domainStats = useMemo(() => {
    return domains.map((d) => {
      const dp = allDomainProgress[d.id] || {};
      const entries = Object.values(dp);
      const mastered = entries.filter((e) => e.status === 'mastered').length;
      const learning = entries.filter((e) => e.status === 'learning').length;
      const total = d.stats?.total_concepts || 0;
      const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;
      const avgMastery = entries.length > 0
        ? Math.round(entries.reduce((s, e) => s + (e.mastery_score || 0), 0) / entries.length)
        : 0;
      return { domain: d, mastered, learning, total, pct, avgMastery, started: entries.length > 0 };
    });
  }, [domains, allDomainProgress]);

  // Global stats
  const globalStats = useMemo(() => {
    let totalMastered = 0;
    let totalLearning = 0;
    let totalConcepts = 0;
    for (const ds of domainStats) {
      totalMastered += ds.mastered;
      totalLearning += ds.learning;
      totalConcepts += ds.total;
    }
    const domainsStarted = domainStats.filter((d) => d.started).length;
    return { totalMastered, totalLearning, totalConcepts, domainsStarted };
  }, [domainStats]);

  // Mastery distribution (buckets: 0-20, 20-40, 40-60, 60-80, 80-100)
  const masteryDistribution = useMemo(() => {
    const buckets = [0, 0, 0, 0, 0];
    for (const dp of Object.values(allDomainProgress)) {
      for (const entry of Object.values(dp)) {
        if (entry.status !== 'not_started') {
          const score = entry.mastery_score || 0;
          const idx = Math.min(4, Math.floor(score / 20));
          buckets[idx]++;
        }
      }
    }
    return buckets;
  }, [allDomainProgress]);

  // Recent activity (last 7 days from history)
  const recentActivity = useMemo(() => {
    const days: Record<string, number> = {};
    const now = Date.now();
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now - i * 86400_000);
      const key = date.toISOString().slice(5, 10); // MM-DD
      days[key] = 0;
    }
    for (const h of history) {
      const date = new Date(h.timestamp || 0);
      const key = date.toISOString().slice(5, 10);
      if (key in days) {
        days[key]++;
      }
    }
    return Object.entries(days).map(([label, count]) => ({ label, count }));
  }, [history]);

  const maxActivity = Math.max(1, ...recentActivity.map((a) => a.count));

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      {/* Header */}
      <header className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <ArrowLeft size={20} />
        </button>
        <BarChart3 size={24} style={{ color: 'var(--color-accent)' }} />
        <h1 className="text-xl font-bold">学习分析</h1>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        {/* Global Stats Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon={<BookOpen size={20} />} label="已掌握" value={globalStats.totalMastered} sub={`/ ${globalStats.totalConcepts}`} color="#22c55e" />
          <StatCard icon={<TrendingUp size={20} />} label="学习中" value={globalStats.totalLearning} color="#3b82f6" />
          <StatCard icon={<Trophy size={20} />} label="已探索领域" value={globalStats.domainsStarted} sub={`/ ${domains.length}`} color="#f59e0b" />
          <StatCard icon={<Flame size={20} />} label="连续学习" value={streak.current} sub="天" color="#ef4444" />
        </div>

        {/* Learning Time Stats */}
        {(() => {
          const timeData = readLearningTime();
          const todayKey = (() => { const d = new Date(); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`; })();
          const todayMin = Math.round((timeData.daily[todayKey] || 0) / 60);
          const totalMin = Math.round(timeData.totalSeconds / 60);
          if (totalMin > 0) return (
            <div className="grid grid-cols-2 gap-4">
              <StatCard icon={<Clock size={20} />} label="今日学习" value={todayMin} sub="分钟" color="#8b5cf6" />
              <StatCard icon={<Clock size={20} />} label="累计学习" value={totalMin >= 60 ? Math.round(totalMin / 60) : totalMin} sub={totalMin >= 60 ? '小时' : '分钟'} color="#6366f1" />
            </div>
          );
          return null;
        })()}

        {/* Study Goal Widget */}
        <StudyGoalWidget />

        {/* Streak Calendar (30-day heatmap) */}
        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Flame size={18} style={{ color: '#ef4444' }} />
            学习日历
            {streak.current > 0 && (
              <span className="text-sm font-normal px-2 py-0.5 rounded-full" style={{ backgroundColor: '#ef444420', color: '#ef4444' }}>
                {streak.current} 天连续
              </span>
            )}
          </h2>
          <StreakCalendar history={history} />
        </section>

        {/* Mastery Distribution */}
        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <h2 className="text-lg font-semibold mb-4">掌握度分布</h2>
          <div className="flex items-end gap-2 h-32">
            {['0-20', '20-40', '40-60', '60-80', '80-100'].map((label, i) => {
              const count = masteryDistribution[i];
              const maxCount = Math.max(1, ...masteryDistribution);
              const height = (count / maxCount) * 100;
              const colors = ['#ef4444', '#f59e0b', '#eab308', '#22c55e', '#10b981'];
              return (
                <div key={label} className="flex-1 flex flex-col items-center gap-1">
                  <span className="text-xs opacity-60">{count}</span>
                  <div className="w-full rounded-t" style={{ height: `${Math.max(4, height)}%`, backgroundColor: colors[i], transition: 'height 0.3s' }} />
                  <span className="text-xs opacity-50">{label}</span>
                </div>
              );
            })}
          </div>
        </section>

        {/* Activity Chart (Last 7 Days) */}
        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <h2 className="text-lg font-semibold mb-4">最近7天学习活动</h2>
          <div className="flex items-end gap-3 h-24">
            {recentActivity.map((day) => {
              const height = (day.count / maxActivity) * 100;
              return (
                <div key={day.label} className="flex-1 flex flex-col items-center gap-1">
                  <span className="text-xs opacity-60">{day.count || ''}</span>
                  <div className="w-full rounded-t" style={{ height: `${Math.max(2, height)}%`, backgroundColor: 'var(--color-accent)', opacity: day.count > 0 ? 1 : 0.2, transition: 'height 0.3s' }} />
                  <span className="text-xs opacity-50">{day.label}</span>
                </div>
              );
            })}
          </div>
        </section>

        {/* Domain Progress Cards */}
        <section>
          <h2 className="text-lg font-semibold mb-4">领域进度</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {domainStats
              .sort((a, b) => b.pct - a.pct || (b.started ? 1 : 0) - (a.started ? 1 : 0))
              .map((ds) => (
                <DomainCard key={ds.domain.id} ds={ds} onClick={() => { switchDomain(ds.domain.id); navigate(`/domain/${ds.domain.id}`); }} />
              ))}
          </div>
        </section>

        {/* Learning Velocity (from Analytics API) */}
        <VelocitySection />

        {/* Domain Comparison (V2.1) */}
        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <DomainComparison maxDomains={12} />
        </section>

        {/* Recent Activity (V2.1) */}
        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <h2 className="text-base font-semibold mb-3 flex items-center gap-2">
            <Clock size={16} className="text-blue-500" />
            最近学习
          </h2>
          <RecentActivity maxItems={8} />
        </section>
      </div>
    </div>
  );
}

function StatCard({ icon, label, value, sub, color }: { icon: React.ReactNode; label: string; value: number; sub?: string; color: string }) {
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

interface DomainStatEntry {
  domain: Domain;
  mastered: number;
  learning: number;
  total: number;
  pct: number;
  avgMastery: number;
  started: boolean;
}

function DomainCard({ ds, onClick }: { ds: DomainStatEntry; onClick: () => void }) {
  const { domain, mastered, learning, total, pct } = ds;
  // Social proof: deterministic learner count
  const hashSeed = domain.id.split('').reduce((a, ch) => a + ch.charCodeAt(0), 0);
  const learners = Math.max(12, Math.round(total * 0.6 + (hashSeed % 80) + 15));
  return (
    <button onClick={onClick} className="rounded-xl p-4 text-left hover:ring-1 transition-all w-full" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{domain.icon}</span>
        <span className="font-medium">{domain.name}</span>
        <span className="ml-auto text-sm font-bold" style={{ color: domain.color }}>{pct}%</span>
      </div>
      {/* Progress bar */}
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

/** 30-day streak heatmap calendar */
function StreakCalendar({ history }: { history: Array<{ timestamp: number }> }) {
  const days = useMemo(() => {
    const result: { date: string; count: number; label: string }[] = [];
    const now = Date.now();
    const dayCounts = new Map<string, number>();

    for (const h of history) {
      const d = new Date(h.timestamp || 0);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      dayCounts.set(key, (dayCounts.get(key) || 0) + 1);
    }

    for (let i = 29; i >= 0; i--) {
      const date = new Date(now - i * 86400_000);
      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      const weekDay = ['日', '一', '二', '三', '四', '五', '六'][date.getDay()];
      const label = `${date.getMonth() + 1}/${date.getDate()} ${weekDay}`;
      result.push({ date: key, count: dayCounts.get(key) || 0, label });
    }
    return result;
  }, [history]);

  const maxCount = Math.max(1, ...days.map((d) => d.count));

  return (
    <div className="flex flex-wrap gap-1.5">
      {days.map((day) => {
        const intensity = day.count === 0 ? 0 : Math.max(0.2, day.count / maxCount);
        return (
          <div
            key={day.date}
            title={`${day.label}: ${day.count} 次学习`}
            className="rounded-sm transition-colors"
            style={{
              width: 18,
              height: 18,
              backgroundColor: day.count === 0
                ? 'var(--color-surface-3)'
                : `rgba(34, 197, 94, ${intensity})`,
              border: '1px solid var(--color-surface-4)',
            }}
          />
        );
      })}
      <div className="w-full flex items-center justify-between mt-1">
        <span className="text-xs opacity-40">30天前</span>
        <div className="flex items-center gap-1">
          <span className="text-xs opacity-40">少</span>
          {[0, 0.2, 0.5, 0.8, 1].map((v, i) => (
            <div
              key={i}
              className="rounded-sm"
              style={{
                width: 10,
                height: 10,
                backgroundColor: v === 0 ? 'var(--color-surface-3)' : `rgba(34, 197, 94, ${v})`,
              }}
            />
          ))}
          <span className="text-xs opacity-40">多</span>
        </div>
        <span className="text-xs opacity-40">今天</span>
      </div>
    </div>
  );
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

/** Learning Velocity section — fetches from Analytics API */
function VelocitySection() {
  const [velocity, setVelocity] = useState<{
    days: number;
    daily: Array<{ date: string; assessments: number; concepts_started: number; mastered: number }>;
    summary: { total_assessments: number; total_concepts_started: number; active_days: number };
  } | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await fetchWithRetry(`${API_BASE}/analytics/learning-velocity?days=14`, { retries: 1 });
        if (res.ok && !cancelled) {
          setVelocity(await res.json());
        }
      } catch { /* offline — no velocity data */ }
    })();
    return () => { cancelled = true; };
  }, []);

  if (!velocity || velocity.summary.total_assessments === 0) return null;

  const maxVal = Math.max(1, ...velocity.daily.map((d) => d.assessments + d.concepts_started));

  return (
    <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
        <Zap size={18} style={{ color: '#8b5cf6' }} />
        学习节奏 (14天)
      </h2>
      <div className="flex gap-3 text-xs opacity-60 mb-4">
        <span>活跃天数: {velocity.summary.active_days}</span>
        <span>·</span>
        <span>评估 {velocity.summary.total_assessments} 次</span>
        <span>·</span>
        <span>开始 {velocity.summary.total_concepts_started} 个概念</span>
      </div>
      <div className="flex items-end gap-1 h-20">
        {velocity.daily.map((day) => {
          const total = day.assessments + day.concepts_started;
          const height = (total / maxVal) * 100;
          const label = day.date.slice(5); // MM-DD
          return (
            <div key={day.date} className="flex-1 flex flex-col items-center gap-0.5">
              {total > 0 && <span className="text-[9px] opacity-40">{total}</span>}
              <div
                className="w-full rounded-t"
                title={`${day.date}: ${day.assessments} 评估, ${day.concepts_started} 开始`}
                style={{
                  height: `${Math.max(2, height)}%`,
                  backgroundColor: total > 0 ? '#8b5cf6' : 'var(--color-surface-3)',
                  opacity: total > 0 ? 0.8 : 0.3,
                  transition: 'height 0.3s',
                }}
              />
              <span className="text-[8px] opacity-30">{label}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}