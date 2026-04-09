import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/lib/store/auth';
import { BookOpen, ArrowRight, ArrowLeft } from 'lucide-react';
import { LoginOAuthButtons } from '@/components/auth/LoginOAuthButtons';
import { BackgroundDecoration, FeaturePills, LoginEmailForm } from '@/components/auth/LoginPageParts';

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
        if (session) { navigate('/'); } else { setError('Please check your email to confirm your account.'); }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Operation failed';
      setError(msg === 'Failed to fetch' || msg.includes('fetch') ? '无法连接到认证服务器。请检查网络连接，或尝试使用 VPN。' : msg);
    } finally { setLoading(false); }
  };

  const handleOAuth = async (provider: 'google' | 'github') => {
    if (loading) return;
    setError('');
    setLoading(true);
    try { await signInWithOAuth(provider); }
    catch (err) { setError(err instanceof Error ? err.message : 'OAuth login is not configured yet. Please use email sign-in.'); setLoading(false); }
  };

  return (
    <div className="relative flex min-h-dvh flex-col items-center justify-center px-6 py-16" style={{ backgroundColor: 'var(--color-surface-0)' }}>
      <BackgroundDecoration />
      <button onClick={() => navigate('/')}
        className="absolute top-5 left-5 z-20 inline-flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all group"
        style={{ color: 'var(--color-text-tertiary)' }}
        onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--color-text-primary)'; e.currentTarget.style.backgroundColor = 'var(--color-surface-2)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-text-tertiary)'; e.currentTarget.style.backgroundColor = 'transparent'; }}
      >
        <ArrowLeft size={15} className="transition-transform group-hover:-translate-x-0.5" />
        Back to Home
      </button>
      <div className="relative z-10 w-full max-w-[440px] rounded-2xl animate-fade-in"
        style={{ padding: '48px 40px', backgroundColor: 'rgba(255,255,255,0.7)', backdropFilter: 'blur(20px)', border: '1px solid var(--color-border-subtle)', boxShadow: '0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04)' }}
      >
        <div className="text-center" style={{ marginBottom: 40 }}>
          <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto"
            style={{ marginBottom: 20, background: 'linear-gradient(135deg, #10b981 0%, #34d399 100%)', boxShadow: '0 4px 16px rgba(16,185,129,0.3)' }}>
            <BookOpen size={28} style={{ color: '#fff' }} strokeWidth={1.8} />
          </div>
          <h1 className="text-2xl font-bold" style={{ marginBottom: 10, fontFamily: 'var(--font-heading)', color: 'var(--color-text-primary)' }}>AI Knowledge Graph</h1>
          <p className="text-sm" style={{ marginBottom: 20, color: 'var(--color-text-tertiary)', lineHeight: 1.6 }}>Sign in to sync your learning progress across devices</p>
          <FeaturePills />
        </div>
        {supabaseConfigured && <LoginOAuthButtons loading={loading} onOAuth={handleOAuth} />}
        <LoginEmailForm mode={mode} email={email} password={password} displayName={displayName} error={error}
          loading={loading} supabaseConfigured={supabaseConfigured}
          onEmailChange={setEmail} onPasswordChange={setPassword} onDisplayNameChange={setDisplayName}
          onSubmit={handleSubmit} onToggleMode={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); setPassword(''); }} />
      </div>
      <button onClick={() => navigate('/')}
        className="relative z-10 inline-flex items-center gap-1.5 text-sm font-medium transition-all animate-fade-in stagger-4 group"
        style={{ marginTop: 28, color: 'var(--color-text-tertiary)' }}
        onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--color-text-secondary)'; }}
        onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--color-text-tertiary)'; }}
      >
        Skip, continue without account
        <ArrowRight size={14} className="transition-transform group-hover:translate-x-0.5" />
      </button>
      <p className="relative z-10 text-xs animate-fade-in stagger-5" style={{ marginTop: 16, color: 'var(--color-text-tertiary)', opacity: 0.7 }}>
        Your data is stored locally. Sign in to enable cloud sync.
      </p>
    </div>
  );
}
