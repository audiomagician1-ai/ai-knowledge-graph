import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { ErrorBoundary } from './components/common/ErrorBoundary';
import { ToastContainer } from './components/common/ToastContainer';
import { HomePage } from './pages/HomePage';
import { GraphPage } from './pages/GraphPage';
import { LearnPage } from './pages/LearnPage';
import { ReviewPage } from './pages/ReviewPage';
import { LoginPage } from './pages/LoginPage';
import { useAuthStore } from './lib/store/auth';
// Side-effect: registers onAuthLogin callback for cloud sync
import './lib/store/supabase-sync';

export function App() {
  const initialize = useAuthStore((s) => s.initialize);

  useEffect(() => {
    initialize();
  }, [initialize]);

  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<AppLayout />}>
            {/* Home — domain selection */}
            <Route path="/" element={<HomePage />} />
            {/* Graph — domain overview */}
            <Route path="/domain/:domainId" element={<GraphPage />} />
            {/* Graph — with concept detail panel open */}
            <Route path="/domain/:domainId/:conceptId" element={<GraphPage />} />
            {/* Learn — deep learning page */}
            <Route path="/learn/:domainId/:conceptId" element={<LearnPage />} />
            {/* Review — FSRS spaced repetition review */}
            <Route path="/review" element={<ReviewPage />} />
            <Route path="/review/:domainId" element={<ReviewPage />} />
            {/* Legacy fallback — redirect old /learn/:conceptId to home */}
            <Route path="/learn/:conceptId" element={<Navigate to="/" replace />} />
            {/* Catch-all → home */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
        <ToastContainer />
      </BrowserRouter>
    </ErrorBoundary>
  );
}
