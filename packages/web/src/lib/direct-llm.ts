/**
 * Direct LLM client — calls LLM API directly from the browser.
 * Used when the user enables "direct mode" for intranet/private LLM endpoints
 * that are not reachable from Cloudflare Workers.
 */

import { useSettingsStore, PROVIDER_INFO } from './store/settings';
import { useGraphStore } from './store/graph';
import type { GraphNode } from '@akg/shared';

// ─── Prompt templates (mirrored from workers/src/prompts.ts) ───

const FEYNMAN_SYSTEM_PROMPT = `你是"小图"，一个聪明但对当前话题一知半解的AI学习伙伴。你们正在一起学习新知识。

## 你的双重角色

你在对话中交替扮演两个角色：

### 🎓 导师模式（讲解时）
- 每轮开始时，你先以导师身份**简要讲解一小段知识**（2-4句话）
- 讲解要清晰、通俗，用生活化的比喻帮助理解
- 讲解内容要循序渐进，不要一次灌输太多

### 🤔 好奇学生模式（提问时）
- 讲完一段后，你立刻切换身份，变成一个**听懂了大概但有疑惑的学生**
- 你要提出**真诚的、具体的疑问**，就像真的没搞懂一样
- 语气从"老师讲课"变成"同学请教"：谦虚、好奇、有点困惑
- 目标是让用户用自己的话来解释，从而加深理解

## 当前学习概念
- **概念名称**: {concept_name}
- **所属领域**: {subdomain_name}
- **难度等级**: {difficulty}/9
- **内容类型**: {content_type}

{graph_context}

## 对话流程

### 第一轮（开场）
1. 热情打招呼，说你们今天一起学 {concept_name}
2. 【导师模式】先讲解这个概念的核心定义和重要性（3-4句话）
3. 【切换→好奇学生】说"我大概懂了，但有个地方不太明白..."，然后提出一个入门级的疑问
4. 切换时用语气变化来暗示身份转换（不需要显式标注角色）

### 后续轮次
每轮遵循以下模式：
1. **反馈用户的回答**：
   - 回答到位 → "哦！原来是这样，你这么一说我就懂了！" 然后简要复述确认
   - 回答部分正确 → "嗯嗯，我理解了一部分，但是..."  补充正确的解释
   - 回答有误 → "等等，我有点困惑..." 温和地从另一个角度重新讲解正确内容
2. **【导师模式】引入下一个知识点**（2-3句话）
3. **【好奇学生模式】提出新的疑问**，让用户来解释

### 好奇学生的提问风格（轮换使用）
1. **"为什么"类** — "等一下，我不太理解为什么要这样做，直接XX不行吗？"
2. **"区别"类** — "这个和之前说的YY听起来很像啊，它们到底有啥不同？"
3. **"举例"类** — "道理我好像懂了，但你能给我举个具体的例子吗？"
4. **"如果"类** — "那如果遇到XX情况，这个还管用吗？"
5. **"本质"类** — "所以说到底，XX最核心的一点是什么？你能用一句大白话总结吗？"

### 评估时机（第4轮之后）
- 当核心知识点讲完后，以学生口吻说："感觉我差不多都搞明白了！要不你考考我，看我真的学会没？"
- 这是暗示用户可以点击评估按钮

## 输出规范
- 每次回复控制在 **150-250 字**
- 导师讲解部分：简洁清晰，多用比喻和例子
- 学生提问部分：自然口语化，像真人同学在聊天
- 语气整体：轻松、亲切、平等，不居高临下
- 使用适当的 emoji（不超过2个/回复）
- 对话必须是**中文**
- 每次回复**必须以一个问题结尾**（好奇学生的疑问）
- 绝对不要说"我现在切换为学生模式"之类的元描述
`;

const ASSESSMENT_SYSTEM_PROMPT = `你是一个知识理解度评估专家。用户在对话中扮演了"解答者"的角色——AI先讲解知识，然后以好奇学生的身份提问，用户尝试用自己的话来解答。请根据用户的解答表现，评估其对概念的真实理解程度。

## 评估概念
- **概念名称**: {concept_name}
- **难度等级**: {difficulty}/9

## 评估维度（每项 0-100 分）

1. **completeness（完整性）**: 用户的解答是否覆盖了概念的核心要点？
2. **accuracy（准确性）**: 用户的解答是否正确无误？
3. **depth（深度）**: 用户是否能解释原理，而不只是复述 AI 的讲解？
4. **examples（举例能力）**: 用户是否能举出恰当的例子来辅助解答？

## 输出格式（严格 JSON）
\`\`\`json
{
  "completeness": <0-100>,
  "accuracy": <0-100>,
  "depth": <0-100>,
  "examples": <0-100>,
  "overall_score": <0-100>,
  "gaps": ["知识漏洞1", "知识漏洞2"],
  "feedback": "总体评价，200字以内，鼓励为主",
  "mastered": <true/false>
}
\`\`\`

mastered 标准: overall_score >= 75 且所有单项 >= 60
`;

// ─── Helpers ───

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
  const model = llmConfig.model || 'gpt-4o';

  if (llmConfig.baseUrl) {
    return { baseUrl: llmConfig.baseUrl.replace(/\/$/, ''), apiKey: key, model };
  }

  const info = PROVIDER_INFO[llmConfig.provider];
  return { baseUrl: info.defaultBase.replace(/\/$/, ''), apiKey: key, model };
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

function getOpening(name: string, difficulty: number): string {
  if (difficulty <= 3) return `嗨！👋 我听说${name}是编程中很基础但很重要的概念。不过我还不太理解它到底是什么意思。你能用最简单的话给我解释一下吗？`;
  if (difficulty <= 6) return `嗨！🤔 我最近在学习${name}，感觉挺有意思但又有点复杂。你对这个概念了解多少？能试着用最直白的方式给我讲讲吗？`;
  return `嗨！🧐 ${name}这个话题看起来挺深的，我之前一直没搞明白。听说你对这方面有研究，能帮我从头捋一下吗？先从最核心的概念开始？`;
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

// In-memory conversation storage for direct mode
const directConversations = new Map<string, DirectConversation>();

/** Create a new conversation in direct mode (no Worker call) */
export function directCreateConversation(conceptId: string): {
  conversation_id: string;
  concept_id: string;
  concept_name: string;
  opening_message: string;
  is_milestone: boolean;
} | null {
  const ctx = getConceptContext(conceptId);
  if (!ctx) return null;

  const { node, prereqs, deps, related } = ctx;
  const systemPrompt = buildSystemPrompt(node, prereqs, deps, related);
  const opening = getOpening(node.label, node.difficulty);
  const convId = crypto.randomUUID();

  const conv: DirectConversation = {
    conversationId: convId,
    conceptId,
    conceptName: node.label,
    systemPrompt,
    messages: [{ role: 'assistant', content: opening }],
    isMilestone: node.is_milestone,
  };
  directConversations.set(convId, conv);

  return {
    conversation_id: convId,
    concept_id: conceptId,
    concept_name: node.label,
    opening_message: opening,
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
  const allMessages = [
    { role: 'system', content: conv.systemPrompt },
    ...conv.messages,
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
            max_tokens: 512,
            stream: true,
          }),
          signal,
        });

        if (!res.ok) {
          const text = await res.text().catch(() => '');
          controller.enqueue(encoder.encode(
            `data: ${JSON.stringify({ type: 'chunk', content: `⚠️ LLM 错误 ${res.status}: ${text.slice(0, 200)}` })}\n\n`
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

        // Save assistant response
        if (fullContent) {
          conv.messages.push({ role: 'assistant', content: fullContent });
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

  const dialogueText = conv.messages.map(m =>
    `[${m.role === 'user' ? '用户（老师）' : 'AI（学生）'}]: ${m.content}`
  ).join('\n\n');

  const { baseUrl, apiKey, model } = resolveEndpoint();

  try {
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
        max_tokens: 1024,
      }),
    });

    if (!res.ok) throw new Error(`LLM error ${res.status}`);
    const data: any = await res.json();
    const text = data.choices?.[0]?.message?.content || '';

    // Parse assessment JSON
    const result = parseAssessmentJSON(text);
    if (result) {
      return { concept_id: conv.conceptId, concept_name: conv.conceptName, turns: userTurns, ...result };
    }
  } catch { /* fallback */ }

  // Fallback
  const base = Math.min(40 + userTurns * 8, 85);
  return {
    concept_id: conv.conceptId, concept_name: conv.conceptName, turns: userTurns,
    completeness: base, accuracy: base - 5, depth: base - 10, examples: base - 15,
    overall_score: base - 5, gaps: ['评估服务暂时不可用'], feedback: `你进行了 ${userTurns} 轮对话，表现不错！`,
    mastered: base >= 80,
  };
}

function parseAssessmentJSON(text: string): any | null {
  try { return JSON.parse(text); } catch { /* */ }
  if (text.includes('```json')) {
    const start = text.indexOf('```json') + 7;
    const end = text.indexOf('```', start);
    try { return JSON.parse(text.slice(start, end).trim()); } catch { /* */ }
  }
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}') + 1;
  if (start >= 0 && end > start) {
    try {
      const result = JSON.parse(text.slice(start, end));
      for (const k of ['completeness', 'accuracy', 'depth', 'examples', 'overall_score']) {
        result[k] = Math.max(0, Math.min(100, Math.round(result[k] || 50)));
      }
      result.mastered = result.overall_score >= 75 && ['completeness', 'accuracy', 'depth', 'examples'].every((k: string) => result[k] >= 60);
      result.gaps = result.gaps || [];
      result.feedback = result.feedback || '评估完成';
      return result;
    } catch { /* */ }
  }
  return null;
}
