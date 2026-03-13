import { Outlet } from 'react-router-dom';
import { BottomNav } from './BottomNav';
import { useEffect } from 'react';
import { useAuthStore } from '@/lib/store/auth';

export function AppLayout() {
  const initialize = useAuthStore((s) => s.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <div className="flex min-h-dvh flex-col" style={{ backgroundColor: 'var(--bg-primary)' }}>
      <main className="flex-1" style={{ paddingBottom: 'var(--bottom-nav-height)' }}>
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
}
