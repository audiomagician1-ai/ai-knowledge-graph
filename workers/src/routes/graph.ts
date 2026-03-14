import { Hono } from 'hono';
import type { Env } from '../types';
// Seed data is imported at build time via wrangler's module rules
// We import it from the data directory (copied to workers/data at build)
import seedGraph from '../../data/seed_graph.json';
import ragIndex from '../../data/rag/_index.json';

const app = new Hono<{ Bindings: Env }>();

const seed = seedGraph as any;

/** GET /graph/data */
app.get('/data', (c) => {
  const subdomainId = c.req.query('subdomain_id');

  let concepts = seed.concepts;
  let edges = seed.edges;

  if (subdomainId) {
    const ids = new Set(concepts.filter((cc: any) => cc.subdomain_id === subdomainId).map((cc: any) => cc.id));
    concepts = concepts.filter((cc: any) => cc.subdomain_id === subdomainId);
    edges = edges.filter((e: any) => ids.has(e.source_id) || ids.has(e.target_id));
  }

  const nodes = concepts.map((c: any) => ({
    id: c.id,
    label: c.name,
    domain_id: c.domain_id,
    subdomain_id: c.subdomain_id,
    difficulty: c.difficulty,
    status: 'not_started',
    is_milestone: c.is_milestone ?? false,
    estimated_minutes: c.estimated_minutes,
    content_type: c.content_type,
    tags: c.tags,
  }));

  const graphEdges = edges.map((e: any) => ({
    id: `${e.source_id}-${e.target_id}`,
    source: e.source_id,
    target: e.target_id,
    relation_type: e.relation_type,
    strength: e.strength,
  }));

  return c.json({ nodes, edges: graphEdges });
});

/** GET /graph/domains */
app.get('/domains', (c) => c.json([seed.domain]));

/** GET /graph/subdomains */
app.get('/subdomains', (c) => {
  const conceptCounts: Record<string, number> = {};
  for (const cc of seed.concepts) {
    conceptCounts[cc.subdomain_id] = (conceptCounts[cc.subdomain_id] || 0) + 1;
  }
  return c.json(seed.subdomains.map((sd: any) => ({ ...sd, concept_count: conceptCounts[sd.id] || 0 })));
});

/** GET /graph/concepts/:id */
app.get('/concepts/:id', (c) => {
  const conceptId = c.req.param('id');
  const concept = seed.concepts.find((cc: any) => cc.id === conceptId);
  if (!concept) return c.json({ detail: `概念不存在: ${conceptId}` }, 404);

  const prerequisites: string[] = [];
  const dependents: string[] = [];
  for (const e of seed.edges) {
    if (e.relation_type === 'prerequisite') {
      if (e.target_id === conceptId) prerequisites.push(e.source_id);
      if (e.source_id === conceptId) dependents.push(e.target_id);
    }
  }
  return c.json({ ...concept, prerequisites, dependents });
});

/** GET /graph/concepts/:id/neighbors */
app.get('/concepts/:id/neighbors', (c) => {
  const conceptId = c.req.param('id');
  const depth = Math.min(parseInt(c.req.query('depth') || '1'), 3);
  const allIds = new Set(seed.concepts.map((cc: any) => cc.id));
  if (!allIds.has(conceptId)) return c.json({ detail: `概念不存在: ${conceptId}` }, 404);

  const visited = new Set([conceptId]);
  let frontier = new Set([conceptId]);

  for (let i = 0; i < depth; i++) {
    const next = new Set<string>();
    for (const e of seed.edges) {
      if (frontier.has(e.source_id) && !visited.has(e.target_id)) { next.add(e.target_id); visited.add(e.target_id); }
      if (frontier.has(e.target_id) && !visited.has(e.source_id)) { next.add(e.source_id); visited.add(e.source_id); }
    }
    frontier = next;
  }

  const nodes = seed.concepts.filter((cc: any) => visited.has(cc.id)).map((cc: any) => ({
    id: cc.id, label: cc.name, domain_id: cc.domain_id, subdomain_id: cc.subdomain_id,
    difficulty: cc.difficulty, status: 'not_started', is_milestone: cc.is_milestone ?? false,
  }));
  const graphEdges = seed.edges
    .filter((e: any) => visited.has(e.source_id) && visited.has(e.target_id))
    .map((e: any) => ({ id: `${e.source_id}-${e.target_id}`, source: e.source_id, target: e.target_id, relation_type: e.relation_type, strength: e.strength }));

  return c.json({ nodes, edges: graphEdges, center: conceptId, depth });
});

/** GET /graph/stats */
app.get('/stats', (c) => c.json(seed.meta));

/** GET /graph/rag/:concept_id */
app.get('/rag/:concept_id', (c) => {
  const conceptId = c.req.param('concept_id');
  const idx = ragIndex as any;
  const doc = idx.documents?.find((d: any) => d.id === conceptId);
  if (!doc) return c.json({ detail: `RAG 文档不存在: ${conceptId}` }, 404);
  // RAG content is served from static files — return metadata only for now
  return c.json({
    concept_id: conceptId,
    name: doc.name || conceptId,
    subdomain: doc.subdomain_id || '',
    difficulty: doc.difficulty || 0,
    is_milestone: doc.is_milestone || false,
    file: doc.file,
  });
});

/** GET /graph/rag */
app.get('/rag', (c) => {
  const idx = ragIndex as any;
  return c.json({
    total_docs: idx.stats?.total_docs || 0,
    total_chars: idx.stats?.total_chars || 0,
    by_subdomain: idx.stats?.by_subdomain || {},
    version: idx.version || '',
    generated_at: idx.generated_at || '',
  });
});

export default app;
