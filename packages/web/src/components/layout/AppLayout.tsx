import { Outlet, useLocation } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function AppLayout() {
  const location = useLocation();
  const isLearnPage = location.pathname.startsWith('/learn/');

  return (
    <div className="flex h-dvh bg-mesh noise-overlay" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      {!isLearnPage && <Sidebar />}
      <main className="flex-1 min-w-0 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
