/**
 * Notification hook — request permission and show notifications.
 * 
 * Used for:
 * - Study goal reminders
 * - Review due alerts
 * - Achievement unlocks
 */
import { useCallback, useEffect, useRef } from 'react';
import { useLocalStorage } from './useLocalStorage';
import { createLogger } from '@/lib/utils/logger';

const log = createLogger('Notifications');

export type NotificationPermission = 'default' | 'granted' | 'denied';

interface NotificationPrefs {
  /** User explicitly enabled/disabled notifications */
  enabled: boolean;
  /** Daily reminder hour (0-23, default 20 = 8pm) */
  reminderHour: number;
  /** Last reminder date (YYYY-MM-DD) to avoid duplicates */
  lastReminderDate: string;
}

const DEFAULT_PREFS: NotificationPrefs = {
  enabled: false,
  reminderHour: 20,
  lastReminderDate: '',
};

/**
 * Check if the Notification API is available (not available in SSR/workers)
 */
function isNotificationSupported(): boolean {
  return typeof window !== 'undefined' && 'Notification' in window;
}

export function useNotifications() {
  const [prefs, setPrefs] = useLocalStorage<NotificationPrefs>(
    'akg-notification-prefs',
    DEFAULT_PREFS
  );
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  /** Current browser permission state */
  const permission: NotificationPermission = isNotificationSupported()
    ? (Notification.permission as NotificationPermission)
    : 'denied';

  /** Request notification permission from user */
  const requestPermission = useCallback(async (): Promise<boolean> => {
    if (!isNotificationSupported()) return false;
    try {
      const result = await Notification.requestPermission();
      if (result === 'granted') {
        setPrefs((p) => ({ ...p, enabled: true }));
        log.info('Notification permission granted');
        return true;
      }
      log.info(`Notification permission: ${result}`);
      return false;
    } catch (e) {
      log.warn(`Permission request failed: ${e}`);
      return false;
    }
  }, [setPrefs]);

  /** Show a notification (fires-and-forgets, non-blocking) */
  const showNotification = useCallback(
    (title: string, body: string, options?: { icon?: string; tag?: string; onClick?: () => void }) => {
      if (!isNotificationSupported() || Notification.permission !== 'granted') return;
      try {
        const n = new Notification(title, {
          body,
          icon: options?.icon || '/icon-192.png',
          tag: options?.tag || 'akg-notification',
          badge: '/icon-192.png',
        });
        if (options?.onClick) {
          n.onclick = () => {
            window.focus();
            options.onClick?.();
            n.close();
          };
        }
        // Auto-close after 8 seconds
        setTimeout(() => n.close(), 8000);
      } catch (e) {
        log.warn(`Show notification failed: ${e}`);
      }
    },
    []
  );

  /** Toggle notification preference */
  const toggleEnabled = useCallback(
    async (enabled: boolean) => {
      if (enabled && Notification.permission === 'default') {
        const granted = await requestPermission();
        if (!granted) return;
      }
      setPrefs((p) => ({ ...p, enabled }));
    },
    [requestPermission, setPrefs]
  );

  /** Update reminder hour */
  const setReminderHour = useCallback(
    (hour: number) => {
      setPrefs((p) => ({ ...p, reminderHour: Math.max(0, Math.min(23, hour)) }));
    },
    [setPrefs]
  );

  /** Check and trigger daily reminder if needed */
  const checkDailyReminder = useCallback(
    (goalMet: boolean, conceptsDone: number, conceptTarget: number) => {
      if (!prefs.enabled || Notification.permission !== 'granted') return;

      const now = new Date();
      const todayStr = now.toISOString().slice(0, 10);
      const currentHour = now.getHours();

      // Already reminded today
      if (prefs.lastReminderDate === todayStr) return;
      // Not yet reminder hour
      if (currentHour < prefs.reminderHour) return;

      // Mark as reminded
      setPrefs((p) => ({ ...p, lastReminderDate: todayStr }));

      if (goalMet) {
        showNotification(
          '🎉 今日目标达成！',
          `你已经学习了 ${conceptsDone} 个概念，继续保持！`,
          { tag: 'akg-daily-goal' }
        );
      } else {
        const remaining = Math.max(0, conceptTarget - conceptsDone);
        showNotification(
          '📚 学习提醒',
          `今日还需学习 ${remaining} 个概念达到目标，加油！`,
          { tag: 'akg-daily-reminder' }
        );
      }
    },
    [prefs.enabled, prefs.lastReminderDate, prefs.reminderHour, setPrefs, showNotification]
  );

  // Set up hourly check for daily reminders
  useEffect(() => {
    if (!prefs.enabled || !isNotificationSupported()) return;
    // Check every 30 minutes
    intervalRef.current = setInterval(() => {
      // The actual check logic requires goal data — caller should invoke checkDailyReminder
    }, 30 * 60 * 1000);
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [prefs.enabled]);

  return {
    permission,
    isSupported: isNotificationSupported(),
    prefs,
    requestPermission,
    showNotification,
    toggleEnabled,
    setReminderHour,
    checkDailyReminder,
  };
}
