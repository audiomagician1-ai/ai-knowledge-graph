"""Phase 13 Integration Tests — Psychology Knowledge Sphere

Verifies:
1. Seed graph integrity (183 concepts, 203 edges, 8 subdomains, 0 orphans)
2. RAG coverage (183 docs, one per concept)
3. Socratic engine psychology domain adaptation
4. Evaluator psychology domain adaptation
5. Cross-sphere links include psychology
6. Domain registry includes psychology
7. API integration end-to-end
"""

import json
import os
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

transport = ASGITransport(app=app)

# ── Paths ──

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.dirname(ROOT))
SEED_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "psychology", "seed_graph.json")
RAG_INDEX_PATH = os.path.join(PROJECT_ROOT, "data", "rag", "psychology", "_index.json")
RAG_DIR = os.path.join(PROJECT_ROOT, "data", "rag", "psychology")
CROSS_LINKS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "cross_sphere_links.json")
DOMAINS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "domains.json")


# ── 1. Seed Graph Integrity ──

def _load_seed():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_seed_concept_count():
    seed = _load_seed()
    assert len(seed["concepts"]) == 183


def test_seed_edge_count():
    seed = _load_seed()
    assert len(seed["edges"]) == 203


def test_seed_subdomain_count():
    seed = _load_seed()
    assert len(seed["subdomains"]) == 8


def test_seed_milestone_count():
    seed = _load_seed()
    milestones = [c for c in seed["concepts"] if c.get("is_milestone")]
    assert len(milestones) == 41


def test_seed_no_orphan_nodes():
    """Every concept should be connected to at least one edge."""
    seed = _load_seed()
    edge_nodes = set()
    for e in seed["edges"]:
        edge_nodes.add(e["source_id"])
        edge_nodes.add(e["target_id"])
    concept_ids = {c["id"] for c in seed["concepts"]}
    orphans = concept_ids - edge_nodes
    # Allow overview nodes that may only be targets
    assert len(orphans) == 0, f"Orphan nodes: {orphans}"


def test_seed_no_dangling_edges():
    """Every edge should reference existing concepts."""
    seed = _load_seed()
    concept_ids = {c["id"] for c in seed["concepts"]}
    for e in seed["edges"]:
        assert e["source_id"] in concept_ids, f"Dangling source: {e['source_id']}"
        assert e["target_id"] in concept_ids, f"Dangling target: {e['target_id']}"


def test_seed_all_concepts_have_domain_id():
    seed = _load_seed()
    for c in seed["concepts"]:
        assert c["domain_id"] == "psychology", f"Wrong domain_id for {c['id']}"


def test_seed_subdomains_coverage():
    """Every concept belongs to a declared subdomain."""
    seed = _load_seed()
    valid_subs = {s["id"] for s in seed["subdomains"]}
    for c in seed["concepts"]:
        assert c["subdomain_id"] in valid_subs, f"{c['id']} has invalid subdomain {c['subdomain_id']}"


# ── 2. RAG Coverage ──

def _load_rag_index():
    with open(RAG_INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_rag_doc_count():
    idx = _load_rag_index()
    assert len(idx["documents"]) == 183


def test_rag_one_per_concept():
    seed = _load_seed()
    idx = _load_rag_index()
    concept_ids = {c["id"] for c in seed["concepts"]}
    rag_ids = {d["id"] for d in idx["documents"]}
    missing = concept_ids - rag_ids
    assert len(missing) == 0, f"Missing RAG docs: {missing}"


def test_rag_files_exist():
    idx = _load_rag_index()
    rag_base = os.path.join(PROJECT_ROOT, "data", "rag")
    for doc in idx["documents"]:
        fpath = os.path.join(rag_base, doc["file"])
        assert os.path.exists(fpath), f"RAG file missing: {doc['file']}"


def test_rag_docs_non_empty():
    idx = _load_rag_index()
    rag_base = os.path.join(PROJECT_ROOT, "data", "rag")
    for doc in idx["documents"][:10]:  # Check first 10
        fpath = os.path.join(rag_base, doc["file"])
        content = open(fpath, "r", encoding="utf-8").read()
        assert len(content) > 100, f"RAG doc too short: {doc['file']}"
        assert "核心内容" in content or "## " in content, f"RAG doc missing header: {doc['file']}"


# ── 3. Socratic Engine Adaptation ──

def test_socratic_psychology_supplement_exists():
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
    assert "psychology" in DOMAIN_SUPPLEMENTS
    assert "心理学教学特殊规则" in DOMAIN_SUPPLEMENTS["psychology"]


def test_socratic_psychology_supplement_content():
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
    supp = DOMAIN_SUPPLEMENTS["psychology"]
    assert "经典实验" in supp
    assert "批判性思维" in supp
    assert "去污名化" in supp


# ── 4. Evaluator Adaptation ──

def test_evaluator_psychology_supplement_exists():
    from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
    assert "psychology" in ASSESSMENT_SUPPLEMENTS
    assert "心理学领域评估特殊指标" in ASSESSMENT_SUPPLEMENTS["psychology"]


def test_evaluator_psychology_supplement_content():
    from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
    supp = ASSESSMENT_SUPPLEMENTS["psychology"]
    assert "概念精确性" in supp
    assert "实验理解" in supp
    assert "伦理意识" in supp


# ── 5. Cross-Sphere Links ──

def test_cross_links_include_psychology():
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    psych_links = [
        lk for lk in data["links"]
        if lk["source_domain"] == "psychology" or lk["target_domain"] == "psychology"
    ]
    assert len(psych_links) >= 15


def test_cross_links_psychology_concepts_valid():
    """All psychology concepts in cross-links should exist in seed graph."""
    seed = _load_seed()
    concept_ids = {c["id"] for c in seed["concepts"]}
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for lk in data["links"]:
        if lk["source_domain"] == "psychology":
            assert lk["source_id"] in concept_ids, f"Missing: {lk['source_id']}"
        if lk["target_domain"] == "psychology":
            assert lk["target_id"] in concept_ids, f"Missing: {lk['target_id']}"


# ── 6. Domain Registry ──

def test_domains_registry_includes_psychology():
    with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    domain_ids = [d["id"] for d in data["domains"]]
    assert "psychology" in domain_ids


def test_domains_registry_psychology_color():
    with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    psych = next(d for d in data["domains"] if d["id"] == "psychology")
    assert psych["color"] == "#a855f7"
    assert psych["icon"] == "💜"


# ── 7. API Integration ──

@pytest.mark.asyncio
async def test_api_graph_data():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 183


@pytest.mark.asyncio
async def test_api_subdomains():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 8


@pytest.mark.asyncio
async def test_api_rag_stats():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 183


@pytest.mark.asyncio
async def test_api_rag_concept():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/classical-conditioning?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert "核心内容" in data["content"] or "## " in data["content"]
@pytest.mark.asyncio
async def test_api_cross_links_psychology_filter():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=psychology")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 15
