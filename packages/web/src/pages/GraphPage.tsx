import { useEffect, useState, useCallback, lazy, Suspense, useMemo } from 'react';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useIsDesktop } from '@/lib/hooks/useMediaQuery';
import { apiFetchRecommendations } from '@/lib/api/learning-api';
import type { GraphNode, GraphData } from '@akg/shared';
import { GRAPH_VISUAL } from '@akg/shared';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { DraggableModal } from '@/components/common/DraggableModal';
import { DashboardContent } from '@/components/panels/DashboardContent';
import { SettingsContent } from '@/components/panels/SettingsContent';
import {
  Search, X, Star, ChevronRight, Clock, BookOpen, Zap,
  Filter, Trophy, Loader, Compass, BarChart3, Settings, Network,
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
  const [showDashboard, setShowDashboard] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [recommendations, setRecommendations] = useState<Array<{
    concept_id: string; name: string; difficulty: number;
    estimated_minutes: number; is_milestone: boolean; score: number; reason: string; status: string;
  }>>([]);
  const [recommendLoading, setRecommendLoading] = useState(false);
  const [showRecommend, setShowRecommend] = useState(false);

  const totalNodes = graphData?.nodes.length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;
  const learningCount = Object.values(progress).filter(p => p.status === 'learning').length;
  const progressPct = totalNodes > 0 ? Math.round((masteredCount / totalNodes) * 100) : 0;

  // Whether right panel (chat) is open
  const chatOpen = !!selectedNode;

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
      const prereqEdges = graphData.edges.filter((e) => e.relation_type === 'prerequisite').map((e) => ({ source: e.source, target: e.target }));
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
    try { const res = await fetch('/api/graph/subdomains'); if (res.ok) setSubdomains(await res.json()); } catch { /* ignore */ }
  };

  const handleNodeClick = (node: GraphNode) => selectNode(node?.id ? node : null);

  const difficultyLabel = (d: number) => {
    if (d <= 3) return { text: '入门', color: 'var(--color-accent-emerald)' };
    if (d <= 6) return { text: '进阶', color: 'var(--color-accent-primary)' };
    return { text: '高级', color: 'var(--color-accent-rose)' };
  };

  const searchResults = useMemo(() => {
    if (!searchQuery.trim() || !enrichedGraphData) return [];
    return enrichedGraphData.nodes.filter((n) => n.label.toLowerCase().includes(searchQuery.toLowerCase()) || n.id.toLowerCase().includes(searchQuery.toLowerCase())).slice(0, 8);
  }, [searchQuery, enrichedGraphData]);

  return (
    <div className="relative h-full w-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>

      {/* ===== 3D Graph — takes full screen or left half ===== */}
      <div
        className="absolute inset-0 transition-all duration-500 ease-out"
        style={chatOpen ? { right: '50%' } : {}}
      >
        {loading ? (
          <div className="flex items-center justify-center h-full animate-fade-in">
            <div className="flex flex-col items-center gap-4">
              <Loader size={32} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} />
              <p className="text-base" style={{ color: 'var(--color-text-tertiary)' }}>加载知识图谱...</p>
            </div>
          </div>
        ) : !enrichedGraphData || enrichedGraphData.nodes.length === 0 ? (
          <div className="flex items-center justify-center h-full animate-fade-in">
            <div className="text-center max-w-md">
              <Network size={40} className="mx-auto mb-4" style={{ color: 'var(--color-text-tertiary)' }} />
              <h2 className="text-xl font-semibold mb-2">知识图谱</h2>
              <p style={{ color: 'var(--color-text-tertiary)' }}>请确保后端服务已启动。</p>
            </div>
          </div>
        ) : (
          <Suspense fallback={<div className="flex items-center justify-center h-full"><Loader size={28} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} /></div>}>
            <KnowledgeGraph data={enrichedGraphData!} onNodeClick={handleNodeClick} selectedNodeId={selectedNode?.id} activeSubdomain={activeSubdomain} />
          </Suspense>
        )}
      </div>

      {/* ===== RIGHT PANEL: Chat (50% width) ===== */}
      {chatOpen && (
        <div className="absolute top-0 right-0 bottom-0 z-20 animate-slide-in-right" style={{ width: '50%' }}>
          <div className="h-full flex flex-col" style={{ backgroundColor: 'var(--color-surface-1)', borderLeft: '1px solid var(--color-border)' }}>
            {/* Header */}
            <div className="px-5 py-4 shrink-0 flex items-start justify-between gap-3" style={{ borderBottom: '1px solid var(--color-border)' }}>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1.5">
                  {selectedNode!.is_milestone && <Star size={14} fill="var(--color-accent-primary)" style={{ color: 'var(--color-accent-primary)' }} />}
                  <h3 className="text-[15px] font-semibold truncate">{selectedNode!.label}</h3>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                  {(() => { const diff = difficultyLabel(selectedNode!.difficulty); return (
                    <span className="inline-flex items-center gap-1 rounded-lg px-2 py-0.5 text-xs font-medium" style={{ backgroundColor: diff.color + '14', color: diff.color }}>
                      Lv.{selectedNode!.difficulty} {diff.text}
                    </span>
                  ); })()}
                  {selectedNode!.estimated_minutes && (
                    <span className="inline-flex items-center gap-1 text-xs" style={{ color: 'var(--color-text-tertiary)' }}><Clock size={11} /> {selectedNode!.estimated_minutes}min</span>
                  )}
                  {progress[selectedNode!.id]?.status === 'mastered' ? (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold" style={{ color: 'var(--color-accent-emerald)' }}><Trophy size={11} /> 已掌握</span>
                  ) : progress[selectedNode!.id]?.status === 'learning' ? (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold" style={{ color: 'var(--color-accent-primary)' }}><BookOpen size={11} /> 学习中</span>
                  ) : selectedNode!.is_recommended ? (
                    <span className="inline-flex items-center gap-1 text-xs font-semibold" style={{ color: 'var(--color-accent-cyan)' }}><Zap size={11} /> 推荐</span>
                  ) : null}
                </div>
              </div>
              <button onClick={() => selectNode(null)}
                className="shrink-0 w-7 h-7 flex items-center justify-center rounded-full transition-colors"
                style={{ color: 'var(--color-text-tertiary)' }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.06)')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}>
                <X size={14} />
              </button>
            </div>
            {/* Chat */}
            <div className="flex-1 min-h-0 overflow-hidden">
              <ChatPanel conceptId={selectedNode!.id} conceptName={selectedNode!.label} />
            </div>
          </div>
        </div>
      )}

      {/* ===== TOP-LEFT: Search (overlay on graph) ===== */}
      {!chatOpen && (
        <div className="absolute top-5 left-1/2 -translate-x-1/2 z-20 pointer-events-auto" style={{ width: 'min(420px, 90vw)' }}>
          <div className="relative">
            <div className="flex items-center gap-2 px-4 rounded-2xl" style={{
              height: 44, background: 'rgba(25,24,26,0.85)', backdropFilter: 'blur(20px) saturate(1.5)',
              border: '1px solid rgba(255,255,255,0.08)', boxShadow: '0 4px 24px rgba(0,0,0,0.3)',
            }}>
              <Search size={15} style={{ color: 'var(--color-text-tertiary)', flexShrink: 0 }} />
              <input type="text" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="搜索知识节点..."
                className="flex-1 bg-transparent text-sm outline-none" style={{ color: 'var(--color-text-primary)', border: 'none' }} />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')} className="shrink-0 p-1 rounded-full hover:bg-white/5">
                  <X size={13} style={{ color: 'var(--color-text-tertiary)' }} />
                </button>
              )}
            </div>
            {searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-2 rounded-2xl p-1.5 animate-fade-in-scale" style={{
                maxHeight: 320, overflowY: 'auto', background: 'rgba(25,24,26,0.92)', backdropFilter: 'blur(20px)',
                border: '1px solid rgba(255,255,255,0.08)', boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
              }}>
                {searchResults.map((node) => (
                  <button key={node.id} onClick={() => { selectNode(node); setSearchQuery(''); }}
                    className="w-full text-left flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl transition-colors text-sm"
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.06)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}>
                    {node.is_milestone && <Star size={13} fill="var(--color-accent-primary)" style={{ color: 'var(--color-accent-primary)' }} />}
                    <span className="flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{node.label}</span>
                    <ChevronRight size={13} style={{ color: 'var(--color-text-tertiary)' }} />
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ===== BOTTOM HUB BAR ===== */}
      <div className="absolute bottom-5 left-1/2 -translate-x-1/2 z-30 pointer-events-auto">
        <div className="flex items-center gap-1 px-2 rounded-2xl" style={{
          height: 52, background: 'rgba(25,24,26,0.85)', backdropFilter: 'blur(24px) saturate(1.5)',
          border: '1px solid rgba(255,255,255,0.08)', boxShadow: '0 8px 40px rgba(0,0,0,0.4)',
        }}>
          {/* Filter */}
          <HubButton icon={Filter} label="筛选" active={showFilters} onClick={() => setShowFilters(!showFilters)} />
          {/* Dashboard */}
          <HubButton icon={BarChart3} label="进度" active={showDashboard} onClick={() => { setShowDashboard(!showDashboard); setShowSettings(false); }} />

          {/* Divider */}
          <div className="w-px h-6 mx-1" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }} />

          {/* Recommend — center, prominent */}
          <button onClick={() => {
            if (!showRecommend) { setShowRecommend(true); loadRecommendations(); } else setShowRecommend(false);
          }} className="flex items-center gap-2 px-5 py-2 rounded-xl transition-all text-sm font-medium" style={{
            backgroundColor: showRecommend ? 'var(--color-accent-primary)' : 'rgba(200,149,108,0.12)',
            color: showRecommend ? '#111110' : 'var(--color-accent-primary)',
          }}>
            <Compass size={16} />
            <span>推荐学习</span>
          </button>

          {/* Divider */}
          <div className="w-px h-6 mx-1" style={{ backgroundColor: 'rgba(255,255,255,0.08)' }} />

          {/* Settings */}
          <HubButton icon={Settings} label="设置" active={showSettings} onClick={() => { setShowSettings(!showSettings); setShowDashboard(false); }} />
          {/* Legend */}
          <HubButton icon={BookOpen} label="图例" active={false} onClick={() => {}} />
        </div>
      </div>

      {/* ===== RECOMMEND PANEL (above hub) ===== */}
      {showRecommend && (
        <div className="absolute bottom-20 left-1/2 -translate-x-1/2 z-25 pointer-events-auto animate-fade-in-scale" style={{ width: 360 }}>
          <div className="rounded-2xl overflow-hidden" style={{
            background: 'rgba(25,24,26,0.92)', backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255,255,255,0.08)', boxShadow: '0 12px 48px rgba(0,0,0,0.5)',
          }}>
            <div className="px-4 py-3 flex items-center justify-between" style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <div className="flex items-center gap-2">
                <Compass size={15} style={{ color: 'var(--color-accent-primary)' }} />
                <span className="text-sm font-semibold">推荐学习路径</span>
              </div>
              <button onClick={() => setShowRecommend(false)} className="p-1.5 rounded-full hover:bg-white/5" style={{ color: 'var(--color-text-tertiary)' }}><X size={13} /></button>
            </div>
            <div style={{ maxHeight: 320, overflowY: 'auto' }}>
              {recommendLoading ? (
                <div className="flex items-center justify-center py-8"><Loader size={18} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} /></div>
              ) : recommendations.length === 0 ? (
                <p className="text-sm text-center py-8" style={{ color: 'var(--color-text-tertiary)' }}>暂无推荐</p>
              ) : recommendations.map((rec, idx) => {
                const diff = difficultyLabel(rec.difficulty);
                return (
                  <button key={rec.concept_id} onClick={() => {
                    const node = enrichedGraphData?.nodes.find(n => n.id === rec.concept_id);
                    if (node) { selectNode(node); setShowRecommend(false); }
                  }} className="w-full text-left px-4 py-3 flex items-start gap-3 transition-colors"
                    style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.04)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}>
                    <div className="shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-[11px] font-semibold"
                      style={{ backgroundColor: 'var(--color-accent-primary)', color: '#111110' }}>{idx + 1}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-1.5 mb-0.5">
                        {rec.is_milestone && <Star size={11} fill="var(--color-accent-primary)" style={{ color: 'var(--color-accent-primary)' }} />}
                        <span className="text-sm font-medium truncate">{rec.name}</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                        <span style={{ color: diff.color }}>Lv.{rec.difficulty}</span>
                        <span>{rec.estimated_minutes}min</span>
                      </div>
                    </div>
                    <ChevronRight size={13} className="shrink-0 mt-1" style={{ color: 'var(--color-text-tertiary)' }} />
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* ===== FILTER PANEL (above hub) ===== */}
      {showFilters && subdomains.length > 0 && (
        <div className="absolute bottom-20 left-1/2 -translate-x-1/2 z-25 pointer-events-auto animate-fade-in-scale">
          <div className="rounded-2xl p-2.5 flex flex-wrap gap-1.5" style={{
            maxWidth: 480, background: 'rgba(25,24,26,0.92)', backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255,255,255,0.08)', boxShadow: '0 12px 48px rgba(0,0,0,0.5)',
          }}>
            <button onClick={() => setActiveSubdomain(null)}
              className="rounded-xl px-3 py-1.5 text-sm font-medium transition-all"
              style={{ backgroundColor: !activeSubdomain ? 'var(--color-accent-primary)' : 'transparent', color: !activeSubdomain ? '#111110' : 'var(--color-text-secondary)' }}>
              全部
            </button>
            {subdomains.map((sd) => {
              const isActive = activeSubdomain === sd.id;
              const sdColor = SUBDOMAIN_COLORS[sd.id] || 'var(--color-accent-primary)';
              return (
                <button key={sd.id} onClick={() => setActiveSubdomain(isActive ? null : sd.id)}
                  className="rounded-xl px-3 py-1.5 text-sm font-medium transition-all flex items-center gap-1.5"
                  style={{ backgroundColor: isActive ? sdColor : 'transparent', color: isActive ? '#fff' : 'var(--color-text-secondary)' }}>
                  <span className="w-2 h-2 rounded-full" style={{ backgroundColor: sdColor, opacity: isActive ? 0 : 0.7 }} />
                  {sd.name}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* ===== MODALS ===== */}
      <DraggableModal open={showDashboard} onClose={() => setShowDashboard(false)} title="学习进度" width={520} height={560}>
        <DashboardContent />
      </DraggableModal>
      <DraggableModal open={showSettings} onClose={() => setShowSettings(false)} title="设置" width={480} height={600}>
        <SettingsContent />
      </DraggableModal>
    </div>
  );
}

/* ── Hub Button ── */
function HubButton({ icon: Icon, label, active, onClick }: { icon: typeof Filter; label: string; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick}
      className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl transition-all text-sm font-medium whitespace-nowrap"
      style={{
        backgroundColor: active ? 'rgba(255,255,255,0.08)' : 'transparent',
        color: active ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)',
      }}
      onMouseEnter={(e) => { if (!active) e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.04)'; }}
      onMouseLeave={(e) => { if (!active) e.currentTarget.style.backgroundColor = 'transparent'; }}>
      <Icon size={15} />
      <span>{label}</span>
    </button>
  );
}
