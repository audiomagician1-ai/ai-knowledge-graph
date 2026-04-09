/**
 * AchievementPanel — Displays all achievements grouped by category.
 *
 * Shows achievement icon, name, description, tier badge, progress bar, and unlock status.
 * Used inside a DraggableModal from GraphPage.
 */
import { useEffect } from 'react';
import { useAchievementStore } from '@/lib/store/achievements';
import { Trophy, Loader } from 'lucide-react';
import { AchievementCard, CATEGORY_META } from './AchievementParts';
import type { Achievement } from '@/lib/api/learning-api';

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
