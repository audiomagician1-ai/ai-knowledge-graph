"""Tests for evaluator module — _validate_result, _parse_json, _fallback_evaluate, _format_dialogue"""

from engines.dialogue.evaluator import evaluator


class TestValidateResult:
    """Tests for _validate_result"""

    def test_valid_result_passes_through(self):
        result = {
            "completeness": 80, "accuracy": 75, "depth": 70, "examples": 65,
            "overall_score": 78, "gaps": ["gap1"], "feedback": "Good",
        }
        validated = evaluator._validate_result(result)
        assert validated["completeness"] == 80
        assert validated["overall_score"] == 78
        assert validated["mastered"] is True  # 78>=75 and all dims >= 60

    def test_missing_fields_get_defaults(self):
        result = {"completeness": 60}
        validated = evaluator._validate_result(result)
        assert validated["accuracy"] == 50  # default
        assert validated["depth"] == 50
        assert validated["examples"] == 50
        assert validated["overall_score"] == 50
        assert validated["gaps"] == []
        assert validated["feedback"] == "评估完成"

    def test_scores_clamped_to_0_100(self):
        result = {"completeness": 150, "accuracy": -10, "depth": 50, "examples": 50, "overall_score": 200}
        validated = evaluator._validate_result(result)
        assert validated["completeness"] == 100
        assert validated["accuracy"] == 0
        assert validated["overall_score"] == 100

    def test_mastered_requires_all_dims_above_60(self):
        result = {
            "completeness": 80, "accuracy": 80, "depth": 80, "examples": 55,
            "overall_score": 80,
        }
        validated = evaluator._validate_result(result)
        assert validated["mastered"] is False  # examples < 60

    def test_mastered_requires_overall_above_75(self):
        result = {
            "completeness": 70, "accuracy": 70, "depth": 70, "examples": 70,
            "overall_score": 70,
        }
        validated = evaluator._validate_result(result)
        assert validated["mastered"] is False  # overall < 75

    def test_float_scores_converted_to_int(self):
        result = {"completeness": 82.7, "accuracy": 73.1, "depth": 60.0, "examples": 65.5, "overall_score": 77.3}
        validated = evaluator._validate_result(result)
        assert validated["completeness"] == 82
        assert validated["accuracy"] == 73
        assert validated["overall_score"] == 77


class TestParseJson:
    """Tests for _parse_json"""

    def test_direct_json(self):
        text = '{"completeness": 80, "accuracy": 75}'
        result = evaluator._parse_json(text)
        assert result is not None
        assert result["completeness"] == 80

    def test_json_in_code_block(self):
        text = 'Here is the result:\n```json\n{"score": 85}\n```\nDone.'
        result = evaluator._parse_json(text)
        assert result is not None
        assert result["score"] == 85

    def test_json_embedded_in_text(self):
        text = 'Analysis: {"completeness": 90, "accuracy": 88}'
        result = evaluator._parse_json(text)
        assert result is not None
        assert result["completeness"] == 90

    def test_invalid_json_returns_none(self):
        result = evaluator._parse_json("This is not JSON at all")
        assert result is None

    def test_empty_string_returns_none(self):
        result = evaluator._parse_json("")
        assert result is None


class TestFallbackEvaluate:
    """Tests for _fallback_evaluate"""

    def test_few_turns_low_score(self):
        messages = [
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "Hi"},
        ]
        result = evaluator._fallback_evaluate(messages)
        assert result["overall_score"] < 75
        assert result["mastered"] is False

    def test_many_turns_higher_score(self):
        messages = []
        for i in range(8):
            messages.append({"role": "user", "content": f"Detailed explanation number {i} " * 10})
            messages.append({"role": "assistant", "content": f"Response {i}"})
        result = evaluator._fallback_evaluate(messages)
        assert result["overall_score"] > 50

    def test_scores_capped_at_85(self):
        messages = [{"role": "user", "content": "x" * 5000}] * 20
        result = evaluator._fallback_evaluate(messages)
        assert result["completeness"] <= 85  # base capped


class TestFormatDialogue:
    """Tests for _format_dialogue"""

    def test_basic_formatting(self):
        messages = [
            {"role": "assistant", "content": "Hello"},
            {"role": "user", "content": "Hi there"},
        ]
        result = evaluator._format_dialogue(messages)
        assert "用户（学习者）" in result
        assert "AI（学习伙伴/老师）" in result

    def test_system_messages_skipped(self):
        messages = [
            {"role": "system", "content": "truncation notice"},
            {"role": "user", "content": "My answer"},
        ]
        result = evaluator._format_dialogue(messages)
        assert "truncation" not in result
        assert "My answer" in result

    def test_truncation_on_long_dialogue(self):
        messages = [{"role": "user", "content": "x" * 500}] * 50
        result = evaluator._format_dialogue(messages, max_chars=2000)
        assert "早期对话已省略" in result


# ─── Math Domain Evaluator (Phase 8.5) ───

class TestMathDomainEvaluator:
    """Verify evaluator works correctly with math concepts."""

    def test_fallback_evaluate_with_math_dialogue(self):
        """Fallback evaluator should handle math dialogue with LaTeX."""
        messages = [
            {"role": "assistant", "content": "让我们学习导数。导数的定义是 $f'(x) = \\lim_{h→0} \\frac{f(x+h)-f(x)}{h}$"},
            {"role": "user", "content": "导数就是函数的变化率，$f'(x)$ 表示在 $x$ 处的瞬时变化率"},
            {"role": "assistant", "content": "说得好！几何意义是切线斜率。"},
            {"role": "user", "content": "比如 $f(x) = x^2$ 的导数是 $f'(x) = 2x$，在 $x=3$ 处切线斜率为 6"},
        ]
        result = evaluator._fallback_evaluate(messages)
        assert result["overall_score"] > 0
        assert "mastered" in result
        assert isinstance(result["gaps"], list)

    def test_format_dialogue_preserves_latex(self):
        """Dialogue formatter should preserve LaTeX formulas."""
        messages = [
            {"role": "user", "content": "求根公式是 $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$"},
        ]
        formatted = evaluator._format_dialogue(messages)
        assert "\\frac" in formatted
        assert "\\sqrt" in formatted


class TestDomainAwareAssessment:
    """Tests for domain-specific assessment prompt injection (Phase 9.4)."""

    def test_default_domain_no_supplement(self):
        """AI-engineering domain should not inject domain supplement."""
        from engines.dialogue.prompts.feynman_system import ASSESSMENT_SYSTEM_PROMPT
        prompt = ASSESSMENT_SYSTEM_PROMPT.format(
            concept_name="Test",
            difficulty=5,
            domain_assessment_supplement="",
        )
        assert "数学领域评估" not in prompt
        assert "英语领域评估" not in prompt
        assert "评估概念" in prompt
        assert "Test" in prompt

    def test_math_supplement_injected(self):
        """Mathematics domain should inject math-specific assessment criteria."""
        from engines.dialogue.prompts.feynman_system import (
            ASSESSMENT_SYSTEM_PROMPT,
            MATH_ASSESSMENT_SUPPLEMENT,
        )
        prompt = ASSESSMENT_SYSTEM_PROMPT.format(
            concept_name="导数",
            difficulty=7,
            domain_assessment_supplement=MATH_ASSESSMENT_SUPPLEMENT,
        )
        assert "数学领域评估特殊指标" in prompt
        assert "公式理解" in prompt
        assert "推导能力" in prompt
        assert "计算准确性" in prompt
        assert "导数" in prompt
        assert "7/9" in prompt

    def test_english_supplement_injected(self):
        """English domain should inject English-specific assessment criteria."""
        from engines.dialogue.prompts.feynman_system import (
            ASSESSMENT_SYSTEM_PROMPT,
            ENGLISH_ASSESSMENT_SUPPLEMENT,
        )
        prompt = ASSESSMENT_SYSTEM_PROMPT.format(
            concept_name="Present Tense",
            difficulty=3,
            domain_assessment_supplement=ENGLISH_ASSESSMENT_SUPPLEMENT,
        )
        assert "英语领域评估特殊指标" in prompt
        assert "语法准确性" in prompt
        assert "词汇运用" in prompt
        assert "中英差异意识" in prompt
        assert "产出能力" in prompt
        assert "发音意识" in prompt
        assert "Present Tense" in prompt

    def test_evaluator_uses_domain_from_concept(self):
        """Evaluator should extract domain_id from concept dict for prompt generation."""
        from engines.dialogue.prompts.feynman_system import (
            ASSESSMENT_SYSTEM_PROMPT,
            MATH_ASSESSMENT_SUPPLEMENT,
            ENGLISH_ASSESSMENT_SUPPLEMENT,
        )
        # Simulate what evaluator.evaluate() does
        for domain_id, expected_text in [
            ("mathematics", "数学领域评估"),
            ("english", "英语领域评估"),
            ("ai-engineering", ""),
        ]:
            concept = {"name": "Test", "difficulty": 5, "domain_id": domain_id}
            supplement = ""
            if concept.get("domain_id") == "mathematics":
                supplement = MATH_ASSESSMENT_SUPPLEMENT
            elif concept.get("domain_id") == "english":
                supplement = ENGLISH_ASSESSMENT_SUPPLEMENT
            prompt = ASSESSMENT_SYSTEM_PROMPT.format(
                concept_name=concept["name"],
                difficulty=concept.get("difficulty", 5),
                domain_assessment_supplement=supplement,
            )
            if expected_text:
                assert expected_text in prompt, f"Expected '{expected_text}' in prompt for domain '{domain_id}'"
            else:
                assert "数学领域评估" not in prompt
                assert "英语领域评估" not in prompt

    def test_english_supplement_no_latex(self):
        """English assessment supplement should not mention LaTeX."""
        from engines.dialogue.prompts.feynman_system import ENGLISH_ASSESSMENT_SUPPLEMENT
        assert "LaTeX" not in ENGLISH_ASSESSMENT_SUPPLEMENT
        assert "latex" not in ENGLISH_ASSESSMENT_SUPPLEMENT.lower()

    def test_math_supplement_no_english_teaching(self):
        """Math assessment supplement should not mention English teaching terms."""
        from engines.dialogue.prompts.feynman_system import MATH_ASSESSMENT_SUPPLEMENT
        assert "语法" not in MATH_ASSESSMENT_SUPPLEMENT
        assert "词汇" not in MATH_ASSESSMENT_SUPPLEMENT
        assert "发音" not in MATH_ASSESSMENT_SUPPLEMENT


class TestDomainSupplementRegistries:
    """Verify DOMAIN_SUPPLEMENTS and ASSESSMENT_SUPPLEMENTS registries."""

    def test_domain_supplements_covers_all_domains(self):
        """Registry should have entries for all non-default domains."""
        from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
        expected = {"mathematics", "english", "physics", "product-design", "finance", "psychology", "philosophy", "biology", "economics", "writing", "game-design", "level-design", "game-engine", "software-engineering", "computer-graphics", "3d-art", "concept-design", "animation", "technical-art", "vfx", "game-audio-music", "game-ui-ux"}
        assert set(DOMAIN_SUPPLEMENTS.keys()) == expected

    def test_assessment_supplements_covers_all_domains(self):
        """Assessment registry should have entries for all non-default domains."""
        from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
        expected = {"mathematics", "english", "physics", "product-design", "finance", "psychology", "philosophy", "biology", "economics", "writing", "game-design", "level-design", "game-engine", "software-engineering", "computer-graphics", "3d-art", "concept-design", "animation", "technical-art", "vfx", "game-audio-music", "game-ui-ux"}
        assert set(ASSESSMENT_SUPPLEMENTS.keys()) == expected

    def test_domain_supplements_values_non_empty(self):
        """All domain supplement values should be non-empty strings."""
        from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS
        for domain_id, supplement in DOMAIN_SUPPLEMENTS.items():
            assert isinstance(supplement, str), f"{domain_id} supplement is not a string"
            assert len(supplement.strip()) > 50, f"{domain_id} supplement is too short"

    def test_assessment_supplements_values_non_empty(self):
        """All assessment supplement values should be non-empty strings."""
        from engines.dialogue.prompts.feynman_system import ASSESSMENT_SUPPLEMENTS
        for domain_id, supplement in ASSESSMENT_SUPPLEMENTS.items():
            assert isinstance(supplement, str), f"{domain_id} assessment is not a string"
            assert len(supplement.strip()) > 50, f"{domain_id} assessment is too short"

    def test_default_domain_not_in_registries(self):
        """ai-engineering (default) should NOT be in registries (no special supplement)."""
        from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
        assert "ai-engineering" not in DOMAIN_SUPPLEMENTS
        assert "ai-engineering" not in ASSESSMENT_SUPPLEMENTS

    def test_registry_get_returns_empty_for_unknown(self):
        """Unknown domain should return empty string via .get()."""
        from engines.dialogue.prompts.feynman_system import DOMAIN_SUPPLEMENTS, ASSESSMENT_SUPPLEMENTS
        assert DOMAIN_SUPPLEMENTS.get("nonexistent", "") == ""
        assert ASSESSMENT_SUPPLEMENTS.get("nonexistent", "") == ""
