// ========================================
// Application Constants
// ========================================

/** 应用名称 */
export const APP_NAME = 'AI知识图谱';
export const APP_NAME_EN = 'AI Knowledge Graph';

/** 概念难度等级 */
export const DIFFICULTY_LEVELS = {
  BEGINNER: { min: 1, max: 3, label: '入门', color: '#10b981' },
  INTERMEDIATE: { min: 4, max: 6, label: '进阶', color: '#06b6d4' },
  ADVANCED: { min: 7, max: 9, label: '高级', color: '#f43f5e' },
  EXPERT: { min: 10, max: 10, label: '专家', color: '#8b5cf6' },
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
  /** 节点状态颜色 — Light Breeze */
  NODE_COLORS: {
    not_started: '#94a3b8',  // slate
    learning: '#f59e0b',     // amber
    reviewing: '#06b6d4',    // cyan
    mastered: '#10b981',     // emerald
  },
  /** 里程碑节点高亮色 */
  MILESTONE_COLOR: '#b45309',
  MILESTONE_GLOW: '#b45309',
  MILESTONE_RING: '#d97706',
  /** 难度等级配色(difficulty 1-10) — 从柔和到鲜明的渐变色阶
   *  入门(1-3): 绿色系(易读、友好)
   *  进阶(4-6): 蓝青色系(稳重、成长)
   *  高级(7-9): 橙红色系(挑战、警示)
   *  专家(10):  紫色(稀有、精通)
   */
  DIFFICULTY_COLORS: {
    1: '#86efac',   // green-300  — 最简单
    2: '#4ade80',   // green-400
    3: '#22c55e',   // green-500
    4: '#22d3ee',   // cyan-400   — 中等偏易
    5: '#06b6d4',   // cyan-500
    6: '#0891b2',   // cyan-600   — 中等偏难
    7: '#fb923c',   // orange-400 — 高级入门
    8: '#f97316',   // orange-500
    9: '#f43f5e',   // rose-500   — 高级
    10: '#8b5cf6',  // violet-500 — 专家
  } as Record<number, string>,
  /** @deprecated 旧子域配色方案，已替换为 DIFFICULTY_COLORS */
  SUBDOMAIN_COLORS: {
    'cs-fundamentals': '#64748b',   // slate
    'programming-basics': '#3b82f6', // blue
    'data-structures': '#f97316',    // orange
    'algorithms': '#eab308',         // yellow
    'oop': '#8b5cf6',                // violet
    'web-frontend': '#06b6d4',       // cyan
    'web-backend': '#10b981',        // emerald
    'database': '#ef4444',           // red
    'devops': '#22c55e',             // green
    'system-design': '#a855f7',      // purple
    'ai-foundations': '#3b82f6',     // blue
    'llm-core': '#ec4899',           // pink
    'prompt-engineering': '#eab308', // yellow
    'rag-knowledge': '#14b8a6',      // teal
    'agent-systems': '#8b5cf6',      // violet
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
