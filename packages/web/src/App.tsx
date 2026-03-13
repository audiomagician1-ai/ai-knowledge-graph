import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { GraphPage } from './pages/GraphPage';
import { LearnPage } from './pages/LearnPage';
import { DashboardPage } from './pages/DashboardPage';
import { LoginPage } from './pages/LoginPage';
import { useAuthStore } from './lib/store/auth';

export function App() {
  const session = useAuthStore((s) => s.session);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/graph" replace />} />
          <Route path="/graph" element={session ? <GraphPage /> : <Navigate to="/login" />} />
          <Route path="/learn/:conceptId" element={session ? <LearnPage /> : <Navigate to="/login" />} />
          <Route path="/dashboard" element={session ? <DashboardPage /> : <Navigate to="/login" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
