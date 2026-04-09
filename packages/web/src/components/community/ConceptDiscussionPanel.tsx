/**
 * ConceptDiscussionPanel — Concept-level Q&A and discussion threads.
 * V2.8. Refactored V2.12: extracted DiscussionForm + DiscussionListItem.
 */

import { useState, useEffect, useCallback } from 'react';
import { MessageCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { DiscussionForm } from './DiscussionForm';
import { DiscussionListItem, type Discussion, type DiscussionDetail } from './DiscussionListItem';

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
      .then(data => { setDiscussions(data.discussions || []); setTotal(data.total || 0); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [base, conceptId]);

  useEffect(() => { loadDiscussions(); }, [loadDiscussions]);

  const handleSubmit = async () => {
    if (!formTitle.trim() || !formContent.trim()) return;
    await fetch(`${base}/api/community/discussions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ concept_id: conceptId, domain_id: domainId, type: formType, title: formTitle.trim(), content: formContent.trim() }),
    });
    setFormTitle(''); setFormContent(''); setShowForm(false);
    loadDiscussions();
  };

  const handleVote = async (id: string) => {
    await fetch(`${base}/api/community/discussions/${id}/vote`, { method: 'POST' });
    loadDiscussions();
  };

  const handleReply = async (id: string) => {
    if (!replyText.trim()) return;
    await fetch(`${base}/api/community/discussions/${id}/reply`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: replyText.trim() }),
    });
    setReplyText('');
    const r = await fetch(`${base}/api/community/discussions/${id}`);
    setDetail(await r.json());
    loadDiscussions();
  };

  const toggleExpand = async (id: string) => {
    if (expanded === id) { setExpanded(null); setDetail(null); return; }
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
      <button onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-2 px-4 py-3 border-b hover:bg-white/5 transition-colors"
        style={{ borderColor: 'var(--color-border)' }}>
        <MessageCircle size={15} style={{ color: '#8b5cf6' }} />
        <span className="text-sm font-medium">概念讨论</span>
        {total > 0 && <span className="text-xs px-1.5 py-0.5 rounded-full" style={{ backgroundColor: '#8b5cf620', color: '#8b5cf6' }}>{total}</span>}
        <span className="ml-auto">{isOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}</span>
      </button>

      {isOpen && (
        <div className="px-4 py-3 space-y-3">
          {!showForm && (
            <button onClick={() => setShowForm(true)}
              className="w-full text-xs py-2 rounded-lg border border-dashed hover:bg-white/5 transition-colors"
              style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}>
              + 发起讨论 (提问 / 分享洞见 / 推荐资源)
            </button>
          )}

          {showForm && (
            <DiscussionForm
              formType={formType} formTitle={formTitle} formContent={formContent}
              onTypeChange={setFormType} onTitleChange={setFormTitle} onContentChange={setFormContent}
              onSubmit={handleSubmit} onCancel={() => setShowForm(false)}
            />
          )}

          {loading ? (
            <div className="space-y-2">{[1,2].map(i => <div key={i} className="h-12 rounded-lg bg-white/5 animate-pulse" />)}</div>
          ) : discussions.length === 0 ? (
            <p className="text-xs text-center py-3" style={{ color: 'var(--color-text-secondary)' }}>暂无讨论，成为第一个提问者吧！</p>
          ) : (
            discussions.map(d => (
              <DiscussionListItem
                key={d.id} discussion={d}
                isExpanded={expanded === d.id} detail={detail}
                replyText={replyText}
                onToggleExpand={toggleExpand} onVote={handleVote}
                onReplyChange={setReplyText} onReply={handleReply}
                formatTime={formatTime}
              />
            ))
          )}
        </div>
      )}
    </section>
  );
}
