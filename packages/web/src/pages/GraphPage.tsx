import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { fetchGraphData } from '@/lib/api/graph-api';
import type { GraphNode } from '@akg/shared';
import { GRAPH_VISUAL } from '@akg/shared';

/**
 * 图谱页面 — 知识宇宙主视图
 * Phase 0: 列表视图 + 子域筛选
 * Phase 1: Cytoscape.js 图谱可视化
 */
export function GraphPage() {
  const { graphData, loading, selectedNode, setGraphData, selectNode, setLoading, setError } = useGraphStore();
  const [activeSubdomain, setActiveSubdomain] = useState<string | null>(null);
  const [subdomains, setSubdomains] = useState<Array<{ id: string; name: string; concept_count: number }>>([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadGraph();
    loadSubdomains();
  }, []);

  const loadGraph = async (subdomainId?: string) => {
    setLoading(true);
    try {
      const url = subdomainId
        ? `/api/graph/data?subdomain_id=${subdomainId}`
        : '/api/graph/data';
      const res = await fetch(url);
      if (!res.ok) throw new Error('获取图谱失败');
      const data = await res.json();
      setGraphData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    }
  };

  const loadSubdomains = async () => {
    try {
      const res = await fetch('/api/graph/subdomains');
      if (res.ok) setSubdomains(await res.json());
    } catch { /* ignore */ }
  };

  const handleSubdomainFilter = (sdId: string | null) => {
    setActiveSubdomain(sdId);
    loadGraph(sdId ?? undefined);
  };

  const handleNodeClick = (node: GraphNode) => {
    selectNode(node);
  };

  const nodeColor = (status: string) =>
    GRAPH_VISUAL.NODE_COLORS[status as keyof typeof GRAPH_VISUAL.NODE_COLORS] ?? GRAPH_VISUAL.NODE_COLORS.available;

  const difficultyLabel = (d: number) => {
    if (d <= 3) return { text: '入门', color: '#4ade80' };
    if (d <= 6) return { text: '进阶', color: '#facc15' };
    if (d <= 9) return { text: '高级', color: '#f97316' };
    return { text: '专家', color: '#ef4444' };
  };

  return (
    <div className="flex h-full flex-col">
      {/* 顶部栏 */}
      <header
        className="flex items-center justify-between px-4"
        style={{
          height: 'var(--header-height)',
          paddingTop: 'var(--safe-area-top)',
          backgroundColor: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-default)',
        }}
      >
        <h1 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
          🌌 知识图谱
        </h1>
        {graphData && (
          <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
            {graphData.nodes.length} 节点 · {graphData.edges.length} 连接
          </span>
        )}
      </header>

      {/* 子域筛选 */}
      {subdomains.length > 0 && (
        <div
          className="flex gap-2 overflow-x-auto px-4 py-2 no-scrollbar"
          style={{ backgroundColor: 'var(--bg-secondary)' }}
        >
          <button
            onClick={() => handleSubdomainFilter(null)}
            className="shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition-colors"
            style={{
              backgroundColor: !activeSubdomain ? 'var(--color-primary)' : 'var(--bg-tertiary)',
              color: !activeSubdomain ? '#fff' : 'var(--text-secondary)',
            }}
          >
            全部
          </button>
          {subdomains.map((sd) => (
            <button
              key={sd.id}
              onClick={() => handleSubdomainFilter(sd.id)}
              className="shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition-colors"
              style={{
                backgroundColor: activeSubdomain === sd.id ? 'var(--color-primary)' : 'var(--bg-tertiary)',
                color: activeSubdomain === sd.id ? '#fff' : 'var(--text-secondary)',
              }}
            >
              {sd.name} ({sd.concept_count})
            </button>
          ))}
        </div>
      )}

      {/* 内容区域 */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="flex flex-col items-center gap-3">
              <div
                className="h-8 w-8 animate-spin rounded-full border-2 border-t-transparent"
                style={{ borderColor: 'var(--color-primary)', borderTopColor: 'transparent' }}
              />
              <span style={{ color: 'var(--text-secondary)' }}>加载知识宇宙中...</span>
            </div>
          </div>
        ) : !graphData || graphData.nodes.length === 0 ? (
          <div className="text-center py-20">
            <div className="text-6xl mb-4">🌌</div>
            <h2 className="text-xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
              欢迎来到知识宇宙
            </h2>
            <p style={{ color: 'var(--text-secondary)' }}>
              数据加载中，请确保后端服务已启动
            </p>
          </div>
        ) : (
          <div className="grid gap-3">
            {graphData.nodes.map((node) => {
              const diff = difficultyLabel(node.difficulty);
              return (
                <button
                  key={node.id}
                  onClick={() => handleNodeClick(node)}
                  className="flex items-center gap-3 rounded-xl p-3 text-left transition-colors active:scale-[0.98]"
                  style={{
                    backgroundColor: selectedNode?.id === node.id ? 'var(--bg-tertiary)' : 'var(--bg-card)',
                    border: `1px solid ${selectedNode?.id === node.id ? 'var(--border-accent)' : 'var(--border-default)'}`,
                  }}
                >
                  {/* 状态指示器 */}
                  <div
                    className="h-3 w-3 shrink-0 rounded-full"
                    style={{ backgroundColor: nodeColor(node.status) }}
                  />

                  {/* 信息 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium truncate" style={{ color: 'var(--text-primary)' }}>
                        {node.label}
                      </span>
                      <span
                        className="shrink-0 rounded-full px-1.5 py-0.5 text-[10px] font-medium"
                        style={{ backgroundColor: diff.color + '20', color: diff.color }}
                      >
                        {diff.text}
                      </span>
                    </div>
                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
                      难度 {node.difficulty}/10
                    </span>
                  </div>

                  {/* 箭头 */}
                  <span style={{ color: 'var(--text-muted)' }}>→</span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* 节点详情底部面板 */}
      {selectedNode && (
        <div
          className="px-4 py-4"
          style={{
            backgroundColor: 'var(--bg-secondary)',
            borderTop: '1px solid var(--border-default)',
          }}
        >
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-base font-semibold" style={{ color: 'var(--text-primary)' }}>
              {selectedNode.label}
            </h3>
            <button
              onClick={() => selectNode(null)}
              className="text-xs px-2 py-1 rounded"
              style={{ color: 'var(--text-muted)' }}
            >
              关闭
            </button>
          </div>
          <div className="flex gap-3 mb-3">
            <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              难度 {selectedNode.difficulty}/10
            </span>
            <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
              ID: {selectedNode.id}
            </span>
          </div>
          <button
            onClick={() => navigate(`/learn/${selectedNode.id}`)}
            className="w-full rounded-xl py-2.5 text-sm font-semibold"
            style={{ backgroundColor: 'var(--color-primary)', color: '#fff' }}
          >
            开始学习 🎓
          </button>
        </div>
      )}
    </div>
  );
}
