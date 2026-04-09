import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import { ArrowLeft, Users, Plus, Star, Shield, Filter } from 'lucide-react';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import { SuggestionCard, STATUS_META } from '@/components/community/SuggestionCard';
import { SuggestionForm } from '@/components/community/SuggestionForm';
import type { Suggestion } from '@/components/community/SuggestionCard';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

export function CommunityPage() {
  const navigate = useNavigate();
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [adminMode, setAdminMode] = useState(false);
  const [adminToken, setAdminToken] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all');

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

  const handleSubmit = async (type: Suggestion['type'], title: string, description: string, domainId: string) => {
    const res = await fetchWithRetry(`${API_BASE}/community/suggestions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ type, title, description, domain_id: domainId || undefined }),
    });
    if (res.ok) fetchSuggestions();
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

  const handleModerate = async (id: string, action: 'approved' | 'rejected', reason: string) => {
    if (!adminToken) return;
    try {
      const res = await fetchWithRetry(`${API_BASE}/community/suggestions/${id}/moderate`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${adminToken}` },
        body: JSON.stringify({ action, reason: reason || undefined }),
      });
      if (res.ok) {
        const updated = await res.json();
        setSuggestions((prev) => prev.map((s) => (s.id === id ? { ...s, ...updated } : s)));
      }
    } catch { /* offline */ }
  };

  const handleDelete = async (id: string) => {
    if (!adminToken) return;
    try {
      const res = await fetchWithRetry(`${API_BASE}/community/suggestions/${id}`, {
        method: 'DELETE', headers: { Authorization: `Bearer ${adminToken}` },
      });
      if (res.ok) setSuggestions((prev) => prev.filter((s) => s.id !== id));
    } catch { /* offline */ }
  };

  const filtered = statusFilter === 'all' ? suggestions : suggestions.filter((s) => s.status === statusFilter);

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      <header className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors"><ArrowLeft size={20} /></button>
        <Users size={24} style={{ color: '#8b5cf6' }} />
        <h1 className="text-xl font-bold">社区共建</h1>
        <span className="ml-auto text-sm opacity-50">{filtered.length} 条建议</span>
        <button onClick={() => setAdminMode(!adminMode)} className="p-2 rounded-lg hover:bg-white/10 transition-colors" title="管理员模式">
          <Shield size={16} style={{ color: adminMode ? '#f59e0b' : 'var(--color-text-tertiary)' }} />
        </button>
        <button onClick={() => setShowForm(!showForm)} className="ml-3 px-3 py-1.5 rounded-lg text-sm font-medium flex items-center gap-1.5"
          style={{ backgroundColor: 'var(--color-accent-primary)', color: '#fff' }}>
          <Plus size={14} /> 提议
        </button>
      </header>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        {adminMode && (
          <div className="rounded-xl p-4 space-y-3" style={{ backgroundColor: '#f59e0b11', border: '1px solid #f59e0b44' }}>
            <div className="flex items-center gap-2">
              <Shield size={16} style={{ color: '#f59e0b' }} />
              <span className="text-sm font-semibold" style={{ color: '#f59e0b' }}>管理员模式</span>
            </div>
            <input type="password" value={adminToken} onChange={(e) => setAdminToken(e.target.value)} placeholder="输入管理员密钥…"
              className="w-full px-4 py-2 rounded-xl text-sm bg-transparent outline-none"
              style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }} />
            <div className="flex gap-2 flex-wrap">
              {(['all', 'pending', 'approved', 'rejected'] as const).map((st) => (
                <button key={st} onClick={() => setStatusFilter(st)}
                  className="px-3 py-1 rounded-lg text-xs font-medium transition-all"
                  style={{
                    backgroundColor: statusFilter === st ? '#f59e0b33' : 'var(--color-surface-2)',
                    border: `1px solid ${statusFilter === st ? '#f59e0b' : 'var(--color-border)'}`,
                    color: statusFilter === st ? '#f59e0b' : 'var(--color-text-secondary)',
                  }}>
                  {st === 'all' ? '全部' : STATUS_META[st].label}
                </button>
              ))}
            </div>
          </div>
        )}

        {showForm && <SuggestionForm onSubmit={handleSubmit} onClose={() => setShowForm(false)} />}

        {loading ? (
          <div className="text-center py-16 opacity-40">
            <div className="animate-spin w-8 h-8 border-2 border-white/30 border-t-white rounded-full mx-auto mb-3" />
            <p className="text-sm">加载中…</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 opacity-40">
            <Star size={48} className="mx-auto mb-3" />
            <p className="text-sm">{statusFilter !== 'all' ? '没有符合筛选条件的建议' : '还没有社区建议，成为第一个贡献者吧！'}</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((s) => (
              <SuggestionCard key={s.id} s={s} adminMode={adminMode} adminToken={adminToken}
                onVote={handleVote} onModerate={handleModerate} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
