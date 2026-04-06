import { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { ToastContainer } from './components/common/ToastContainer';
import { HomePage } from './pages/HomePage';
import { useAuthStore } from './lib/store/auth';
import { useAppLifecycle } from './lib/hooks/useAppLifecycle';
import { useLearningStore } from './lib/store/learning';
import { OfflineIndicator } from './components/common/OfflineIndicator';
import { KeyboardShortcutsHelp } from './components/common/KeyboardShortcutsHelp';
import { ConceptSearch } from './components/common/ConceptSearch';
import './lib/store/supabase-sync';

// ── Route-level code splitting ──────────────────────────────
// Only HomePage is eagerly loaded (landing page).
// All other pages are lazy-loaded to reduce initial bundle size.
// GraphPage + Three.js (~200KB gzipped) only loads when user navigates to /domain/:id
const GraphPage = lazy(() => import('./pages/GraphPage').then(m => ({ default: m.GraphPage })));
const LearnPage = lazy(() => import('./pages/LearnPage').then(m => ({ default: m.LearnPage })));
const ReviewPage = lazy(() => import('./pages/ReviewPage').then(m => ({ default: m.ReviewPage })));
const DashboardPage = lazy(() => import('./pages/DashboardPage').then(m => ({ default: m.DashboardPage })));
const LoginPage = lazy(() => import('./pages/LoginPage').then(m => ({ default: m.LoginPage })));
const SettingsPage = lazy(() => import('./pages/SettingsPage').then(m => ({ default: m.SettingsPage })));
const NotFoundPage = lazy(() => import('./pages/NotFoundPage').then(m => ({ default: m.NotFoundPage })));

/** Minimal loading spinner for lazy routes */
function RouteLoader() {
  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
        <span className="text-sm text-gray-400">加载中…</span>
      </div>
    </div>
  );
}

export function App() {
  const initialize = useAuthStore((s) => s.initialize);
  const refreshStreak = useLearningStore((s) => s.refreshStreak);

  useEffect(() => {
    initialize();
  }, [initialize]);

  // Refresh streak data when app returns to foreground (mobile resume / tab focus)
  useAppLifecycle({
    onForeground: () => {
      refreshStreak();
    },
  });

  return (
    <ErrorBoundary showHomeButton>
      <BrowserRouter>
        <Suspense fallback={<RouteLoader />}>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route element={<AppLayout />}>
              {/* Home — domain selection (eager-loaded) */}
              <Route path="/" element={<HomePage />} />
              {/* Graph — domain overview (lazy: Three.js heavy) */}
              <Route path="/domain/:domainId" element={<GraphPage />} />
              {/* Graph — with concept detail panel open */}
              <Route path="/domain/:domainId/:conceptId" element={<GraphPage />} />
              {/* Learn — deep learning page (lazy) */}
              <Route path="/learn/:domainId/:conceptId" element={<LearnPage />} />
              {/* Review — FSRS spaced repetition review (lazy) */}
              <Route path="/review" element={<ReviewPage />} />
              <Route path="/review/:domainId" element={<ReviewPage />} />
              {/* Dashboard — learning analytics (lazy) */}
              <Route path="/dashboard" element={<DashboardPage />} />
              {/* Settings — LLM config + data export/import (lazy) */}
              <Route path="/settings" element={<SettingsPage />} />
              {/* Legacy fallback — redirect old /learn/:conceptId to home */}
              <Route path="/learn/:conceptId" element={<Navigate to="/" replace />} />
              {/* 404 — show a proper not-found page */}
              <Route path="*" element={<NotFoundPage />} />
            </Route>
          </Routes>
        </Suspense>
        <ToastContainer />
        <OfflineIndicator />
        <KeyboardShortcutsHelp />
        <ConceptSearch />
      </BrowserRouter>
    </ErrorBoundary>
  );
}
