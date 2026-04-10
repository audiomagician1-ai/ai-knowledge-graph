/**
 * DashboardCustomizer — Settings panel for toggling & reordering Dashboard widget sections.
 * V4.0: User-configurable Dashboard layout persisted to localStorage.
 */
import { Eye, EyeOff, ArrowUp, ArrowDown, RotateCcw, Settings2 } from 'lucide-react';
import { useState } from 'react';
import { useDashboardPrefs, type SectionPref } from '@/hooks/useDashboardPrefs';

const SECTION_LABELS: Record<string, string> = {
  learning: '学习与复习',
  analytics: '数据分析',
  domains: '领域与图谱',
  social: '社交互动',
  content: '内容与发现',
};

export function DashboardCustomizer() {
  const { sections, toggleSection, moveSection, resetToDefaults } = useDashboardPrefs();
  const [open, setOpen] = useState(false);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs opacity-50 hover:opacity-80 transition-opacity border border-white/10 hover:border-white/20"
        title="自定义 Dashboard 布局"
      >
        <Settings2 size={13} />
        <span>自定义</span>
      </button>
    );
  }

  return (
    <div className="border border-white/10 rounded-xl p-4 bg-white/5 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold opacity-70">Dashboard 布局设置</h3>
        <div className="flex items-center gap-2">
          <button onClick={resetToDefaults} className="text-xs opacity-40 hover:opacity-70 flex items-center gap-1" title="恢复默认">
            <RotateCcw size={12} /> 重置
          </button>
          <button onClick={() => setOpen(false)} className="text-xs opacity-40 hover:opacity-70">关闭</button>
        </div>
      </div>
      <div className="space-y-1">
        {sections.map((sec: SectionPref, idx: number) => (
          <div key={sec.id} className="flex items-center gap-2 py-1.5 px-2 rounded-lg hover:bg-white/5 transition-colors">
            <button onClick={() => toggleSection(sec.id)} className="opacity-60 hover:opacity-100" title={sec.visible ? '隐藏' : '显示'}>
              {sec.visible ? <Eye size={14} /> : <EyeOff size={14} className="text-red-400" />}
            </button>
            <span className={`text-sm flex-1 ${sec.visible ? '' : 'line-through opacity-40'}`}>
              {SECTION_LABELS[sec.id] || sec.id}
            </span>
            <button
              onClick={() => moveSection(sec.id, 'up')}
              disabled={idx === 0}
              className="opacity-30 hover:opacity-70 disabled:opacity-10"
              title="上移"
            >
              <ArrowUp size={13} />
            </button>
            <button
              onClick={() => moveSection(sec.id, 'down')}
              disabled={idx === sections.length - 1}
              className="opacity-30 hover:opacity-70 disabled:opacity-10"
              title="下移"
            >
              <ArrowDown size={13} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
