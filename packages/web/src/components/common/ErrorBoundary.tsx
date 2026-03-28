import { Component, type ReactNode, type ErrorInfo } from 'react';
import { createLogger } from '@/lib/utils/logger';

const log = createLogger('ErrorBoundary');

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * React Error Boundary — 捕获子组件渲染错误
 */
export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    log.error('Uncaught render error', { err: error.message, componentStack: errorInfo.componentStack?.slice(0, 200) });
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

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
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              className="rounded-xl px-6 py-2.5 text-sm font-medium"
              style={{ backgroundColor: '#10b981', color: '#ffffff' }}
            >
              刷新页面
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}