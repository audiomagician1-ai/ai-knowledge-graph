// ========================================
// Application Constants
// ========================================

/** 应用名称 */
export const APP_NAME = 'AI知识图谱';
export const APP_NAME_EN = 'AI Knowledge Graph';

/** 概念难度等级 */
export const DIFFICULTY_LEVELS = {
  BEGINNER: { min: 1, max: 3, label: '入门', color: '#4ade80' },
  INTERMEDIATE: { min: 4, max: 6, label: '进阶', color: '#facc15' },
  ADVANCED: { min: 7, max: 9, label: '高级', color: '#f97316' },
  EXPERT: { min: 10, max: 10, label: '专家', color: '#ef4444' },
} as const;

/** 理解度阈值 */
export const MASTERY_THRESHOLDS = {
  /** 点亮节点的最低分数 */
  PASS: 0.6,
  /** 掌握节点的最低分数 */
  MASTERED: 0.85,
  /** 复习提醒的衰减阈值 */
  REVIEW_TRIGGER: 0.5,
} as const;

/** 图谱可视化常量 */
export const GRAPH_VISUAL = {
  /** 节点状态颜色 */
  NODE_COLORS: {
    locked: '#374151',     // gray-700
    available: '#6366f1',  // indigo-500
    learning: '#f59e0b',   // amber-500
    reviewing: '#8b5cf6',  // violet-500
    mastered: '#10b981',   // emerald-500
  },
  /** 战争迷雾透明度 */
  FOG_OPACITY: 0.15,
  /** 默认缩放范围 */
  ZOOM_MIN: 0.2,
  ZOOM_MAX: 3.0,
} as const;

/** API 端点 */
export const API_ENDPOINTS = {
  GRAPH: '/api/graph',
  DIALOGUE: '/api/dialogue',
  LEARNING: '/api/learning',
  AUTH: '/api/auth',
} as const;

/** Supabase 表名 */
export const DB_TABLES = {
  PROFILES: 'profiles',
  USER_SETTINGS: 'user_settings',
  USER_CONCEPT_STATUS: 'user_concept_status',
  CONVERSATIONS: 'conversations',
  LEARNING_EVENTS: 'learning_events',
} as const;
