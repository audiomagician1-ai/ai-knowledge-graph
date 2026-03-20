import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/lib/store/auth';
import { BookOpen, Loader2, ArrowRight, ArrowLeft, Sparkles, Brain, Network } from 'lucide-react';

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
          padding: '44px 40px',
          backgroundColor: 'rgba(255,255,255,0.7)',
          backdropFilter: 'blur(20px)',
          border: '1px solid var(--color-border-subtle)',
          boxShadow: '0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04)',
        }}
      >
        {/* ── Logo + Title ── */}
        <div className="text-center" style={{ marginBottom: 36 }}>
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
          <p className="text-sm" style={{ marginBottom: 24, color: 'var(--color-text-tertiary)', lineHeight: 1.6 }}>
            Sign in to sync your learning progress across devices
          </p>
          <FeaturePills />
        </div>

        {/* ── OAuth buttons ── */}
        {supabaseConfigured && (
          <>
            <div className="animate-fade-in stagger-1" style={{ display: 'flex', flexDirection: 'column', gap: 12, marginBottom: 28 }}>
              <button
                onClick={() => handleOAuth('google')}
                disabled={loading}
                className="w-full flex items-center justify-center gap-3 rounded-xl py-3.5 text-sm font-medium transition-all disabled:opacity-50"
                style={{
                  backgroundColor: 'var(--color-surface-1)',
                  color: 'var(--color-text-primary)',
                  border: '1px solid var(--color-border)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface-2)';
                  e.currentTarget.style.borderColor = 'rgba(0,0,0,0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface-1)';
                  e.currentTarget.style.borderColor = 'var(--color-border)';
                }}
              >
                <GoogleIcon />
                Continue with Google
              </button>
              <button
                onClick={() => handleOAuth('github')}
                disabled={loading}
                className="w-full flex items-center justify-center gap-3 rounded-xl py-3.5 text-sm font-medium transition-all disabled:opacity-50"
                style={{
                  backgroundColor: 'var(--color-surface-1)',
                  color: 'var(--color-text-primary)',
                  border: '1px solid var(--color-border)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface-2)';
                  e.currentTarget.style.borderColor = 'rgba(0,0,0,0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'var(--color-surface-1)';
                  e.currentTarget.style.borderColor = 'var(--color-border)';
                }}
              >
                <GitHubIcon />
                Continue with GitHub
              </button>
            </div>

            {/* ── Divider ── */}
            <div className="flex items-center gap-4 animate-fade-in stagger-2" style={{ marginBottom: 28 }}>
              <div className="flex-1 h-px" style={{ backgroundColor: 'var(--color-border)' }} />
              <span className="text-xs font-medium tracking-wider uppercase" style={{ color: 'var(--color-text-tertiary)' }}>
                or
              </span>
              <div className="flex-1 h-px" style={{ backgroundColor: 'var(--color-border)' }} />
            </div>
          </>
        )}

        {/* ── Email form ── */}
        <form onSubmit={handleSubmit} className="animate-fade-in stagger-3" style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {mode === 'register' && (
            <div>
              <label className="block text-xs font-medium" style={{ marginBottom: 8, color: 'var(--color-text-secondary)' }}>
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
            <label className="block text-xs font-medium" style={{ marginBottom: 8, color: 'var(--color-text-secondary)' }}>
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
            <label className="block text-xs font-medium" style={{ marginBottom: 8, color: 'var(--color-text-secondary)' }}>
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
              marginTop: 8,
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

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24">
      <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 01-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
      <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
      <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
      <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
    </svg>
  );
}

function GitHubIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
    </svg>
  );
}
