import type { DialogueRequest } from '@akg/shared';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

/**
 * 发送费曼对话消息（流式）
 * 返回 ReadableStream 用于 SSE 解析
 */
export async function sendDialogueMessage(
  request: DialogueRequest,
  signal?: AbortSignal,
): Promise<Response> {
  const res = await fetch(`${API_BASE}/dialogue/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    signal,
  });
  if (!res.ok) throw new Error(`对话请求失败: ${res.statusText}`);
  return res;
}

/** 请求对概念的理解度评估 */
export async function requestAssessment(
  conversationId: string,
  conceptId: string,
): Promise<Response> {
  const res = await fetch(`${API_BASE}/dialogue/assess`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ conversation_id: conversationId, concept_id: conceptId }),
  });
  if (!res.ok) throw new Error(`评估请求失败: ${res.statusText}`);
  return res;
}

/** 创建新的对话会话 */
export async function createConversation(conceptId: string, domainId?: string): Promise<{ conversation_id: string }> {
  const res = await fetch(`${API_BASE}/dialogue/conversations`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ concept_id: conceptId, domain_id: domainId || 'ai-engineering' }),
  });
  if (!res.ok) throw new Error(`创建对话失败: ${res.statusText}`);
  return res.json();
}
