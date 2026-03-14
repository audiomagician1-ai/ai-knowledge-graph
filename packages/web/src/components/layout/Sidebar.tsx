import { useNavigate, useLocation } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { Network, BarChart3, Settings, Zap } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/graph', icon: Network, label: '图谱' },
  { path: '/dashboard', icon: BarChart3, label: '进度' },
  { path: '/settings', icon: Settings, label: '设置' },
] as const;

export function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { graphData } = useGraphStore();
  const { progress } = useLearningStore();
  const totalNodes = graphData?.nodes.length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;
  const progressPct = totalNodes > 0 ? Math.round((masteredCount / totalNodes) * 100) : 0;

  return (
    <aside
      className="flex flex-col h-full shrink-0 border-r"
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: 'var(--color-surface-1)',
        borderColor: 'var(--color-border)',
      }}
    >
      {/* Brand */}
      <div className="px-5 pt-6 pb-5">
        <button onClick={() => navigate('/graph')} className="flex items-center gap-2.5">
          <div
            className="w-7 h-7 rounded-md flex items-center justify-center"
            style={{ backgroundColor: 'var(--color-accent-primary)' }}
          >
            <span className="text-xs font-bold" style={{ color: '#0a0c10' }}>AI</span>
          </div>
          <span className="text-sm font-semibold tracking-tight" style={{ color: 'var(--color-text-primary)' }}>
            Knowledge Graph
          </span>
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3">
        {NAV_ITEMS.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className="w-full flex items-center gap-2.5 px-3 py-2 rounded-lg mb-0.5 transition-all duration-150"
              style={{
                backgroundColor: isActive ? 'var(--color-surface-3)' : 'transparent',
                color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-tertiary)',
              }}
            >
              <Icon size={16} style={isActive ? { color: 'var(--color-accent-primary)' } : undefined} />
              <span className="text-[13px] font-medium">{label}</span>
            </button>
          );
        })}
      </nav>

      {/* Bottom stats */}
      {totalNodes > 0 && (
        <div className="px-4 pb-5">
          <div className="flex items-center gap-2 mb-2">
            <Zap size={12} style={{ color: 'var(--color-accent-emerald)' }} />
            <span className="text-[11px] font-mono" style={{ color: 'var(--color-text-tertiary)' }}>
              {masteredCount}/{totalNodes}
            </span>
            <span className="text-[11px] font-mono ml-auto" style={{ color: 'var(--color-text-tertiary)' }}>
              {progressPct}%
            </span>
          </div>
          <div className="h-1 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-4)' }}>
            <div
              className="h-full rounded-full transition-all duration-700"
              style={{
                width: `${progressPct}%`,
                backgroundColor: 'var(--color-accent-emerald)',
                minWidth: progressPct > 0 ? 3 : 0,
              }}
            />
          </div>
        </div>
      )}
    </aside>
  );
}