import type { AssessmentResult } from '@/lib/store/dialogue';
import {
  BarChart3, Trophy,
  CheckCircle2, Target, BookOpen,
} from 'lucide-react';

/** Full assessment result card for LearnPage — gradient border + dimension icons */
export function LearnAssessmentCard({ result, conceptName }: { result: AssessmentResult; conceptName: string }) {
  const scoreColor = (s: number) => {
    if (s >= 80) return 'var(--color-accent-emerald)';
    if (s >= 60) return 'var(--color-accent-amber)';
    return 'var(--color-accent-rose)';
  };

  const dimensions = [
    { label: '完整性', key: 'completeness' as const, icon: Target },
    { label: '准确性', key: 'accuracy' as const, icon: CheckCircle2 },
    { label: '深度', key: 'depth' as const, icon: BookOpen },
    { label: '举例', key: 'examples' as const, icon: Target },
  ];

  return (
    <div className="animate-fade-in-scale">
      <div
        className="gradient-border"
        style={{
          background: result.mastered
            ? 'linear-gradient(135deg, rgba(52, 211, 153, 0.05), rgba(16, 185, 129, 0.08))'
            : 'var(--color-surface-2)',
        }}
      >
        <div className="rounded-lg p-6" style={{ backgroundColor: 'var(--color-surface-2)' }}>
          {/* Header */}
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-3">
              <div
                className="w-10 h-10 rounded-md flex items-center justify-center"
                style={{
                  backgroundColor: result.mastered
                    ? 'var(--color-accent-emerald)'
                    : 'var(--color-accent-primary)',
                }}
              >
                {result.mastered ? <Trophy size={18} style={{ color: 'var(--color-text-on-accent)' }} /> : <BarChart3 size={18} style={{ color: 'var(--color-text-on-accent)' }} />}
              </div>
              <div>
                <h3 className="text-[15px] font-bold" style={{ color: 'var(--color-text-primary)' }}>
                  {result.mastered ? '理解达标！' : '评估结果'}
                </h3>
                <p className="text-[12px]" style={{ color: 'var(--color-text-tertiary)' }}>
                  {conceptName}
                </p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold font-mono" style={{ color: scoreColor(result.overall_score) }}>
                {result.overall_score}
              </div>
              <div className="text-[10px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>/ 100</div>
            </div>
          </div>

          {/* Dimension bars */}
          <div className="space-y-3 mb-5">
            {dimensions.map((dim) => {
              const score = result[dim.key];
              const Icon = dim.icon;
              return (
                <div key={dim.key}>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="flex items-center gap-1.5 text-[12px] font-medium" style={{ color: 'var(--color-text-secondary)' }}>
                      <Icon size={12} />
                      {dim.label}
                    </span>
                    <span className="text-[12px] font-mono font-semibold" style={{ color: scoreColor(score) }}>
                      {score}
                    </span>
                  </div>
                  <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-4)' }}>
                    <div
                      className="h-1.5 rounded-full transition-all duration-700 ease-out"
                      style={{ width: `${score}%`, backgroundColor: scoreColor(score) }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Feedback */}
          <div
            className="rounded-md px-4 py-3 mb-4"
            style={{ backgroundColor: 'var(--color-surface-3)', border: '1px solid var(--color-border-subtle)' }}
          >
            <p className="text-[13px] leading-relaxed" style={{ color: 'var(--color-text-primary)' }}>
              {result.feedback}
            </p>
          </div>

          {/* Knowledge gaps */}
          {result.gaps.length > 0 && (
            <div>
              <p className="text-[11px] font-mono font-medium uppercase tracking-wider mb-2" style={{ color: 'var(--color-accent-amber)' }}>
                知识盲区
              </p>
              <ul className="space-y-1.5">
                {result.gaps.map((gap, i) => (
                  <li key={i} className="flex items-start gap-2 text-[12px]" style={{ color: 'var(--color-text-secondary)' }}>
                    <span className="mt-1.5 w-1 h-1 rounded-full shrink-0" style={{ backgroundColor: 'var(--color-accent-amber)' }} />
                    {gap}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}