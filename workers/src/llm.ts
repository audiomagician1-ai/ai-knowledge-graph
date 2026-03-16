import type { Env, UserLLMConfig } from './types';

const OPENROUTER_BASE = 'https://openrouter.ai/api/v1';
const OPENAI_BASE = 'https://api.openai.com/v1';
const DEEPSEEK_BASE = 'https://api.deepseek.com/v1';

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

function resolveEndpoint(
  env: Env,
  userConfig?: UserLLMConfig | null,
): { baseUrl: string; apiKey: string; model: string } {
  // User-provided key takes priority
  if (userConfig?.api_key) {
    const key = userConfig.api_key;
    const model = userConfig.model || 'gpt-4o';

    if (userConfig.base_url) {
      return { baseUrl: normalizeProviderUrl(userConfig.base_url.replace(/\/$/, '')), apiKey: key, model };
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

  // Server-side keys fallback
  if (env.OPENROUTER_API_KEY) {
    return { baseUrl: OPENROUTER_BASE, apiKey: env.OPENROUTER_API_KEY, model: 'openai/gpt-4o' };
  }
  if (env.DEEPSEEK_API_KEY) {
    return { baseUrl: DEEPSEEK_BASE, apiKey: env.DEEPSEEK_API_KEY, model: 'deepseek-chat' };
  }
  if (env.OPENAI_API_KEY) {
    return { baseUrl: OPENAI_BASE, apiKey: env.OPENAI_API_KEY, model: 'gpt-4o' };
  }

  throw new Error('No LLM API key configured');
}

/** Non-streaming chat completion */
export async function llmChat(
  env: Env,
  opts: LLMOptions,
  userConfig?: UserLLMConfig | null,
): Promise<string> {
  const { baseUrl, apiKey, model } = resolveEndpoint(env, userConfig);

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
      max_tokens: opts.max_tokens ?? 2048,
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
): ReadableStream {
  const { baseUrl, apiKey, model } = resolveEndpoint(env, userConfig);

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
            max_tokens: opts.max_tokens ?? 512,
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
