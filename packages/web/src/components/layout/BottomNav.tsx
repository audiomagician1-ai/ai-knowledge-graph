import { useNavigate, useLocation } from 'react-router-dom';
import { Network, BarChart3, Settings } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/graph', icon: Network, label: '图谱' },
  { path: '/dashboard', icon: BarChart3, label: '进度' },
  { path: '/settings', icon: Settings, label: '设置' },
] as const;

export function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();

  // 学习页面隐藏底部导航
  if (location.pathname.startsWith('/learn/')) return null;

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around border-t"
      style={{
        height: 'var(--bottom-nav-height, 56px)',
        backgroundColor: 'var(--color-surface-1)',
        borderColor: 'var(--color-border)',
        paddingBottom: 'env(safe-area-inset-bottom, 0px)',
      }}
      data-testid="bottom-nav"
    >
      {NAV_ITEMS.map(({ path, icon: Icon, label }) => {
        const isActive = location.pathname === path;
        return (
          <button
            key={path}
            onClick={() => navigate(path)}
            className="flex flex-col items-center justify-center gap-1 px-5 py-2 transition-colors duration-150 rounded-lg"
            style={{
              color: isActive ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)',
              minWidth: 72,
              minHeight: 52,
            }}
          >
            <Icon size={22} strokeWidth={isActive ? 2.5 : 2} />
            <span className="text-xs font-medium">{label}</span>
          </button>
        );
      })}
    </nav>
  );
}
