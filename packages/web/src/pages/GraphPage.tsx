import { useEffect, useState, useCallback, lazy, Suspense, useMemo } from 'react';
import { createLogger } from '@/lib/utils/logger';
import { useNavigate, useParams } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useDomainStore } from '@/lib/store/domain';
import { apiFetchRecommendations, apiFetchDueReviews } from '@/lib/api/learning-api';
import type { GraphNode, GraphData } from '@akg/shared';
import { ChatPanel } from '@/components/chat/ChatPanel';
import { DraggableModal } from '@/components/common/DraggableModal';
import { DashboardContent } from '@/components/panels/DashboardContent';
import { SettingsContent } from '@/components/panels/SettingsContent';
import { AchievementPanel } from '@/components/panels/AchievementPanel';
import { useAchievementStore } from '@/lib/store/achievements';
import { Loader, Network } from 'lucide-react';
import { useSettingsStore } from '@/lib/store/settings';
import { useAuthStore } from '@/lib/store/auth';
import { GraphMiniStats } from '@/components/graph/GraphMiniStats';
import { GraphLegend } from '@/components/graph/GraphLegend';
import { SubdomainFilter } from '@/components/graph/SubdomainFilter';
import { GraphBreadcrumb } from '@/components/graph/GraphBreadcrumb';
import { GraphSearchOverlay } from '@/components/graph/GraphSearchOverlay';
import { GraphHubBar } from '@/components/graph/GraphHubBar';
import { GraphRecommendPanel, type Recommendation } from '@/components/graph/GraphRecommendPanel';
import { GraphConceptHeader } from '@/components/graph/GraphConceptHeader';
import { useGraphKeyNav } from '@/lib/hooks/useGraphKeyNav';

const log = createLogger('GraphPage');

const KnowledgeGraph = lazy(() =>
  import('@/components/graph/KnowledgeGraph').then((m) => ({ default: m.KnowledgeGraph }))
);

export function GraphPage() {
  const { domainId: urlDomainId, conceptId: urlConceptId } = useParams<{ domainId: string; conceptId?: string }>();
  const navigate = useNavigate();

  const { graphData, loading, selectedNode, activeSubdomain, loadGraphData, selectNode, setActiveSubdomain } = useGraphStore();
  const { activeDomain, fetchDomains, getActiveDomainInfo, switchDomain } = useDomainStore();
  const { progress, computeStats, refreshStreak, initEdges, recommendedIds, syncWithBackend, backendSynced } = useLearningStore();

  const [showDashboard, setShowDashboard] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showAchievements, setShowAchievements] = useState(false);
  const { unseenCount: achievementBadge } = useAchievementStore();
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [recommendLoading, setRecommendLoading] = useState(false);
  const [showRecommend, setShowRecommend] = useState(false);
  const [showDomainPicker, setShowDomainPicker] = useState(false);
  const [dueReviewCount, setDueReviewCount] = useState(0);

  const { user, supabaseConfigured, signOut } = useAuthStore();
  const isLoggedIn = !!user;
  const isUsingFreeAPI = useSettingsStore((s) => !s.llmConfig.apiKey?.trim());
  const { domains } = useDomainStore();
  const activeDomains = domains.filter((d) => d.is_active !== false);

  // ── URL ↔ Store sync ──
  useEffect(() => { if (urlDomainId && urlDomainId !== activeDomain) switchDomain(urlDomainId); }, [urlDomainId]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (urlConceptId && graphData) {
      const node = graphData.nodes.find((n) => n.id === urlConceptId);
      if (node && selectedNode?.id !== urlConceptId) selectNode(node);
    } else if (!urlConceptId && selectedNode) { selectNode(null); }
  }, [urlConceptId, graphData]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Data loading ──
  useEffect(() => { apiFetchDueReviews(1, activeDomain || undefined).then((data) => { if (data) setDueReviewCount(data.due_count); }); }, [activeDomain]);
  useEffect(() => { if (graphData) { refreshStreak(); computeStats(graphData.nodes.length); initEdges(graphData.edges.filter((e) => e.relation_type === 'prerequisite').map((e) => ({ source: e.source, target: e.target }))); } }, [graphData]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (graphData) computeStats(graphData.nodes.length); }, [progress]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { if (!backendSynced) syncWithBackend(); }, [backendSynced]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { fetchDomains(); }, []); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => { loadGraphData(activeDomain); }, [activeDomain]); // eslint-disable-line react-hooks/exhaustive-deps

  // ── Navigation handlers ──
  const handleNodeClick = (node: GraphNode) => { if (node?.id) navigate(`/domain/${urlDomainId}/${node.id}`, { replace: true }); };
  const handleCloseDetail = () => { selectNode(null); navigate(`/domain/${urlDomainId}`, { replace: true }); };
  const handleDomainSwitch = (domainId: string) => { if (domainId === activeDomain) { setShowDomainPicker(false); return; } setShowDomainPicker(false); navigate(`/domain/${domainId}`); };

  const chatOpen = !!selectedNode;

  const loadRecommendations = useCallback(async () => {
    setRecommendLoading(true);
    try { const data = await apiFetchRecommendations(5, activeDomain); if (data) setRecommendations(data.recommendations); }
    catch (e) { log.warn('Failed to load recommendations', { err: (e as Error).message }); }
    finally { setRecommendLoading(false); }
  }, [activeDomain]);

  const enrichedGraphData = useMemo<GraphData | null>(() => {
    if (!graphData) return null;
    return { ...graphData, nodes: graphData.nodes.map((n) => ({ ...n, status: progress[n.id] ? progress[n.id].status : n.status, is_recommended: recommendedIds.has(n.id) })) };
  }, [graphData, progress, recommendedIds]);

  useGraphKeyNav(
    (node) => navigate(`/domain/${urlDomainId}/${node.id}`, { replace: true }),
    (node) => navigate(`/domain/${urlDomainId}/${node.id}`),
  );

  // ── Hub bar toggle callbacks ──
  const toggleDashboard = useCallback(() => { setShowDashboard((v) => !v); setShowSettings(false); setShowAchievements(false); }, []);
  const toggleSettings = useCallback(() => { setShowSettings((v) => !v); setShowDashboard(false); setShowAchievements(false); }, []);
  const toggleAchievements = useCallback(() => { setShowAchievements((v) => !v); setShowDashboard(false); setShowSettings(false); }, []);
  const toggleDomainPicker = useCallback(() => { setShowDomainPicker((v) => !v); setShowRecommend(false); }, []);
  const toggleRecommend = useCallback(() => { setShowRecommend((v) => { if (!v) { setShowDomainPicker(false); loadRecommendations(); } return !v; }); }, [loadRecommendations]);

  return (
    <div className="relative h-full w-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      {/* ===== 3D Graph ===== */}
      <div className="absolute inset-0 transition-all duration-500 ease-out" style={chatOpen ? { right: '50%' } : {}}>
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
          <>
            <Suspense fallback={<div className="flex items-center justify-center h-full"><Loader size={28} className="animate-spin" style={{ color: 'var(--color-text-tertiary)' }} /></div>}>
              <KnowledgeGraph key={activeDomain} data={enrichedGraphData} onNodeClick={handleNodeClick} selectedNodeId={selectedNode?.id} activeSubdomain={activeSubdomain} domainColor={getActiveDomainInfo()?.color} domainId={activeDomain} />
            </Suspense>
            {!chatOpen && (<>
              <GraphMiniStats nodes={enrichedGraphData.nodes} domainName={getActiveDomainInfo()?.name || ''} domainColor={getActiveDomainInfo()?.color || '#8b5cf6'} streak={useLearningStore.getState().streak.current} />
              <SubdomainFilter nodes={enrichedGraphData.nodes} activeSubdomain={activeSubdomain} onSubdomainChange={setActiveSubdomain} domainColor={getActiveDomainInfo()?.color || '#8b5cf6'} />
              <GraphLegend />
            </>)}
            {chatOpen && urlDomainId && <GraphBreadcrumb domainId={urlDomainId} />}
          </>
        )}
      </div>

      {/* ===== RIGHT PANEL: Chat ===== */}
      {chatOpen && (
        <div className="absolute top-0 right-0 bottom-0 z-20 animate-slide-in-right" style={{ width: '50%' }}>
          <div className="h-full flex flex-col" style={{ backgroundColor: 'var(--color-surface-2)', borderLeft: '1px solid var(--color-border)' }}>
            <GraphConceptHeader node={selectedNode!} progress={progress} onClose={handleCloseDetail} />
            <div className="flex-1 min-h-0 overflow-hidden" style={{ borderTop: '1px solid var(--color-border)' }}>
              <ChatPanel conceptId={selectedNode!.id} conceptName={selectedNode!.label} domainId={urlDomainId} />
            </div>
          </div>
        </div>
      )}

      {/* ===== Search overlay ===== */}
      {!chatOpen && <GraphSearchOverlay graphData={enrichedGraphData} onNodeClick={handleNodeClick} />}

      {/* ===== Hub Bar ===== */}
      <GraphHubBar
        chatOpen={chatOpen} activeDomain={activeDomain} activeDomains={activeDomains}
        isUsingFreeAPI={isUsingFreeAPI} isLoggedIn={isLoggedIn} supabaseConfigured={supabaseConfigured}
        achievementBadge={achievementBadge} dueReviewCount={dueReviewCount}
        showDashboard={showDashboard} showSettings={showSettings} showAchievements={showAchievements}
        showDomainPicker={showDomainPicker} showRecommend={showRecommend}
        onToggleDashboard={toggleDashboard} onToggleSettings={toggleSettings}
        onToggleAchievements={toggleAchievements} onToggleDomainPicker={toggleDomainPicker}
        onToggleRecommend={toggleRecommend} onDomainSwitch={handleDomainSwitch}
        onNavigate={navigate} onSignOut={signOut}
      />

      {/* ===== Recommend Panel ===== */}
      {showRecommend && (
        <GraphRecommendPanel recommendations={recommendations} loading={recommendLoading} chatOpen={chatOpen} graphData={enrichedGraphData} onNodeClick={handleNodeClick} onClose={() => setShowRecommend(false)} />
      )}

      {/* ===== MODALS ===== */}
      <DraggableModal open={showDashboard} onClose={() => setShowDashboard(false)} title="学习进度" width={820} height={680}>
        <DashboardContent onNavigate={(conceptId) => { setShowDashboard(false); navigate(`/domain/${urlDomainId}/${conceptId}`, { replace: true }); }} onDomainSwitch={() => setShowDashboard(false)} />
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
