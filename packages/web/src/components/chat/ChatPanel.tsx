import { useEffect, useRef, useState } from 'react';
import { useDialogueStore } from '@/lib/store/dialogue';
import { useLearningStore } from '@/lib/store/learning';
import type { AssessmentResult } from '@/lib/store/dialogue';
import {
  Send, BarChart3, Brain, Lightbulb, RotateCcw, Zap,
  Trophy, CheckCircle2, Target, BookOpen, Sparkles,
  History, Trash2, MessageSquare, X, ChevronDown,
} from 'lucide-react';

interface ChatPanelProps {
  conceptId: string;
  conceptName: string;
}

type PanelView = 'chat' | 'history';

export function ChatPanel({ conceptId, conceptName }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const [view, setView] = useState<PanelView>('chat');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    conversationId, messages, isStreaming, isAssessing, suggestAssess, assessment, error,
    startConversation, sendMessage, requestAssessment, cancelStream, reset,
    savedConversations, loadSavedConversation, deleteSavedConversation,
  } = useDialogueStore();

  const isBusy = isStreaming || isAssessing;
  const { startLearning, recordAssessment } = useLearningStore();

  // Start conversation when concept changes
  useEffect(() => {
    if (conceptId) {
      reset();
      startConversation(conceptId);
      startLearning(conceptId);
    }
    return () => { /* don't reset on unmount to preserve state */ };
  }, [conceptId]);

  // Record assessment results
  useEffect(() => {
    if (assessment && conceptId) {
      recordAssessment(conceptId, conceptName || conceptId, assessment.overall_score, assessment.mastered);
    }
  }, [assessment]);

  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, assessment]);

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

  // Filter history for this concept
  const conceptHistory = savedConversations
    .filter(c => c.conceptId === conceptId)
    .sort((a, b) => b.updatedAt - a.updatedAt);

  const allHistory = [...savedConversations].sort((a, b) => b.updatedAt - a.updatedAt);

  if (view === 'history') {
    return (
      <div className="flex flex-col h-full">
        {/* History header */}
        <div
          className="flex items-center justify-between px-4 py-3 shrink-0"
          style={{ borderBottom: '1px solid var(--color-border)' }}
        >
          <div className="flex items-center gap-2">
            <History size={16} style={{ color: 'var(--color-accent-indigo)' }} />
            <span className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
              对话历史
            </span>
          </div>
          <button
            onClick={() => setView('chat')}
            className="w-7 h-7 flex items-center justify-center rounded-lg transition-colors"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            <X size={14} />
          </button>
        </div>

        {/* History list */}
        <div className="flex-1 overflow-y-auto">
          {allHistory.length === 0 ? (
            <div className="p-6 text-center">
              <MessageSquare size={24} className="mx-auto mb-2" style={{ color: 'var(--color-text-tertiary)' }} />
              <p className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>暂无对话记录</p>
            </div>
          ) : (
            <div className="py-2">
              {allHistory.map((conv) => (
                <div
                  key={conv.conversationId}
                  className="group flex items-center gap-3 px-4 py-3 cursor-pointer transition-colors"
                  style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
                  onClick={() => { loadSavedConversation(conv.conversationId); setView('chat'); }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>
                      {conv.conceptName}
                    </div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                        {conv.messages.length} 条消息
                      </span>
                      {conv.assessment && (
                        <span
                          className="text-xs font-semibold"
                          style={{ color: conv.assessment.mastered ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)' }}
                        >
                          {conv.assessment.overall_score}分
                        </span>
                      )}
                      <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
                        {new Date(conv.updatedAt).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteSavedConversation(conv.conversationId); }}
                    className="opacity-0 group-hover:opacity-100 w-7 h-7 flex items-center justify-center rounded-lg transition-all"
                    style={{ color: 'var(--color-accent-rose)' }}
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Chat header */}
      <div
        className="flex items-center gap-2 px-4 py-2.5 shrink-0"
        style={{ borderBottom: '1px solid var(--color-border)' }}
      >
        <Brain size={15} style={{ color: 'var(--color-accent-indigo)' }} />
        <span className="text-sm font-semibold flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>
          {conceptName || '选择节点开始'}
        </span>
        <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
          第 {userTurns} 轮
        </span>
        {/* History toggle */}
        <button
          onClick={() => setView('history')}
          className="w-7 h-7 flex items-center justify-center rounded-lg transition-colors"
          style={{ color: 'var(--color-text-tertiary)' }}
          title="对话历史"
        >
          <History size={14} />
        </button>
        {suggestAssess && !assessment && (
          <button
            onClick={requestAssessment}
            disabled={isBusy}
            className="btn-primary flex items-center gap-1.5 px-3 py-1.5 text-xs"
            style={{ opacity: isBusy ? 0.5 : 1, fontSize: '0.7rem', padding: '4px 10px' }}
          >
            <BarChart3 size={12} />
            {isAssessing ? '评估中...' : '评估'}
          </button>
        )}
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        <div className="px-4 py-3 space-y-3">
          {/* Tip card */}
          {messages.length <= 1 && (
            <div
              className="rounded-xl px-3.5 py-2.5 flex items-start gap-3"
              style={{ backgroundColor: 'var(--color-surface-3)', border: '1px solid var(--color-border)' }}
            >
              <Lightbulb size={15} className="shrink-0 mt-0.5" style={{ color: 'var(--color-accent-amber)' }} />
              <p className="text-xs leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                用你自己的话向 AI 解释这个概念，AI 会追问帮你发现知识盲区。
              </p>
            </div>
          )}

          {/* Messages */}
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className="max-w-[88%] rounded-xl px-3.5 py-2.5 text-sm leading-relaxed"
                style={
                  msg.role === 'user'
                    ? {
                        background: 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
                        color: '#fff',
                        borderBottomRightRadius: 4,
                      }
                    : {
                        backgroundColor: 'var(--color-surface-3)',
                        color: 'var(--color-text-primary)',
                        borderBottomLeftRadius: 4,
                        border: '1px solid var(--color-border)',
                      }
                }
              >
                <div className="whitespace-pre-wrap break-words">{msg.content}</div>
                {msg.role === 'assistant' && msg.content === '' && isStreaming && (
                  <div className="flex items-center gap-1 mt-1">
                    <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-accent-indigo)' }} />
                    <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-accent-violet)', animationDelay: '150ms' }} />
                    <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-accent-cyan)', animationDelay: '300ms' }} />
                  </div>
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
      <div
        className="shrink-0 px-3 py-2.5"
        style={{ borderTop: '1px solid var(--color-border)' }}
      >
        {assessment ? (
          <button
            onClick={() => { reset(); startConversation(conceptId); }}
            className="btn-primary w-full flex items-center justify-center gap-2 py-2.5 text-sm"
          >
            <RotateCcw size={14} />
            再来一轮
          </button>
        ) : (
          <div
            className="flex items-end gap-2 rounded-xl px-3 py-2"
            style={{
              backgroundColor: 'var(--color-surface-3)',
              border: '1px solid var(--color-border)',
            }}
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="用你的话解释..."
              rows={1}
              className="flex-1 bg-transparent text-sm outline-none resize-none leading-relaxed"
              style={{
                color: 'var(--color-text-primary)',
                maxHeight: '80px',
              }}
              disabled={isBusy || !conversationId}
            />
            <button
              onClick={handleSend}
              disabled={isBusy || !input.trim() || !conversationId}
              className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-all"
              style={{
                background: !input.trim() || isBusy
                  ? 'var(--color-surface-4)'
                  : 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
                color: '#fff',
                opacity: !input.trim() || isBusy ? 0.4 : 1,
              }}
            >
              <Send size={14} />
            </button>
          </div>
        )}
        <p className="text-[10px] mt-1.5 text-center" style={{ color: 'var(--color-text-tertiary)' }}>
          Enter 发送 · 4 轮后可评估理解度
        </p>
      </div>

      {/* Error toast */}
      {error && (
        <div
          className="absolute bottom-20 left-4 right-4 z-50 rounded-lg px-3 py-2 text-xs animate-fade-in"
          style={{ backgroundColor: 'rgba(244, 63, 94, 0.15)', color: 'var(--color-accent-rose)' }}
        >
          {error}
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
      className="rounded-xl p-3.5 animate-fade-in"
      style={{
        backgroundColor: result.mastered ? 'rgba(52, 211, 153, 0.08)' : 'var(--color-surface-3)',
        border: `1px solid ${result.mastered ? 'rgba(52, 211, 153, 0.2)' : 'var(--color-border)'}`,
      }}
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          {result.mastered ? (
            <Trophy size={16} style={{ color: 'var(--color-accent-emerald)' }} />
          ) : (
            <BarChart3 size={16} style={{ color: 'var(--color-accent-amber)' }} />
          )}
          <span className="text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {result.mastered ? '已掌握！' : '评估结果'}
          </span>
        </div>
        <span className="text-xl font-bold" style={{ color: scoreColor(result.overall_score) }}>
          {result.overall_score}
          <span className="text-xs font-normal" style={{ color: 'var(--color-text-tertiary)' }}>/100</span>
        </span>
      </div>

      {/* Compact dimension bars */}
      <div className="space-y-2 mb-3">
        {dims.map((dim) => {
          const score = result[dim.key];
          return (
            <div key={dim.key} className="flex items-center gap-2">
              <span className="text-xs w-10 shrink-0" style={{ color: 'var(--color-text-tertiary)' }}>
                {dim.label}
              </span>
              <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-4)' }}>
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{ width: `${score}%`, backgroundColor: scoreColor(score) }}
                />
              </div>
              <span className="text-xs w-6 text-right font-mono" style={{ color: scoreColor(score) }}>
                {score}
              </span>
            </div>
          );
        })}
      </div>

      {/* Feedback */}
      <p className="text-xs leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
        {result.feedback}
      </p>
    </div>
  );
}