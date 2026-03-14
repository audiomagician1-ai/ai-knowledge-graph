// ========================================
// Application Constants
// ========================================

/** 应用名称 */
export const APP_NAME = 'AI知识图谱';
export const APP_NAME_EN = 'AI Knowledge Graph';

/** 概念难度等级 */
export const DIFFICULTY_LEVELS = {
  BEGINNER: { min: 1, max: 3, label: '入门', color: '#47d18c' },
  INTERMEDIATE: { min: 4, max: 6, label: '进阶', color: '#5eb8f0' },
  ADVANCED: { min: 7, max: 9, label: '高级', color: '#f07878' },
  EXPERT: { min: 10, max: 10, label: '专家', color: '#c78bf0' },
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
  /** 节点状态颜色 — Fresh Inspiration */
  NODE_COLORS: {
    not_started: '#4a5568',  // cool gray
    learning: '#f5b85a',     // warm gold
    reviewing: '#5eb8f0',    // sky blue
    mastered: '#47d18c',     // vivid green
  },
  /** 里程碑节点高亮色 */
  MILESTONE_COLOR: '#f5d05a',    // bright gold
  MILESTONE_GLOW: '#f5d05a',
  MILESTONE_RING: '#f5b85a',
  /** 子域配色方案 — 鲜明活力 */
  SUBDOMAIN_COLORS: {
    'cs-fundamentals': '#8899b0',   // steel blue
    'programming-basics': '#5eb8f0', // sky blue
    'data-structures': '#f0a05e',    // tangerine
    'algorithms': '#f5b85a',         // golden
    'oop': '#c78bf0',                // lavender
    'web-frontend': '#5ed3ac',       // mint
    'web-backend': '#47d18c',        // emerald
    'database': '#f07878',           // coral
    'devops': '#7cd18c',             // fresh green
    'system-design': '#c78bf0',      // purple
    'ai-foundations': '#5eb8f0',     // sky
    'llm-core': '#f08a7a',           // salmon
    'prompt-engineering': '#f5c85a', // gold
    'rag-knowledge': '#5ed3ac',      // mint
    'agent-systems': '#a78bf0',      // violet
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
