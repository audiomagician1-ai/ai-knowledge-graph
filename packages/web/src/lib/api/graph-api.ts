import type { GraphData, Concept, Domain } from '@akg/shared';

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

/** 获取指定领域的图谱数据 */
export async function fetchGraphData(domainId?: string): Promise<GraphData> {
  const url = domainId
    ? `${API_BASE}/graph/data?domain_id=${domainId}`
    : `${API_BASE}/graph/data`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`获取图谱失败: ${res.statusText}`);
  return res.json();
}

/** 获取概念详情 */
export async function fetchConcept(conceptId: string): Promise<Concept> {
  const res = await fetch(`${API_BASE}/graph/concepts/${conceptId}`);
  if (!res.ok) throw new Error(`获取概念失败: ${res.statusText}`);
  return res.json();
}

/** 获取所有领域 */
export async function fetchDomains(): Promise<Domain[]> {
  const res = await fetch(`${API_BASE}/graph/domains`);
  if (!res.ok) throw new Error(`获取领域失败: ${res.statusText}`);
  return res.json();
}

/** 获取概念的邻居节点 */
export async function fetchNeighbors(conceptId: string, depth: number = 1): Promise<GraphData> {
  const res = await fetch(`${API_BASE}/graph/concepts/${conceptId}/neighbors?depth=${depth}`);
  if (!res.ok) throw new Error(`获取邻居节点失败: ${res.statusText}`);
  return res.json();
}
