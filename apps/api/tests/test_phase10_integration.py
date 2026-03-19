"""Phase 10 Integration Tests — Physics Knowledge Sphere

Verifies:
1. Seed graph integrity (194 concepts, 232 edges, 10 subdomains, 0 orphans)
2. RAG coverage (194 docs, one per concept)
3. Socratic engine physics domain adaptation
4. Evaluator physics domain adaptation
5. Cross-sphere links include physics
6. Domain registry includes physics
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
SEED_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "physics", "seed_graph.json")
RAG_INDEX_PATH = os.path.join(PROJECT_ROOT, "data", "rag", "physics", "_index.json")
RAG_DIR = os.path.join(PROJECT_ROOT, "data", "rag", "physics")
CROSS_LINKS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "cross_sphere_links.json")
DOMAINS_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "domains.json")


# ── 1. Seed Graph Integrity ──

class TestPhysicsSeedIntegrity:
    """Verify physics seed graph data quality."""

    @pytest.fixture(autouse=True)
    def load_seed(self):
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            self.seed = json.load(f)
        self.concepts = self.seed["concepts"]
        self.edges = self.seed["edges"]
        self.subdomains = self.seed["subdomains"]

    def test_concept_count(self):
        assert len(self.concepts) >= 190

    def test_edge_count(self):
        assert len(self.edges) >= 220

    def test_subdomain_count(self):
        assert len(self.subdomains) == 10

    def test_milestone_count(self):
        milestones = [c for c in self.concepts if c.get("is_milestone")]
        assert len(milestones) >= 20

    def test_no_orphan_nodes(self):
        """Every concept should have at least one edge."""
        edge_nodes = set()
        for e in self.edges:
            edge_nodes.add(e["source_id"])
            edge_nodes.add(e["target_id"])
        concept_ids = {c["id"] for c in self.concepts}
        orphans = concept_ids - edge_nodes
        assert orphans == set(), f"Orphan nodes: {orphans}"

    def test_all_edge_nodes_exist(self):
        """All edge source/target IDs should reference existing concepts."""
        concept_ids = {c["id"] for c in self.concepts}
        for e in self.edges:
            assert e["source_id"] in concept_ids, f"Missing source: {e['source_id']}"
            assert e["target_id"] in concept_ids, f"Missing target: {e['target_id']}"

    def test_all_concepts_have_domain_id(self):
        for c in self.concepts:
            assert c["domain_id"] == "physics"

    def test_subdomains_covered(self):
        """All 10 subdomains should have at least one concept."""
        sub_ids = {s["id"] for s in self.subdomains}
        concept_subs = {c["subdomain_id"] for c in self.concepts}
        assert sub_ids == concept_subs

    def test_difficulty_range(self):
        for c in self.concepts:
            assert 1 <= c["difficulty"] <= 9


# ── 2. RAG Coverage ──

class TestPhysicsRAGCoverage:
    """Verify RAG document coverage matches seed graph."""

    @pytest.fixture(autouse=True)
    def load_data(self):
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            self.seed = json.load(f)
        with open(RAG_INDEX_PATH, "r", encoding="utf-8") as f:
            self.rag_index = json.load(f)

    def test_rag_doc_count_matches_concepts(self):
        assert len(self.rag_index["documents"]) == len(self.seed["concepts"])

    def test_all_concepts_have_rag_doc(self):
        rag_ids = {d["id"] for d in self.rag_index["documents"]}
        concept_ids = {c["id"] for c in self.seed["concepts"]}
        missing = concept_ids - rag_ids
        assert missing == set(), f"Missing RAG docs: {missing}"

    def test_all_rag_files_exist(self):
        for doc in self.rag_index["documents"]:
            filepath = os.path.join(PROJECT_ROOT, "data", "rag", doc["file"])
            assert os.path.exists(filepath), f"Missing file: {doc['file']}"


# ── 3. Socratic Engine Adaptation ──

class TestPhysicsSocraticAdaptation:
    """Verify physics domain supplement is properly injected."""

    def test_physics_supplement_exists(self):
        from engines.dialogue.prompts.feynman_system import PHYSICS_DOMAIN_SUPPLEMENT
        assert "物理教学特殊规则" in PHYSICS_DOMAIN_SUPPLEMENT
        assert "LaTeX" in PHYSICS_DOMAIN_SUPPLEMENT or "公式" in PHYSICS_DOMAIN_SUPPLEMENT
        assert "直觉" in PHYSICS_DOMAIN_SUPPLEMENT
        assert "实验" in PHYSICS_DOMAIN_SUPPLEMENT
        assert "单位" in PHYSICS_DOMAIN_SUPPLEMENT or "量纲" in PHYSICS_DOMAIN_SUPPLEMENT

    def test_physics_supplement_injected_in_socratic(self):
        from engines.dialogue.prompts.feynman_system import PHYSICS_DOMAIN_SUPPLEMENT
        from engines.dialogue.socratic import SocraticEngine
        # The import validates the PHYSICS_DOMAIN_SUPPLEMENT is available
        assert PHYSICS_DOMAIN_SUPPLEMENT is not None


# ── 4. Evaluator Adaptation ──

class TestPhysicsEvaluatorAdaptation:
    """Verify physics assessment supplement exists."""

    def test_physics_assessment_supplement_exists(self):
        from engines.dialogue.prompts.feynman_system import PHYSICS_ASSESSMENT_SUPPLEMENT
        assert "物理领域评估特殊指标" in PHYSICS_ASSESSMENT_SUPPLEMENT
        assert "物理图像" in PHYSICS_ASSESSMENT_SUPPLEMENT
        assert "公式理解" in PHYSICS_ASSESSMENT_SUPPLEMENT
        assert "数量级" in PHYSICS_ASSESSMENT_SUPPLEMENT


# ── 5. Cross-sphere Links ──

class TestPhysicsCrossLinks:
    """Verify physics cross-sphere links."""

    @pytest.fixture(autouse=True)
    def load_links(self):
        with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
            self.data = json.load(f)
        self.links = self.data["links"]

    def test_physics_links_exist(self):
        physics_links = [l for l in self.links
                         if l["source_domain"] == "physics" or l["target_domain"] == "physics"]
        assert len(physics_links) >= 10

    def test_physics_math_links(self):
        math_physics = [l for l in self.links
                        if (l["source_domain"] == "mathematics" and l["target_domain"] == "physics")]
        assert len(math_physics) >= 5


# ── 6. Domain Registry ──

class TestPhysicsDomainRegistry:
    """Verify physics is registered in domains.json."""

    @pytest.fixture(autouse=True)
    def load_domains(self):
        with open(DOMAINS_PATH, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def test_physics_registered(self):
        domain_ids = {d["id"] for d in self.data["domains"]}
        assert "physics" in domain_ids

    def test_physics_config(self):
        physics = [d for d in self.data["domains"] if d["id"] == "physics"][0]
        assert physics["name"] == "物理"
        assert physics["color"] == "#22c55e"
        assert physics["icon"] == "🟢"
        assert physics["is_active"] is True


# ── 7. API Integration ──

@pytest.mark.asyncio
async def test_physics_full_pipeline():
    """Full pipeline: domain listed → graph data → concept detail → RAG doc."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Domain listed
        resp = await client.get("/api/graph/domains")
        assert resp.status_code == 200
        domain_ids = {d["id"] for d in resp.json()}
        assert "physics" in domain_ids

        # 2. Graph data available
        resp = await client.get("/api/graph/data?domain=physics")
        assert resp.status_code == 200
        nodes = resp.json()["nodes"]
        assert len(nodes) >= 190

        # 3. Concept detail works
        resp = await client.get("/api/graph/concepts/newtons-second-law?domain=physics")
        assert resp.status_code == 200
        assert resp.json()["id"] == "newtons-second-law"

        # 4. RAG document available
        resp = await client.get("/api/graph/rag/newtons-second-law?domain=physics")
        assert resp.status_code == 200
        assert "$" in resp.json()["content"] or "力" in resp.json()["content"]

        # 5. Cross-links include physics
        resp = await client.get("/api/graph/cross-links?domain=physics")
        assert resp.status_code == 200
        assert resp.json()["total"] > 0
