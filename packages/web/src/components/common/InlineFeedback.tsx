import { useState, useCallback } from 'react';
import { MessageSquare, Send, X, ThumbsUp, ThumbsDown } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface InlineFeedbackProps {
  /** The concept being discussed */
  conceptId?: string;
  /** The domain context */
  domainId?: string;
  /** Which AI message triggered the feedback (for context) */
  messageContent?: string;
  /** Compact mode (just thumbs up/down) vs expanded (full form) */
  compact?: boolean;
}

/**
 * InlineFeedback — Allows users to submit feedback on AI responses
 * directly from the learn page. Bridges to the community system.
 */
export function InlineFeedback({
  conceptId,
  domainId,
  messageContent,
  compact = true,
}: InlineFeedbackProps) {
  const [expanded, setExpanded] = useState(false);
  const [sentiment, setSentiment] = useState<'positive' | 'negative' | null>(null);
  const [feedbackText, setFeedbackText] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const handleQuickFeedback = useCallback(
    async (type: 'positive' | 'negative') => {
      setSentiment(type);
      if (type === 'positive') {
        // Quick positive — no form needed
        try {
          await fetchWithRetry(`${API_BASE}/community/suggestions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              type: 'feedback',
              concept_id: conceptId,
              domain_id: domainId,
              title: `👍 Helpful explanation for ${conceptId || 'concept'}`,
              description: `User found the AI explanation helpful.${messageContent ? ` Context: "${messageContent.slice(0, 200)}..."` : ''}`,
            }),
          });
        } catch { /* offline ok */ }
        setSubmitted(true);
        setTimeout(() => setSubmitted(false), 3000);
      } else {
        // Negative — expand form for details
        setExpanded(true);
      }
    },
    [conceptId, domainId, messageContent]
  );

  const handleSubmitDetailed = useCallback(async () => {
    if (!feedbackText.trim() || feedbackText.trim().length < 10) return;
    setSubmitting(true);
    try {
      await fetchWithRetry(`${API_BASE}/community/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: sentiment === 'negative' ? 'correction' : 'feedback',
          concept_id: conceptId,
          domain_id: domainId,
          title: `${sentiment === 'negative' ? '⚠️' : '💡'} Feedback on ${conceptId || 'concept'}`,
          description: feedbackText.trim() + (messageContent ? `\n\n---\nContext: "${messageContent.slice(0, 300)}"` : ''),
        }),
      });
      setSubmitted(true);
      setExpanded(false);
      setFeedbackText('');
      setTimeout(() => setSubmitted(false), 5000);
    } catch {
      /* offline */
    } finally {
      setSubmitting(false);
    }
  }, [feedbackText, sentiment, conceptId, domainId, messageContent]);

  if (submitted) {
    return (
      <div className="flex items-center gap-1.5 text-xs opacity-60 py-1">
        <span style={{ color: '#22c55e' }}>✓</span>
        <span>感谢反馈！</span>
      </div>
    );
  }

  if (compact && !expanded) {
    return (
      <div className="flex items-center gap-1 py-0.5">
        <button
          onClick={() => handleQuickFeedback('positive')}
          className="p-1.5 rounded-md hover:bg-white/10 transition-colors"
          title="有帮助"
          aria-label="有帮助"
        >
          <ThumbsUp size={12} style={{ color: 'var(--color-text-tertiary)' }} />
        </button>
        <button
          onClick={() => handleQuickFeedback('negative')}
          className="p-1.5 rounded-md hover:bg-white/10 transition-colors"
          title="需要改进"
          aria-label="需要改进"
        >
          <ThumbsDown size={12} style={{ color: 'var(--color-text-tertiary)' }} />
        </button>
      </div>
    );
  }

  return (
    <div
      className="rounded-xl p-3 mt-2 space-y-2"
      style={{ backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)' }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <MessageSquare size={12} style={{ color: '#f59e0b' }} />
          <span className="text-xs font-medium">这个解释有什么问题？</span>
        </div>
        <button
          onClick={() => { setExpanded(false); setSentiment(null); }}
          className="p-1 rounded hover:bg-white/10"
        >
          <X size={12} />
        </button>
      </div>
      <textarea
        value={feedbackText}
        onChange={(e) => setFeedbackText(e.target.value)}
        placeholder="请描述问题或建议 (至少10个字符)…"
        rows={3}
        className="w-full bg-transparent text-xs outline-none resize-none rounded-lg p-2"
        style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }}
      />
      <button
        onClick={handleSubmitDetailed}
        disabled={submitting || feedbackText.trim().length < 10}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium"
        style={{
          backgroundColor: 'var(--color-accent-primary)',
          color: 'var(--color-text-on-accent)',
          opacity: (submitting || feedbackText.trim().length < 10) ? 0.4 : 1,
        }}
      >
        <Send size={10} />
        {submitting ? '提交中…' : '提交反馈'}
      </button>
    </div>
  );
}
