// ========================================
// Feynman Dialogue / Chat Types
// ========================================

/** 对话消息角色 */
export type MessageRole = 'user' | 'assistant' | 'system';

/** 对话消息 */
export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  metadata?: {
    question_type?: 'scaffolding' | 'reverse' | 'application' | 'summary';
    understanding_snapshot?: number; // 当前理解度快照
  };
}

/** 对话会话 */
export interface Conversation {
  id: string;
  user_id: string;
  concept_id: string;
  messages: ChatMessage[];
  summary?: string;
  understanding_delta?: number; // 本次对话带来的理解度变化
  status: 'active' | 'completed' | 'abandoned';
  created_at: string;
  updated_at: string;
}

/** 对话引擎请求 */
export interface DialogueRequest {
  conversation_id: string;
  concept_id: string;
  user_message: string;
  context?: {
    mastery_level: number;
    related_concepts: string[];
  };
}

/** 对话引擎响应 (streaming) */
export interface DialogueResponse {
  message: string;
  is_complete: boolean;
  assessment?: {
    should_assess: boolean;
    preliminary_score?: number;
  };
}
