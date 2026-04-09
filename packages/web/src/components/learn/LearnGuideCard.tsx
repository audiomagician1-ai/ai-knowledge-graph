import { Lightbulb, Brain } from 'lucide-react';

export function LearnGuideCard() {
  return (
    <div className="gradient-border animate-fade-in" style={{ padding: 0 }}>
      <div
        className="rounded-lg px-6 py-5 flex items-start gap-4"
        style={{ backgroundColor: 'var(--color-surface-2)' }}
      >
        <div
          className="w-9 h-9 rounded-md flex items-center justify-center shrink-0"
          style={{ backgroundColor: 'var(--color-accent-primary)' }}
        >
          <Lightbulb size={16} style={{ color: '#ffffff' }} />
        </div>
        <div>
          <h3 className="text-sm font-bold mb-1" style={{ color: 'var(--color-text-primary)' }}>
            探索式学习
          </h3>
          <p className="text-[13px] leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
            AI 会先讲解概念，然后提供选项引导你深入。你可以点选选项或自由输入来互动。
          </p>
        </div>
      </div>
    </div>
  );
}

export function LearnLoadingIndicator() {
  return (
    <div className="flex justify-start animate-fade-in">
      <div
        className="w-7 h-7 rounded-md flex items-center justify-center shrink-0 mr-3 mt-1"
        style={{ backgroundColor: 'var(--color-surface-3)' }}
      >
        <Brain size={13} style={{ color: 'var(--color-text-secondary)' }} />
      </div>
      <div
        style={{
          borderRadius: '16px 16px 16px 4px',
          padding: '20px 24px',
          backgroundColor: '#ffffff',
          color: 'var(--color-text-primary)',
          border: '1px solid rgba(0, 0, 0, 0.1)',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.08)',
        }}
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'var(--color-accent-primary)', animationDelay: '0ms', animationDuration: '1.2s' }} />
            <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'var(--color-accent-primary)', animationDelay: '150ms', animationDuration: '1.2s' }} />
            <span className="w-1.5 h-1.5 rounded-full animate-bounce" style={{ backgroundColor: 'var(--color-accent-primary)', animationDelay: '300ms', animationDuration: '1.2s' }} />
          </div>
          <span className="text-[13px]" style={{ color: 'var(--color-text-tertiary)' }}>
            正在准备学习内容…
          </span>
        </div>
      </div>
    </div>
  );
}
