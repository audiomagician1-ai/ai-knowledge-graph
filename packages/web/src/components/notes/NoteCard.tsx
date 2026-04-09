import { useNavigate } from 'react-router-dom';
import { Trash2 } from 'lucide-react';

interface NoteCardProps {
  conceptId: string;
  content: string;
  createdAt: string | number;
  updatedAt: string | number;
  onDelete: (id: string) => void;
}

export function NoteCard({ conceptId, content, createdAt, updatedAt, onDelete }: NoteCardProps) {
  const navigate = useNavigate();
  return (
    <div
      className="rounded-xl p-4 hover:ring-1 transition-all cursor-pointer"
      style={{ backgroundColor: 'var(--color-surface-1)' }}
      onClick={() => navigate(`/`)}
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <h3 className="text-sm font-semibold">{conceptId}</h3>
        <button onClick={(e) => { e.stopPropagation(); onDelete(conceptId); }}
          className="p-1 rounded hover:bg-red-500/10 transition-colors shrink-0" title="删除笔记">
          <Trash2 size={14} style={{ color: '#ef4444' }} />
        </button>
      </div>
      <p className="text-sm opacity-70 whitespace-pre-wrap line-clamp-3">{content}</p>
      <div className="flex gap-4 mt-2 text-[10px] opacity-30">
        <span>创建: {new Date(createdAt).toLocaleDateString('zh-CN')}</span>
        <span>更新: {new Date(updatedAt).toLocaleDateString('zh-CN')}</span>
      </div>
    </div>
  );
}
