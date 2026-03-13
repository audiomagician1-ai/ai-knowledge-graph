import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';

export function AppLayout() {
  return (
    <div className="flex h-dvh bg-mesh noise-overlay" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <Sidebar />
      <main className="flex-1 min-w-0 overflow-hidden">
        <Outlet />
      </main>
    </div>
  );
}
