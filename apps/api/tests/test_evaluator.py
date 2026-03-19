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
