import { Component, type ReactNode, type ErrorInfo } from 'react';

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
    console.error('[ErrorBoundary]', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div
          className="flex items-center justify-center min-h-[200px] p-6"
          style={{ backgroundColor: '#0f172a' }}
        >
          <div className="text-center max-w-md">
            <div className="text-5xl mb-4">💥</div>
            <h2 className="text-lg font-bold mb-2" style={{ color: '#f1f5f9' }}>
              出了点小问题
            </h2>
            <p className="text-sm mb-4" style={{ color: '#94a3b8' }}>
              {this.state.error?.message || '未知错误'}
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: null });
                window.location.reload();
              }}
              className="rounded-xl px-6 py-2.5 text-sm font-medium"
              style={{ backgroundColor: '#5ed3ac', color: '#0f1419' }}
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