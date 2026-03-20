"""Phase 18 Integration Tests — Game Design Knowledge Sphere

Verifies:
1. Seed graph integrity (250 concepts, 274 edges, 12 subdomains, 0 orphans)
2. RAG coverage (250 docs, one per concept)
3. Socratic engine game-design domain adaptation
4. Evaluator game-design domain adaptation
5. Cross-sphere links include game-design
6. Domain registry includes game-design
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
SEED_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "game-design", "seed_graph.json")
RAG_INDEX_PATH = os.path.join(PROJECT_ROOT, "data", "rag", "game-design", "_index.json")
RAG_DIR = os.path.join(PROJECT_ROOT, "data", "rag", "game-design")
CROSS_LINKS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "cross_sphere_links.json")
DOMAINS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "domains.json")


# ── 1. Seed Graph Integrity ──

def _load_seed():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_seed_concept_count():
    seed = _load_seed()
    assert len(seed["concepts"]) == 250


def test_seed_edge_count():
    seed = _load_seed()
    assert len(seed["edges"]) == 274


def test_seed_subdomain_count():
    seed = _load_seed()
    assert len(seed["subdomains"]) == 12


def test_seed_milestone_count():
    seed = _load_seed()
    milestones = [c for c in seed["concepts"] if c.get("is_milestone")]
    assert len(milestones) == 34


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
        assert c["domain_id"] == "game-design", f"Wrong domain_id for {c['id']}"


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
    assert len(idx["documents"]) == 250


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

def test_socratic_game_design_supplement_exists():
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
    assert "game-design" in DOMAIN_SUPPLEMENTS
    assert "游戏设计教学特殊规则" in DOMAIN_SUPPLEMENTS["game-design"]


def test_socratic_game_design_supplement_content():
    from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
    supp = DOMAIN_SUPPLEMENTS["game-design"]
    assert "案例驱动" in supp
    assert "系统思维" in supp
    assert "玩家中心" in supp
    assert "迭代思维" in supp


# ── 3b. Evaluator Adaptation ──

def test_evaluator_game_design_supplement_exists():
    from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
    assert "game-design" in ASSESSMENT_SUPPLEMENTS
    assert "游戏设计领域评估特殊指标" in ASSESSMENT_SUPPLEMENTS["game-design"]


def test_evaluator_game_design_supplement_content():
    from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
    supp = ASSESSMENT_SUPPLEMENTS["game-design"]
    assert "案例运用" in supp
    assert "系统理解" in supp
    assert "玩家视角" in supp


# ── 4. Cross-Sphere Links ──

def test_cross_links_include_game_design():
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    gd_links = [
        lk for lk in data["links"]
        if lk["source_domain"] == "game-design" or lk["target_domain"] == "game-design"
    ]
    assert len(gd_links) >= 15


def test_cross_links_game_design_concepts_valid():
    """All game-design concepts in cross-links should exist in seed graph."""
    seed = _load_seed()
    concept_ids = {c["id"] for c in seed["concepts"]}
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for lk in data["links"]:
        if lk["source_domain"] == "game-design":
            assert lk["source_id"] in concept_ids, f"Missing: {lk['source_id']}"
        if lk["target_domain"] == "game-design":
            assert lk["target_id"] in concept_ids, f"Missing: {lk['target_id']}"


def test_cross_links_game_design_multi_domain():
    """Game-design cross-links should span multiple target domains."""
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    target_domains = set()
    for lk in data["links"]:
        if lk["source_domain"] == "game-design":
            target_domains.add(lk["target_domain"])
    assert len(target_domains) >= 4, f"Only links to {target_domains}"


# ── 5. Domain Registry ──

def test_domains_registry_includes_game_design():
    with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    domain_ids = [d["id"] for d in data["domains"]]
    assert "game-design" in domain_ids


def test_domains_registry_game_design_color():
    with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    gd = next(d for d in data["domains"] if d["id"] == "game-design")
    assert gd["color"] == "#dc2626"
    assert gd["icon"] == "🎮"


# ── 6. API Integration ──

@pytest.mark.asyncio
async def test_api_graph_data():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=game-design")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 250


@pytest.mark.asyncio
async def test_api_subdomains():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/subdomains?domain=game-design")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 12


@pytest.mark.asyncio
async def test_api_stats():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/stats?domain=game-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["stats"]["total_concepts"] == 250
        assert data["stats"]["total_edges"] == 274


@pytest.mark.asyncio
async def test_api_cross_links_game_design_filter():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=game-design")
        assert resp.status_code == 200
        data = resp.json()
        links = data.get("links", data) if isinstance(data, dict) else data
        assert len(links) >= 15


@pytest.mark.asyncio
async def test_api_rag_stats():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag?domain=game-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_docs"] == 250
        assert data["domain"] == "game-design"


@pytest.mark.asyncio
async def test_api_rag_concept():
    """Should return RAG content for a game-design concept."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/gd-overview?domain=game-design")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "gd-overview"
        assert data["domain"] == "game-design"
        assert "核心内容" in data["content"]


@pytest.mark.asyncio
async def test_api_concept_detail():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=game-design")
        assert resp.status_code == 200
        data = resp.json()
        # Pick first node and verify structure
        node = data["nodes"][0]
        assert node["domain_id"] == "game-design"
        assert "id" in node
        assert "label" in node
