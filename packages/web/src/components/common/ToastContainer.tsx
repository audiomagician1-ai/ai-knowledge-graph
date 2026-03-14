import { useToastStore, type ToastType } from '@/lib/store/toast';

const STYLE_MAP: Record<ToastType, { bg: string; border: string; text: string; icon: string }> = {
  success: { bg: '#1a2218', border: '#2d3a28', text: '#8aad7a', icon: '✓' },
  error: { bg: '#450a0a', border: '#991b1b', text: '#fca5a5', icon: '✕' },
  info: { bg: '#172554', border: '#1e40af', text: '#93c5fd', icon: 'ℹ' },
  warning: { bg: '#422006', border: '#92400e', text: '#fde68a', icon: '⚠' },
};

export function ToastContainer() {
  const { toasts, removeToast } = useToastStore();

  if (toasts.length === 0) return null;

  return (
    <div className="fixed top-4 right-4 z-[9999] flex flex-col gap-2 max-w-sm">
      {toasts.map((t) => {
        const s = STYLE_MAP[t.type];
        return (
          <div
            key={t.id}
            className="flex items-center gap-2 rounded-lg px-4 py-3 text-sm shadow-lg animate-in slide-in-from-right"
            style={{ backgroundColor: s.bg, border: `1px solid ${s.border}`, color: s.text }}
            role="alert"
          >
            <span className="font-bold text-base">{s.icon}</span>
            <span className="flex-1">{t.message}</span>
            <button
              onClick={() => removeToast(t.id)}
              className="shrink-0 opacity-60 hover:opacity-100 text-xs ml-2"
            >
              ✕
            </button>
          </div>
        );
      })}
    </div>
  );
}