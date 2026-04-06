import { Outlet } from 'react-router-dom';
import { OfflineIndicator } from '../common/OfflineIndicator';

export function AppLayout() {
  return (
    <div className="h-dvh w-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <OfflineIndicator />
      <Outlet />
    </div>
  );
}
