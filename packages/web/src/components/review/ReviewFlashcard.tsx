import { Brain, Clock, Zap, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { DueReviewItem, ReviewResult } from '@/lib/api/learning-api';

const RATINGS = [
  { value: 1, label: '忘了', key: '1', color: 'var(--color-accent-rose)', bg: 'rgba(244,63,94,0.1)' },
  { value: 2, label: '困难', key: '2', color: 'var(--color-accent-amber)', bg: 'rgba(245,158,11,0.1)' },
  { value: 3, label: '记得', key: '3', color: 'var(--color-accent-primary)', bg: 'rgba(16,185,129,0.1)' },
  { value: 4, label: '简单', key: '4', color: 'var(--color-accent-blue)', bg: 'rgba(59,130,246,0.1)' },
] as const;

export { RATINGS };

interface ReviewFlashcardProps {
  item: DueReviewItem;
  conceptName: string;
  domain: string;
  showAnswer: boolean;
  submitting: boolean;
  lastResult: ReviewResult | null;
  totalDue: number;
  completedCount: number;
  remaining: number;
  onReveal: () => void;
  onRate: (rating: number) => void;
}

export function ReviewFlashcard({
  item, conceptName, domain, showAnswer, submitting, lastResult,
  totalDue, completedCount, remaining, onReveal, onRate,
}: ReviewFlashcardProps) {
  const navigate = useNavigate();

  return (
    <div className="w-full max-w-lg">
      {/* Progress bar */}
      <div className="mb-6">
        <div className="h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-3)' }}>
          <div className="h-full rounded-full transition-all duration-500"
            style={{ width: `${(completedCount / totalDue) * 100}%`, backgroundColor: 'var(--color-accent-primary)' }} />
        </div>
        <p className="text-[11px] mt-2 text-right font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
          剩余 {remaining} 张
        </p>
      </div>

      {/* Card */}
      <div className="gradient-border animate-fade-in" style={{ padding: 0 }}>
        <div className="rounded-lg px-8 py-10" style={{ backgroundColor: 'var(--color-surface-2)' }}>
          <div className="text-center mb-6">
            <h2 className="text-xl font-bold mb-2" style={{ color: 'var(--color-text-primary)' }}>{conceptName}</h2>
            <div className="flex items-center justify-center gap-3 text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>
              <span className="flex items-center gap-1"><Brain size={11} /> 复习 {item.fsrs_reps} 次</span>
              <span className="flex items-center gap-1"><Clock size={11} /> 逾期 {item.overdue_days.toFixed(1)} 天</span>
              {item.mastery_score > 0 && (
                <span className="flex items-center gap-1"><Zap size={11} /> 掌握度 {item.mastery_score}</span>
              )}
            </div>
          </div>

          {!showAnswer ? (
            <div className="text-center">
              <p className="text-sm mb-6" style={{ color: 'var(--color-text-secondary)' }}>回忆这个概念的核心内容...</p>
              <button onClick={onReveal} className="btn-primary px-8 py-3 text-sm font-semibold">显示答案</button>
              <p className="text-[10px] mt-3 font-mono" style={{ color: 'var(--color-text-tertiary)' }}>按 空格 或 Enter 翻转</p>
            </div>
          ) : (
            <div className="text-center">
              <p className="text-sm mb-6" style={{ color: 'var(--color-text-secondary)' }}>你对这个概念的回忆程度如何？</p>
              <div className="grid grid-cols-4 gap-3">
                {RATINGS.map((r) => (
                  <button key={r.value} onClick={() => onRate(r.value)} disabled={submitting}
                    className="flex flex-col items-center gap-1.5 rounded-xl py-3 px-2 transition-all"
                    style={{ backgroundColor: r.bg, border: `1px solid ${r.color}25`, opacity: submitting ? 0.5 : 1 }}
                    onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.05)'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}>
                    <span className="text-sm font-bold" style={{ color: r.color }}>{r.label}</span>
                    <span className="text-[10px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>{r.key}</span>
                  </button>
                ))}
              </div>
              <p className="text-[10px] mt-3 font-mono" style={{ color: 'var(--color-text-tertiary)' }}>按 1-4 快速评分</p>
            </div>
          )}

          {lastResult && (
            <div className="mt-4 text-center animate-fade-in">
              <p className="text-[11px]" style={{ color: 'var(--color-accent-primary)' }}>
                {lastResult.card.scheduled_days > 0 ? `下次复习: ${lastResult.card.scheduled_days} 天后` : '稍后再复习'}
              </p>
            </div>
          )}
        </div>
      </div>

      {domain && (
        <div className="mt-4 text-center">
          <button onClick={() => navigate(`/learn/${domain}/${item.concept_id}`)}
            className="text-[12px] inline-flex items-center gap-1 transition-colors"
            style={{ color: 'var(--color-text-tertiary)' }}
            onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--color-accent-primary)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-text-tertiary)'; }}>
            需要深入学习？进入对话模式 <ChevronRight size={12} />
          </button>
        </div>
      )}
    </div>
  );
}
