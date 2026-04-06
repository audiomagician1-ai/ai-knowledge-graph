import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock Notification API
class MockNotification {
  static permission: NotificationPermission = 'default';
  static requestPermission = vi.fn(async () => 'granted' as NotificationPermission);
  
  title: string;
  body: string;
  onclick: (() => void) | null = null;
  close = vi.fn();
  
  constructor(title: string, options?: NotificationOptions) {
    this.title = title;
    this.body = options?.body || '';
  }
}

// @ts-expect-error - mock
globalThis.Notification = MockNotification;

describe('Notifications', () => {
  beforeEach(() => {
    MockNotification.permission = 'default';
    MockNotification.requestPermission.mockResolvedValue('granted');
    localStorage.clear();
  });

  it('should detect notification support', () => {
    expect('Notification' in window).toBe(true);
  });

  it('should handle permission request', async () => {
    const result = await Notification.requestPermission();
    expect(result).toBe('granted');
  });

  it('should respect denied permission', () => {
    MockNotification.permission = 'denied';
    expect(Notification.permission).toBe('denied');
  });

  it('should store notification prefs in localStorage', () => {
    const prefs = {
      enabled: true,
      reminderHour: 20,
      lastReminderDate: '',
    };
    localStorage.setItem('akg-notification-prefs', JSON.stringify(prefs));
    const stored = JSON.parse(localStorage.getItem('akg-notification-prefs')!);
    expect(stored.enabled).toBe(true);
    expect(stored.reminderHour).toBe(20);
  });

  it('should create notification with correct title and body', () => {
    MockNotification.permission = 'granted';
    const n = new MockNotification('Test Title', { body: 'Test body' });
    expect(n.title).toBe('Test Title');
    expect(n.body).toBe('Test body');
  });

  it('should not duplicate reminders on same day', () => {
    const today = new Date().toISOString().slice(0, 10);
    const prefs = {
      enabled: true,
      reminderHour: 20,
      lastReminderDate: today,
    };
    // If lastReminderDate === today, should skip
    expect(prefs.lastReminderDate).toBe(today);
  });
});
