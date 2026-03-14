import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { BottomNav } from './BottomNav';
import { useIsDesktop } from '@/lib/hooks/useMediaQuery';

export function AppLayout() {
  const isDesktop = useIsDesktop();

  return (
    <div className="flex h-dvh" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      {isDesktop && <Sidebar />}
      <main className="flex-1 min-w-0 overflow-hidden" style={{ paddingBottom: isDesktop ? 0 : 'var(--bottom-nav-height, 56px)' }}>
        <Outlet />
      </main>
      {!isDesktop && <BottomNav />}
    </div>
  );
}
