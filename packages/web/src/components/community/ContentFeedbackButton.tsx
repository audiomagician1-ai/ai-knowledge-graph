/**
 * ContentFeedbackButton — Inline button for reporting content quality issues.
 * Expands into a mini-form with category selection and optional comment.
 * V2.11
 */

import { useState } from 'react';
import { MessageSquareWarning, Check, X, ThumbsUp, AlertTriangle, Clock, HelpCircle, FileQuestion } from 'lucide-react';

interface ContentFeedbackButtonProps {
  conceptId: string;
  domainId?: string;
  compact?: boolean;
}

const CATEGORIES = [
  { value: 'inaccurate', label: '不准确', icon: <AlertTriangle size={14} />, color: '#ef4444' },
  { value: 'outdated', label: '已过时', icon: <Clock size={14} />, color: '#f59e0b' },
  { value: 'unclear', label: '不清楚', icon: <HelpCircle size={14} />, color: '#3b82f6' },
  { value: 'incomplete', label: '不完整', icon: <FileQuestion size={14} />, color: '#8b5cf6' },
  { value: 'excellent', label: '很棒!', icon: <ThumbsUp size={14} />, color: '#22c55e' },
] as const;

const API_BASE = import.meta.env.VITE_API_URL || '';

export function ContentFeedbackButton({ conceptId, domainId, compact = false }: ContentFeedbackButtonProps) {
  const [expanded, setExpanded] = useState(false);
  const [category, setCategory] = useState<string>('');
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!category) return;
    setSubmitting(true);
    try {
      await fetch(`${API_BASE}/api/community/content-feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          concept_id: conceptId,
          domain_id: domainId,
          category,
          comment: comment.trim() || null,
        }),
      });
      setSubmitted(true);
      setTimeout(() => {
        setExpanded(false);
        setSubmitted(false);
        setCategory('');
        setComment('');
      }, 2000);
    } catch { /* graceful degradation */ }
    setSubmitting(false);
  };

  if (submitted) {
    return (
      <div className="flex items-center gap-2 text-sm py-2 px-3 rounded-lg" style={{ backgroundColor: '#22c55e20', color: '#22c55e' }}>
        <Check size={16} /> 感谢你的反馈!
      </div>
    );
  }

  if (!expanded) {
    return (
      <button
        onClick={() => setExpanded(true)}
        className="flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg hover:bg-white/10 transition-colors"
        style={{ color: 'var(--color-text-secondary)' }}
        title="报告内容问题"
      >
        <MessageSquareWarning size={14} />
        {!compact && <span>内容反馈</span>}
      </button>
    );
  }

  return (
    <div className="rounded-xl p-3 space-y-3 border" style={{ backgroundColor: 'var(--color-surface-1)', borderColor: 'var(--color-border)' }}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium" style={{ color: 'var(--color-text-secondary)' }}>这段内容如何?</span>
        <button onClick={() => { setExpanded(false); setCategory(''); setComment(''); }} className="p-1 rounded hover:bg-white/10"><X size={14} /></button>
      </div>

      {/* Category Selection */}
      <div className="flex flex-wrap gap-1.5">
        {CATEGORIES.map(c => (
          <button
            key={c.value}
            onClick={() => setCategory(c.value)}
            className="flex items-center gap-1 text-xs px-2 py-1 rounded-full border transition-colors"
            style={{
              borderColor: category === c.value ? c.color : 'var(--color-border)',
              backgroundColor: category === c.value ? `${c.color}20` : 'transparent',
              color: category === c.value ? c.color : 'var(--color-text-secondary)',
            }}
          >
            {c.icon} {c.label}
          </button>
        ))}
      </div>

      {/* Comment (optional) */}
      {category && (
        <>
          <textarea
            value={comment}
            onChange={e => setComment(e.target.value)}
            placeholder="补充说明 (可选)..."
            rows={2}
            className="w-full text-xs rounded-lg px-3 py-2 resize-none border"
            style={{ backgroundColor: 'var(--color-surface-0)', borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }}
            maxLength={2000}
          />
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="w-full text-xs font-medium py-2 rounded-lg transition-colors"
            style={{ backgroundColor: 'var(--color-accent)', color: '#fff', opacity: submitting ? 0.6 : 1 }}
          >
            {submitting ? '提交中...' : '提交反馈'}
          </button>
        </>
      )}
    </div>
  );
}
