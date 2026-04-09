/**
 * DiscussionListItem — Single discussion thread with expandable replies.
 * Extracted from ConceptDiscussionPanel (V2.12 Code Health).
 */

import { ThumbsUp, CheckCircle, Send } from 'lucide-react';
import { TYPE_CONFIG } from './DiscussionForm';

interface Reply {
  id: string;
  content: string;
  votes: number;
  created_at: number;
  is_accepted: boolean;
}

export interface Discussion {
  id: string;
  concept_id: string;
  type: string;
  title: string;
  content: string;
  votes: number;
  reply_count: number;
  resolved: boolean;
  created_at: number;
}

export interface DiscussionDetail extends Discussion {
  replies: Reply[];
}

interface DiscussionListItemProps {
  discussion: Discussion;
  isExpanded: boolean;
  detail: DiscussionDetail | null;
  replyText: string;
  onToggleExpand: (id: string) => void;
  onVote: (id: string) => void;
  onReplyChange: (v: string) => void;
  onReply: (id: string) => void;
  formatTime: (ts: number) => string;
}

export function DiscussionListItem({
  discussion: d, isExpanded, detail, replyText,
  onToggleExpand, onVote, onReplyChange, onReply, formatTime,
}: DiscussionListItemProps) {
  const cfg = TYPE_CONFIG[d.type] || TYPE_CONFIG.question;
  const Icon = cfg.icon;

  return (
    <div className="rounded-lg overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <button
        onClick={() => onToggleExpand(d.id)}
        className="w-full flex items-start gap-2 px-3 py-2.5 text-left hover:bg-white/5 transition-colors"
      >
        <Icon size={14} style={{ color: cfg.color }} className="mt-0.5 shrink-0" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium truncate">{d.title}</span>
            {d.resolved && <CheckCircle size={12} style={{ color: '#22c55e' }} />}
          </div>
          <div className="flex items-center gap-3 mt-0.5 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
            <span>{cfg.label}</span>
            <span>{d.reply_count} 回复</span>
            <span>{formatTime(d.created_at)}</span>
          </div>
        </div>
        <button
          onClick={e => { e.stopPropagation(); onVote(d.id); }}
          className="flex items-center gap-0.5 text-xs px-1.5 py-0.5 rounded hover:bg-white/10 shrink-0"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          <ThumbsUp size={11} /> {d.votes}
        </button>
      </button>

      {/* Expanded detail */}
      {isExpanded && detail && detail.id === d.id && (
        <div className="px-3 pb-3 border-t" style={{ borderColor: 'var(--color-border)' }}>
          <p className="text-xs mt-2 mb-3" style={{ color: 'var(--color-text-secondary)' }}>{detail.content}</p>

          {detail.replies.length > 0 && (
            <div className="space-y-2 mb-3">
              {detail.replies.map(reply => (
                <div key={reply.id} className="ml-4 pl-3 text-xs py-1.5" style={{ borderLeft: '2px solid var(--color-border)' }}>
                  <p>{reply.content}</p>
                  <span className="text-xs mt-0.5 block" style={{ color: 'var(--color-text-secondary)' }}>
                    {formatTime(reply.created_at)}
                  </span>
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2">
            <input
              value={replyText}
              onChange={e => onReplyChange(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && onReply(d.id)}
              placeholder="输入回复..."
              className="flex-1 text-xs px-2 py-1.5 rounded-md bg-transparent border outline-none"
              style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }}
            />
            <button
              onClick={() => onReply(d.id)}
              disabled={!replyText.trim()}
              className="text-xs px-2 py-1.5 rounded-md text-white disabled:opacity-40"
              style={{ backgroundColor: '#8b5cf6' }}
            >
              <Send size={12} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
