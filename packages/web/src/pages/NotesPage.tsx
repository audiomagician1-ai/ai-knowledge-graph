import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConceptNotes } from '@/lib/hooks/useConceptNotes';
import { useKeyboardShortcuts } from '@/lib/hooks/useKeyboardShortcuts';
import {
  ArrowLeft, StickyNote, Trash2, Download, Upload,
  Search, BookOpen, RefreshCw,
} from 'lucide-react';

/**
 * Notes Management Page — view, search, and manage all concept notes.
 * Path: /notes
 */
export function NotesPage() {
  const navigate = useNavigate();
  const { allNotesArray, deleteNote, exportNotes, importNotes, noteCount, syncToBackend, syncFromBackend } = useConceptNotes();
  const [syncing, setSyncing] = useState(false);
  const [search, setSearch] = useState('');
  const [importText, setImportText] = useState('');
  const [showImport, setShowImport] = useState(false);

  useKeyboardShortcuts([
    { key: 'Escape', handler: () => navigate('/'), description: 'Back to home' },
  ]);

  const filtered = search.trim()
    ? allNotesArray.filter(
        (n) =>
          n.conceptId.toLowerCase().includes(search.toLowerCase()) ||
          n.content.toLowerCase().includes(search.toLowerCase())
      )
    : allNotesArray;

  const handleExport = () => {
    const json = exportNotes();
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `akg-notes-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleImport = () => {
    if (importNotes(importText)) {
      setImportText('');
      setShowImport(false);
    }
  };

  return (
    <div className="min-h-dvh" style={{ backgroundColor: 'var(--color-surface-0)', color: 'var(--color-text-primary)' }}>
      {/* Header */}
      <header className="flex items-center gap-3 px-6 py-4 border-b" style={{ borderColor: 'var(--color-border)' }}>
        <button onClick={() => navigate('/')} className="p-2 rounded-lg hover:bg-white/10 transition-colors">
          <ArrowLeft size={20} />
        </button>
        <StickyNote size={24} style={{ color: '#f59e0b' }} />
        <h1 className="text-xl font-bold">学习笔记</h1>
        <span className="ml-auto text-sm opacity-50">{noteCount} 条</span>
      </header>

      <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
        {/* Search + actions */}
        <div className="flex items-center gap-3">
          <div className="flex-1 relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 opacity-40" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="搜索笔记…"
              className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm bg-transparent outline-none"
              style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }}
            />
          </div>
          <button
            onClick={handleExport}
            disabled={noteCount === 0}
            className="p-2.5 rounded-xl hover:bg-white/10 transition-colors"
            title="导出笔记"
            style={{ opacity: noteCount === 0 ? 0.3 : 1 }}
          >
            <Download size={18} />
          </button>
          <button
            onClick={() => setShowImport(!showImport)}
            className="p-2.5 rounded-xl hover:bg-white/10 transition-colors"
            title="导入笔记"
          >
            <Upload size={18} />
          </button>
          <button
            onClick={async () => {
              setSyncing(true);
              try {
                await syncToBackend();
                await syncFromBackend();
              } finally {
                setSyncing(false);
              }
            }}
            disabled={syncing}
            className="p-2.5 rounded-xl hover:bg-white/10 transition-colors"
            title="同步到云端"
          >
            <RefreshCw size={18} className={syncing ? 'animate-spin' : ''} />
          </button>
        </div>

        {/* Import area */}
        {showImport && (
          <div className="rounded-xl p-4 space-y-3" style={{ backgroundColor: 'var(--color-surface-1)' }}>
            <textarea
              value={importText}
              onChange={(e) => setImportText(e.target.value)}
              placeholder="粘贴导出的 JSON 笔记数据…"
              rows={4}
              className="w-full bg-transparent text-sm outline-none resize-none rounded-lg p-3"
              style={{ border: '1px solid var(--color-border)', color: 'var(--color-text-primary)' }}
            />
            <button
              onClick={handleImport}
              disabled={!importText.trim()}
              className="px-4 py-2 rounded-lg text-sm font-medium"
              style={{ backgroundColor: 'var(--color-accent-primary)', color: '#fff', opacity: importText.trim() ? 1 : 0.4 }}
            >
              导入合并
            </button>
          </div>
        )}

        {/* Notes list */}
        {filtered.length === 0 ? (
          <div className="text-center py-16 opacity-40">
            <BookOpen size={48} className="mx-auto mb-3" />
            <p className="text-sm">{noteCount === 0 ? '还没有笔记，学习时可以随时记录' : '没有匹配的笔记'}</p>
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((note) => (
              <div
                key={note.conceptId}
                className="rounded-xl p-4 hover:ring-1 transition-all cursor-pointer"
                style={{ backgroundColor: 'var(--color-surface-1)' }}
                onClick={() => {
                  // Try to navigate to the concept
                  navigate(`/`);
                }}
              >
                <div className="flex items-start justify-between gap-3 mb-2">
                  <h3 className="text-sm font-semibold">{note.conceptId}</h3>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteNote(note.conceptId);
                    }}
                    className="p-1 rounded hover:bg-red-500/10 transition-colors shrink-0"
                    title="删除笔记"
                  >
                    <Trash2 size={14} style={{ color: '#ef4444' }} />
                  </button>
                </div>
                <p className="text-sm opacity-70 whitespace-pre-wrap line-clamp-3">{note.content}</p>
                <div className="flex gap-4 mt-2 text-[10px] opacity-30">
                  <span>创建: {new Date(note.createdAt).toLocaleDateString('zh-CN')}</span>
                  <span>更新: {new Date(note.updatedAt).toLocaleDateString('zh-CN')}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
