/**
 * DashboardWidgetGrid — Categorized lazy-loaded widget sections for the Dashboard.
 * V3.3: Extracted from DashboardPage.tsx to maintain <200L limit + add section grouping.
 */
import { lazy, Suspense, useState } from 'react';
import { ChevronDown, ChevronUp, Brain, BarChart3, Users, Search, Compass, GitBranch } from 'lucide-react';
import { WidgetSkeleton } from '@/components/dashboard/DashboardHelpers';

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

// ── Analytics & Insights ──
const WeeklyReport = lazy(() => import('./WeeklyReport').then(m => ({ default: m.WeeklyReport })));
const StudyPatterns = lazy(() => import('./StudyPatterns').then(m => ({ default: m.StudyPatterns })));
const StudyTimeChart = lazy(() => import('./StudyTimeChart').then(m => ({ default: m.StudyTimeChart })));
const StreakInsights = lazy(() => import('./StreakInsights').then(m => ({ default: m.StreakInsights })));
const SessionSummaryWidget = lazy(() => import('./SessionSummaryWidget').then(m => ({ default: m.SessionSummaryWidget })));
const WeakConceptsWidget = lazy(() => import('./WeakConceptsWidget').then(m => ({ default: m.WeakConceptsWidget })));
const LearningEfficiencyChart = lazy(() => import('./LearningEfficiencyChart').then(m => ({ default: m.LearningEfficiencyChart })));
const ComparativeProgressWidget = lazy(() => import('./ComparativeProgressWidget').then(m => ({ default: m.ComparativeProgressWidget })));

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

export function DashboardWidgetGrid() {
  return (
    <div className="space-y-8">
      <CollapsibleSection title="学习与复习" icon={<Brain size={14} className="opacity-40" />}>
        <Suspense fallback={<WidgetSkeleton />}><LearningProfileWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><SessionSummaryWidget hours={24} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><AdaptivePathWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><ReviewQueue /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><ReviewPriorityWidget limit={8} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><StudyPlanWidget days={3} dailyMinutes={30} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><PrerequisiteCheckWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><MasteryForecastWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><NextMilestonesWidget limit={5} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><SessionReplayWidget limit={8} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><FSRSInsightsWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><GoalRecommendWidget /></Suspense>
      </CollapsibleSection>

      <CollapsibleSection title="数据分析" icon={<BarChart3 size={14} className="opacity-40" />}>
        <Suspense fallback={<WidgetSkeleton />}><ProgressSnapshotWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><WeeklyReport /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><StudyPatterns /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><StudyTimeChart days={14} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><StreakInsights /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><WeakConceptsWidget limit={5} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><LearningEfficiencyChart maxDomains={8} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><ComparativeProgressWidget /></Suspense>
      </CollapsibleSection>

      <CollapsibleSection title="领域与图谱" icon={<GitBranch size={14} className="opacity-40" />}>
        <Suspense fallback={<WidgetSkeleton />}><DomainRadar /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><DifficultyHeatmap /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><MilestoneTracker /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><DomainRecommendWidget limit={4} /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><GraphTopologyWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><ConceptClusterWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><DifficultyAccuracyWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><DomainOverviewBatchWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><LearningHeatmapWidget /></Suspense>
      </CollapsibleSection>

      <CollapsibleSection title="社交互动" icon={<Users size={14} className="opacity-40" />} defaultOpen={false}>
        <Suspense fallback={<WidgetSkeleton />}><GlobalLeaderboard /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><PeerComparisonCard /></Suspense>
      </CollapsibleSection>

      <CollapsibleSection title="内容与发现" icon={<Search size={14} className="opacity-40" />} defaultOpen={false}>
        <Suspense fallback={<WidgetSkeleton />}><SearchSuggestionsWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><ContentSearchWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><ContentHealthWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><OnboardingRecommendWidget /></Suspense>
        <Suspense fallback={<WidgetSkeleton />}><ConceptJourneyWidget /></Suspense>
      </CollapsibleSection>
    </div>
  );
}
