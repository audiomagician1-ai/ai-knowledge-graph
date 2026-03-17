"""Tests for feynman_system.py — parse_ai_response / choices parsing / validation"""

from engines.dialogue.prompts.feynman_system import (
    parse_ai_response,
    _parse_choices_json,
    _try_trailing_json,
    _validate_choices,
    _DEFAULT_CHOICES,
)


class TestParseAiResponse:
    """Tests for parse_ai_response — main entry point."""

    def test_empty_string_returns_defaults(self):
        result = parse_ai_response("")
        assert result["content"] == ""
        assert len(result["choices"]) == 3  # DEFAULT_CHOICES

    def test_none_returns_defaults(self):
        result = parse_ai_response(None)
        assert result["content"] == ""
        assert result["choices"] == list(_DEFAULT_CHOICES)

    def test_whitespace_only_returns_defaults(self):
        result = parse_ai_response("   \n\t  ")
        assert result["content"] == ""

    def test_valid_choices_block(self):
        raw = (
            "Hello, let's learn!\n\n"
            "```choices\n"
            '[{"id":"opt-1","text":"Option A","type":"explore"},'
            '{"id":"opt-2","text":"Option B","type":"answer"}]\n'
            "```"
        )
        result = parse_ai_response(raw)
        assert result["content"] == "Hello, let's learn!"
        assert len(result["choices"]) == 2
        assert result["choices"][0]["text"] == "Option A"
        assert result["choices"][1]["type"] == "answer"

    def test_choices_block_with_extra_whitespace(self):
        raw = (
            "Content here.\n\n"
            "```choices  \n"
            '[\n  {"id":"opt-1","text":"A","type":"explore"},\n'
            '  {"id":"opt-2","text":"B","type":"action"}\n]\n'
            "```\n"
        )
        result = parse_ai_response(raw)
        assert result["content"] == "Content here."
        assert len(result["choices"]) == 2

    def test_no_choices_block_fallback_trailing_json(self):
        raw = (
            "Some content.\n\n"
            '[{"id":"opt-1","text":"X","type":"explore"},'
            '{"id":"opt-2","text":"Y","type":"answer"}]'
        )
        result = parse_ai_response(raw)
        assert result["content"] == "Some content."
        assert len(result["choices"]) == 2

    def test_no_choices_at_all_returns_defaults(self):
        raw = "Just plain text without any choices."
        result = parse_ai_response(raw)
        assert result["content"] == "Just plain text without any choices."
        assert result["choices"] == list(_DEFAULT_CHOICES)

    def test_malformed_choices_block_returns_defaults(self):
        raw = "Content\n```choices\nNOT VALID JSON\n```"
        result = parse_ai_response(raw)
        assert result["content"] == "Content"
        assert result["choices"] == list(_DEFAULT_CHOICES)

    def test_choices_text_capped_at_60(self):
        long_text = "A" * 100
        raw = (
            "Content\n```choices\n"
            f'[{{"id":"opt-1","text":"{long_text}","type":"explore"}},'
            f'{{"id":"opt-2","text":"Short","type":"explore"}}]\n```'
        )
        result = parse_ai_response(raw)
        assert len(result["choices"][0]["text"]) == 60

    def test_max_4_choices(self):
        choices = ",".join(
            f'{{"id":"opt-{i}","text":"Choice {i}","type":"explore"}}'
            for i in range(1, 7)
        )
        raw = f"Content\n```choices\n[{choices}]\n```"
        result = parse_ai_response(raw)
        assert len(result["choices"]) == 4

    def test_invalid_type_defaults_to_explore(self):
        raw = (
            "Content\n```choices\n"
            '[{"id":"opt-1","text":"A","type":"invalid_type"},'
            '{"id":"opt-2","text":"B","type":"explore"}]\n```'
        )
        result = parse_ai_response(raw)
        assert result["choices"][0]["type"] == "explore"


class TestParseChoicesJson:
    """Tests for _parse_choices_json — JSON parsing with cleanup."""

    def test_valid_json_array(self):
        result = _parse_choices_json('[{"text":"a"},{"text":"b"}]')
        assert len(result) == 2

    def test_single_quotes_fixed(self):
        result = _parse_choices_json("[{'text':'a'},{'text':'b'}]")
        assert len(result) == 2

    def test_trailing_comma_fixed(self):
        result = _parse_choices_json('[{"text":"a"},{"text":"b"},]')
        assert len(result) == 2

    def test_invalid_json_returns_empty(self):
        result = _parse_choices_json("not json at all")
        assert result == []

    def test_json_object_not_array_returns_empty(self):
        result = _parse_choices_json('{"text":"a"}')
        assert result == []


class TestTryTrailingJson:
    """Tests for _try_trailing_json — fallback JSON array detection."""

    def test_trailing_array_extracted(self):
        text = 'Some content [{"text":"a","type":"explore"},{"text":"b","type":"answer"}]'
        content, choices = _try_trailing_json(text)
        assert content == "Some content"
        assert len(choices) == 2

    def test_no_bracket_returns_text(self):
        text = "No brackets here"
        content, choices = _try_trailing_json(text)
        assert content == "No brackets here"
        assert choices == []

    def test_bracket_without_type_ignored(self):
        text = "Code example: [1, 2, 3]"
        content, choices = _try_trailing_json(text)
        assert content == "Code example: [1, 2, 3]"
        assert choices == []

    def test_single_item_array_rejected(self):
        """Arrays with < 2 items are not considered choices."""
        text = 'Content [{"text":"only one","type":"explore"}]'
        content, choices = _try_trailing_json(text)
        assert choices == []


class TestValidateChoices:
    """Tests for _validate_choices — sanitization and fallback."""

    def test_empty_list_returns_defaults(self):
        assert _validate_choices([]) == list(_DEFAULT_CHOICES)

    def test_none_returns_defaults(self):
        assert _validate_choices(None) == list(_DEFAULT_CHOICES)

    def test_single_choice_returns_defaults(self):
        """Less than 2 valid choices triggers fallback."""
        result = _validate_choices([{"text": "only one", "type": "explore"}])
        assert result == list(_DEFAULT_CHOICES)

    def test_valid_types_preserved(self):
        choices = [
            {"text": "A", "type": "explore"},
            {"text": "B", "type": "answer"},
            {"text": "C", "type": "action"},
            {"text": "D", "type": "level"},
        ]
        result = _validate_choices(choices)
        types = [c["type"] for c in result]
        assert types == ["explore", "answer", "action", "level"]

    def test_auto_assigns_ids(self):
        choices = [{"text": "A", "type": "explore"}, {"text": "B", "type": "explore"}]
        result = _validate_choices(choices)
        assert result[0]["id"] == "opt-1"
        assert result[1]["id"] == "opt-2"

    def test_preserves_existing_ids(self):
        choices = [
            {"id": "my-1", "text": "A", "type": "explore"},
            {"id": "my-2", "text": "B", "type": "explore"},
        ]
        result = _validate_choices(choices)
        assert result[0]["id"] == "my-1"

    def test_non_dict_items_skipped(self):
        choices = [{"text": "A", "type": "explore"}, "not a dict", {"text": "B", "type": "explore"}]
        result = _validate_choices(choices)
        assert len(result) == 2

    def test_empty_text_items_skipped(self):
        choices = [
            {"text": "", "type": "explore"},
            {"text": "Valid", "type": "explore"},
            {"text": "Also valid", "type": "explore"},
        ]
        result = _validate_choices(choices)
        assert len(result) == 2
        assert result[0]["text"] == "Valid"
