import type { GraphData, Concept, Domain } from '@akg/shared';
import { createLogger } from '@/lib/utils/logger';
import { fetchWithRetry } from '@/lib/utils/fetch-retry';

const log = createLogger('GraphAPI');
const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api';

/** 获取指定领域的图谱数据 */
export async function fetchGraphData(domain?: string): Promise<GraphData> {
  const url = domain
    ? `${API_BASE}/graph/data?domain=${encodeURIComponent(domain)}`
    : `${API_BASE}/graph/data`;
  const res = await fetchWithRetry(url, { retries: 2 });
  if (!res.ok) {
    log.error('fetchGraphData failed', { domain, status: res.status });
    throw new Error(`获取图谱失败: ${res.statusText}`);
  }
  return res.json();
}

/** 获取概念详情 */
export async function fetchConcept(conceptId: string): Promise<Concept> {
  const res = await fetchWithRetry(`${API_BASE}/graph/concepts/${encodeURIComponent(conceptId)}`);
  if (!res.ok) throw new Error(`获取概念失败: ${res.statusText}`);
  return res.json();
}

/** 获取所有领域 */
export async function fetchDomains(): Promise<Domain[]> {
  const res = await fetchWithRetry(`${API_BASE}/graph/domains`, { retries: 2 });
  if (!res.ok) throw new Error(`获取领域失败: ${res.statusText}`);
  return res.json();
}

/** 领域间连接 */
export interface DomainLink {
  source: string;
  target: string;
  count: number;
  relations: string[];
}

/** 获取领域间连接（聚合的跨领域知识关联） */
export async function fetchDomainLinks(): Promise<DomainLink[]> {
  const res = await fetchWithRetry(`${API_BASE}/graph/domain-links`);
  if (!res.ok) throw new Error(`获取领域连接失败: ${res.statusText}`);
  return res.json();
}

/** 获取概念的邻居节点 */
export async function fetchNeighbors(conceptId: string, depth: number = 1): Promise<GraphData> {
  const res = await fetchWithRetry(`${API_BASE}/graph/concepts/${encodeURIComponent(conceptId)}/neighbors?depth=${depth}`);
  if (!res.ok) throw new Error(`获取邻居节点失败: ${res.statusText}`);
  return res.json();
}
