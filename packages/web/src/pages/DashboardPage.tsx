import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useLearningStore, type LearningHistory } from '@/lib/store/learning';
import { useGraphStore } from '@/lib/store/graph';

/**
 * 学习进度面板 — 展示真实学习数据
 */
export function DashboardPage() {
  const { stats, progress, history, streak, computeStats, refreshStreak } = useLearningStore();
  const { graphData } = useGraphStore();
  const navigate = useNavigate();

  useEffect(() => {
    refreshStreak();
    if (graphData) {
      computeStats(graphData.nodes.length);
    }
  }, [graphData]);

  const recentHistory = [...history].reverse().slice(0, 10);
  const masteredNodes = Object.values(progress).filter(p => p.status === 'mastered');
  const learningNodes = Object.values(progress).filter(p => p.status === 'learning');

  // 学习进度百分比
  const totalNodes = stats?.total_concepts || 0;
  const progressPct = totalNodes > 0 ? Math.round((masteredNodes.length / totalNodes) * 100) : 0;

  return (
    <div className="min-h-dvh" style={{ backgroundColor: '#0f172a' }}>
      {/* Header */}
      <header
        className="flex items-center px-4"
        style={{
          height: '48px',
          paddingTop: 'var(--safe-area-top)',
          backgroundColor: '#1e293b',
          borderBottom: '1px solid #334155',
        }}
      >
        <h1 className="text-base font-bold" style={{ color: '#f1f5f9' }}>
          📊 学习进度
        </h1>
      </header>

      <div className="px-4 py-6 space-y-5">
        {/* 统计卡片 */}
        <div className="grid grid-cols-2 gap-3">
          {[
            { label: '已掌握', value: masteredNodes.length, icon: '⭐', color: '#10b981' },
            { label: '学习中', value: learningNodes.length, icon: '📖', color: '#f59e0b' },
            { label: '未开始', value: stats?.not_started_count ?? totalNodes, icon: '🔵', color: '#94a3b8' },
            { label: '总节点', value: totalNodes, icon: '🌐', color: '#8b5cf6' },
          ].map(({ label, value, icon, color }) => (
            <div
              key={label}
              className="rounded-xl p-4"
              style={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
            >
              <div className="text-2xl mb-1">{icon}</div>
              <div className="text-2xl font-bold" style={{ color }}>{value}</div>
              <div className="text-xs" style={{ color: '#94a3b8' }}>{label}</div>
            </div>
          ))}
        </div>

        {/* 总体进度条 */}
        <div className="rounded-xl p-4" style={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium" style={{ color: '#f1f5f9' }}>总体进度</span>
            <span className="text-sm font-bold" style={{ color: '#8b5cf6' }}>{progressPct}%</span>
          </div>
          <div className="h-3 rounded-full" style={{ backgroundColor: '#334155' }}>
            <div
              className="h-full rounded-full transition-all duration-500"
              style={{ width: `${progressPct}%`, backgroundColor: '#8b5cf6', minWidth: progressPct > 0 ? 8 : 0 }}
            />
          </div>
          <div className="flex justify-between mt-1.5 text-[10px]" style={{ color: '#64748b' }}>
            <span>{masteredNodes.length} 已掌握</span>
            <span>{totalNodes} 总计</span>
          </div>
        </div>

        {/* 连续学习 + 最高纪录 */}
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-xl p-4" style={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-[11px]" style={{ color: '#94a3b8' }}>连续学习</div>
                <div className="text-2xl font-bold" style={{ color: '#f59e0b' }}>
                  {streak.current} <span className="text-sm font-normal">天</span>
                </div>
              </div>
              <div className="text-3xl">🔥</div>
            </div>
          </div>
          <div className="rounded-xl p-4" style={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-[11px]" style={{ color: '#94a3b8' }}>最高纪录</div>
                <div className="text-2xl font-bold" style={{ color: '#8b5cf6' }}>
                  {streak.longest} <span className="text-sm font-normal">天</span>
                </div>
              </div>
              <div className="text-3xl">🏆</div>
            </div>
          </div>
        </div>

        {/* 最近学习记录 */}
        <div className="rounded-xl p-4" style={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}>
          <h2 className="text-sm font-semibold mb-3" style={{ color: '#f1f5f9' }}>
            📋 最近学习
          </h2>
          {recentHistory.length === 0 ? (
            <div className="text-center py-6">
              <div className="text-4xl mb-2">🧠</div>
              <p className="text-xs" style={{ color: '#64748b' }}>
                还没有学习记录，去图谱选一个概念开始吧！
              </p>
              <button
                onClick={() => navigate('/graph')}
                className="mt-3 rounded-lg px-4 py-2 text-xs font-medium"
                style={{ backgroundColor: '#8b5cf6', color: '#fff' }}
              >
                前往图谱
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              {recentHistory.map((item, i) => (
                <HistoryItem key={`${item.concept_id}-${item.timestamp}-${i}`} item={item} />
              ))}
            </div>
          )}
        </div>

        {/* 已掌握概念列表 */}
        {masteredNodes.length > 0 && (
          <div className="rounded-xl p-4" style={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}>
            <h2 className="text-sm font-semibold mb-3" style={{ color: '#f1f5f9' }}>
              🏅 已掌握概念 ({masteredNodes.length})
            </h2>
            <div className="flex flex-wrap gap-2">
              {masteredNodes.map((p) => (
                <button
                  key={p.concept_id}
                  onClick={() => navigate(`/learn/${p.concept_id}`)}
                  className="rounded-full px-2.5 py-1 text-[11px] font-medium"
                  style={{ backgroundColor: '#10b98120', color: '#10b981', border: '1px solid #10b98140' }}
                >
                  ✓ {p.concept_id.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="text-center text-[10px] py-2" style={{ color: '#475569' }}>
          AI Knowledge Graph v0.3.0 · 数据存储在本地浏览器
        </div>
      </div>
    </div>
  );
}

/** 学习历史条目 */
function HistoryItem({ item }: { item: LearningHistory }) {
  const time = new Date(item.timestamp);
  const timeStr = `${time.getMonth() + 1}/${time.getDate()} ${time.getHours().toString().padStart(2, '0')}:${time.getMinutes().toString().padStart(2, '0')}`;
  const scoreColor = item.score >= 80 ? '#10b981' : item.score >= 60 ? '#f59e0b' : '#ef4444';

  return (
    <div
      className="flex items-center gap-3 rounded-lg px-3 py-2"
      style={{ backgroundColor: '#0f172a' }}
    >
      <span className="text-base">{item.mastered ? '⭐' : '📝'}</span>
      <div className="flex-1 min-w-0">
        <div className="text-xs font-medium truncate" style={{ color: '#e2e8f0' }}>
          {item.concept_name}
        </div>
        <div className="text-[10px]" style={{ color: '#64748b' }}>{timeStr}</div>
      </div>
      <div className="text-sm font-bold" style={{ color: scoreColor }}>
        {item.score}
      </div>
    </div>
  );
}
