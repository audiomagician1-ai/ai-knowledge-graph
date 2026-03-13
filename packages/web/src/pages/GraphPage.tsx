import { useEffect, useState, lazy, Suspense, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import type { GraphNode, GraphData } from '@akg/shared';
import { GRAPH_VISUAL } from '@akg/shared';
import {
  Search, X, Star, ChevronRight, Clock, BookOpen, Zap,
  Layers, Filter, Compass,
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
  const { progress, computeStats, refreshStreak } = useLearningStore();
  const [subdomains, setSubdomains] = useState<Array<{ id: string; name: string; concept_count: number }>>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const navigate = useNavigate();

  const enrichedGraphData = useMemo<GraphData | null>(() => {
    if (!graphData) return null;
    return {
      ...graphData,
      nodes: graphData.nodes.map((n) => {
        const p = progress[n.id];
        return p ? { ...n, status: p.status } : n;
      }),
    };
  }, [graphData, progress]);

  useEffect(() => {
    if (graphData) {
      refreshStreak();
      computeStats(graphData.nodes.length);
    }
  }, [graphData, progress]);

  useEffect(() => {
    loadGraph();
    loadSubdomains();
  }, []);

  const loadGraph = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/graph/data');
      if (!res.ok) throw new Error('Failed to fetch graph');
      const data = await res.json();
      setGraphData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const loadSubdomains = async () => {
    try {
      const res = await fetch('/api/graph/subdomains');
      if (res.ok) setSubdomains(await res.json());
    } catch { /* ignore */ }
  };

  const handleNodeClick = (node: GraphNode) => {
    selectNode(node?.id ? node : null);
  };

  const difficultyLabel = (d: number) => {
    if (d <= 3) return { text: '入门', color: 'var(--color-accent-emerald)' };
    if (d <= 6) return { text: '进阶', color: 'var(--color-accent-amber)' };
    if (d <= 9) return { text: '高级', color: '#f97316' };
    return { text: '专家', color: 'var(--color-accent-rose)' };
  };

  const searchResults = useMemo(() => {
    if (!searchQuery.trim() || !enrichedGraphData) return [];
    const q = searchQuery.toLowerCase();
    return enrichedGraphData.nodes
      .filter((n) => n.label.toLowerCase().includes(q) || n.id.toLowerCase().includes(q))
      .slice(0, 8);
  }, [searchQuery, enrichedGraphData]);

  const milestoneCount = enrichedGraphData?.nodes.filter(n => n.is_milestone).length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;
  const learningCount = Object.values(progress).filter(p => p.status === 'learning').length;
  const totalNodes = enrichedGraphData?.nodes.length || 0;

  return (
    <div className="relative flex h-full w-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>

      {/* ── Graph Canvas (full area) ── */}
      <div className="absolute inset-0">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center gap-4 animate-fade-in">
              <div className="relative">
                <div
                  className="w-12 h-12 rounded-full animate-spin"
                  style={{
                    border: '2px solid var(--color-surface-3)',
                    borderTopColor: 'var(--color-accent-indigo)',
                  }}
                />
                <Compass
                  size={20}
                  className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2"
                  style={{ color: 'var(--color-accent-indigo)' }}
                />
              </div>
              <div className="text-center">
                <p className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                  正在构建知识图谱...
                </p>
                <p className="text-xs mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
                  Loading neural network
                </p>
              </div>
            </div>
          </div>
        ) : !enrichedGraphData || enrichedGraphData.nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center animate-fade-in max-w-md px-8">
              <div
                className="w-20 h-20 rounded-2xl mx-auto mb-6 flex items-center justify-center"
                style={{
                  background: 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
                  boxShadow: '0 8px 32px rgba(99, 102, 241, 0.3)',
                }}
              >
                <Compass size={36} className="text-white" />
              </div>
              <h2 className="text-xl font-bold mb-2" style={{ color: 'var(--color-text-primary)' }}>
                欢迎来到知识图谱
              </h2>
              <p className="text-sm leading-relaxed" style={{ color: 'var(--color-text-tertiary)' }}>
                请确保后端服务已启动。知识图谱将展示 267 个 AI 工程概念及其关联关系。
              </p>
            </div>
          </div>
        ) : (
          <Suspense
            fallback={
              <div className="flex items-center justify-center h-full">
                <div className="flex flex-col items-center gap-4 animate-fade-in">
                  <div
                    className="w-12 h-12 rounded-full animate-spin"
                    style={{
                      border: '2px solid var(--color-surface-3)',
                      borderTopColor: 'var(--color-accent-violet)',
                    }}
                  />
                  <p className="text-xs font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
                    Initializing Cytoscape...
                  </p>
                </div>
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

      {/* ── Top bar overlay ── */}
      <div className="absolute top-0 left-0 right-0 z-10 pointer-events-none">
        <div className="flex items-center gap-3 p-4 pointer-events-auto">

          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <div
              className="glass-heavy flex items-center gap-2.5 rounded-xl px-4 h-11"
            >
              <Search size={16} style={{ color: 'var(--color-text-tertiary)', flexShrink: 0 }} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="搜索概念节点..."
                className="flex-1 bg-transparent text-sm outline-none"
                style={{
                  color: 'var(--color-text-primary)',
                }}
              />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')} className="shrink-0">
                  <X size={14} style={{ color: 'var(--color-text-tertiary)' }} />
                </button>
              )}
            </div>

            {/* Search results dropdown */}
            {searchResults.length > 0 && (
              <div
                className="absolute top-full left-0 right-0 mt-2 glass-heavy rounded-xl overflow-hidden animate-fade-in-scale"
                style={{ maxHeight: 320, overflowY: 'auto' }}
              >
                {searchResults.map((node) => (
                  <button
                    key={node.id}
                    onClick={() => { selectNode(node); setSearchQuery(''); }}
                    className="w-full text-left flex items-center gap-3 px-4 py-3 transition-colors"
                    style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  >
                    {node.is_milestone && (
                      <Star size={14} fill="var(--color-accent-amber)" style={{ color: 'var(--color-accent-amber)', flexShrink: 0 }} />
                    )}
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>
                        {node.label}
                      </div>
                      <div className="text-[11px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
                        {node.subdomain_id}
                      </div>
                    </div>
                    <ChevronRight size={14} style={{ color: 'var(--color-text-tertiary)', flexShrink: 0 }} />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Filter toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="glass-heavy flex items-center gap-2 rounded-xl px-4 h-11 transition-all"
            style={{
              borderColor: showFilters ? 'var(--color-accent-indigo)' : undefined,
              color: showFilters ? 'var(--color-accent-indigo)' : 'var(--color-text-secondary)',
            }}
          >
            <Filter size={15} />
            <span className="text-sm font-medium">筛选</span>
          </button>

          {/* Stats pills */}
          <div className="hidden lg:flex items-center gap-2">
            <div className="glass-heavy rounded-xl px-4 h-11 flex items-center gap-3">
              <span className="flex items-center gap-1.5 text-xs font-mono">
                <Layers size={13} style={{ color: 'var(--color-accent-indigo)' }} />
                <span style={{ color: 'var(--color-text-secondary)' }}>{totalNodes}</span>
              </span>
              <span className="w-px h-4" style={{ backgroundColor: 'var(--color-border)' }} />
              <span className="flex items-center gap-1.5 text-xs font-mono">
                <Star size={13} style={{ color: 'var(--color-accent-amber)' }} />
                <span style={{ color: 'var(--color-text-secondary)' }}>{milestoneCount}</span>
              </span>
              {masteredCount > 0 && (
                <>
                  <span className="w-px h-4" style={{ backgroundColor: 'var(--color-border)' }} />
                  <span className="flex items-center gap-1.5 text-xs font-mono">
                    <Zap size={13} style={{ color: 'var(--color-accent-emerald)' }} />
                    <span style={{ color: 'var(--color-accent-emerald)' }}>{masteredCount}</span>
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Subdomain filter tabs */}
        {showFilters && subdomains.length > 0 && (
          <div className="px-4 pb-3 pointer-events-auto animate-fade-in">
            <div
              className="glass-heavy rounded-xl p-2 flex gap-1.5 overflow-x-auto no-scrollbar"
            >
              <button
                onClick={() => { setActiveSubdomain(null); }}
                className="shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium transition-all"
                style={{
                  backgroundColor: !activeSubdomain ? 'var(--color-accent-indigo)' : 'transparent',
                  color: !activeSubdomain ? '#fff' : 'var(--color-text-secondary)',
                }}
              >
                全部
              </button>
              {subdomains.map((sd) => {
                const isActive = activeSubdomain === sd.id;
                const sdColor = SUBDOMAIN_COLORS[sd.id] || 'var(--color-accent-indigo)';
                return (
                  <button
                    key={sd.id}
                    onClick={() => setActiveSubdomain(isActive ? null : sd.id)}
                    className="shrink-0 rounded-lg px-3 py-1.5 text-xs font-medium transition-all flex items-center gap-1.5"
                    style={{
                      backgroundColor: isActive ? sdColor : 'transparent',
                      color: isActive ? '#fff' : 'var(--color-text-secondary)',
                    }}
                  >
                    <span
                      className="w-2 h-2 rounded-full shrink-0"
                      style={{ backgroundColor: sdColor, opacity: isActive ? 0 : 1 }}
                    />
                    {sd.name}
                    <span className="font-mono opacity-60">{sd.concept_count}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* ── Legend (bottom-left) ── */}
      <div className="absolute bottom-4 left-4 z-10">
        <div className="glass-heavy rounded-xl px-4 py-3">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: 'var(--color-accent-amber)', border: '2px solid #f59e0b', boxShadow: '0 0 8px rgba(251, 191, 36, 0.4)' }} />
              <span className="text-[11px] font-medium" style={{ color: 'var(--color-accent-amber)' }}>里程碑</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: 'var(--color-text-tertiary)' }} />
              <span className="text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>未学习</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#f59e0b' }} />
              <span className="text-[11px]" style={{ color: '#f59e0b' }}>学习中</span>
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: 'var(--color-accent-emerald)' }} />
              <span className="text-[11px]" style={{ color: 'var(--color-accent-emerald)' }}>已掌握</span>
            </span>
          </div>
        </div>
      </div>

      {/* ── Detail Panel (right side) ── */}
      {selectedNode && (
        <div className="absolute top-4 right-4 bottom-4 z-10 w-[340px] animate-slide-in-right">
          <div className="glass-heavy rounded-2xl h-full flex flex-col overflow-hidden">
            {/* Panel header */}
            <div className="px-5 pt-5 pb-4" style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    {selectedNode.is_milestone && (
                      <Star size={16} fill="var(--color-accent-amber)" style={{ color: 'var(--color-accent-amber)' }} />
                    )}
                    <h3 className="text-base font-bold truncate" style={{ color: 'var(--color-text-primary)' }}>
                      {selectedNode.label}
                    </h3>
                  </div>
                  <div className="flex items-center gap-2 flex-wrap">
                    {(() => {
                      const diff = difficultyLabel(selectedNode.difficulty);
                      return (
                        <span
                          className="inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[11px] font-semibold font-mono"
                          style={{ backgroundColor: diff.color + '18', color: diff.color }}
                        >
                          {diff.text} Lv.{selectedNode.difficulty}
                        </span>
                      );
                    })()}
                    {selectedNode.estimated_minutes && (
                      <span className="inline-flex items-center gap-1 text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>
                        <Clock size={11} />
                        {selectedNode.estimated_minutes}min
                      </span>
                    )}
                    {selectedNode.content_type && (
                      <span className="inline-flex items-center gap-1 text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>
                        <BookOpen size={11} />
                        {selectedNode.content_type}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => selectNode(null)}
                  className="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg transition-colors"
                  style={{ color: 'var(--color-text-tertiary)' }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Panel body */}
            <div className="flex-1 px-5 py-4 overflow-y-auto">
              {/* Subdomain badge */}
              {selectedNode.subdomain_id && (
                <div className="mb-4">
                  <span
                    className="text-[10px] font-mono font-semibold uppercase tracking-wider"
                    style={{ color: 'var(--color-text-tertiary)' }}
                  >
                    Subdomain
                  </span>
                  <div className="mt-1.5">
                    <span
                      className="inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-medium"
                      style={{
                        backgroundColor: (SUBDOMAIN_COLORS[selectedNode.subdomain_id] || 'var(--color-accent-indigo)') + '15',
                        color: SUBDOMAIN_COLORS[selectedNode.subdomain_id] || 'var(--color-accent-indigo)',
                      }}
                    >
                      <span
                        className="w-2 h-2 rounded-full"
                        style={{ backgroundColor: SUBDOMAIN_COLORS[selectedNode.subdomain_id] || 'var(--color-accent-indigo)' }}
                      />
                      {selectedNode.subdomain_id.replace(/-/g, ' ')}
                    </span>
                  </div>
                </div>
              )}

              {/* Status */}
              {progress[selectedNode.id] && (
                <div className="mb-4">
                  <span
                    className="text-[10px] font-mono font-semibold uppercase tracking-wider"
                    style={{ color: 'var(--color-text-tertiary)' }}
                  >
                    Status
                  </span>
                  <div className="mt-1.5">
                    {progress[selectedNode.id].status === 'mastered' ? (
                      <span className="inline-flex items-center gap-1.5 text-xs font-semibold" style={{ color: 'var(--color-accent-emerald)' }}>
                        <Zap size={13} /> 已掌握
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 text-xs font-semibold" style={{ color: '#f59e0b' }}>
                        <BookOpen size={13} /> 学习中
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Action button */}
            <div className="px-5 pb-5">
              <button
                onClick={() => navigate(`/learn/${selectedNode.id}`)}
                className="btn-primary w-full flex items-center justify-center gap-2 py-3"
              >
                <Zap size={16} />
                <span>开始费曼学习</span>
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
