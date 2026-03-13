/**
 * LLM 代理 Edge Function
 * 前端不直接调用 LLM API，通过此 EF 代理（隐藏 API Key）
 */
import { corsHeaders } from '../_shared/cors.ts';

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders });
  }

  // TODO: Phase 2 — 实现 LLM 代理
  // 1. 验证 JWT
  // 2. 根据请求类型选择模型
  // 3. 转发至 OpenRouter/OpenAI/DeepSeek
  // 4. 流式响应

  return new Response(
    JSON.stringify({ message: 'LLM proxy will be implemented in Phase 2' }),
    { headers: { ...corsHeaders, 'Content-Type': 'application/json' } },
  );
});
