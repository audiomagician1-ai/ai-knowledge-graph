/**
 * ReviewBanner — Homepage banner showing due FSRS reviews + learning progress.
 * Behavior design: P0 止血 — 构建回访提示体系 + 让进度可见。
 * Principles: Loss aversion ("X个知识点待复习"), sunk cost (progress bar), MAP-P prompt.
 */
import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, Flame, Trophy, ChevronRight } from 'lucide-react';
import { useLearningStore } from '@/lib/store/learning';

/**
 * Calculate streak from learning history (consecutive days with at least 1 assessment).
 */
function calcStreak(history: Array<{ timestamp: number }>): number {
  if (!history.length) return 0;
  const daySet = new Set<string>();
  for (const h of history) {
    const d = new Date(h.timestamp);
    daySet.add(`${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`);
  }
  const today = new Date();
  let streak = 0;
  for (let i = 0; i < 365; i++) {
    const d = new Date(today.getTime() - i * 86400000);
    const key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
    if (daySet.has(key)) streak++;
    else if (i > 0) break; // gap found (allow today to be missing)
  }
  return streak;
}

export function ReviewBanner() {
  const nav = useNavigate();
  const { progress, history } = useLearningStore();
  const [dismissed, setDismissed] = useState(false);

  // Calculate progress stats
  const stats = useMemo(() => {
    const entries = Object.values(progress);
    const mastered = entries.filter(p => p.status === 'mastered').length;
    const learning = entries.filter(p => p.status === 'learning').length;
    const streak = calcStreak(history);

    // Estimate due reviews: concepts mastered >24h ago (rough heuristic without FSRS API)
    const now = Date.now();
    const dueForReview = entries.filter(p =>
      p.status === 'mastered' && p.mastered_at && (now - p.mastered_at) > 86400000
    ).length;

    return { mastered, learning, streak, dueForReview, total: entries.length };
  }, [progress, history]);

  // Don't show if user has no learning activity
  const hasActivity = stats.total > 0;

  // Session storage: dismiss for this session
  useEffect(() => {
    const d = sessionStorage.getItem('akg-review-banner-dismissed');
    if (d) setDismissed(true);
  }, []);

  if (dismissed || !hasActivity) return null;

  return (
    <div className="absolute left-4 right-4 bottom-6 z-20"
         style={{ animation: 'slideUp 0.4s ease-out' }}>
      <div className="bg-white/95 backdrop-blur-md rounded-xl shadow-md border border-gray-100
                      px-4 py-3 flex items-center gap-3">
        {/* Left: Stats */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-1.5">
            {stats.mastered > 0 && (
              <span className="flex items-center gap-1 text-xs font-medium text-green-600">
                <Trophy size={13} />
                {stats.mastered} 已掌握
              </span>
            )}
            {stats.learning > 0 && (
              <span className="flex items-center gap-1 text-xs font-medium text-blue-600">
                <BookOpen size={13} />
                {stats.learning} 学习中
              </span>
            )}
            {stats.streak > 0 && (
              <span className="flex items-center gap-1 text-xs font-medium text-orange-500">
                <Flame size={13} />
                {stats.streak}天连续
              </span>
            )}
          </div>

          {stats.dueForReview > 0 ? (
            <p className="text-sm font-medium text-gray-800">
              <span className="text-orange-500">{stats.dueForReview}</span> 个知识点待复习
            </p>
          ) : stats.learning > 0 ? (
            <p className="text-sm text-gray-600">继续上次的学习之旅</p>
          ) : (
            <p className="text-sm text-gray-600">学习进度已保存</p>
          )}
        </div>

        {/* Right: CTA */}
        {stats.dueForReview > 0 ? (
          <button onClick={() => nav('/review')}
                  className="flex items-center gap-1 px-3.5 py-2 rounded-xl text-xs font-semibold
                             text-white bg-gradient-to-r from-orange-400 to-orange-500
                             hover:from-orange-500 hover:to-orange-600 shadow-sm transition-all">
            去复习
            <ChevronRight size={14} />
          </button>
        ) : (
          <button onClick={() => nav('/dashboard')}
                  className="flex items-center gap-1 px-3.5 py-2 rounded-xl text-xs font-semibold
                             text-gray-600 bg-gray-100 hover:bg-gray-200 transition-all">
            查看进度
            <ChevronRight size={14} />
          </button>
        )}

        {/* Dismiss */}
        <button onClick={() => {
                  sessionStorage.setItem('akg-review-banner-dismissed', '1');
                  setDismissed(true);
                }}
                className="absolute -top-2 -right-2 w-5 h-5 rounded-full bg-gray-200 text-gray-500
                           flex items-center justify-center text-xs hover:bg-gray-300 transition-colors">
          ×
        </button>
      </div>

      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
}
