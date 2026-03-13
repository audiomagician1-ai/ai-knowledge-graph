import { useParams } from 'react-router-dom';

/**
 * 费曼学习对话页面
 * TODO: Phase 2 实现费曼对话引擎
 */
export function LearnPage() {
  const { conceptId } = useParams<{ conceptId: string }>();

  return (
    <div className="flex h-dvh flex-col" style={{ backgroundColor: 'var(--bg-primary)' }}>
      {/* 顶部栏 */}
      <header
        className="flex items-center gap-3 px-4"
        style={{
          height: 'var(--header-height)',
          paddingTop: 'var(--safe-area-top)',
          backgroundColor: 'var(--bg-secondary)',
          borderBottom: '1px solid var(--border-default)',
        }}
      >
        <button
          onClick={() => history.back()}
          className="flex items-center justify-center rounded-lg"
          style={{ width: 36, height: 36, color: 'var(--text-primary)' }}
        >
          ←
        </button>
        <h1 className="text-base font-semibold flex-1 truncate" style={{ color: 'var(--text-primary)' }}>
          费曼学习: {conceptId}
        </h1>
      </header>

      {/* 对话区域 */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        <div className="text-center py-12">
          <div className="text-5xl mb-4">🎓</div>
          <h2 className="text-lg font-bold mb-2" style={{ color: 'var(--text-primary)' }}>
            准备好了吗？
          </h2>
          <p className="mb-6" style={{ color: 'var(--text-secondary)' }}>
            试着用最简单的话向AI解释这个概念
          </p>
          <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
            费曼对话引擎将在 Phase 2 中实现
          </p>
        </div>
      </div>

      {/* 输入区域 */}
      <div
        className="flex items-center gap-2 px-4 py-3"
        style={{
          backgroundColor: 'var(--bg-secondary)',
          borderTop: '1px solid var(--border-default)',
          paddingBottom: 'calc(var(--safe-area-bottom) + 12px)',
        }}
      >
        <input
          type="text"
          placeholder="用你自己的话解释这个概念..."
          className="flex-1 rounded-xl px-4 py-3 text-sm outline-none"
          style={{
            backgroundColor: 'var(--bg-tertiary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-default)',
          }}
          disabled
        />
        <button
          className="rounded-xl px-4 py-3 text-sm font-medium"
          style={{ backgroundColor: 'var(--color-primary)', color: '#fff' }}
          disabled
        >
          发送
        </button>
      </div>
    </div>
  );
}
