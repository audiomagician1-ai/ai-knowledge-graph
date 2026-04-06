import { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDomainStore } from '@/lib/store/domain';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import {
  ArrowLeft, Trophy, Medal, Crown, Star, TrendingUp,
  Users, Flame,
} from 'lucide-react';

/**
 * Leaderboard Page — shows domain-level rankings.
 * Currently uses deterministic mock data based on domain metadata.
 * Ready for Supabase integration when social features go live.
 * Path: /leaderboard
 */
export function LeaderboardPage() {
  const navigate = useNavigate();
  const domains = useDomainStore((s) => s.domains);

  useKeyboardShortcuts([
    { key: 'Escape', handler: () => navigate('/'), description: 'Back to home' },
    { key: 'h', handler: () => navigate('/'), description: 'Go to home' },
  ]);

  // Load user's actual progress across all domains
  const userStats = useMemo(() => {
    let totalMastered = 0;
    let totalLearning = 0;
    let domainsStarted = 0;
    for (const d of domains) {
      try {
        const raw = localStorage.getItem(`akg-learning:${d.id}`);
        if (raw) {
          const parsed = JSON.parse(raw)?.progress || {};
          const entries = Object.values(parsed) as Array<{ status: string }>;
          const mastered = entries.filter((e) => e.status === 'mastered').length;
          const learning = entries.filter((e) => e.status === 'learning').length;
          totalMastered += mastered;
          totalLearning += learning;
          if (mastered + learning > 0) domainsStarted++;
        }
      } catch { /* skip */ }
    }
    return { totalMastered, totalLearning, domainsStarted };
  }, [domains]);

  // Generate mock leaderboard entries (deterministic, seeded by date)
  const leaderboard = useMemo(() => {
    const names = [
      '知识探索者', '图谱之星', '求知若渴', '苏格拉底门徒',
      '费曼学习法大师', '概念连接者', '知识宇宙旅人', '深度学习者',
      '好奇心驱动', '通识达人', '交叉学科爱好者', '永不止步',
    ];
    const day = new Date().getDate();
    const entries = names.map((name, i) => {
      const seed = (name.charCodeAt(0) * 31 + day * 7 + i * 13) % 1000;
      const mastered = Math.max(5, Math.round(seed / 4 + (12 - i) * 15));
      const streak = Math.max(0, Math.round(seed / 80 + (12 - i) * 2));
      return { name, mastered, streak, rank: 0 };
    });

    // Insert user
    entries.push({
      name: '🌟 我',
      mastered: userStats.totalMastered,
      streak: 0, // Could read from learning store
      rank: 0,
    });

    // Sort by mastered desc
    entries.sort((a, b) => b.mastered - a.mastered);
    entries.forEach((e, i) => { e.rank = i + 1; });

    return entries;
  }, [userStats]);

  const userRank = leaderboard.find((e) => e.name === '🌟 我')?.rank || 0;

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      {/* Header */}
      <header className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <ArrowLeft size={20} />
        </button>
        <Trophy size={24} style={{ color: '#f59e0b' }} />
        <h1 className="text-xl font-bold">学习排行榜</h1>
        <span className="ml-auto text-sm px-3 py-1 rounded-full" style={{ backgroundColor: '#f59e0b20', color: '#f59e0b' }}>
          排名 #{userRank}
        </span>
      </header>

      <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
        {/* My Stats Card */}
        <div className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)', border: '1px solid var(--color-accent)' }}>
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-full flex items-center justify-center text-2xl" style={{ backgroundColor: '#f59e0b20' }}>
              🧑‍🎓
            </div>
            <div className="flex-1">
              <div className="text-lg font-bold">我的成绩</div>
              <div className="flex gap-4 mt-1 text-sm" style={{ color: 'var(--color-text-secondary)' }}>
                <span className="flex items-center gap-1">
                  <Star size={14} style={{ color: '#22c55e' }} />
                  {userStats.totalMastered} 已掌握
                </span>
                <span className="flex items-center gap-1">
                  <TrendingUp size={14} style={{ color: '#3b82f6' }} />
                  {userStats.totalLearning} 学习中
                </span>
                <span className="flex items-center gap-1">
                  <Users size={14} style={{ color: '#8b5cf6' }} />
                  {userStats.domainsStarted} 领域
                </span>
              </div>
            </div>
            <div className="text-3xl font-bold" style={{ color: '#f59e0b' }}>#{userRank}</div>
          </div>
        </div>

        {/* Leaderboard */}
        <section className="rounded-xl overflow-hidden" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <div className="px-5 py-3 border-b flex items-center gap-2" style={{ borderColor: 'var(--color-border)' }}>
            <Medal size={16} style={{ color: '#f59e0b' }} />
            <span className="font-medium text-sm">全站排行</span>
            <span className="ml-auto text-xs opacity-50">基于掌握概念数</span>
          </div>

          <div className="divide-y" style={{ borderColor: 'var(--color-border)' }}>
            {leaderboard.map((entry) => {
              const isMe = entry.name === '🌟 我';
              return (
                <div
                  key={entry.name}
                  className="flex items-center gap-3 px-5 py-3 transition-colors"
                  style={{
                    backgroundColor: isMe ? 'rgba(59, 130, 246, 0.08)' : 'transparent',
                  }}
                >
                  {/* Rank */}
                  <div className="w-8 text-center shrink-0">
                    {entry.rank === 1 ? (
                      <Crown size={20} style={{ color: '#f59e0b' }} />
                    ) : entry.rank === 2 ? (
                      <Medal size={20} style={{ color: '#94a3b8' }} />
                    ) : entry.rank === 3 ? (
                      <Medal size={20} style={{ color: '#b87333' }} />
                    ) : (
                      <span className="text-sm font-bold opacity-40">{entry.rank}</span>
                    )}
                  </div>

                  {/* Name */}
                  <div className="flex-1 min-w-0">
                    <span className={`text-sm ${isMe ? 'font-bold' : ''}`}>
                      {entry.name}
                    </span>
                  </div>

                  {/* Streak */}
                  {entry.streak > 0 && (
                    <span className="flex items-center gap-1 text-xs" style={{ color: '#ef4444' }}>
                      <Flame size={12} /> {entry.streak}天
                    </span>
                  )}

                  {/* Score */}
                  <div className="text-right shrink-0">
                    <span className="text-sm font-semibold">{entry.mastered}</span>
                    <span className="text-xs opacity-40 ml-1">概念</span>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Note */}
        <p className="text-center text-xs opacity-40 py-2">
          📊 排行榜数据将在社区功能上线后与全球用户共享
        </p>
      </div>
    </div>
  );
}
