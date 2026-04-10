import { Sparkles, Brain, Network, Loader2 } from 'lucide-react';

/* ── Decorative background blobs ── */
export function BackgroundDecoration() {
  return (
    <div className="pointer-events-none fixed inset-0 overflow-hidden" aria-hidden>
      <div
        className="absolute -top-32 -right-32 w-[480px] h-[480px] rounded-full"
        style={{ background: 'radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%)' }}
      />
      <div
        className="absolute -bottom-40 -left-40 w-[520px] h-[520px] rounded-full"
        style={{ background: 'radial-gradient(circle, rgba(245,158,11,0.08) 0%, transparent 70%)' }}
      />
      <div
        className="absolute top-1/3 -left-20 w-[300px] h-[300px] rounded-full"
        style={{ background: 'radial-gradient(circle, rgba(99,102,241,0.06) 0%, transparent 70%)' }}
      />
    </div>
  );
}

/* ── Feature pills shown below subtitle ── */
export function FeaturePills() {
  const pills = [
    { icon: Sparkles, label: 'AI-Powered' },
    { icon: Brain, label: 'Smart Review' },
    { icon: Network, label: 'Knowledge Graph' },
  ];
  return (
    <div className="flex items-center justify-center gap-3 flex-wrap">
      {pills.map(({ icon: Icon, label }) => (
        <span
          key={label}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium"
          style={{
            backgroundColor: 'var(--color-tint-primary)',
            color: 'var(--color-accent-primary)',
            border: '1px solid rgba(16,185,129,0.15)',
          }}
        >
          <Icon size={12} />
          {label}
        </span>
      ))}
    </div>
  );
}

/* ── Email/password login form ── */
interface LoginEmailFormProps {
  mode: 'login' | 'register';
  email: string;
  password: string;
  displayName: string;
  error: string;
  loading: boolean;
  supabaseConfigured: boolean;
  onEmailChange: (val: string) => void;
  onPasswordChange: (val: string) => void;
  onDisplayNameChange: (val: string) => void;
  onSubmit: (e: React.FormEvent) => void;
  onToggleMode: () => void;
}

export function LoginEmailForm({
  mode, email, password, displayName, error, loading, supabaseConfigured,
  onEmailChange, onPasswordChange, onDisplayNameChange, onSubmit, onToggleMode,
}: LoginEmailFormProps) {
  return (
    <form onSubmit={onSubmit} className="animate-fade-in stagger-3" style={{ display: 'flex', flexDirection: 'column', gap: 24, marginTop: supabaseConfigured ? 0 : 8 }}>
      {mode === 'register' && (
        <div>
          <label className="block text-xs font-medium" style={{ marginBottom: 10, color: 'var(--color-text-secondary)' }}>Display Name</label>
          <input type="text" placeholder="Your name" value={displayName} onChange={(e) => onDisplayNameChange(e.target.value)} required className="login-input" />
        </div>
      )}
      <div>
        <label className="block text-xs font-medium" style={{ marginBottom: 10, color: 'var(--color-text-secondary)' }}>Email</label>
        <input type="email" placeholder="you@example.com" value={email} onChange={(e) => onEmailChange(e.target.value)} required autoComplete="email" className="login-input" />
      </div>
      <div>
        <label className="block text-xs font-medium" style={{ marginBottom: 10, color: 'var(--color-text-secondary)' }}>Password</label>
        <input type="password" placeholder="••••••••" value={password} onChange={(e) => onPasswordChange(e.target.value)} required minLength={6} autoComplete={mode === 'login' ? 'current-password' : 'new-password'} className="login-input" />
      </div>
      {error && (
        <div className="text-sm rounded-lg" style={{ padding: '12px 16px', backgroundColor: 'rgba(244,63,94,0.08)', color: 'var(--color-accent-rose)', border: '1px solid rgba(244,63,94,0.15)' }}>
          {error}
        </div>
      )}
      <button type="submit" disabled={loading}
        className="w-full rounded-xl text-sm font-semibold transition-all disabled:opacity-50 flex items-center justify-center gap-2"
        style={{ marginTop: 12, padding: '14px 0', background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'var(--color-text-on-accent)', boxShadow: '0 2px 8px rgba(16,185,129,0.08)' }}
        onMouseEnter={(e) => { if (!loading) e.currentTarget.style.boxShadow = '0 4px 16px rgba(16,185,129,0.12)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.boxShadow = '0 2px 8px rgba(16,185,129,0.08)'; }}
      >
        {loading && <Loader2 size={14} className="animate-spin" />}
        {loading ? 'Processing...' : mode === 'login' ? 'Sign in with Email' : 'Create Account'}
      </button>
      <button type="button" onClick={onToggleMode}
        className="w-full text-sm font-medium transition-colors"
        style={{ padding: '12px 0', marginTop: 4, color: 'var(--color-accent-primary)' }}
        onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--color-accent-warm)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-accent-primary)'; }}
      >
        {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
      </button>
    </form>
  );
}
