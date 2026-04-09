import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { ArrowLeft, Route as RouteIcon } from 'lucide-react';
import { PathGroupSection, type PathGroup } from '@/components/learning-path/PathGroupSection';
import { KnowledgeGapsSection, type KnowledgeGap } from '@/components/learning-path/KnowledgeGapsSection';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

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
  const [gaps, setGaps] = useState<KnowledgeGap[]>([]);

  useKeyboardShortcuts([
    { key: 'Escape', handler: () => navigate(domainId ? `/domain/${domainId}` : '/'), description: 'Back' },
  ]);

  const domain = domains.find((d) => d.id === domainId);

  useEffect(() => {
    if (domainId) loadGraphData(domainId);
  }, [domainId, loadGraphData]);

  // Fetch knowledge gaps
  useEffect(() => {
    if (!domainId) return;
    let cancelled = false;
    (async () => {
      try {
        const res = await fetchWithRetry(`${API_BASE}/learning/knowledge-gaps/${domainId}?limit=5`, { retries: 1 });
        if (res.ok && !cancelled) {
          const data = await res.json();
          setGaps(data.gaps || []);
        }
      } catch { /* offline */ }
    })();
    return () => { cancelled = true; };
  }, [domainId]);

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
  const pathGroups: PathGroup[] = useMemo(() => {
    if (!graphData?.nodes?.length) return [];
    const nodes = graphData.nodes as Array<{ id: string; label: string; group?: string; is_milestone?: boolean }>;
    const edges = (graphData.edges || []) as Array<{ source: string; target: string }>;

    const inDegree = new Map<string, number>();
    const adj = new Map<string, string[]>();
    for (const n of nodes) { inDegree.set(n.id, 0); adj.set(n.id, []); }
    for (const e of edges) { adj.get(e.source)?.push(e.target); inDegree.set(e.target, (inDegree.get(e.target) || 0) + 1); }

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
    for (const n of nodes) { if (!sorted.includes(n.id)) sorted.push(n.id); }

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
        id: c.id, label: c.label, isMilestone: c.is_milestone || false,
        status: (domainProgress[c.id]?.status as string) || 'not_started',
        mastery: domainProgress[c.id]?.mastery_score || 0,
      })),
    }));
  }, [graphData, domainProgress]);

  const totalConcepts = pathGroups.reduce((s, g) => s + g.concepts.length, 0);
  const masteredCount = pathGroups.reduce((s, g) => s + g.concepts.filter((c) => c.status === 'mastered').length, 0);
  const learningCount = pathGroups.reduce((s, g) => s + g.concepts.filter((c) => c.status === 'learning').length, 0);

  const nextRecommended = useMemo(() => {
    for (const group of pathGroups) { for (const c of group.concepts) { if (c.status !== 'mastered') return c.id; } }
    return null;
  }, [pathGroups]);

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      <header className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <button onClick={() => navigate(domainId ? `/domain/${domainId}` : '/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
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
          {[
            { label: '已掌握', value: masteredCount, color: '#22c55e' },
            { label: '学习中', value: learningCount, color: '#3b82f6' },
            { label: '未开始', value: totalConcepts - masteredCount - learningCount, color: undefined },
          ].map(({ label, value, color }) => (
            <div key={label} className="rounded-xl p-3 text-center" style={{ backgroundColor: 'var(--color-surface-1)' }}>
              <div className="text-2xl font-bold" style={color ? { color } : undefined}>{value}</div>
              <div className="text-xs opacity-60">{label}</div>
            </div>
          ))}
        </div>

        {/* Overall progress bar */}
        <div className="rounded-xl p-4" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <div className="flex justify-between text-sm mb-2">
            <span>总进度</span>
            <span className="font-bold">{totalConcepts > 0 ? Math.round((masteredCount / totalConcepts) * 100) : 0}%</span>
          </div>
          <div className="w-full h-3 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-3)' }}>
            <div className="h-full rounded-full transition-all duration-500"
              style={{ width: `${totalConcepts > 0 ? (masteredCount / totalConcepts) * 100 : 0}%`, backgroundColor: domain?.color || '#3b82f6' }} />
          </div>
        </div>

        <KnowledgeGapsSection gaps={gaps} domainId={domainId} />

        {pathGroups.map((group) => (
          <PathGroupSection
            key={group.name}
            group={group}
            isExpanded={expandedGroup === group.name || expandedGroup === null}
            domainId={domainId}
            domainColor={domain?.color}
            nextRecommended={nextRecommended}
            onToggle={() => setExpandedGroup(
              (expandedGroup === group.name || expandedGroup === null) && expandedGroup !== null ? null : group.name
            )}
          />
        ))}

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
