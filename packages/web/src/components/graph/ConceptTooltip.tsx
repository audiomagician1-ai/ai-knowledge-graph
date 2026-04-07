/**
 * ConceptTooltip — Floating tooltip that appears when hovering over a concept node in the 3D graph.
 * Shows concept name, difficulty, status, and estimated time.
 */
import { useMemo } from 'react';
import { BookOpen, CheckCircle, Clock, Star, Zap } from 'lucide-react';
import type { GraphNode } from '@akg/shared';

interface ConceptTooltipProps {
  node: GraphNode | null;
  position: { x: number; y: number } | null;
}

const DIFFICULTY_LABELS: Record<number, { text: string; color: string }> = {
  1: { text: '入门', color: '#22c55e' },
  2: { text: '入门', color: '#22c55e' },
  3: { text: '基础', color: '#22c55e' },
  4: { text: '进阶', color: '#06b6d4' },
  5: { text: '进阶', color: '#06b6d4' },
  6: { text: '进阶', color: '#0891b2' },
  7: { text: '高级', color: '#f97316' },
  8: { text: '高级', color: '#ea580c' },
  9: { text: '专家', color: '#8b5cf6' },
};

const STATUS_INFO: Record<string, { label: string; color: string; icon: typeof CheckCircle }> = {
  mastered: { label: '已掌握', color: '#10b981', icon: CheckCircle },
  learning: { label: '学习中', color: '#f59e0b', icon: BookOpen },
  not_started: { label: '未开始', color: '#94a3b8', icon: Clock },
};

export function ConceptTooltip({ node, position }: ConceptTooltipProps) {
  if (!node || !position) return null;

  const diff = DIFFICULTY_LABELS[node.difficulty] || { text: '未知', color: '#94a3b8' };
  const status = STATUS_INFO[node.status] || STATUS_INFO.not_started;
  const StatusIcon = status.icon;

  return (
    <div
      className="fixed z-50 pointer-events-none animate-fade-in"
      style={{
        left: position.x + 16,
        top: position.y - 8,
        maxWidth: 280,
      }}
    >
      <div className="bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm rounded-lg shadow-xl border border-gray-200/60 dark:border-gray-700/60 px-3 py-2.5">
        {/* Name + milestone */}
        <div className="flex items-center gap-1.5 mb-1.5">
          {node.is_milestone && <Star size={13} fill="#f59e0b" className="text-amber-500 flex-shrink-0" />}
          <span className="text-sm font-semibold text-gray-800 dark:text-gray-100 truncate">{node.label}</span>
        </div>

        {/* Status + difficulty + time */}
        <div className="flex items-center gap-3 text-xs">
          <span className="inline-flex items-center gap-1" style={{ color: status.color }}>
            <StatusIcon size={11} />
            {status.label}
          </span>
          <span className="inline-flex items-center gap-1" style={{ color: diff.color }}>
            <Zap size={11} />
            Lv.{node.difficulty} {diff.text}
          </span>
          {node.estimated_minutes && (
            <span className="inline-flex items-center gap-1 text-gray-400">
              <Clock size={11} />
              {node.estimated_minutes}min
            </span>
          )}
        </div>

        {/* Recommended tag */}
        {node.is_recommended && (
          <div className="mt-1.5 pt-1.5 border-t border-gray-100 dark:border-gray-700">
            <span className="text-[10px] font-medium text-cyan-600 dark:text-cyan-400">
              ✨ AI 推荐学习
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
