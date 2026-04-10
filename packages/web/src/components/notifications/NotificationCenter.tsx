/**
 * NotificationCenter — Bell icon with dropdown notification panel.
 * Shows unread badge, notification list, mark-read, and dismiss actions.
 * V2.11
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, Check, CheckCheck, X, Trophy, Flame, BookOpen, MessageCircle, FileText, Star, Target, Sparkles } from 'lucide-react';

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  link: string | null;
  read: boolean;
  created_at: number;
}

const TYPE_ICONS: Record<string, React.ReactNode> = {
  mastery: <Trophy size={16} style={{ color: '#22c55e' }} />,
  streak: <Flame size={16} style={{ color: '#ef4444' }} />,
  review_due: <BookOpen size={16} style={{ color: '#3b82f6' }} />,
  discussion_reply: <MessageCircle size={16} style={{ color: '#8b5cf6' }} />,
  content_feedback: <FileText size={16} style={{ color: '#f59e0b' }} />,
  weekly_report: <Star size={16} style={{ color: '#6366f1' }} />,
  milestone: <Target size={16} style={{ color: '#ec4899' }} />,
  recommendation: <Sparkles size={16} style={{ color: '#14b8a6' }} />,
};

function timeAgo(ts: number): string {
  const diff = Math.floor(Date.now() / 1000 - ts);
  if (diff < 60) return '刚刚';
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
  return `${Math.floor(diff / 86400)}天前`;
}

const API_BASE = import.meta.env.VITE_API_URL || '';

export function NotificationCenter() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const panelRef = useRef<HTMLDivElement>(null);

  const fetchNotifications = useCallback(async () => {
    try {
      const resp = await fetch(`${API_BASE}/api/notifications?limit=20`);
      if (!resp.ok) return;
      const data = await resp.json();
      setNotifications(data.notifications || []);
      setUnreadCount(data.unread_count || 0);
    } catch { /* API unavailable — graceful degradation */ }
  }, []);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 60_000);
    return () => clearInterval(interval);
  }, [fetchNotifications]);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    if (open) document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [open]);

  const markRead = async (id: string) => {
    await fetch(`${API_BASE}/api/notifications/${id}/read`, { method: 'POST' }).catch(() => {});
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
    setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const markAllRead = async () => {
    await fetch(`${API_BASE}/api/notifications/read-all`, { method: 'POST' }).catch(() => {});
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    setUnreadCount(0);
  };

  const dismiss = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    await fetch(`${API_BASE}/api/notifications/${id}`, { method: 'DELETE' }).catch(() => {});
    setNotifications(prev => prev.filter(n => n.id !== id));
    setUnreadCount(prev => {
      const was = notifications.find(n => n.id === id);
      return was && !was.read ? Math.max(0, prev - 1) : prev;
    });
  };

  const handleClick = (n: Notification) => {
    if (!n.read) markRead(n.id);
    if (n.link) {
      navigate(n.link);
      setOpen(false);
    }
  };

  return (
    <div className="relative" ref={panelRef}>
      <button
        onClick={() => setOpen(prev => !prev)}
        className="relative p-2 rounded-lg hover:bg-white/10 transition-colors"
        aria-label="Notifications"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center text-[10px] font-bold rounded-full px-1"
            style={{ backgroundColor: 'var(--color-status-danger)', color: 'var(--color-text-on-accent)' }}>
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 max-h-[70vh] rounded-xl shadow-2xl border overflow-hidden z-50 flex flex-col"
          style={{ backgroundColor: 'var(--color-surface-1)', borderColor: 'var(--color-border)' }}>
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b" style={{ borderColor: 'var(--color-border)' }}>
            <h3 className="text-sm font-semibold">通知</h3>
            {unreadCount > 0 && (
              <button onClick={markAllRead} className="text-xs flex items-center gap-1 px-2 py-1 rounded hover:bg-white/10 transition-colors" style={{ color: 'var(--color-accent)' }}>
                <CheckCheck size={14} /> 全部已读
              </button>
            )}
          </div>

          {/* List */}
          <div className="overflow-y-auto flex-1">
            {notifications.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 opacity-50">
                <Bell size={32} className="mb-2" />
                <span className="text-sm">暂无通知</span>
              </div>
            ) : (
              notifications.map(n => (
                <div
                  key={n.id}
                  onClick={() => handleClick(n)}
                  className="flex items-start gap-3 px-4 py-3 border-b cursor-pointer hover:bg-white/5 transition-colors"
                  style={{
                    borderColor: 'var(--color-border)',
                    opacity: n.read ? 0.6 : 1,
                    backgroundColor: n.read ? 'transparent' : 'rgba(59, 130, 246, 0.05)',
                  }}
                >
                  <div className="mt-0.5 shrink-0">{TYPE_ICONS[n.type] || <Bell size={16} />}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium truncate">{n.title}</span>
                      {!n.read && <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: 'var(--color-accent)' }} />}
                    </div>
                    <p className="text-xs mt-0.5 line-clamp-2" style={{ color: 'var(--color-text-secondary)' }}>{n.message}</p>
                    <span className="text-[10px] mt-1 block" style={{ color: 'var(--color-text-tertiary)' }}>{timeAgo(n.created_at)}</span>
                  </div>
                  <button
                    onClick={(e) => dismiss(n.id, e)}
                    className="shrink-0 p-1 rounded hover:bg-white/10 transition-colors opacity-0 group-hover:opacity-100"
                    style={{ opacity: 0.4 }}
                    aria-label="Dismiss"
                  >
                    <X size={14} />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
}
