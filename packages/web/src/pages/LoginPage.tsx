import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/lib/store/auth';
import { BookOpen, Mail, Loader2 } from 'lucide-react';

export function LoginPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signInWithEmail, signUp, signInWithOAuth } = useAuthStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (mode === 'login') {
        await signInWithEmail(email, password);
      } else {
        await signUp(email, password, displayName);
      }
      navigate('/graph');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Operation failed');
    } finally {
      setLoading(false);
    }
  };

  const handleOAuth = async (provider: 'google' | 'github') => {
    setError('');
    try {
      await signInWithOAuth(provider);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'OAuth failed');
    }
  };

  const inputStyle: React.CSSProperties = {
    backgroundColor: 'var(--color-surface-2)',
    color: 'var(--color-text-primary)',
    border: '1px solid var(--color-border)',
    borderRadius: 8,
    padding: '12px 16px',
    fontSize: 14,
    width: '100%',
    outline: 'none',
  };

  return (
    <div
      className="flex min-h-dvh flex-col items-center justify-center px-6"
      style={{ backgroundColor: 'var(--color-surface-0)' }}
    >
      {/* Logo */}
      <div className="mb-10 text-center animate-fade-in">
        <div
          className="w-14 h-14 rounded-xl flex items-center justify-center mx-auto mb-4"
          style={{ backgroundColor: 'var(--color-accent-primary)' }}
        >
          <BookOpen size={24} style={{ color: '#fff' }} />
        </div>
        <h1
          className="text-2xl font-bold mb-1"
          style={{ fontFamily: 'var(--font-heading)', color: 'var(--color-text-primary)' }}
        >
          AI Knowledge Graph
        </h1>
        <p className="text-sm" style={{ color: 'var(--color-text-tertiary)' }}>
          Sign in to sync progress across devices
        </p>
      </div>

      {/* OAuth buttons */}
      <div className="w-full max-w-sm space-y-3 mb-6 animate-fade-in stagger-1">
        <button
          onClick={() => handleOAuth('google')}
          className="w-full flex items-center justify-center gap-3 rounded-lg py-3 text-sm font-medium transition-colors"
          style={{
            backgroundColor: 'var(--color-surface-2)',
            color: 'var(--color-text-primary)',
            border: '1px solid var(--color-border)',
          }}
        >
          <GoogleIcon />
          Continue with Google
        </button>
        <button
          onClick={() => handleOAuth('github')}
          className="w-full flex items-center justify-center gap-3 rounded-lg py-3 text-sm font-medium transition-colors"
          style={{
            backgroundColor: 'var(--color-surface-2)',
            color: 'var(--color-text-primary)',
            border: '1px solid var(--color-border)',
          }}
        >
          <GitHubIcon />
          Continue with GitHub
        </button>
      </div>

      {/* Divider */}
      <div className="w-full max-w-sm flex items-center gap-4 mb-6 animate-fade-in stagger-2">
        <div className="flex-1 h-px" style={{ backgroundColor: 'var(--color-border)' }} />
        <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>OR</span>
        <div className="flex-1 h-px" style={{ backgroundColor: 'var(--color-border)' }} />
      </div>

      {/* Email form */}
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-3 animate-fade-in stagger-3">
        {mode === 'register' && (
          <input
            type="text" placeholder="Display name" value={displayName}
            onChange={(e) => setDisplayName(e.target.value)} required
            style={inputStyle}
          />
        )}
        <input
          type="email" placeholder="Email" value={email}
          onChange={(e) => setEmail(e.target.value)} required
          style={inputStyle}
        />
        <input
          type="password" placeholder="Password" value={password}
          onChange={(e) => setPassword(e.target.value)} required minLength={6}
          style={inputStyle}
        />

        {error && (
          <p className="text-sm" style={{ color: 'var(--color-accent-rose)' }}>{error}</p>
        )}

        <button
          type="submit" disabled={loading}
          className="w-full rounded-lg py-3 text-sm font-semibold transition-opacity disabled:opacity-50 flex items-center justify-center gap-2"
          style={{ backgroundColor: 'var(--color-accent-primary)', color: '#fff' }}
        >
          {loading && <Loader2 size={14} className="animate-spin" />}
          {loading ? 'Processing...' : mode === 'login' ? 'Sign in with Email' : 'Create Account'}
        </button>

        <button
          type="button"
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
          className="w-full py-2 text-sm"
          style={{ color: 'var(--color-accent-primary)' }}
        >
          {mode === 'login' ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
        </button>
      </form>

      {/* Skip */}
      <button
        onClick={() => navigate('/graph')}
        className="mt-6 text-sm transition-colors animate-fade-in stagger-4"
        style={{ color: 'var(--color-text-tertiary)' }}
        onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-text-tertiary)'; }}
      >
        Skip, continue without account &rarr;
      </button>
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
