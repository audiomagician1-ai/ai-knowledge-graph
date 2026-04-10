import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Map, Trophy, Star, TrendingUp, Flame, BookOpen } from 'lucide-react';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';

interface JourneyEvent {
  type: 'mastered' | 'milestone' | 'domain_milestone';
  concept_id?: string;
  concept_name?: string;
  domain_id: string;
  domain_name: string;
  score?: number;
  timestamp: number;
  badge?: string;
  percentage?: number;
  mastered_count?: number;
  total_concepts?: number;
}

interface DomainSummary {
  domain_id: string;
  domain_name: string;
  icon: string;
  color: string;
  mastered: number;
  total: number;
  percentage: number;
}

interface JourneyData {
  events: JourneyEvent[];
  total_events: number;
  domain_summary: DomainSummary[];
  stats: {
    total_mastered: number;
    domains_started: number;
    domains_completed: number;
    current_streak: number;
  };
}

const EVENT_ICONS: Record<string, typeof Trophy> = {
  mastered: BookOpen,
  milestone: Trophy,
  domain_milestone: Star,
};

function formatDate(ts: number): string {
  if (!ts) return '';
  const d = new Date(ts * 1000);
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

export function LearningJourneyPage() {
  const navigate = useNavigate();
  const [data, setData] = useState<JourneyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useKeyboardShortcuts([
    { key: 'Escape', handler: () => navigate('/'), description: 'Back' },
  ]);

  useEffect(() => {
    const base = (import.meta as Record<string, any>).env?.VITE_API_URL || '';
    fetch(`${base}/api/analytics/learning-journey`)
      .then(r => r.json())
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="min-h-dvh flex items-center justify-center" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--color-accent)' }} />
    </div>
  );

  if (!data) return (
    <div className="min-h-dvh flex flex-col items-center justify-center gap-4" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      <Map size={48} className="opacity-30" />
      <p className="opacity-50">暂无学习旅程数据</p>
      <button onClick={() => navigate('/')} className="px-4 py-2 rounded-lg" style={{ backgroundColor: 'var(--color-accent)' }}>开始学习</button>
    </div>
  );

  const filteredEvents = filter === 'all' ? data.events : data.events.filter(e => e.type === filter);

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      <header className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <button onClick={() => navigate(-1)} className="p-2 rounded-lg hover:bg-white/10 transition-colors"><ArrowLeft size={20} /></button>
        <Map size={24} style={{ color: 'var(--color-accent)' }} />
        <h1 className="text-xl font-bold">学习旅程</h1>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">
        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { icon: <BookOpen size={18} />, label: '已掌握', value: data.stats.total_mastered, color: '#22c55e' },
            { icon: <TrendingUp size={18} />, label: '已探索域', value: data.stats.domains_started, color: '#3b82f6' },
            { icon: <Star size={18} />, label: '已完成域', value: data.stats.domains_completed, color: '#f59e0b' },
            { icon: <Flame size={18} />, label: '连续学习', value: `${data.stats.current_streak}天`, color: '#ef4444' },
          ].map((s, i) => (
            <div key={i} className="rounded-lg p-3 text-center" style={{ backgroundColor: 'var(--color-surface-1)' }}>
              <div className="flex items-center justify-center gap-2 mb-1" style={{ color: s.color }}>{s.icon}<span className="text-xl font-bold">{s.value}</span></div>
              <span className="text-xs opacity-50">{s.label}</span>
            </div>
          ))}
        </div>

        {/* Domain Progress Grid */}
        {data.domain_summary.length > 0 && (
          <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
            <h2 className="text-base font-semibold mb-3">领域掌握度</h2>
            <div className="space-y-2">
              {data.domain_summary.filter(d => d.mastered > 0).slice(0, 12).map((d) => (
                <button key={d.domain_id} onClick={() => navigate(`/domain/${d.domain_id}`)}
                  className="w-full flex items-center gap-3 rounded-lg px-3 py-2 hover:bg-white/5 transition-colors text-left">
                  <span className="text-lg shrink-0">{d.icon}</span>
                  <span className="text-sm truncate flex-1">{d.domain_name}</span>
                  <span className="text-xs opacity-50">{d.mastered}/{d.total}</span>
                  <div className="w-20 h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: 'var(--color-surface-2)' }}>
                    <div className="h-full rounded-full transition-all" style={{ width: `${d.percentage}%`, backgroundColor: d.color }} />
                  </div>
                  <span className="text-xs font-mono w-10 text-right" style={{ color: d.color }}>{d.percentage}%</span>
                </button>
              ))}
            </div>
          </section>
        )}

        {/* Event Timeline */}
        <section className="rounded-xl p-5" style={{ backgroundColor: 'var(--color-surface-1)' }}>
          <div className="flex items-center gap-2 mb-4">
            <h2 className="text-base font-semibold">学习时间线</h2>
            <span className="text-xs opacity-40">{data.total_events} 个事件</span>
          </div>

          {/* Filter tabs */}
          <div className="flex gap-2 mb-4 flex-wrap">
            {[
              { key: 'all', label: '全部' },
              { key: 'mastered', label: '掌握' },
              { key: 'milestone', label: '里程碑' },
              { key: 'domain_milestone', label: '域成就' },
            ].map(f => (
              <button key={f.key} onClick={() => setFilter(f.key)}
                className="px-3 py-1 rounded-full text-xs transition-all"
                style={{
                  backgroundColor: filter === f.key ? 'var(--color-accent)' : 'var(--color-surface-2)',
                  color: filter === f.key ? 'var(--color-text-on-accent)' : 'inherit',
                  opacity: filter === f.key ? 1 : 0.6,
                }}>
                {f.label}
              </button>
            ))}
          </div>

          {/* Timeline */}
          <div className="space-y-1 max-h-[600px] overflow-y-auto pr-1">
            {filteredEvents.length === 0 && (
              <p className="text-sm opacity-40 text-center py-8">暂无事件</p>
            )}
            {filteredEvents.slice(0, 100).map((event, i) => {
              const Icon = EVENT_ICONS[event.type] || BookOpen;
              const isSpecial = event.type !== 'mastered';
              return (
                <div key={i} className="flex items-start gap-3 rounded-lg px-3 py-2 transition-colors hover:bg-white/5"
                  style={isSpecial ? { backgroundColor: 'var(--color-surface-2)' } : {}}>
                  <div className="mt-0.5 shrink-0 flex items-center justify-center w-6 h-6 rounded-full"
                    style={{ backgroundColor: isSpecial ? '#f59e0b20' : 'var(--color-surface-2)' }}>
                    {event.badge ? <span className="text-sm">{event.badge}</span> : <Icon size={12} style={{ color: isSpecial ? '#f59e0b' : 'var(--color-accent)' }} />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm truncate">
                      {event.type === 'domain_milestone'
                        ? `${event.domain_name} 达成 ${event.percentage}% (${event.mastered_count}/${event.total_concepts})`
                        : `掌握 ${event.concept_name}`}
                    </p>
                    <p className="text-xs opacity-40">{event.domain_name} · {formatDate(event.timestamp)}</p>
                  </div>
                  {event.score && <span className="text-xs font-mono opacity-50 shrink-0">{event.score}分</span>}
                </div>
              );
            })}
          </div>
        </section>
      </div>
    </div>
  );
}