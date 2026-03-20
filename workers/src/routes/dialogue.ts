import { Hono } from 'hono';
import type { Env, UserLLMConfig } from '../types';
import { llmChat, llmChatStream } from '../llm';
import { FEYNMAN_SYSTEM_PROMPT, GRAPH_CONTEXT_TEMPLATE, ASSESSMENT_SYSTEM_PROMPT, formatPrompt, getAssessmentSupplement, getDomainSupplement } from '../prompts';
// Multi-domain seed data imports
import seedAI from '../../data/seed/ai-engineering/seed_graph.json';
import seedMath from '../../data/seed/mathematics/seed_graph.json';
import seedEnglish from '../../data/seed/english/seed_graph.json';
import seedPhysics from '../../data/seed/physics/seed_graph.json';
import seedProduct from '../../data/seed/product-design/seed_graph.json';
import seedFinance from '../../data/seed/finance/seed_graph.json';
import seedPsychology from '../../data/seed/psychology/seed_graph.json';
import seedPhilosophy from '../../data/seed/philosophy/seed_graph.json';
import seedBiology from '../../data/seed/biology/seed_graph.json';
import seedEconomics from '../../data/seed/economics/seed_graph.json';
import seedWriting from '../../data/seed/writing/seed_graph.json';
import seedGameDesign from '../../data/seed/game-design/seed_graph.json';
import seedLevelDesign from '../../data/seed/level-design/seed_graph.json';

const app = new Hono<{ Bindings: Env }>();

const seedMap: Record<string, any> = {
  'ai-engineering': seedAI, 'mathematics': seedMath, 'english': seedEnglish,
  'physics': seedPhysics, 'product-design': seedProduct, 'finance': seedFinance,
  'psychology': seedPsychology, 'philosophy': seedPhilosophy,
  'biology': seedBiology, 'economics': seedEconomics, 'writing': seedWriting,
  'game-design': seedGameDesign,
  'level-design': seedLevelDesign,
};

function findConceptAcrossDomains(conceptId: string): { seed: any; domain: string } | null {
  for (const [domainId, seed] of Object.entries(seedMap)) {
    if (seed.concepts.find((cc: any) => cc.id === conceptId)) return { seed, domain: domainId };
  }
  return null;
}

function extractLLMConfig(c: any): UserLLMConfig | null {
  const apiKey = (c.req.header('x-llm-api-key') || '').trim();
  if (!apiKey) return null;
  let provider = (c.req.header('x-llm-provider') || 'openrouter').trim().toLowerCase();
  if (!['openrouter', 'openai', 'deepseek', 'custom'].includes(provider)) provider = 'openrouter';
  return {
    provider,
    api_key: apiKey,
    model: c.req.header('x-llm-model')?.trim() || undefined,
    base_url: c.req.header('x-llm-base-url')?.trim() || undefined,
  };
}

function getConceptInfo(conceptId: string) {
  const found = findConceptAcrossDomains(conceptId);
  if (!found) return null;
  const { seed } = found;
  const concept = seed.concepts.find((cc: any) => cc.id === conceptId);
  if (!concept) return null;
  const prereqs: string[] = [], deps: string[] = [], related: string[] = [];
  const idToName: Record<string, string> = {};
  for (const cc of seed.concepts) idToName[cc.id] = cc.name;
  for (const e of seed.edges) {
    if (e.relation_type === 'prerequisite') {
      if (e.target_id === conceptId) prereqs.push(e.source_id);
      if (e.source_id === conceptId) deps.push(e.target_id);
    } else if (e.relation_type === 'related_to') {
      if (e.source_id === conceptId) related.push(e.target_id);
      else if (e.target_id === conceptId) related.push(e.source_id);
    }
  }
  return {
    ...concept,
    prerequisite_names: prereqs.map(p => idToName[p] || p),
    dependent_names: deps.map(d => idToName[d] || d),
    related_names: related.map(r => idToName[r] || r),
  };
}

function buildSystemPrompt(concept: any): string {
  const graphContext = formatPrompt(GRAPH_CONTEXT_TEMPLATE, {
    prerequisites: concept.prerequisite_names?.join(', ') || '无',
    dependents: concept.dependent_names?.join(', ') || '无',
    related: concept.related_names?.join(', ') || '无',
    is_milestone: concept.is_milestone ? '⭐ 是（里程碑节点）' : '否',
  });

  // Domain-specific teaching supplement (registry lookup)
  const domainSupplement = getDomainSupplement(concept.domain_id);

  return formatPrompt(FEYNMAN_SYSTEM_PROMPT, {
    concept_name: concept.name,
    subdomain_name: concept.subdomain_id || '',
    difficulty: String(concept.difficulty || 5),
    content_type: concept.content_type || 'theory',
    graph_context: graphContext + domainSupplement,
  });
}

function getOpening(concept: any): string {
  const name = concept.name;
  const diff = concept.difficulty || 5;
  // Domain-neutral openings — matches BE (socratic.py) and FE (direct-llm.ts) fallback style.
  // Round 78 fix: removed CS-specific wording from low-difficulty opening.
  if (diff <= 3) return `嗨！👋 我听说${name}是很基础但很重要的概念。不过我还不太理解它到底是什么意思。你能用最简单的话给我解释一下吗？`;
  if (diff <= 6) return `嗨！🤔 我最近在学习${name}，感觉挺有意思但又有点复杂。你对这个概念了解多少？能试着用最直白的方式给我讲讲吗？`;
  return `嗨！🧐 ${name}这个话题看起来挺深的，我之前一直没搞明白。听说你对这方面有研究，能帮我从头捋一下吗？先从最核心的概念开始？`;
}

/** POST /dialogue/conversations — create new conversation */
app.post('/conversations', async (c) => {
  const { concept_id } = await c.req.json<{ concept_id: string }>();
  if (!concept_id || concept_id.length > 200) return c.json({ detail: 'Invalid concept_id' }, 422);
  const concept = getConceptInfo(concept_id);
  if (!concept) return c.json({ detail: `概念不存在: ${concept_id}` }, 404);

  const convId = crypto.randomUUID();
  const systemPrompt = buildSystemPrompt(concept);
  const opening = getOpening(concept);
  const db = c.env.DB;
  const now = Date.now() / 1000;

  await db.prepare('INSERT INTO conversations (id, concept_id, concept_name, system_prompt, is_milestone, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .bind(convId, concept_id, concept.name, systemPrompt, concept.is_milestone ? 1 : 0, now, now).run();
  await db.prepare('INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)')
    .bind(convId, 'assistant', opening, now).run();

  return c.json({
    conversation_id: convId,
    concept_id,
    concept_name: concept.name,
    opening_message: opening,
    is_milestone: concept.is_milestone || false,
  });
});

/** POST /dialogue/chat — SSE streaming chat */
app.post('/chat', async (c) => {
  const { conversation_id, message } = await c.req.json<{ conversation_id: string; message: string }>();
  if (!conversation_id) return c.json({ detail: 'conversation_id required' }, 422);
  if (!message || message.length > 10000) return c.json({ detail: 'message required (max 10000 chars)' }, 422);
  const db = c.env.DB;

  const conv = await db.prepare('SELECT * FROM conversations WHERE id = ?').bind(conversation_id).first<any>();
  if (!conv) return c.json({ detail: '会话不存在' }, 404);

  const userConfig = extractLLMConfig(c);
  const hasServerKey = !!(c.env.OPENROUTER_API_KEY || c.env.OPENAI_API_KEY || c.env.DEEPSEEK_API_KEY);

  // Save user message
  const now = Date.now() / 1000;
  await db.prepare('INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)')
    .bind(conversation_id, 'user', message, now).run();

  // No API key at all
  if (!userConfig && !hasServerKey) {
    const fallback = '⚠️ 还没有配置 LLM API Key 哦！请到「设置」页面配置你的 API Key，然后就可以开始对话了。';
    await db.prepare('INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)')
      .bind(conversation_id, 'assistant', fallback, now).run();

    const encoder = new TextEncoder();
    const body = new ReadableStream({
      start(controller) {
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'chunk', content: fallback })}\n\n`));
        controller.enqueue(encoder.encode(`data: ${JSON.stringify({ type: 'done', suggest_assess: false })}\n\n`));
        controller.close();
      }
    });
    return new Response(body, {
      headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive' },
    });
  }

  // Build message history (sliding window: keep last 40 messages, matching FastAPI backend)
  const MAX_MESSAGES = 40;
  const { results: dbMessages } = await db.prepare('SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at').bind(conversation_id).all();
  const msgList = (dbMessages || []).map((m: any) => ({ role: m.role, content: m.content }));
  const windowedMessages = msgList.length > MAX_MESSAGES ? msgList.slice(-MAX_MESSAGES) : msgList;
  const allMessages = [
    { role: 'system', content: conv.system_prompt },
    ...windowedMessages,
  ];

  // Count user turns for suggest_assess
  const userTurns = (dbMessages || []).filter((m: any) => m.role === 'user').length;

  // Stream LLM response
  const stream = llmChatStream(c.env, { messages: allMessages, temperature: 0.75, max_tokens: 512 }, userConfig, 'dialogue');

  // We need to intercept the stream to save the full response
  const encoder = new TextEncoder();
  let fullResponse = '';
  const transformedStream = new ReadableStream({
    async start(controller) {
      const reader = stream.getReader();
      const decoder = new TextDecoder();

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value, { stream: true });
          // Parse each SSE line to collect full content and replace done event
          let hasDoneEvent = false;
          for (const line of text.split('\n')) {
            if (line.startsWith('data: ')) {
              try {
                const payload = JSON.parse(line.slice(6));
                if (payload.type === 'chunk') {
                  fullResponse += payload.content;
                  // When done is in same value, forward chunk individually
                  // (we can't forward raw value as it includes the done event)
                }
                if (payload.type === 'done') {
                  hasDoneEvent = true;
                }
              } catch { /* pass */ }
            }
          }
          if (hasDoneEvent) {
            // Re-encode only the chunk events, then append replaced done
            for (const line of text.split('\n')) {
              if (line.startsWith('data: ')) {
                try {
                  const payload = JSON.parse(line.slice(6));
                  if (payload.type === 'chunk') {
                    controller.enqueue(encoder.encode(`data: ${JSON.stringify(payload)}\n\n`));
                  }
                } catch { /* pass */ }
              }
            }
            controller.enqueue(encoder.encode(
              `data: ${JSON.stringify({ type: 'done', suggest_assess: userTurns >= 4, turn: userTurns })}\n\n`
            ));
          } else {
            controller.enqueue(value);
          }
        }
      } finally {
        // Save assistant response to DB
        if (fullResponse) {
          await db.prepare('INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)')
            .bind(conversation_id, 'assistant', fullResponse, Date.now() / 1000).run();
        }
        controller.close();
      }
    }
  });

  return new Response(transformedStream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'X-Accel-Buffering': 'no',
    },
  });
});

/** POST /dialogue/assess — understanding assessment */
app.post('/assess', async (c) => {
  const { conversation_id } = await c.req.json<{ conversation_id: string }>();
  const db = c.env.DB;

  const conv = await db.prepare('SELECT * FROM conversations WHERE id = ?').bind(conversation_id).first<any>();
  if (!conv) return c.json({ detail: '会话不存在' }, 404);

  const userConfig = extractLLMConfig(c);

  const { results: dbMessages } = await db.prepare('SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at').bind(conversation_id).all();
  const messages = (dbMessages || []).map((m: any) => ({ role: m.role, content: m.content }));
  const userTurns = messages.filter(m => m.role === 'user').length;

  if (userTurns < 2) {
    return c.json({ error: '请至少进行 2 轮对话后再评估', current_turns: userTurns }, 400);
  }

  const conceptName = conv.concept_name;
  const found = findConceptAcrossDomains(conv.concept_id);
  const difficulty = found?.seed.concepts.find((cc: any) => cc.id === conv.concept_id)?.difficulty || 5;
  const domainId = found?.domain || 'ai-engineering';

  const systemPrompt = formatPrompt(ASSESSMENT_SYSTEM_PROMPT, {
    concept_name: conceptName,
    difficulty: String(difficulty),
    domain_assessment_supplement: getAssessmentSupplement(domainId),
  });

  // Truncate dialogue to prevent exceeding LLM context window (matches FastAPI evaluator 8000 char limit)
  let totalChars = 0;
  const MAX_DIALOGUE_CHARS = 8000;
  const dialogueLines: string[] = [];
  // Prioritize recent messages by iterating in reverse, use push+reverse for O(n) (matching FastAPI evaluator.py)
  for (let i = messages.length - 1; i >= 0; i--) {
    const m = messages[i];
    // Role labels match FastAPI evaluator.py: user=学习者, AI=学习伙伴/老师
    const line = `[${m.role === 'user' ? '用户（学习者）' : 'AI（学习伙伴/老师）'}]: ${m.content}`;
    if (totalChars + line.length > MAX_DIALOGUE_CHARS) break;
    dialogueLines.push(line);
    totalChars += line.length;
  }
  dialogueLines.reverse();
  const dialogueText = dialogueLines.join('\n\n');

  try {
    const response = await llmChat(c.env, {
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: `以下是用户在费曼对话中的完整对话记录，请评估用户对「${conceptName}」的理解程度：\n\n${dialogueText}` },
      ],
      temperature: 0.2,
      max_tokens: 1024,
    }, userConfig, 'assessment');

    const result = parseAssessmentJSON(response);
    if (result) {
      if (result.mastered) {
        await db.prepare("UPDATE conversations SET status = 'completed', updated_at = ? WHERE id = ?")
          .bind(Date.now() / 1000, conversation_id).run();
      }
      return c.json({ concept_id: conv.concept_id, concept_name: conceptName, turns: userTurns, ...result });
    }
  } catch { /* fallback */ }

  // Fallback assessment — mastered logic matches standard: overall>=75 && all dims>=60
  const base = Math.min(40 + userTurns * 8, 85);
  const dims = { completeness: base, accuracy: base - 5, depth: base - 10, examples: base - 15 };
  const overall = base - 5;
  const mastered = overall >= 75 && Object.values(dims).every(s => s >= 60);
  return c.json({
    concept_id: conv.concept_id, concept_name: conceptName, turns: userTurns,
    ...dims, overall_score: overall, gaps: ['评估服务暂时不可用'], feedback: `你进行了 ${userTurns} 轮对话，表现不错！`,
    mastered,
  });
});

/** Validate and normalize assessment result — clamp scores, recalculate mastered (matches FastAPI evaluator.validate_result) */
function validateAssessment(result: any): any {
  for (const k of ['completeness', 'accuracy', 'depth', 'examples', 'overall_score']) {
    const v = result[k];
    const raw = (v === null || v === undefined) ? NaN : Number(v);
    result[k] = Math.max(0, Math.min(100, Math.round(Number.isFinite(raw) ? raw : 50)));
  }
  // Always recalculate mastered from scores (don't trust LLM's mastered field)
  result.mastered = result.overall_score >= 75 && ['completeness', 'accuracy', 'depth', 'examples'].every((k: string) => result[k] >= 60);
  result.gaps = Array.isArray(result.gaps) ? result.gaps : [];
  result.feedback = result.feedback || '评估完成';
  return result;
}

function parseAssessmentJSON(text: string): any | null {
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

export default app;
