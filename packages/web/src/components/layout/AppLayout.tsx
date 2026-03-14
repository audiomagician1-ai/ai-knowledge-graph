import { Outlet } from 'react-router-dom';

export function AppLayout() {
  return (
    <div className="h-dvh w-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <Outlet />
    </div>
  );
}
