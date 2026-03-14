import { useEffect, useState, useCallback, lazy, Suspense, useMemo } from 'react';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useIsDesktop } from '@/lib/hooks/useMediaQuery';
import { apiFetchRecommendations } from '@/lib/api/learning-api';
import type { GraphNode, GraphData } from '@akg/shared';
import { GRAPH_VISUAL } from '@akg/shared';
import { ChatPanel } from '@/components/chat/ChatPanel';
import {
  Search, X, Star, ChevronRight, Clock, BookOpen, Zap,
  Filter, Trophy, Loader, Compass, Sparkles,
} from 'lucide-react';

const KnowledgeGraph = lazy(() =>
  import('@/components/graph/KnowledgeGraph').then((m) => ({ default: m.KnowledgeGraph }))
);

const SUBDOMAIN_COLORS = GRAPH_VISUAL.SUBDOMAIN_COLORS;

export function GraphPage() {
  const {
    graphData, loading, selectedNode, activeSubdomain,
    setGraphData, selectNode, setActiveSubdomain, setLoading, setError,
  } = useGraphStore();
  const { progress, computeStats, refreshStreak, initEdges, recommendedIds, syncWithBackend, backendSynced } = useLearningStore();
  const isDesktop = useIsDesktop();
  const [subdomains, setSubdomains] = useState<Array<{ id: string; name: string; concept_count: number }>>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [showRecommend, setShowRecommend] = useState(false);
  const [recommendations, setRecommendations] = useState<Array<{
    concept_id: string; name: string; difficulty: number;
    estimated_minutes: number; is_milestone: boolean; score: number; reason: string; status: string;
  }>>([]);
  const [recommendLoading, setRecommendLoading] = useState(false);

  const loadRecommendations = useCallback(async () => {
    setRecommendLoading(true);
    const data = await apiFetchRecommendations(5);
    if (data) setRecommendations(data.recommendations);
    setRecommendLoading(false);
  }, []);

  const enrichedGraphData = useMemo<GraphData | null>(() => {
    if (!graphData) return null;
    return {
      ...graphData,
      nodes: graphData.nodes.map((n) => {
        const p = progress[n.id];
        const isRecommended = recommendedIds.has(n.id);
        return { ...n, status: p ? p.status : n.status, is_recommended: isRecommended };
      }),
    };
  }, [graphData, progress, recommendedIds]);

  useEffect(() => {
    if (graphData) {
      refreshStreak();
      computeStats(graphData.nodes.length);
      const prereqEdges = graphData.edges
        .filter((e) => e.relation_type === 'prerequisite')
        .map((e) => ({ source: e.source, target: e.target }));
      initEdges(prereqEdges);
    }
  }, [graphData]);

  useEffect(() => { if (graphData) computeStats(graphData.nodes.length); }, [progress]);

  // Sync with backend on first load
  useEffect(() => { if (!backendSynced) syncWithBackend(); }, [backendSynced]);

  useEffect(() => { loadGraph(); loadSubdomains(); }, []);

  const loadGraph = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/graph/data');
      if (!res.ok) throw new Error('Failed to fetch graph');
      setGraphData(await res.json());
    } catch (err) { setError(err instanceof Error ? err.message : 'Unknown error'); }
  };

  const loadSubdomains = async () => {
    try {
      const res = await fetch('/api/graph/subdomains');
      if (res.ok) setSubdomains(await res.json());
    } catch { /* ignore */ }
  };

  const handleNodeClick = (node: GraphNode) => selectNode(node?.id ? node : null);

  const difficultyLabel = (d: number) => {
    if (d <= 3) return { text: '入门', color: 'var(--color-accent-emerald)' };
    if (d <= 6) return { text: '进阶', color: 'var(--color-accent-amber)' };
    return { text: '高级', color: 'var(--color-accent-rose)' };
  };

  const searchResults = useMemo(() => {
    if (!searchQuery.trim() || !enrichedGraphData) return [];
    const q = searchQuery.toLowerCase();
    return enrichedGraphData.nodes
      .filter((n) => n.label.toLowerCase().includes(q) || n.id.toLowerCase().includes(q))
      .slice(0, 8);
  }, [searchQuery, enrichedGraphData]);

  return (
    <div className="relative flex h-full w-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>

      {/* ── 3D Graph Canvas ── */}
      <div className="absolute inset-0">
        {loading ? (
          <div className="flex items-center justify-center h-full animate-fade-in">
            <div className="flex flex-col items-center gap-3">
              <Loader size={24} className="animate-spin" style={{ color: 'var(--color-accent-primary)' }} />
              <p className="text-[13px]" style={{ color: 'var(--color-text-tertiary)' }}>加载知识图谱...</p>
            </div>
          </div>
        ) : !enrichedGraphData || enrichedGraphData.nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full animate-fade-in">
            <div className="text-center max-w-sm">
              <h2 className="text-lg font-semibold mb-2">知识图谱</h2>
              <p className="text-[13px]" style={{ color: 'var(--color-text-tertiary)' }}>
                请确保后端服务已启动。
              </p>
            </div>
          </div>
        ) : (
          <Suspense
            fallback={
              <div className="flex items-center justify-center h-full animate-fade-in">
                <Loader size={24} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} />
              </div>
            }
          >
            <KnowledgeGraph
              data={enrichedGraphData!}
              onNodeClick={handleNodeClick}
              selectedNodeId={selectedNode?.id}
              activeSubdomain={activeSubdomain}
            />
          </Suspense>
        )}
      </div>

      {/* ── Top bar ── */}
      <div className="absolute top-0 left-0 right-0 z-10 pointer-events-none">
        <div className="flex items-center gap-2 p-3 pointer-events-auto">
          {/* Search */}
          <div className="relative flex-1 max-w-sm">
            <div className="glass-heavy flex items-center gap-2 rounded-lg px-3 h-9">
              <Search size={14} style={{ color: 'var(--color-text-tertiary)', flexShrink: 0 }} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索..."
                className="flex-1 bg-transparent text-[13px] outline-none"
                style={{ color: 'var(--color-text-primary)' }}
              />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')} className="shrink-0">
                  <X size={13} style={{ color: 'var(--color-text-tertiary)' }} />
                </button>
              )}
            </div>
            {searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 glass-heavy rounded-lg overflow-hidden animate-fade-in-scale" style={{ maxHeight: 280, overflowY: 'auto' }}>
                {searchResults.map((node) => (
                  <button
                    key={node.id}
                    onClick={() => { selectNode(node); setSearchQuery(''); }}
                    className="w-full text-left flex items-center gap-2.5 px-3 py-2 transition-colors text-[13px]"
                    style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    {node.is_milestone && <Star size={12} fill="var(--color-accent-amber)" style={{ color: 'var(--color-accent-amber)' }} />}
                    <span className="flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{node.label}</span>
                    <ChevronRight size={12} style={{ color: 'var(--color-text-tertiary)' }} />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Filter toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="glass-heavy flex items-center gap-1.5 rounded-lg px-3 h-9 transition-all"
            style={{ color: showFilters ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)' }}
          >
            <Filter size={13} />
            <span className="text-[12px] font-medium">筛选</span>
          </button>
        </div>

        {/* Subdomain tabs */}
        {showFilters && subdomains.length > 0 && (
          <div className="px-3 pb-2 pointer-events-auto animate-fade-in">
            <div className="glass-heavy rounded-lg p-1.5 flex gap-1 overflow-x-auto no-scrollbar">
              <button
                onClick={() => setActiveSubdomain(null)}
                className="shrink-0 rounded-md px-2.5 py-1.5 text-[12px] font-medium transition-all"
                style={{
                  backgroundColor: !activeSubdomain ? 'var(--color-accent-primary)' : 'transparent',
                  color: !activeSubdomain ? '#0a0c10' : 'var(--color-text-tertiary)',
                }}
              >全部</button>
              {subdomains.map((sd) => {
                const isActive = activeSubdomain === sd.id;
                const sdColor = SUBDOMAIN_COLORS[sd.id] || 'var(--color-accent-primary)';
                return (
                  <button
                    key={sd.id}
                    onClick={() => setActiveSubdomain(isActive ? null : sd.id)}
                    className="shrink-0 rounded-md px-2.5 py-1.5 text-[12px] font-medium transition-all flex items-center gap-1"
                    style={{
                      backgroundColor: isActive ? sdColor : 'transparent',
                      color: isActive ? '#fff' : 'var(--color-text-tertiary)',
                    }}
                  >
                    <span className="w-2 h-2 rounded-full" style={{ backgroundColor: sdColor, opacity: isActive ? 0 : 0.7 }} />
                    {sd.name}
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* ── Legend (bottom-left) ── */}
      <div className="absolute bottom-3 left-3 z-10">
        <div className="glass-heavy rounded-lg px-3 py-2 flex items-center gap-4">
          {[
            { label: '里程碑', color: 'var(--color-accent-amber)' },
            { label: '推荐', color: '#22d3ee' },
            { label: '学习中', color: '#f59e0b' },
            { label: '已掌握', color: 'var(--color-accent-emerald)' },
          ].map(({ label, color }) => (
            <span key={label} className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
              <span className="text-[11px]" style={{ color }}>{label}</span>
            </span>
          ))}
        </div>
      </div>

      {/* ── Right Panel ── */}
      {selectedNode && (
        <div
          className={`z-10 animate-slide-in-right ${
            isDesktop
              ? 'absolute top-2 right-2 bottom-2 w-[560px]'
              : 'fixed inset-0'
          }`}
        >
          <div className="glass-heavy rounded-xl h-full flex flex-col overflow-hidden">
            {/* Panel Header */}
            <div className="px-4 pt-4 pb-3 shrink-0" style={{ borderBottom: '1px solid var(--color-border)' }}>
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1.5 mb-1">
                    {selectedNode.is_milestone && <Star size={14} fill="var(--color-accent-amber)" style={{ color: 'var(--color-accent-amber)' }} />}
                    <h3 className="text-[15px] font-semibold truncate">{selectedNode.label}</h3>
                  </div>
                  <div className="flex items-center gap-1.5 flex-wrap">
                    {(() => {
                      const diff = difficultyLabel(selectedNode.difficulty);
                      return (
                        <span className="inline-flex items-center gap-1 rounded px-1.5 py-px text-[11px] font-medium"
                          style={{ backgroundColor: diff.color + '15', color: diff.color }}>
                          Lv.{selectedNode.difficulty} {diff.text}
                        </span>
                      );
                    })()}
                    {selectedNode.estimated_minutes && (
                      <span className="inline-flex items-center gap-1 text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>
                        <Clock size={10} /> {selectedNode.estimated_minutes}min
                      </span>
                    )}
                    {progress[selectedNode.id]?.status === 'mastered' ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium" style={{ color: 'var(--color-accent-emerald)' }}>
                        <Trophy size={10} /> 已掌握
                      </span>
                    ) : progress[selectedNode.id]?.status === 'learning' ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium" style={{ color: '#f59e0b' }}>
                        <BookOpen size={10} /> 学习中
                      </span>
                    ) : selectedNode.is_recommended ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium" style={{ color: '#22d3ee' }}>
                        <Zap size={10} /> 推荐
                      </span>
                    ) : null}
                  </div>
                </div>
                <button
                  onClick={() => selectNode(null)}
                  className="shrink-0 w-7 h-7 flex items-center justify-center rounded-md transition-colors"
                  style={{ color: 'var(--color-text-tertiary)' }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  <X size={14} />
                </button>
              </div>
            </div>

            {/* Chat Panel */}
            <div className="flex-1 min-h-0 overflow-hidden">
              <ChatPanel conceptId={selectedNode.id} conceptName={selectedNode.label} />
            </div>
          </div>
        </div>
      )}

      {/* ── Recommend Button + Panel (bottom-right, when no node selected) ── */}
      {!selectedNode && (
        <div className="absolute bottom-4 right-4 z-10 flex flex-col items-end gap-2">
          {/* Recommendation Panel */}
          {showRecommend && (
            <div className="glass-heavy rounded-xl overflow-hidden animate-fade-in-scale" style={{ width: isDesktop ? 340 : 300 }}>
              <div className="px-4 pt-3 pb-2 flex items-center justify-between" style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
                <div className="flex items-center gap-1.5">
                  <Compass size={14} style={{ color: 'var(--color-accent-primary)' }} />
                  <span className="text-[13px] font-semibold">推荐学习路径</span>
                </div>
                <button onClick={() => setShowRecommend(false)} className="p-1 rounded" style={{ color: 'var(--color-text-tertiary)' }}>
                  <X size={12} />
                </button>
              </div>
              <div className="max-h-[320px] overflow-y-auto">
                {recommendLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader size={16} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} />
                  </div>
                ) : recommendations.length === 0 ? (
                  <div className="text-center py-8 px-4">
                    <p className="text-[12px]" style={{ color: 'var(--color-text-tertiary)' }}>暂无推荐</p>
                  </div>
                ) : (
                  recommendations.map((rec, idx) => {
                    const diff = difficultyLabel(rec.difficulty);
                    return (
                      <button
                        key={rec.concept_id}
                        onClick={() => {
                          const node = enrichedGraphData?.nodes.find(n => n.id === rec.concept_id);
                          if (node) { selectNode(node); setShowRecommend(false); }
                        }}
                        className="w-full text-left px-4 py-2.5 flex items-start gap-3 transition-colors"
                        style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
                        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
                        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                      >
                        <div className="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold mt-0.5"
                          style={{ backgroundColor: 'var(--color-accent-primary)', color: '#0a0c10' }}>
                          {idx + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-1.5 mb-0.5">
                            {rec.is_milestone && <Star size={10} fill="var(--color-accent-amber)" style={{ color: 'var(--color-accent-amber)' }} />}
                            <span className="text-[13px] font-medium truncate">{rec.name}</span>
                          </div>
                          <div className="flex items-center gap-2 mb-0.5">
                            <span className="text-[10px] font-medium" style={{ color: diff.color }}>Lv.{rec.difficulty}</span>
                            <span className="text-[10px]" style={{ color: 'var(--color-text-tertiary)' }}>{rec.estimated_minutes}min</span>
                            {rec.status === 'learning' && (
                              <span className="text-[10px] font-medium" style={{ color: '#f59e0b' }}>进行中</span>
                            )}
                          </div>
                          <p className="text-[11px] leading-tight" style={{ color: 'var(--color-text-tertiary)' }}>{rec.reason}</p>
                        </div>
                        <ChevronRight size={12} className="shrink-0 mt-1" style={{ color: 'var(--color-text-tertiary)' }} />
                      </button>
                    );
                  })
                )}
              </div>
            </div>
          )}

          {/* Recommend Button */}
          <button
            onClick={() => {
              if (!showRecommend) { setShowRecommend(true); loadRecommendations(); }
              else setShowRecommend(false);
            }}
            className="btn-primary flex items-center gap-2 px-5 py-2.5 rounded-xl shadow-lg text-[13px] font-semibold transition-all hover:scale-105 active:scale-95"
          >
            <Sparkles size={15} />
            AI 推荐学习
          </button>
        </div>
      )}
    </div>
  );
}
