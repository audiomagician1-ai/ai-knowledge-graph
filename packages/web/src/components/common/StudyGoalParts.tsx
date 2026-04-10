import { CheckCircle2 } from 'lucide-react';

/** SVG ring progress indicator */
export function ProgressRing({
  progress,
  color,
  label,
  value,
  done,
}: {
  progress: number;
  color: string;
  label: string;
  value: string;
  done: boolean;
}) {
  const radius = 36;
  const stroke = 5;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference * (1 - progress / 100);

  return (
    <div className="flex flex-col items-center gap-1">
      <div className="relative" style={{ width: 80, height: 80 }}>
        <svg width="80" height="80" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r={radius} fill="none" stroke="var(--color-surface-3)" strokeWidth={stroke} />
          <circle
            cx="40" cy="40" r={radius} fill="none"
            stroke={done ? '#22c55e' : color} strokeWidth={stroke} strokeLinecap="round"
            strokeDasharray={circumference} strokeDashoffset={dashOffset}
            transform="rotate(-90 40 40)"
            style={{ transition: 'stroke-dashoffset 0.5s ease' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          {done ? <CheckCircle2 size={20} style={{ color: '#22c55e' }} /> : <span className="text-sm font-bold">{progress}%</span>}
        </div>
      </div>
      <span className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{label} {value}</span>
    </div>
  );
}

/** Goal settings editor */
export function GoalSettings({
  goal,
  onUpdate,
  onClose,
}: {
  goal: { dailyConceptTarget: number; dailyTimeTarget: number; enabled: boolean };
  onUpdate: (patch: Partial<typeof goal>) => void;
  onClose: () => void;
}) {
  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium block mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>每日概念目标</label>
        <div className="flex items-center gap-3">
          {[1, 3, 5, 10].map((v) => (
            <button key={v} onClick={() => onUpdate({ dailyConceptTarget: v })}
              className="px-3 py-1.5 rounded-lg text-sm transition-colors"
              style={{ backgroundColor: goal.dailyConceptTarget === v ? 'var(--color-accent-primary)' : 'var(--color-surface-3)', color: goal.dailyConceptTarget === v ? 'var(--color-text-on-accent)' : 'var(--color-text-primary)' }}>
              {v} 个
            </button>
          ))}
        </div>
      </div>
      <div>
        <label className="text-sm font-medium block mb-1.5" style={{ color: 'var(--color-text-secondary)' }}>每日时间目标</label>
        <div className="flex items-center gap-3">
          {[5, 15, 30, 60].map((v) => (
            <button key={v} onClick={() => onUpdate({ dailyTimeTarget: v })}
              className="px-3 py-1.5 rounded-lg text-sm transition-colors"
              style={{ backgroundColor: goal.dailyTimeTarget === v ? 'var(--color-accent-primary)' : 'var(--color-surface-3)', color: goal.dailyTimeTarget === v ? 'var(--color-text-on-accent)' : 'var(--color-text-primary)' }}>
              {v} 分钟
            </button>
          ))}
        </div>
      </div>
      <div className="flex items-center justify-between">
        <label className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>启用每日目标</label>
        <button onClick={() => onUpdate({ enabled: !goal.enabled })}
          className="w-10 h-6 rounded-full relative transition-colors"
          style={{ backgroundColor: goal.enabled ? 'var(--color-accent-primary)' : 'var(--color-surface-3)' }} aria-label="切换每日目标">
          <div className="w-4 h-4 rounded-full bg-white absolute top-1 transition-all" style={{ left: goal.enabled ? '22px' : '4px' }} />
        </button>
      </div>
      <button onClick={onClose} className="w-full py-2 rounded-lg text-sm transition-colors" style={{ backgroundColor: 'var(--color-surface-3)' }}>完成设置</button>
    </div>
  );
}
