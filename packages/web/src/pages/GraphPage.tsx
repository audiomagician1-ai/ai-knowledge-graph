import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import type { GraphNode } from '@akg/shared';
import { GRAPH_VISUAL } from '@akg/shared';
import { KnowledgeGraph } from '@/components/graph/KnowledgeGraph';

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
  const [subdomains, setSubdomains] = useState<Array<{ id: string; name: string; concept_count: number }>>([]);
  const navigate = useNavigate();

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

  // Stats
  const milestoneCount = graphData?.nodes.filter(n => n.is_milestone).length || 0;

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
        {graphData && (
          <div className="flex items-center gap-3 text-xs" style={{ color: '#94a3b8' }}>
            <span>{graphData.nodes.length} 节点</span>
            <span>{graphData.edges.length} 连接</span>
            <span style={{ color: '#fbbf24' }}>⭐ {milestoneCount} 里程碑</span>
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
        ) : !graphData || graphData.nodes.length === 0 ? (
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
          <KnowledgeGraph
            data={graphData}
            onNodeClick={handleNodeClick}
            selectedNodeId={selectedNode?.id}
            activeSubdomain={activeSubdomain}
          />
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
