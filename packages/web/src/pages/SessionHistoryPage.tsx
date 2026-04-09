import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';
import {
  ArrowLeft, History, Filter, ChevronLeft, ChevronRight,
  Award, BookOpen, Play, Search,
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

interface HistoryItem {
  id: number;
  concept_id: string;
  concept_name: string;
  score: number;
  mastered: boolean;
  action: string;
  timestamp: number;
  date: string;
  time: string;
}

interface Pagination {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

const ACTION_ICONS: Record<string, typeof Award> = {
  mastered: Award,
  assessment: BookOpen,
  start: Play,
};

const ACTION_LABELS: Record<string, string> = {
  mastered: '掌握',
  assessment: '评估',
  start: '开始学习',
  all: '全部',
};

const ACTION_COLORS: Record<string, string> = {
  mastered: 'text-yellow-400',
  assessment: 'text-blue-400',
  start: 'text-green-400',
};

/**
 * Session History Page — paginated learning timeline.
 * Path: /history
 */
export function SessionHistoryPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [pagination, setPagination] = useState<Pagination | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionFilter, setActionFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  useKeyboardShortcuts([
    { key: 'Escape', handler: () => navigate(-1), description: 'Go back' },
  ]);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        per_page: '15',
        action_filter: actionFilter,
        days: '90',
      });
      if (search.trim()) params.set('concept_filter', search.trim());

      const res = await fetchWithRetry(`${API_BASE}/analytics/session-history?${params}`);
      const data = await res.json();
      setItems(data.items || []);
      setPagination(data.pagination || null);
    } catch {
      setItems([]);
    } finally {
      setLoading(false);
    }
  }, [page, actionFilter, search]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  // Reset page when filters change
  useEffect(() => { setPage(1); }, [actionFilter, search]);

  return (
    <div className="min-h-dvh bg-gradient-to-b from-gray-950 via-gray-900 to-gray-950 text-white">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-gray-950/80 backdrop-blur-md border-b border-white/5 px-4 py-3">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <button onClick={() => navigate(-1)} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
            <ArrowLeft size={20} />
          </button>
          <History size={20} className="text-blue-400" />
          <h1 className="text-lg font-semibold">学习历史</h1>
          {pagination && (
            <span className="ml-auto text-sm text-gray-400">{pagination.total} 条记录</span>
          )}
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
            <input
              type="text"
              placeholder="搜索概念..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm focus:outline-none focus:border-blue-500/50 transition-colors"
            />
          </div>
          <div className="flex items-center gap-1 bg-white/5 rounded-lg p-1">
            <Filter size={14} className="text-gray-400 ml-2 mr-1" />
            {(['all', 'mastered', 'assessment', 'start'] as const).map((a) => (
              <button
                key={a}
                onClick={() => setActionFilter(a)}
                className={`px-3 py-1.5 rounded-md text-xs font-medium transition-colors ${
                  actionFilter === a ? 'bg-blue-500/20 text-blue-300' : 'text-gray-400 hover:text-white'
                }`}
              >
                {ACTION_LABELS[a]}
              </button>
            ))}
          </div>
        </div>

        {/* Timeline */}
        {loading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-white/5 rounded-lg animate-pulse" />
            ))}
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-16 text-gray-500">
            <History size={48} className="mx-auto mb-4 opacity-30" />
            <p>暂无学习记录</p>
          </div>
        ) : (
          <div className="space-y-2">
            {items.map((item) => {
              const Icon = ACTION_ICONS[item.action] || BookOpen;
              const color = ACTION_COLORS[item.action] || 'text-gray-400';
              return (
                <div
                  key={`${item.id}-${item.timestamp}`}
                  className="flex items-center gap-4 px-4 py-3 bg-white/[0.03] hover:bg-white/[0.06] rounded-lg border border-white/5 transition-colors cursor-pointer"
                  onClick={() => {
                    const parts = item.concept_id.split('/');
                    if (parts.length >= 2) navigate(`/domain/${parts[0]}/${item.concept_id}`);
                  }}
                >
                  <div className={`p-2 rounded-lg bg-white/5 ${color}`}>
                    <Icon size={18} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{item.concept_name || item.concept_id}</p>
                    <p className="text-xs text-gray-500">{ACTION_LABELS[item.action]}</p>
                  </div>
                  {item.score > 0 && (
                    <div className="text-right">
                      <p className={`text-sm font-bold ${item.mastered ? 'text-yellow-400' : 'text-blue-400'}`}>
                        {item.score}分
                      </p>
                    </div>
                  )}
                  <div className="text-right text-xs text-gray-500 whitespace-nowrap">
                    <p>{item.date}</p>
                    <p>{item.time}</p>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Pagination */}
        {pagination && pagination.total_pages > 1 && (
          <div className="flex items-center justify-center gap-4 pt-4">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={!pagination.has_prev}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft size={18} />
            </button>
            <span className="text-sm text-gray-400">
              {pagination.page} / {pagination.total_pages}
            </span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={!pagination.has_next}
              className="p-2 rounded-lg bg-white/5 hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronRight size={18} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
