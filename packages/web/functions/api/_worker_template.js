// Cloudflare Pages Advanced Mode _worker.js
// Proxies /api/* requests to the Cloudflare Worker backend

const WORKER_BASE = 'https://akg-api.audiomagician1.workers.dev';

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Only proxy /api/* paths
    if (!url.pathname.startsWith('/api/')) {
      // Fall through to static assets
      return env.ASSETS.fetch(request);
    }

    const targetUrl = `${WORKER_BASE}${url.pathname}${url.search}`;
    const headers = new Headers(request.headers);
    headers.delete('host');

    const init = {
      method: request.method,
      headers,
    };

    if (request.method !== 'GET' && request.method !== 'HEAD') {
      init.body = request.body;
      init.duplex = 'half';
    }

    const response = await fetch(targetUrl, init);

    // Forward response with CORS headers
    const newHeaders = new Headers(response.headers);
    newHeaders.set('Access-Control-Allow-Origin', '*');
    newHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    newHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-LLM-Provider, X-LLM-API-Key, X-LLM-Model, X-LLM-Base-URL');

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: newHeaders });
    }

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders,
    });
  },
};
