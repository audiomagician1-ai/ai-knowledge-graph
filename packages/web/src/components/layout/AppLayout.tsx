import { Outlet } from 'react-router-dom';
import { BottomNav } from './BottomNav';

export function AppLayout() {
  return (
    <div className="flex min-h-dvh flex-col" style={{ backgroundColor: '#0f172a' }}>
      <main className="flex-1" style={{ paddingBottom: 'var(--bottom-nav-height)' }}>
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}
