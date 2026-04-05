import { useEffect, useState, useCallback } from 'react';
import { createLogger } from '@/lib/utils/logger';
import { useNavigate, useParams } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { useDomainStore } from '@/lib/store/domain';
import { useAchievementStore } from '@/lib/store/achievements';
import {
  apiFetchDueReviews, apiSubmitReview,
  type DueReviewItem, type ReviewResult,
} from '@/lib/api/learning-api';
import {
  ArrowLeft, Clock, Brain, RotateCcw,
  CheckCircle2, Zap, ChevronRight, Loader,
  AlertTriangle, RefreshCw,
} from 'lucide-react';

const log = createLogger('ReviewPage');

/** FSRS rating labels and keyboard shortcuts */
const RATINGS = [
  { value: 1, label: '忘了', key: '1', color: 'var(--color-accent-rose)', bg: 'rgba(244,63,94,0.1)' },
  { value: 2, label: '困难', key: '2', color: 'var(--color-accent-amber)', bg: 'rgba(245,158,11,0.1)' },
  { value: 3, label: '记得', key: '3', color: 'var(--color-accent-primary)', bg: 'rgba(16,185,129,0.1)' },
  { value: 4, label: '简单', key: '4', color: 'var(--color-accent-blue)', bg: 'rgba(59,130,246,0.1)' },
] as const;

export function ReviewPage() {
  const { domainId } = useParams<{ domainId?: string }>();
  const navigate = useNavigate();
  const { graphData } = useGraphStore();
  const { activeDomain } = useDomainStore();
  const { checkNewAchievements } = useAchievementStore();

  const [queue, setQueue] = useState<DueReviewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [lastResult, setLastResult] = useState<ReviewResult | null>(null);
  const [completedCount, setCompletedCount] = useState(0);

  const domain = domainId || activeDomain || '';

  // Build concept name lookup from graph data
  const nameMap = new Map<string, string>();
  if (graphData?.nodes) {
    for (const n of graphData.nodes) {
      nameMap.set(n.id, n.label);
    }
  }

  const currentItem = queue[currentIdx] ?? null;
  const conceptName = currentItem ? (nameMap.get(currentItem.concept_id) || currentItem.concept_id) : '';
  const totalDue = queue.length;
  const remaining = totalDue - currentIdx;

  // Load due reviews
  const loadDue = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetchDueReviews(50, domain);
      if (data) {
        setQueue(data.items);
        setCurrentIdx(0);
        setShowAnswer(false);
        setCompletedCount(0);
      } else {
        setError('无法加载复习队列');
      }
    } catch {
      setError('加载失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  }, [domain]);

  useEffect(() => { loadDue(); }, [loadDue]);

  // Keyboard shortcuts: 1-4 for rating, Space to reveal
  useEffect(() => {
    function handleKey(e: KeyboardEvent) {
      if (submitting || !currentItem) return;
      if (!showAnswer && (e.key === ' ' || e.key === 'Enter')) {
        e.preventDefault();
        setShowAnswer(true);
        return;
      }
      if (showAnswer && e.key >= '1' && e.key <= '4') {
        e.preventDefault();
        handleRate(Number(e.key));
      }
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [showAnswer, submitting, currentItem]);

  const handleRate = async (rating: number) => {
    if (!currentItem || submitting) return;
    setSubmitting(true);
    log.info('Submitting review', { conceptId: currentItem.concept_id, rating });

    const result = await apiSubmitReview(currentItem.concept_id, rating);
    setSubmitting(false);

    if (result?.success) {
      setLastResult(result);
      setCompletedCount((c) => c + 1);
      if (result.achievements_unlocked?.length > 0) {
        checkNewAchievements();
      }
      // Move to next card
      setTimeout(() => {
        setShowAnswer(false);
        setLastResult(null);
        setCurrentIdx((i) => i + 1);
      }, 600);
    } else {
      setError('提交失败，请重试');
    }
  };

  // ── Render ──

  if (loading) {
    return (
      <div className="flex h-dvh items-center justify-center" style={{ backgroundColor: 'var(--color-surface-0)' }}>
        <div className="flex flex-col items-center gap-4">
          <Loader size={32} className="animate-spin" style={{ color: 'var(--color-accent-primary)' }} />
          <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>加载复习队列...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-dvh" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      {/* Header */}
      <header
        className="flex items-center gap-4 px-6 shrink-0 border-b"
        style={{ height: 64, backgroundColor: 'var(--color-surface-1)', borderColor: 'var(--color-border)' }}
      >
        <button
          onClick={() => navigate(domain ? `/domain/${domain}` : '/')}
          className="flex items-center justify-center w-9 h-9 rounded-md transition-colors"
          style={{ color: 'var(--color-text-secondary)' }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          <ArrowLeft size={18} />
        </button>
        <div className="flex-1 min-w-0">
          <h1 className="text-[15px] font-bold" style={{ color: 'var(--color-text-primary)' }}>
            间隔复习
          </h1>
          <p className="text-[12px]" style={{ color: 'var(--color-text-tertiary)' }}>
            {totalDue > 0 ? `${completedCount} / ${totalDue} 完成` : '无待复习'}
          </p>
        </div>
        <button
          onClick={loadDue}
          className="flex items-center justify-center w-9 h-9 rounded-md transition-colors"
          style={{ color: 'var(--color-text-secondary)' }}
          onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'var(--color-surface-3)')}
          onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
        >
          <RefreshCw size={16} />
        </button>
      </header>

      {/* Main content */}
      <div className="flex-1 flex items-center justify-center overflow-y-auto px-6 py-8">
        {error && (
          <div className="flex flex-col items-center gap-4">
            <AlertTriangle size={32} style={{ color: 'var(--color-accent-rose)' }} />
            <p className="text-sm" style={{ color: 'var(--color-accent-rose)' }}>{error}</p>
            <button onClick={loadDue} className="btn-primary px-4 py-2 text-sm">重新加载</button>
          </div>
        )}

        {!error && totalDue === 0 && (
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center"
              style={{ backgroundColor: 'rgba(16,185,129,0.1)' }}>
              <CheckCircle2 size={32} style={{ color: 'var(--color-accent-primary)' }} />
            </div>
            <h2 className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>
              全部复习完成！
            </h2>
            <p className="text-sm max-w-xs" style={{ color: 'var(--color-text-secondary)' }}>
              目前没有待复习的概念。继续学习新知识，系统会自动安排复习。
            </p>
            <button onClick={() => navigate(domain ? `/domain/${domain}` : '/')}
              className="btn-primary px-5 py-2.5 text-sm flex items-center gap-2">
              <ArrowLeft size={14} /> 返回图谱
            </button>
          </div>
        )}

        {!error && currentItem && currentIdx < totalDue && (
          <div className="w-full max-w-lg">
            {/* Progress bar */}
            <div className="mb-6">
              <div className="h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-3)' }}>
                <div className="h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${(completedCount / totalDue) * 100}%`,
                    backgroundColor: 'var(--color-accent-primary)',
                  }} />
              </div>
              <p className="text-[11px] mt-2 text-right font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
                剩余 {remaining} 张
              </p>
            </div>

            {/* Card */}
            <div className="gradient-border animate-fade-in" style={{ padding: 0 }}>
              <div className="rounded-lg px-8 py-10" style={{ backgroundColor: 'var(--color-surface-2)' }}>
                {/* Concept name */}
                <div className="text-center mb-6">
                  <h2 className="text-xl font-bold mb-2" style={{ color: 'var(--color-text-primary)' }}>
                    {conceptName}
                  </h2>
                  <div className="flex items-center justify-center gap-3 text-[11px]" style={{ color: 'var(--color-text-tertiary)' }}>
                    <span className="flex items-center gap-1">
                      <Brain size={11} /> 复习 {currentItem.fsrs_reps} 次
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock size={11} /> 逾期 {currentItem.overdue_days.toFixed(1)} 天
                    </span>
                    {currentItem.mastery_score > 0 && (
                      <span className="flex items-center gap-1">
                        <Zap size={11} /> 掌握度 {currentItem.mastery_score}
                      </span>
                    )}
                  </div>
                </div>

                {/* Show/reveal answer area */}
                {!showAnswer ? (
                  <div className="text-center">
                    <p className="text-sm mb-6" style={{ color: 'var(--color-text-secondary)' }}>
                      回忆这个概念的核心内容...
                    </p>
                    <button
                      onClick={() => setShowAnswer(true)}
                      className="btn-primary px-8 py-3 text-sm font-semibold"
                    >
                      显示答案
                    </button>
                    <p className="text-[10px] mt-3 font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
                      按 空格 或 Enter 翻转
                    </p>
                  </div>
                ) : (
                  <div className="text-center">
                    <p className="text-sm mb-6" style={{ color: 'var(--color-text-secondary)' }}>
                      你对这个概念的回忆程度如何？
                    </p>
                    {/* Rating buttons */}
                    <div className="grid grid-cols-4 gap-3">
                      {RATINGS.map((r) => (
                        <button
                          key={r.value}
                          onClick={() => handleRate(r.value)}
                          disabled={submitting}
                          className="flex flex-col items-center gap-1.5 rounded-xl py-3 px-2 transition-all"
                          style={{
                            backgroundColor: r.bg,
                            border: `1px solid ${r.color}25`,
                            opacity: submitting ? 0.5 : 1,
                          }}
                          onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.05)'; }}
                          onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
                        >
                          <span className="text-sm font-bold" style={{ color: r.color }}>{r.label}</span>
                          <span className="text-[10px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>{r.key}</span>
                        </button>
                      ))}
                    </div>
                    <p className="text-[10px] mt-3 font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
                      按 1-4 快速评分
                    </p>
                  </div>
                )}

                {/* Last result feedback */}
                {lastResult && (
                  <div className="mt-4 text-center animate-fade-in">
                    <p className="text-[11px]" style={{ color: 'var(--color-accent-primary)' }}>
                      {lastResult.card.scheduled_days > 0
                        ? `下次复习: ${lastResult.card.scheduled_days} 天后`
                        : '稍后再复习'}
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Deep learn link */}
            {currentItem && domain && (
              <div className="mt-4 text-center">
                <button
                  onClick={() => navigate(`/learn/${domain}/${currentItem.concept_id}`)}
                  className="text-[12px] inline-flex items-center gap-1 transition-colors"
                  style={{ color: 'var(--color-text-tertiary)' }}
                  onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--color-accent-primary)'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-text-tertiary)'; }}
                >
                  需要深入学习？进入对话模式 <ChevronRight size={12} />
                </button>
              </div>
            )}
          </div>
        )}

        {/* All done after completing queue */}
        {!error && totalDue > 0 && currentIdx >= totalDue && (
          <div className="flex flex-col items-center gap-4 text-center animate-fade-in">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center"
              style={{ backgroundColor: 'rgba(16,185,129,0.1)' }}>
              <CheckCircle2 size={32} style={{ color: 'var(--color-accent-primary)' }} />
            </div>
            <h2 className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>
              本轮复习完成！
            </h2>
            <p className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
              共复习 {completedCount} 个概念
            </p>
            <div className="flex gap-3 mt-2">
              <button onClick={loadDue}
                className="btn-ghost px-4 py-2.5 text-sm flex items-center gap-2">
                <RotateCcw size={14} /> 检查更多
              </button>
              <button onClick={() => navigate(domain ? `/domain/${domain}` : '/')}
                className="btn-primary px-4 py-2.5 text-sm flex items-center gap-2">
                <ArrowLeft size={14} /> 返回图谱
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}