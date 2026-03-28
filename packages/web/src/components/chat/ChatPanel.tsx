import { useEffect, useRef, useState } from 'react';
import { createLogger } from '@/lib/utils/logger';
import { useDialogueStore } from '@/lib/store/dialogue';
import { useLearningStore } from '@/lib/store/learning';
import { useAchievementStore } from '@/lib/store/achievements';
import type { AssessmentResult, SavedConversation } from '@/lib/store/dialogue';
import type { ConceptProgress } from '@/lib/store/learning';
import { MarkdownRenderer } from './MarkdownRenderer';
import { ChoiceButtons } from './ChoiceButtons';
import { stripChoicesBlock } from '@/lib/utils/text';
import { useCountUp } from '@/lib/hooks/useCountUp';
import {
  Send, BarChart3, Brain, RotateCcw, Zap, Play,
  Trophy, History, Trash2, MessageSquare, X,
} from 'lucide-react';

const log = createLogger('ChatPanel');

interface ChatPanelProps {
  conceptId: string;
  conceptName: string;
  domainId?: string;
}

type PanelView = 'idle' | 'chat' | 'history';

export function ChatPanel({ conceptId, conceptName, domainId }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const [view, setView] = useState<PanelView>('idle');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const prevConceptRef = useRef<string | null>(null);

  const {
    conversationId, messages, isStreaming, isAssessing, isInitializing, suggestAssess, assessment, error,
    currentChoices,
    startConversation, sendMessage, selectChoice, requestAssessment, cancelStream, reset,
    savedConversations, loadSavedConversation, deleteSavedConversation,
  } = useDialogueStore();

  const isBusy = isStreaming || isAssessing;
  const isUserTyping = input.length > 0;
  const { progress, startLearning, recordAssessment, newlyUnlockedIds } = useLearningStore();
  const { checkNewAchievements } = useAchievementStore();
  const [showCelebration, setShowCelebration] = useState(false);
  // C-01 fix: prevent duplicate recordAssessment calls (same guard as LearnPage)
  const recordedConvRef = useRef<string | null>(null);

  // M-01: Cancel active stream on unmount to prevent stale callbacks writing to store
  // (LearnPage has this via cleanup in [conceptId] effect, ChatPanel was missing it)
  useEffect(() => {
    return () => { cancelStream(); reset(); };
  // eslint-disable-next-line react-hooks/exhaustive-deps -- cleanup-only, stable refs
  }, []);

  // When concept changes → reset to idle (show history + start button)
  useEffect(() => {
    if (conceptId && conceptId !== prevConceptRef.current) {
      prevConceptRef.current = conceptId;
      recordedConvRef.current = null;
      reset();
      setView('idle');
      setInput('');
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- Zustand actions are stable refs
  }, [conceptId]);

  // Record assessment + show celebration if mastered
  useEffect(() => {
    if (assessment && conceptId && conversationId && recordedConvRef.current !== conversationId) {
      recordedConvRef.current = conversationId;
      recordAssessment(conceptId, conceptName || conceptId, assessment.overall_score, assessment.mastered);
      // Check for newly unlocked achievements after assessment
      checkNewAchievements();
      if (assessment.mastered) {
        setShowCelebration(true);
        const timer = setTimeout(() => setShowCelebration(false), 4000);
        return () => clearTimeout(timer);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- Zustand actions are stable refs
  }, [assessment, conversationId]);

  // Auto-scroll — also trigger when choices appear (so user doesn't need to scroll manually)
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, assessment, currentChoices]);

  // m-01: Auto-dismiss error after 6 seconds (consistent with LearnPage)
  useEffect(() => {
    if (!error) return;
    const timer = setTimeout(() => useDialogueStore.setState({ error: null }), 6000);
    return () => clearTimeout(timer);
  }, [error]);

  const handleStartLearning = () => {
    startConversation(conceptId, domainId);
    startLearning(conceptId);
    setView('chat');
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isBusy) return;
    setInput('');
    await sendMessage(text);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const userTurns = messages.filter((m) => m.role === 'user').length;

  // This concept's history
  const conceptConvHistory = savedConversations
    .filter(c => c.conceptId === conceptId)
    .sort((a, b) => b.updatedAt - a.updatedAt);

  // This concept's progress
  const nodeProgress: ConceptProgress | null = progress[conceptId] || null;

  /* ─── HISTORY VIEW ─── */
  if (view === 'history') {
    return (
      <div className="flex flex-col h-full">
        <div
          className="flex items-center justify-between px-8 py-6 shrink-0"
          style={{ borderBottom: '1px solid var(--color-border)' }}
        >
          <div className="flex items-center gap-3">
            <History size={18} style={{ color: 'var(--color-accent-primary)' }} />
            <span className="text-base font-bold" style={{ color: 'var(--color-text-primary)' }}>
              "{conceptName}" 的对话记录
            </span>
          </div>
          <button
            onClick={() => setView('idle')}
            className="w-10 h-10 flex items-center justify-center rounded-xl transition-colors hover:bg-white/5"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {conceptConvHistory.length === 0 ? (
            <div className="p-8 text-center">
              <MessageSquare size={32} className="mx-auto mb-4" style={{ color: 'var(--color-text-tertiary)' }} />
              <p className="text-base" style={{ color: 'var(--color-text-tertiary)' }}>暂无对话记录</p>
            </div>
          ) : (
            <div className="p-4 space-y-3">
              {conceptConvHistory.map((conv) => (
                <div
                  key={conv.conversationId}
                  className="group flex items-center gap-4 rounded-xl px-6 py-5 cursor-pointer transition-all"
                  style={{ border: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface-2)' }}
                  onClick={() => { loadSavedConversation(conv.conversationId); setView('chat'); }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-accent)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; }}
                >
                   <Brain size={20} style={{ color: 'var(--color-accent-primary)', flexShrink: 0 }} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <span className="text-[15px]" style={{ color: 'var(--color-text-secondary)' }}>
                        {conv.messages.length} 条消息
                      </span>
                      {conv.assessment && (
                        <span
                          className="text-[15px] font-bold"
                          style={{ color: conv.assessment.mastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)' }}
                        >
                          {conv.assessment.overall_score}分 {conv.assessment.mastered ? '✓' : ''}
                        </span>
                      )}
                    </div>
                    <span className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
                      {new Date(conv.updatedAt).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteSavedConversation(conv.conversationId); }}
                    className="opacity-0 group-hover:opacity-100 w-10 h-10 flex items-center justify-center rounded-xl transition-all"
                    style={{ color: 'var(--color-accent-rose)' }}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  /* ─── IDLE VIEW: per-node progress + history + start button ─── */
  if (view === 'idle') {
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
                  {conceptConvHistory.length}
                </div>
                <div className="text-sm mt-2" style={{ color: 'var(--color-text-tertiary)' }}>对话记录</div>
              </div>
            </div>
          </div>

          {/* Recent history preview (last 3) */}
          {conceptConvHistory.length > 0 && (
            <div className="rounded-xl" style={{ backgroundColor: '#ffffff', border: '1px solid rgba(0,0,0,0.08)', boxShadow: '0 1px 3px rgba(0,0,0,0.06)', padding: '20px 24px' }}>
              <div className="flex items-center justify-between" style={{ marginBottom: 16 }}>
                <span className="text-sm font-bold" style={{ color: 'var(--color-text-secondary)' }}>
                  最近对话
                </span>
                <button
                  onClick={() => setView('history')}
                  className="text-sm flex items-center gap-1.5 transition-colors"
                  style={{ color: 'var(--color-accent-primary)' }}
                >
                  查看全部
                  <History size={14} />
                </button>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {conceptConvHistory.slice(0, 3).map((conv) => (
                  <div
                    key={conv.conversationId}
                    className="flex items-center gap-4 rounded-lg cursor-pointer transition-all"
                    style={{ backgroundColor: '#f5f5f3', padding: '14px 18px', border: '1px solid transparent' }}
                    onClick={() => { loadSavedConversation(conv.conversationId); setView('chat'); }}
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
            onClick={handleStartLearning}
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

  /* ─── CHAT VIEW ─── */
  return (
    <div className="flex flex-col h-full relative">
      {/* Chat header */}
      <div
        className="flex items-center gap-3 shrink-0"
        style={{ padding: '16px 24px', borderBottom: '1px solid rgba(0,0,0,0.08)', backgroundColor: '#ffffff' }}
      >
            <Brain size={18} style={{ color: 'var(--color-accent-primary)' }} />
        <span className="text-base font-bold flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>
          {conceptName}
        </span>
        <span className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
          第 {userTurns} 轮
        </span>
        <button
          onClick={() => setView('history')}
          className="w-10 h-10 flex items-center justify-center rounded-xl transition-colors hover:bg-white/5"
          style={{ color: 'var(--color-text-tertiary)' }}
          title="对话历史"
        >
          <History size={18} />
        </button>
        {suggestAssess && !assessment && (
          <button
            onClick={requestAssessment}
            disabled={isBusy}
            className="btn-primary flex items-center gap-2 text-sm"
            style={{ opacity: isBusy ? 0.5 : 1, padding: '8px 18px', fontSize: '0.875rem' }}
          >
            <BarChart3 size={16} />
            {isAssessing ? '评估中...' : '理解度评估'}
          </button>
        )}
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto" style={{ backgroundColor: 'var(--color-surface-2)' }}>
        <div style={{ padding: '24px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
          {/* Loading indicator while LLM prepares opening content */}
          {isInitializing && (
            <div className="flex justify-start animate-fade-in">
              <div
                style={{
                  borderRadius: '16px 16px 16px 4px',
                  padding: '20px 24px',
                  backgroundColor: '#ffffff',
                  color: 'var(--color-text-primary)',
                  border: '1px solid rgba(0, 0, 0, 0.1)',
                  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
                }}
              >
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'var(--color-accent-primary)', animationDelay: '0ms', animationDuration: '1.2s' }} />
                    <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'var(--color-accent-primary)', animationDelay: '150ms', animationDuration: '1.2s' }} />
                    <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'var(--color-accent-primary)', animationDelay: '300ms', animationDuration: '1.2s' }} />
                  </div>
                  <span className="text-[13px]" style={{ color: 'var(--color-text-tertiary)' }}>
                    正在准备学习内容…
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                style={{
                  maxWidth: '82%',
                  borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                  padding: '20px 24px',
                  fontSize: 20,
                  lineHeight: 1.85,
                  ...(msg.role === 'user'
                    ? {
                        backgroundColor: '#d4edda',
                        color: 'var(--color-text-primary)',
                        border: '1px solid rgba(16, 185, 129, 0.25)',
                      }
                    : {
                        backgroundColor: '#ffffff',
                        color: 'var(--color-text-primary)',
                        border: '1px solid rgba(0, 0, 0, 0.1)',
                        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
                      }),
                }}
              >
                {msg.role === 'assistant' ? (
                  msg.content ? (
                    <MarkdownRenderer content={stripChoicesBlock(msg.content)} />
                  ) : isStreaming ? (
                    <div className="flex items-center gap-1.5 mt-1">
                      <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-text-tertiary)' }} />
                      <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-text-tertiary)', animationDelay: '150ms' }} />
                      <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-text-tertiary)', animationDelay: '300ms' }} />
                    </div>
                  ) : null
                ) : (
                  <div className="whitespace-pre-wrap break-words">{msg.content}</div>
                )}
              </div>
            </div>
          ))}

          {/* Inline assessment result */}
              {assessment && <InlineAssessmentCard result={assessment} />}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="shrink-0" style={{ padding: '20px 24px', borderTop: '1px solid rgba(0,0,0,0.08)', backgroundColor: '#ffffff' }}>
        {assessment ? (
          <div className="flex gap-3">
            <button
              onClick={() => setView('idle')}
              className="btn-ghost flex-1 flex items-center justify-center gap-2 py-3 text-base"
            >
              返回
            </button>
            <button
              onClick={() => { reset(); handleStartLearning(); }}
              className="btn-primary flex-1 flex items-center justify-center gap-2 py-3 text-base"
            >
              <RotateCcw size={16} />
              再来一轮
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Choice buttons — shown when AI provides choices */}
            {currentChoices && currentChoices.length > 0 && !isBusy && (
              <ChoiceButtons
                choices={currentChoices}
                onSelect={selectChoice}
                disabled={isBusy}
                dimmed={isUserTyping}
              />
            )}
            <div
              className="flex items-end gap-3 rounded-xl px-5 py-4"
              style={{
                backgroundColor: '#f5f5f3',
                border: '1px solid rgba(0, 0, 0, 0.1)',
              }}
            >
              <textarea
                value={input}
                onChange={(e) => {
                  setInput(e.target.value);
                  // Auto-resize
                  e.target.style.height = 'auto';
                  e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px';
                }}
                onKeyDown={handleKeyDown}
                placeholder={currentChoices ? "也可以用自己的话回答..." : "输入你的回答..."}
                rows={3}
                className="flex-1 bg-transparent text-[20px] outline-none resize-none leading-relaxed"
                style={{
                  color: 'var(--color-text-primary)',
                  minHeight: '4.5em',
                  maxHeight: '150px',
                }}
                disabled={isBusy || !conversationId}
              />
              <button
                onClick={handleSend}
                disabled={isBusy || !input.trim() || !conversationId}
                className="shrink-0 w-10 h-10 rounded-md flex items-center justify-center transition-all"
                style={{
                    background: !input.trim() || isBusy
                      ? 'var(--color-surface-4)'
                      : 'var(--color-accent-primary)',
                  color: '#ffffff',
                  opacity: !input.trim() || isBusy ? 0.4 : 1,
                }}
              >
                <Send size={18} />
              </button>
            </div>
          </div>
        )}
        {!assessment && (
          <p className="text-sm mt-2.5 text-center" style={{ color: 'var(--color-text-tertiary)' }}>
            Enter 发送 · Shift+Enter 换行
          </p>
        )}
      </div>

      {/* Error toast */}
      {error && (
        <div
          className="absolute bottom-24 left-5 right-5 z-50 rounded-xl px-4 py-3 text-sm animate-fade-in"
          style={{ backgroundColor: 'rgba(244, 63, 94, 0.12)', color: 'var(--color-accent-rose)', border: '1px solid rgba(244, 63, 94, 0.2)' }}
        >
          {error}
        </div>
      )}

      {/* Mastery celebration overlay */}
      {showCelebration && (
        <div className="absolute inset-0 z-50 flex items-center justify-center pointer-events-none animate-fade-in">
          <div
            className="rounded-lg px-8 py-6 text-center pointer-events-auto"
            style={{
              backgroundColor: 'var(--color-surface-2)',
              border: '1px solid rgba(138, 173, 122, 0.2)',
            }}
          >
            <div className="text-2xl mb-2" style={{ fontFamily: '"Noto Serif SC", Georgia, serif' }}>✔</div>
            <div className="text-lg font-bold mb-1" style={{ color: 'var(--color-accent-emerald)' }}>
              概念已掌握！
            </div>
            <div className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
              {conceptName} 节点已点亮
            </div>
            {newlyUnlockedIds.length > 0 && (
              <div className="mt-3 pt-3" style={{ borderTop: '1px solid rgba(138, 173, 122, 0.15)' }}>
                <div className="flex items-center justify-center gap-1.5 text-xs" style={{ color: 'var(--color-accent-cyan)' }}>
                  <Zap size={13} />
                  <span>已解锁 {newlyUnlockedIds.length} 个新概念</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/** Compact assessment card with animated scores */
function InlineAssessmentCard({ result }: { result: AssessmentResult }) {
  const scoreColor = (s: number) => {
    if (s >= 80) return 'var(--color-accent-emerald)';
    if (s >= 60) return 'var(--color-accent-amber)';
    return 'var(--color-accent-rose)';
  };

  const animatedOverall = useCountUp(result.overall_score, 1000, 200);

  const dims = [
    { label: '完整性', key: 'completeness' as const, delay: 300 },
    { label: '准确性', key: 'accuracy' as const, delay: 450 },
    { label: '深度', key: 'depth' as const, delay: 600 },
    { label: '举例', key: 'examples' as const, delay: 750 },
  ];

  return (
    <div
      className="rounded-lg p-5 animate-fade-in-scale"
      style={{
        backgroundColor: result.mastered ? 'rgba(138, 173, 122, 0.06)' : 'var(--color-surface-2)',
        border: `1px solid ${result.mastered ? 'rgba(138, 173, 122, 0.15)' : 'var(--color-border)'}`,
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {result.mastered ? (
            <Trophy size={18} style={{ color: 'var(--color-accent-emerald)' }} />
          ) : (
            <BarChart3 size={18} style={{ color: 'var(--color-accent-amber)' }} />
          )}
          <span className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>
            {result.mastered ? '已掌握！' : '评估结果'}
          </span>
        </div>
        <span className="text-3xl font-bold tabular-nums" style={{ color: scoreColor(result.overall_score) }}>
          {animatedOverall}
          <span className="text-sm font-normal ml-1" style={{ color: 'var(--color-text-tertiary)' }}>/100</span>
        </span>
      </div>

      <div className="space-y-3 mb-5">
        {dims.map((dim) => {
          const score = result[dim.key];
          return <AnimatedDimBar key={dim.key} label={dim.label} score={score} delay={dim.delay} scoreColor={scoreColor} />;
        })}
      </div>

      <p className="text-base leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
        {result.feedback}
      </p>

      {result.gaps.length > 0 && (
        <div className="mt-3 pt-3" style={{ borderTop: '1px solid var(--color-border-subtle)' }}>
          <p className="text-sm font-bold mb-2" style={{ color: 'var(--color-accent-amber)' }}>知识盲区</p>
          <ul className="space-y-1">
            {result.gaps.map((gap, i) => (
              <li key={i} className="flex items-start gap-2.5 text-[15px]" style={{ color: 'var(--color-text-secondary)' }}>
                <span className="mt-2 w-1 h-1 rounded-full shrink-0" style={{ backgroundColor: 'var(--color-accent-amber)' }} />
                {gap}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

/** Single dimension bar with staggered fill animation */
function AnimatedDimBar({ label, score, delay, scoreColor }: {
  label: string; score: number; delay: number;
  scoreColor: (s: number) => string;
}) {
  const animVal = useCountUp(score, 800, delay);
  return (
    <div className="flex items-center gap-4">
      <span className="text-[15px] w-14 shrink-0" style={{ color: 'var(--color-text-tertiary)' }}>
        {label}
      </span>
      <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-4)' }}>
        <div
          className="h-full rounded-full"
          style={{
            width: `${animVal}%`,
            backgroundColor: scoreColor(score),
            transition: 'none',
          }}
        />
      </div>
      <span className="text-[15px] w-10 text-right font-bold tabular-nums" style={{ color: scoreColor(score) }}>
        {animVal}
      </span>
    </div>
  );
}