/**
 * GraphLegend — Color legend for node statuses and difficulty levels in the 3D graph.
 * Collapsible to save space; expands on hover/click.
 */
import { useState } from 'react';
import { Info, ChevronUp, ChevronDown } from 'lucide-react';

export function GraphLegend() {
  const [expanded, setExpanded] = useState(false);

  const statusItems = [
    { color: '#10b981', label: '已掌握', desc: '成功通过评估' },
    { color: '#f59e0b', label: '学习中', desc: '正在学习对话' },
    { color: '#06b6d4', label: '推荐学习', desc: 'AI 推荐路径' },
    { color: '#94a3b8', label: '未开始', desc: '尚未接触' },
  ];

  const difficultyItems = [
    { color: '#22c55e', label: '入门 (1-3)', range: '基础概念' },
    { color: '#06b6d4', label: '进阶 (4-6)', range: '需要前置知识' },
    { color: '#f97316', label: '高级 (7-8)', range: '深度理解' },
    { color: '#8b5cf6', label: '专家 (9)', range: '领域最前沿' },
  ];

  return (
    <div className="absolute bottom-4 left-4 z-10 pointer-events-auto">
      <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/60 dark:border-gray-700/60 overflow-hidden transition-all duration-200">
        {/* Toggle header */}
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-2 px-3 py-2 w-full text-left hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
          aria-label={expanded ? '收起图例' : '展开图例'}
        >
          <Info size={14} className="text-gray-400" />
          <span className="text-xs font-medium text-gray-600 dark:text-gray-300">图例</span>
          {expanded ? <ChevronDown size={14} className="text-gray-400 ml-auto" /> : <ChevronUp size={14} className="text-gray-400 ml-auto" />}
        </button>

        {/* Expandable content */}
        {expanded && (
          <div className="px-3 pb-3 space-y-3">
            {/* Status legend */}
            <div>
              <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5">状态</p>
              <div className="space-y-1">
                {statusItems.map(item => (
                  <div key={item.label} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                    <span className="text-xs text-gray-700 dark:text-gray-200">{item.label}</span>
                    <span className="text-[10px] text-gray-400 ml-auto">{item.desc}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Difficulty legend */}
            <div>
              <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1.5">难度</p>
              <div className="space-y-1">
                {difficultyItems.map(item => (
                  <div key={item.label} className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ backgroundColor: item.color }} />
                    <span className="text-xs text-gray-700 dark:text-gray-200">{item.label}</span>
                    <span className="text-[10px] text-gray-400 ml-auto">{item.range}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Interaction hint */}
            <div className="pt-1 border-t border-gray-100 dark:border-gray-700">
              <p className="text-[10px] text-gray-400">
                点击节点开始学习 · 滚轮缩放 · 拖拽旋转
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
