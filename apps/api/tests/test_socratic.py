"""Tests for socratic.py — _load_rag_content, build_system_prompt, _get_rag_dir, get_opening fallback"""

import os
import pytest
import pytest_asyncio
from unittest.mock import patch, AsyncMock

from engines.dialogue.socratic import (
    SocraticEngine,
    _load_rag_content,
    _get_rag_dir,
    OPENING_USER_PROMPT,
)


# ─── _get_rag_dir ───

class TestGetRagDir:
    def test_returns_string(self):
        result = _get_rag_dir()
        assert isinstance(result, str)

    def test_path_ends_with_rag(self):
        result = _get_rag_dir()
        assert result.endswith("rag") or result.endswith("rag_data")

    def test_dev_mode_path_exists(self):
        """In dev mode, rag dir should exist at data/rag relative to project root"""
        result = _get_rag_dir()
        assert os.path.isdir(result), f"RAG dir does not exist: {result}"


# ─── _load_rag_content ───

class TestLoadRagContent:
    def test_existing_concept_returns_content(self):
        """Should load content from a known RAG file"""
        content = _load_rag_content("ai-overview", "ai-foundations")
        assert len(content) > 0
        assert not content.startswith("---")
        assert not content.startswith("# ")

    def test_nonexistent_concept_returns_empty(self):
        content = _load_rag_content("nonexistent-concept-xyz", "nonexistent-subdomain")
        assert content == ""

    def test_nonexistent_subdomain_returns_empty(self):
        content = _load_rag_content("ai-overview", "fake-subdomain")
        assert content == ""

    def test_content_truncated_at_3000(self):
        """Long content should be truncated to ~3000 chars"""
        content = _load_rag_content("ai-overview", "ai-foundations")
        assert len(content) <= 3100

    def test_yaml_frontmatter_stripped(self):
        content = _load_rag_content("ai-overview", "ai-foundations")
        if content:
            assert not content.lstrip().startswith("---")

    def test_h1_title_stripped(self):
        content = _load_rag_content("ai-overview", "ai-foundations")
        if content:
            first_line = content.split("\n")[0]
            assert not first_line.startswith("# ")


# ─── SocraticEngine.build_system_prompt ───

class TestBuildSystemPrompt:
    @pytest.fixture
    def engine(self):
        return SocraticEngine()

    @pytest.fixture
    def sample_concept(self):
        return {
            "id": "neural-network-basics",
            "name": "神经网络基础",
            "subdomain_id": "ai-foundations",
            "subdomain_name": "AI基础",
            "difficulty": 5,
            "content_type": "theory",
            "is_milestone": False,
        }

    @pytest.mark.asyncio
    async def test_basic_prompt_contains_concept_name(self, engine, sample_concept):
        prompt = await engine.build_system_prompt(sample_concept)
        assert "神经网络基础" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_subdomain(self, engine, sample_concept):
        prompt = await engine.build_system_prompt(sample_concept)
        assert "AI基础" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_difficulty(self, engine, sample_concept):
        prompt = await engine.build_system_prompt(sample_concept)
        assert "5/9" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_prerequisites(self, engine, sample_concept):
        prompt = await engine.build_system_prompt(
            sample_concept, prerequisites=["线性代数", "微积分"],
        )
        assert "线性代数" in prompt
        assert "微积分" in prompt

    @pytest.mark.asyncio
    async def test_prompt_no_prerequisites_shows_none(self, engine, sample_concept):
        prompt = await engine.build_system_prompt(sample_concept, prerequisites=[])
        assert "先修概念" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_dependents(self, engine, sample_concept):
        prompt = await engine.build_system_prompt(
            sample_concept, dependents=["深度学习", "CNN"],
        )
        assert "深度学习" in prompt
        assert "CNN" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_related(self, engine, sample_concept):
        prompt = await engine.build_system_prompt(
            sample_concept, related=["感知机", "激活函数"],
        )
        assert "感知机" in prompt
        assert "激活函数" in prompt

    @pytest.mark.asyncio
    async def test_milestone_concept(self, engine):
        concept = {
            "id": "test-milestone", "name": "里程碑概念",
            "subdomain_id": "test", "subdomain_name": "测试",
            "difficulty": 7, "content_type": "practice", "is_milestone": True,
        }
        prompt = await engine.build_system_prompt(concept)
        assert "⭐" in prompt or "里程碑" in prompt

    @pytest.mark.asyncio
    async def test_non_milestone_concept(self, engine, sample_concept):
        prompt = await engine.build_system_prompt(sample_concept)
        assert "否" in prompt

    @pytest.mark.asyncio
    async def test_rag_content_injected_when_available(self, engine):
        concept = {
            "id": "ai-overview", "name": "AI概述",
            "subdomain_id": "ai-foundations", "subdomain_name": "AI基础",
            "difficulty": 3, "content_type": "theory", "is_milestone": False,
        }
        prompt = await engine.build_system_prompt(concept)
        assert "参考知识文档" in prompt

    @pytest.mark.asyncio
    async def test_no_rag_content_for_unknown_concept(self, engine):
        concept = {
            "id": "unknown-concept-xyz", "name": "未知概念",
            "subdomain_id": "nonexistent", "subdomain_name": "不存在的领域",
            "difficulty": 1, "content_type": "theory", "is_milestone": False,
        }
        prompt = await engine.build_system_prompt(concept)
        assert "参考知识文档" not in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_four_phases(self, engine, sample_concept):
        prompt = await engine.build_system_prompt(sample_concept)
        assert "Phase 1" in prompt
        assert "Phase 2" in prompt
        assert "Phase 3" in prompt
        assert "Phase 4" in prompt

    @pytest.mark.asyncio
    async def test_prompt_contains_choices_format(self, engine, sample_concept):
        prompt = await engine.build_system_prompt(sample_concept)
        assert "choices" in prompt
        assert "opt-1" in prompt


# ─── OPENING_USER_PROMPT ───

class TestOpeningPrompt:
    def test_opening_prompt_template(self):
        result = OPENING_USER_PROMPT.format(concept_name="测试概念")
        assert "测试概念" in result
        assert "开始学习" in result


# ─── SocraticEngine.get_opening fallback ───

class TestGetOpeningFallback:
    @pytest.fixture
    def engine(self):
        return SocraticEngine()

    @pytest.mark.asyncio
    async def test_fallback_when_llm_fails(self, engine):
        """When LLM call fails, should return hardcoded fallback"""
        concept = {"id": "test", "name": "测试概念", "is_milestone": False}
        system_prompt = "test system prompt"

        with patch("engines.dialogue.socratic.llm_router") as mock_router:
            mock_router.chat = AsyncMock(side_effect=Exception("LLM unavailable"))
            text, choices = await engine.get_opening(concept, system_prompt)

        assert "测试概念" in text
        assert len(choices) == 4
        assert all(c["type"] == "level" for c in choices)
        assert choices[0]["id"] == "opt-1"


# ─── Math Domain Prompt Adaptation (Phase 8.4) ───

class TestMathDomainPrompt:
    @pytest.fixture
    def engine(self):
        return SocraticEngine()

    @pytest.fixture
    def math_concept(self):
        return {
            "id": "derivative-concept",
            "name": "导数概念",
            "domain_id": "mathematics",
            "subdomain_id": "calculus",
            "subdomain_name": "微积分",
            "difficulty": 5,
            "content_type": "theory",
            "is_milestone": True,
        }

    @pytest.fixture
    def sample_concept(self):
        return {
            "id": "neural-network-basics",
            "name": "神经网络基础",
            "subdomain_id": "ai-foundations",
            "subdomain_name": "AI基础",
            "difficulty": 5,
            "content_type": "theory",
            "is_milestone": False,
        }

    @pytest.mark.asyncio
    async def test_math_prompt_contains_math_supplement(self, engine, math_concept):
        """Math domain should inject MATH_DOMAIN_SUPPLEMENT into prompt."""
        prompt = await engine.build_system_prompt(math_concept)
        assert "数学教学特殊规则" in prompt
        assert "LaTeX" in prompt
        assert "证明引导" in prompt

    @pytest.mark.asyncio
    async def test_math_prompt_loads_math_rag_content(self, engine, math_concept):
        """Math domain should load RAG content from mathematics subdirectory."""
        prompt = await engine.build_system_prompt(math_concept)
        # The derivative-concept has a RAG doc with math content
        assert "导数" in prompt
        assert "参考知识文档" in prompt

    @pytest.mark.asyncio
    async def test_ai_domain_no_math_supplement(self, engine, sample_concept):
        """AI engineering domain should NOT include math supplement."""
        prompt = await engine.build_system_prompt(sample_concept)
        assert "数学教学特殊规则" not in prompt

    @pytest.mark.asyncio
    async def test_math_prompt_contains_base_structure(self, engine, math_concept):
        """Math prompt should still contain the base Feynman prompt structure."""
        prompt = await engine.build_system_prompt(math_concept)
        assert "小图" in prompt
        assert "Phase 1" in prompt
        assert "choices" in prompt
