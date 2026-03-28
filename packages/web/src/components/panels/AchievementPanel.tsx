/**
 * AchievementPanel — Displays all achievements grouped by category.
 *
 * Shows achievement icon, name, description, tier badge, progress bar, and unlock status.
 * Used inside a DraggableModal from GraphPage.
 */
import { useEffect } from 'react';
import { createLogger } from '@/lib/utils/logger';
import { useAchievementStore } from '@/lib/store/achievements';
import { Trophy, Loader } from 'lucide-react';
import type { Achievement } from '@/lib/api/learning-api';

const log = createLogger('AchievementPanel');

const CATEGORY_META: Record<string, { label: string; icon: string }> = {
  learning:   { label: '学习里程碑', icon: '📖' },
  streak:     { label: '连续学习',   icon: '🔥' },
  domain:     { label: '领域深度',   icon: '🌐' },
  assessment: { label: '评估表现',   icon: '📝' },
  review:     { label: '间隔复习',   icon: '🔄' },
  special:    { label: '特殊成就',   icon: '⭐' },
};

const TIER_COLORS: Record<string, string> = {
  bronze:   '#CD7F32',
  silver:   '#C0C0C0',
  gold:     '#FFD700',
  platinum: '#E5E4E2',
};

const TIER_LABELS: Record<string, string> = {
  bronze:   '铜',
  silver:   '银',
  gold:     '金',
  platinum: '铂金',
};

function AchievementCard({ achievement }: { achievement: Achievement }) {
  const tierColor = TIER_COLORS[achievement.tier] || '#888';
  const isUnlocked = achievement.unlocked;

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        padding: '12px 16px',
        borderRadius: 8,
        border: `1px solid ${isUnlocked ? 'var(--color-border-accent)' : 'var(--color-border)'}`,
        backgroundColor: isUnlocked ? 'var(--color-tint-emerald)' : 'var(--color-surface-1)',
        opacity: isUnlocked ? 1 : 0.75,
        transition: 'all 0.2s ease',
      }}
    >
      {/* Icon */}
      <span style={{ fontSize: 28, flexShrink: 0, filter: isUnlocked ? 'none' : 'grayscale(0.6)' }}>
        {achievement.icon}
      </span>

      {/* Content */}
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 2 }}>
          <span style={{
            fontWeight: 600,
            fontSize: 14,
            color: 'var(--color-text-primary)',
          }}>
            {achievement.name}
          </span>
          <span style={{
            fontSize: 11,
            fontWeight: 600,
            padding: '1px 6px',
            borderRadius: 4,
            color: '#fff',
            backgroundColor: tierColor,
            lineHeight: '16px',
          }}>
            {TIER_LABELS[achievement.tier] || achievement.tier}
          </span>
        </div>

        <p style={{
          fontSize: 12,
          color: 'var(--color-text-tertiary)',
          margin: '2px 0 6px 0',
          lineHeight: 1.4,
        }}>
          {achievement.description}
        </p>

        {/* Progress bar */}
        <div style={{
          width: '100%',
          height: 6,
          borderRadius: 3,
          backgroundColor: 'var(--color-surface-3)',
          overflow: 'hidden',
        }}>
          <div style={{
            height: '100%',
            width: `${Math.min(100, achievement.progress)}%`,
            borderRadius: 3,
            backgroundColor: isUnlocked ? 'var(--color-accent-emerald)' : 'var(--color-accent-amber)',
            transition: 'width 0.5s ease',
          }} />
        </div>

        {/* Status text */}
        <div style={{
          fontSize: 11,
          color: 'var(--color-text-tertiary)',
          marginTop: 3,
          display: 'flex',
          justifyContent: 'space-between',
        }}>
          <span>
            {isUnlocked
              ? `✅ 已解锁${achievement.unlocked_at
                  ? ' · ' + new Date(achievement.unlocked_at * 1000).toLocaleDateString('zh-CN')
                  : ''
                }`
              : `${Math.round(achievement.progress)}%`
            }
          </span>
        </div>
      </div>
    </div>
  );
}

export function AchievementPanel() {
  const { achievements, summary, loading, fetchAchievements, markAllSeen, unseenCount } = useAchievementStore();

  useEffect(() => {
    fetchAchievements();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- stable ref
  }, []);

  // Mark all as seen when panel opens
  useEffect(() => {
    if (unseenCount > 0) markAllSeen();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- stable ref
  }, [unseenCount]);

  if (loading && achievements.length === 0) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: 40 }}>
        <Loader size={24} style={{ animation: 'spin 1s linear infinite', color: 'var(--color-text-tertiary)' }} />
      </div>
    );
  }

  // Group by category
  const grouped: Record<string, Achievement[]> = {};
  for (const ach of achievements) {
    if (!grouped[ach.category]) grouped[ach.category] = [];
    grouped[ach.category].push(ach);
  }

  const categoryOrder = ['learning', 'streak', 'domain', 'assessment', 'review', 'special'];

  return (
    <div style={{ padding: '16px 20px', overflowY: 'auto', maxHeight: '70vh' }}>
      {/* Summary */}
      {summary && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: 12,
          padding: '12px 16px',
          marginBottom: 16,
          borderRadius: 8,
          backgroundColor: 'var(--color-surface-2)',
          border: '1px solid var(--color-border)',
        }}>
          <Trophy size={20} style={{ color: 'var(--color-accent-amber)' }} />
          <span style={{
            fontSize: 14,
            fontWeight: 600,
            color: 'var(--color-text-primary)',
          }}>
            {summary.unlocked} / {summary.total} 成就已解锁
          </span>
          <div style={{
            flex: 1,
            height: 6,
            borderRadius: 3,
            backgroundColor: 'var(--color-surface-3)',
            overflow: 'hidden',
          }}>
            <div style={{
              height: '100%',
              width: `${summary.total > 0 ? (summary.unlocked / summary.total) * 100 : 0}%`,
              borderRadius: 3,
              backgroundColor: 'var(--color-accent-amber)',
              transition: 'width 0.5s ease',
            }} />
          </div>
        </div>
      )}

      {/* Category groups */}
      {categoryOrder.map(cat => {
        const items = grouped[cat];
        if (!items || items.length === 0) return null;
        const meta = CATEGORY_META[cat] || { label: cat, icon: '📋' };
        const unlockedInCat = items.filter(a => a.unlocked).length;

        return (
          <div key={cat} style={{ marginBottom: 20 }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: 8,
              marginBottom: 10,
            }}>
              <span style={{ fontSize: 16 }}>{meta.icon}</span>
              <span style={{
                fontSize: 13,
                fontWeight: 600,
                color: 'var(--color-text-secondary)',
                textTransform: 'uppercase',
                letterSpacing: '0.5px',
              }}>
                {meta.label}
              </span>
              <span style={{
                fontSize: 11,
                color: 'var(--color-text-tertiary)',
                marginLeft: 4,
              }}>
                ({unlockedInCat}/{items.length})
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {items.map(ach => (
                <AchievementCard key={ach.key} achievement={ach} />
              ))}
            </div>
          </div>
        );
      })}

      {achievements.length === 0 && !loading && (
        <div style={{
          textAlign: 'center',
          padding: 40,
          color: 'var(--color-text-tertiary)',
          fontSize: 14,
        }}>
          暂无成就数据。开始学习以解锁成就！
        </div>
      )}
    </div>
  );
}
