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
  ArrowLeft, RotateCcw,
  CheckCircle2, Loader,
  AlertTriangle, RefreshCw,
} from 'lucide-react';
import { ReviewFlashcard } from '@/components/review/ReviewFlashcard';

const log = createLogger('ReviewPage');

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
          <ReviewFlashcard
            item={currentItem}
            conceptName={conceptName}
            domain={domain}
            showAnswer={showAnswer}
            submitting={submitting}
            lastResult={lastResult}
            totalDue={totalDue}
            completedCount={completedCount}
            remaining={remaining}
            onReveal={() => setShowAnswer(true)}
            onRate={handleRate}
          />
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