import { useNavigate } from 'react-router-dom';
import { Home, ArrowLeft } from 'lucide-react';

/**
 * 404 Not Found page — shown for unrecognized routes.
 * Provides clear navigation options instead of a confusing silent redirect.
 */
export function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div
      className="min-h-dvh w-full flex items-center justify-center p-6"
      style={{ backgroundColor: 'var(--color-surface-0, #0f172a)' }}
    >
      <div className="text-center max-w-md">
        {/* Visual indicator */}
        <div className="text-7xl font-bold mb-2 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
          404
        </div>
        <h1 className="text-xl font-semibold text-white mb-2">
          页面不存在
        </h1>
        <p className="text-sm text-gray-400 mb-8">
          你访问的页面可能已被移动或删除。
        </p>

        {/* Navigation options */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium
                       border border-white/10 text-gray-300 hover:text-white hover:border-white/20
                       transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            返回上页
          </button>
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium
                       bg-blue-600 hover:bg-blue-500 text-white transition-colors"
          >
            <Home className="w-4 h-4" />
            回到首页
          </button>
        </div>
      </div>
    </div>
  );
}
