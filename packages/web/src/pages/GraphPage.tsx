import { useEffect, useState, useCallback, useRef, lazy, Suspense, useMemo } from 'react';
import { createLogger } from '@/lib/utils/logger';
import { useNavigate, useParams } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useDomainStore } from '@/lib/store/domain';
import { apiFetchRecommendations } from '@/lib/api/learning-api';
import type { GraphNode, GraphData } from '@akg/shared';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { DraggableModal } from '@/components/common/DraggableModal';
import { DashboardContent } from '@/components/panels/DashboardContent';
import { SettingsContent } from '@/components/panels/SettingsContent';
import { AchievementPanel } from '@/components/panels/AchievementPanel';
import { useAchievementStore } from '@/lib/store/achievements';
import {
  Search, X, Star, ChevronRight, Clock, BookOpen, Zap,
  Trophy, Loader, Compass, BarChart3, Settings, Network,
  Globe, Check, LogIn, User, Home, MessageCircle, AlertTriangle,
} from 'lucide-react';
import { useSettingsStore } from '@/lib/store/settings';
import { useAuthStore } from '@/lib/store/auth';

const log = createLogger('GraphPage');

const KnowledgeGraph = lazy(() =>
  import('@/components/graph/KnowledgeGraph').then((m) => ({ default: m.KnowledgeGraph }))
);

export function GraphPage() {
  const { domainId: urlDomainId, conceptId: urlConceptId } = useParams<{ domainId: string; conceptId?: string }>();
  const navigate = useNavigate();

  const {
    graphData, loading, selectedNode, activeSubdomain,
    loadGraphData, selectNode,
  } = useGraphStore();
  const { activeDomain, fetchDomains, getActiveDomainInfo, switchDomain } = useDomainStore();
  const { progress, computeStats, refreshStreak, initEdges, recommendedIds, syncWithBackend, backendSynced } = useLearningStore();

  const [searchQuery, setSearchQuery] = useState('');

  const [showDashboard, setShowDashboard] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showAchievements, setShowAchievements] = useState(false);
  const { unseenCount: achievementBadge } = useAchievementStore();
  const [recommendations, setRecommendations] = useState<Array<{
    concept_id: string; name: string; difficulty: number;
    estimated_minutes: number; is_milestone: boolean; score: number; reason: string; status: string;
  }>>([]);
  const [recommendLoading, setRecommendLoading] = useState(false);
  const [showRecommend, setShowRecommend] = useState(false);
  const [showDomainPicker, setShowDomainPicker] = useState(false);

  // Auth
  const { user, supabaseConfigured, signOut } = useAuthStore();
  const isLoggedIn = !!user;

  // Settings — detect free API mode
  const isUsingFreeAPI = useSettingsStore((s) => !s.llmConfig.apiKey?.trim());

  // Domain
  const { domains } = useDomainStore();
  const activeDomains = domains.filter((d) => d.is_active !== false);

  // Close domain picker on outside click
  const domainPickerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!showDomainPicker) return;
    function handleClick(e: MouseEvent) {
      if (domainPickerRef.current && !domainPickerRef.current.contains(e.target as Node)) setShowDomainPicker(false);
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, [showDomainPicker]);

  // ── Sync URL domainId → store ──
  useEffect(() => {
    if (urlDomainId && urlDomainId !== activeDomain) {
      switchDomain(urlDomainId);
    }
  }, [urlDomainId]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Restore concept selection from URL ──
  useEffect(() => {
    if (urlConceptId && graphData) {
      const node = graphData.nodes.find((n) => n.id === urlConceptId);
      if (node && selectedNode?.id !== urlConceptId) {
        selectNode(node);
      }
    } else if (!urlConceptId && selectedNode) {
      // URL has no conceptId but a node is selected → clear it
      // (happens when user navigates back to /domain/:domainId)
      selectNode(null);
    }
  }, [urlConceptId, graphData]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleDomainSwitch = (domainId: string) => {
    if (domainId === activeDomain) { setShowDomainPicker(false); return; }
    setShowDomainPicker(false);
    navigate(`/domain/${domainId}`);
  };

  // ── Node click → update URL ──
  const handleNodeClick = (node: GraphNode) => {
    if (node?.id) {
      navigate(`/domain/${urlDomainId}/${node.id}`, { replace: true });
    }
  };

  // ── Close detail panel → update URL ──
  const handleCloseDetail = () => {
    selectNode(null);
    navigate(`/domain/${urlDomainId}`, { replace: true });
  };

  // (stats used in DashboardContent via store; not needed here after routing overhaul)

  // Whether right panel (chat) is open
  const chatOpen = !!selectedNode;

  const loadRecommendations = useCallback(async () => {
    setRecommendLoading(true);
    try {
      const data = await apiFetchRecommendations(5, activeDomain);
      if (data) setRecommendations(data.recommendations);
    } catch (e) { log.warn('Failed to load recommendations', { err: (e as Error).message }); }
    finally { setRecommendLoading(false); }
  }, [activeDomain]);

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
    // eslint-disable-next-line react-hooks/exhaustive-deps -- Zustand actions are stable refs
  }, [graphData]);

  // eslint-disable-next-line react-hooks/exhaustive-deps -- computeStats is stable, graphData read from closure
  useEffect(() => { if (graphData) computeStats(graphData.nodes.length); }, [progress]);
  // eslint-disable-next-line react-hooks/exhaustive-deps -- one-time sync on mount
  useEffect(() => { if (!backendSynced) syncWithBackend(); }, [backendSynced]);
  // eslint-disable-next-line react-hooks/exhaustive-deps -- mount-only
  useEffect(() => { fetchDomains(); }, []);

  // Reload graph when activeDomain changes
  // eslint-disable-next-line react-hooks/exhaustive-deps -- activeDomain drives reload
  useEffect(() => { loadGraphData(activeDomain); }, [activeDomain]);



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
            <KnowledgeGraph key={activeDomain} data={enrichedGraphData!} onNodeClick={handleNodeClick} selectedNodeId={selectedNode?.id} activeSubdomain={activeSubdomain} domainColor={getActiveDomainInfo()?.color} domainId={activeDomain} />
          </Suspense>
        )}
      </div>

      {/* ===== RIGHT PANEL: Chat (50% width) ===== */}
      {chatOpen && (
        <div className="absolute top-0 right-0 bottom-0 z-20 animate-slide-in-right" style={{ width: '50%' }}>
            <div className="h-full flex flex-col" style={{ backgroundColor: 'var(--color-surface-2)', borderLeft: '1px solid var(--color-border)' }}>
            {/* Header */}
            <div className="shrink-0 flex items-start justify-between" style={{ padding: '24px 28px', gap: 16, backgroundColor: 'var(--color-surface-1)', borderBottom: '1px solid var(--color-border-subtle)' }}>
              <div className="flex-1 min-w-0">
                <div className="flex items-center" style={{ gap: 10, marginBottom: 10 }}>
                  {selectedNode!.is_milestone && <Star size={16} fill="var(--color-accent-primary)" style={{ color: 'var(--color-accent-primary)' }} />}
                  <h3 className="font-bold truncate" style={{ fontSize: 18 }}>{selectedNode!.label}</h3>
                </div>
                <div className="flex items-center flex-wrap" style={{ gap: 14 }}>
                  {(() => { const diff = difficultyLabel(selectedNode!.difficulty); return (
                    <span className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1 text-sm font-medium" style={{ backgroundColor: diff.color + '14', color: diff.color }}>
                      Lv.{selectedNode!.difficulty} {diff.text}
                    </span>
                  ); })()}
                  {selectedNode!.estimated_minutes && (
                    <span className="inline-flex items-center gap-1.5 text-sm" style={{ color: 'var(--color-text-tertiary)' }}><Clock size={13} /> {selectedNode!.estimated_minutes}min</span>
                  )}
                  {progress[selectedNode!.id]?.status === 'mastered' ? (
                    <span className="inline-flex items-center gap-1.5 text-sm font-semibold" style={{ color: 'var(--color-accent-emerald)' }}><Trophy size={13} /> 已掌握</span>
                  ) : progress[selectedNode!.id]?.status === 'learning' ? (
                    <span className="inline-flex items-center gap-1.5 text-sm font-semibold" style={{ color: 'var(--color-accent-primary)' }}><BookOpen size={13} /> 学习中</span>
                  ) : selectedNode!.is_recommended ? (
                    <span className="inline-flex items-center gap-1.5 text-sm font-semibold" style={{ color: 'var(--color-accent-cyan)' }}><Zap size={13} /> 推荐</span>
                  ) : null}
                </div>
              </div>
              <button onClick={() => handleCloseDetail()}
                className="shrink-0 w-9 h-9 flex items-center justify-center rounded-full transition-colors"
                style={{ color: 'var(--color-text-tertiary)' }}
                onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.06)')}
                onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}>
                <X size={16} />
              </button>
            </div>
            {/* Chat */}
            <div className="flex-1 min-h-0 overflow-hidden" style={{ borderTop: '1px solid var(--color-border)' }}>
              <ChatPanel conceptId={selectedNode!.id} conceptName={selectedNode!.label} domainId={urlDomainId} />
            </div>
          </div>
        </div>
      )}

      {/* ===== TOP: Search (overlay on graph, shifts to left-half when chat is open) ===== */}
      {!chatOpen ? (
        <div className="absolute top-5 left-1/2 -translate-x-1/2 z-20 pointer-events-auto" style={{ width: 'min(420px, 90vw)' }}>
          <div className="relative">
            <div className="flex items-center gap-2" style={{
              height: 48, padding: '0 20px', borderRadius: 16, background: 'rgba(245,245,242,0.92)', backdropFilter: 'blur(16px)',
              border: '1px solid rgba(0,0,0,0.10)', boxShadow: '0 2px 16px rgba(0,0,0,0.06)',
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
              <div className="absolute top-full left-0 right-0 animate-fade-in-scale" style={{
                marginTop: 8, borderRadius: 16, padding: 8, maxHeight: 320, overflowY: 'auto', background: 'rgba(245,245,242,0.96)', backdropFilter: 'blur(16px)',
                border: '1px solid rgba(0,0,0,0.10)', boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
              }}>
                {searchResults.map((node) => (
                  <button key={node.id} onClick={() => { handleNodeClick(node); setSearchQuery(''); }}
                    className="w-full text-left flex items-center transition-colors"
                    style={{ gap: 10, padding: '12px 16px', borderRadius: 10, fontSize: 14 }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.04)')}
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
      ) : null}

      {/* ===== BOTTOM HUB BAR (shifts to left-half center when chat is open) ===== */}
      <div className="absolute bottom-6 z-30 pointer-events-auto transition-all duration-500 ease-out" style={chatOpen ? { left: '25%', transform: 'translateX(-50%)' } : { left: '50%', transform: 'translateX(-50%)' }} ref={domainPickerRef}>
        <div className="flex items-center" style={{
          padding: '0 8px', height: 64, borderRadius: 20, background: 'rgba(245,245,242,0.92)', backdropFilter: 'blur(20px)',
          border: '1px solid rgba(0,0,0,0.10)', boxShadow: '0 8px 32px rgba(0,0,0,0.08)', gap: 4,
        }}>
          {/* Home — back to domain selection */}
          <HubButton icon={Home} label="首页" active={false} onClick={() => navigate('/')} />

          {/* Domain Switcher — icon + 2 chars */}
          <HubButton icon={Globe} label="知域" active={showDomainPicker} onClick={() => { setShowDomainPicker(!showDomainPicker); setShowRecommend(false); }} />

          {/* Dashboard — icon + 2 chars */}
          <HubButton icon={BarChart3} label="进度" active={showDashboard} onClick={() => { setShowDashboard(!showDashboard); setShowSettings(false); setShowAchievements(false); }} />

          {/* Achievements — icon + badge */}
          <div style={{ position: 'relative' }}>
            <HubButton icon={Trophy} label="成就" active={showAchievements} onClick={() => { setShowAchievements(!showAchievements); setShowDashboard(false); setShowSettings(false); }} />
            {achievementBadge > 0 && (
              <span style={{
                position: 'absolute', top: 2, right: 4,
                width: 16, height: 16, borderRadius: '50%',
                backgroundColor: 'var(--color-accent-rose)',
                color: '#fff', fontSize: 10, fontWeight: 700,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                lineHeight: 1,
              }}>{achievementBadge > 9 ? '9+' : achievementBadge}</span>
            )}
          </div>

          {/* Recommend — center, prominent */}
          <button onClick={() => {
            if (!showRecommend) { setShowRecommend(true); setShowDomainPicker(false); loadRecommendations(); } else setShowRecommend(false);
          }} className="flex items-center gap-2 rounded-2xl transition-all font-semibold whitespace-nowrap" style={{
            padding: '8px 20px', height: 48,
            backgroundColor: showRecommend ? 'var(--color-accent-primary)' : 'rgba(16,185,129,0.1)',
            color: showRecommend ? '#ffffff' : 'var(--color-accent-primary)', fontSize: 14,
          }}>
            <Compass size={18} />
            <span>推荐</span>
          </button>

          {/* Settings — icon + 2 chars */}
          <HubButton icon={Settings} label="设置" active={showSettings} onClick={() => { setShowSettings(!showSettings); setShowDashboard(false); setShowAchievements(false); }} />

          {/* User / Login — icon + 2 chars */}
          {supabaseConfigured && isLoggedIn ? (
            <HubButton icon={User} label="我的" active={false} onClick={() => signOut()} />
          ) : (
            <HubButton icon={LogIn} label="登录" active={false} onClick={() => navigate('/login')} />
          )}

          {/* Social / Community — placeholder for future social module */}
          <HubButton icon={MessageCircle} label="交流" active={false} onClick={() => {
            // TODO: Open social/community panel when implemented
          }} />
        </div>

        {/* Free API warning banner */}
        {isUsingFreeAPI && (
          <div
            className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 whitespace-nowrap flex items-center gap-2 rounded-full animate-fade-in"
            style={{
              padding: '6px 16px',
              background: 'rgba(245, 158, 11, 0.12)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(245, 158, 11, 0.25)',
              fontSize: 12,
              color: 'var(--color-accent-amber)',
              fontWeight: 500,
            }}
          >
            <AlertTriangle size={13} />
            <span>正在使用免费 API，质量和稳定性可能不佳</span>
            <button
              onClick={() => { setShowSettings(true); setShowDashboard(false); setShowAchievements(false); }}
              className="underline font-semibold"
              style={{ color: 'var(--color-accent-amber)', textUnderlineOffset: 2 }}
            >
              去设置
            </button>
          </div>
        )}

        {/* ===== DOMAIN PICKER PANEL (above hub) ===== */}
        {showDomainPicker && (
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 animate-fade-in-scale" style={{ width: 320 }}>
            <div style={{
              borderRadius: 16, overflow: 'hidden', background: 'rgba(245,245,242,0.96)', backdropFilter: 'blur(20px)',
              border: '1px solid rgba(0,0,0,0.10)', boxShadow: '0 12px 48px rgba(0,0,0,0.1)',
            }}>
              <div className="flex items-center justify-between" style={{ padding: '14px 20px', borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
                <div className="flex items-center gap-2">
                  <Globe size={14} style={{ color: 'var(--color-accent-primary)' }} />
                  <span className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>知识域</span>
                </div>
                <button onClick={() => setShowDomainPicker(false)} className="p-1.5 rounded-full hover:bg-black/5" style={{ color: 'var(--color-text-tertiary)' }}><X size={14} /></button>
              </div>
              <div style={{ maxHeight: 320, overflowY: 'auto' }}>
                {activeDomains.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-8 px-5" style={{ gap: 8 }}>
                    <Loader size={18} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} />
                    <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>请启动后端服务以加载知识域</span>
                  </div>
                ) : activeDomains.map((domain) => {
                  const isActive = domain.id === activeDomain;
                  return (
                    <button key={domain.id} onClick={() => handleDomainSwitch(domain.id)}
                      className="w-full text-left flex items-center gap-3 transition-colors"
                      style={{ padding: '10px 20px', backgroundColor: isActive ? 'rgba(0,0,0,0.04)' : 'transparent', borderBottom: '1px solid rgba(0,0,0,0.04)' }}
                      onMouseEnter={(e) => { if (!isActive) e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.03)'; }}
                      onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = isActive ? 'rgba(0,0,0,0.04)' : 'transparent'; }}>
                      <span className="text-lg">{domain.icon}</span>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>{domain.name}</div>
                        <div className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>{domain.description}</div>
                      </div>
                      {isActive && <Check size={15} className="shrink-0" style={{ color: 'var(--color-accent-primary)' }} />}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ===== RECOMMEND PANEL (above hub) ===== */}
      {showRecommend && (
        <div className="absolute pointer-events-auto animate-fade-in-scale transition-all duration-500 ease-out" style={{ width: 400, bottom: 100, zIndex: 25, ...(chatOpen ? { left: '25%', transform: 'translateX(-50%)' } : { left: '50%', transform: 'translateX(-50%)' }) }}>
          <div style={{
            borderRadius: 16, overflow: 'hidden', background: 'rgba(245,245,242,0.96)', backdropFilter: 'blur(20px)',
            border: '1px solid rgba(0,0,0,0.10)', boxShadow: '0 12px 48px rgba(0,0,0,0.1)',
          }}>
             <div className="flex items-center justify-between" style={{ padding: '18px 24px', borderBottom: '1px solid rgba(0,0,0,0.06)' }}>
              <div className="flex items-center gap-2">
                <Compass size={15} style={{ color: 'var(--color-accent-primary)' }} />
                <span className="text-sm font-semibold">推荐学习路径</span>
              </div>
              <button onClick={() => setShowRecommend(false)} className="p-1.5 rounded-full hover:bg-black/5" style={{ color: 'var(--color-text-tertiary)' }}><X size={14} /></button>
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
                    if (node) { handleNodeClick(node); setShowRecommend(false); }
                  }} className="w-full text-left flex items-start transition-colors"
                    style={{ padding: '16px 24px', gap: 14, borderBottom: '1px solid rgba(0,0,0,0.04)' }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.03)')}
                    onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}>
                    <div className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold"
                      style={{ backgroundColor: 'var(--color-accent-primary)', color: '#ffffff' }}>{idx + 1}</div>
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



      {/* ===== MODALS ===== */}
      <DraggableModal open={showDashboard} onClose={() => setShowDashboard(false)} title="学习进度" width={820} height={680}>
        <DashboardContent
          onNavigate={(conceptId) => {
            setShowDashboard(false);
            navigate(`/domain/${urlDomainId}/${conceptId}`, { replace: true });
          }}
          onDomainSwitch={() => {
            setShowDashboard(false);
          }}
        />
      </DraggableModal>
      <DraggableModal open={showSettings} onClose={() => setShowSettings(false)} title="设置" width={520} height={760}>
        <SettingsContent />
      </DraggableModal>
      <DraggableModal open={showAchievements} onClose={() => setShowAchievements(false)} title="🏆 成就" width={520} height={680}>
        <AchievementPanel />
      </DraggableModal>
    </div>
  );
}

/* ── Hub Button — unified: icon(18) + 2-char label, fixed width for symmetry ── */
function HubButton({ icon: Icon, label, active, onClick }: { icon: typeof BarChart3; label: string; active: boolean; onClick: () => void }) {
  return (
    <button onClick={onClick}
      className="flex flex-col items-center justify-center rounded-xl transition-all whitespace-nowrap"
      style={{
        width: 56, height: 48,
        backgroundColor: active ? 'rgba(0,0,0,0.06)' : 'transparent',
        color: active ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)',
      }}
      onMouseEnter={(e) => { if (!active) e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.04)'; }}
      onMouseLeave={(e) => { if (!active) e.currentTarget.style.backgroundColor = 'transparent'; }}>
      <Icon size={18} strokeWidth={active ? 2.5 : 2} />
      <span style={{ fontSize: 10, fontWeight: 500, marginTop: 2, lineHeight: 1 }}>{label}</span>
    </button>
  );
}
