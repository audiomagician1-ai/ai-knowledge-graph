import { Component, type ReactNode, type ErrorInfo } from 'react';
import { createLogger } from '@/lib/utils/logger';

const log = createLogger('ErrorBoundary');

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  /** If true, show a "go home" button in addition to retry */
  showHomeButton?: boolean;
}

interface State {
  hasError: boolean;
  error: Error | null;
  retryCount: number;
}

/**
 * React Error Boundary — 捕获子组件渲染错误
 * 
 * Features:
 * - Logs errors with component stack
 * - Shows retry button (resets error state without reload)
 * - Shows reload button as fallback
 * - Optional "go home" button for route-level boundaries
 * - Tracks retry count to prevent infinite loops
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null, retryCount: 0 };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    log.error('Uncaught render error', {
      err: error.message,
      componentStack: errorInfo.componentStack?.slice(0, 200),
      retryCount: this.state.retryCount,
    });
  }

  handleRetry = () => {
    if (this.state.retryCount >= 3) {
      // Too many retries, force reload
      window.location.reload();
      return;
    }
    this.setState((prev) => ({
      hasError: false,
      error: null,
      retryCount: prev.retryCount + 1,
    }));
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      const { retryCount } = this.state;
      const canRetry = retryCount < 3;

      return (
        <div
          className="flex items-center justify-center min-h-[200px] p-6"
          style={{ backgroundColor: 'var(--color-surface-0, #f5f5f2)' }}
        >
          <div className="text-center max-w-md">
            <div className="text-5xl mb-4">💥</div>
            <h2 className="text-lg font-bold mb-2" style={{ color: 'var(--color-text-primary, #1c1917)' }}>
              出了点小问题
            </h2>
            <p className="text-sm mb-4" style={{ color: 'var(--color-text-tertiary, #78716c)' }}>
              {this.state.error?.message || '未知错误'}
            </p>
            <div className="flex items-center justify-center gap-3">
              {canRetry && (
                <button
                  onClick={this.handleRetry}
                  className="rounded-xl px-6 py-2.5 text-sm font-medium transition-colors hover:opacity-90"
                  style={{ backgroundColor: '#3b82f6', color: 'var(--color-text-on-accent)' }}
                >
                  重试 {retryCount > 0 ? `(${retryCount}/3)` : ''}
                </button>
              )}
              <button
                onClick={() => window.location.reload()}
                className="rounded-xl px-6 py-2.5 text-sm font-medium transition-colors hover:opacity-90"
                style={{ backgroundColor: '#10b981', color: 'var(--color-text-on-accent)' }}
              >
                刷新页面
              </button>
              {this.props.showHomeButton && (
                <button
                  onClick={this.handleGoHome}
                  className="rounded-xl px-6 py-2.5 text-sm font-medium transition-colors hover:opacity-90"
                  style={{ backgroundColor: '#6b7280', color: 'var(--color-text-on-accent)' }}
                >
                  返回首页
                </button>
              )}
            </div>
            {retryCount > 0 && (
              <p className="text-xs mt-3" style={{ color: 'var(--color-text-tertiary, #78716c)' }}>
                已重试 {retryCount} 次
              </p>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}