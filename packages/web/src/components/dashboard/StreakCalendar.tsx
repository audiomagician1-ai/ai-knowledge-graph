import { useMemo } from 'react';

interface StreakCalendarProps {
  history: Array<{ timestamp: number }>;
}

/** 30-day streak heatmap calendar */
export function StreakCalendar({ history }: StreakCalendarProps) {
  const days = useMemo(() => {
    const result: { date: string; count: number; label: string }[] = [];
    const now = Date.now();
    const dayCounts = new Map<string, number>();

    for (const h of history) {
      const d = new Date(h.timestamp || 0);
      const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
      dayCounts.set(key, (dayCounts.get(key) || 0) + 1);
    }

    for (let i = 29; i >= 0; i--) {
      const date = new Date(now - i * 86400_000);
      const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
      const weekDay = ['日', '一', '二', '三', '四', '五', '六'][date.getDay()];
      const label = `${date.getMonth() + 1}/${date.getDate()} ${weekDay}`;
      result.push({ date: key, count: dayCounts.get(key) || 0, label });
    }
    return result;
  }, [history]);

  const maxCount = Math.max(1, ...days.map((d) => d.count));

  return (
    <div className="flex flex-wrap gap-1.5">
      {days.map((day) => {
        const intensity = day.count === 0 ? 0 : Math.max(0.2, day.count / maxCount);
        return (
          <div
            key={day.date}
            title={`${day.label}: ${day.count} 次学习`}
            className="rounded-sm transition-colors"
            style={{
              width: 18,
              height: 18,
              backgroundColor: day.count === 0
                ? 'var(--color-surface-3)'
                : `rgba(34, 197, 94, ${intensity})`,
              border: '1px solid var(--color-surface-4)',
            }}
          />
        );
      })}
      <div className="w-full flex items-center justify-between mt-1">
        <span className="text-xs opacity-40">30天前</span>
        <div className="flex items-center gap-1">
          <span className="text-xs opacity-40">少</span>
          {[0, 0.2, 0.5, 0.8, 1].map((v, i) => (
            <div
              key={i}
              className="rounded-sm"
              style={{
                width: 10,
                height: 10,
                backgroundColor: v === 0 ? 'var(--color-surface-3)' : `rgba(34, 197, 94, ${v})`,
              }}
            />
          ))}
          <span className="text-xs opacity-40">多</span>
        </div>
        <span className="text-xs opacity-40">今天</span>
      </div>
    </div>
  );
}