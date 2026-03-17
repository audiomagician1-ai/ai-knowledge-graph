"""Tests for dialogue API endpoints — conversation CRUD + chat + assessment.

Uses mocked LLM to avoid external API calls during tests.
"""
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
import pytest

# Setup temp DB before importing app
_tmp_dir = tempfile.mkdtemp()
import db.sqlite_client as sc
sc._DB_DIR = Path(_tmp_dir)
sc.DB_PATH = sc._DB_DIR / "test_dialogue_api.db"
sc.init_db()

from main import app

client = TestClient(app)

# A real concept ID from the seed graph
CONCEPT_ID = "binary-system"


def _mock_opening():
    """Mock socratic_engine methods for conversation creation."""
    async def mock_build_system_prompt(**kwargs):
        return "Mock system prompt for testing"

    async def mock_get_opening(concept, system_prompt, **kwargs):
        return (
            f"让我们一起学习「{concept['name']}」！",
            [
                {"id": "opt-1", "text": "完全没听说过", "type": "level"},
                {"id": "opt-2", "text": "有一些了解", "type": "level"},
            ],
        )

    return mock_build_system_prompt, mock_get_opening


class TestCreateConversation:
    def setup_method(self):
        # Clear caches between tests
        from routers.dialogue import _session_cache, _session_locks
        _session_cache.clear()
        _session_locks.clear()

    @patch("routers.dialogue.socratic_engine")
    def test_create_conversation_success(self, mock_engine):
        mock_build, mock_open = _mock_opening()
        mock_engine.build_system_prompt = mock_build
        mock_engine.get_opening = mock_open

        res = client.post("/api/dialogue/conversations", json={"concept_id": CONCEPT_ID})
        assert res.status_code == 200
        data = res.json()
        assert data["concept_id"] == CONCEPT_ID
        assert data["concept_name"] == "二进制与数制"
        assert data["conversation_id"]
        assert data["opening_message"]
        assert isinstance(data["opening_choices"], list)
        assert len(data["opening_choices"]) >= 2

    def test_create_conversation_unknown_concept(self):
        res = client.post("/api/dialogue/conversations", json={"concept_id": "nonexistent-concept-xyz"})
        assert res.status_code == 404

    def test_create_conversation_missing_concept_id(self):
        res = client.post("/api/dialogue/conversations", json={})
        assert res.status_code == 422


class TestChat:
    def setup_method(self):
        from routers.dialogue import _session_cache, _session_locks
        _session_cache.clear()
        _session_locks.clear()

    def _create_conv(self):
        """Helper: create a conversation and return its ID."""
        with patch("routers.dialogue.socratic_engine") as mock_engine:
            mock_build, mock_open = _mock_opening()
            mock_engine.build_system_prompt = mock_build
            mock_engine.get_opening = mock_open
            res = client.post("/api/dialogue/conversations", json={"concept_id": CONCEPT_ID})
            return res.json()["conversation_id"]

    @patch("routers.dialogue.socratic_engine")
    def test_chat_no_api_key(self, mock_engine):
        """Without API key and no server key, should return helpful error via SSE."""
        mock_build, mock_open = _mock_opening()
        mock_engine.build_system_prompt = mock_build
        mock_engine.get_opening = mock_open

        conv_id = self._create_conv()

        # Ensure no server API key (settings is imported lazily from config)
        with patch("config.settings") as mock_settings:
            mock_settings.openrouter_api_key = ""
            mock_settings.openai_api_key = ""
            mock_settings.deepseek_api_key = ""

            res = client.post(
                "/api/dialogue/chat",
                json={"conversation_id": conv_id, "message": "Hello"},
            )
            assert res.status_code == 200
            body = res.text
            assert "API Key" in body

    def test_chat_nonexistent_conversation(self):
        res = client.post(
            "/api/dialogue/chat",
            json={"conversation_id": "fake-id-12345", "message": "Hello"},
        )
        assert res.status_code == 404

    def test_chat_missing_message(self):
        res = client.post(
            "/api/dialogue/chat",
            json={"conversation_id": "any"},
        )
        assert res.status_code == 422


class TestAssess:
    def setup_method(self):
        from routers.dialogue import _session_cache, _session_locks
        _session_cache.clear()
        _session_locks.clear()

    def _create_conv_with_messages(self, num_user_turns=3):
        """Create a conversation and add mock messages for assessment."""
        with patch("routers.dialogue.socratic_engine") as mock_engine:
            mock_build, mock_open = _mock_opening()
            mock_engine.build_system_prompt = mock_build
            mock_engine.get_opening = mock_open
            res = client.post("/api/dialogue/conversations", json={"concept_id": CONCEPT_ID})
            conv_id = res.json()["conversation_id"]

        # Add messages directly to session cache
        from routers.dialogue import _session_cache
        session = _session_cache.get(conv_id)
        for i in range(num_user_turns):
            session["messages"].append({"role": "user", "content": f"My answer {i}: I understand this concept"})
            session["messages"].append({"role": "assistant", "content": f"Great explanation! Let me ask more."})
        return conv_id

    def test_assess_too_few_turns(self):
        """Assessment should require at least 2 user turns."""
        with patch("routers.dialogue.socratic_engine") as mock_engine:
            mock_build, mock_open = _mock_opening()
            mock_engine.build_system_prompt = mock_build
            mock_engine.get_opening = mock_open
            res = client.post("/api/dialogue/conversations", json={"concept_id": CONCEPT_ID})
            conv_id = res.json()["conversation_id"]

        # Only 0 user turns — should fail
        res = client.post("/api/dialogue/assess", json={"conversation_id": conv_id})
        assert res.status_code == 400
        assert "2 轮" in res.json()["detail"]

    @patch("routers.dialogue.evaluator")
    def test_assess_success(self, mock_eval):
        """Assessment with enough turns should return valid result."""
        mock_eval.evaluate = AsyncMock(return_value={
            "completeness": 80,
            "accuracy": 75,
            "depth": 70,
            "examples": 65,
            "overall_score": 78,
            "gaps": ["需要更多例子"],
            "feedback": "不错的理解",
            "mastered": True,
        })

        conv_id = self._create_conv_with_messages(3)
        res = client.post("/api/dialogue/assess", json={"conversation_id": conv_id})
        assert res.status_code == 200
        data = res.json()
        assert data["concept_id"] == CONCEPT_ID
        assert data["overall_score"] == 78
        assert data["mastered"] is True
        assert data["turns"] >= 3

    @patch("routers.dialogue.evaluator")
    def test_assess_not_mastered(self, mock_eval):
        """Assessment below threshold should not mark mastered."""
        mock_eval.evaluate = AsyncMock(return_value={
            "completeness": 60,
            "accuracy": 55,
            "depth": 50,
            "examples": 45,
            "overall_score": 55,
            "gaps": ["基础概念不清", "缺少实例"],
            "feedback": "需要继续学习",
            "mastered": False,
        })

        conv_id = self._create_conv_with_messages(2)
        res = client.post("/api/dialogue/assess", json={"conversation_id": conv_id})
        assert res.status_code == 200
        data = res.json()
        assert data["mastered"] is False
        assert data["overall_score"] == 55

    def test_assess_nonexistent_conversation(self):
        res = client.post("/api/dialogue/assess", json={"conversation_id": "fake-id-99"})
        assert res.status_code == 404


class TestGetConversation:
    def setup_method(self):
        from routers.dialogue import _session_cache, _session_locks
        _session_cache.clear()
        _session_locks.clear()

    @patch("routers.dialogue.socratic_engine")
    def test_get_conversation_detail(self, mock_engine):
        mock_build, mock_open = _mock_opening()
        mock_engine.build_system_prompt = mock_build
        mock_engine.get_opening = mock_open

        res = client.post("/api/dialogue/conversations", json={"concept_id": CONCEPT_ID})
        conv_id = res.json()["conversation_id"]

        res = client.get(f"/api/dialogue/conversations/{conv_id}")
        assert res.status_code == 200
        data = res.json()
        assert data["id"] == conv_id
        assert data["concept_id"] == CONCEPT_ID
        assert len(data["messages"]) >= 1  # At least opening message

    def test_get_nonexistent_conversation(self):
        res = client.get("/api/dialogue/conversations/nonexistent-id")
        assert res.status_code == 404

    def test_list_conversations(self):
        res = client.get("/api/dialogue/conversations")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


class TestInputValidation:
    """Test request validation and edge cases."""

    def test_concept_id_max_length(self):
        long_id = "x" * 201
        res = client.post("/api/dialogue/conversations", json={"concept_id": long_id})
        assert res.status_code == 422

    def test_chat_message_max_length(self):
        long_msg = "x" * 10001
        res = client.post("/api/dialogue/chat", json={
            "conversation_id": "any",
            "message": long_msg,
        })
        assert res.status_code == 422

    def test_chat_is_choice_flag(self):
        """is_choice field should be accepted."""
        res = client.post("/api/dialogue/chat", json={
            "conversation_id": "fake",
            "message": "test",
            "is_choice": True,
        })
        # Will be 404 (conv not found) not 422 (validation), proving is_choice is accepted
        assert res.status_code == 404
