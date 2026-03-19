import { useNavigate, useLocation } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { useAuthStore } from '@/lib/store/auth';
import { Network, BarChart3, Settings, Zap, BookOpen, LogIn, LogOut, User } from 'lucide-react';
import { DomainSwitcher } from './DomainSwitcher';

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
  const { user, supabaseConfigured, signOut } = useAuthStore();
  const isLoggedIn = !!user;
  const displayName = useAuthStore((s) => s.displayName());
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
            <BookOpen size={16} style={{ color: '#ffffff' }} />
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

      {/* Domain Switcher */}
      <DomainSwitcher />

      {/* User section */}
      {supabaseConfigured && (
        <div className="px-4 pb-3">
          {isLoggedIn ? (
            <div
              className="flex items-center gap-3 rounded-lg px-4 py-3"
              style={{ backgroundColor: 'var(--color-surface-2)' }}
            >
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center shrink-0"
                style={{ backgroundColor: 'var(--color-accent-primary)', color: '#fff', fontSize: 13, fontWeight: 600 }}
              >
                {(displayName || '?')[0].toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate" style={{ color: 'var(--color-text-primary)' }}>
                  {displayName}
                </div>
                <div className="text-xs truncate" style={{ color: 'var(--color-text-tertiary)' }}>
                  已同步
                </div>
              </div>
              <button
                onClick={() => signOut()}
                className="shrink-0 p-1.5 rounded-md transition-colors"
                style={{ color: 'var(--color-text-tertiary)' }}
                title="退出登录"
              >
                <LogOut size={16} />
              </button>
            </div>
          ) : (
            <button
              onClick={() => navigate('/login')}
              className="w-full flex items-center gap-3 rounded-lg px-4 py-3 transition-colors"
              style={{ backgroundColor: 'var(--color-surface-2)', color: 'var(--color-text-secondary)' }}
              onMouseEnter={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-surface-3)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.backgroundColor = 'var(--color-surface-2)'; }}
            >
              <LogIn size={18} style={{ color: 'var(--color-accent-primary)' }} />
              <span className="text-sm font-medium">登录 · 跨端同步</span>
            </button>
          )}
        </div>
      )}

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