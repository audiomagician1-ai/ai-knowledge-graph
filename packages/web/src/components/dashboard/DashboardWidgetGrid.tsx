/**
 * DashboardWidgetGrid — Categorized lazy-loaded widget sections for the Dashboard.
 * V3.3: Extracted from DashboardPage.tsx to maintain <200L limit + add section grouping.
 */
import { lazy, Suspense, useState, type ReactNode } from 'react';
import { ChevronDown, ChevronUp, Brain, BarChart3, Users, Search, GitBranch } from 'lucide-react';
import { WidgetSkeleton } from '@/components/dashboard/DashboardHelpers';
import { WidgetErrorBoundary } from './WidgetErrorBoundary';
import { useDashboardPrefs } from '@/hooks/useDashboardPrefs';
import { DashboardCustomizer } from './DashboardCustomizer';

/** Wrap a widget in error boundary + suspense */
function W({ name, children }: { name: string; children: ReactNode }) {
  return (
    <WidgetErrorBoundary name={name}>
      <Suspense fallback={<WidgetSkeleton />}>{children}</Suspense>
    </WidgetErrorBoundary>
  );
}

// ── Learning & Review ──
const AdaptivePathWidget = lazy(() => import('./AdaptivePathWidget').then(m => ({ default: m.AdaptivePathWidget })));
const ReviewQueue = lazy(() => import('./ReviewQueue').then(m => ({ default: m.ReviewQueue })));
const ReviewPriorityWidget = lazy(() => import('./ReviewPriorityWidget').then(m => ({ default: m.ReviewPriorityWidget })));
const StudyPlanWidget = lazy(() => import('./StudyPlanWidget').then(m => ({ default: m.StudyPlanWidget })));
const PrerequisiteCheckWidget = lazy(() => import('./PrerequisiteCheckWidget').then(m => ({ default: m.PrerequisiteCheckWidget })));
const MasteryForecastWidget = lazy(() => import('./MasteryForecastWidget').then(m => ({ default: m.MasteryForecastWidget })));
const NextMilestonesWidget = lazy(() => import('./NextMilestonesWidget').then(m => ({ default: m.NextMilestonesWidget })));
const SessionReplayWidget = lazy(() => import('./SessionReplayWidget').then(m => ({ default: m.SessionReplayWidget })));
const FSRSInsightsWidget = lazy(() => import('./FSRSInsightsWidget').then(m => ({ default: m.FSRSInsightsWidget })));
const GoalRecommendWidget = lazy(() => import('./GoalRecommendWidget').then(m => ({ default: m.GoalRecommendWidget })));
const LearningProfileWidget = lazy(() => import('./LearningProfileWidget').then(m => ({ default: m.LearningProfileWidget })));
const PortfolioExportWidget = lazy(() => import('./PortfolioExportWidget').then(m => ({ default: m.PortfolioExportWidget })));
const DailySummaryWidget = lazy(() => import('./DailySummaryWidget').then(m => ({ default: m.DailySummaryWidget })));
const AchievementShowcaseWidget = lazy(() => import('./AchievementShowcaseWidget').then(m => ({ default: m.AchievementShowcaseWidget })));

// ── Analytics & Insights ──
const WeeklyReport = lazy(() => import('./WeeklyReport').then(m => ({ default: m.WeeklyReport })));
const ApiHealthWidget = lazy(() => import('./ApiHealthWidget').then(m => ({ default: m.ApiHealthWidget })));
const StudyPatterns = lazy(() => import('./StudyPatterns').then(m => ({ default: m.StudyPatterns })));
const StudyTimeChart = lazy(() => import('./StudyTimeChart').then(m => ({ default: m.StudyTimeChart })));
const StreakInsights = lazy(() => import('./StreakInsights').then(m => ({ default: m.StreakInsights })));
const SessionSummaryWidget = lazy(() => import('./SessionSummaryWidget').then(m => ({ default: m.SessionSummaryWidget })));
const WeakConceptsWidget = lazy(() => import('./WeakConceptsWidget').then(m => ({ default: m.WeakConceptsWidget })));
const LearningEfficiencyChart = lazy(() => import('./LearningEfficiencyChart').then(m => ({ default: m.LearningEfficiencyChart })));
const ComparativeProgressWidget = lazy(() => import('./ComparativeProgressWidget').then(m => ({ default: m.ComparativeProgressWidget })));
const LearningStyleWidget = lazy(() => import('./LearningStyleWidget'));
const LearningCalendarWidget = lazy(() => import('./LearningCalendarWidget').then(m => ({ default: m.LearningCalendarWidget })));

// ── Domain & Graph ──
const DomainRadar = lazy(() => import('./DomainRadar').then(m => ({ default: m.DomainRadar })));
const DifficultyHeatmap = lazy(() => import('./DifficultyHeatmap').then(m => ({ default: m.DifficultyHeatmap })));
const MilestoneTracker = lazy(() => import('./MilestoneTracker').then(m => ({ default: m.MilestoneTracker })));
const DomainRecommendWidget = lazy(() => import('./DomainRecommendWidget').then(m => ({ default: m.DomainRecommendWidget })));
const GraphTopologyWidget = lazy(() => import('./GraphTopologyWidget').then(m => ({ default: m.GraphTopologyWidget })));
const ConceptClusterWidget = lazy(() => import('./ConceptClusterWidget').then(m => ({ default: m.ConceptClusterWidget })));
const DifficultyAccuracyWidget = lazy(() => import('./DifficultyAccuracyWidget').then(m => ({ default: m.DifficultyAccuracyWidget })));
const DomainOverviewBatchWidget = lazy(() => import('./DomainOverviewBatchWidget').then(m => ({ default: m.DomainOverviewBatchWidget })));
const LearningHeatmapWidget = lazy(() => import('./LearningHeatmapWidget'));
const CrossDomainInsightsWidget = lazy(() => import('./CrossDomainInsightsWidget'));
const DifficultyTunerWidget = lazy(() => import('./DifficultyTunerWidget').then(m => ({ default: m.DifficultyTunerWidget })));
const KnowledgeMapWidget = lazy(() => import('./KnowledgeMapWidget').then(m => ({ default: m.KnowledgeMapWidget })));

// ── Social & Community ──
const GlobalLeaderboard = lazy(() => import('./GlobalLeaderboard').then(m => ({ default: m.GlobalLeaderboard })));
const PeerComparisonCard = lazy(() => import('./PeerComparisonCard').then(m => ({ default: m.PeerComparisonCard })));

// ── Content & Search ──
const ContentSearchWidget = lazy(() => import('./ContentSearchWidget').then(m => ({ default: m.ContentSearchWidget })));
const ContentHealthWidget = lazy(() => import('./ContentHealthWidget').then(m => ({ default: m.ContentHealthWidget })));
const OnboardingRecommendWidget = lazy(() => import('./OnboardingRecommendWidget').then(m => ({ default: m.OnboardingRecommendWidget })));
const ConceptJourneyWidget = lazy(() => import('./ConceptJourneyWidget'));
const SearchSuggestionsWidget = lazy(() => import('./SearchSuggestionsWidget'));
const ProgressSnapshotWidget = lazy(() => import('./ProgressSnapshotWidget'));

interface SectionProps {
  title: string;
  icon: React.ReactNode;
  defaultOpen?: boolean;
  children: React.ReactNode;
}

function CollapsibleSection({ title, icon, defaultOpen = true, children }: SectionProps) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div>
      <button onClick={() => setOpen(!open)} className="flex items-center gap-2 w-full text-left mb-3 group">
        {icon}
        <h2 className="text-sm font-semibold uppercase tracking-wider opacity-50 group-hover:opacity-70 transition-opacity">{title}</h2>
        <span className="ml-auto opacity-30">{open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</span>
      </button>
      {open && <div className="space-y-4">{children}</div>}
    </div>
  );
}

// Section id → renderable content map (order controlled by prefs)
const SECTION_MAP: Record<string, { title: string; icon: React.ReactNode; defaultOpen: boolean; content: React.ReactNode }> = {
  learning: {
    title: '学习与复习', icon: <Brain size={14} className="opacity-40" />, defaultOpen: true,
    content: (<>
        <W name="今日概览"><DailySummaryWidget /></W>
        <W name="学习档案"><LearningProfileWidget /></W>
        <W name="学习小结"><SessionSummaryWidget hours={24} /></W>
        <W name="智能路径"><AdaptivePathWidget /></W>
        <W name="复习队列"><ReviewQueue /></W>
        <W name="复习优先级"><ReviewPriorityWidget limit={8} /></W>
        <W name="学习计划"><StudyPlanWidget days={3} dailyMinutes={30} /></W>
        <W name="前置检查"><PrerequisiteCheckWidget /></W>
        <W name="掌握预测"><MasteryForecastWidget /></W>
        <W name="里程碑"><NextMilestonesWidget limit={5} /></W>
        <W name="学习回放"><SessionReplayWidget limit={8} /></W>
        <W name="FSRS分析"><FSRSInsightsWidget /></W>
        <W name="目标建议"><GoalRecommendWidget /></W>
        <W name="学习档案导出"><PortfolioExportWidget /></W>
        <W name="成就展示"><AchievementShowcaseWidget /></W>
    </>),
  },
  analytics: {
    title: '数据分析', icon: <BarChart3 size={14} className="opacity-40" />, defaultOpen: true,
    content: (<>
        <W name="进度快照"><ProgressSnapshotWidget /></W>
        <W name="周报"><WeeklyReport /></W>
        <W name="学习模式"><StudyPatterns /></W>
        <W name="学习时间"><StudyTimeChart days={14} /></W>
        <W name="连续洞察"><StreakInsights /></W>
        <W name="薄弱概念"><WeakConceptsWidget limit={5} /></W>
        <W name="学习效率"><LearningEfficiencyChart maxDomains={8} /></W>
        <W name="周对比"><ComparativeProgressWidget /></W>
        <W name="学习风格"><LearningStyleWidget /></W>
        <W name="学习日历"><LearningCalendarWidget months={3} /></W>
        <W name="API健康"><ApiHealthWidget /></W>
    </>),
  },
  domains: {
    title: '领域与图谱', icon: <GitBranch size={14} className="opacity-40" />, defaultOpen: true,
    content: (<>
        <W name="掌握度雷达"><DomainRadar /></W>
        <W name="难度热力图"><DifficultyHeatmap /></W>
        <W name="里程碑追踪"><MilestoneTracker /></W>
        <W name="域推荐"><DomainRecommendWidget limit={4} /></W>
        <W name="图谱拓扑"><GraphTopologyWidget /></W>
        <W name="概念聚类"><ConceptClusterWidget /></W>
        <W name="难度校准"><DifficultyAccuracyWidget /></W>
        <W name="全域概览"><DomainOverviewBatchWidget /></W>
        <W name="学习热力图"><LearningHeatmapWidget /></W>
        <W name="跨域洞察"><CrossDomainInsightsWidget /></W>
        <W name="难度调优"><DifficultyTunerWidget limit={10} /></W>
        <W name="知识图谱探索"><KnowledgeMapWidget /></W>
    </>),
  },
  social: {
    title: '社交互动', icon: <Users size={14} className="opacity-40" />, defaultOpen: false,
    content: (<>
        <W name="排行榜"><GlobalLeaderboard /></W>
        <W name="同伴对比"><PeerComparisonCard /></W>
    </>),
  },
  content: {
    title: '内容与发现', icon: <Search size={14} className="opacity-40" />, defaultOpen: false,
    content: (<>
        <W name="搜索建议"><SearchSuggestionsWidget /></W>
        <W name="内容搜索"><ContentSearchWidget /></W>
        <W name="内容健康"><ContentHealthWidget /></W>
        <W name="入门推荐"><OnboardingRecommendWidget /></W>
        <W name="概念旅程"><ConceptJourneyWidget /></W>
    </>),
  },
};

export function DashboardWidgetGrid() {
  const { sections } = useDashboardPrefs();

  return (
    <div className="space-y-8">
      <DashboardCustomizer />
      {sections.filter(s => s.visible).map(sec => {
        const cfg = SECTION_MAP[sec.id];
        if (!cfg) return null;
        return (
          <CollapsibleSection key={sec.id} title={cfg.title} icon={cfg.icon} defaultOpen={cfg.defaultOpen}>
            {cfg.content}
          </CollapsibleSection>
        );
      })}
    </div>
  );
}
