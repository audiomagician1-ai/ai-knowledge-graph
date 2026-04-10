/**
 * DashboardWidgetGrid — Categorized lazy-loaded widget sections for the Dashboard.
 * V3.3: Extracted from DashboardPage.tsx to maintain <200L limit + add section grouping.
 * V4.6: Widget lazy imports extracted to widget-registry.ts (189→120L).
 */
import { Suspense, useState, type ReactNode } from 'react';
import { ChevronDown, ChevronUp, Brain, BarChart3, Users, Search, GitBranch } from 'lucide-react';
import { WidgetSkeleton } from '@/components/dashboard/DashboardHelpers';
import { WidgetErrorBoundary } from './WidgetErrorBoundary';
import { useDashboardPrefs } from '@/hooks/useDashboardPrefs';
import { DashboardCustomizer } from './DashboardCustomizer';
import * as W_ from './widget-registry';

/** Wrap a widget in error boundary + suspense */
function W({ name, children }: { name: string; children: ReactNode }) {
  return (
    <WidgetErrorBoundary name={name}>
      <Suspense fallback={<WidgetSkeleton />}>{children}</Suspense>
    </WidgetErrorBoundary>
  );
}

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
        <W name="今日概览"><W_.DailySummaryWidget /></W>
        <W name="学习档案"><W_.LearningProfileWidget /></W>
        <W name="学习小结"><W_.SessionSummaryWidget hours={24} /></W>
        <W name="智能路径"><W_.AdaptivePathWidget /></W>
        <W name="复习队列"><W_.ReviewQueue /></W>
        <W name="复习优先级"><W_.ReviewPriorityWidget limit={8} /></W>
        <W name="学习计划"><W_.StudyPlanWidget days={3} dailyMinutes={30} /></W>
        <W name="前置检查"><W_.PrerequisiteCheckWidget /></W>
        <W name="掌握预测"><W_.MasteryForecastWidget /></W>
        <W name="里程碑"><W_.NextMilestonesWidget limit={5} /></W>
        <W name="学习回放"><W_.SessionReplayWidget limit={8} /></W>
        <W name="FSRS分析"><W_.FSRSInsightsWidget /></W>
        <W name="目标建议"><W_.GoalRecommendWidget /></W>
        <W name="学习档案导出"><W_.PortfolioExportWidget /></W>
        <W name="成就展示"><W_.AchievementShowcaseWidget /></W>
    </>),
  },
  analytics: {
    title: '数据分析', icon: <BarChart3 size={14} className="opacity-40" />, defaultOpen: true,
    content: (<>
        <W name="进度快照"><W_.ProgressSnapshotWidget /></W>
        <W name="周报"><W_.WeeklyReport /></W>
        <W name="学习模式"><W_.StudyPatterns /></W>
        <W name="学习时间"><W_.StudyTimeChart days={14} /></W>
        <W name="连续洞察"><W_.StreakInsights /></W>
        <W name="薄弱概念"><W_.WeakConceptsWidget limit={5} /></W>
        <W name="学习效率"><W_.LearningEfficiencyChart maxDomains={8} /></W>
        <W name="周对比"><W_.ComparativeProgressWidget /></W>
        <W name="学习风格"><W_.LearningStyleWidget /></W>
        <W name="学习日历"><W_.LearningCalendarWidget months={3} /></W>
        <W name="API健康"><W_.ApiHealthWidget /></W>
    </>),
  },
  domains: {
    title: '领域与图谱', icon: <GitBranch size={14} className="opacity-40" />, defaultOpen: true,
    content: (<>
        <W name="掌握度雷达"><W_.DomainRadar /></W>
        <W name="难度热力图"><W_.DifficultyHeatmap /></W>
        <W name="里程碑追踪"><W_.MilestoneTracker /></W>
        <W name="域推荐"><W_.DomainRecommendWidget limit={4} /></W>
        <W name="图谱拓扑"><W_.GraphTopologyWidget /></W>
        <W name="概念聚类"><W_.ConceptClusterWidget /></W>
        <W name="难度校准"><W_.DifficultyAccuracyWidget /></W>
        <W name="全域概览"><W_.DomainOverviewBatchWidget /></W>
        <W name="学习热力图"><W_.LearningHeatmapWidget /></W>
        <W name="跨域洞察"><W_.CrossDomainInsightsWidget /></W>
        <W name="难度调优"><W_.DifficultyTunerWidget limit={10} /></W>
        <W name="知识图谱探索"><W_.KnowledgeMapWidget /></W>
    </>),
  },
  social: {
    title: '社交互动', icon: <Users size={14} className="opacity-40" />, defaultOpen: false,
    content: (<>
        <W name="排行榜"><W_.GlobalLeaderboard /></W>
        <W name="同伴对比"><W_.PeerComparisonCard /></W>
    </>),
  },
  content: {
    title: '内容与发现', icon: <Search size={14} className="opacity-40" />, defaultOpen: false,
    content: (<>
        <W name="搜索建议"><W_.SearchSuggestionsWidget /></W>
        <W name="内容搜索"><W_.ContentSearchWidget /></W>
        <W name="内容健康"><W_.ContentHealthWidget /></W>
        <W name="入门推荐"><W_.OnboardingRecommendWidget /></W>
        <W name="概念旅程"><W_.ConceptJourneyWidget /></W>
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
