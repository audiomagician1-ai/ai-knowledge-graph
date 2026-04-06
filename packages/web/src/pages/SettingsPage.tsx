import { useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { SettingsContent } from '@/components/panels/SettingsContent';

/**
 * Standalone settings page — accessible at /settings.
 * Wraps the existing SettingsContent panel component with page-level chrome (header + back nav).
 */
export function SettingsPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-dvh w-full" style={{ backgroundColor: 'var(--color-surface-0, #0f172a)' }}>
      {/* Header bar */}
      <header className="sticky top-0 z-30 flex items-center gap-3 px-4 py-3 border-b border-white/10 backdrop-blur-md bg-[#0f172a]/80">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition-colors"
          aria-label="返回"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>返回</span>
        </button>
        <h1 className="text-lg font-semibold text-white">设置</h1>
      </header>

      {/* Settings content — reuse the panel component */}
      <main className="max-w-2xl mx-auto px-4 py-6">
        <SettingsContent />
      </main>
    </div>
  );
}
