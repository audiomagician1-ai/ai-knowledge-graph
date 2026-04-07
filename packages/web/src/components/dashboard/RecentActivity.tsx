/**
 * RecentActivity — Timeline of recent learning actions.
 * Shows the last N assessments, learning sessions, and milestones with timestamps.
 */
import { useMemo } from 'react';
import { useLearningStore } from '@/lib/store/learning';
import { CheckCircle, BookOpen, Star, Clock, Activity } from 'lucide-react';

interface RecentActivityProps {
  maxItems?: number;
}

interface ActivityItem {
  id: string;
  conceptId: string;
  type: 'mastered' | 'assessed' | 'started';
  timestamp: number;
  score?: number;
}

function formatTimeAgo(ts: number): string {
  const now = Date.now();
  const diff = now - ts;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  if (days < 7) return `${days}天前`;
  return new Date(ts).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

const TYPE_CONFIG = {
  mastered: { icon: CheckCircle, color: '#10b981', label: '掌握了', bg: '#10b98120' },
  assessed: { icon: Star, color: '#f59e0b', label: '评估了', bg: '#f59e0b20' },
  started: { icon: BookOpen, color: '#06b6d4', label: '开始学习', bg: '#06b6d420' },
} as const;

export function RecentActivity({ maxItems = 10 }: RecentActivityProps) {
  const progress = useLearningStore(s => s.progress);
  const history = useLearningStore(s => s.history);

  const activities = useMemo(() => {
    const items: ActivityItem[] = [];

    // From progress: mastered events
    for (const [conceptId, p] of Object.entries(progress)) {
      if (p.status === 'mastered' && p.mastered_at) {
        items.push({
          id: `m-${conceptId}`,
          conceptId,
          type: 'mastered',
          timestamp: p.mastered_at,
          score: p.mastery_score,
        });
      }
      // Started learning
      if (p.last_learn_at && p.sessions >= 1) {
        items.push({
          id: `s-${conceptId}`,
          conceptId,
          type: p.status === 'mastered' ? 'assessed' : 'started',
          timestamp: p.last_learn_at,
          score: p.last_score,
        });
      }
    }

    // Sort by timestamp descending (most recent first)
    items.sort((a, b) => b.timestamp - a.timestamp);

    // Deduplicate by conceptId (keep most recent action)
    const seen = new Set<string>();
    const deduped: ActivityItem[] = [];
    for (const item of items) {
      if (!seen.has(item.conceptId)) {
        seen.add(item.conceptId);
        deduped.push(item);
      }
    }

    return deduped.slice(0, maxItems);
  }, [progress, history, maxItems]);

  if (activities.length === 0) {
    return (
      <div className="text-center py-6 text-gray-400">
        <Activity size={20} className="mx-auto mb-2 opacity-50" />
        <p className="text-xs">开始学习后将在此显示活动记录</p>
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {activities.map((item, idx) => {
        const config = TYPE_CONFIG[item.type];
        const Icon = config.icon;
        return (
          <div key={item.id} className="flex items-center gap-3 py-2 px-1 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
            {/* Timeline dot + line */}
            <div className="relative flex-shrink-0">
              <div className="w-7 h-7 rounded-full flex items-center justify-center" style={{ backgroundColor: config.bg }}>
                <Icon size={13} style={{ color: config.color }} />
              </div>
              {idx < activities.length - 1 && (
                <div className="absolute top-7 left-1/2 -translate-x-1/2 w-px h-3 bg-gray-200 dark:bg-gray-700" />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-medium text-gray-700 dark:text-gray-200 truncate">
                  {item.conceptId.replace(/-/g, ' ')}
                </span>
                {item.score != null && item.score > 0 && (
                  <span className="text-[10px] font-medium px-1.5 py-0.5 rounded" style={{ backgroundColor: config.bg, color: config.color }}>
                    {item.score}分
                  </span>
                )}
              </div>
              <div className="flex items-center gap-1 text-[10px] text-gray-400">
                <span>{config.label}</span>
                <span>·</span>
                <Clock size={9} />
                <span>{formatTimeAgo(item.timestamp)}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
