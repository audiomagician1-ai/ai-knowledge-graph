/**
 * Direct LLM client — calls LLM API directly from the browser.
 * Used when the user enables "direct mode" for intranet/private LLM endpoints
 * that are not reachable from Cloudflare Workers.
 */

import { useSettingsStore, PROVIDER_INFO, resolveBaseUrl, getDefaultModel } from './store/settings';
import { useGraphStore } from './store/graph';
import { createLogger } from '@/lib/utils/logger';
import type { GraphNode } from '@akg/shared';

const log = createLogger('DirectLLM');
import { FEYNMAN_SYSTEM_PROMPT, ASSESSMENT_SYSTEM_PROMPT, getAssessmentSupplement, getDomainSupplement } from './direct-llm-prompts';

// Re-export for backward compatibility (test imports)
export { getAssessmentSupplement, getDomainSupplement } from './direct-llm-prompts';

// ─── Constants ───

/** Max messages to send to LLM (sliding window to prevent token overflow) */
const MAX_CONTEXT_MESSAGES = 20;

/**
 * Build the token-limit parameter for the request body.
 * OpenAI's newer models (o1, o3, gpt-5+, chatgpt-4o-latest, chatgpt-5 series etc.)
 * require `max_completion_tokens` instead of `max_tokens`.
 */
export function tokenLimitParam(model: string, tokens: number): Record<string, number> {
  const m = model.toLowerCase();
  // o1/o3 reasoning, chatgpt-* series, gpt-5+ series (bare or vendor-prefixed)
  if (/(?:^|\/)(?:o[1-9]|chatgpt-|gpt-(?:[5-9]|\d{2,}))/.test(m)) {
    return { max_completion_tokens: tokens };
  }
  return { max_tokens: tokens };
}

// ─── Helpers ───

/** Parse ```choices JSON block from LLM response content */
export function parseChoicesFromContent(text: string): { content: string; choices: Array<{ id: string; text: string; type: string }> } {
  if (!text) return { content: '', choices: [] };

  // Try to find ```choices ... ``` block
  const choicesPattern = /```choices\s*\n([\s\S]*?)```/;
  const match = text.match(choicesPattern);

  if (match) {
    const choicesJson = match[1].trim();
    const content = text.slice(0, match.index).trim();
    try {
      const parsed = JSON.parse(choicesJson);
      if (Array.isArray(parsed) && parsed.length >= 2) {
        const valid = parsed
          .filter((c: any) => c && typeof c.text === 'string' && c.text.trim())
          .slice(0, 4)
          .map((c: any, i: number) => ({
            id: c.id || `opt-${i + 1}`,
            text: String(c.text).slice(0, 60),
            type: ['explore', 'answer', 'action', 'level'].includes(c.type) ? c.type : 'explore',
          }));
        if (valid.length >= 2) return { content, choices: valid };
      }
    } catch { /* fallback to no choices */ }
    return { content, choices: [] };
  }

  // Fallback: detect trailing bullet-point options when LLM doesn't use ```choices block
  // Patterns: "你想了解：\n- option1？\n- option2？" or similar
  const fallbackChoices = parseBulletChoices(text);
  if (fallbackChoices) return fallbackChoices;

  return { content: text.trim(), choices: [] };
}

/** Fallback parser: extract choices from trailing bullet-point lists.
 *  Detects patterns like:
 *  - "你想了解：\n- xxx？\n- yyy？\n- zzz？"
 *  - "你可以选择：\n· xxx\n· yyy"
 *  - End-of-message bullet list with question marks
 */
function parseBulletChoices(text: string): { content: string; choices: Array<{ id: string; text: string; type: string }> } | null {
  // Match trailing section with bullet points (-, ·, •, *, 1. 2. etc.)
  // The trigger line is optional ("你想了解：" etc.)
  const trailingBulletPattern = /(?:^|\n)((?:你想(?:了解|知道)|接下来|你(?:可以)?选择|你(?:更)?想)[^\n]{0,20}[：:]\s*\n)?((?:\s*[-·•*]\s+.+(?:\n|$)){2,5})\s*$/;
  const match = text.match(trailingBulletPattern);
  if (!match) return null;

  const bulletSection = match[2];
  const triggerLine = match[1] || '';
  const bullets = bulletSection
    .split('\n')
    .map(l => l.replace(/^\s*[-·•*]\s+/, '').trim())
    .filter(l => l.length >= 2 && l.length <= 60);

  if (bullets.length < 2) return null;

  // Remove the bullet section (and trigger line) from visible content
  const endIdx = text.lastIndexOf(triggerLine + bulletSection);
  const content = (endIdx > 0 ? text.slice(0, endIdx) : text.replace(triggerLine + bulletSection, '')).trim();

  const choices = bullets.slice(0, 4).map((b, i) => ({
    id: `opt-${i + 1}`,
    text: b.replace(/[？?]$/, ''),
    type: b.includes('了解') || b.includes('什么') || b.includes('如何') || b.includes('为什么') ? 'explore' as const : 'answer' as const,
  }));

  return { content, choices };
}

/** Apply sliding window to messages array — keep system prompt separate */
export function windowMessages(messages: Array<{ role: string; content: string }>): Array<{ role: string; content: string }> {
  if (messages.length <= MAX_CONTEXT_MESSAGES) return messages;
  // Keep the first message (opening context) + truncation notice + last (N-2) messages
  const firstMsg = messages[0];
  const recent = messages.slice(-(MAX_CONTEXT_MESSAGES - 2));
  return [firstMsg, { role: 'system', content: '[对话历史已截断，以下为最近的对话记录]' }, ...recent];
}

function fmt(template: string, vars: Record<string, string>): string {
  let result = template;
  for (const [key, value] of Object.entries(vars)) {
    result = result.replaceAll(`{${key}}`, value);
  }
  return result;
}

function resolveEndpoint(): { baseUrl: string; apiKey: string; model: string } {
  const { llmConfig } = useSettingsStore.getState();
  const key = llmConfig.apiKey;
  // Use provider-appropriate default model
  const model = llmConfig.model || getDefaultModel(llmConfig.provider);

  const rawBase = llmConfig.baseUrl || PROVIDER_INFO[llmConfig.provider].defaultBase;
  const baseUrl = resolveBaseUrl(rawBase, !!llmConfig.useProxy);
  return { baseUrl, apiKey: key, model };
}

/** Get concept info + graph context from the loaded graph store */
function getConceptContext(conceptId: string) {
  const { graphData } = useGraphStore.getState();
  if (!graphData) return null;

  const node = graphData.nodes.find(n => n.id === conceptId);
  if (!node) return null;

  // Build graph context
  const prereqs: string[] = [];
  const deps: string[] = [];
  const related: string[] = [];
  const idToLabel: Record<string, string> = {};
  for (const n of graphData.nodes) idToLabel[n.id] = n.label;

  for (const e of graphData.edges) {
    if (e.relation_type === 'prerequisite') {
      if (e.target === conceptId) prereqs.push(idToLabel[e.source] || e.source);
      if (e.source === conceptId) deps.push(idToLabel[e.target] || e.target);
    } else {
      if (e.source === conceptId) related.push(idToLabel[e.target] || e.target);
      else if (e.target === conceptId) related.push(idToLabel[e.source] || e.source);
    }
  }

  return { node, prereqs, deps, related };
}

// Domain-specific teaching supplement registry — synced from apps/api/engines/dialogue/prompts/feynman_system.py

function buildSystemPrompt(node: GraphNode, prereqs: string[], deps: string[], related: string[]): string {
  const graphContext = `## 图谱上下文（帮助你理解这个概念在知识体系中的位置）
- **先修概念**: ${prereqs.join(', ') || '无'}
- **后续概念**: ${deps.join(', ') || '无'}
- **相关概念**: ${related.join(', ') || '无'}
- **是否为里程碑**: ${node.is_milestone ? '⭐ 是（里程碑节点）' : '否'}
`;

  // Domain-specific supplement (registry lookup)
  const domainId = 'domain_id' in node ? (node as { domain_id?: string }).domain_id : undefined;
  const domainSupplement = getDomainSupplement(domainId);

  return fmt(FEYNMAN_SYSTEM_PROMPT, {
    concept_name: node.label,
    subdomain_name: node.subdomain_id || '',
    difficulty: String(node.difficulty || 5),
    content_type: node.content_type || 'theory',
    graph_context: graphContext + domainSupplement,
  });
}

/** Opening user prompt — triggers LLM to generate Phase 1 probe */
const OPENING_USER_PROMPT = '开始学习「{concept_name}」';

/** Fallback opening when LLM call fails */
function getFallbackOpening(name: string): {
  text: string;
  choices: Array<{ id: string; text: string; type: string }>;
} {
  return {
    text: `👋 今天我们一起来探索「${name}」！\n\n这是一个很有意思的概念，让我先简单介绍一下，然后我们一步步深入。\n\n你之前对 ${name} 有了解吗？`,
    choices: [
      { id: 'opt-1', text: '完全没听说过', type: 'level' },
      { id: 'opt-2', text: '听过但说不太清楚', type: 'level' },
      { id: 'opt-3', text: '有一些了解，想深入', type: 'level' },
      { id: 'opt-4', text: '比较熟悉，直接进阶', type: 'level' },
    ],
  };
}

// ─── Public API ───

export interface DirectConversation {
  conversationId: string;
  conceptId: string;
  conceptName: string;
  systemPrompt: string;
  messages: Array<{ role: string; content: string }>;
  isMilestone: boolean;
}

// In-memory conversation storage for direct mode (max 20 conversations)
const directConversations = new Map<string, DirectConversation>();
const MAX_DIRECT_CONVERSATIONS = 20;

/** Clean up direct conversations map — evict oldest when exceeding limit */
function pruneDirectConversations(): void {
  if (directConversations.size <= MAX_DIRECT_CONVERSATIONS) return;
  const entries = Array.from(directConversations.entries());
  // Map preserves insertion order — delete oldest entries
  const toRemove = entries.slice(0, entries.length - MAX_DIRECT_CONVERSATIONS);
  for (const [key] of toRemove) directConversations.delete(key);
}

/** Clear a specific direct conversation (called by dialogue store reset) */
export function clearDirectConversation(conversationId: string): void {
  directConversations.delete(conversationId);
}

/** Clear all direct conversations */
export function clearAllDirectConversations(): void {
  directConversations.clear();
}

/** Create a new conversation in direct mode — LLM generates opening + choices */
export async function directCreateConversation(conceptId: string): Promise<{
  conversation_id: string;
  concept_id: string;
  concept_name: string;
  opening_message: string;
  opening_choices: Array<{ id: string; text: string; type: string }> | null;
  is_milestone: boolean;
} | null> {
  const ctx = getConceptContext(conceptId);
  if (!ctx) return null;

  const { node, prereqs, deps, related } = ctx;
  const systemPrompt = buildSystemPrompt(node, prereqs, deps, related);
  const convId = crypto.randomUUID();

  // Try to get LLM-generated opening with choices
  let openingText = '';
  let openingChoices: Array<{ id: string; text: string; type: string }> | null = null;

  try {
    const { baseUrl, apiKey, model } = resolveEndpoint();
    const userMsg = OPENING_USER_PROMPT.replace('{concept_name}', node.label);

    const res = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMsg },
        ],
        temperature: 0.8,
        ...tokenLimitParam(model, 2048),
      }),
      signal: AbortSignal.timeout(15000), // 15s timeout
    });

    // Guard: wrong URL may return 200 + HTML instead of JSON
    const openCT = res.headers.get('content-type') || '';
    if (res.ok && !openCT.includes('application/json')) {
      log.warn('LLM returned non-JSON content-type', { contentType: openCT });
    } else if (res.ok) {
      const data: any = await res.json();
      const raw = data.choices?.[0]?.message?.content || '';
      if (raw) {
        const parsed = parseChoicesFromContent(raw);
        openingText = parsed.content;
        openingChoices = parsed.choices.length >= 2 ? parsed.choices : null;
      } else {
        throw new Error('Empty LLM response');
      }
    } else {
      throw new Error(`LLM error ${res.status}`);
    }
  } catch {
    // Fallback to hardcoded opening
    const fallback = getFallbackOpening(node.label);
    openingText = fallback.text;
    openingChoices = fallback.choices;
  }

  const conv: DirectConversation = {
    conversationId: convId,
    conceptId,
    conceptName: node.label,
    systemPrompt,
    messages: [{ role: 'assistant', content: openingText }],
    isMilestone: node.is_milestone,
  };
  directConversations.set(convId, conv);
  pruneDirectConversations();

  return {
    conversation_id: convId,
    concept_id: conceptId,
    concept_name: node.label,
    opening_message: openingText,
    opening_choices: openingChoices,
    is_milestone: node.is_milestone,
  };
}

/** Stream chat in direct mode — returns a ReadableStream of SSE-like events */
export function directChatStream(
  conversationId: string,
  userMessage: string,
  signal?: AbortSignal,
): ReadableStream<Uint8Array> {
  const conv = directConversations.get(conversationId);
  const encoder = new TextEncoder();

  if (!conv) {
    return new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'chunk', content: '⚠️ 会话不存在' })}\n\n`));
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`));
        controller.close();
      }
    });
  }

  // Save user message
  conv.messages.push({ role: 'user', content: userMessage });
  const userTurns = conv.messages.filter(m => m.role === 'user').length;

  const { baseUrl, apiKey, model } = resolveEndpoint();
  // Apply sliding window to prevent token overflow
  const windowedMsgs = windowMessages(conv.messages);

  // V2: After 2+ exchanges, inject a format reminder to reinforce choices output.
  // Stored assistant messages have choices stripped (clean content), so the LLM
  // loses the pattern after several turns without this reminder.
  const CHOICES_REMINDER = '\n\n(记住：回复末尾必须附带 ```choices JSON 代码块，包含 2-4 个选项。)';
  const needReminder = windowedMsgs.length >= 4;
  const messagesWithReminder = needReminder
    ? windowedMsgs.map((m, i) =>
        (i === windowedMsgs.length - 1 && m.role === 'user')
          ? { ...m, content: m.content + CHOICES_REMINDER }
          : m
      )
    : windowedMsgs;

  const allMessages = [
    { role: 'system', content: conv.systemPrompt },
    ...messagesWithReminder,
  ];

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
            messages: allMessages,
            temperature: 0.75,
            ...tokenLimitParam(model, 2048),
            stream: true,
          }),
          signal,
        });

        if (!res.ok) {
          const text = await res.text().catch(() => '');
          // Build user-friendly error message for common HTTP status codes
          let friendlyMsg = `⚠️ LLM 错误 ${res.status}: `;
          if (res.status === 401) {
            friendlyMsg += 'API Key 无效或已过期，请在设置中检查 Key 是否正确。';
          } else if (res.status === 402) {
            friendlyMsg += 'API 账户余额不足，请前往服务商充值后重试。';
          } else if (res.status === 429) {
            friendlyMsg += '请求过于频繁，请稍后再试。';
          } else if (res.status === 404) {
            friendlyMsg += '模型不存在或 Base URL 错误，请检查设置。';
          } else {
            friendlyMsg += text.slice(0, 200);
          }
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', content: friendlyMsg })}\n\n`
          ));
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`
          ));
          controller.close();
          return;
        }

        // Guard: wrong URL may return 200 + HTML instead of SSE/JSON
        const streamCT = res.headers.get('content-type') || '';
        if (!streamCT.includes('text/event-stream') && !streamCT.includes('application/json')) {
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', content: `⚠️ LLM 返回了非预期的 content-type: ${streamCT}，请检查 Base URL 设置。` })}\n\n`
          ));
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`
          ));
          controller.close();
          return;
        }

        if (!res.body) {
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', content: '⚠️ LLM 返回了空响应体' })}\n\n`
          ));
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`
          ));
          controller.close();
          return;
        }
        const reader = res.body.getReader();
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

        // Parse choices from response and save clean content
        if (fullContent) {
          const parsed = parseChoicesFromContent(fullContent);
          // Store clean content (without choices block) for conversation history
          conv.messages.push({ role: 'assistant', content: parsed.content || fullContent });
          // M-02 fix: Cap conversation messages to prevent unbounded memory growth
          if (conv.messages.length > MAX_CONTEXT_MESSAGES * 2) {
            conv.messages = [conv.messages[0], ...conv.messages.slice(-(MAX_CONTEXT_MESSAGES * 2 - 1))];
          }

          // Send choices event if parsed successfully
          if (parsed.choices.length >= 2) {
            controller.enqueue(encoder.encode(
              `data: ${JSON.stringify({ type: 'choices', choices: parsed.choices })}\n\n`
            ));
          }
        }

        controller.enqueue(encoder.encode(
          `data: ${JSON.stringify({ type: 'done', suggest_assess: userTurns >= 4, turn: userTurns })}\n\n`
        ));
      } catch (err) {
        if (err instanceof DOMException && err.name === 'AbortError') {
          // Intentional cancellation
        } else {
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', content: '抱歉，我刚才走神了 😅 你能再说一遍吗？' })}\n\n`
          ));
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`
          ));
        }
      } finally {
        controller.close();
      }
    }
  });
}

/** Assess understanding in direct mode */
export async function directAssess(conversationId: string): Promise<Record<string, unknown>> {
  const conv = directConversations.get(conversationId);
  if (!conv) return { error: '会话不存在' };

  const userTurns = conv.messages.filter(m => m.role === 'user').length;
  if (userTurns < 2) return { error: '请至少进行 2 轮对话后再评估', current_turns: userTurns };

  const ctx = getConceptContext(conv.conceptId);
  const difficulty = ctx?.node.difficulty || 5;
  const domainId = ctx?.node && 'domain_id' in ctx.node ? (ctx.node as { domain_id?: string }).domain_id : undefined;

  const systemPrompt = fmt(ASSESSMENT_SYSTEM_PROMPT, {
    concept_name: conv.conceptName,
    difficulty: String(difficulty),
    domain_assessment_supplement: getAssessmentSupplement(domainId),
  });

  // Truncate dialogue to prevent exceeding LLM context window
  // (matches FastAPI evaluator 8000 char limit and Workers dialogue.ts)
  // Role labels match FastAPI evaluator.py: user=学习者, AI=学习伙伴/老师
  const MAX_DIALOGUE_CHARS = 8000;
  let totalChars = 0;
  const dialogueLines: string[] = [];
  // Prioritize recent messages by iterating in reverse, use push+reverse for O(n)
  for (let i = conv.messages.length - 1; i >= 0; i--) {
    const m = conv.messages[i];
    const line = `[${m.role === 'user' ? '用户（学习者）' : 'AI（学习伙伴/老师）'}]: ${m.content}`;
    if (totalChars + line.length > MAX_DIALOGUE_CHARS) break;
    dialogueLines.push(line);
    totalChars += line.length;
  }
  dialogueLines.reverse();
  const dialogueText = dialogueLines.join('\n\n');

  const { baseUrl, apiKey, model } = resolveEndpoint();

  try {
    // m-07 fix: Add timeout to prevent indefinite "评估中..." UI state
    const res = await fetch(`${baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: `以下是用户在费曼对话中的完整对话记录，请评估用户对「${conv.conceptName}」的理解程度：\n\n${dialogueText}` },
        ],
        temperature: 0.2,
        ...tokenLimitParam(model, 1024),
      }),
      signal: AbortSignal.timeout(30_000),
    });

    if (!res.ok) throw new Error(`LLM error ${res.status}`);
    // Guard: wrong URL may return 200 + HTML instead of JSON
    const evalCT = res.headers.get('content-type') || '';
    if (!evalCT.includes('application/json')) {
      throw new Error(`LLM returned non-JSON (${evalCT}). Check your Base URL.`);
    }
    const data: any = await res.json();
    const text = data.choices?.[0]?.message?.content || '';

    // Parse assessment JSON
    const result = parseAssessmentJSON(text);
    if (result) {
      return { concept_id: conv.conceptId, concept_name: conv.conceptName, turns: userTurns, ...result };
    }
  } catch { /* fallback */ }

  // Fallback — mastered logic must match backend evaluator._validate_result:
  // overall_score >= 75 AND all dimensions >= 60
  const base = Math.min(40 + userTurns * 8, 85);
  const dims = { completeness: base, accuracy: base - 5, depth: base - 10, examples: base - 15 };
  const overall = base - 5;
  const mastered = overall >= 75 && Object.values(dims).every(s => s >= 60);
  return {
    concept_id: conv.conceptId, concept_name: conv.conceptName, turns: userTurns,
    ...dims, overall_score: overall,
    gaps: ['评估服务暂时不可用'], feedback: `你进行了 ${userTurns} 轮对话，表现不错！`,
    mastered,
  };
}

/** Validate and normalize assessment result — clamp scores, recalculate mastered
 *  (matches FastAPI evaluator.validate_result and Workers validateAssessment) */
function validateAssessment(result: any): any {
  for (const k of ['completeness', 'accuracy', 'depth', 'examples', 'overall_score']) {
    const v = result[k];
    const raw = (v === null || v === undefined) ? NaN : Number(v);
    result[k] = Math.max(0, Math.min(100, Math.round(Number.isFinite(raw) ? raw : 50)));
  }
  result.mastered = result.overall_score >= 75 && ['completeness', 'accuracy', 'depth', 'examples'].every((k: string) => result[k] >= 60);
  result.gaps = Array.isArray(result.gaps) ? result.gaps : [];
  result.feedback = result.feedback || '评估完成';
  return result;
}

export function parseAssessmentJSON(text: string): any | null {
  try { return validateAssessment(JSON.parse(text)); } catch { /* */ }
  if (text.includes('```json')) {
    const start = text.indexOf('```json') + 7;
    const end = text.indexOf('```', start);
    try { return validateAssessment(JSON.parse(text.slice(start, end).trim())); } catch { /* */ }
  }
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}') + 1;
  if (start >= 0 && end > start) {
    try { return validateAssessment(JSON.parse(text.slice(start, end))); } catch { /* */ }
  }
  return null;
}
