import { useNavigate } from 'react-router-dom';
import { Award, BookOpen, Play } from 'lucide-react';

export interface HistoryItem {
  id: number;
  concept_id: string;
  concept_name: string;
  score: number;
  mastered: boolean;
  action: string;
  timestamp: number;
  date: string;
  time: string;
}

export interface Pagination {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export const ACTION_ICONS: Record<string, typeof Award> = { mastered: Award, assessment: BookOpen, start: Play };
export const ACTION_LABELS: Record<string, string> = { mastered: '掌握', assessment: '评估', start: '开始学习', all: '全部' };
export const ACTION_COLORS: Record<string, string> = { mastered: 'text-yellow-400', assessment: 'text-blue-400', start: 'text-green-400' };

export function HistoryItemRow({ item }: { item: HistoryItem }) {
  const navigate = useNavigate();
  const Icon = ACTION_ICONS[item.action] || BookOpen;
  const color = ACTION_COLORS[item.action] || 'text-gray-400';
  return (
    <div
      className="flex items-center gap-4 px-4 py-3 bg-white/[0.03] hover:bg-white/[0.06] rounded-lg border border-white/5 transition-colors cursor-pointer"
      onClick={() => { const parts = item.concept_id.split('/'); if (parts.length >= 2) navigate(`/domain/${parts[0]}/${item.concept_id}`); }}
    >
      <div className={`p-2 rounded-lg bg-white/5 ${color}`}><Icon size={18} /></div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{item.concept_name || item.concept_id}</p>
        <p className="text-xs text-gray-500">{ACTION_LABELS[item.action]}</p>
      </div>
      {item.score > 0 && (
        <div className="text-right">
          <p className={`text-sm font-bold ${item.mastered ? 'text-yellow-400' : 'text-blue-400'}`}>{item.score}分</p>
        </div>
      )}
      <div className="text-right text-xs text-gray-500 whitespace-nowrap"><p>{item.date}</p><p>{item.time}</p></div>
    </div>
  );
}
