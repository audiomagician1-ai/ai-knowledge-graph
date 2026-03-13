// ========================================
// Learning & User Progress Types
// ========================================

/** 概念学习状态 */
export type ConceptStatus =
  | 'locked'      // 前置未满足，不可见详情
  | 'available'   // 可以开始学习
  | 'learning'    // 正在学习中
  | 'reviewing'   // 已学过，等待复习
  | 'mastered';   // 已掌握

/** 用户概念学习状态 */
export interface UserConceptStatus {
  user_id: string;
  concept_id: string;
  status: ConceptStatus;
  mastery_level: number; // 0.0 ~ 1.0
  // FSRS 字段
  fsrs_stability?: number;
  fsrs_difficulty?: number;
  fsrs_due_date?: string;
  fsrs_last_review?: string;
  // 统计
  total_sessions: number;
  total_time_sec: number;
  feynman_score?: number;
  last_feynman_at?: string;
}

/** 理解度评估结果 */
export interface UnderstandingAssessment {
  overall_score: number; // 0-100
  completeness: number;  // 完整性 0-100
  accuracy: number;      // 准确性 0-100
  depth: number;         // 深度 0-100
  examples: number;      // 举例能力 0-100
  gaps: string[];        // 知识漏洞
  feedback: string;      // 整体反馈
}

/** 学习事件 */
export interface LearningEvent {
  id: string;
  user_id: string;
  concept_id: string;
  event_type: 'feynman_attempt' | 'review' | 'quiz' | 'unlock' | 'mastered';
  payload: Record<string, unknown>;
  created_at: string;
}

/** 学习统计 */
export interface LearningStats {
  total_concepts: number;
  mastered_count: number;
  learning_count: number;
  available_count: number;
  locked_count: number;
  total_study_time_sec: number;
  current_streak: number;
  longest_streak: number;
}
