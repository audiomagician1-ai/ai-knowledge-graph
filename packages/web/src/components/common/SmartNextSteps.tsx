import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLearningStore } from '@/lib/store/learning';
import { useGraphStore } from '@/lib/store/graph';
import { useDomainStore } from '@/lib/store/domain';
import { Zap, RotateCcw, TrendingUp, Trophy, ArrowRight } from 'lucide-react';

interface SmartStep {
  type: 'review' | 'learn_recommended' | 'continue_learning' | 'explore_domain' | 'milestone';
  icon: typeof Zap;
  title: string;
  description: string;
  action: () => void;
  priority: number;
  color: string;
}

/**
 * Smart Next Steps widget — analyzes user progress and graph structure
 * to suggest the most impactful next learning actions.
 * Shows up to 3 prioritized suggestions.
 */
export function SmartNextSteps() {
  const navigate = useNavigate();
  const progress = useLearningStore((s) => s.progress);
  const graphData = useGraphStore((s) => s.graphData);
  const { activeDomain, getActiveDomainInfo } = useDomainStore();

  const steps = useMemo<SmartStep[]>(() => {
    const suggestions: SmartStep[] = [];
    if (!graphData) return suggestions;

    const progressEntries = Object.entries(progress);
    const masteredIds = new Set(progressEntries.filter(([, p]) => p.status === 'mastered').map(([id]) => id));
    const learningIds = new Set(progressEntries.filter(([, p]) => p.status === 'learning').map(([id]) => id));

    // Build prerequisite map
    const prereqMap = new Map<string, Set<string>>();
    for (const edge of graphData.edges) {
      if (edge.relation_type === 'prerequisite') {
        if (!prereqMap.has(edge.target)) prereqMap.set(edge.target, new Set());
        prereqMap.get(edge.target)!.add(edge.source);
      }
    }

    // 1. "Continue learning" — concepts in learning status (highest priority)
    const learningConcepts = graphData.nodes.filter((n) => learningIds.has(n.id));
    if (learningConcepts.length > 0) {
      // Pick the one with most sessions (most invested)
      const best = learningConcepts.sort((a, b) =>
        (progress[b.id]?.sessions || 0) - (progress[a.id]?.sessions || 0)
      )[0];
      suggestions.push({
        type: 'continue_learning',
        icon: TrendingUp,
        title: `继续学习: ${best.label}`,
        description: `已学 ${progress[best.id]?.sessions || 0} 次，再接再厉`,
        action: () => navigate(`/domain/${activeDomain}/${best.id}`),
        priority: 100,
        color: '#3b82f6',
      });
    }

    // 2. "Recommended" — concepts whose all prerequisites are mastered
    const recommended = graphData.nodes.filter((n) => {
      if (masteredIds.has(n.id) || learningIds.has(n.id)) return false;
      const prereqs = prereqMap.get(n.id);
      if (!prereqs || prereqs.size === 0) return false; // entry nodes are less interesting
      return [...prereqs].every((p) => masteredIds.has(p));
    });
    if (recommended.length > 0) {
      // Prefer milestones, then lowest difficulty
      const sorted = recommended.sort((a, b) => {
        if (a.is_milestone !== b.is_milestone) return a.is_milestone ? -1 : 1;
        return a.difficulty - b.difficulty;
      });
      const best = sorted[0];
      suggestions.push({
        type: 'learn_recommended',
        icon: Zap,
        title: `解锁新概念: ${best.label}`,
        description: `前置已全部掌握，Lv.${best.difficulty}${best.is_milestone ? ' ⭐' : ''}`,
        action: () => navigate(`/domain/${activeDomain}/${best.id}`),
        priority: 90,
        color: '#10b981',
      });
    }

    // 3. "Milestone approaching" — milestone concepts that have >50% prereqs mastered
    const approachingMilestones = graphData.nodes.filter((n) => {
      if (!n.is_milestone || masteredIds.has(n.id)) return false;
      const prereqs = prereqMap.get(n.id);
      if (!prereqs || prereqs.size === 0) return false;
      const masteredCount = [...prereqs].filter((p) => masteredIds.has(p)).length;
      return masteredCount > 0 && masteredCount / prereqs.size >= 0.5 && masteredCount < prereqs.size;
    });
    if (approachingMilestones.length > 0) {
      const best = approachingMilestones[0];
      const prereqs = prereqMap.get(best.id)!;
      const remaining = [...prereqs].filter((p) => !masteredIds.has(p)).length;
      suggestions.push({
        type: 'milestone',
        icon: Trophy,
        title: `接近里程碑: ${best.label}`,
        description: `还差 ${remaining} 个前置概念`,
        action: () => navigate(`/domain/${activeDomain}/${best.id}`),
        priority: 80,
        color: '#f59e0b',
      });
    }

    // 4. "Explore new domain" — if no progress at all
    if (progressEntries.length === 0) {
      const domainInfo = getActiveDomainInfo();
      suggestions.push({
        type: 'explore_domain',
        icon: ArrowRight,
        title: `开始探索: ${domainInfo?.name || '知识域'}`,
        description: '从入门概念开始你的学习旅程',
        action: () => {
          // Find lowest difficulty entry node
          const entry = graphData.nodes
            .filter((n) => !(prereqMap.get(n.id)?.size))
            .sort((a, b) => a.difficulty - b.difficulty)[0];
          if (entry) navigate(`/domain/${activeDomain}/${entry.id}`);
        },
        priority: 70,
        color: '#8b5cf6',
      });
    }

    // 5. "Review" — if there are mastered concepts (always useful)
    if (masteredIds.size > 3) {
      suggestions.push({
        type: 'review',
        icon: RotateCcw,
        title: '巩固复习',
        description: `${masteredIds.size} 个已掌握概念等待复习`,
        action: () => navigate(activeDomain ? `/review/${activeDomain}` : '/review'),
        priority: 60,
        color: '#ef4444',
      });
    }

    return suggestions.sort((a, b) => b.priority - a.priority).slice(0, 3);
  }, [graphData, progress, activeDomain, navigate, getActiveDomainInfo]);

  if (steps.length === 0) return null;

  return (
    <div className="rounded-xl" style={{ backgroundColor: 'var(--color-surface-1)', border: '1px solid var(--color-border)', boxShadow: '0 1px 3px rgba(0,0,0,0.06)', padding: '20px 24px' }}>
      <h3 className="text-sm font-bold flex items-center gap-2" style={{ color: 'var(--color-text-primary)', marginBottom: 16 }}>
        <Zap size={14} style={{ color: '#10b981' }} />
        推荐下一步
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
        {steps.map((step, i) => {
          const Icon = step.icon;
          return (
            <button key={i} onClick={step.action} className="flex items-center gap-3 rounded-lg transition-all text-left"
              style={{ padding: '12px 16px', backgroundColor: '#f5f5f3', border: '1px solid transparent' }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#eeeeec'; e.currentTarget.style.borderColor = `${step.color}30`; }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#f5f5f3'; e.currentTarget.style.borderColor = 'transparent'; }}>
              <div className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style={{ backgroundColor: `${step.color}15` }}>
                <Icon size={16} style={{ color: step.color }} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>{step.title}</div>
                <div className="text-xs truncate" style={{ color: 'var(--color-text-tertiary)' }}>{step.description}</div>
              </div>
              <ArrowRight size={14} className="shrink-0" style={{ color: 'var(--color-text-tertiary)' }} />
            </button>
          );
        })}
      </div>
    </div>
  );
}