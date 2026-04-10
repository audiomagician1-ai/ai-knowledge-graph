import type { Achievement } from '@/lib/api/learning-api';
import { BookOpen, Flame, Globe, ClipboardCheck, RefreshCw, Star } from 'lucide-react';

export const TIER_COLORS: Record<string, string> = {
  bronze:   'var(--color-accent-bronze)',
  silver:   'var(--color-accent-slate)',
  gold:     'var(--color-accent-gold)',
  platinum: '#E5E4E2',
};

export const TIER_LABELS: Record<string, string> = {
  bronze:   '铜',
  silver:   '银',
  gold:     '金',
  platinum: '铂金',
};

export const CATEGORY_META: Record<string, { label: string; icon: React.ReactNode }> = {
  learning:   { label: '学习里程碑', icon: <BookOpen size={16} /> },
  streak:     { label: '连续学习',   icon: <Flame size={16} /> },
  domain:     { label: '领域深度',   icon: <Globe size={16} /> },
  assessment: { label: '评估表现',   icon: <ClipboardCheck size={16} /> },
  review:     { label: '间隔复习',   icon: <RefreshCw size={16} /> },
  special:    { label: '特殊成就',   icon: <Star size={16} /> },
};

/**
 * Single achievement card — icon, name, tier badge, description, progress bar, unlock status.
 */
export function AchievementCard({ achievement }: { achievement: Achievement }) {
  const tierColor = TIER_COLORS[achievement.tier] || 'var(--color-text-tertiary)';
  const isUnlocked = achievement.unlocked;

  return (
    <div
      style={{
        display: 'flex', alignItems: 'center', gap: 12,
        padding: '12px 16px', borderRadius: 8,
        border: `1px solid ${isUnlocked ? 'var(--color-border-accent)' : 'var(--color-border)'}`,
        backgroundColor: isUnlocked ? 'var(--color-tint-emerald)' : 'var(--color-surface-1)',
        opacity: isUnlocked ? 1 : 0.75, transition: 'all 0.2s ease',
      }}
    >
      <span className="text-[28px] shrink-0" style={{ filter: isUnlocked ? 'none' : 'grayscale(0.6)' }}>
        {achievement.icon}
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div className="flex items-center gap-2 mb-0.5">
          <span className="font-semibold text-sm text-[var(--color-text-primary)]">{achievement.name}</span>
          <span className="text-[11px] font-semibold px-1.5 py-px rounded text-[var(--color-text-on-accent)] leading-4" style={{ backgroundColor: tierColor }}>
            {TIER_LABELS[achievement.tier] || achievement.tier}
          </span>
        </div>
        <p className="text-xs text-[var(--color-text-tertiary)] my-0.5 mb-1.5 leading-snug">
          {achievement.description}
        </p>
        <div style={{ width: '100%', height: 6, borderRadius: 3, backgroundColor: 'var(--color-surface-3)', overflow: 'hidden' }}>
          <div style={{
            height: '100%', width: `${Math.min(100, achievement.progress)}%`, borderRadius: 3,
            backgroundColor: isUnlocked ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)', transition: 'width 0.5s ease',
          }} />
        </div>
        <div className="text-[11px] text-[var(--color-text-tertiary)] mt-1 flex justify-between">
          <span>
            {isUnlocked
              ? `✅ 已解锁${achievement.unlocked_at ? ' · ' + new Date(achievement.unlocked_at * 1000).toLocaleDateString('zh-CN') : ''}`
              : `${Math.round(achievement.progress)}%`}
          </span>
        </div>
      </div>
    </div>
  );
}
