import { useState, useEffect, useCallback } from 'react';
import {
  MessageCircle, HelpCircle, Lightbulb, Link2, BookOpen,
  ThumbsUp, CheckCircle, Send, ChevronDown, ChevronUp,
} from 'lucide-react';

interface Discussion {
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

interface DiscussionDetail extends Discussion {
  replies: Array<{
    id: string;
    content: string;
    votes: number;
    created_at: number;
    is_accepted: boolean;
  }>;
}

const TYPE_CONFIG: Record<string, { icon: typeof HelpCircle; label: string; color: string }> = {
  question: { icon: HelpCircle, label: '提问', color: '#3b82f6' },
  insight: { icon: Lightbulb, label: '洞见', color: '#f59e0b' },
  resource: { icon: Link2, label: '资源', color: '#22c55e' },
  explanation: { icon: BookOpen, label: '解释', color: '#8b5cf6' },
};

interface Props {
  conceptId: string;
  domainId?: string;
  compact?: boolean;
}

export function ConceptDiscussionPanel({ conceptId, domainId, compact = false }: Props) {
  const [discussions, setDiscussions] = useState<Discussion[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [detail, setDetail] = useState<DiscussionDetail | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [formTitle, setFormTitle] = useState('');
  const [formContent, setFormContent] = useState('');
  const [formType, setFormType] = useState('question');
  const [replyText, setReplyText] = useState('');
  const [isOpen, setIsOpen] = useState(!compact);

  const base = (import.meta as Record<string, any>).env?.VITE_API_URL || '';

  const loadDiscussions = useCallback(() => {
    setLoading(true);
    fetch(`${base}/api/community/discussions?concept_id=${encodeURIComponent(conceptId)}&limit=10`)
      .then(r => r.json())
      .then(data => {
        setDiscussions(data.discussions || []);
        setTotal(data.total || 0);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [base, conceptId]);

  useEffect(() => { loadDiscussions(); }, [loadDiscussions]);

  const handleSubmit = async () => {
    if (!formTitle.trim() || !formContent.trim()) return;
    await fetch(`${base}/api/community/discussions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        concept_id: conceptId,
        domain_id: domainId,
        type: formType,
        title: formTitle.trim(),
        content: formContent.trim(),
      }),
    });
    setFormTitle('');
    setFormContent('');
    setShowForm(false);
    loadDiscussions();
  };

  const handleVote = async (id: string) => {
    await fetch(`${base}/api/community/discussions/${id}/vote`, { method: 'POST' });
    loadDiscussions();
  };

  const handleReply = async (id: string) => {
    if (!replyText.trim()) return;
    await fetch(`${base}/api/community/discussions/${id}/reply`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: replyText.trim() }),
    });
    setReplyText('');
    // Reload detail
    const r = await fetch(`${base}/api/community/discussions/${id}`);
    setDetail(await r.json());
    loadDiscussions();
  };

  const toggleExpand = async (id: string) => {
    if (expanded === id) {
      setExpanded(null);
      setDetail(null);
      return;
    }
    setExpanded(id);
    const r = await fetch(`${base}/api/community/discussions/${id}`);
    setDetail(await r.json());
  };

  const formatTime = (ts: number) => {
    const diff = (Date.now() / 1000 - ts) / 3600;
    if (diff < 1) return '刚刚';
    if (diff < 24) return `${Math.floor(diff)}小时前`;
    return `${Math.floor(diff / 24)}天前`;
  };

  return (
    <section className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      {/* Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-2 px-4 py-3 border-b hover:bg-white/5 transition-colors"
        style={{ borderColor: 'var(--color-border)' }}
      >
        <MessageCircle size={15} style={{ color: '#8b5cf6' }} />
        <span className="text-sm font-medium">概念讨论</span>
        {total > 0 && (
          <span className="text-xs px-1.5 py-0.5 rounded-full" style={{ backgroundColor: '#8b5cf620', color: '#8b5cf6' }}>
            {total}
          </span>
        )}
        <span className="ml-auto">{isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</span>
      </button>

      {isOpen && (
        <div className="px-4 py-3 space-y-3">
          {/* New post button */}
          {!showForm && (
            <button
              onClick={() => setShowForm(true)}
              className="w-full text-xs py-2 rounded-lg border border-dashed hover:bg-white/5 transition-colors"
              style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}
            >
              + 发起讨论 (提问 / 分享洞见 / 推荐资源)
            </button>
          )}

          {/* New form */}
          {showForm && (
            <div className="rounded-lg p-3 space-y-2" style={{ backgroundColor: 'var(--color-surface-0)' }}>
              <div className="flex gap-1">
                {Object.entries(TYPE_CONFIG).map(([key, cfg]) => {
                  const Icon = cfg.icon;
                  return (
                    <button
                      key={key}
                      onClick={() => setFormType(key)}
                      className="flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors"
                      style={{
                        backgroundColor: formType === key ? `${cfg.color}20` : 'transparent',
                        color: formType === key ? cfg.color : 'var(--color-text-secondary)',
                      }}
                    >
                      <Icon size={12} /> {cfg.label}
                    </button>
                  );
                })}
              </div>
              <input
                value={formTitle}
                onChange={e => setFormTitle(e.target.value)}
                placeholder="标题..."
                className="w-full text-sm px-3 py-1.5 rounded-md bg-transparent border outline-none"
                style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }}
              />
              <textarea
                value={formContent}
                onChange={e => setFormContent(e.target.value)}
                placeholder="详细内容..."
                rows={3}
                className="w-full text-sm px-3 py-1.5 rounded-md bg-transparent border outline-none resize-none"
                style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }}
              />
              <div className="flex justify-end gap-2">
                <button onClick={() => setShowForm(false)} className="text-xs px-3 py-1.5 rounded-md hover:bg-white/10 transition-colors"
                  style={{ color: 'var(--color-text-secondary)' }}>取消</button>
                <button
                  onClick={handleSubmit}
                  disabled={!formTitle.trim() || !formContent.trim()}
                  className="flex items-center gap-1 text-xs px-3 py-1.5 rounded-md text-white transition-colors disabled:opacity-40"
                  style={{ backgroundColor: '#8b5cf6' }}
                >
                  <Send size={12} /> 发布
                </button>
              </div>
            </div>
          )}

          {/* Discussion list */}
          {loading ? (
            <div className="space-y-2">{[1,2].map(i => <div key={i} className="h-12 rounded-lg bg-white/5 animate-pulse" />)}</div>
          ) : discussions.length === 0 ? (
            <p className="text-xs text-center py-3" style={{ color: 'var(--color-text-secondary)' }}>
              暂无讨论，成为第一个提问者吧！
            </p>
          ) : (
            discussions.map(d => {
              const cfg = TYPE_CONFIG[d.type] || TYPE_CONFIG.question;
              const Icon = cfg.icon;
              const isExpanded = expanded === d.id;

              return (
                <div key={d.id} className="rounded-lg overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>
                  <button
                    onClick={() => toggleExpand(d.id)}
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
                      onClick={e => { e.stopPropagation(); handleVote(d.id); }}
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
                          onChange={e => setReplyText(e.target.value)}
                          onKeyDown={e => e.key === 'Enter' && handleReply(d.id)}
                          placeholder="输入回复..."
                          className="flex-1 text-xs px-2 py-1.5 rounded-md bg-transparent border outline-none"
                          style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-primary)' }}
                        />
                        <button
                          onClick={() => handleReply(d.id)}
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
            })
          )}
        </div>
      )}
    </section>
  );
}