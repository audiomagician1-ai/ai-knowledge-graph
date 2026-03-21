"""Phase 15 Integration Tests — Biology Knowledge Sphere

Verifies:
1. Seed graph integrity (172 concepts, 203 edges, 8 subdomains, 0 orphans)
2. RAG coverage (172 docs, one per concept)
3. Socratic engine biology domain adaptation
4. Evaluator biology domain adaptation
5. Cross-sphere links include biology
6. Domain registry includes biology
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
SEED_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "biology", "seed_graph.json")
RAG_INDEX_PATH = os.path.join(PROJECT_ROOT, "data", "rag", "biology", "_index.json")
RAG_DIR = os.path.join(PROJECT_ROOT, "data", "rag", "biology")
CROSS_LINKS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "cross_sphere_links.json")
DOMAINS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "domains.json")


# ── 1. Seed Graph Integrity ──

def _load_seed():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_seed_concept_count():
    seed = _load_seed()
    assert len(seed["concepts"]) == 172


def test_seed_edge_count():
    seed = _load_seed()
    assert len(seed["edges"]) == 203


def test_seed_subdomain_count():
    seed = _load_seed()
    assert len(seed["subdomains"]) == 8


def test_seed_milestone_count():
    seed = _load_seed()
    milestones = [c for c in seed["concepts"] if c.get("is_milestone")]
    assert len(milestones) == 36


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
        assert c["domain_id"] == "biology", f"Wrong domain_id for {c['id']}"


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
    assert len(idx["documents"]) == 172


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
        # v1 docs use "核心内容", v2 research-rewrite docs use "##" markdown headers
        has_header = "核心内容" in content or "## " in content
        assert has_header, f"RAG doc missing header: {doc['file']}"


# ── 3. Socratic Engine Adaptation ──

def test_socratic_biology_supplement_exists():
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
    assert "biology" in DOMAIN_SUPPLEMENTS
    assert "生物学教学特殊规则" in DOMAIN_SUPPLEMENTS["biology"]


def test_socratic_biology_supplement_content():
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
    supp = DOMAIN_SUPPLEMENTS["biology"]
    assert "实验驱动" in supp
    assert "多尺度联系" in supp
    assert "进化视角" in supp
    assert "医学关联" in supp


# ── 3. Evaluator Adaptation ──

def test_evaluator_biology_supplement_exists():
    from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
    assert "biology" in ASSESSMENT_SUPPLEMENTS
    assert "生物学领域评估特殊指标" in ASSESSMENT_SUPPLEMENTS["biology"]


def test_evaluator_biology_supplement_content():
    from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
    supp = ASSESSMENT_SUPPLEMENTS["biology"]
    assert "机制理解" in supp
    assert "尺度贯通" in supp
    assert "进化推理" in supp


# ── 4. Cross-Sphere Links ──

def test_cross_links_include_biology():
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    bio_links = [
        lk for lk in data["links"]
        if lk["source_domain"] == "biology" or lk["target_domain"] == "biology"
    ]
    assert len(bio_links) >= 15


def test_cross_links_biology_concepts_valid():
    """All biology concepts in cross-links should exist in seed graph."""
    seed = _load_seed()
    concept_ids = {c["id"] for c in seed["concepts"]}
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for lk in data["links"]:
        if lk["source_domain"] == "biology":
            assert lk["source_id"] in concept_ids, f"Missing: {lk['source_id']}"
        if lk["target_domain"] == "biology":
            assert lk["target_id"] in concept_ids, f"Missing: {lk['target_id']}"


def test_cross_links_biology_multi_domain():
    """Biology cross-links should span multiple target domains."""
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    target_domains = set()
    for lk in data["links"]:
        if lk["source_domain"] == "biology":
            target_domains.add(lk["target_domain"])
    assert len(target_domains) >= 4, f"Only links to {target_domains}"


# ── 5. Domain Registry ──

def test_domains_registry_includes_biology():
    with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    domain_ids = [d["id"] for d in data["domains"]]
    assert "biology" in domain_ids


def test_domains_registry_biology_color():
    with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    bio = next(d for d in data["domains"] if d["id"] == "biology")
    assert bio["color"] == "#84cc16"
    assert bio["icon"] == "🟤"


# ── 6. API Integration ──

@pytest.mark.asyncio
async def test_api_graph_data():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=biology")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 172


@pytest.mark.asyncio
async def test_api_subdomains():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=biology")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 8


@pytest.mark.asyncio
async def test_api_stats():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=biology")
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["total_concepts"] == 172
        assert data["stats"]["total_edges"] == 203


@pytest.mark.asyncio
async def test_api_cross_links_biology_filter():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=biology")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 15


@pytest.mark.asyncio
async def test_api_rag_stats():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=biology")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 172


@pytest.mark.asyncio
async def test_api_rag_concept():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/cell-biology-overview?domain=biology")
        assert resp.status_code == 200
        data = resp.json()
        assert "核心内容" in data["content"]
