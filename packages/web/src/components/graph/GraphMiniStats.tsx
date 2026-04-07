/**
 * GraphMiniStats — Compact domain stats overlay for the 3D graph page.
 * Shows mastery progress, concept counts, and learning streak in a minimal HUD.
 */
import { useMemo } from 'react';
import { BookOpen, CheckCircle, Clock, TrendingUp, Zap } from 'lucide-react';
import type { GraphNode } from '@akg/shared';

interface GraphMiniStatsProps {
  nodes: GraphNode[];
  domainName: string;
  domainColor: string;
  streak?: number;
}

export function GraphMiniStats({ nodes, domainName, domainColor, streak = 0 }: GraphMiniStatsProps) {
  const stats = useMemo(() => {
    const total = nodes.length;
    const mastered = nodes.filter(n => n.status === 'mastered').length;
    const learning = nodes.filter(n => n.status === 'learning').length;
    const notStarted = total - mastered - learning;
    const pct = total > 0 ? Math.round((mastered / total) * 100) : 0;
    return { total, mastered, learning, notStarted, pct };
  }, [nodes]);

  // SVG progress ring
  const radius = 18;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (stats.pct / 100) * circumference;

  return (
    <div className="absolute top-4 left-4 z-10 pointer-events-auto">
      <div className="bg-white/90 dark:bg-gray-900/90 backdrop-blur-sm rounded-xl shadow-lg border border-gray-200/60 dark:border-gray-700/60 px-4 py-3 min-w-[200px]">
        {/* Domain name + progress ring */}
        <div className="flex items-center gap-3 mb-2">
          <svg width="44" height="44" viewBox="0 0 44 44" className="flex-shrink-0">
            <circle cx="22" cy="22" r={radius} fill="none" stroke="#e5e7eb" strokeWidth="3" />
            <circle
              cx="22" cy="22" r={radius} fill="none"
              stroke={domainColor}
              strokeWidth="3"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              transform="rotate(-90 22 22)"
              className="transition-all duration-700 ease-out"
            />
            <text x="22" y="22" textAnchor="middle" dominantBaseline="central"
              className="text-[10px] font-bold fill-gray-700 dark:fill-gray-200">
              {stats.pct}%
            </text>
          </svg>
          <div className="min-w-0">
            <h3 className="text-sm font-semibold text-gray-800 dark:text-gray-100 truncate">{domainName}</h3>
            <p className="text-xs text-gray-500 dark:text-gray-400">{stats.total} 概念</p>
          </div>
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-3 gap-2 text-center">
          <div className="flex flex-col items-center gap-0.5">
            <div className="flex items-center gap-1">
              <CheckCircle size={12} className="text-emerald-500" />
              <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">{stats.mastered}</span>
            </div>
            <span className="text-[10px] text-gray-400">已掌握</span>
          </div>
          <div className="flex flex-col items-center gap-0.5">
            <div className="flex items-center gap-1">
              <BookOpen size={12} className="text-amber-500" />
              <span className="text-xs font-medium text-amber-600 dark:text-amber-400">{stats.learning}</span>
            </div>
            <span className="text-[10px] text-gray-400">学习中</span>
          </div>
          <div className="flex flex-col items-center gap-0.5">
            <div className="flex items-center gap-1">
              <Clock size={12} className="text-gray-400" />
              <span className="text-xs font-medium text-gray-500">{stats.notStarted}</span>
            </div>
            <span className="text-[10px] text-gray-400">未开始</span>
          </div>
        </div>

        {/* Streak badge */}
        {streak > 0 && (
          <div className="mt-2 pt-2 border-t border-gray-100 dark:border-gray-700 flex items-center justify-center gap-1.5">
            <Zap size={12} className="text-orange-500" />
            <span className="text-xs font-medium text-orange-600 dark:text-orange-400">
              {streak} 天连续学习
            </span>
            <TrendingUp size={12} className="text-orange-400" />
          </div>
        )}
      </div>
    </div>
  );
}
