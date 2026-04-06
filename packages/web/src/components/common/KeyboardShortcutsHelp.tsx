import { useState, useEffect } from 'react';
import { Keyboard, X } from 'lucide-react';

interface ShortcutItem {
  keys: string[];
  description: string;
}

const GLOBAL_SHORTCUTS: ShortcutItem[] = [
  { keys: ['D'], description: '打开学习仪表盘' },
  { keys: ['G'], description: '打开 3D 知识图谱' },
  { keys: ['S'], description: '打开设置' },
  { keys: ['H'], description: '返回首页' },
  { keys: ['Esc'], description: '返回上一页' },
  { keys: ['Shift', '?'], description: '显示此帮助' },
];

/**
 * Keyboard shortcuts help overlay — triggered by Shift+? on any page.
 * Renders as a bottom sheet on mobile, centered modal on desktop.
 */
export function KeyboardShortcutsHelp() {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA') return;
      if (e.key === '?' && e.shiftKey) {
        e.preventDefault();
        setOpen(prev => !prev);
      }
      if (e.key === 'Escape' && open) {
        e.preventDefault();
        setOpen(false);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={() => setOpen(false)}
      role="dialog"
      aria-label="键盘快捷键"
    >
      <div
        className="bg-[#1e293b] rounded-xl border border-white/10 shadow-2xl w-[90vw] max-w-md mx-4 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <Keyboard className="w-5 h-5 text-blue-400" />
            <h2 className="text-base font-semibold text-white">键盘快捷键</h2>
          </div>
          <button
            onClick={() => setOpen(false)}
            className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
            aria-label="关闭"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Shortcuts list */}
        <div className="px-5 py-4 space-y-3">
          {GLOBAL_SHORTCUTS.map((item, i) => (
            <div key={i} className="flex items-center justify-between">
              <span className="text-sm text-gray-300">{item.description}</span>
              <div className="flex items-center gap-1">
                {item.keys.map((key, j) => (
                  <kbd
                    key={j}
                    className="min-w-[28px] h-7 px-2 flex items-center justify-center text-xs font-mono font-medium text-gray-200 bg-white/10 border border-white/20 rounded-md shadow-sm"
                  >
                    {key}
                  </kbd>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-5 py-3 border-t border-white/10 text-center">
          <p className="text-xs text-gray-500">按 <kbd className="px-1 py-0.5 bg-white/10 rounded text-gray-400 font-mono">Esc</kbd> 关闭</p>
        </div>
      </div>
    </div>
  );
}
