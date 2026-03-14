import { useNavigate, useLocation } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { Network, BarChart3, Settings, Zap, BookOpen } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/graph', icon: Network, label: '知识图谱' },
  { path: '/dashboard', icon: BarChart3, label: '学习进度' },
  { path: '/settings', icon: Settings, label: '设置' },
] as const;

export function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { graphData } = useGraphStore();
  const { progress } = useLearningStore();
  const totalNodes = graphData?.nodes.length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;
  const learningCount = Object.values(progress).filter(p => p.status === 'learning').length;
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
      <div className="px-6 pt-7 pb-6">
        <button onClick={() => navigate('/graph')} className="flex items-center gap-3 group">
          <div
            className="w-9 h-9 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: 'var(--color-accent-primary)' }}
          >
            <BookOpen size={16} style={{ color: '#111110' }} />
          </div>
          <div className="flex flex-col">
            <span style={{ fontFamily: 'var(--font-heading, "Noto Serif SC", Georgia, serif)', color: 'var(--color-text-primary)', fontSize: '15px', fontWeight: 500 }}>
              知识图谱
            </span>
            <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
              Knowledge Graph
            </span>
          </div>
        </button>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-4 space-y-1">
        {NAV_ITEMS.map(({ path, icon: Icon, label }) => {
          const isActive = location.pathname === path;
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-150"
              style={{
                backgroundColor: isActive ? 'var(--color-surface-3)' : 'transparent',
                color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
                minHeight: 48,
              }}
              onMouseEnter={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'var(--color-surface-2)';
              }}
              onMouseLeave={(e) => {
                if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <Icon size={20} style={isActive ? { color: 'var(--color-accent-primary)' } : undefined} />
              <span className="text-[15px] font-medium">{label}</span>
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full" style={{ backgroundColor: 'var(--color-accent-primary)' }} />
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom stats */}
      {totalNodes > 0 && (
        <div className="px-5 pb-6">
          <div className="rounded-lg p-4" style={{ backgroundColor: 'var(--color-surface-2)', border: '1px solid var(--color-border)' }}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium" style={{ color: 'var(--color-text-tertiary)' }}>学习进度</span>
              <span className="text-xs font-medium font-mono" style={{ color: 'var(--color-accent-primary)' }}>{progressPct}%</span>
            </div>
            <div className="h-1.5 rounded-full overflow-hidden mb-2" style={{ backgroundColor: 'var(--color-surface-4)' }}>
              <div
                className="h-full rounded-full transition-all duration-700"
                style={{ width: `${progressPct}%`, backgroundColor: 'var(--color-accent-emerald)', minWidth: progressPct > 0 ? 4 : 0 }}
              />
            </div>
            <div className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
              {masteredCount} 掌握 · {learningCount} 学习中 · 共 {totalNodes}
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}