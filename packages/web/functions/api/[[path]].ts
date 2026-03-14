// Cloudflare Pages Function: proxy /api/* to the Worker
const WORKER_BASE = 'https://akg-api.audiomagician1.workers.dev';

export const onRequest: PagesFunction = async (context) => {
  const url = new URL(context.request.url);
  const targetUrl = `${WORKER_BASE}${url.pathname}${url.search}`;

  const headers = new Headers(context.request.headers);
  // Remove host header to avoid issues
  headers.delete('host');

  const init: RequestInit = {
    method: context.request.method,
    headers,
  };

  // Forward body for non-GET requests
  if (context.request.method !== 'GET' && context.request.method !== 'HEAD') {
    init.body = context.request.body;
    // @ts-ignore - duplex is needed for streaming body
    init.duplex = 'half';
  }

  const response = await fetch(targetUrl, init);

  // Clone response with CORS headers
  const newHeaders = new Headers(response.headers);
  newHeaders.set('Access-Control-Allow-Origin', '*');

  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders,
  });
};
