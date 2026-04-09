import type { AssessmentResult } from '@/lib/store/dialogue';
import { useCountUp } from '@/lib/hooks/useCountUp';
import { Trophy, BarChart3 } from 'lucide-react';

/** Single dimension bar with staggered fill animation */
function AnimatedDimBar({ label, score, delay, scoreColor }: {
  label: string; score: number; delay: number;
  scoreColor: (s: number) => string;
}) {
  const animVal = useCountUp(score, 800, delay);
  return (
    <div className="flex items-center gap-4">
      <span className="text-[15px] w-14 shrink-0" style={{ color: 'var(--color-text-tertiary)' }}>
        {label}
      </span>
      <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-4)' }}>
        <div
          className="h-full rounded-full"
          style={{
            width: `${animVal}%`,
            backgroundColor: scoreColor(score),
            transition: 'none',
          }}
        />
      </div>
      <span className="text-[15px] w-10 text-right font-bold tabular-nums" style={{ color: scoreColor(score) }}>
        {animVal}
      </span>
    </div>
  );
}

/** Compact assessment card with animated scores */
export function InlineAssessmentCard({ result }: { result: AssessmentResult }) {
  const scoreColor = (s: number) => {
    if (s >= 80) return 'var(--color-accent-emerald)';
    if (s >= 60) return 'var(--color-accent-amber)';
    return 'var(--color-accent-rose)';
  };

  const animatedOverall = useCountUp(result.overall_score, 1000, 200);

  const dims = [
    { label: '完整性', key: 'completeness' as const, delay: 300 },
    { label: '准确性', key: 'accuracy' as const, delay: 450 },
    { label: '深度', key: 'depth' as const, delay: 600 },
    { label: '举例', key: 'examples' as const, delay: 750 },
  ];

  return (
    <div
      className="rounded-lg p-5 animate-fade-in-scale"
      style={{
        backgroundColor: result.mastered ? 'rgba(138, 173, 122, 0.06)' : 'var(--color-surface-2)',
        border: `1px solid ${result.mastered ? 'rgba(138, 173, 122, 0.15)' : 'var(--color-border)'}`,
      }}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          {result.mastered ? (
            <Trophy size={18} style={{ color: 'var(--color-accent-emerald)' }} />
          ) : (
            <BarChart3 size={18} style={{ color: 'var(--color-accent-amber)' }} />
          )}
          <span className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>
            {result.mastered ? '已掌握！' : '评估结果'}
          </span>
        </div>
        <span className="text-3xl font-bold tabular-nums" style={{ color: scoreColor(result.overall_score) }}>
          {animatedOverall}
          <span className="text-sm font-normal ml-1" style={{ color: 'var(--color-text-tertiary)' }}>/100</span>
        </span>
      </div>

      <div className="space-y-3 mb-5">
        {dims.map((dim) => {
          const score = result[dim.key];
          return <AnimatedDimBar key={dim.key} label={dim.label} score={score} delay={dim.delay} scoreColor={scoreColor} />;
        })}
      </div>

      <p className="text-base leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
        {result.feedback}
      </p>

      {result.gaps.length > 0 && (
        <div className="mt-3 pt-3" style={{ borderTop: '1px solid var(--color-border-subtle)' }}>
          <p className="text-sm font-bold mb-2" style={{ color: 'var(--color-accent-amber)' }}>知识盲区</p>
          <ul className="space-y-1">
            {result.gaps.map((gap, i) => (
              <li key={i} className="flex items-start gap-2.5 text-[15px]" style={{ color: 'var(--color-text-secondary)' }}>
                <span className="mt-2 w-1 h-1 rounded-full shrink-0" style={{ backgroundColor: 'var(--color-accent-amber)' }} />
                {gap}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
