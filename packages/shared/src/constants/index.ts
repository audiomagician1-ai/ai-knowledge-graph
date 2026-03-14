// ========================================
// Application Constants
// ========================================

/** 应用名称 */
export const APP_NAME = 'AI知识图谱';
export const APP_NAME_EN = 'AI Knowledge Graph';

/** 概念难度等级 */
export const DIFFICULTY_LEVELS = {
  BEGINNER: { min: 1, max: 3, label: '入门', color: '#8aad7a' },
  INTERMEDIATE: { min: 4, max: 6, label: '进阶', color: '#c8956c' },
  ADVANCED: { min: 7, max: 9, label: '高级', color: '#c97b7b' },
  EXPERT: { min: 10, max: 10, label: '专家', color: '#b07cc3' },
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
  /** 节点状态颜色 — Observatory Study 暖色系 */
  NODE_COLORS: {
    not_started: '#807d78',  // warm gray
    learning: '#c8956c',     // copper
    reviewing: '#8a9ec0',    // muted blue
    mastered: '#8aad7a',     // sage green
  },
  /** 里程碑节点高亮色 */
  MILESTONE_COLOR: '#d4a57c',    // warm copper
  MILESTONE_GLOW: '#d4a57c',     // same — no glow
  MILESTONE_RING: '#c8956c',     // copper
  /** 子域配色方案 — Observatory Study 降饱和暖色 */
  SUBDOMAIN_COLORS: {
    'cs-fundamentals': '#8a8884',   // warm stone
    'programming-basics': '#8a9ec0', // muted slate-blue
    'data-structures': '#b8917a',    // dusty terracotta
    'algorithms': '#c8956c',         // copper
    'oop': '#9b8aad',                // muted lavender
    'web-frontend': '#7ba9a0',       // sage-teal
    'web-backend': '#8aad7a',        // sage green
    'database': '#c97b7b',           // muted rose
    'devops': '#9aad7a',             // olive sage
    'system-design': '#b07cc3',      // muted plum
    'ai-foundations': '#7b9ec8',     // dusty blue
    'llm-core': '#c4887a',           // warm coral
    'prompt-engineering': '#c8a86c', // warm gold
    'rag-knowledge': '#7bae7f',      // soft sage
    'agent-systems': '#9b8aad',      // muted lavender
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
