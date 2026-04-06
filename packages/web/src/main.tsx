import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import { initPerfMonitor } from './lib/utils/perf-monitor';
import { initCapacitor } from './lib/utils/capacitor';
import './styles/globals.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);

// Initialize Capacitor plugins (no-op on web, configures native shell on mobile)
initCapacitor();

// Start collecting performance metrics after initial render
requestIdleCallback?.(() => initPerfMonitor()) ?? setTimeout(() => initPerfMonitor(), 1000);
