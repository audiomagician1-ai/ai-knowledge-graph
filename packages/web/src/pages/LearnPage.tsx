import { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDialogueStore } from '@/lib/store/dialogue';
import { useLearningStore } from '@/lib/store/learning';
import type { AssessmentResult } from '@/lib/store/dialogue';

/**
 * 费曼学习对话页面
 * 用户是"老师"，AI是"学生"
 * 苏格拉底式追问 + 理解度评估
 */
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

  // When assessment completes, persist to learning store
  useEffect(() => {
    if (assessment && conceptId) {
      recordAssessment(
        conceptId,
        conceptName || conceptId,
        assessment.overall_score,
        assessment.mastered,
      );
    }
  }, [assessment]);

  // Auto-scroll to bottom
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
    <div className="flex h-dvh flex-col" style={{ backgroundColor: '#0f172a' }}>
      {/* Header */}
      <header
        className="flex items-center gap-3 px-4 shrink-0"
        style={{
          height: '52px',
          paddingTop: 'var(--safe-area-top)',
          backgroundColor: '#1e293b',
          borderBottom: '1px solid #334155',
        }}
      >
        <button
          onClick={() => navigate('/graph')}
          className="flex items-center justify-center rounded-lg"
          style={{ width: 36, height: 36, color: '#f1f5f9' }}
        >
          ←
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            {isMilestone && <span>⭐</span>}
            <h1 className="text-sm font-semibold truncate" style={{ color: '#f1f5f9' }}>
              {conceptName || conceptId}
            </h1>
          </div>
          <p className="text-[10px]" style={{ color: '#94a3b8' }}>
            费曼学习 · 轮次 {userTurns}
          </p>
        </div>
        {suggestAssess && !assessment && (
          <button
            onClick={requestAssessment}
            disabled={isBusy}
            className="rounded-lg px-3 py-1.5 text-xs font-medium"
            style={{ backgroundColor: '#8b5cf6', color: '#fff', opacity: isBusy ? 0.5 : 1 }}
          >
            {isAssessing ? '评估中...' : '📊 评估'}
          </button>
        )}
      </header>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {/* 引导卡片 */}
        <div
          className="rounded-xl p-3 text-xs"
          style={{ backgroundColor: '#1e293b', border: '1px solid #334155', color: '#94a3b8' }}
        >
          💡 <strong style={{ color: '#e2e8f0' }}>费曼学习法</strong>：试着用最简单的话向AI解释这个概念。
          AI会通过追问帮你发现理解的盲区。
        </div>

        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className="max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed"
              style={
                msg.role === 'user'
                  ? { backgroundColor: '#6366f1', color: '#fff', borderBottomRightRadius: 4 }
                  : { backgroundColor: '#1e293b', color: '#e2e8f0', borderBottomLeftRadius: 4, border: '1px solid #334155' }
              }
            >
              {msg.role === 'assistant' && (
                <div className="text-[10px] mb-1" style={{ color: '#94a3b8' }}>
                  🧠 小图 (AI学生)
                </div>
              )}
              <div className="whitespace-pre-wrap">{msg.content}</div>
              {msg.role === 'assistant' && msg.content === '' && isStreaming && (
                <span className="inline-block w-2 h-4 animate-pulse" style={{ backgroundColor: '#8b5cf6' }} />
              )}
            </div>
          </div>
        ))}

        {/* Assessment result */}
        {assessment && <AssessmentCard result={assessment} conceptName={conceptName || ''} />}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      {!assessment ? (
        <div
          className="flex items-end gap-2 px-4 py-3 shrink-0"
          style={{
            backgroundColor: '#1e293b',
            borderTop: '1px solid #334155',
            paddingBottom: 'calc(var(--safe-area-bottom, 0px) + 12px)',
          }}
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="用你自己的话解释..."
            rows={1}
            className="flex-1 rounded-xl px-4 py-3 text-sm outline-none resize-none"
            style={{
              backgroundColor: '#0f172a',
              color: '#f1f5f9',
              border: '1px solid #334155',
              maxHeight: '120px',
            }}
            disabled={isBusy || !conversationId}
          />
          <button
            onClick={handleSend}
            disabled={isBusy || !input.trim() || !conversationId}
            className="rounded-xl px-4 py-3 text-sm font-medium transition-opacity"
            style={{
              backgroundColor: isBusy ? '#475569' : '#8b5cf6',
              color: '#fff',
              opacity: !input.trim() || isBusy ? 0.5 : 1,
            }}
          >
            {isStreaming ? '...' : '发送'}
          </button>
        </div>
      ) : (
        <div
          className="flex gap-3 px-4 py-3 shrink-0"
          style={{
            backgroundColor: '#1e293b',
            borderTop: '1px solid #334155',
            paddingBottom: 'calc(var(--safe-area-bottom, 0px) + 12px)',
          }}
        >
          <button
            onClick={() => navigate('/graph')}
            className="flex-1 rounded-xl py-3 text-sm font-medium"
            style={{ backgroundColor: '#334155', color: '#e2e8f0' }}
          >
            返回图谱
          </button>
          <button
            onClick={() => {
              reset();
              if (conceptId) startConversation(conceptId);
            }}
            className="flex-1 rounded-xl py-3 text-sm font-medium"
            style={{ backgroundColor: '#8b5cf6', color: '#fff' }}
          >
            再来一轮
          </button>
        </div>
      )}

      {/* Error */}
      {error && (
        <div
          className="absolute top-16 left-4 right-4 rounded-lg p-3 text-xs"
          style={{ backgroundColor: '#7f1d1d', color: '#fca5a5', border: '1px solid #991b1b' }}
        >
          ⚠ {error}
        </div>
      )}
    </div>
  );
}

/** 评估结果卡片 */
function AssessmentCard({ result, conceptName }: { result: AssessmentResult; conceptName: string }) {
  const scoreColor = (s: number) => {
    if (s >= 80) return '#10b981';
    if (s >= 60) return '#f59e0b';
    return '#ef4444';
  };

  const dimensions = [
    { label: '完整性', key: 'completeness' as const },
    { label: '准确性', key: 'accuracy' as const },
    { label: '深度', key: 'depth' as const },
    { label: '举例', key: 'examples' as const },
  ];

  return (
    <div
      className="rounded-2xl p-4"
      style={{
        backgroundColor: '#1e293b',
        border: `2px solid ${result.mastered ? '#10b981' : '#f59e0b'}`,
      }}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <h3 className="text-sm font-bold" style={{ color: '#f1f5f9' }}>
            {result.mastered ? '🎉 理解达标！' : '📊 评估结果'}
          </h3>
          <p className="text-[10px]" style={{ color: '#94a3b8' }}>
            {conceptName}
          </p>
        </div>
        <div
          className="text-2xl font-bold"
          style={{ color: scoreColor(result.overall_score) }}
        >
          {result.overall_score}
        </div>
      </div>

      {/* Dimension bars */}
      <div className="space-y-2 mb-3">
        {dimensions.map((dim) => {
          const score = result[dim.key];
          return (
            <div key={dim.key} className="flex items-center gap-2">
              <span className="text-[10px] w-10 shrink-0" style={{ color: '#94a3b8' }}>
                {dim.label}
              </span>
              <div className="flex-1 h-2 rounded-full" style={{ backgroundColor: '#334155' }}>
                <div
                  className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${score}%`,
                    backgroundColor: scoreColor(score),
                  }}
                />
              </div>
              <span className="text-[10px] w-6 text-right" style={{ color: scoreColor(score) }}>
                {score}
              </span>
            </div>
          );
        })}
      </div>

      {/* Feedback */}
      <p className="text-xs leading-relaxed mb-2" style={{ color: '#cbd5e1' }}>
        {result.feedback}
      </p>

      {/* Knowledge gaps */}
      {result.gaps.length > 0 && (
        <div>
          <p className="text-[10px] font-medium mb-1" style={{ color: '#f59e0b' }}>
            需要加强的方面:
          </p>
          <ul className="text-[10px] space-y-0.5" style={{ color: '#94a3b8' }}>
            {result.gaps.map((gap, i) => (
              <li key={i}>• {gap}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
