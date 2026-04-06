import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { initPerfMonitor } from './lib/utils/perf-monitor';
import './styles/globals.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

// Start collecting performance metrics after initial render
requestIdleCallback?.(() => initPerfMonitor()) ?? setTimeout(() => initPerfMonitor(), 1000);
