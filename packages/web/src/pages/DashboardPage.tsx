import { useLearningStore } from '@/lib/store/learning';

/**
 * 学习进度面板
 * TODO: Phase 3 实现完整统计面板
 */
export function DashboardPage() {
  const stats = useLearningStore((s) => s.stats);

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* 顶部栏 */}
      <header
        className="flex items-center px-4"
        style={{
          height: 'var(--header-height)',
          paddingTop: 'var(--safe-area-top)',
          backgroundColor: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-default)',
        }}
      >
        <h1 className="text-lg font-bold" style={{ color: 'var(--text-primary)' }}>
          学习进度
        </h1>
      </header>

      <div className="px-4 py-6">
        {/* 统计卡片 */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          {[
            { label: '已掌握', value: stats?.mastered_count ?? 0, icon: '⭐', color: 'var(--node-mastered)' },
            { label: '学习中', value: stats?.learning_count ?? 0, icon: '📖', color: 'var(--node-learning)' },
            { label: '可学习', value: stats?.available_count ?? 0, icon: '🔓', color: 'var(--node-available)' },
            { label: '总节点', value: stats?.total_concepts ?? 0, icon: '🌐', color: 'var(--text-muted)' },
          ].map(({ label, value, icon, color }) => (
            <div
              key={label}
              className="rounded-xl p-4"
              style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-default)' }}
            >
              <div className="text-2xl mb-1">{icon}</div>
              <div className="text-2xl font-bold" style={{ color }}>{value}</div>
              <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>{label}</div>
            </div>
          ))}
        </div>

        {/* 学习连续天数 */}
        <div
          className="rounded-xl p-4 mb-6"
          style={{ backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-default)' }}
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm" style={{ color: 'var(--text-secondary)' }}>连续学习</div>
              <div className="text-3xl font-bold" style={{ color: 'var(--color-accent)' }}>
                {stats?.current_streak ?? 0} 天
              </div>
            </div>
            <div className="text-4xl">🔥</div>
          </div>
        </div>

        <p className="text-center text-sm" style={{ color: 'var(--text-muted)' }}>
          更多学习统计将在后续版本中添加
        </p>
      </div>
    </div>
  );
}
