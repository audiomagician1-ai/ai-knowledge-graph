import { useEffect } from 'react';
import { useGraphStore } from '@/lib/store/graph';

/**
 * 图谱页面 — 知识宇宙主视图
 * TODO: Phase 1 实现 Cytoscape.js 图谱渲染
 */
export function GraphPage() {
  const { graphData, loading } = useGraphStore();

  useEffect(() => {
    // TODO: fetchGraphData 并 setGraphData
  }, []);

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
          知识图谱
        </h1>
        <div className="flex gap-2">
          {/* TODO: 搜索 + 筛选按钮 */}
        </div>
      </header>

      {/* 图谱区域 */}
      <div className="graph-container flex-1 relative" id="graph-viewport">
        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex flex-col items-center gap-3">
              <div
                className="h-8 w-8 animate-spin rounded-full border-2 border-t-transparent"
                style={{ borderColor: 'var(--color-primary)', borderTopColor: 'transparent' }}
              />
              <span style={{ color: 'var(--text-secondary)' }}>加载知识宇宙中...</span>
            </div>
          </div>
        ) : !graphData ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center px-8">
              <div className="text-6xl mb-4">🌌</div>
              <h2 className="text-xl font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
                欢迎来到知识宇宙
              </h2>
              <p style={{ color: 'var(--text-secondary)' }}>
                在这里，每一个知识节点都是一颗等待点亮的星辰
              </p>
            </div>
          </div>
        ) : (
          <div className="absolute inset-0">
            {/* TODO: Cytoscape.js 图谱渲染组件 */}
            <p className="p-4" style={{ color: 'var(--text-muted)' }}>
              图谱节点: {graphData.nodes.length} | 边: {graphData.edges.length}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
