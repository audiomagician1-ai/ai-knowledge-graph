import { useEffect, useMemo, lazy, Suspense } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLearningStore } from '@/lib/store/learning';
import { useDomainStore } from '@/lib/store/domain';
import { ArrowLeft, BarChart3, BookOpen, Trophy, TrendingUp, Flame, Clock } from 'lucide-react';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import { readLearningTime } from '@/lib/hooks/useLearningTimer';
import { StudyGoalWidget } from '@/components/common/StudyGoalWidget';
import { ShareProgress } from '@/components/common/ShareProgress';
import { StreakRewards } from '@/components/common/StreakRewards';
import { StatCard, DomainCard, WidgetSkeleton, type DomainStatEntry } from '@/components/dashboard/DashboardHelpers';
import { StreakCalendar } from '@/components/dashboard/StreakCalendar';
import { VelocitySection } from '@/components/dashboard/VelocitySection';
import { useDashboardProgress } from '@/lib/hooks/useDashboardProgress';

const DomainComparison = lazy(() => import('@/components/dashboard/DomainComparison').then(m => ({ default: m.DomainComparison })));
const RecentActivity = lazy(() => import('@/components/dashboard/RecentActivity').then(m => ({ default: m.RecentActivity })));
const WeeklyReport = lazy(() => import('@/components/dashboard/WeeklyReport').then(m => ({ default: m.WeeklyReport })));
const StudyPatterns = lazy(() => import('@/components/dashboard/StudyPatterns').then(m => ({ default: m.StudyPatterns })));
const DomainRadar = lazy(() => import('@/components/dashboard/DomainRadar').then(m => ({ default: m.DomainRadar })));
const DifficultyHeatmap = lazy(() => import('@/components/dashboard/DifficultyHeatmap').then(m => ({ default: m.DifficultyHeatmap })));
const MilestoneTracker = lazy(() => import('@/components/dashboard/MilestoneTracker').then(m => ({ default: m.MilestoneTracker })));
const ReviewQueue = lazy(() => import('@/components/dashboard/ReviewQueue').then(m => ({ default: m.ReviewQueue })));
const AdaptivePathWidget = lazy(() => import('@/components/dashboard/AdaptivePathWidget').then(m => ({ default: m.AdaptivePathWidget })));
const StudyTimeChart = lazy(() => import('@/components/dashboard/StudyTimeChart').then(m => ({ default: m.StudyTimeChart })));
const StreakInsights = lazy(() => import('@/components/dashboard/StreakInsights').then(m => ({ default: m.StreakInsights })));
const DomainRecommendWidget = lazy(() => import('@/components/dashboard/DomainRecommendWidget').then(m => ({ default: m.DomainRecommendWidget })));
const StudyPlanWidget = lazy(() => import('@/components/dashboard/StudyPlanWidget').then(m => ({ default: m.StudyPlanWidget })));
const WeakConceptsWidget = lazy(() => import('@/components/dashboard/WeakConceptsWidget').then(m => ({ default: m.WeakConceptsWidget })));
const LearningEfficiencyChart = lazy(() => import('@/components/dashboard/LearningEfficiencyChart').then(m => ({ default: m.LearningEfficiencyChart })));
const GlobalLeaderboard = lazy(() => import('@/components/dashboard/GlobalLeaderboard').then(m => ({ default: m.GlobalLeaderboard })));
const PeerComparisonCard = lazy(() => import('@/components/dashboard/PeerComparisonCard').then(m => ({ default: m.PeerComparisonCard })));

export function DashboardPage() {
  const navigate = useNavigate();
  const domains = useDomainStore((s) => s.domains);
  const fetchDomains = useDomainStore((s) => s.fetchDomains);
  const switchDomain = useDomainStore((s) => s.switchDomain);
  const progress = useLearningStore((s) => s.progress);
  const history = useLearningStore((s) => s.history);
  const streak = useLearningStore((s) => s.streak);

  useKeyboardShortcuts([
    { key: 'Escape', handler: () => navigate('/'), description: 'Back to home' },
    { key: 'h', handler: () => navigate('/'), description: 'Go to home' },
  ]);

  useEffect(() => { fetchDomains(); }, [fetchDomains]);

  const { domainStats, globalStats, masteryDistribution, recentActivity } = useDashboardProgress(domains, progress, history);
  const maxActivity = Math.max(1, ...recentActivity.map((a) => a.count));

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      <header className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors"><ArrowLeft size={20} /></button>
        <BarChart3 size={24} style={{ color: 'var(--color-accent)' }} />
        <h1 className="text-xl font-bold">学习分析</h1>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-6 space-y-6">
        {/* Global Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard icon={<BookOpen size={20} />} label="已掌握" value={globalStats.totalMastered} sub={`/ ${globalStats.totalConcepts}`} color="#22c55e" />
          <StatCard icon={<TrendingUp size={20} />} label="学习中" value={globalStats.totalLearning} color="#3b82f6" />
          <StatCard icon={<Trophy size={20} />} label="已探索领域" value={globalStats.domainsStarted} sub={`/ ${domains.length}`} color="#f59e0b" />
          <StatCard icon={<Flame size={20} />} label="连续学习" value={streak.current} sub="天" color="#ef4444" />
        </div>

        {/* Learning Time */}
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

        <StudyGoalWidget />
        <ShareProgress />

        {/* Streak Calendar */}
        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Flame size={18} style={{ color: '#ef4444' }} /> 学习日历
            {streak.current > 0 && <span className="text-sm font-normal px-2 py-0.5 rounded-full" style={{ backgroundColor: '#ef444420', color: '#ef4444' }}>{streak.current} 天连续</span>}
          </h2>
          <StreakCalendar history={history} />
          <div className="mt-4"><StreakRewards currentStreak={streak.current} longestStreak={streak.longest || streak.current} compact /></div>
        </section>

        {/* Mastery Distribution */}
        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <h2 className="text-lg font-semibold mb-4">掌握度分布</h2>
          <div className="flex items-end gap-2 h-32">
            {['0-20', '20-40', '40-60', '60-80', '80-100'].map((label, i) => {
              const count = masteryDistribution[i]; const maxCount = Math.max(1, ...masteryDistribution); const height = (count / maxCount) * 100;
              const colors = ['#ef4444', '#f59e0b', '#eab308', '#22c55e', '#10b981'];
              return (<div key={label} className="flex-1 flex flex-col items-center gap-1"><span className="text-xs opacity-60">{count}</span><div className="w-full rounded-t" style={{ height: `${Math.max(4, height)}%`, backgroundColor: colors[i], transition: 'height 0.3s' }} /><span className="text-xs opacity-50">{label}</span></div>);
            })}
          </div>
        </section>

        {/* Activity Chart */}
        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <h2 className="text-lg font-semibold mb-4">最近7天学习活动</h2>
          <div className="flex items-end gap-3 h-24">
            {recentActivity.map((day) => { const height = (day.count / maxActivity) * 100; return (
              <div key={day.label} className="flex-1 flex flex-col items-center gap-1"><span className="text-xs opacity-60">{day.count || ''}</span><div className="w-full rounded-t" style={{ height: `${Math.max(2, height)}%`, backgroundColor: 'var(--color-accent)', opacity: day.count > 0 ? 1 : 0.2, transition: 'height 0.3s' }} /><span className="text-xs opacity-50">{day.label}</span></div>
            ); })}
          </div>
        </section>

        {/* Lazy widgets */}
        <Suspense fallback={<WidgetSkeleton />}><WeeklyReport /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><StudyPatterns /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><DomainRadar /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><DifficultyHeatmap /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><MilestoneTracker /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><AdaptivePathWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><ReviewQueue /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><StudyTimeChart days={14} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><StreakInsights /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><DomainRecommendWidget limit={4} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><StudyPlanWidget days={3} dailyMinutes={30} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><WeakConceptsWidget limit={5} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><LearningEfficiencyChart maxDomains={8} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><GlobalLeaderboard /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><PeerComparisonCard /></Suspense>

        {/* Domain Progress */}
        <section>
          <h2 className="text-lg font-semibold mb-4">领域进度</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {domainStats.sort((a, b) => b.pct - a.pct || (b.started ? 1 : 0) - (a.started ? 1 : 0)).map((ds) => (
              <DomainCard key={ds.domain.id} ds={ds} onClick={() => { switchDomain(ds.domain.id); navigate(`/domain/${ds.domain.id}`); }} />
            ))}
          </div>
        </section>

        <VelocitySection />

        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <Suspense fallback={<WidgetSkeleton />}><DomainComparison maxDomains={12} /></Suspense>
        </section>

        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <h2 className="text-base font-semibold mb-3 flex items-center gap-2"><Clock size={16} className="text-blue-500" /> 最近学习</h2>
          <Suspense fallback={<WidgetSkeleton />}><RecentActivity maxItems={8} /></Suspense>
        </section>
      </div>
    </div>
  );
}