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
  /** 节点状态颜色 — 无战争迷雾，所有节点始终可见 */
  NODE_COLORS: {
    not_started: '#94a3b8',  // slate-400 — 柔和灰蓝
    learning: '#f59e0b',     // amber-500
    reviewing: '#8b5cf6',    // violet-500
    mastered: '#10b981',     // emerald-500
  },
  /** 里程碑节点高亮色 */
  MILESTONE_COLOR: '#fbbf24',    // amber-400 金色
  MILESTONE_GLOW: '#fde68a',     // amber-200 发光
  MILESTONE_RING: '#f59e0b',     // amber-500 外环
  /** 子域配色方案 */
  SUBDOMAIN_COLORS: {
    'cs-fundamentals': '#64748b',
    'programming-basics': '#6366f1',
    'data-structures': '#ec4899',
    'algorithms': '#f97316',
    'oop': '#8b5cf6',
    'web-frontend': '#06b6d4',
    'web-backend': '#14b8a6',
    'database': '#f43f5e',
    'devops': '#84cc16',
    'system-design': '#a855f7',
    'ai-foundations': '#3b82f6',
    'llm-core': '#ef4444',
    'prompt-engineering': '#f59e0b',
    'rag-knowledge': '#10b981',
    'agent-systems': '#8b5cf6',
  } as Record<string, string>,
  /** 默认缩放范围 */
  ZOOM_MIN: 0.1,
  ZOOM_MAX: 4.0,
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
