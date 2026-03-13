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
        height: 'var(--bottom-nav-height)',
        backgroundColor: '#1e293b',
        borderColor: '#334155',
        paddingBottom: 'var(--safe-area-bottom)',
      }}
      data-testid="bottom-nav"
    >
      {NAV_ITEMS.map(({ path, icon: Icon, label }) => {
        const isActive = location.pathname === path;
        return (
          <button
            key={path}
            onClick={() => navigate(path)}
            className="flex flex-col items-center justify-center gap-1 px-4 py-2"
            style={{
              color: isActive ? '#8b5cf6' : '#64748b',
              minWidth: 64,
              minHeight: 44, // 触控目标 ≥ 44px
            }}
          >
            <Icon size={22} />
            <span className="text-xs">{label}</span>
          </button>
        );
      })}
    </nav>
  );
}
