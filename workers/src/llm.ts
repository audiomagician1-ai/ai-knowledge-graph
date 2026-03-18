import type { Env, UserLLMConfig } from './types';

const OPENROUTER_BASE = 'https://openrouter.ai/api/v1';
const OPENAI_BASE = 'https://api.openai.com/v1';
const DEEPSEEK_BASE = 'https://api.deepseek.com/v1';

/** SSRF protection — block private/internal URLs (mirrors FastAPI _validate_base_url) */
function validateBaseUrl(url: string): void {
  let parsed: URL;
  try {
    parsed = new URL(url);
  } catch {
    throw new Error(`Invalid base URL: ${url}`);
  }

  // Scheme check
  if (!['http:', 'https:'].includes(parsed.protocol)) {
    throw new Error(`Unsupported scheme: ${parsed.protocol}`);
  }

  const hostname = parsed.hostname.toLowerCase();

  // Block localhost and loopback
  if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '::1') {
    throw new Error('Localhost not allowed');
  }

  // Block cloud metadata endpoints
  if (hostname === 'metadata.google.internal' || hostname === '169.254.169.254') {
    throw new Error('Metadata endpoint not allowed');
  }

  // Block private IP ranges (10.x, 172.16-31.x, 192.168.x)
  const ipMatch = hostname.match(/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/);
  if (ipMatch) {
    const [, a, b] = ipMatch.map(Number);
    if (a === 10 || (a === 172 && b >= 16 && b <= 31) || (a === 192 && b === 168)) {
      throw new Error('Private IP not allowed');
    }
  }
}

/** Normalize well-known provider URLs */
function normalizeProviderUrl(url: string): string {
  if (/^https:\/\/openrouter\.ai(\/.*)?$/i.test(url)) {
    if (/^https:\/\/openrouter\.ai\/api\/v1$/i.test(url)) return url;
    return 'https://openrouter.ai/api/v1';
  }
  return url;
}

interface LLMOptions {
  messages: Array<{ role: string; content: string }>;
  temperature?: number;
  max_tokens?: number;
  stream?: boolean;
}

/**
 * Build the token-limit parameter for the request body.
 * OpenAI's newer models (o1, o3, chatgpt-4o-latest, chatgpt-5 series etc.)
 * require `max_completion_tokens` instead of `max_tokens`.
 */
function tokenLimitParam(model: string, tokens: number): Record<string, number> {
  const m = model.toLowerCase();
  if (/^(o[1-9]|chatgpt-)/.test(m) || /\/(o[1-9]|chatgpt-)/.test(m)) {
    return { max_completion_tokens: tokens };
  }
  return { max_tokens: tokens };
}

/** Default free-tier model (matches FastAPI config.py defaults) */
const DEFAULT_FREE_MODEL = 'stepfun/step-3.5-flash:free';

/** Get the configured model for a given tier, falling back to free default */
function getModelForTier(env: Env, tier: 'dialogue' | 'assessment' | 'simple'): string {
  switch (tier) {
    case 'dialogue': return env.LLM_MODEL_DIALOGUE || DEFAULT_FREE_MODEL;
    case 'assessment': return env.LLM_MODEL_ASSESSMENT || DEFAULT_FREE_MODEL;
    case 'simple': return env.LLM_MODEL_SIMPLE || DEFAULT_FREE_MODEL;
  }
}

function resolveEndpoint(
  env: Env,
  userConfig?: UserLLMConfig | null,
  tier: 'dialogue' | 'assessment' | 'simple' = 'dialogue',
): { baseUrl: string; apiKey: string; model: string } {
  // User-provided key takes priority
  if (userConfig?.api_key) {
    const key = userConfig.api_key;
    const model = userConfig.model || 'gpt-4o';

    if (userConfig.base_url) {
      const cleaned = normalizeProviderUrl(userConfig.base_url.replace(/\/$/, ''));
      validateBaseUrl(cleaned);
      return { baseUrl: cleaned, apiKey: key, model };
    }
    switch (userConfig.provider) {
      case 'deepseek':
        return { baseUrl: DEEPSEEK_BASE, apiKey: key, model: model.includes('/') ? model.split('/').pop()! : model };
      case 'openai':
        return { baseUrl: OPENAI_BASE, apiKey: key, model: model.includes('/') ? model.split('/').pop()! : model };
      case 'custom':
        return { baseUrl: OPENAI_BASE, apiKey: key, model };
      default: // openrouter
        return { baseUrl: OPENROUTER_BASE, apiKey: key, model };
    }
  }

  // Server-side keys fallback — use configured free-tier model
  const serverModel = getModelForTier(env, tier);
  if (env.OPENROUTER_API_KEY) {
    return { baseUrl: OPENROUTER_BASE, apiKey: env.OPENROUTER_API_KEY, model: serverModel };
  }
  if (env.DEEPSEEK_API_KEY) {
    // DeepSeek direct: strip vendor prefix
    const dsModel = serverModel.includes('/') ? serverModel.split('/').pop()! : serverModel;
    return { baseUrl: DEEPSEEK_BASE, apiKey: env.DEEPSEEK_API_KEY, model: dsModel };
  }
  if (env.OPENAI_API_KEY) {
    const oaiModel = serverModel.includes('/') ? serverModel.split('/').pop()! : serverModel;
    return { baseUrl: OPENAI_BASE, apiKey: env.OPENAI_API_KEY, model: oaiModel };
  }

  throw new Error('No LLM API key configured');
}

/** Non-streaming chat completion */
export async function llmChat(
  env: Env,
  opts: LLMOptions,
  userConfig?: UserLLMConfig | null,
  tier: 'dialogue' | 'assessment' | 'simple' = 'dialogue',
): Promise<string> {
  const { baseUrl, apiKey, model } = resolveEndpoint(env, userConfig, tier);

  const res = await fetch(`${baseUrl}/chat/completions`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model,
      messages: opts.messages,
      temperature: opts.temperature ?? 0.7,
      ...tokenLimitParam(model, opts.max_tokens ?? 2048),
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`LLM error ${res.status}: ${text}`);
  }

  const data: any = await res.json();
  return data.choices[0].message.content;
}

/** Streaming chat completion — returns a ReadableStream of SSE */
export function llmChatStream(
  env: Env,
  opts: LLMOptions,
  userConfig?: UserLLMConfig | null,
  tier: 'dialogue' | 'assessment' | 'simple' = 'dialogue',
): ReadableStream {
  const { baseUrl, apiKey, model } = resolveEndpoint(env, userConfig, tier);

  const encoder = new TextEncoder();

  return new ReadableStream({
    async start(controller) {
      try {
        const res = await fetch(`${baseUrl}/chat/completions`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            model,
            messages: opts.messages,
            temperature: opts.temperature ?? 0.75,
            ...tokenLimitParam(model, opts.max_tokens ?? 512),
            stream: true,
          }),
        });

        if (!res.ok) {
          const text = await res.text();
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', content: `⚠️ LLM 错误: ${res.status}` })}\n\n`
          ));
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`
          ));
          controller.close();
          return;
        }

        const reader = res.body!.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let fullContent = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue;
            const payload = line.slice(6).trim();
            if (payload === '[DONE]') continue;
            try {
              const chunk = JSON.parse(payload);
              const delta = chunk.choices?.[0]?.delta;
              if (delta?.content) {
                fullContent += delta.content;
                controller.enqueue(encoder.encode(
                  `data: ${JSON.stringify({ type: 'chunk', content: delta.content })}\n\n`
                ));
              }
            } catch { /* ignore */ }
          }
        }

        controller.enqueue(encoder.encode(
          `data: ${JSON.stringify({ type: 'done', suggest_assess: false, full_content: fullContent })}\n\n`
        ));
      } catch (err) {
        controller.enqueue(encoder.encode(
          `data: ${JSON.stringify({ type: 'chunk', content: '抱歉，我刚才走神了 😅 你能再说一遍吗？' })}\n\n`
        ));
        controller.enqueue(encoder.encode(
          `data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`
        ));
      } finally {
        controller.close();
      }
    },
  });
}
