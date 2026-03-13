import { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDialogueStore } from '@/lib/store/dialogue';
import { useLearningStore } from '@/lib/store/learning';
import type { AssessmentResult } from '@/lib/store/dialogue';
import {
  ArrowLeft, Star, Send, BarChart3, Brain, Lightbulb,
  RotateCcw, ArrowRight, Zap, AlertTriangle, Trophy,
  CheckCircle2, Target, BookOpen, Sparkles,
} from 'lucide-react';

export function LearnPage() {
  const { conceptId } = useParams<{ conceptId: string }>();
  const navigate = useNavigate();
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const {
    conversationId, conceptName, isMilestone,
    messages, isStreaming, isAssessing, suggestAssess, assessment, error,
    startConversation, sendMessage, requestAssessment, cancelStream, reset,
  } = useDialogueStore();

  const isBusy = isStreaming || isAssessing;
  const { startLearning, recordAssessment } = useLearningStore();

  useEffect(() => {
    if (conceptId) {
      startConversation(conceptId);
      startLearning(conceptId);
    }
    return () => reset();
  }, [conceptId]);

  useEffect(() => {
    if (assessment && conceptId) {
      recordAssessment(conceptId, conceptName || conceptId, assessment.overall_score, assessment.mastered);
    }
  }, [assessment]);

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

  return (
    <div className="flex h-dvh" style={{ backgroundColor: 'var(--color-surface-0)' }}>

      {/* ── Main chat area ── */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Header */}
        <header
          className="flex items-center gap-4 px-6 shrink-0 border-b"
          style={{
            height: '64px',
            backgroundColor: 'var(--color-surface-1)',
            borderColor: 'var(--color-border)',
          }}
        >
          <button
            onClick={() => navigate('/graph')}
            className="flex items-center justify-center w-9 h-9 rounded-xl transition-colors"
            style={{ color: 'var(--color-text-secondary)' }}
            onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
            onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
          >
            <ArrowLeft size={18} />
          </button>

          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              {isMilestone && <Star size={14} fill="var(--color-accent-amber)" style={{ color: 'var(--color-accent-amber)' }} />}
              <h1 className="text-[15px] font-bold truncate" style={{ color: 'var(--color-text-primary)' }}>
                {conceptName || conceptId}
              </h1>
            </div>
            <p className="text-[12px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
              Feynman Dialogue · Round {userTurns}
            </p>
          </div>

          {suggestAssess && !assessment && (
            <button
              onClick={requestAssessment}
              disabled={isBusy}
              className="btn-primary flex items-center gap-2 px-4 py-2 text-[13px]"
              style={{ opacity: isBusy ? 0.5 : 1 }}
            >
              <BarChart3 size={14} />
              {isAssessing ? '评估中...' : '理解度评估'}
            </button>
          )}
        </header>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-6 py-6 space-y-5">

            {/* Guide card */}
            <div
              className="gradient-border animate-fade-in"
              style={{ padding: 0 }}
            >
              <div
                className="rounded-2xl px-5 py-4 flex items-start gap-4"
                style={{ backgroundColor: 'var(--color-surface-2)' }}
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
                  style={{ background: 'linear-gradient(135deg, var(--color-accent-amber), #f97316)', boxShadow: '0 4px 12px rgba(251, 191, 36, 0.2)' }}
                >
                  <Lightbulb size={18} className="text-white" />
                </div>
                <div>
                  <h3 className="text-sm font-bold mb-1" style={{ color: 'var(--color-text-primary)' }}>
                    费曼学习法
                  </h3>
                  <p className="text-[13px] leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
                    试着用最简单的话向 AI 解释这个概念。AI 会以好奇学生的身份追问，帮你发现理解的盲区。
                  </p>
                </div>
              </div>
            </div>

            {/* Messages */}
            {messages.map((msg, idx) => (
              <div
                key={msg.id}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
                style={{ animationDelay: `${Math.min(idx * 30, 200)}ms` }}
              >
                {msg.role === 'assistant' && (
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center shrink-0 mr-3 mt-1"
                    style={{
                      background: 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
                    }}
                  >
                    <Brain size={14} className="text-white" />
                  </div>
                )}
                <div
                  className="max-w-[75%] rounded-2xl px-5 py-3.5 text-[14px] leading-relaxed"
                  style={
                    msg.role === 'user'
                      ? {
                          background: 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
                          color: '#fff',
                          borderBottomRightRadius: 6,
                          boxShadow: '0 4px 16px rgba(99, 102, 241, 0.2)',
                        }
                      : {
                          backgroundColor: 'var(--color-surface-2)',
                          color: 'var(--color-text-primary)',
                          borderBottomLeftRadius: 6,
                          border: '1px solid var(--color-border)',
                        }
                  }
                >
                  {msg.role === 'assistant' && (
                    <div className="flex items-center gap-1.5 mb-1.5">
                      <span className="text-[11px] font-mono font-semibold" style={{ color: 'var(--color-accent-indigo)' }}>
                        AI Student
                      </span>
                    </div>
                  )}
                  <div className="whitespace-pre-wrap">{msg.content}</div>
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

            {/* Assessment result */}
            {assessment && <AssessmentCard result={assessment} conceptName={conceptName || ''} />}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input area */}
        {!assessment ? (
          <div
            className="shrink-0 border-t"
            style={{
              backgroundColor: 'var(--color-surface-1)',
              borderColor: 'var(--color-border)',
            }}
          >
            <div className="max-w-3xl mx-auto px-6 py-4">
              <div
                className="flex items-end gap-3 rounded-2xl px-4 py-3 transition-all"
                style={{
                  backgroundColor: 'var(--color-surface-2)',
                  border: '1px solid var(--color-border)',
                }}
              >
                <textarea
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="用你自己的话解释这个概念..."
                  rows={1}
                  className="flex-1 bg-transparent text-[14px] outline-none resize-none leading-relaxed"
                  style={{
                    color: 'var(--color-text-primary)',
                    maxHeight: '120px',
                  }}
                  disabled={isBusy || !conversationId}
                />
                <button
                  onClick={handleSend}
                  disabled={isBusy || !input.trim() || !conversationId}
                  className="shrink-0 w-9 h-9 rounded-xl flex items-center justify-center transition-all"
                  style={{
                    background: !input.trim() || isBusy
                      ? 'var(--color-surface-3)'
                      : 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
                    color: '#fff',
                    opacity: !input.trim() || isBusy ? 0.5 : 1,
                    boxShadow: input.trim() && !isBusy ? '0 2px 12px rgba(99, 102, 241, 0.3)' : 'none',
                  }}
                >
                  <Send size={16} />
                </button>
              </div>
              <p className="text-[11px] mt-2 text-center font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
                Enter 发送 · Shift+Enter 换行 · 对话 4 轮后可评估理解度
              </p>
            </div>
          </div>
        ) : (
          <div
            className="shrink-0 border-t"
            style={{
              backgroundColor: 'var(--color-surface-1)',
              borderColor: 'var(--color-border)',
            }}
          >
            <div className="max-w-3xl mx-auto px-6 py-4 flex gap-3">
              <button
                onClick={() => navigate('/graph')}
                className="btn-ghost flex-1 flex items-center justify-center gap-2 py-3"
              >
                <ArrowLeft size={16} />
                返回图谱
              </button>
              <button
                onClick={() => { reset(); if (conceptId) startConversation(conceptId); }}
                className="btn-primary flex-1 flex items-center justify-center gap-2 py-3"
              >
                <RotateCcw size={16} />
                再来一轮
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Error toast */}
      {error && (
        <div
          className="fixed top-4 left-1/2 -translate-x-1/2 z-50 glass-heavy rounded-xl px-5 py-3 flex items-center gap-3 animate-fade-in"
          style={{ maxWidth: 480 }}
        >
          <AlertTriangle size={16} style={{ color: 'var(--color-accent-rose)' }} />
          <span className="text-sm" style={{ color: 'var(--color-accent-rose)' }}>{error}</span>
        </div>
      )}
    </div>
  );
}

/** Assessment result card — redesigned */
function AssessmentCard({ result, conceptName }: { result: AssessmentResult; conceptName: string }) {
  const scoreColor = (s: number) => {
    if (s >= 80) return 'var(--color-accent-emerald)';
    if (s >= 60) return 'var(--color-accent-amber)';
    return 'var(--color-accent-rose)';
  };

  const dimensions = [
    { label: '完整性', key: 'completeness' as const, icon: Target },
    { label: '准确性', key: 'accuracy' as const, icon: CheckCircle2 },
    { label: '深度', key: 'depth' as const, icon: BookOpen },
    { label: '举例', key: 'examples' as const, icon: Sparkles },
  ];

  return (
    <div className="animate-fade-in-scale">
      <div
        className="gradient-border"
        style={{
          background: result.mastered
            ? 'linear-gradient(135deg, rgba(52, 211, 153, 0.05), rgba(16, 185, 129, 0.08))'
            : 'var(--color-surface-2)',
        }}
      >
        <div className="rounded-2xl p-6" style={{ backgroundColor: 'var(--color-surface-2)' }}>
          {/* Header */}
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <div
                className="w-11 h-11 rounded-xl flex items-center justify-center"
                style={{
                  background: result.mastered
                    ? 'linear-gradient(135deg, var(--color-accent-emerald), #10b981)'
                    : 'linear-gradient(135deg, var(--color-accent-amber), #f97316)',
                  boxShadow: result.mastered
                    ? '0 4px 16px rgba(52, 211, 153, 0.25)'
                    : '0 4px 16px rgba(251, 191, 36, 0.25)',
                }}
              >
                {result.mastered ? <Trophy size={20} className="text-white" /> : <BarChart3 size={20} className="text-white" />}
              </div>
              <div>
                <h3 className="text-[15px] font-bold" style={{ color: 'var(--color-text-primary)' }}>
                  {result.mastered ? '理解达标！' : '评估结果'}
                </h3>
                <p className="text-[12px]" style={{ color: 'var(--color-text-tertiary)' }}>
                  {conceptName}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div
                className="text-3xl font-bold font-mono"
                style={{ color: scoreColor(result.overall_score) }}
              >
                {result.overall_score}
              </div>
              <div className="text-[10px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>/ 100</div>
            </div>
          </div>

          {/* Dimension bars */}
          <div className="space-y-3 mb-5">
            {dimensions.map((dim) => {
              const score = result[dim.key];
              const Icon = dim.icon;
              return (
                <div key={dim.key}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="flex items-center gap-1.5 text-[12px] font-medium" style={{ color: 'var(--color-text-secondary)' }}>
                      <Icon size={12} />
                      {dim.label}
                    </span>
                    <span className="text-[12px] font-mono font-semibold" style={{ color: scoreColor(score) }}>
                      {score}
                    </span>
                  </div>
                  <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-4)' }}>
                    <div
                      className="h-full rounded-full transition-all duration-700 ease-out"
                      style={{
                        width: `${score}%`,
                        background: `linear-gradient(90deg, ${scoreColor(score)}, ${scoreColor(score)}dd)`,
                        boxShadow: `0 0 8px ${scoreColor(score)}40`,
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Feedback */}
          <div
            className="rounded-xl px-4 py-3 mb-4"
            style={{ backgroundColor: 'var(--color-surface-3)', border: '1px solid var(--color-border-subtle)' }}
          >
            <p className="text-[13px] leading-relaxed" style={{ color: 'var(--color-text-primary)' }}>
              {result.feedback}
            </p>
          </div>

          {/* Knowledge gaps */}
          {result.gaps.length > 0 && (
            <div>
              <p className="text-[11px] font-mono font-semibold uppercase tracking-wider mb-2" style={{ color: 'var(--color-accent-amber)' }}>
                Knowledge Gaps
              </p>
              <ul className="space-y-1.5">
                {result.gaps.map((gap, i) => (
                  <li key={i} className="flex items-start gap-2 text-[12px]" style={{ color: 'var(--color-text-secondary)' }}>
                    <span className="mt-1.5 w-1 h-1 rounded-full shrink-0" style={{ backgroundColor: 'var(--color-accent-amber)' }} />
                    {gap}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
