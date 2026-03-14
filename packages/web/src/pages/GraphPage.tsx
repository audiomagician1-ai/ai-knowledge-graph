import { useEffect, useState, useCallback, lazy, Suspense, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useIsDesktop } from '@/lib/hooks/useMediaQuery';
import { apiFetchRecommendations } from '@/lib/api/learning-api';
import type { GraphNode, GraphData } from '@akg/shared';
import { GRAPH_VISUAL } from '@akg/shared';
import { ChatPanel } from '@/components/chat/ChatPanel';
import {
  Search, X, Star, ChevronRight, Clock, BookOpen, Zap,
  Filter, Trophy, Loader, Compass,
  BarChart3, Settings, Network,
} from 'lucide-react';

const KnowledgeGraph = lazy(() =>
  import('@/components/graph/KnowledgeGraph').then((m) => ({ default: m.KnowledgeGraph }))
);

const SUBDOMAIN_COLORS = GRAPH_VISUAL.SUBDOMAIN_COLORS;

export function GraphPage() {
  const navigate = useNavigate();
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

  const totalNodes = graphData?.nodes.length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;
  const learningCount = Object.values(progress).filter(p => p.status === 'learning').length;
  const progressPct = totalNodes > 0 ? Math.round((masteredCount / totalNodes) * 100) : 0;

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
    <div className="relative h-full w-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>

      {/* ===== 3D Graph Canvas — Full Screen ===== */}
      <div className="absolute inset-0">
        {loading ? (
          <div className="flex items-center justify-center h-full animate-fade-in">
            <div className="flex flex-col items-center gap-4">
              <Loader size={36} className="animate-spin" style={{ color: 'var(--color-accent-primary)' }} />
              <p className="text-lg font-medium" style={{ color: 'var(--color-text-tertiary)' }}>加载知识图谱...</p>
            </div>
          </div>
        ) : !enrichedGraphData || enrichedGraphData.nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full animate-fade-in">
            <div className="text-center max-w-md">
              <Network size={48} className="mx-auto mb-4" style={{ color: 'var(--color-accent-primary)' }} />
              <h2 className="text-2xl font-bold mb-3">知识图谱</h2>
              <p className="text-lg" style={{ color: 'var(--color-text-tertiary)' }}>请确保后端服务已启动。</p>
            </div>
          </div>
        ) : (
          <Suspense
            fallback={
              <div className="flex items-center justify-center h-full animate-fade-in">
                <Loader size={32} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} />
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

      {/* ===== TOP-LEFT: Brand + Navigation ===== */}
      <div className="absolute top-6 left-6 z-20 pointer-events-auto">
        <div className="floating-panel flex items-center gap-2 p-2">
          {/* Brand */}
          <div className="flex items-center gap-3 pl-3 pr-4">
            <div
              className="w-8 h-8 rounded-md flex items-center justify-center shrink-0"
              style={{ backgroundColor: 'var(--color-accent-primary)' }}
            >
              <BookOpen size={15} style={{ color: '#111110' }} />
            </div>
            <span className="text-sm font-medium whitespace-nowrap" style={{ fontFamily: '"Noto Serif SC", Georgia, serif', color: 'var(--color-text-primary)' }}>知识图谱</span>
          </div>
          {/* Divider */}
          <div className="w-px h-8 shrink-0" style={{ backgroundColor: 'var(--color-border)' }} />
          {/* Nav Pills */}
          {[
            { icon: Network, label: '图谱', path: '/graph', active: true },
            { icon: BarChart3, label: '进度', path: '/dashboard', active: false },
            { icon: Settings, label: '设置', path: '/settings', active: false },
          ].map(({ icon: Icon, label, path, active }) => (
            <button
              key={path}
              onClick={() => navigate(path)}
              className="flex items-center gap-1.5 px-3 py-2 rounded-md transition-all text-sm font-medium whitespace-nowrap"
              style={{
                backgroundColor: active ? 'var(--color-surface-3)' : 'transparent',
                color: active ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)',
              }}
              onMouseEnter={(e) => { if (!active) e.currentTarget.style.backgroundColor = 'var(--color-surface-2)'; }}
              onMouseLeave={(e) => { if (!active) e.currentTarget.style.backgroundColor = 'transparent'; }}
            >
              <Icon size={16} />
              <span>{label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* ===== TOP-RIGHT: Search + Filter ===== */}
      <div className="absolute top-6 right-6 z-20 flex items-center gap-2 pointer-events-auto">
        {/* Search Bar */}
        <div className="relative">
          <div className="floating-panel flex items-center gap-2 px-3" style={{ height: 40, minWidth: isDesktop ? 260 : 200 }}>
            <Search size={16} style={{ color: 'var(--color-text-tertiary)', flexShrink: 0 }} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="搜索知识节点..."
              className="flex-1 bg-transparent text-sm outline-none"
              style={{ color: 'var(--color-text-primary)', border: 'none' }}
            />
            {searchQuery && (
              <button onClick={() => setSearchQuery('')} className="shrink-0 p-1.5 rounded-md hover:bg-white/5">
                <X size={14} style={{ color: 'var(--color-text-tertiary)' }} />
              </button>
            )}
          </div>

          {/* Search Results Dropdown */}
          {searchResults.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-2 floating-panel p-1 animate-fade-in-scale" style={{ maxHeight: 360, overflowY: 'auto' }}>
              {searchResults.map((node) => (
                <button
                  key={node.id}
                  onClick={() => { selectNode(node); setSearchQuery(''); }}
                  className="w-full text-left flex items-center gap-2.5 px-3 py-2 rounded-md transition-colors text-sm"
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  {node.is_milestone && <Star size={14} fill="var(--color-accent-amber)" style={{ color: 'var(--color-accent-amber)' }} />}
                  <span className="flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{node.label}</span>
                  <ChevronRight size={14} style={{ color: 'var(--color-text-tertiary)' }} />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Filter Toggle */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="floating-panel flex items-center gap-1.5 px-3"
          style={{ height: 44, color: showFilters ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)' }}
        >
          <Filter size={16} />
          <span className="text-sm font-medium">筛选</span>
        </button>
      </div>

      {/* ===== Subdomain Filter Tabs ===== */}
      {showFilters && subdomains.length > 0 && (
        <div className="absolute top-16 right-6 z-20 pointer-events-auto animate-fade-in">
          <div className="floating-panel p-2 flex flex-wrap gap-1" style={{ maxWidth: isDesktop ? 480 : 320 }}>
            <button
              onClick={() => setActiveSubdomain(null)}
              className="rounded-lg px-3 py-2 text-sm font-medium transition-all"
              style={{
                backgroundColor: !activeSubdomain ? 'var(--color-accent-primary)' : 'transparent',
                color: !activeSubdomain ? '#08090d' : 'var(--color-text-secondary)',
              }}
            >全部</button>
            {subdomains.map((sd) => {
              const isActive = activeSubdomain === sd.id;
              const sdColor = SUBDOMAIN_COLORS[sd.id] || 'var(--color-accent-primary)';
              return (
                <button
                  key={sd.id}
                  onClick={() => setActiveSubdomain(isActive ? null : sd.id)}
                  className="rounded-md px-3 py-1.5 text-sm font-medium transition-all flex items-center gap-1.5"
                  style={{
                    backgroundColor: isActive ? sdColor : 'transparent',
                    color: isActive ? '#fff' : 'var(--color-text-secondary)',
                  }}
                >
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: sdColor, opacity: isActive ? 0 : 0.8 }} />
                  {sd.name}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* ===== BOTTOM-LEFT: Compact Progress + Legend ===== */}
      <div className="absolute bottom-6 left-6 z-20 pointer-events-auto" style={{ maxWidth: 260 }}>
        <div className="floating-panel p-4">
          {/* Progress */}
          {totalNodes > 0 && (
            <>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold" style={{ color: 'var(--color-text-secondary)' }}>学习进度</span>
                <span className="text-xs font-bold font-mono" style={{ color: 'var(--color-accent-primary)' }}>{progressPct}%</span>
              </div>
              <div className="h-1.5 rounded-full overflow-hidden mb-3" style={{ backgroundColor: 'var(--color-surface-4)' }}>
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${progressPct}%`, backgroundColor: 'var(--color-accent-emerald)', minWidth: progressPct > 0 ? 4 : 0 }}
                />
              </div>
              <div className="flex items-center gap-3 text-xs mb-3" style={{ color: 'var(--color-text-tertiary)' }}>
                <span><b style={{ color: 'var(--color-accent-emerald)' }}>{masteredCount}</b> 掌握</span>
                <span><b style={{ color: 'var(--color-accent-amber)' }}>{learningCount}</b> 学习中</span>
                <span>共 {totalNodes}</span>
              </div>
            </>
          )}
          {/* Legend */}
          <div className="flex flex-wrap gap-x-3 gap-y-1">
            {[
              { label: '里程碑', color: 'var(--color-accent-amber)' },
              { label: '推荐', color: 'var(--color-accent-cyan)' },
              { label: '学习中', color: 'var(--color-accent-primary)' },
              { label: '已掌握', color: 'var(--color-accent-emerald)' },
            ].map(({ label, color }) => (
              <span key={label} className="flex items-center gap-1">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
                <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>{label}</span>
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* ===== BOTTOM-RIGHT: AI Recommend ===== */}
      {!selectedNode && (
        <div className="absolute bottom-6 right-6 z-20 flex flex-col items-end gap-2 pointer-events-auto">
          {/* Recommendation Panel */}
          {showRecommend && (
              <div className="floating-panel overflow-hidden animate-fade-in-scale" style={{ width: isDesktop ? 360 : 290 }}>
              <div className="px-4 py-3 flex items-center justify-between" style={{ borderBottom: '1px solid var(--color-border)' }}>
                <div className="flex items-center gap-2">
                  <Compass size={16} style={{ color: 'var(--color-accent-primary)' }} />
                  <span className="text-sm font-bold">推荐学习路径</span>
                </div>
                <button onClick={() => setShowRecommend(false)} className="p-1.5 rounded-lg hover:bg-white/5" style={{ color: 'var(--color-text-tertiary)' }}>
                  <X size={14} />
                </button>
              </div>
              <div className="max-h-[360px] overflow-y-auto">
                {recommendLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader size={20} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} />
                  </div>
                ) : recommendations.length === 0 ? (
                  <div className="text-center py-8 px-4">
                    <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>暂无推荐</p>
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
                        className="w-full text-left px-4 py-3 flex items-start gap-3 transition-colors"
                        style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
                        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
                        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                      >
                        <div className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium"
                          style={{ backgroundColor: 'var(--color-accent-primary)', color: '#111110' }}>
                          {idx + 1}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            {rec.is_milestone && <Star size={12} fill="var(--color-accent-amber)" style={{ color: 'var(--color-accent-amber)' }} />}
                            <span className="text-sm font-semibold truncate">{rec.name}</span>
                          </div>
                          <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                            <span className="font-semibold" style={{ color: diff.color }}>Lv.{rec.difficulty}</span>
                            <span>{rec.estimated_minutes}min</span>
                          </div>
                        </div>
                        <ChevronRight size={14} className="shrink-0 mt-1" style={{ color: 'var(--color-text-tertiary)' }} />
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
            className="btn-primary flex items-center gap-2 px-4 py-2.5 rounded-md text-sm font-medium"
          >
            <Compass size={16} />
            推荐学习
          </button>
        </div>
      )}

      {/* ===== RIGHT PANEL: Node Detail + Chat ===== */}
      {selectedNode && (
        <div
          className={`z-20 animate-slide-in-right ${
            isDesktop
              ? 'absolute top-4 right-4 bottom-4 w-[460px]'
              : 'fixed inset-0'
          }`}
        >
          <div className="h-full flex flex-col overflow-hidden" style={{
            backgroundColor: 'var(--color-surface-1)',
            border: '1px solid var(--color-border)',
            borderRadius: 8,
            boxShadow: '0 2px 12px rgba(0,0,0,0.3)',
          }}>
            {/* Panel Header */}
            <div className="px-5 py-4 shrink-0" style={{ borderBottom: '1px solid var(--color-border)' }}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    {selectedNode.is_milestone && <Star size={16} fill="var(--color-accent-amber)" style={{ color: 'var(--color-accent-amber)' }} />}
                    <h3 className="text-base font-bold truncate">{selectedNode.label}</h3>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    {(() => {
                      const diff = difficultyLabel(selectedNode.difficulty);
                      return (
                        <span className="inline-flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-semibold"
                          style={{ backgroundColor: diff.color + '18', color: diff.color }}>
                          Lv.{selectedNode.difficulty} {diff.text}
                        </span>
                      );
                    })()}
                    {selectedNode.estimated_minutes && (
                      <span className="inline-flex items-center gap-1.5 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
                        <Clock size={12} /> {selectedNode.estimated_minutes}min
                      </span>
                    )}
                    {progress[selectedNode.id]?.status === 'mastered' ? (
                      <span className="inline-flex items-center gap-1 text-xs font-bold" style={{ color: 'var(--color-accent-emerald)' }}>
                        <Trophy size={12} /> 已掌握
                      </span>
                    ) : progress[selectedNode.id]?.status === 'learning' ? (
                      <span className="inline-flex items-center gap-1 text-xs font-bold" style={{ color: 'var(--color-accent-primary)' }}>
                        <BookOpen size={12} /> 学习中
                      </span>
                    ) : selectedNode.is_recommended ? (
                      <span className="inline-flex items-center gap-1 text-xs font-bold" style={{ color: 'var(--color-accent-cyan)' }}>
                        <Zap size={12} /> 推荐
                      </span>
                    ) : null}
                  </div>
                </div>
                <button
                  onClick={() => selectNode(null)}
                  className="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg transition-colors"
                  style={{ color: 'var(--color-text-secondary)' }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  <X size={16} />
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
    </div>
  );
}
