/**
 * WidgetErrorBoundary — Isolates crash in a single Dashboard widget.
 *
 * V4.1: Prevents one failing widget from taking down the entire Dashboard.
 * Shows a compact error card with retry button instead of a blank screen.
 */
import { Component, type ErrorInfo, type ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  name?: string;
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class WidgetErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.warn(`[WidgetErrorBoundary] ${this.props.name ?? 'Widget'} crashed:`, error.message, info.componentStack?.slice(0, 200));
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-xl border border-red-500/20 bg-red-500/5 p-4 space-y-2">
          <div className="flex items-center gap-2 text-red-400">
            <AlertTriangle size={16} />
            <span className="text-sm font-medium">{this.props.name ?? '组件'}加载失败</span>
          </div>
          <p className="text-xs opacity-40 truncate">{this.state.error?.message}</p>
          <button
            onClick={this.handleRetry}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-white/10 hover:border-white/20 opacity-60 hover:opacity-100 transition-opacity"
          >
            <RefreshCw size={12} />
            重试
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
