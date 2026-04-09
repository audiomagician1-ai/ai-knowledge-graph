import type { SavedConversation } from '@/lib/store/dialogue';
import type { ConceptProgress } from '@/lib/store/learning';
import { ConceptPrerequisites } from '@/components/graph/ConceptPrerequisites';
import { ConceptMinimap } from '@/components/graph/ConceptMinimap';
import { SmartNextSteps } from '@/components/common/SmartNextSteps';
import { MasteryTimeline } from '@/components/dashboard/MasteryTimeline';
import { CrossDomainBridge } from '@/components/graph/CrossDomainBridge';
import { ConceptDiscussionPanel } from '@/components/community/ConceptDiscussionPanel';
import {
  Trophy, Brain, Play, History, MessageSquare,
} from 'lucide-react';

interface ChatIdleViewProps {
  conceptId: string;
  conceptName: string;
  domainId?: string;
  urlDomainId?: string;
  nodeProgress: ConceptProgress | null;
  conversations: SavedConversation[];
  onStartLearning: () => void;
  onViewHistory: () => void;
  onLoadConversation: (conversationId: string) => void;
  onConceptClick: (id: string) => void;
}

export function ChatIdleView({
  conceptId, conceptName, domainId, urlDomainId,
  nodeProgress, conversations,
  onStartLearning, onViewHistory, onLoadConversation, onConceptClick,
}: ChatIdleViewProps) {
  return (
    <div className="flex flex-col h-full" style={{ backgroundColor: 'var(--color-surface-2)' }}>
      <div className="flex-1 overflow-y-auto" style={{ padding: '28px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
        {/* Per-node mastery card */}
        <div
          className="rounded-xl"
          style={{ backgroundColor: '#ffffff', padding: 24, border: '1px solid rgba(0,0,0,0.08)', boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}
        >
          <div className="flex items-center gap-4 mb-6">
            <div
              className="w-10 h-10 rounded-md flex items-center justify-center shrink-0"
              style={{
                backgroundColor: nodeProgress?.status === 'mastered'
                  ? 'var(--color-accent-emerald)'
                  : 'var(--color-accent-primary)',
              }}
            >
              {nodeProgress?.status === 'mastered'
                ? <Trophy size={18} style={{ color: '#ffffff' }} />
                : <Brain size={18} style={{ color: '#ffffff' }} />
              }
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>
                {conceptName}
              </h4>
              <span className="text-sm" style={{
                color: nodeProgress?.status === 'mastered' ? 'var(--color-accent-emerald)'
                  : nodeProgress?.status === 'learning' ? 'var(--color-accent-amber)'
                  : 'var(--color-text-tertiary)',
              }}>
                {nodeProgress?.status === 'mastered' ? '已掌握'
                  : nodeProgress?.status === 'learning' ? '学习中'
                  : '未开始'}
              </span>
            </div>
          </div>

          {/* Per-node stats */}
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center rounded-xl px-3 py-5" style={{ backgroundColor: '#f5f5f3' }}>
              <div className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
                {nodeProgress?.sessions || 0}
              </div>
              <div className="text-sm mt-2" style={{ color: 'var(--color-text-tertiary)' }}>学习次数</div>
            </div>
            <div className="text-center rounded-xl px-3 py-5" style={{ backgroundColor: '#f5f5f3' }}>
              <div className="text-2xl font-bold" style={{
                color: nodeProgress?.mastery_score
                  ? (nodeProgress.mastery_score >= 75 ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)')
                  : 'var(--color-text-tertiary)',
              }}>
                {nodeProgress?.mastery_score || '—'}
              </div>
              <div className="text-sm mt-2" style={{ color: 'var(--color-text-tertiary)' }}>最高分</div>
            </div>
            <div className="text-center rounded-xl px-3 py-5" style={{ backgroundColor: '#f5f5f3' }}>
              <div className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
                {conversations.length}
              </div>
              <div className="text-sm mt-2" style={{ color: 'var(--color-text-tertiary)' }}>对话记录</div>
            </div>
          </div>
        </div>

        {/* Prerequisites / Dependents */}
        <ConceptPrerequisites
          conceptId={conceptId}
          onConceptClick={onConceptClick}
        />

        {/* Subdomain Minimap */}
        <ConceptMinimap
          conceptId={conceptId}
          onConceptClick={onConceptClick}
        />

        {/* Smart Next Steps */}
        <SmartNextSteps />

        {/* Mastery Timeline (V2.5) */}
        {nodeProgress && nodeProgress.sessions > 0 && (
          <MasteryTimeline conceptId={conceptId} />
        )}

        {/* Cross-Domain Bridge (V2.5) */}
        <CrossDomainBridge
          conceptId={conceptId}
          domainId={urlDomainId || domainId || ''}
        />

        {/* Concept Discussion (V2.8) */}
        <ConceptDiscussionPanel
          conceptId={conceptId}
          domainId={urlDomainId || domainId}
          compact
        />

        {/* Recent history preview (last 3) */}
        {conversations.length > 0 && (
          <div className="rounded-xl" style={{ backgroundColor: '#ffffff', border: '1px solid rgba(0,0,0,0.08)', boxShadow: '0 1px 3px rgba(0,0,0,0.06)', padding: '20px 24px' }}>
            <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
              <span className="text-sm font-bold" style={{ color: 'var(--color-text-secondary)' }}>
                最近对话
              </span>
              <button
                onClick={onViewHistory}
                className="text-sm flex items-center gap-1.5 transition-colors"
                style={{ color: 'var(--color-accent-primary)' }}
              >
                查看全部
                <History size={14} />
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {conversations.slice(0, 3).map((conv) => (
                <div
                  key={conv.conversationId}
                  className="flex items-center gap-4 rounded-lg cursor-pointer transition-all"
                  style={{ backgroundColor: '#f5f5f3', padding: '14px 18px', border: '1px solid transparent' }}
                  onClick={() => onLoadConversation(conv.conversationId)}
                  onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = '#eeeeec'; e.currentTarget.style.borderColor = 'rgba(0,0,0,0.1)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = '#f5f5f3'; e.currentTarget.style.borderColor = 'transparent'; }}
                >
                  <MessageSquare size={16} style={{ color: 'var(--color-text-tertiary)', flexShrink: 0 }} />
                  <span className="text-[15px] flex-1" style={{ color: 'var(--color-text-secondary)' }}>
                    {conv.messages.length} 条消息
                  </span>
                  {conv.assessment && (
                    <span
                      className="text-sm font-semibold"
                      style={{ color: conv.assessment.mastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)' }}
                    >
                      {conv.assessment.overall_score}分
                    </span>
                  )}
                  <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                    {new Date(conv.updatedAt).toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' })}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Start learning button */}
      <div className="shrink-0" style={{ padding: '20px 24px', borderTop: '1px solid rgba(0,0,0,0.08)', backgroundColor: '#ffffff' }}>
        <button
          onClick={onStartLearning}
          className="btn-primary w-full flex items-center justify-center gap-3 py-4 text-lg font-bold"
        >
          <Play size={20} />
          开始学习
        </button>
        <p className="text-sm mt-4 text-center" style={{ color: 'var(--color-text-tertiary)' }}>
          AI 将根据你的掌握程度讲解并提问
        </p>
      </div>
    </div>
  );
}
