import { useEffect, useRef, useState } from 'react';
import { useDialogueStore } from '@/lib/store/dialogue';
import { useLearningStore } from '@/lib/store/learning';
import type { AssessmentResult, SavedConversation } from '@/lib/store/dialogue';
import type { ConceptProgress } from '@/lib/store/learning';
import { MarkdownRenderer } from './MarkdownRenderer';
import {
  Send, BarChart3, Brain, RotateCcw, Zap, Play,
  Trophy, History, Trash2, MessageSquare, X, BookOpen,
  Sparkles,
} from 'lucide-react';

interface ChatPanelProps {
  conceptId: string;
  conceptName: string;
}

type PanelView = 'idle' | 'chat' | 'history';

export function ChatPanel({ conceptId, conceptName }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const [view, setView] = useState<PanelView>('idle');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const prevConceptRef = useRef<string | null>(null);

  const {
    conversationId, messages, isStreaming, isAssessing, suggestAssess, assessment, error,
    startConversation, sendMessage, requestAssessment, reset,
    savedConversations, loadSavedConversation, deleteSavedConversation,
  } = useDialogueStore();

  const isBusy = isStreaming || isAssessing;
  const { progress, startLearning, recordAssessment, newlyUnlockedIds, clearNewlyUnlocked } = useLearningStore();
  const [showCelebration, setShowCelebration] = useState(false);

  // When concept changes → reset to idle (show history + start button)
  useEffect(() => {
    if (conceptId && conceptId !== prevConceptRef.current) {
      prevConceptRef.current = conceptId;
      reset();
      setView('idle');
      setInput('');
    }
  }, [conceptId]);

  // Record assessment + show celebration if mastered
  useEffect(() => {
    if (assessment && conceptId) {
      recordAssessment(conceptId, conceptName || conceptId, assessment.overall_score, assessment.mastered);
      if (assessment.mastered) {
        setShowCelebration(true);
        setTimeout(() => setShowCelebration(false), 4000);
      }
    }
  }, [assessment]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, assessment]);

  const handleStartLearning = () => {
    startConversation(conceptId);
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
          className="flex items-center justify-between px-5 py-3 shrink-0"
          style={{ borderBottom: '1px solid var(--color-border)' }}
        >
          <div className="flex items-center gap-2">
            <History size={16} style={{ color: 'var(--color-accent-indigo)' }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
              "{conceptName}" 的对话记录
            </span>
          </div>
          <button
            onClick={() => setView('idle')}
            className="w-8 h-8 flex items-center justify-center rounded-lg transition-colors"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            <X size={15} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {conceptConvHistory.length === 0 ? (
            <div className="p-8 text-center">
              <MessageSquare size={28} className="mx-auto mb-3" style={{ color: 'var(--color-text-tertiary)' }} />
              <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>暂无对话记录</p>
            </div>
          ) : (
            <div className="p-3 space-y-2">
              {conceptConvHistory.map((conv) => (
                <div
                  key={conv.conversationId}
                  className="group flex items-center gap-4 rounded-xl px-4 py-3 cursor-pointer transition-all"
                  style={{ border: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface-2)' }}
                  onClick={() => { loadSavedConversation(conv.conversationId); setView('chat'); }}
                  onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-accent)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; }}
                >
                  <Brain size={18} style={{ color: 'var(--color-accent-indigo)', flexShrink: 0 }} />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                        {conv.messages.length} 条消息
                      </span>
                      {conv.assessment && (
                        <span
                          className="text-sm font-bold"
                          style={{ color: conv.assessment.mastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)' }}
                        >
                          {conv.assessment.overall_score}分 {conv.assessment.mastered ? '✓' : ''}
                        </span>
                      )}
                    </div>
                    <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                      {new Date(conv.updatedAt).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteSavedConversation(conv.conversationId); }}
                    className="opacity-0 group-hover:opacity-100 w-8 h-8 flex items-center justify-center rounded-lg transition-all"
                    style={{ color: 'var(--color-accent-rose)' }}
                  >
                    <Trash2 size={14} />
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
      <div className="flex flex-col h-full">
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {/* Per-node mastery card */}
          <div
            className="rounded-xl p-5"
            style={{ backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)' }}
          >
            <div className="flex items-center gap-3 mb-4">
              <div
                className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                style={{
                  background: nodeProgress?.status === 'mastered'
                    ? 'linear-gradient(135deg, var(--color-accent-emerald), #10b981)'
                    : 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
                }}
              >
                {nodeProgress?.status === 'mastered'
                  ? <Trophy size={18} className="text-white" />
                  : <Brain size={18} className="text-white" />
                }
              </div>
              <div className="flex-1 min-w-0">
                <h4 className="text-sm font-bold" style={{ color: 'var(--color-text-primary)' }}>
                  {conceptName}
                </h4>
                <span className="text-xs" style={{
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
            <div className="grid grid-cols-3 gap-3">
              <div className="text-center rounded-lg py-2" style={{ backgroundColor: 'var(--color-surface-3)' }}>
                <div className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>
                  {nodeProgress?.sessions || 0}
                </div>
                <div className="text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>学习次数</div>
              </div>
              <div className="text-center rounded-lg py-2" style={{ backgroundColor: 'var(--color-surface-3)' }}>
                <div className="text-lg font-bold" style={{
                  color: nodeProgress?.mastery_score
                    ? (nodeProgress.mastery_score >= 75 ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)')
                    : 'var(--color-text-tertiary)',
                }}>
                  {nodeProgress?.mastery_score || '—'}
                </div>
                <div className="text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>最高分</div>
              </div>
              <div className="text-center rounded-lg py-2" style={{ backgroundColor: 'var(--color-surface-3)' }}>
                <div className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>
                  {conceptConvHistory.length}
                </div>
                <div className="text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>对话记录</div>
              </div>
            </div>
          </div>

          {/* Recent history preview (last 3) */}
          {conceptConvHistory.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold" style={{ color: 'var(--color-text-secondary)' }}>
                  最近对话
                </span>
                <button
                  onClick={() => setView('history')}
                  className="text-xs flex items-center gap-1 transition-colors"
                  style={{ color: 'var(--color-accent-indigo)' }}
                >
                  查看全部
                  <History size={12} />
                </button>
              </div>
              <div className="space-y-2">
                {conceptConvHistory.slice(0, 3).map((conv) => (
                  <div
                    key={conv.conversationId}
                    className="flex items-center gap-3 rounded-lg px-4 py-2.5 cursor-pointer transition-all"
                    style={{ backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)' }}
                    onClick={() => { loadSavedConversation(conv.conversationId); setView('chat'); }}
                    onMouseEnter={(e) => { e.currentTarget.style.borderColor = 'var(--color-border-accent)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.borderColor = 'var(--color-border)'; }}
                  >
                    <MessageSquare size={14} style={{ color: 'var(--color-text-tertiary)', flexShrink: 0 }} />
                    <span className="text-sm flex-1" style={{ color: 'var(--color-text-secondary)' }}>
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
        <div className="shrink-0 p-5" style={{ borderTop: '1px solid var(--color-border)' }}>
          <button
            onClick={handleStartLearning}
            className="btn-primary w-full flex items-center justify-center gap-3 py-3 text-base"
          >
            <Play size={18} />
            开始学习
          </button>
          <p className="text-xs mt-2 text-center" style={{ color: 'var(--color-text-tertiary)' }}>
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
        className="flex items-center gap-3 px-5 py-3 shrink-0"
        style={{ borderBottom: '1px solid var(--color-border)' }}
      >
        <Brain size={16} style={{ color: 'var(--color-accent-indigo)' }} />
        <span className="text-sm font-semibold flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>
          {conceptName}
        </span>
        <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
          第 {userTurns} 轮
        </span>
        <button
          onClick={() => setView('history')}
          className="w-8 h-8 flex items-center justify-center rounded-lg transition-colors"
          style={{ color: 'var(--color-text-tertiary)' }}
          title="对话历史"
        >
          <History size={14} />
        </button>
        {suggestAssess && !assessment && (
          <button
            onClick={requestAssessment}
            disabled={isBusy}
            className="btn-primary flex items-center gap-1.5 text-xs"
            style={{ opacity: isBusy ? 0.5 : 1, padding: '6px 14px', fontSize: '0.75rem' }}
          >
            <BarChart3 size={13} />
            {isAssessing ? '评估中...' : '理解度评估'}
          </button>
        )}
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-5 py-4 space-y-4">
          {/* Messages */}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className="max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed"
                style={
                  msg.role === 'user'
                    ? {
                        background: 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
                        color: '#fff',
                        borderBottomRightRadius: 6,
                      }
                    : {
                        backgroundColor: 'var(--color-surface-2)',
                        color: 'var(--color-text-primary)',
                        borderBottomLeftRadius: 6,
                        border: '1px solid var(--color-border)',
                      }
                }
              >
                {msg.role === 'assistant' ? (
                  msg.content ? (
                    <MarkdownRenderer content={msg.content} />
                  ) : isStreaming ? (
                    <div className="flex items-center gap-1.5 mt-1">
                      <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-accent-indigo)' }} />
                      <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-accent-violet)', animationDelay: '150ms' }} />
                      <span className="w-2 h-2 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-accent-cyan)', animationDelay: '300ms' }} />
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
      <div className="shrink-0 px-5 py-3" style={{ borderTop: '1px solid var(--color-border)' }}>
        {assessment ? (
          <div className="flex gap-3">
            <button
              onClick={() => setView('idle')}
              className="btn-ghost flex-1 flex items-center justify-center gap-2 py-2.5 text-sm"
            >
              返回
            </button>
            <button
              onClick={() => { reset(); handleStartLearning(); }}
              className="btn-primary flex-1 flex items-center justify-center gap-2 py-2.5 text-sm"
            >
              <RotateCcw size={14} />
              再来一轮
            </button>
          </div>
        ) : (
          <div
            className="flex items-end gap-3 rounded-xl px-4 py-3"
            style={{
              backgroundColor: 'var(--color-surface-2)',
              border: '1px solid var(--color-border)',
            }}
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="输入你的回答..."
              rows={1}
              className="flex-1 bg-transparent text-sm outline-none resize-none leading-relaxed"
              style={{
                color: 'var(--color-text-primary)',
                maxHeight: '100px',
              }}
              disabled={isBusy || !conversationId}
            />
            <button
              onClick={handleSend}
              disabled={isBusy || !input.trim() || !conversationId}
              className="shrink-0 w-9 h-9 rounded-lg flex items-center justify-center transition-all"
              style={{
                background: !input.trim() || isBusy
                  ? 'var(--color-surface-4)'
                  : 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
                color: '#fff',
                opacity: !input.trim() || isBusy ? 0.4 : 1,
              }}
            >
              <Send size={15} />
            </button>
          </div>
        )}
        {!assessment && (
          <p className="text-[11px] mt-2 text-center" style={{ color: 'var(--color-text-tertiary)' }}>
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
            className="rounded-2xl px-8 py-6 text-center pointer-events-auto"
            style={{
              background: 'linear-gradient(135deg, rgba(52, 211, 153, 0.15), rgba(16, 185, 129, 0.1))',
              border: '1px solid rgba(52, 211, 153, 0.3)',
              backdropFilter: 'blur(16px)',
              boxShadow: '0 0 60px rgba(52, 211, 153, 0.2)',
            }}
          >
            <div className="text-4xl mb-3">🎉</div>
            <div className="text-lg font-bold mb-1" style={{ color: 'var(--color-accent-emerald)' }}>
              概念已掌握！
            </div>
            <div className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
              {conceptName} 节点已点亮
            </div>
            {newlyUnlockedIds.length > 0 && (
              <div className="mt-3 pt-3" style={{ borderTop: '1px solid rgba(52, 211, 153, 0.15)' }}>
                <div className="flex items-center justify-center gap-1.5 text-xs" style={{ color: '#22d3ee' }}>
                  <Sparkles size={13} />
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

/** Compact assessment card for inline display */
function InlineAssessmentCard({ result }: { result: AssessmentResult }) {
  const scoreColor = (s: number) => {
    if (s >= 80) return 'var(--color-accent-emerald)';
    if (s >= 60) return 'var(--color-accent-amber)';
    return 'var(--color-accent-rose)';
  };

  const dims = [
    { label: '完整性', key: 'completeness' as const },
    { label: '准确性', key: 'accuracy' as const },
    { label: '深度', key: 'depth' as const },
    { label: '举例', key: 'examples' as const },
  ];

  return (
    <div
      className="rounded-xl p-5 animate-fade-in"
      style={{
        backgroundColor: result.mastered ? 'rgba(52, 211, 153, 0.08)' : 'var(--color-surface-2)',
        border: `1px solid ${result.mastered ? 'rgba(52, 211, 153, 0.2)' : 'var(--color-border)'}`,
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {result.mastered ? (
            <Trophy size={18} style={{ color: 'var(--color-accent-emerald)' }} />
          ) : (
            <BarChart3 size={18} style={{ color: 'var(--color-accent-amber)' }} />
          )}
          <span className="text-base font-bold" style={{ color: 'var(--color-text-primary)' }}>
            {result.mastered ? '已掌握！' : '评估结果'}
          </span>
        </div>
        <span className="text-2xl font-bold" style={{ color: scoreColor(result.overall_score) }}>
          {result.overall_score}
          <span className="text-xs font-normal ml-0.5" style={{ color: 'var(--color-text-tertiary)' }}>/100</span>
        </span>
      </div>

      <div className="space-y-2.5 mb-4">
        {dims.map((dim) => {
          const score = result[dim.key];
          return (
            <div key={dim.key} className="flex items-center gap-3">
              <span className="text-sm w-12 shrink-0" style={{ color: 'var(--color-text-tertiary)' }}>
                {dim.label}
              </span>
              <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-4)' }}>
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${score}%`, backgroundColor: scoreColor(score) }}
                />
              </div>
              <span className="text-sm w-8 text-right font-semibold" style={{ color: scoreColor(score) }}>
                {score}
              </span>
            </div>
          );
        })}
      </div>

      <p className="text-sm leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
        {result.feedback}
      </p>

      {result.gaps.length > 0 && (
        <div className="mt-3 pt-3" style={{ borderTop: '1px solid var(--color-border-subtle)' }}>
          <p className="text-xs font-semibold mb-1.5" style={{ color: 'var(--color-accent-amber)' }}>知识盲区</p>
          <ul className="space-y-1">
            {result.gaps.map((gap, i) => (
              <li key={i} className="flex items-start gap-2 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
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