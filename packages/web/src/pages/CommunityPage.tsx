import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import {
  ArrowLeft, Users, Plus, ThumbsUp, MessageSquare,
  Lightbulb, Link2, AlertTriangle, Star,
} from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface Suggestion {
  id: string;
  type: 'concept' | 'link' | 'correction' | 'feedback';
  status: string;
  domain_id?: string;
  title: string;
  description: string;
  source_concept?: string;
  target_concept?: string;
  created_at: number;
  votes: number;
}

const TYPE_META = {
  concept: { icon: Lightbulb, label: '新概念', color: '#22c55e' },
  link: { icon: Link2, label: '新链接', color: '#3b82f6' },
  correction: { icon: AlertTriangle, label: '纠错', color: '#f59e0b' },
  feedback: { icon: MessageSquare, label: '反馈', color: '#8b5cf6' },
} as const;

/**
 * Community Page — browse and submit knowledge graph suggestions.
 * Path: /community
 */
export function CommunityPage() {
  const navigate = useNavigate();
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formType, setFormType] = useState<Suggestion['type']>('concept');
  const [formTitle, setFormTitle] = useState('');
  const [formDesc, setFormDesc] = useState('');
  const [formDomain, setFormDomain] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useKeyboardShortcuts([
    { key: 'Escape', handler: () => showForm ? setShowForm(false) : navigate('/'), description: 'Back' },
  ]);

  const fetchSuggestions = useCallback(async () => {
    try {
      const res = await fetchWithRetry(`${API_BASE}/community/suggestions?limit=50`, { retries: 1 });
      if (res.ok) setSuggestions(await res.json());
    } catch { /* offline */ }
    setLoading(false);
  }, []);

  useEffect(() => { fetchSuggestions(); }, [fetchSuggestions]);

  const handleSubmit = async () => {
    if (!formTitle.trim() || !formDesc.trim() || formDesc.trim().length < 10) return;
    setSubmitting(true);
    try {
      const res = await fetchWithRetry(`${API_BASE}/community/suggestions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          type: formType,
          title: formTitle.trim(),
          description: formDesc.trim(),
          domain_id: formDomain || undefined,
        }),
      });
      if (res.ok) {
        setFormTitle('');
        setFormDesc('');
        setShowForm(false);
        fetchSuggestions();
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleVote = async (id: string) => {
    try {
      const res = await fetchWithRetry(`${API_BASE}/community/suggestions/${id}/vote`, { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setSuggestions((prev) => prev.map((s) => (s.id === id ? { ...s, votes: data.votes } : s)));
      }
    } catch { /* offline */ }
  };

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      {/* Header */}
      <header className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <ArrowLeft size={20} />
        </button>
        <Users size={24} style={{ color: '#8b5cf6' }} />
        <h1 className="text-xl font-bold">社区共建</h1>
        <span className="ml-auto text-sm opacity-50">{suggestions.length} 条建议</span>
        <button
          onClick={() => setShowForm(!showForm)}
          className="ml-3 px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1.5"
          style={{ backgroundColor: 'var(--color-accent-primary)', color: '#fff' }}
        >
          <Plus size={14} /> 提议
        </button>
      </header>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        {/* Submit form */}
        {showForm && (
          <div className="rounded-xl p-5 space-y-4" style={{ backgroundColor: 'var(--color-surface-1)', border: '1px solid var(--color-border)' }}>
            <h3 className="text-sm font-semibold">提交新建议</h3>
            {/* Type selector */}
            <div className="flex gap-2 flex-wrap">
              {(Object.entries(TYPE_META) as [Suggestion['type'], typeof TYPE_META[keyof typeof TYPE_META]][]).map(([key, meta]) => (
                <button
                  key={key}
                  onClick={() => setFormType(key)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
                  style={{
                    backgroundColor: formType === key ? meta.color + '33' : 'var(--color-surface-2)',
                    border: `1px solid ${formType === key ? meta.color : 'var(--color-border)'}`,
                    color: formType === key ? meta.color : 'var(--color-text-secondary)',
                  }}
                >
                  {meta.label}
                </button>
              ))}
            </div>
            <input
              type="text"
              value={formTitle}
              onChange={(e) => setFormTitle(e.target.value)}
              placeholder="标题 (至少3个字符)"
              className="w-full px-4 py-2.5 rounded-xl text-sm bg-transparent outline-none"
              style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }}
            />
            <input
              type="text"
              value={formDomain}
              onChange={(e) => setFormDomain(e.target.value)}
              placeholder="相关知识域 (可选, 如 programming)"
              className="w-full px-4 py-2.5 rounded-xl text-sm bg-transparent outline-none"
              style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }}
            />
            <textarea
              value={formDesc}
              onChange={(e) => setFormDesc(e.target.value)}
              placeholder="详细描述 (至少10个字符)…"
              rows={4}
              className="w-full bg-transparent text-sm outline-none resize-none rounded-xl p-4"
              style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }}
            />
            <div className="flex gap-3">
              <button
                onClick={handleSubmit}
                disabled={submitting || formTitle.trim().length < 3 || formDesc.trim().length < 10}
                className="px-4 py-2 rounded-lg text-sm font-medium"
                style={{
                  backgroundColor: 'var(--color-accent-primary)', color: '#fff',
                  opacity: (submitting || formTitle.trim().length < 3 || formDesc.trim().length < 10) ? 0.4 : 1,
                }}
              >
                {submitting ? '提交中…' : '提交建议'}
              </button>
              <button
                onClick={() => setShowForm(false)}
                className="px-4 py-2 rounded-lg text-sm hover:bg-white/10"
              >
                取消
              </button>
            </div>
          </div>
        )}

        {/* Suggestions list */}
        {loading ? (
          <div className="text-center py-16 opacity-40">
            <div className="animate-spin w-8 h-8 border-2 border-white/30 border-t-white rounded-full mx-auto mb-3" />
            <p className="text-sm">加载中…</p>
          </div>
        ) : suggestions.length === 0 ? (
          <div className="text-center py-16 opacity-40">
            <Star size={48} className="mx-auto mb-3" />
            <p className="text-sm">还没有社区建议，成为第一个贡献者吧！</p>
          </div>
        ) : (
          <div className="space-y-3">
            {suggestions.map((s) => {
              const meta = TYPE_META[s.type];
              const Icon = meta.icon;
              return (
                <div
                  key={s.id}
                  className="rounded-xl p-4 hover:ring-1 transition-all"
                  style={{ backgroundColor: 'var(--color-surface-1)' }}
                >
                  <div className="flex items-start gap-3">
                    {/* Vote column */}
                    <button
                      onClick={() => handleVote(s.id)}
                      className="flex flex-col items-center gap-1 pt-1 shrink-0"
                      title="投票支持"
                    >
                      <ThumbsUp size={16} style={{ color: 'var(--color-text-tertiary)' }} />
                      <span className="text-xs font-mono font-bold">{s.votes}</span>
                    </button>
                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1.5 flex-wrap">
                        <span
                          className="px-2 py-0.5 rounded text-[10px] font-medium"
                          style={{ backgroundColor: meta.color + '22', color: meta.color }}
                        >
                          <Icon size={10} className="inline mr-1" />
                          {meta.label}
                        </span>
                        {s.domain_id && (
                          <span className="text-[10px] opacity-40">{s.domain_id}</span>
                        )}
                        <span className="text-[10px] opacity-30 ml-auto">
                          {new Date(s.created_at * 1000).toLocaleDateString('zh-CN')}
                        </span>
                      </div>
                      <h3 className="text-sm font-semibold mb-1">{s.title}</h3>
                      <p className="text-sm opacity-60 line-clamp-2">{s.description}</p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
