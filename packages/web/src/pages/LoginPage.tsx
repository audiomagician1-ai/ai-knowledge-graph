import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/lib/store/auth';

export function LoginPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { signInWithEmail, signUp } = useAuthStore();

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
      setError(err instanceof Error ? err.message : '操作失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="flex min-h-dvh flex-col items-center justify-center px-6"
      style={{ backgroundColor: 'var(--bg-primary)' }}
    >
      {/* Logo区域 */}
      <div className="mb-8 text-center">
        <div className="text-6xl mb-3">🌌</div>
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          AI知识图谱
        </h1>
        <p className="mt-1 text-sm" style={{ color: 'var(--text-secondary)' }}>
          点亮你的知识宇宙
        </p>
      </div>

      {/* 表单 */}
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4">
        {mode === 'register' && (
          <input
            type="text"
            placeholder="显示名称"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            required
            className="w-full rounded-xl px-4 py-3 text-sm outline-none"
            style={{
              backgroundColor: 'var(--bg-tertiary)',
              color: 'var(--text-primary)',
              border: '1px solid var(--border-default)',
            }}
          />
        )}
        <input
          type="email"
          placeholder="邮箱"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full rounded-xl px-4 py-3 text-sm outline-none"
          style={{
            backgroundColor: 'var(--bg-tertiary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-default)',
          }}
        />
        <input
          type="password"
          placeholder="密码"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
          className="w-full rounded-xl px-4 py-3 text-sm outline-none"
          style={{
            backgroundColor: 'var(--bg-tertiary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-default)',
          }}
        />

        {error && (
          <p className="text-sm text-red-400">{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl py-3 text-sm font-semibold transition-opacity disabled:opacity-50"
          style={{ backgroundColor: 'var(--color-primary)', color: '#fff' }}
        >
          {loading ? '处理中...' : mode === 'login' ? '登录' : '注册'}
        </button>

        <button
          type="button"
          onClick={() => setMode(mode === 'login' ? 'register' : 'login')}
          className="w-full py-2 text-sm"
          style={{ color: 'var(--color-primary)' }}
        >
          {mode === 'login' ? '没有账号？去注册' : '已有账号？去登录'}
        </button>
      </form>
    </div>
  );
}
