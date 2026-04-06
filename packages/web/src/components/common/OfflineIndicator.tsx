import { WifiOff } from 'lucide-react';
import { useOnlineStatus } from '@/lib/hooks/useOnlineStatus';

/**
 * Shows a subtle banner when the user is offline.
 * Auto-hides when connectivity is restored.
 * Important for mobile users who may lose signal while studying.
 */
export function OfflineIndicator() {
  const isOnline = useOnlineStatus();

  if (isOnline) return null;

  return (
    <div
      className="fixed top-0 left-0 right-0 z-50 flex items-center justify-center gap-2 
                 py-2 px-4 text-xs font-medium text-amber-200 bg-amber-900/90 backdrop-blur-sm
                 animate-in slide-in-from-top duration-300"
      role="alert"
      aria-live="polite"
    >
      <WifiOff className="w-3.5 h-3.5" />
      <span>网络已断开 — 学习记录将在恢复后同步</span>
    </div>
  );
}
