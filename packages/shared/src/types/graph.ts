// ========================================
// Knowledge Graph Types
// ========================================

import type { ConceptStatus } from './learning';

/** 领域节点 */
export interface Domain {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  concept_count?: number;
  created_at?: string;
}

/** 概念节点（核心） */
export interface Concept {
  id: string;
  name: string;
  description: string;
  domain_id: string;
  difficulty: number; // 1-10
  estimated_minutes: number;
  content_type: 'theory' | 'practice' | 'project';
  tags: string[];
  created_at?: string;
  updated_at?: string;
}

/** 概念关系类型 */
export type RelationType = 'prerequisite' | 'related_to';
export type RelatedSubType = 'analogy' | 'application' | 'contrast';

/** 概念关系边 */
export interface ConceptEdge {
  source_id: string;
  target_id: string;
  relation_type: RelationType;
  strength: number; // 0.0 - 1.0
  sub_type?: RelatedSubType;
}

/** 图谱数据（前端渲染用） */
export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphNode {
  id: string;
  label: string;
  domain_id: string;
  difficulty: number;
  status: ConceptStatus;
  position?: { x: number; y: number };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  relation_type: RelationType;
  strength: number;
}
