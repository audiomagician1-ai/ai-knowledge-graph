"""Phase 17 Integration Tests — Writing Knowledge Sphere

Verifies:
1. Seed graph integrity (170 concepts, 204 edges, 8 subdomains, 0 orphans)
2. RAG coverage (170 docs, one per concept)
3. Socratic engine writing domain adaptation
4. Evaluator writing domain adaptation
5. Cross-sphere links include writing
6. Domain registry includes writing
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
SEED_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "writing", "seed_graph.json")
RAG_INDEX_PATH = os.path.join(PROJECT_ROOT, "data", "rag", "writing", "_index.json")
RAG_DIR = os.path.join(PROJECT_ROOT, "data", "rag", "writing")
CROSS_LINKS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "cross_sphere_links.json")
DOMAINS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "domains.json")


# ── 1. Seed Graph Integrity ──

def _load_seed():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_seed_concept_count():
    seed = _load_seed()
    assert len(seed["concepts"]) == 170


def test_seed_edge_count():
    seed = _load_seed()
    assert len(seed["edges"]) == 204


def test_seed_subdomain_count():
    seed = _load_seed()
    assert len(seed["subdomains"]) == 8


def test_seed_milestone_count():
    seed = _load_seed()
    milestones = [c for c in seed["concepts"] if c.get("is_milestone")]
    assert len(milestones) == 42


def test_seed_no_orphan_nodes():
    """Every concept should be connected to at least one edge."""
    seed = _load_seed()
    edge_nodes = set()
    for e in seed["edges"]:
        edge_nodes.add(e["source_id"])
        edge_nodes.add(e["target_id"])
    concept_ids = {c["id"] for c in seed["concepts"]}
    orphans = concept_ids - edge_nodes
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
        assert c["domain_id"] == "writing", f"Wrong domain_id for {c['id']}"


def test_seed_subdomains_coverage():
    """Every concept belongs to a declared subdomain."""
    seed = _load_seed()
    valid_subs = {s["id"] for s in seed["subdomains"]}
    for c in seed["concepts"]:
        assert c["subdomain_id"] in valid_subs, f"{c['id']} has invalid subdomain {c['subdomain_id']}"


def test_seed_no_duplicate_ids():
    """All concept IDs should be unique."""
    seed = _load_seed()
    ids = [c["id"] for c in seed["concepts"]]
    assert len(ids) == len(set(ids)), "Duplicate concept IDs detected"


# ── 2. RAG Coverage ──

def _load_rag_index():
    with open(RAG_INDEX_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_rag_doc_count():
    idx = _load_rag_index()
    assert len(idx["documents"]) == 170


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
        assert "核心内容" in content, f"RAG doc missing header: {doc['file']}"


# ── 3. Socratic Engine Adaptation ──

def test_socratic_writing_supplement_exists():
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
    assert "writing" in DOMAIN_SUPPLEMENTS
    assert "写作教学特殊规则" in DOMAIN_SUPPLEMENTS["writing"]


def test_socratic_writing_supplement_content():
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
    supp = DOMAIN_SUPPLEMENTS["writing"]
    assert "过程导向" in supp
    assert "读者意识" in supp
    assert "示例驱动" in supp
    assert "练习为本" in supp


# ── 3b. Evaluator Adaptation ──

def test_evaluator_writing_supplement_exists():
    from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
    assert "writing" in ASSESSMENT_SUPPLEMENTS
    assert "写作领域评估特殊指标" in ASSESSMENT_SUPPLEMENTS["writing"]


def test_evaluator_writing_supplement_content():
    from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
    supp = ASSESSMENT_SUPPLEMENTS["writing"]
    assert "技法理解" in supp
    assert "体裁意识" in supp
    assert "修改能力" in supp


# ── 4. Cross-Sphere Links ──

def test_cross_links_include_writing():
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    writing_links = [
        lk for lk in data["links"]
        if lk["source_domain"] == "writing" or lk["target_domain"] == "writing"
    ]
    assert len(writing_links) >= 15


def test_cross_links_writing_concepts_valid():
    """All writing concepts in cross-links should exist in seed graph."""
    seed = _load_seed()
    concept_ids = {c["id"] for c in seed["concepts"]}
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for lk in data["links"]:
        if lk["source_domain"] == "writing":
            assert lk["source_id"] in concept_ids, f"Missing: {lk['source_id']}"
        if lk["target_domain"] == "writing":
            assert lk["target_id"] in concept_ids, f"Missing: {lk['target_id']}"


def test_cross_links_writing_multi_domain():
    """Writing cross-links should span multiple target domains."""
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    target_domains = set()
    for lk in data["links"]:
        if lk["source_domain"] == "writing":
            target_domains.add(lk["target_domain"])
    assert len(target_domains) >= 4, f"Only links to {target_domains}"


# ── 5. Domain Registry ──

def test_domains_registry_includes_writing():
    with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    domain_ids = [d["id"] for d in data["domains"]]
    assert "writing" in domain_ids


def test_domains_registry_writing_color():
    with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    writing = next(d for d in data["domains"] if d["id"] == "writing")
    assert writing["color"] == "#f59e0b"
    assert writing["icon"] == "✍️"


# ── 6. API Integration ──

@pytest.mark.asyncio
async def test_api_graph_data():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=writing")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 170


@pytest.mark.asyncio
async def test_api_subdomains():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=writing")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 8


@pytest.mark.asyncio
async def test_api_stats():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=writing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["total_concepts"] == 170
        assert data["stats"]["total_edges"] == 204


@pytest.mark.asyncio
async def test_api_cross_links_writing_filter():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=writing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 15


@pytest.mark.asyncio
async def test_api_rag_stats():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=writing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 170


@pytest.mark.asyncio
async def test_api_rag_concept():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/writing-overview?domain=writing")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "writing-overview"
        assert len(data["content"]) > 50
