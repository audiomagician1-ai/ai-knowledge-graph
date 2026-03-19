"""Phase 12 Integration Tests — Finance Knowledge Sphere

Verifies:
1. Seed graph integrity (160 concepts, 182 edges, 8 subdomains, 0 orphans)
2. RAG coverage (160 docs, one per concept)
3. Socratic engine finance domain adaptation
4. Evaluator finance domain adaptation
5. Cross-sphere links include finance
6. Domain registry includes finance
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
SEED_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "finance", "seed_graph.json")
RAG_INDEX_PATH = os.path.join(PROJECT_ROOT, "data", "rag", "finance", "_index.json")
RAG_DIR = os.path.join(PROJECT_ROOT, "data", "rag", "finance")
CROSS_LINKS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "cross_sphere_links.json")
DOMAINS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "domains.json")


# ── 1. Seed Graph Integrity ──

def _load_seed():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def test_seed_concept_count():
    seed = _load_seed()
    assert len(seed["concepts"]) == 160


def test_seed_edge_count():
    seed = _load_seed()
    assert len(seed["edges"]) == 182


def test_seed_subdomain_count():
    seed = _load_seed()
    assert len(seed["subdomains"]) == 8


def test_seed_milestone_count():
    seed = _load_seed()
    milestones = [c for c in seed["concepts"] if c.get("is_milestone")]
    assert len(milestones) == 32


def test_seed_no_orphan_nodes():
    seed = _load_seed()
    ids = {c["id"] for c in seed["concepts"]}
    connected = set()
    for e in seed["edges"]:
        connected.add(e["source_id"])
        connected.add(e["target_id"])
    orphans = ids - connected
    assert len(orphans) == 0, f"Orphan nodes: {orphans}"


def test_seed_domain_id_consistent():
    seed = _load_seed()
    for c in seed["concepts"]:
        assert c["domain_id"] == "finance", f"Concept {c['id']} has wrong domain_id: {c['domain_id']}"


def test_seed_subdomains_used():
    """Every subdomain should have at least one concept."""
    seed = _load_seed()
    subdomain_ids = {s["id"] for s in seed["subdomains"]}
    used_subdomains = {c["subdomain_id"] for c in seed["concepts"]}
    unused = subdomain_ids - used_subdomains
    assert len(unused) == 0, f"Unused subdomains: {unused}"


def test_seed_edges_reference_valid_concepts():
    seed = _load_seed()
    ids = {c["id"] for c in seed["concepts"]}
    for e in seed["edges"]:
        assert e["source_id"] in ids, f"Edge source {e['source_id']} not found"
        assert e["target_id"] in ids, f"Edge target {e['target_id']} not found"


# ── 2. RAG Coverage ──

def test_rag_index_exists():
    assert os.path.exists(RAG_INDEX_PATH), f"RAG index not found: {RAG_INDEX_PATH}"


def test_rag_doc_count():
    with open(RAG_INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)
    assert len(index["documents"]) == 160


def test_rag_files_exist():
    """Every RAG index entry should have a corresponding file."""
    with open(RAG_INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)
    rag_base = os.path.dirname(RAG_DIR)  # data/rag/
    missing = []
    for doc in index["documents"]:
        path = os.path.join(rag_base, doc["file"])
        if not os.path.exists(path):
            missing.append(doc["file"])
    assert len(missing) == 0, f"Missing RAG files: {missing[:5]}..."


def test_rag_covers_all_concepts():
    """Every concept in seed should have a RAG doc."""
    seed = _load_seed()
    with open(RAG_INDEX_PATH, "r", encoding="utf-8") as f:
        index = json.load(f)
    rag_ids = {d["id"] for d in index["documents"]}
    concept_ids = {c["id"] for c in seed["concepts"]}
    missing = concept_ids - rag_ids
    assert len(missing) == 0, f"Concepts without RAG: {missing}"


# ── 3. Socratic Engine Adaptation ──

def test_socratic_finance_supplement_exists():
    from engines.dialogue.prompts.feynman_system import FINANCE_DOMAIN_SUPPLEMENT
    assert "金融" in FINANCE_DOMAIN_SUPPLEMENT or "风险意识" in FINANCE_DOMAIN_SUPPLEMENT


@pytest.mark.asyncio
async def test_socratic_finance_supplement_injected():
    from engines.dialogue.socratic import SocraticEngine
    engine = SocraticEngine()
    concept = {
        "id": "compound-interest",
        "name": "复利效应",
        "domain_id": "finance",
        "subdomain_id": "personal-finance",
        "difficulty": 1,
        "content_type": "theory",
        "is_milestone": True,
    }
    prompt = await engine.build_system_prompt(concept)
    assert "金融" in prompt or "风险意识" in prompt


# ── 4. Evaluator Adaptation ──

def test_evaluator_finance_supplement_exists():
    from engines.dialogue.prompts.feynman_system import FINANCE_ASSESSMENT_SUPPLEMENT
    assert "金融" in FINANCE_ASSESSMENT_SUPPLEMENT or "风险意识" in FINANCE_ASSESSMENT_SUPPLEMENT


# ── 5. Cross-Sphere Links ──

def test_cross_links_include_finance():
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    domains_in_links = set()
    for link in data["links"]:
        domains_in_links.add(link["source_domain"])
        domains_in_links.add(link["target_domain"])
    assert "finance" in domains_in_links


def test_cross_links_finance_count():
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    fin_links = [l for l in data["links"] if l["source_domain"] == "finance" or l["target_domain"] == "finance"]
    assert len(fin_links) >= 10


def test_cross_links_finance_concepts_exist():
    """All finance concept IDs in cross-links should exist in seed graph."""
    seed = _load_seed()
    concept_ids = {c["id"] for c in seed["concepts"]}
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    for link in data["links"]:
        if link["source_domain"] == "finance":
            assert link["source_id"] in concept_ids, f"Missing: {link['source_id']}"
        if link["target_domain"] == "finance":
            assert link["target_id"] in concept_ids, f"Missing: {link['target_id']}"


# ── 6. Domain Registry ──

def test_domains_includes_finance():
    with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    domain_ids = [d["id"] for d in data["domains"]]
    assert "finance" in domain_ids


def test_finance_domain_config():
    with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    fin = next(d for d in data["domains"] if d["id"] == "finance")
    assert fin["name"] == "金融理财"
    assert fin["icon"] == "🟠"
    assert fin["color"] == "#f97316"
    assert fin["is_active"] is True


# ── 7. API Integration ──

@pytest.mark.asyncio
async def test_api_graph_data():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/data?domain=finance")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["nodes"]) == 160
        assert len(data["edges"]) == 182


@pytest.mark.asyncio
async def test_api_rag_document():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/rag/compound-interest?domain=finance")
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_id"] == "compound-interest"
        assert len(data["content"]) > 100


@pytest.mark.asyncio
async def test_api_cross_links():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/graph/cross-links?domain=finance")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["links"]) >= 10


@pytest.mark.asyncio
async def test_api_full_pipeline():
    """Full pipeline: domains → graph data → concept detail → RAG doc → cross-links."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Domain list includes finance
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        domain_ids = [d["id"] for d in resp.json()]
        assert "finance" in domain_ids

        # Step 2: Finance graph data loads
        resp = await client.get("/api/graph/data?domain=finance")
        assert resp.status_code == 200
        assert len(resp.json()["nodes"]) == 160

        # Step 3: Concept detail works
        resp = await client.get("/api/graph/concepts/time-value-of-money?domain=finance")
        assert resp.status_code == 200
        assert resp.json()["domain_id"] == "finance"

        # Step 4: RAG doc loads
        resp = await client.get("/api/graph/rag/time-value-of-money?domain=finance")
        assert resp.status_code == 200
        assert len(resp.json()["content"]) > 50

        # Step 5: Cross-links include finance
        resp = await client.get("/api/graph/cross-links?domain=finance")
        assert resp.status_code == 200
        assert len(resp.json()["links"]) >= 10
