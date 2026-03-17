import { Hono } from 'hono';
import { cors } from 'hono/cors';
import type { Env } from './types';
import graphRoutes from './routes/graph';
import learningRoutes from './routes/learning';
import dialogueRoutes from './routes/dialogue';

const app = new Hono<{ Bindings: Env }>();

// CORS — allow Cloudflare Pages domain + local dev
// Note: credentials:true requires specific origin (not wildcard '*')
// Unknown origins get the request origin echoed back without credentials
app.use('*', cors({
  origin: (origin) => {
    if (!origin) return '';
    // Allow any localhost, *.pages.dev, and custom domains
    if (
      origin.includes('localhost') ||
      origin.includes('127.0.0.1') ||
      origin.endsWith('.pages.dev') ||
      origin.endsWith('.workers.dev')
    ) return origin;
    // Non-matching origins: echo origin but without credentials
    return origin;
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
