import { useEffect, useState, lazy, Suspense, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import type { GraphNode, GraphData } from '@akg/shared';
import { GRAPH_VISUAL } from '@akg/shared';

// Lazy-load Cytoscape.js graph component (~350KB) — only loaded when graph data ready
const KnowledgeGraph = lazy(() =>
  import('@/components/graph/KnowledgeGraph').then((m) => ({ default: m.KnowledgeGraph }))
);

const SUBDOMAIN_COLORS = GRAPH_VISUAL.SUBDOMAIN_COLORS;

/**
 * 图谱页面 — 知识宇宙主视图
 * Cytoscape.js 力导向图谱 + 里程碑高亮 + 子域筛选 + 详情面板
 */
export function GraphPage() {
  const {
    graphData, loading, selectedNode, activeSubdomain,
    setGraphData, selectNode, setActiveSubdomain, setLoading, setError,
  } = useGraphStore();
  const { progress, computeStats, refreshStreak } = useLearningStore();
  const [subdomains, setSubdomains] = useState<Array<{ id: string; name: string; concept_count: number }>>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  // Merge learning progress into graph node statuses
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

  // Compute stats when graph loads or progress changes
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

  const handleSubdomainFilter = (sdId: string | null) => {
    setActiveSubdomain(sdId);
  };

  const difficultyLabel = (d: number) => {
    if (d <= 3) return { text: '入门', color: '#4ade80' };
    if (d <= 6) return { text: '进阶', color: '#facc15' };
    if (d <= 9) return { text: '高级', color: '#f97316' };
    return { text: '专家', color: '#ef4444' };
  };

  // Search filter
  const searchResults = useMemo(() => {
    if (!searchQuery.trim() || !enrichedGraphData) return [];
    const q = searchQuery.toLowerCase();
    return enrichedGraphData.nodes
      .filter((n) => n.label.toLowerCase().includes(q) || n.id.toLowerCase().includes(q))
      .slice(0, 8);
  }, [searchQuery, enrichedGraphData]);

  // Stats
  const milestoneCount = enrichedGraphData?.nodes.filter(n => n.is_milestone).length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;
  const learningCount = Object.values(progress).filter(p => p.status === 'learning').length;

  return (
    <div className="flex h-full flex-col" style={{ backgroundColor: '#0f172a' }}>
      {/* Header */}
      <header
        className="flex items-center justify-between px-4 shrink-0"
        style={{
          height: '48px',
          paddingTop: 'var(--safe-area-top)',
          backgroundColor: '#1e293b',
          borderBottom: '1px solid #334155',
        }}
      >
        <h1 className="text-base font-bold" style={{ color: '#f1f5f9' }}>
          🧠 AI知识图谱
        </h1>
        {enrichedGraphData && (
          <div className="flex items-center gap-3 text-xs" style={{ color: '#94a3b8' }}>
            <span>{enrichedGraphData.nodes.length} 节点</span>
            {masteredCount > 0 && <span style={{ color: '#10b981' }}>✓ {masteredCount}</span>}
            {learningCount > 0 && <span style={{ color: '#f59e0b' }}>◉ {learningCount}</span>}
            <span style={{ color: '#fbbf24' }}>⭐ {milestoneCount}</span>
          </div>
        )}
      </header>

      {/* Subdomain filter tabs */}
      {subdomains.length > 0 && (
        <div
          className="flex gap-1.5 overflow-x-auto px-3 py-2 no-scrollbar shrink-0"
          style={{ backgroundColor: '#1e293b' }}
        >
          <button
            onClick={() => handleSubdomainFilter(null)}
            className="shrink-0 rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors"
            style={{
              backgroundColor: !activeSubdomain ? '#6366f1' : '#334155',
              color: !activeSubdomain ? '#fff' : '#94a3b8',
            }}
          >
            全部
          </button>
          {subdomains.map((sd) => (
            <button
              key={sd.id}
              onClick={() => handleSubdomainFilter(sd.id)}
              className="shrink-0 rounded-full px-2.5 py-1 text-[11px] font-medium transition-colors"
              style={{
                backgroundColor: activeSubdomain === sd.id
                  ? (SUBDOMAIN_COLORS[sd.id] || '#6366f1')
                  : '#334155',
                color: activeSubdomain === sd.id ? '#fff' : '#94a3b8',
              }}
            >
              {sd.name} ({sd.concept_count})
            </button>
          ))}
        </div>
      )}

      {/* Search bar */}
      <div className="relative px-3 py-2 shrink-0" style={{ backgroundColor: '#1e293b' }}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="🔍 搜索概念..."
          className="w-full rounded-lg px-3 py-2 text-xs outline-none"
          style={{
            backgroundColor: '#0f172a',
            color: '#f1f5f9',
            border: '1px solid #334155',
          }}
        />
        {searchResults.length > 0 && (
          <div
            className="absolute left-3 right-3 mt-1 rounded-lg overflow-hidden z-50"
            style={{ backgroundColor: '#1e293b', border: '1px solid #334155', maxHeight: 240, overflowY: 'auto' }}
          >
            {searchResults.map((node) => (
              <button
                key={node.id}
                onClick={() => {
                  selectNode(node);
                  setSearchQuery('');
                }}
                className="w-full text-left px-3 py-2 text-xs flex items-center gap-2 hover:bg-[#334155] transition-colors"
                style={{ color: '#e2e8f0' }}
              >
                {node.is_milestone && <span>⭐</span>}
                <span className="flex-1 truncate">{node.label}</span>
                <span
                  className="shrink-0 text-[9px] rounded-full px-1.5 py-0.5"
                  style={{
                    backgroundColor: (SUBDOMAIN_COLORS[node.subdomain_id] || '#6366f1') + '30',
                    color: SUBDOMAIN_COLORS[node.subdomain_id] || '#6366f1',
                  }}
                >
                  {node.subdomain_id}
                </span>
                {progress[node.id]?.status === 'mastered' && (
                  <span className="text-[9px]" style={{ color: '#10b981' }}>✓</span>
                )}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Graph Canvas */}
      <div className="flex-1 relative">
        {loading ? (
          <div className="flex items-center justify-center h-full">
            <div className="flex flex-col items-center gap-3">
              <div
                className="h-8 w-8 animate-spin rounded-full border-2 border-t-transparent"
                style={{ borderColor: '#8b5cf6', borderTopColor: 'transparent' }}
              />
              <span style={{ color: '#94a3b8' }}>加载知识宇宙...</span>
            </div>
          </div>
        ) : !enrichedGraphData || enrichedGraphData.nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full text-center">
            <div>
              <div className="text-6xl mb-4">🧠</div>
              <h2 className="text-xl font-bold mb-2" style={{ color: '#f1f5f9' }}>
                欢迎来到AI知识宇宙
              </h2>
              <p style={{ color: '#94a3b8' }}>
                请确保后端服务已启动 (FastAPI)
              </p>
            </div>
          </div>
        ) : (
          <Suspense
            fallback={
              <div className="flex items-center justify-center h-full">
                <div className="flex flex-col items-center gap-3">
                  <div
                    className="h-8 w-8 animate-spin rounded-full border-2 border-t-transparent"
                    style={{ borderColor: '#8b5cf6', borderTopColor: 'transparent' }}
                  />
                  <span style={{ color: '#94a3b8' }}>加载图谱引擎...</span>
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

        {/* Legend overlay */}
        <div
          className="absolute bottom-3 left-3 rounded-lg px-3 py-2 text-[10px]"
          style={{ backgroundColor: 'rgba(15, 23, 42, 0.85)', border: '1px solid #334155' }}
        >
          <div className="flex items-center gap-3 flex-wrap">
            <span style={{ color: '#94a3b8' }}>图例:</span>
            <span className="flex items-center gap-1">
              <span className="inline-block w-3 h-3 rounded-full" style={{ backgroundColor: '#fbbf24', border: '2px solid #f59e0b' }} />
              <span style={{ color: '#fde68a' }}>里程碑</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#94a3b8' }} />
              <span style={{ color: '#94a3b8' }}>未学习</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#f59e0b' }} />
              <span style={{ color: '#f59e0b' }}>学习中</span>
            </span>
            <span className="flex items-center gap-1">
              <span className="inline-block w-2.5 h-2.5 rounded-full" style={{ backgroundColor: '#10b981' }} />
              <span style={{ color: '#10b981' }}>已掌握</span>
            </span>
          </div>
        </div>
      </div>

      {/* Detail panel */}
      {selectedNode && (
        <div
          className="px-4 py-3 shrink-0"
          style={{
            backgroundColor: '#1e293b',
            borderTop: '1px solid #334155',
          }}
        >
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              {selectedNode.is_milestone && <span className="text-base">⭐</span>}
              <h3 className="text-base font-semibold" style={{ color: '#f1f5f9' }}>
                {selectedNode.label}
              </h3>
            </div>
            <button
              onClick={() => selectNode(null)}
              className="text-xs px-2 py-1 rounded"
              style={{ color: '#94a3b8' }}
            >
              ✕
            </button>
          </div>
          <div className="flex gap-3 mb-3 flex-wrap">
            {(() => {
              const diff = difficultyLabel(selectedNode.difficulty);
              return (
                <span
                  className="rounded-full px-2 py-0.5 text-[10px] font-medium"
                  style={{ backgroundColor: diff.color + '20', color: diff.color }}
                >
                  {diff.text} · 难度 {selectedNode.difficulty}/9
                </span>
              );
            })()}
            {selectedNode.estimated_minutes && (
              <span className="text-[10px]" style={{ color: '#94a3b8' }}>
                ⏱ {selectedNode.estimated_minutes}min
              </span>
            )}
            {selectedNode.content_type && (
              <span className="text-[10px]" style={{ color: '#94a3b8' }}>
                📖 {selectedNode.content_type}
              </span>
            )}
            {selectedNode.subdomain_id && (
              <span
                className="rounded-full px-1.5 py-0.5 text-[10px]"
                style={{
                  backgroundColor: (SUBDOMAIN_COLORS[selectedNode.subdomain_id] || '#6366f1') + '30',
                  color: SUBDOMAIN_COLORS[selectedNode.subdomain_id] || '#6366f1',
                }}
              >
                {selectedNode.subdomain_id}
              </span>
            )}
          </div>
          <button
            onClick={() => navigate(`/learn/${selectedNode.id}`)}
            className="w-full rounded-xl py-2.5 text-sm font-semibold transition-colors"
            style={{ backgroundColor: '#8b5cf6', color: '#fff' }}
          >
            开始学习 🎓
          </button>
        </div>
      )}
    </div>
  );
}
