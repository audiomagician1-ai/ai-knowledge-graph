import { MarkdownRenderer } from './MarkdownRenderer';
import { ChoiceButtons } from './ChoiceButtons';
import { InlineAssessmentCard } from './InlineAssessmentCard';
import { stripChoicesBlock } from '@/lib/utils/text';
import {
  Send, BarChart3, Brain, RotateCcw, History, Zap,
} from 'lucide-react';
import type { ChatMessage, ChoiceOption, AssessmentResult } from '@/lib/store/dialogue';

interface ChatViewProps {
  conceptName: string;
  messages: ChatMessage[];
  isStreaming: boolean;
  isAssessing: boolean;
  isInitializing: boolean;
  isBusy: boolean;
  suggestAssess: boolean;
  assessment: AssessmentResult | null;
  currentChoices: ChoiceOption[] | null;
  conversationId: string | null;
  input: string;
  userTurns: number;
  showCelebration: boolean;
  newlyUnlockedIds: string[];
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
  onInputChange: (value: string) => void;
  onSend: () => void;
  onRequestAssessment: () => void;
  onSelectChoice: (choice: string) => void;
  onViewHistory: () => void;
  onBack: () => void;
  onRestart: () => void;
}

/**
 * The active chat view — messages, input area, assessment overlay.
 * Extracted from ChatPanel to keep page files under 200 lines.
 */
export function ChatView({
  conceptName, messages, isStreaming, isAssessing, isInitializing, isBusy,
  suggestAssess, assessment, currentChoices, conversationId,
  input, userTurns, showCelebration, newlyUnlockedIds, messagesEndRef,
  onInputChange, onSend, onRequestAssessment, onSelectChoice, onViewHistory, onBack, onRestart,
}: ChatViewProps) {
  const isUserTyping = input.length > 0;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSend(); }
  };

  return (
    <div className="flex flex-col h-full relative">
      {/* Chat header */}
      <div className="flex items-center gap-3 shrink-0"
        style={{ padding: '16px 24px', borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface-1)' }}>
        <Brain size={18} style={{ color: 'var(--color-accent-primary)' }} />
        <span className="text-base font-bold flex-1 truncate" style={{ color: 'var(--color-text-primary)' }}>{conceptName}</span>
        <span className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>第 {userTurns} 轮</span>
        <button onClick={onViewHistory} className="w-10 h-10 flex items-center justify-center rounded-xl transition-colors hover:bg-white/5"
          style={{ color: 'var(--color-text-tertiary)' }} title="对话历史"><History size={18} /></button>
        {suggestAssess && !assessment && (
          <button onClick={onRequestAssessment} disabled={isBusy}
            className="btn-primary flex items-center gap-2 text-sm"
            style={{ opacity: isBusy ? 0.5 : 1, padding: '8px 18px', fontSize: '0.875rem' }}>
            <BarChart3 size={16} />
            {isAssessing ? '评估中...' : '理解度评估'}
          </button>
        )}
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto" style={{ backgroundColor: 'var(--color-surface-2)' }}>
        <div style={{ padding: '24px 24px', display: 'flex', flexDirection: 'column', gap: 20 }}>
          {isInitializing && (
            <div className="flex justify-start animate-fade-in">
              <div style={{ borderRadius: '16px 16px 16px 4px', padding: '20px 24px', backgroundColor: 'var(--color-surface-1)', color: 'var(--color-text-primary)', border: '1px solid var(--color-border)', boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }}>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'var(--color-accent-primary)', animationDelay: '0ms', animationDuration: '1.2s' }} />
                    <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'var(--color-accent-primary)', animationDelay: '150ms', animationDuration: '1.2s' }} />
                    <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'var(--color-accent-primary)', animationDelay: '300ms', animationDuration: '1.2s' }} />
                  </div>
                  <span className="text-[13px]" style={{ color: 'var(--color-text-tertiary)' }}>正在准备学习内容…</span>
                </div>
              </div>
            </div>
          )}
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div style={{
                maxWidth: '82%',
                borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                padding: '20px 24px', fontSize: 20, lineHeight: 1.85,
                ...(msg.role === 'user'
                    ? { backgroundColor: '#d4edda', color: 'var(--color-text-primary)', border: '1px solid rgba(16,185,129,0.25)' }
                    : { backgroundColor: 'var(--color-surface-1)', color: 'var(--color-text-primary)', border: '1px solid var(--color-border)', boxShadow: '0 1px 3px rgba(0,0,0,0.06)' }),
              }}>
                {msg.role === 'assistant' ? (
                  msg.content ? <MarkdownRenderer content={stripChoicesBlock(msg.content)} /> :
                  isStreaming ? (
                    <div className="flex items-center gap-1.5 mt-1">
                      <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-text-tertiary)' }} />
                      <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-text-tertiary)', animationDelay: '150ms' }} />
                      <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: 'var(--color-text-tertiary)', animationDelay: '300ms' }} />
                    </div>
                  ) : null
                ) : <div className="whitespace-pre-wrap break-words">{msg.content}</div>}
              </div>
            </div>
          ))}
          {assessment && <InlineAssessmentCard result={assessment} />}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="shrink-0" style={{ padding: '20px 24px', borderTop: '1px solid var(--color-border)', backgroundColor: 'var(--color-surface-1)' }}>
        {assessment ? (
          <div className="flex gap-3">
            <button onClick={onBack} className="btn-ghost flex-1 flex items-center justify-center gap-2 py-3 text-base">返回</button>
            <button onClick={onRestart} className="btn-primary flex-1 flex items-center justify-center gap-2 py-3 text-base">
              <RotateCcw size={16} /> 再来一轮
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {currentChoices && currentChoices.length > 0 && !isBusy && (
              <ChoiceButtons choices={currentChoices} onSelect={onSelectChoice} disabled={isBusy} dimmed={isUserTyping} />
            )}
            <div className="flex items-end gap-3 rounded-xl px-5 py-4" style={{ backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)' }}>
              <textarea
                value={input}
                onChange={(e) => { onInputChange(e.target.value); e.target.style.height = 'auto'; e.target.style.height = Math.min(e.target.scrollHeight, 150) + 'px'; }}
                onKeyDown={handleKeyDown}
                placeholder={currentChoices ? "也可以用自己的话回答..." : "输入你的回答..."}
                rows={3}
                className="flex-1 bg-transparent text-[20px] outline-none resize-none leading-relaxed"
                style={{ color: 'var(--color-text-primary)', minHeight: '4.5em', maxHeight: '150px' }}
                disabled={isBusy || !conversationId}
              />
              <button onClick={onSend} disabled={isBusy || !input.trim() || !conversationId}
                className="shrink-0 w-10 h-10 rounded-md flex items-center justify-center transition-all"
                style={{ background: !input.trim() || isBusy ? 'var(--color-surface-4)' : 'var(--color-accent-primary)', color: 'var(--color-text-on-accent)', opacity: !input.trim() || isBusy ? 0.4 : 1 }}>
                <Send size={18} />
              </button>
            </div>
          </div>
        )}
        {!assessment && <p className="text-sm mt-2.5 text-center" style={{ color: 'var(--color-text-tertiary)' }}>Enter 发送 · Shift+Enter 换行</p>}
      </div>

      {/* Mastery celebration overlay */}
      {showCelebration && (
        <div className="absolute inset-0 z-50 flex items-center justify-center pointer-events-none animate-fade-in">
          <div className="rounded-lg px-8 py-6 text-center pointer-events-auto"
            style={{ backgroundColor: 'var(--color-surface-2)', border: '1px solid rgba(138,173,122,0.2)' }}>
            <div className="text-2xl mb-2">✔</div>
            <div className="text-lg font-bold mb-1" style={{ color: 'var(--color-accent-emerald)' }}>概念已掌握！</div>
            <div className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>{conceptName} 节点已点亮</div>
            {newlyUnlockedIds.length > 0 && (
              <div className="mt-3 pt-3" style={{ borderTop: '1px solid rgba(138,173,122,0.15)' }}>
                <div className="flex items-center justify-center gap-1.5 text-xs" style={{ color: 'var(--color-accent-cyan)' }}>
                  <Zap size={13} /> <span>已解锁 {newlyUnlockedIds.length} 个新概念</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
