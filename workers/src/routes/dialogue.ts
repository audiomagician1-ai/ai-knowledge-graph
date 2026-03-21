import { Hono } from 'hono';
import type { Env, UserLLMConfig } from '../types';
import { llmChat, llmChatStream } from '../llm';
import { FEYNMAN_SYSTEM_PROMPT, GRAPH_CONTEXT_TEMPLATE, ASSESSMENT_SYSTEM_PROMPT, formatPrompt, getAssessmentSupplement, getDomainSupplement, parseChoicesFromContent } from '../prompts';
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
import seedGameEngine from '../../data/seed/game-engine/seed_graph.json';
import seedSoftwareEngineering from '../../data/seed/software-engineering/seed_graph.json';
import seedComputerGraphics from '../../data/seed/computer-graphics/seed_graph.json';
import seed3DArt from '../../data/seed/3d-art/seed_graph.json';
import seedConceptDesign from '../../data/seed/concept-design/seed_graph.json';
import seedAnimation from '../../data/seed/animation/seed_graph.json';
import seedTechnicalArt from '../../data/seed/technical-art/seed_graph.json';
import seedVfx from '../../data/seed/vfx/seed_graph.json';
import seedGameAudioMusic from '../../data/seed/game-audio-music/seed_graph.json';
import seedGameUiUx from '../../data/seed/game-ui-ux/seed_graph.json';
import seedNarrativeDesign from '../../data/seed/narrative-design/seed_graph.json';
import seedMultiplayerNetwork from '../../data/seed/multiplayer-network/seed_graph.json';
import seedGameAudioSfx from '../../data/seed/game-audio-sfx/seed_graph.json';
import seedGamePublishing from '../../data/seed/game-publishing/seed_graph.json';
import seedGameLiveOps from '../../data/seed/game-live-ops/seed_graph.json';
import seedGameQa from '../../data/seed/game-qa/seed_graph.json';
import seedGameProduction from '../../data/seed/game-production/seed_graph.json';

const app = new Hono<{ Bindings: Env }>();

const seedMap: Record<string, any> = {
  'ai-engineering': seedAI, 'mathematics': seedMath, 'english': seedEnglish,
  'physics': seedPhysics, 'product-design': seedProduct, 'finance': seedFinance,
  'psychology': seedPsychology, 'philosophy': seedPhilosophy,
  'biology': seedBiology, 'economics': seedEconomics, 'writing': seedWriting,
  'game-design': seedGameDesign,
  'level-design': seedLevelDesign,
  'game-engine': seedGameEngine,
  'software-engineering': seedSoftwareEngineering,
  'computer-graphics': seedComputerGraphics,
  '3d-art': seed3DArt,
  'concept-design': seedConceptDesign,
  'animation': seedAnimation,
  'technical-art': seedTechnicalArt,
  'vfx': seedVfx,
  'game-audio-music': seedGameAudioMusic,
  'game-ui-ux': seedGameUiUx,
  'narrative-design': seedNarrativeDesign,
  'multiplayer-network': seedMultiplayerNetwork,
  'game-audio-sfx': seedGameAudioSfx,
  'game-publishing': seedGamePublishing,
  'game-live-ops': seedGameLiveOps,
  'game-qa': seedGameQa,
  'game-production': seedGameProduction,
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

/** Fallback opening when LLM is unavailable (matches FastAPI socratic.py and direct-llm.ts) */
function getFallbackOpening(concept: any): { text: string; choices: Array<{ id: string; text: string; type: string }> } {
  const name = concept.name;
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

/** POST /dialogue/conversations — create new conversation (V2: LLM opening + choices) */
app.post('/conversations', async (c) => {
  const { concept_id } = await c.req.json<{ concept_id: string }>();
  if (!concept_id || concept_id.length > 200) return c.json({ detail: 'Invalid concept_id' }, 422);
  const concept = getConceptInfo(concept_id);
  if (!concept) return c.json({ detail: `概念不存在: ${concept_id}` }, 404);

  const convId = crypto.randomUUID();
  const systemPrompt = buildSystemPrompt(concept);
  const db = c.env.DB;
  const now = Date.now() / 1000;

  // V2: Try LLM-generated opening with choices
  let openingText = '';
  let openingChoices: Array<{ id: string; text: string; type: string }> | null = null;
  const userConfig = extractLLMConfig(c);
  const hasServerKey = !!(c.env.OPENROUTER_API_KEY || c.env.OPENAI_API_KEY || c.env.DEEPSEEK_API_KEY);

  if (userConfig || hasServerKey) {
    try {
      const raw = await llmChat(c.env, {
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: `开始学习「${concept.name}」` },
        ],
        temperature: 0.8,
        max_tokens: 2048,
      }, userConfig, 'dialogue');

      const parsed = parseChoicesFromContent(raw);
      openingText = parsed.content;
      openingChoices = parsed.choices.length >= 2 ? parsed.choices : null;
    } catch {
      // Fallback on LLM failure
    }
  }

  // Fallback if LLM failed or no key
  if (!openingText) {
    const fallback = getFallbackOpening(concept);
    openingText = fallback.text;
    openingChoices = fallback.choices;
  }

  await db.prepare('INSERT INTO conversations (id, concept_id, concept_name, system_prompt, is_milestone, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)')
    .bind(convId, concept_id, concept.name, systemPrompt, concept.is_milestone ? 1 : 0, now, now).run();
  await db.prepare('INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)')
    .bind(convId, 'assistant', openingText, now).run();

  return c.json({
    conversation_id: convId,
    concept_id,
    concept_name: concept.name,
    opening_message: openingText,
    opening_choices: openingChoices,
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

  // Build message history (sliding window: keep first message + truncation notice + last N)
  const MAX_MESSAGES = 40;
  const { results: dbMessages } = await db.prepare('SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at').bind(conversation_id).all();
  const msgList = (dbMessages || []).map((m: any) => ({ role: m.role, content: m.content }));
  let windowedMessages: typeof msgList;
  if (msgList.length > MAX_MESSAGES) {
    // Keep the first message (opening context) + truncation notice + last (N-2) messages
    const firstMsg = msgList.slice(0, 1);
    const recent = msgList.slice(-(MAX_MESSAGES - 2));
    windowedMessages = [...firstMsg, { role: 'system', content: '[对话历史已截断，以下为最近的对话记录]' }, ...recent];
  } else {
    windowedMessages = msgList;
  }
  // V2: Inject a format reminder before the last user message to reinforce choices output.
  // After several turns, LLM tends to "forget" the system prompt instruction about ```choices blocks
  // because the stored assistant messages have choices stripped (clean content).
  const CHOICES_REMINDER = '(记住：回复末尾必须附带 ```choices JSON 代码块，包含 2-4 个选项。)';
  const needReminder = windowedMessages.length >= 4; // After 2+ exchanges
  const messagesWithReminder = needReminder
    ? windowedMessages.map((m, i) =>
        // Append reminder to the LAST user message
        (i === windowedMessages.length - 1 && m.role === 'user')
          ? { ...m, content: m.content + '\n\n' + CHOICES_REMINDER }
          : m
      )
    : windowedMessages;

  const allMessages = [
    { role: 'system', content: conv.system_prompt },
    ...messagesWithReminder,
  ];

  // Count user turns for suggest_assess
  const userTurns = (dbMessages || []).filter((m: any) => m.role === 'user').length;

  // Stream LLM response (max_tokens raised to 2048 for long conversations + choices block)
  const stream = llmChatStream(c.env, { messages: allMessages, temperature: 0.75, max_tokens: 2048 }, userConfig, 'dialogue');

  // We need to intercept the stream to save the full response
  const encoder = new TextEncoder();
  let fullResponse = '';
  let choicesSent = false;
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

            // V2: Parse choices from full response before sending done
            const parsed = parseChoicesFromContent(fullResponse);
            if (parsed.choices.length >= 2) {
              controller.enqueue(encoder.encode(
                `data: ${JSON.stringify({ type: 'choices', choices: parsed.choices })}\n\n`
              ));
            }

            controller.enqueue(encoder.encode(
              `data: ${JSON.stringify({ type: 'done', suggest_assess: userTurns >= 4, turn: userTurns })}\n\n`
            ));
            choicesSent = true;
          } else {
            controller.enqueue(value);
          }
        }

        // V2: If choices weren't sent yet (no hasDoneEvent in any chunk), send them now
        if (!choicesSent && fullResponse) {
          const parsed = parseChoicesFromContent(fullResponse);
          if (parsed.choices.length >= 2) {
            controller.enqueue(encoder.encode(
              `data: ${JSON.stringify({ type: 'choices', choices: parsed.choices })}\n\n`
            ));
          }
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'done', suggest_assess: userTurns >= 4, turn: userTurns })}\n\n`
          ));
        }
      } finally {
        // Save assistant response to DB — store clean content (without choices block)
        if (fullResponse) {
          const cleanContent = parseChoicesFromContent(fullResponse).content || fullResponse;
          await db.prepare('INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?, ?, ?, ?)')
            .bind(conversation_id, 'assistant', cleanContent, Date.now() / 1000).run();
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
