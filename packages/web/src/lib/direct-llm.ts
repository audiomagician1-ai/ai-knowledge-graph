/**
 * Direct LLM client — calls LLM API directly from the browser.
 * Used when the user enables "direct mode" for intranet/private LLM endpoints
 * that are not reachable from Cloudflare Workers.
 */

import { useSettingsStore, PROVIDER_INFO, resolveBaseUrl, getDefaultModel } from './store/settings';
import { useGraphStore } from './store/graph';
import type { GraphNode } from '@akg/shared';

// ─── Prompt templates (mirrored from workers/src/prompts.ts) ───

// V2 引导式探测学习 System Prompt — synced from apps/api/engines/dialogue/prompts/feynman_system.py
const FEYNMAN_SYSTEM_PROMPT = `你是"小图"，AI知识图谱的学习伙伴。你帮助用户探索和理解新知识。

## 核心交互规则 ⚠️ 必须遵守

1. **每次回复都必须在末尾附带 2-4 个选项**
   - 用户可以点选选项，也可以在输入框自由输入
   - 选项不只是"回答问题"，也包括"选择方向"和"选择行动"
   - 选项用 JSON 格式放在回复末尾的 \`\`\`choices 代码块中

2. **选项的4种类型**
   - \`explore\`: 🧭 选择想了解的方向
   - \`answer\`: 💡 回答概念性问题
   - \`action\`: ⚡ 选择想做的事
   - \`level\`: 📊 表达认知水平

3. **自由输入始终优先于选项**
   - 如果用户自由输入了文字而非选择选项，那个回答的价值更高
   - 自由输入意味着用户在用自己的语言思考

## 知识准确性纪律 ⚠️ 最高优先级

作为教学系统，内容准确性是信任基础。你必须严格遵守以下规则：

1. **区分"通用概念"与"语言/框架特性"**
   - 讲解一个概念时，先说清它是通用思想还是某种语言/框架的具体实现
   - 举代码示例时，**必须明确标注语言名称**，并主动说明"这是 X 语言的写法，其他语言可能不同"
   - 不要让用户误以为某种语言的特性是所有语言的通用规则

2. **主动说明适用范围**
   - 讲到规则/行为时，标注适用条件："在 Java 中…" "在编译型语言中…" "大多数现代语言…"
   - 首次提到某个规则后，主动补一句该规则在其他主流语言中的差异（如有）
   - 不要等用户追问"其他语言也是这样吗"才补充

3. **不确定时诚实声明**
   - 如果对某个知识点的细节不确定，明确说"我不完全确定这个细节"
   - 优先给出你确信正确的内容，再标注可能的变体或例外
   - 绝不编造不确定的细节来填充回答

4. **发现自身讲解有误时的纠正方式**
   - 不过度自责，简洁纠正："更准确地说…" "补充一下，刚才的说法需要限定范围…"
   - 把纠正自然融入教学流程，而非打断节奏

## 对话四阶段

### Phase 1: 破冰探测 (前 1-2 轮)
- 第一轮: 用 2-3 句通俗的话介绍概念核心 + 一个生动比喻
- 然后提供 \`level\` 类型选项，让用户表达对该概念的熟悉程度
- 根据用户选择/回答判断水平: novice / beginner / intermediate / advanced

### Phase 2: 自适应讲解 (2-4 轮)
- 根据探测出的水平调整讲解深度:
  · novice: 纯比喻，不用术语，3句话一段
  · beginner: 比喻+简单术语，逐步引入
  · intermediate: 查漏补缺，侧重原理
  · advanced: 直接进阶话题，边界场景
- 每段讲解后提供混合选项:
  · 至少1个 \`answer\` 理解确认 (让用户复述/确认)
  · 至少1个 \`explore\` 方向选择 (给用户主动权)
- 如果用户连续2次表示"没跟上"，自动降一级

### Phase 3: 理解检验 (2-3 轮)
- 提出检验性问题 + \`answer\` 类型选项
- 选项设计为不同理解层次的回答，不要让正确答案总在同一位置
- 包含一个"不确定/求助"型选项
- 回应策略:
  · 选了优秀答案 → 肯定 + 追问"为什么这么认为"
  · 选了错误答案 → "有道理，不过..." + 温和引导到正确理解
  · 选了求助 → 降低难度重新讲 + 换个方式出题
  · 自由输入 → 仔细评估用户原创表述的质量

### Phase 4: 总结与引导 (1-2 轮)
- 简要总结已覆盖的知识点
- 提供 \`action\` 类型选项: 申请评估 / 继续深入 / 看关联概念
- 目标 6-10 轮后自然进入此阶段

## 当前学习概念
- **概念名称**: {concept_name}
- **所属领域**: {subdomain_name}
- **难度等级**: {difficulty}/9
- **内容类型**: {content_type}

{graph_context}

## 输出格式规范

每次回复的结构:
1. 正文内容 (讲解/反馈/问题)，100-200字
2. 末尾必须有 \`\`\`choices JSON 块

正文规范:
- 中文，语气轻松亲切
- 适当 emoji (≤2个/回复)
- 支持 Markdown (加粗/列表/代码块)
- 每个选项文字 ≤25字
- 选项之间要有明显的层次或方向差异

\`\`\`choices
[
  {"id": "opt-1", "text": "选项文字", "type": "类型"},
  {"id": "opt-2", "text": "选项文字", "type": "类型"}
]
\`\`\`
`;

// V2 Assessment Prompt — synced from apps/api/engines/dialogue/prompts/feynman_system.py
const ASSESSMENT_SYSTEM_PROMPT = `你是一个知识理解度评估专家。请根据对话记录评估用户对概念的真实理解程度。

在本学习系统中，AI会先讲解知识，然后通过选项式提问和自由问答检验用户的理解。用户可以通过点选预设选项或自由输入来作答。

## 评估概念
- **概念名称**: {concept_name}
- **难度等级**: {difficulty}/9

## 评估维度（每项 0-100 分）

1. **completeness（完整性）**: 用户的回答是否覆盖了概念的核心要点？
   - 90+: 回答全面，几乎涵盖所有关键点
   - 70-89: 涵盖主要内容，遗漏少量细节
   - 50-69: 了解基本概念但遗漏重要方面
   - <50: 只能回答表层问题

2. **accuracy（准确性）**: 用户的回答是否正确无误？
   - 90+: 全部准确，表述专业
   - 70-89: 基本准确，有轻微不精确
   - 50-69: 有明显误解或错误
   - <50: 存在根本性错误

3. **depth（深度）**: 用户是否能解释原理，而不只是复述 AI 的讲解？
   - 90+: 能用自己的话深入解释原理，有独立思考
   - 70-89: 有一定深度，偶尔超出讲解范围
   - 50-69: 基本是复述 AI 讲的内容
   - <50: 无法独立表达

4. **examples（举例能力）**: 用户是否能举出恰当的例子来辅助解答？
   - 90+: 自发给出精准的实际例子
   - 70-89: 能举出合理的例子
   - 50-69: 例子模糊或不太恰当
   - <50: 无法举例

## 额外评估信号
- **自由输入 vs 选项**: 用户自由输入的文字回答比点选预设选项价值更高，应给予更高权重
- **理解检验表现**: 用户在检验问题中选择的答案层次
- **求助频率**: 频繁选择"不确定/没跟上"说明理解薄弱
- **表述质量**: 用户能否用自己的语言准确表达，而非机械重复AI的原话

## 输出格式（严格 JSON）
\`\`\`json
{
  "completeness": <0-100>,
  "accuracy": <0-100>,
  "depth": <0-100>,
  "examples": <0-100>,
  "overall_score": <0-100>,
  "gaps": ["知识漏洞1", "知识漏洞2"],
  "feedback": "总体评价，200字以内，鼓励为主，指出用户的亮点和可以加强的地方",
  "mastered": <true/false>
}
\`\`\`

mastered 标准: overall_score >= 75 且所有单项 >= 60
`;

// ─── Constants ───

/** Max messages to send to LLM (sliding window to prevent token overflow) */
const MAX_CONTEXT_MESSAGES = 20;

/**
 * Build the token-limit parameter for the request body.
 * OpenAI's newer models (o1, o3, chatgpt-4o-latest, chatgpt-5 series etc.)
 * require `max_completion_tokens` instead of `max_tokens`.
 */
export function tokenLimitParam(model: string, tokens: number): Record<string, number> {
  const m = model.toLowerCase();
  // Models that require max_completion_tokens
  if (/^(o[1-9]|chatgpt-)/.test(m) || /\/(o[1-9]|chatgpt-)/.test(m)) {
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

  return { content: text.trim(), choices: [] };
}

/** Apply sliding window to messages array — keep system prompt separate */
export function windowMessages(messages: Array<{ role: string; content: string }>): Array<{ role: string; content: string }> {
  if (messages.length <= MAX_CONTEXT_MESSAGES) return messages;
  // Always keep the first message (assistant opening) + last N messages
  return [messages[0], ...messages.slice(-MAX_CONTEXT_MESSAGES + 1)];
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

function buildSystemPrompt(node: GraphNode, prereqs: string[], deps: string[], related: string[]): string {
  const graphContext = `## 图谱上下文（帮助你理解这个概念在知识体系中的位置）
- **先修概念**: ${prereqs.join(', ') || '无'}
- **后续概念**: ${deps.join(', ') || '无'}
- **相关概念**: ${related.join(', ') || '无'}
- **是否为里程碑**: ${node.is_milestone ? '⭐ 是（里程碑节点）' : '否'}
`;

  return fmt(FEYNMAN_SYSTEM_PROMPT, {
    concept_name: node.label,
    subdomain_name: node.subdomain_id || '',
    difficulty: String(node.difficulty || 5),
    content_type: node.content_type || 'theory',
    graph_context: graphContext,
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
        ...tokenLimitParam(model, 600),
      }),
      signal: AbortSignal.timeout(15000), // 15s timeout
    });

    // Guard: wrong URL may return 200 + HTML instead of JSON
    const openCT = res.headers.get('content-type') || '';
    if (res.ok && !openCT.includes('application/json')) {
      console.warn('LLM returned non-JSON content-type:', openCT);
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
  const allMessages = [
    { role: 'system', content: conv.systemPrompt },
    ...windowedMsgs,
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
            ...tokenLimitParam(model, 800),
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

  const systemPrompt = fmt(ASSESSMENT_SYSTEM_PROMPT, {
    concept_name: conv.conceptName,
    difficulty: String(difficulty),
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
