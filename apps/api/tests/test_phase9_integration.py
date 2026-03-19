"""Phase 9 Integration Tests — English Knowledge Sphere end-to-end verification.

Tests the complete Phase 9 feature set:
- 9.1 Seed graph integrity (200 concepts, 229 edges, 10 subdomains)
- 9.2 RAG document coverage (200 teaching docs)
- 9.3 Socratic engine domain adaptation (ENGLISH_DOMAIN_SUPPLEMENT)
- 9.4 Evaluator domain adaptation (ENGLISH_ASSESSMENT_SUPPLEMENT)
- 9.5 Cross-sphere links (AI↔English, Math↔English)
- 9.6 This file — integration testing
"""

import json
import os
import pytest
from httpx import AsyncClient, ASGITransport
from main import app

transport = ASGITransport(app=app)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# ── 9.1 Seed Graph Integrity ────────────────────────────


class TestEnglishSeedIntegrity:
    """Verify English seed graph data integrity."""

    @pytest.fixture(autouse=True)
    def load_seed(self):
        path = os.path.join(PROJECT_ROOT, "data", "seed", "english", "seed_graph.json")
        with open(path, "r", encoding="utf-8") as f:
            self.seed = json.load(f)

    def test_concept_count(self):
        assert len(self.seed["concepts"]) == 200

    def test_edge_count(self):
        assert len(self.seed["edges"]) == 229

    def test_subdomain_count(self):
        assert len(self.seed["subdomains"]) == 10

    def test_milestone_count(self):
        milestones = [c for c in self.seed["concepts"] if c.get("is_milestone")]
        assert len(milestones) == 27

    def test_no_orphan_nodes(self):
        """Every concept must be connected to at least one edge."""
        connected = set()
        for e in self.seed["edges"]:
            connected.add(e["source_id"])
            connected.add(e["target_id"])
        all_ids = {c["id"] for c in self.seed["concepts"]}
        orphans = all_ids - connected
        assert orphans == set(), f"Orphan nodes: {orphans}"

    def test_all_edges_reference_valid_concepts(self):
        """All edge endpoints must reference existing concept IDs."""
        valid_ids = {c["id"] for c in self.seed["concepts"]}
        for e in self.seed["edges"]:
            assert e["source_id"] in valid_ids, f"Edge source {e['source_id']} not found"
            assert e["target_id"] in valid_ids, f"Edge target {e['target_id']} not found"

    def test_all_subdomains_have_concepts(self):
        """Each subdomain should have at least one concept."""
        subdomain_ids = {s["id"] for s in self.seed["subdomains"]}
        concept_subdomains = {c["subdomain_id"] for c in self.seed["concepts"]}
        empty = subdomain_ids - concept_subdomains
        assert empty == set(), f"Empty subdomains: {empty}"

    def test_domain_id_consistency(self):
        """All concepts must have domain_id='english'."""
        for c in self.seed["concepts"]:
            assert c["domain_id"] == "english", f"Concept {c['id']} has domain {c['domain_id']}"

    def test_required_concept_fields(self):
        """Each concept must have all required fields."""
        required = {"id", "name", "domain_id", "subdomain_id", "difficulty", "estimated_minutes", "content_type", "tags"}
        for c in self.seed["concepts"]:
            missing = required - set(c.keys())
            assert not missing, f"Concept {c['id']} missing fields: {missing}"


# ── 9.2 RAG Document Coverage ───────────────────────────


class TestEnglishRAGCoverage:
    """Verify RAG document coverage for English domain."""

    @pytest.fixture(autouse=True)
    def load_data(self):
        seed_path = os.path.join(PROJECT_ROOT, "data", "seed", "english", "seed_graph.json")
        with open(seed_path, "r", encoding="utf-8") as f:
            self.seed = json.load(f)
        self.rag_dir = os.path.join(PROJECT_ROOT, "data", "rag", "english")

    def test_rag_directory_exists(self):
        assert os.path.isdir(self.rag_dir)

    def test_every_concept_has_rag_doc(self):
        """Every seed concept must have a corresponding RAG markdown file."""
        missing = []
        for c in self.seed["concepts"]:
            subdomain = c["subdomain_id"]
            # RAG files are named by concept ID with .md extension
            doc_path = os.path.join(self.rag_dir, subdomain, f"{c['id']}.md")
            if not os.path.exists(doc_path):
                missing.append(f"{subdomain}/{c['id']}.md")
        assert not missing, f"Missing RAG docs: {missing[:10]}..."

    def test_rag_docs_not_empty(self):
        """RAG docs should have meaningful content (>100 chars)."""
        short = []
        for c in self.seed["concepts"][:20]:  # Sample first 20
            subdomain = c["subdomain_id"]
            doc_path = os.path.join(self.rag_dir, subdomain, f"{c['id']}.md")
            if os.path.exists(doc_path):
                with open(doc_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if len(content) < 100:
                    short.append(c["id"])
        assert not short, f"Too-short RAG docs: {short}"


# ── 9.3 Socratic Engine Adaptation ──────────────────────


class TestEnglishSocraticAdaptation:
    """Verify Socratic engine properly handles English domain."""

    def test_english_supplement_exists(self):
        from engines.dialogue.prompts.feynman_system import ENGLISH_DOMAIN_SUPPLEMENT
        assert "双语讲解" in ENGLISH_DOMAIN_SUPPLEMENT
        assert "不要使用LaTeX" in ENGLISH_DOMAIN_SUPPLEMENT

    @pytest.mark.asyncio
    async def test_english_supplement_injected_in_socratic(self):
        """Socratic engine should inject English supplement for English concepts."""
        from engines.dialogue.socratic import socratic_engine
        from engines.dialogue.prompts.feynman_system import ENGLISH_DOMAIN_SUPPLEMENT

        concept = {
            "id": "present-simple",
            "name": "一般现在时",
            "domain_id": "english",
            "subdomain_id": "tenses",
            "subdomain_name": "时态系统",
            "difficulty": 2,
            "content_type": "theory",
            "is_milestone": False,
        }
        prompt = await socratic_engine.build_system_prompt(concept, [], [], [])
        assert "英语教学特殊规则" in prompt
        assert "双语讲解" in prompt

    @pytest.mark.asyncio
    async def test_math_supplement_not_in_english(self):
        """English concepts should not get math supplement."""
        from engines.dialogue.socratic import socratic_engine

        concept = {
            "id": "present-simple",
            "name": "一般现在时",
            "domain_id": "english",
            "subdomain_id": "tenses",
            "subdomain_name": "时态系统",
            "difficulty": 2,
            "content_type": "theory",
            "is_milestone": False,
        }
        prompt = await socratic_engine.build_system_prompt(concept, [], [], [])
        assert "数学教学特殊规则" not in prompt


# ── 9.4 Evaluator Domain Adaptation ─────────────────────


class TestEnglishEvaluatorAdaptation:
    """Verify evaluator handles English-specific assessment."""

    def test_english_assessment_supplement_exists(self):
        from engines.dialogue.prompts.feynman_system import ENGLISH_ASSESSMENT_SUPPLEMENT
        assert "英语领域评估特殊指标" in ENGLISH_ASSESSMENT_SUPPLEMENT
        assert "语法准确性" in ENGLISH_ASSESSMENT_SUPPLEMENT

    def test_evaluator_generates_domain_prompt(self):
        """Evaluator should format prompt with English assessment supplement."""
        from engines.dialogue.prompts.feynman_system import (
            ASSESSMENT_SYSTEM_PROMPT,
            ENGLISH_ASSESSMENT_SUPPLEMENT,
        )
        prompt = ASSESSMENT_SYSTEM_PROMPT.format(
            concept_name="一般现在时",
            difficulty=3,
            domain_assessment_supplement=ENGLISH_ASSESSMENT_SUPPLEMENT,
        )
        assert "英语领域评估" in prompt
        assert "一般现在时" in prompt
        assert "3/9" in prompt

    def test_fallback_evaluator_works_with_english(self):
        """Fallback evaluator should handle English dialogue."""
        from engines.dialogue.evaluator import evaluator
        messages = [
            {"role": "assistant", "content": "Let's learn about present simple tense. 一般现在时用于..."},
            {"role": "user", "content": "一般现在时表示经常发生的动作，比如 'I go to school every day.'"},
            {"role": "assistant", "content": "说得好！注意第三人称单数要加s。"},
            {"role": "user", "content": "对，比如 'She goes to school.' 第三人称单数要在动词后加s或es。"},
        ]
        result = evaluator._fallback_evaluate(messages)
        assert result["overall_score"] > 0
        assert "mastered" in result


# ── 9.5 Cross-Sphere Links ──────────────────────────────


class TestCrossSphereIntegration:
    """Verify cross-sphere links integrate with other APIs."""

    @pytest.mark.asyncio
    async def test_cross_links_english_concepts_accessible(self):
        """English concepts referenced in cross-links should be accessible via concept API."""
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            links_resp = await client.get("/api/graph/cross-links?domain=english")
            links = links_resp.json()["links"]
            assert len(links) > 0

            # Check first English concept is accessible
            for link in links:
                if link["target_domain"] == "english":
                    resp = await client.get(f"/api/graph/concepts/{link['target_id']}?domain=english")
                    assert resp.status_code == 200, f"Concept {link['target_id']} not accessible"
                    break

    @pytest.mark.asyncio
    async def test_cross_links_bidirectional_consistency(self):
        """AI→English and English→AI links should both be findable."""
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/graph/cross-links?domain=english")
            data = resp.json()
            # Should have links where English is source AND where English is target
            as_source = [lk for lk in data["links"] if lk["source_domain"] == "english"]
            as_target = [lk for lk in data["links"] if lk["target_domain"] == "english"]
            assert len(as_source) > 0, "No links where English is source"
            assert len(as_target) > 0, "No links where English is target"

    @pytest.mark.asyncio
    async def test_three_domains_fully_connected(self):
        """All three domain pairs should have at least one link."""
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/graph/cross-links")
            links = resp.json()["links"]
            pairs = set()
            for lk in links:
                pairs.add((lk["source_domain"], lk["target_domain"]))
            # Should have AI↔Math, AI↔English, and Math direction
            assert ("ai-engineering", "mathematics") in pairs
            assert ("ai-engineering", "english") in pairs
            assert ("mathematics", "ai-engineering") in pairs
            assert ("english", "ai-engineering") in pairs


# ── End-to-End Domain Pipeline ──────────────────────────


class TestEnglishDomainPipeline:
    """End-to-end verification of the English domain pipeline."""

    @pytest.mark.asyncio
    async def test_domain_registry_includes_english(self):
        """Domain registry should list English with correct metadata."""
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.get("/api/graph/domains")
            domains = resp.json()
            eng = next((d for d in domains if d["id"] == "english"), None)
            assert eng is not None
            assert eng["name"] == "英语"
            assert eng["icon"] == "🟡"
            assert eng["color"] == "#eab308"
            assert eng["stats"]["total_concepts"] == 200
            assert eng["stats"]["total_edges"] == 229
            assert eng["stats"]["subdomains"] == 10

    @pytest.mark.asyncio
    async def test_full_pipeline_graph_to_rag(self):
        """Complete pipeline: domain list → graph data → concept detail → RAG doc."""
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Domain list
            domains_resp = await client.get("/api/graph/domains")
            assert any(d["id"] == "english" for d in domains_resp.json())

            # 2. Graph data
            graph_resp = await client.get("/api/graph/data?domain=english")
            nodes = graph_resp.json()["nodes"]
            assert len(nodes) == 200

            # 3. Pick a concept
            concept_id = nodes[0]["id"]
            concept_resp = await client.get(f"/api/graph/concepts/{concept_id}?domain=english")
            assert concept_resp.status_code == 200
            concept = concept_resp.json()
            assert concept["domain_id"] == "english"

            # 4. RAG doc
            rag_resp = await client.get(f"/api/graph/rag/{concept_id}?domain=english")
            assert rag_resp.status_code == 200
            assert len(rag_resp.json()["content"]) > 50

            # 5. Cross-links for this concept
            links_resp = await client.get(f"/api/graph/cross-links?concept_id={concept_id}")
            # Some concepts may not have cross-links, that's OK
            assert links_resp.status_code == 200
