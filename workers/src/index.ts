import { Hono } from 'hono';
import { cors } from 'hono/cors';
import type { Env } from './types';
import graphRoutes from './routes/graph';
import learningRoutes from './routes/learning';
import dialogueRoutes from './routes/dialogue';

const app = new Hono<{ Bindings: Env }>();

// CORS — allow Cloudflare Pages domain + local dev
// credentials:true requires specific origin (not wildcard), so only trusted origins get CORS headers
// Origin matching uses URL parsing to prevent bypass (e.g. evil-localhost.com matching "localhost")
app.use('*', cors({
  origin: (origin) => {
    if (!origin) return '';
    let hostname: string;
    try {
      hostname = new URL(origin).hostname;
    } catch {
      return '';
    }
    // Allow local dev (exact hostname match, not substring)
    if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1') return origin;
    // Allow Cloudflare Pages/Workers domains (suffix match on parsed hostname)
    if (hostname.endsWith('.pages.dev') || hostname.endsWith('.workers.dev')) return origin;
    // Untrusted origins: return empty string (no CORS headers, request blocked by browser)
    return '';
  },
  allowHeaders: [
    'Content-Type', 'Authorization',
    'X-LLM-Provider', 'X-LLM-API-Key', 'X-LLM-Model', 'X-LLM-Base-URL',
  ],
  allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  credentials: true,
}));

// Health check
app.get('/api/health', (c) => c.json({ status: 'ok', version: '0.1.0', runtime: 'cloudflare-workers' }));

// Route groups
app.route('/api/graph', graphRoutes);
app.route('/api/learning', learningRoutes);
app.route('/api/dialogue', dialogueRoutes);

// 404 fallback for API routes
app.all('/api/*', (c) => c.json({ detail: 'Not found' }, 404));

export default app;
