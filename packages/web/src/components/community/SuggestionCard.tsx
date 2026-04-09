import {
  ThumbsUp, Shield, CheckCircle, XCircle, Trash2, Filter,
  Lightbulb, Link2, AlertTriangle, MessageSquare,
} from 'lucide-react';
import { useState } from 'react';

interface Suggestion {
  id: string;
  type: 'concept' | 'link' | 'correction' | 'feedback';
  status: 'pending' | 'approved' | 'rejected';
  domain_id?: string;
  title: string;
  description: string;
  created_at: number;
  votes: number;
  moderation_reason?: string;
}

const STATUS_META = {
  pending: { icon: Filter, label: '待审核', color: '#f59e0b' },
  approved: { icon: CheckCircle, label: '已通过', color: '#22c55e' },
  rejected: { icon: XCircle, label: '已拒绝', color: '#ef4444' },
} as const;

const TYPE_META = {
  concept: { icon: Lightbulb, label: '新概念', color: '#22c55e' },
  link: { icon: Link2, label: '新链接', color: '#3b82f6' },
  correction: { icon: AlertTriangle, label: '纠错', color: '#f59e0b' },
  feedback: { icon: MessageSquare, label: '反馈', color: '#8b5cf6' },
} as const;

export type { Suggestion };
export { STATUS_META, TYPE_META };

interface SuggestionCardProps {
  s: Suggestion;
  adminMode: boolean;
  adminToken: string;
  onVote: (id: string) => void;
  onModerate: (id: string, action: 'approved' | 'rejected', reason: string) => void;
  onDelete: (id: string) => void;
}

export function SuggestionCard({ s, adminMode, adminToken, onVote, onModerate, onDelete }: SuggestionCardProps) {
  const [moderating, setModerating] = useState(false);
  const [reason, setReason] = useState('');
  const meta = TYPE_META[s.type];
  const Icon = meta.icon;
  const statusMeta = STATUS_META[s.status];
  const StatusIcon = statusMeta.icon;

  return (
    <div
      className="rounded-xl p-4 hover:ring-1 transition-all"
      style={{
        backgroundColor: 'var(--color-surface-1)',
        opacity: s.status === 'rejected' ? 0.6 : 1,
      }}
    >
      <div className="flex items-start gap-3">
        <button onClick={() => onVote(s.id)} className="flex flex-col items-center gap-1 pt-1 shrink-0" title="投票支持" disabled={s.status !== 'pending'}>
          <ThumbsUp size={16} style={{ color: s.status === 'pending' ? 'var(--color-text-tertiary)' : '#555' }} />
          <span className="text-xs font-mono font-bold">{s.votes}</span>
        </button>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1.5 flex-wrap">
            <span className="px-2 py-0.5 rounded text-[10px] font-medium" style={{ backgroundColor: meta.color + '22', color: meta.color }}>
              <Icon size={10} className="inline mr-1" />{meta.label}
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-medium" style={{ backgroundColor: statusMeta.color + '22', color: statusMeta.color }}>
              <StatusIcon size={10} className="inline mr-1" />{statusMeta.label}
            </span>
            {s.domain_id && <span className="text-[10px] opacity-40">{s.domain_id}</span>}
            <span className="text-[10px] opacity-30 ml-auto">{new Date(s.created_at * 1000).toLocaleDateString('zh-CN')}</span>
          </div>
          <h3 className="text-sm font-semibold mb-1">{s.title}</h3>
          <p className="text-sm opacity-60 line-clamp-2">{s.description}</p>
          {s.moderation_reason && (
            <p className="text-xs mt-2 px-2 py-1 rounded" style={{ backgroundColor: 'var(--color-surface-2)', color: 'var(--color-text-secondary)' }}>
              审核备注: {s.moderation_reason}
            </p>
          )}
          {adminMode && adminToken && s.status === 'pending' && (
            <div className="mt-3 space-y-2">
              {moderating ? (
                <div className="space-y-2">
                  <input type="text" value={reason} onChange={(e) => setReason(e.target.value)} placeholder="审核备注 (可选)…"
                    className="w-full px-3 py-1.5 rounded-lg text-xs bg-transparent outline-none"
                    style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }} />
                  <div className="flex gap-2">
                    <button onClick={() => { onModerate(s.id, 'approved', reason); setModerating(false); setReason(''); }}
                      className="px-3 py-1 rounded-lg text-xs font-medium flex items-center gap-1"
                      style={{ backgroundColor: '#22c55e22', color: '#22c55e', border: '1px solid #22c55e44' }}>
                      <CheckCircle size={12} /> 通过
                    </button>
                    <button onClick={() => { onModerate(s.id, 'rejected', reason); setModerating(false); setReason(''); }}
                      className="px-3 py-1 rounded-lg text-xs font-medium flex items-center gap-1"
                      style={{ backgroundColor: '#ef444422', color: '#ef4444', border: '1px solid #ef444444' }}>
                      <XCircle size={12} /> 拒绝
                    </button>
                    <button onClick={() => { setModerating(false); setReason(''); }} className="px-3 py-1 rounded-lg text-xs hover:bg-white/10">取消</button>
                  </div>
                </div>
              ) : (
                <div className="flex gap-2">
                  <button onClick={() => setModerating(true)} className="px-3 py-1 rounded-lg text-xs font-medium flex items-center gap-1"
                    style={{ backgroundColor: '#f59e0b22', color: '#f59e0b', border: '1px solid #f59e0b44' }}>
                    <Shield size={12} /> 审核
                  </button>
                  <button onClick={() => onDelete(s.id)} className="px-3 py-1 rounded-lg text-xs font-medium flex items-center gap-1"
                    style={{ backgroundColor: '#ef444411', color: '#ef4444', border: '1px solid #ef444433' }}>
                    <Trash2 size={12} /> 删除
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
