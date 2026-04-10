/**
 * NotificationsPage — Full-page notification center.
 * Shows all notifications with read/dismiss actions and type filtering.
 * V2.11
 */

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Bell, Check, CheckCheck, Trash2, Trophy, Flame, BookOpen, MessageCircle, FileText, Star, Target, Sparkles, Filter } from 'lucide-react';

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
  mastery: <Trophy size={18} style={{ color: '#22c55e' }} />,
  streak: <Flame size={18} style={{ color: '#ef4444' }} />,
  review_due: <BookOpen size={18} style={{ color: '#3b82f6' }} />,
  discussion_reply: <MessageCircle size={18} style={{ color: '#8b5cf6' }} />,
  content_feedback: <FileText size={18} style={{ color: '#f59e0b' }} />,
  weekly_report: <Star size={18} style={{ color: '#6366f1' }} />,
  milestone: <Target size={18} style={{ color: '#ec4899' }} />,
  recommendation: <Sparkles size={18} style={{ color: '#14b8a6' }} />,
};

const TYPE_LABELS: Record<string, string> = {
  mastery: '掌握', streak: '连续', review_due: '复习', discussion_reply: '讨论',
  content_feedback: '反馈', weekly_report: '周报', milestone: '里程碑', recommendation: '推荐',
};

function timeAgo(ts: number): string {
  const diff = Math.floor(Date.now() / 1000 - ts);
  if (diff < 60) return '刚刚';
  if (diff < 3600) return `${Math.floor(diff / 60)}分钟前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}小时前`;
  return `${Math.floor(diff / 86400)}天前`;
}

const API_BASE = import.meta.env.VITE_API_URL || '';

export function NotificationsPage() {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [filter, setFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);

  const fetchData = useCallback(async () => {
    try {
      const url = filter
        ? `${API_BASE}/api/notifications?type=${filter}&limit=50`
        : `${API_BASE}/api/notifications?limit=50`;
      const resp = await fetch(url);
      if (!resp.ok) return;
      const data = await resp.json();
      setNotifications(data.notifications || []);
      setUnreadCount(data.unread_count || 0);
    } catch { /* graceful */ }
    setLoading(false);
  }, [filter]);

  useEffect(() => { fetchData(); }, [fetchData]);

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

  const dismiss = async (id: string) => {
    const was = notifications.find(n => n.id === id);
    await fetch(`${API_BASE}/api/notifications/${id}`, { method: 'DELETE' }).catch(() => {});
    setNotifications(prev => prev.filter(n => n.id !== id));
    if (was && !was.read) setUnreadCount(prev => Math.max(0, prev - 1));
  };

  const handleClick = (n: Notification) => {
    if (!n.read) markRead(n.id);
    if (n.link) navigate(n.link);
  };

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      <header className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors"><ArrowLeft size={20} /></button>
        <Bell size={24} style={{ color: 'var(--color-accent)' }} />
        <h1 className="text-xl font-bold">通知中心</h1>
        {unreadCount > 0 && (
          <span className="ml-2 px-2 py-0.5 text-xs font-bold rounded-full" style={{ backgroundColor: 'var(--color-status-danger)', color: 'var(--color-text-on-accent)' }}>
            {unreadCount} 未读
          </span>
        )}
        <div className="flex-1" />
        {unreadCount > 0 && (
          <button onClick={markAllRead} className="flex items-center gap-1 text-sm px-3 py-1.5 rounded-lg hover:bg-white/10 transition-colors" style={{ color: 'var(--color-accent)' }}>
            <CheckCheck size={16} /> 全部已读
          </button>
        )}
      </header>

      <div className="max-w-3xl mx-auto px-4 py-6">
        {/* Filter bar */}
        <div className="flex items-center gap-2 mb-4 overflow-x-auto pb-2">
          <Filter size={14} style={{ color: 'var(--color-text-tertiary)' }} />
          <button
            onClick={() => setFilter('')}
            className="text-xs px-3 py-1 rounded-full border transition-colors shrink-0"
            style={{
              borderColor: !filter ? 'var(--color-accent)' : 'var(--color-border)',
              backgroundColor: !filter ? 'rgba(59,130,246,0.1)' : 'transparent',
              color: !filter ? 'var(--color-accent)' : 'var(--color-text-secondary)',
            }}
          >
            全部
          </button>
          {Object.entries(TYPE_LABELS).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setFilter(key)}
              className="text-xs px-3 py-1 rounded-full border transition-colors shrink-0"
              style={{
                borderColor: filter === key ? 'var(--color-accent)' : 'var(--color-border)',
                backgroundColor: filter === key ? 'rgba(59,130,246,0.1)' : 'transparent',
                color: filter === key ? 'var(--color-accent)' : 'var(--color-text-secondary)',
              }}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Notification list */}
        {loading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => <div key={i} className="h-20 rounded-xl animate-pulse" style={{ backgroundColor: 'var(--color-surface-1)' }} />)}
          </div>
        ) : notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 opacity-50">
            <Bell size={48} className="mb-4" />
            <span className="text-lg">暂无通知</span>
            <span className="text-sm mt-1">学习过程中的重要提醒会出现在这里</span>
          </div>
        ) : (
          <div className="space-y-2">
            {notifications.map(n => (
              <div
                key={n.id}
                className="flex items-start gap-3 px-4 py-3 rounded-xl cursor-pointer hover:bg-white/5 transition-colors border"
                style={{
                  borderColor: 'var(--color-border)',
                  opacity: n.read ? 0.6 : 1,
                  backgroundColor: n.read ? 'var(--color-surface-1)' : 'rgba(59,130,246,0.05)',
                }}
                onClick={() => handleClick(n)}
              >
                <div className="mt-0.5 shrink-0">{TYPE_ICONS[n.type] || <Bell size={18} />}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">{n.title}</span>
                    {!n.read && <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: 'var(--color-accent)' }} />}
                  </div>
                  <p className="text-xs mt-1" style={{ color: 'var(--color-text-secondary)' }}>{n.message}</p>
                  <span className="text-[10px] mt-1 block" style={{ color: 'var(--color-text-tertiary)' }}>{timeAgo(n.created_at)}</span>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                  {!n.read && (
                    <button onClick={e => { e.stopPropagation(); markRead(n.id); }} className="p-1.5 rounded-lg hover:bg-white/10" title="标为已读">
                      <Check size={14} />
                    </button>
                  )}
                  <button onClick={e => { e.stopPropagation(); dismiss(n.id); }} className="p-1.5 rounded-lg hover:bg-white/10 opacity-40 hover:opacity-100" title="删除">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
