import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import {
  ArrowLeft, Route as RouteIcon, ChevronRight, Lock, CheckCircle2,
  BookOpen, Sparkles, Target, Zap,
} from 'lucide-react';

/**
 * Learning Path Page — shows a recommended linear path through a domain.
 * Uses topological sort from seed_graph edges + user progress.
 * Path: /path/:domainId
 */
export function LearningPathPage() {
  const { domainId } = useParams<{ domainId: string }>();
  const navigate = useNavigate();
  const domains = useDomainStore((s) => s.domains);
  const graphData = useGraphStore((s) => s.graphData);
  const loadGraphData = useGraphStore((s) => s.loadGraphData);
  const progress = useLearningStore((s) => s.progress);

  const [expandedGroup, setExpandedGroup] = useState<string | null>(null);

  useKeyboardShortcuts([
    { key: 'Escape', handler: () => navigate(domainId ? `/domain/${domainId}` : '/'), description: 'Back' },
  ]);

  const domain = domains.find((d) => d.id === domainId);

  useEffect(() => {
    if (domainId) loadGraphData(domainId);
  }, [domainId, loadGraphData]);

  // Load domain-specific progress
  const domainProgress = useMemo(() => {
    if (!domainId) return {};
    try {
      const raw = localStorage.getItem(`akg-learning:${domainId}`);
      if (raw) return JSON.parse(raw)?.progress || {};
    } catch { /* skip */ }
    return progress;
  }, [domainId, progress]);

  // Build topological learning path from graph edges
  const pathGroups = useMemo(() => {
    if (!graphData?.nodes?.length) return [];

    const nodes = graphData.nodes as Array<{ id: string; label: string; group?: string; is_milestone?: boolean }>;
    const edges = (graphData.edges || []) as Array<{ source: string; target: string }>;

    // Build adjacency for topological sort
    const inDegree = new Map<string, number>();
    const adj = new Map<string, string[]>();
    for (const n of nodes) {
      inDegree.set(n.id, 0);
      adj.set(n.id, []);
    }
    for (const e of edges) {
      adj.get(e.source)?.push(e.target);
      inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1);
    }

    // Kahn's algorithm
    const queue = nodes.filter((n) => (inDegree.get(n.id) || 0) === 0).map((n) => n.id);
    const sorted: string[] = [];
    while (queue.length > 0) {
      const curr = queue.shift()!;
      sorted.push(curr);
      for (const next of adj.get(curr) || []) {
        const newDeg = (inDegree.get(next) || 1) - 1;
        inDegree.set(next, newDeg);
        if (newDeg === 0) queue.push(next);
      }
    }
    // Add any remaining (cycles)
    for (const n of nodes) {
      if (!sorted.includes(n.id)) sorted.push(n.id);
    }

    // Group by subdomain
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    const groups = new Map<string, typeof nodes>();
    for (const id of sorted) {
      const node = nodeMap.get(id);
      if (!node) continue;
      const group = node.group || '核心概念';
      if (!groups.has(group)) groups.set(group, []);
      groups.get(group)!.push(node);
    }

    return Array.from(groups.entries()).map(([name, concepts]) => ({
      name,
      concepts: concepts.map((c) => ({
        id: c.id,
        label: c.label,
        isMilestone: c.is_milestone || false,
        status: (domainProgress[c.id]?.status as string) || 'not_started',
        mastery: domainProgress[c.id]?.mastery_score || 0,
      })),
    }));
  }, [graphData, domainProgress]);

  // Stats
  const totalConcepts = pathGroups.reduce((s, g) => s + g.concepts.length, 0);
  const masteredCount = pathGroups.reduce(
    (s, g) => s + g.concepts.filter((c) => c.status === 'mastered').length,
    0
  );
  const learningCount = pathGroups.reduce(
    (s, g) => s + g.concepts.filter((c) => c.status === 'learning').length,
    0
  );

  // Find next recommended concept
  const nextRecommended = useMemo(() => {
    for (const group of pathGroups) {
      for (const c of group.concepts) {
        if (c.status !== 'mastered') return c.id;
      }
    }
    return null;
  }, [pathGroups]);

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      {/* Header */}
      <header className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <button
          onClick={() => navigate(domainId ? `/domain/${domainId}` : '/')}
          className="p-2 rounded-lg hover:bg-white/10 transition-colors"
        >
          <ArrowLeft size={20} />
        </button>
        <RouteIcon size={24} style={{ color: domain?.color || 'var(--color-accent)' }} />
        <div>
          <h1 className="text-xl font-bold">学习路径</h1>
          <p className="text-sm opacity-60">{domain?.icon} {domain?.name || domainId}</p>
        </div>
      </header>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
        {/* Progress overview */}
        <div className="grid grid-cols-3 gap-3">
          <div className="rounded-xl p-3 text-center" style={{ backgroundColor: 'var(--color-surface-1)' }}>
            <div className="text-2xl font-bold" style={{ color: '#22c55e' }}>{masteredCount}</div>
            <div className="text-xs opacity-60">已掌握</div>
          </div>
          <div className="rounded-xl p-3 text-center" style={{ backgroundColor: 'var(--color-surface-1)' }}>
            <div className="text-2xl font-bold" style={{ color: '#3b82f6' }}>{learningCount}</div>
            <div className="text-xs opacity-60">学习中</div>
          </div>
          <div className="rounded-xl p-3 text-center" style={{ backgroundColor: 'var(--color-surface-1)' }}>
            <div className="text-2xl font-bold">{totalConcepts - masteredCount - learningCount}</div>
            <div className="text-xs opacity-60">未开始</div>
          </div>
        </div>

        {/* Overall progress bar */}
        <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <div className="flex justify-between text-sm mb-2">
            <span>总进度</span>
            <span className="font-bold">{totalConcepts > 0 ? Math.round((masteredCount / totalConcepts) * 100) : 0}%</span>
          </div>
          <div className="w-full h-3 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-3)' }}>
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{
                width: `${totalConcepts > 0 ? (masteredCount / totalConcepts) * 100 : 0}%`,
                backgroundColor: domain?.color || '#3b82f6',
              }}
            />
          </div>
        </div>

        {/* Learning path groups */}
        {pathGroups.map((group) => {
          const groupMastered = group.concepts.filter((c) => c.status === 'mastered').length;
          const groupTotal = group.concepts.length;
          const isExpanded = expandedGroup === group.name || expandedGroup === null;

          return (
            <section key={group.name} className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--color-surface-1)' }}>
              <button
                onClick={() => setExpandedGroup(isExpanded && expandedGroup !== null ? null : group.name)}
                className="w-full flex items-center justify-between px-5 py-3 hover:bg-white/5 transition-colors"
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium">{group.name}</span>
                  <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: 'var(--color-surface-3)' }}>
                    {groupMastered}/{groupTotal}
                  </span>
                </div>
                <ChevronRight
                  size={16}
                  style={{
                    transition: 'transform 0.2s',
                    transform: isExpanded ? 'rotate(90deg)' : 'rotate(0)',
                  }}
                />
              </button>

              {isExpanded && (
                <div className="px-5 pb-4 space-y-1">
                  {group.concepts.map((concept, idx) => {
                    const isNext = concept.id === nextRecommended;
                    return (
                      <button
                        key={concept.id}
                        onClick={() => navigate(`/learn/${domainId}/${concept.id}`)}
                        className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-white/5 transition-colors text-left"
                        style={{
                          border: isNext ? `1px solid ${domain?.color || '#3b82f6'}` : '1px solid transparent',
                        }}
                      >
                        {/* Status icon */}
                        <div className="shrink-0">
                          {concept.status === 'mastered' ? (
                            <CheckCircle2 size={18} style={{ color: '#22c55e' }} />
                          ) : concept.status === 'learning' ? (
                            <BookOpen size={18} style={{ color: '#3b82f6' }} />
                          ) : idx > 0 && group.concepts[idx - 1].status === 'not_started' ? (
                            <Lock size={18} style={{ color: 'var(--color-text-tertiary)' }} />
                          ) : (
                            <Target size={18} style={{ color: 'var(--color-text-tertiary)' }} />
                          )}
                        </div>

                        {/* Concept info */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className={`text-sm ${concept.status === 'mastered' ? 'line-through opacity-50' : ''}`}>
                              {concept.label}
                            </span>
                            {concept.isMilestone && (
                              <Sparkles size={12} style={{ color: '#f59e0b' }} />
                            )}
                            {isNext && (
                              <span className="text-[10px] px-1.5 py-0.5 rounded" style={{ backgroundColor: `${domain?.color || '#3b82f6'}20`, color: domain?.color || '#3b82f6' }}>
                                推荐
                              </span>
                            )}
                          </div>
                          {concept.mastery > 0 && (
                            <div className="flex items-center gap-2 mt-0.5">
                              <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-3)', maxWidth: 80 }}>
                                <div
                                  className="h-full rounded-full"
                                  style={{
                                    width: `${concept.mastery}%`,
                                    backgroundColor: concept.mastery >= 75 ? '#22c55e' : '#3b82f6',
                                  }}
                                />
                              </div>
                              <span className="text-[10px] opacity-40">{concept.mastery}分</span>
                            </div>
                          )}
                        </div>

                        {/* Arrow */}
                        {concept.status !== 'mastered' && (
                          <Zap size={14} style={{ color: 'var(--color-text-tertiary)' }} />
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </section>
          );
        })}

        {pathGroups.length === 0 && (
          <div className="text-center py-12 opacity-50">
            <RouteIcon size={48} className="mx-auto mb-3" />
            <p>加载学习路径中…</p>
          </div>
        )}
      </div>
    </div>
  );
}
