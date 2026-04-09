import type { Achievement } from '@/lib/api/learning-api';

export const TIER_COLORS: Record<string, string> = {
  bronze:   '#CD7F32',
  silver:   '#C0C0C0',
  gold:     '#FFD700',
  platinum: '#E5E4E2',
};

export const TIER_LABELS: Record<string, string> = {
  bronze:   '铜',
  silver:   '银',
  gold:     '金',
  platinum: '铂金',
};

export const CATEGORY_META: Record<string, { label: string; icon: string }> = {
  learning:   { label: '学习里程碑', icon: '📖' },
  streak:     { label: '连续学习',   icon: '🔥' },
  domain:     { label: '领域深度',   icon: '🌐' },
  assessment: { label: '评估表现',   icon: '📝' },
  review:     { label: '间隔复习',   icon: '🔄' },
  special:    { label: '特殊成就',   icon: '⭐' },
};

/**
 * Single achievement card — icon, name, tier badge, description, progress bar, unlock status.
 */
export function AchievementCard({ achievement }: { achievement: Achievement }) {
  const tierColor = TIER_COLORS[achievement.tier] || '#888';
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
      <span style={{ fontSize: 28, flexShrink: 0, filter: isUnlocked ? 'none' : 'grayscale(0.6)' }}>
        {achievement.icon}
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
          <span style={{ fontWeight: 600, fontSize: 14, color: 'var(--color-text-primary)' }}>{achievement.name}</span>
          <span style={{ fontSize: 11, fontWeight: 600, padding: '1px 6px', borderRadius: 4, color: '#fff', backgroundColor: tierColor, lineHeight: '16px' }}>
            {TIER_LABELS[achievement.tier] || achievement.tier}
          </span>
        </div>
        <p style={{ fontSize: 12, color: 'var(--color-text-tertiary)', margin: '2px 0 6px 0', lineHeight: 1.4 }}>
          {achievement.description}
        </p>
        <div style={{ width: '100%', height: 6, borderRadius: 3, backgroundColor: 'var(--color-surface-3)', overflow: 'hidden' }}>
          <div style={{
            height: '100%', width: `${Math.min(100, achievement.progress)}%`, borderRadius: 3,
            backgroundColor: isUnlocked ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)', transition: 'width 0.5s ease',
          }} />
        </div>
        <div style={{ fontSize: 11, color: 'var(--color-text-tertiary)', marginTop: 3, display: 'flex', justifyContent: 'space-between' }}>
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
