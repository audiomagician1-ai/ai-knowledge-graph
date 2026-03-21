import { Hono } from 'hono';
import type { Env } from '../types';
// Seed data is imported at build time via wrangler's module rules
// We import it from the data directory (copied to workers/data at build)
// Multi-domain seed data imports
import domainsRegistry from '../../data/seed/domains.json';
import crossSphereLinks from '../../data/seed/cross_sphere_links.json';
import seedAI from '../../data/seed/ai-engineering/seed_graph.json';
import seedMath from '../../data/seed/mathematics/seed_graph.json';
import seedEnglish from '../../data/seed/english/seed_graph.json';
import seedPhysics from '../../data/seed/physics/seed_graph.json';
import seedProduct from '../../data/seed/product-design/seed_graph.json';
import seedFinance from '../../data/seed/finance/seed_graph.json';
import seedPsychology from '../../data/seed/psychology/seed_graph.json';
import seedPhilosophy from '../../data/seed/philosophy/seed_graph.json';
import seedBiology from '../../data/seed/biology/seed_graph.json';
import seedEconomics from '../../data/seed/economics/seed_graph.json';
import seedWriting from '../../data/seed/writing/seed_graph.json';
import seedGameDesign from '../../data/seed/game-design/seed_graph.json';
import seedLevelDesign from '../../data/seed/level-design/seed_graph.json';
import seedGameEngine from '../../data/seed/game-engine/seed_graph.json';
import seedSoftwareEngineering from '../../data/seed/software-engineering/seed_graph.json';
import seedComputerGraphics from '../../data/seed/computer-graphics/seed_graph.json';
import seed3DArt from '../../data/seed/3d-art/seed_graph.json';
import seedConceptDesign from '../../data/seed/concept-design/seed_graph.json';
import seedAnimation from '../../data/seed/animation/seed_graph.json';
import seedTechnicalArt from '../../data/seed/technical-art/seed_graph.json';
import seedVfx from '../../data/seed/vfx/seed_graph.json';
import seedGameAudioMusic from '../../data/seed/game-audio-music/seed_graph.json';
import seedGameUiUx from '../../data/seed/game-ui-ux/seed_graph.json';
import seedNarrativeDesign from '../../data/seed/narrative-design/seed_graph.json';
import seedMultiplayerNetwork from '../../data/seed/multiplayer-network/seed_graph.json';
// Multi-domain RAG index imports
import ragAI from '../../data/rag/_index.json';
import ragMath from '../../data/rag/mathematics/_index.json';
import ragEnglish from '../../data/rag/english/_index.json';
import ragPhysics from '../../data/rag/physics/_index.json';
import ragProduct from '../../data/rag/product-design/_index.json';
import ragFinance from '../../data/rag/finance/_index.json';
import ragPsychology from '../../data/rag/psychology/_index.json';
import ragPhilosophy from '../../data/rag/philosophy/_index.json';
import ragBiology from '../../data/rag/biology/_index.json';
import ragEconomics from '../../data/rag/economics/_index.json';
import ragWriting from '../../data/rag/writing/_index.json';
import ragGameDesign from '../../data/rag/game-design/_index.json';
import ragLevelDesign from '../../data/rag/level-design/_index.json';
import ragGameEngine from '../../data/rag/game-engine/_index.json';
import ragSoftwareEngineering from '../../data/rag/software-engineering/_index.json';
import ragComputerGraphics from '../../data/rag/computer-graphics/_index.json';
import rag3DArt from '../../data/rag/3d-art/_index.json';
import ragConceptDesign from '../../data/rag/concept-design/_index.json';
import ragAnimation from '../../data/rag/animation/_index.json';
import ragTechnicalArt from '../../data/rag/technical-art/_index.json';
import ragVfx from '../../data/rag/vfx/_index.json';
import ragGameAudioMusic from '../../data/rag/game-audio-music/_index.json';
import ragGameUiUx from '../../data/rag/game-ui-ux/_index.json';
import ragNarrativeDesign from '../../data/rag/narrative-design/_index.json';
import ragMultiplayerNetwork from '../../data/rag/multiplayer-network/_index.json';

const app = new Hono<{ Bindings: Env }>();

const DEFAULT_DOMAIN = 'ai-engineering';
const domainsList = (domainsRegistry as any).domains as any[];
const seedMap: Record<string, any> = {
  'ai-engineering': seedAI, 'mathematics': seedMath, 'english': seedEnglish,
  'physics': seedPhysics, 'product-design': seedProduct, 'finance': seedFinance,
  'psychology': seedPsychology, 'philosophy': seedPhilosophy,
  'biology': seedBiology, 'economics': seedEconomics, 'writing': seedWriting,
  'game-design': seedGameDesign,
  'level-design': seedLevelDesign,
  'game-engine': seedGameEngine,
  'software-engineering': seedSoftwareEngineering,
  'computer-graphics': seedComputerGraphics,
  '3d-art': seed3DArt,
  'concept-design': seedConceptDesign,
  'animation': seedAnimation,
  'technical-art': seedTechnicalArt,
  'vfx': seedVfx,
  'game-audio-music': seedGameAudioMusic,
  'game-ui-ux': seedGameUiUx,
  'narrative-design': seedNarrativeDesign,
  'multiplayer-network': seedMultiplayerNetwork,
};
const ragMap: Record<string, any> = {
  'ai-engineering': ragAI, 'mathematics': ragMath, 'english': ragEnglish,
  'physics': ragPhysics, 'product-design': ragProduct, 'finance': ragFinance,
  'psychology': ragPsychology, 'philosophy': ragPhilosophy,
  'biology': ragBiology, 'economics': ragEconomics, 'writing': ragWriting,
  'game-design': ragGameDesign,
  'level-design': ragLevelDesign,
  'game-engine': ragGameEngine,
  'software-engineering': ragSoftwareEngineering,
  'computer-graphics': ragComputerGraphics,
  '3d-art': rag3DArt,
  'concept-design': ragConceptDesign,
  'animation': ragAnimation,
  'technical-art': ragTechnicalArt,
  'vfx': ragVfx,
  'game-audio-music': ragGameAudioMusic,
  'game-ui-ux': ragGameUiUx,
  'narrative-design': ragNarrativeDesign,
  'multiplayer-network': ragMultiplayerNetwork,
};
function getSeed(domain: string): any { return seedMap[domain] || null; }
function getRagIndex(domain: string): any { return ragMap[domain] || { documents: [], stats: {} }; }

/** GET /graph/data */
app.get('/data', (c) => {
  const domain = c.req.query('domain') || DEFAULT_DOMAIN;
  const subdomainId = c.req.query('subdomain_id');
  const seed = getSeed(domain);
  if (!seed) return c.json({ detail: 'Domain not found' }, 404);

  let concepts = seed.concepts;
  let edges = seed.edges;

  if (subdomainId) {
    const ids = new Set(concepts.filter((cc: any) => cc.subdomain_id === subdomainId).map((cc: any) => cc.id));
    concepts = concepts.filter((cc: any) => cc.subdomain_id === subdomainId);
    edges = edges.filter((e: any) => ids.has(e.source_id) && ids.has(e.target_id));
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
app.get('/domains', (c) => { const result = domainsList.filter((d: any) => d.is_active !== false).map((d: any) => { const s = getSeed(d.id); const stats = s ? { total_concepts: s.concepts?.length ?? 0, total_edges: s.edges?.length ?? 0, subdomains: s.subdomains?.length ?? 0 } : { total_concepts: 0, total_edges: 0, subdomains: 0 }; return { ...d, stats }; }); return c.json(result); });

/** GET /graph/subdomains */
app.get('/subdomains', (c) => {
  const domain = c.req.query('domain') || DEFAULT_DOMAIN;
  const seed = getSeed(domain);
  if (!seed) return c.json({ detail: 'Domain not found' }, 404);
  const conceptCounts: Record<string, number> = {};
  for (const cc of seed.concepts) {
    conceptCounts[cc.subdomain_id] = (conceptCounts[cc.subdomain_id] || 0) + 1;
  }
  return c.json(seed.subdomains.map((sd: any) => ({ ...sd, concept_count: conceptCounts[sd.id] || 0 })));
});

/** GET /graph/concepts/:id */
app.get('/concepts/:id', (c) => {
  const conceptId = c.req.param('id');
  const domain = c.req.query('domain') || DEFAULT_DOMAIN;
  const seed = getSeed(domain);
  if (!seed) return c.json({ detail: 'Domain not found' }, 404);
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
  const domain = c.req.query('domain') || DEFAULT_DOMAIN;
  const seed = getSeed(domain);
  if (!seed) return c.json({ detail: 'Domain not found' }, 404);
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
app.get('/stats', (c) => {
  const domain = c.req.query('domain') || DEFAULT_DOMAIN;
  const seed = getSeed(domain);
  if (!seed) return c.json({ detail: 'Domain not found' }, 404);
  return c.json(seed.meta);
});

/** GET /graph/rag/:concept_id */
app.get('/rag/:concept_id', (c) => {
  const conceptId = c.req.param('concept_id');
  const domain = c.req.query('domain') || DEFAULT_DOMAIN;
  const idx = getRagIndex(domain);
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
  const domain = c.req.query('domain') || DEFAULT_DOMAIN;
  const idx = getRagIndex(domain);
  return c.json({
    domain,
    total_docs: idx.stats?.total_docs || idx.total_concepts || 0,
    total_chars: idx.stats?.total_chars || 0,
    by_subdomain: idx.stats?.by_subdomain || {},
    version: idx.version || '',
    generated_at: idx.generated_at || '',
  });
});

/** GET /graph/cross-links */
app.get('/cross-links', (c) => {
  const domain = c.req.query('domain');
  const conceptId = c.req.query('concept_id');
  let links = (crossSphereLinks as any).links || [];
  if (domain) links = links.filter((lk: any) => lk.source_domain === domain || lk.target_domain === domain);
  if (conceptId) links = links.filter((lk: any) => lk.source_id === conceptId || lk.target_id === conceptId);
  return c.json({ links, total: links.length });
});

export default app;
