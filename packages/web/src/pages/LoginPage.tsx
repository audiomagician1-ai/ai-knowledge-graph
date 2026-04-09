import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createLogger } from '@/lib/utils/logger';
import { useAuthStore } from '@/lib/store/auth';
import { BookOpen, Loader2, ArrowRight, ArrowLeft, Sparkles, Brain, Network } from 'lucide-react';
import { LoginOAuthButtons } from '@/components/auth/LoginOAuthButtons';

const log = createLogger('LoginPage');

/* ── Decorative background blobs ── */
function BackgroundDecoration() {
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

/* ── Feature pill shown below subtitle ── */
function FeaturePills() {
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

export function LoginPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signInWithEmail, signUp, signInWithOAuth, supabaseConfigured } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (mode === 'login') {
        await signInWithEmail(email, password);
        navigate('/');
      } else {
        await signUp(email, password, displayName);
        const { session } = useAuthStore.getState();
        if (session) {
          navigate('/');
        } else {
          setError('Please check your email to confirm your account.');
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Operation failed';
      if (msg === 'Failed to fetch' || msg.includes('fetch')) {
        setError('无法连接到认证服务器。请检查网络连接，或尝试使用 VPN。');
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = async (provider: 'google' | 'github') => {
    if (loading) return;
    setError('');
    setLoading(true);
    try {
      await signInWithOAuth(provider);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'OAuth login is not configured yet. Please use email sign-in.');
      setLoading(false);
    }
  };

  return (
    <div
      className="relative flex min-h-dvh flex-col items-center justify-center px-6 py-16"
      style={{ backgroundColor: 'var(--color-surface-0)' }}
    >
      <BackgroundDecoration />

      {/* ── Back to home ── */}
      <button
        onClick={() => navigate('/')}
        className="absolute top-5 left-5 z-20 inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all group"
        style={{ color: 'var(--color-text-tertiary)' }}
        onMouseEnter={(e) => {
          e.currentTarget.style.color = 'var(--color-text-primary)';
          e.currentTarget.style.backgroundColor = 'var(--color-surface-2)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.color = 'var(--color-text-tertiary)';
          e.currentTarget.style.backgroundColor = 'transparent';
        }}
      >
        <ArrowLeft size={15} className="transition-transform group-hover:-translate-x-0.5" />
        Back to Home
      </button>

      {/* ── Card container ── */}
      <div
        className="relative z-10 w-full max-w-[440px] rounded-2xl animate-fade-in"
        style={{
          padding: '48px 40px',
          backgroundColor: 'rgba(255,255,255,0.7)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--color-border-subtle)',
          boxShadow: '0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04)',
        }}
      >
        {/* ── Logo + Title ── */}
        <div className="text-center" style={{ marginBottom: 40 }}>
          <div
            className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto"
            style={{
              marginBottom: 20,
              background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)',
              boxShadow: '0 4px 16px rgba(16,185,129,0.3)',
            }}
          >
            <BookOpen size={28} style={{ color: '#fff' }} strokeWidth={1.8} />
          </div>
          <h1
            className="text-2xl font-bold"
            style={{ marginBottom: 10, fontFamily: 'var(--font-heading)', color: 'var(--color-text-primary)' }}
          >
            AI Knowledge Graph
          </h1>
          <p className="text-sm" style={{ marginBottom: 20, color: 'var(--color-text-tertiary)', lineHeight: 1.6 }}>
            Sign in to sync your learning progress across devices
          </p>
          <FeaturePills />
        </div>

        {supabaseConfigured && <LoginOAuthButtons loading={loading} onOAuth={handleOAuth} />}

        {/* ── Email form ── */}
        <form onSubmit={handleSubmit} className="animate-fade-in stagger-3" style={{ display: 'flex', flexDirection: 'column', gap: 24, marginTop: supabaseConfigured ? 0 : 8 }}>
          {mode === 'register' && (
            <div>
              <label className="block text-xs font-medium" style={{ marginBottom: 10, color: 'var(--color-text-secondary)' }}>
                Display Name
              </label>
              <input
                type="text"
                placeholder="Your name"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                required
                className="login-input"
              />
            </div>
          )}
          <div>
            <label className="block text-xs font-medium" style={{ marginBottom: 10, color: 'var(--color-text-secondary)' }}>
              Email
            </label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              className="login-input"
            />
          </div>
          <div>
            <label className="block text-xs font-medium" style={{ marginBottom: 10, color: 'var(--color-text-secondary)' }}>
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              className="login-input"
            />
          </div>

          {error && (
            <div
              className="text-sm rounded-lg"
              style={{
                padding: '12px 16px',
                backgroundColor: 'rgba(244,63,94,0.08)',
                color: 'var(--color-accent-rose)',
                border: '1px solid rgba(244,63,94,0.15)',
              }}
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl text-sm font-semibold transition-all disabled:opacity-50 flex items-center justify-center gap-2"
            style={{
              marginTop: 12,
              padding: '14px 0',
              background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              color: '#fff',
              boxShadow: '0 2px 8px rgba(16,185,129,0.3)',
            }}
            onMouseEnter={(e) => {
              if (!loading) e.currentTarget.style.boxShadow = '0 4px 16px rgba(16,185,129,0.4)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.boxShadow = '0 2px 8px rgba(16,185,129,0.3)';
            }}
          >
            {loading && <Loader2 size={14} className="animate-spin" />}
            {loading ? 'Processing...' : mode === 'login' ? 'Sign in with Email' : 'Create Account'}
          </button>

          <button
            type="button"
            onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); setPassword(''); }}
            className="w-full text-sm font-medium transition-colors"
            style={{ padding: '12px 0', marginTop: 4, color: 'var(--color-accent-primary)' }}
            onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--color-accent-warm)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-accent-primary)'; }}
          >
            {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
          </button>
        </form>
      </div>

      {/* ── Skip link (outside the card) ── */}
      <button
        onClick={() => navigate('/')}
        className="relative z-10 inline-flex items-center gap-1.5 text-sm font-medium transition-all animate-fade-in stagger-4 group"
        style={{ marginTop: 28, color: 'var(--color-text-tertiary)' }}
        onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-text-tertiary)'; }}
      >
        Skip, continue without account
        <ArrowRight size={14} className="transition-transform group-hover:translate-x-0.5" />
      </button>

      {/* ── Footer ── */}
      <p
        className="relative z-10 text-xs animate-fade-in stagger-5"
        style={{ marginTop: 16, color: 'var(--color-text-tertiary)', opacity: 0.7 }}
      >
        Your data is stored locally. Sign in to enable cloud sync.
      </p>
    </div>
  );
}


