/**
 * widget-registry.ts — Centralized lazy-loaded widget import registry.
 * V4.6: Extracted from DashboardWidgetGrid.tsx (189→~120L) to keep grid file under 200L limit.
 * All 45 dashboard widgets are registered here for code splitting.
 */
import { lazy } from 'react';

// ── Learning & Review ──
export const AdaptivePathWidget = lazy(() => import('./AdaptivePathWidget').then(m => ({ default: m.AdaptivePathWidget })));
export const ReviewQueue = lazy(() => import('./ReviewQueue').then(m => ({ default: m.ReviewQueue })));
export const ReviewPriorityWidget = lazy(() => import('./ReviewPriorityWidget').then(m => ({ default: m.ReviewPriorityWidget })));
export const StudyPlanWidget = lazy(() => import('./StudyPlanWidget').then(m => ({ default: m.StudyPlanWidget })));
export const PrerequisiteCheckWidget = lazy(() => import('./PrerequisiteCheckWidget').then(m => ({ default: m.PrerequisiteCheckWidget })));
export const MasteryForecastWidget = lazy(() => import('./MasteryForecastWidget').then(m => ({ default: m.MasteryForecastWidget })));
export const NextMilestonesWidget = lazy(() => import('./NextMilestonesWidget').then(m => ({ default: m.NextMilestonesWidget })));
export const SessionReplayWidget = lazy(() => import('./SessionReplayWidget').then(m => ({ default: m.SessionReplayWidget })));
export const FSRSInsightsWidget = lazy(() => import('./FSRSInsightsWidget').then(m => ({ default: m.FSRSInsightsWidget })));
export const GoalRecommendWidget = lazy(() => import('./GoalRecommendWidget').then(m => ({ default: m.GoalRecommendWidget })));
export const LearningProfileWidget = lazy(() => import('./LearningProfileWidget').then(m => ({ default: m.LearningProfileWidget })));
export const PortfolioExportWidget = lazy(() => import('./PortfolioExportWidget').then(m => ({ default: m.PortfolioExportWidget })));
export const DailySummaryWidget = lazy(() => import('./DailySummaryWidget').then(m => ({ default: m.DailySummaryWidget })));
export const AchievementShowcaseWidget = lazy(() => import('./AchievementShowcaseWidget').then(m => ({ default: m.AchievementShowcaseWidget })));

// ── Analytics & Insights ──
export const WeeklyReport = lazy(() => import('./WeeklyReport').then(m => ({ default: m.WeeklyReport })));
export const ApiHealthWidget = lazy(() => import('./ApiHealthWidget').then(m => ({ default: m.ApiHealthWidget })));
export const StudyPatterns = lazy(() => import('./StudyPatterns').then(m => ({ default: m.StudyPatterns })));
export const StudyTimeChart = lazy(() => import('./StudyTimeChart').then(m => ({ default: m.StudyTimeChart })));
export const StreakInsights = lazy(() => import('./StreakInsights').then(m => ({ default: m.StreakInsights })));
export const SessionSummaryWidget = lazy(() => import('./SessionSummaryWidget').then(m => ({ default: m.SessionSummaryWidget })));
export const WeakConceptsWidget = lazy(() => import('./WeakConceptsWidget').then(m => ({ default: m.WeakConceptsWidget })));
export const LearningEfficiencyChart = lazy(() => import('./LearningEfficiencyChart').then(m => ({ default: m.LearningEfficiencyChart })));
export const ComparativeProgressWidget = lazy(() => import('./ComparativeProgressWidget').then(m => ({ default: m.ComparativeProgressWidget })));
export const LearningStyleWidget = lazy(() => import('./LearningStyleWidget').then(m => ({ default: m.LearningStyleWidget })));
export const LearningCalendarWidget = lazy(() => import('./LearningCalendarWidget').then(m => ({ default: m.LearningCalendarWidget })));

// ── Domain & Graph ──
export const DomainRadar = lazy(() => import('./DomainRadar').then(m => ({ default: m.DomainRadar })));
export const DifficultyHeatmap = lazy(() => import('./DifficultyHeatmap').then(m => ({ default: m.DifficultyHeatmap })));
export const MilestoneTracker = lazy(() => import('./MilestoneTracker').then(m => ({ default: m.MilestoneTracker })));
export const DomainRecommendWidget = lazy(() => import('./DomainRecommendWidget').then(m => ({ default: m.DomainRecommendWidget })));
export const GraphTopologyWidget = lazy(() => import('./GraphTopologyWidget').then(m => ({ default: m.GraphTopologyWidget })));
export const ConceptClusterWidget = lazy(() => import('./ConceptClusterWidget').then(m => ({ default: m.ConceptClusterWidget })));
export const DifficultyAccuracyWidget = lazy(() => import('./DifficultyAccuracyWidget').then(m => ({ default: m.DifficultyAccuracyWidget })));
export const DomainOverviewBatchWidget = lazy(() => import('./DomainOverviewBatchWidget').then(m => ({ default: m.DomainOverviewBatchWidget })));
export const LearningHeatmapWidget = lazy(() => import('./LearningHeatmapWidget').then(m => ({ default: m.LearningHeatmapWidget })));
export const CrossDomainInsightsWidget = lazy(() => import('./CrossDomainInsightsWidget').then(m => ({ default: m.CrossDomainInsightsWidget })));
export const DifficultyTunerWidget = lazy(() => import('./DifficultyTunerWidget').then(m => ({ default: m.DifficultyTunerWidget })));
export const KnowledgeMapWidget = lazy(() => import('./KnowledgeMapWidget').then(m => ({ default: m.KnowledgeMapWidget })));

// ── Social & Community ──
export const GlobalLeaderboard = lazy(() => import('./GlobalLeaderboard').then(m => ({ default: m.GlobalLeaderboard })));
export const PeerComparisonCard = lazy(() => import('./PeerComparisonCard').then(m => ({ default: m.PeerComparisonCard })));

// ── Content & Search ──
export const ContentSearchWidget = lazy(() => import('./ContentSearchWidget').then(m => ({ default: m.ContentSearchWidget })));
export const ContentHealthWidget = lazy(() => import('./ContentHealthWidget').then(m => ({ default: m.ContentHealthWidget })));
export const OnboardingRecommendWidget = lazy(() => import('./OnboardingRecommendWidget').then(m => ({ default: m.OnboardingRecommendWidget })));
export const ConceptJourneyWidget = lazy(() => import('./ConceptJourneyWidget').then(m => ({ default: m.ConceptJourneyWidget })));
export const SearchSuggestionsWidget = lazy(() => import('./SearchSuggestionsWidget').then(m => ({ default: m.SearchSuggestionsWidget })));
export const ProgressSnapshotWidget = lazy(() => import('./ProgressSnapshotWidget').then(m => ({ default: m.ProgressSnapshotWidget })));