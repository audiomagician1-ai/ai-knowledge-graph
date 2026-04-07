/**
 * GraphStatusFilter — Quick filter buttons for node status in the 3D graph.
 * Allows filtering to show only mastered, learning, or all nodes.
 */
import { CheckCircle, BookOpen, Eye } from 'lucide-react';

export type StatusFilterValue = 'all' | 'mastered' | 'learning' | 'not_started';

interface GraphStatusFilterProps {
  value: StatusFilterValue;
  onChange: (value: StatusFilterValue) => void;
  counts: { mastered: number; learning: number; notStarted: number; total: number };
}

const FILTERS: { value: StatusFilterValue; label: string; icon: typeof Eye; color: string }[] = [
  { value: 'all', label: '全部', icon: Eye, color: '#6b7280' },
  { value: 'mastered', label: '已掌握', icon: CheckCircle, color: '#10b981' },
  { value: 'learning', label: '学习中', icon: BookOpen, color: '#f59e0b' },
];

export function GraphStatusFilter({ value, onChange, counts }: GraphStatusFilterProps) {
  return (
    <div className="absolute bottom-4 right-4 z-10 pointer-events-auto">
      <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/60 dark:border-gray-700/60 flex items-center gap-1 p-1">
        {FILTERS.map(f => {
          const isActive = value === f.value;
          const Icon = f.icon;
          const count = f.value === 'all' ? counts.total :
            f.value === 'mastered' ? counts.mastered :
            f.value === 'learning' ? counts.learning : counts.notStarted;
          return (
            <button
              key={f.value}
              onClick={() => onChange(f.value)}
              className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-gray-100 dark:bg-gray-800 shadow-sm'
                  : 'hover:bg-gray-50 dark:hover:bg-gray-800/50'
              }`}
              style={{ color: isActive ? f.color : '#9ca3af' }}
              aria-label={`筛选: ${f.label}`}
            >
              <Icon size={12} />
              <span>{f.label}</span>
              <span className="text-[10px] opacity-60 tabular-nums">{count}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
