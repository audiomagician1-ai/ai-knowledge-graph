import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trophy, Crown, Medal, Flame, TrendingUp, ChevronDown, User } from 'lucide-react';

interface LeaderboardEntry {
  name: string;
  is_self: boolean;
  mastered: number;
  learning: number;
  domains_started: number;
  avg_efficiency: number;
  current_streak: number;
  composite_score: number;
  rank: number;
}

interface LeaderboardResponse {
  leaderboard: LeaderboardEntry[];
  user_rank: number;
  total_participants: number;
  sort_by: string;
}

type SortKey = 'mastered' | 'efficiency' | 'streak' | 'score';

const SORT_LABELS: Record<SortKey, string> = {
  mastered: '掌握数',
  efficiency: '学习效率',
  streak: '连续天数',
  score: '综合评分',
};

export function GlobalLeaderboard() {
  const navigate = useNavigate();
  const [data, setData] = useState<LeaderboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState<SortKey>('score');
  const [showSort, setShowSort] = useState(false);

  useEffect(() => {
    const base = (import.meta as Record<string, any>).env?.VITE_API_URL || '';
    setLoading(true);
    fetch(`${base}/api/analytics/leaderboard?sort_by=${sortBy}&limit=10`)
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [sortBy]);

  if (loading) return (
    <section className="rounded-xl p-5 animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      <div className="h-5 w-32 rounded bg-white/10 mb-4" />
      <div className="space-y-2">{[1,2,3,4,5].map(i => <div key={i} className="h-10 rounded-lg bg-white/5" />)}</div>
    </section>
  );

  if (!data || data.leaderboard.length === 0) return null;

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Crown size={16} style={{ color: '#f59e0b' }} />;
    if (rank === 2) return <Medal size={16} style={{ color: '#94a3b8' }} />;
    if (rank === 3) return <Medal size={16} style={{ color: '#b87333' }} />;
    return <span className="text-xs font-bold opacity-40">{rank}</span>;
  };

  const getSortValue = (entry: LeaderboardEntry) => {
    if (sortBy === 'mastered') return `${entry.mastered} 概念`;
    if (sortBy === 'efficiency') return `${entry.avg_efficiency}`;
    if (sortBy === 'streak') return `${entry.current_streak} 天`;
    return `${entry.composite_score}`;
  };

  return (
    <section className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--color-surface-1)' }}>
      {/* Header */}
      <div className="flex items-center gap-2 px-5 py-3 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <Trophy size={16} style={{ color: '#f59e0b' }} />
        <span className="font-medium text-sm">社交排行榜</span>
        <span className="ml-1 text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: '#f59e0b20', color: '#f59e0b' }}>
          #{data.user_rank}
        </span>

        {/* Sort dropdown */}
        <div className="ml-auto relative">
          <button
            onClick={() => setShowSort(!showSort)}
            className="flex items-center gap-1 text-xs px-2 py-1 rounded-md hover:bg-white/10 transition-colors"
            style={{ color: 'var(--color-text-secondary)' }}
          >
            {SORT_LABELS[sortBy]} <ChevronDown size={12} />
          </button>
          {showSort && (
            <div
              className="absolute right-0 top-full mt-1 rounded-lg py-1 z-10 min-w-[100px]"
              style={{ backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)' }}
            >
              {(Object.keys(SORT_LABELS) as SortKey[]).map(key => (
                <button
                  key={key}
                  onClick={() => { setSortBy(key); setShowSort(false); }}
                  className="block w-full text-left px-3 py-1.5 text-xs hover:bg-white/10 transition-colors"
                  style={{ color: key === sortBy ? 'var(--color-accent)' : 'var(--color-text-primary)' }}
                >
                  {SORT_LABELS[key]}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Entries */}
      <div className="divide-y" style={{ borderColor: 'var(--color-border)' }}>
        {data.leaderboard.map(entry => (
          <div
            key={`${entry.name}-${entry.rank}`}
            className="flex items-center gap-3 px-5 py-2.5 transition-colors"
            style={{
              backgroundColor: entry.is_self ? 'rgba(59, 130, 246, 0.08)' : 'transparent',
              cursor: entry.is_self ? 'pointer' : 'default',
            }}
            onClick={entry.is_self ? () => navigate('/leaderboard') : undefined}
          >
            <div className="w-6 text-center shrink-0">{getRankIcon(entry.rank)}</div>

            <div className="flex items-center gap-1.5 flex-1 min-w-0">
              {entry.is_self ? (
                <User size={14} style={{ color: 'var(--color-accent)' }} />
              ) : null}
              <span className={`text-sm truncate ${entry.is_self ? 'font-bold' : ''}`}
                style={entry.is_self ? { color: 'var(--color-accent)' } : undefined}
              >
                {entry.name}
              </span>
            </div>

            {entry.current_streak > 0 && (
              <span className="flex items-center gap-0.5 text-xs shrink-0" style={{ color: '#ef4444' }}>
                <Flame size={11} /> {entry.current_streak}
              </span>
            )}

            <div className="text-right shrink-0 min-w-[60px]">
              <span className="text-sm font-semibold">{getSortValue(entry)}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Footer */}
      <button
        onClick={() => navigate('/leaderboard')}
        className="w-full px-5 py-2.5 text-xs text-center border-t hover:bg-white/5 transition-colors flex items-center justify-center gap-1"
        style={{ borderColor: 'var(--color-border)', color: 'var(--color-text-secondary)' }}
      >
        <TrendingUp size={12} /> 查看完整排行榜
      </button>
    </section>
  );
}