import { useNavigate, useLocation } from 'react-router-dom';
import { useGraphStore } from '@/lib/store/graph';
import { useLearningStore } from '@/lib/store/learning';
import { Network, BarChart3, Settings, Brain, Sparkles, Zap } from 'lucide-react';

const NAV_ITEMS = [
  { path: '/graph', icon: Network, label: '知识图谱', desc: '探索知识宇宙' },
  { path: '/dashboard', icon: BarChart3, label: '学习进度', desc: '查看成长轨迹' },
  { path: '/settings', icon: Settings, label: '设置', desc: 'API 配置' },
] as const;

export function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const { graphData } = useGraphStore();
  const { progress } = useLearningStore();
  const totalNodes = graphData?.nodes.length || 0;
  const masteredCount = Object.values(progress).filter(p => p.status === 'mastered').length;
  const learningCount = Object.values(progress).filter(p => p.status === 'learning').length;
  const progressPct = totalNodes > 0 ? Math.round((masteredCount / totalNodes) * 100) : 0;

  return (
    <aside
      className="flex flex-col h-full shrink-0 border-r"
      style={{
        width: 'var(--sidebar-width)',
        backgroundColor: 'var(--color-surface-1)',
        borderColor: 'var(--color-border)',
      }}
    >
      {/* Logo */}
      <div className="px-6 py-7">
        <button
          onClick={() => navigate('/graph')}
          className="flex items-center gap-3 group"
        >
          <div
            className="flex items-center justify-center w-10 h-10 rounded-xl"
            style={{
              background: 'linear-gradient(135deg, var(--color-accent-indigo), var(--color-accent-violet))',
              boxShadow: '0 4px 16px rgba(99, 102, 241, 0.3)',
            }}
          >
            <Brain size={20} className="text-white" />
          </div>
          <div>
            <div className="text-sm font-bold tracking-tight" style={{ color: 'var(--color-text-primary)' }}>
              AI Knowledge
            </div>
            <div
              className="text-[11px] font-medium tracking-wider"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              知识图谱 v0.3
            </div>
          </div>
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 space-y-1">
        <div
          className="px-3 mb-3 text-[10px] font-semibold uppercase tracking-[0.15em]"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          导航
        </div>
        {NAV_ITEMS.map(({ path, icon: Icon, label, desc }) => {
          const isActive = location.pathname === path;
          return (
            <button
              key={path}
              onClick={() => navigate(path)}
              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 group"
              style={{
                backgroundColor: isActive ? 'var(--color-surface-3)' : 'transparent',
                color: isActive ? 'var(--color-text-primary)' : 'var(--color-text-secondary)',
              }}
            >
              <div
                className="flex items-center justify-center w-9 h-9 rounded-lg transition-all duration-200"
                style={{
                  backgroundColor: isActive
                    ? 'rgba(99, 102, 241, 0.15)'
                    : 'transparent',
                  color: isActive ? 'var(--color-accent-indigo)' : 'inherit',
                }}
              >
                <Icon size={18} />
              </div>
              <div className="text-left">
                <div className="text-[13px] font-semibold leading-tight">{label}</div>
                <div
                  className="text-[11px] leading-tight mt-0.5"
                  style={{ color: 'var(--color-text-tertiary)' }}
                >
                  {desc}
                </div>
              </div>
              {isActive && (
                <div
                  className="ml-auto w-1.5 h-6 rounded-full"
                  style={{
                    background: 'linear-gradient(180deg, var(--color-accent-indigo), var(--color-accent-violet))',
                  }}
                />
              )}
            </button>
          );
        })}
      </nav>

      {/* Bottom section — progress overview */}
      <div className="px-4 py-5 border-t" style={{ borderColor: 'var(--color-border)' }}>
        <div
          className="rounded-xl p-4"
          style={{
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.06))',
            border: '1px solid var(--color-border)',
          }}
        >
          {totalNodes > 0 && (masteredCount > 0 || learningCount > 0) ? (
            <>
              <div className="flex items-center justify-between mb-2">
                <span className="text-[12px] font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                  学习进度
                </span>
                <span className="text-[12px] font-mono font-bold" style={{ color: 'var(--color-accent-indigo)' }}>
                  {progressPct}%
                </span>
              </div>
              {/* Progress bar */}
              <div className="h-1.5 rounded-full overflow-hidden mb-2" style={{ backgroundColor: 'var(--color-surface-4)' }}>
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${progressPct}%`,
                    background: 'linear-gradient(90deg, var(--color-accent-indigo), var(--color-accent-emerald))',
                    minWidth: progressPct > 0 ? 4 : 0,
                  }}
                />
              </div>
              <div className="flex items-center gap-3 text-[11px]">
                <span className="flex items-center gap-1" style={{ color: 'var(--color-accent-emerald)' }}>
                  <Zap size={10} /> {masteredCount} 掌握
                </span>
                {learningCount > 0 && (
                  <span className="flex items-center gap-1" style={{ color: 'var(--color-accent-amber)' }}>
                    <Sparkles size={10} /> {learningCount} 学习中
                  </span>
                )}
                <span style={{ color: 'var(--color-text-tertiary)' }}>/ {totalNodes}</span>
              </div>
            </>
          ) : (
            <>
              <div className="flex items-center gap-2 mb-2">
                <Sparkles size={14} style={{ color: 'var(--color-accent-amber)' }} />
                <span className="text-[12px] font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                  交互式学习
                </span>
              </div>
              <p className="text-[11px] leading-relaxed" style={{ color: 'var(--color-text-tertiary)' }}>
                点击图谱节点，与 AI 对话来检验和深化你的理解。
              </p>
            </>
          )}
        </div>
      </div>
    </aside>
  );
}