import { useRef, useState, useCallback, useEffect, type ReactNode } from 'react';
import { X } from 'lucide-react';

interface DraggableModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  width?: number;
  height?: number;
  children: ReactNode;
}

export function DraggableModal({ open, onClose, title, width = 560, height = 520, children }: DraggableModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const [pos, setPos] = useState({ x: 0, y: 0 });
  const [initialized, setInitialized] = useState(false);
  const dragging = useRef(false);
  const offset = useRef({ x: 0, y: 0 });

  // Center on first open
  useEffect(() => {
    if (open && !initialized) {
      setPos({
        x: Math.round((window.innerWidth - width) / 2),
        y: Math.round((window.innerHeight - height) / 2),
      });
      setInitialized(true);
    }
    if (!open) setInitialized(false);
  }, [open, initialized, width, height]);

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    if ((e.target as HTMLElement).closest('button, input, textarea, select, a')) return;
    dragging.current = true;
    offset.current = { x: e.clientX - pos.x, y: e.clientY - pos.y };
    e.preventDefault();
  }, [pos]);

  useEffect(() => {
    if (!open) return;
    const onMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      setPos({
        x: Math.max(0, Math.min(window.innerWidth - 100, e.clientX - offset.current.x)),
        y: Math.max(0, Math.min(window.innerHeight - 60, e.clientY - offset.current.y)),
      });
    };
    const onUp = () => { dragging.current = false; };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => { window.removeEventListener('mousemove', onMove); window.removeEventListener('mouseup', onUp); };
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50" style={{ pointerEvents: 'none' }}>
      {/* Backdrop — click to close */}
      <div className="absolute inset-0" style={{ pointerEvents: 'auto' }} onClick={onClose} />
      {/* Modal */}
      <div
        ref={modalRef}
        className="absolute flex flex-col animate-fade-in-scale"
        style={{
          left: pos.x,
          top: pos.y,
          width,
          maxHeight: height,
          pointerEvents: 'auto',
          background: 'var(--color-surface-1)',
          border: '1px solid rgba(0,0,0,0.1)',
          borderRadius: 16,
          boxShadow: '0 24px 80px rgba(0,0,0,0.12), 0 0 0 0.5px rgba(0,0,0,0.04)',
          overflow: 'hidden',
        }}
      >
        {/* Title bar — draggable */}
        <div
          className="flex items-center justify-between px-7 py-5 shrink-0 select-none cursor-grab active:cursor-grabbing"
          style={{ borderBottom: '1px solid var(--color-border)' }}
          onMouseDown={onMouseDown}
        >
          <span className="text-base font-bold" style={{ color: 'var(--color-text-primary)' }}>{title}</span>
          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full flex items-center justify-center transition-colors"
            style={{ color: 'var(--color-text-tertiary)' }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(0,0,0,0.06)';
              e.currentTarget.style.color = 'var(--color-text-primary)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = 'var(--color-text-tertiary)';
            }}
          >
            <X size={14} />
          </button>
        </div>
        {/* Content */}
        <div className="flex-1 overflow-y-auto" style={{ WebkitOverflowScrolling: 'touch' }}>
          {children}
        </div>
      </div>
    </div>
  );
}
