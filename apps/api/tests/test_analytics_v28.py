"""V2.8 Social & Collaborative Learning — Backend Tests.

Tests for:
- GET /api/analytics/leaderboard
- GET /api/analytics/peer-comparison
- POST /api/community/discussions
- GET /api/community/discussions
- POST /api/community/discussions/{id}/reply
- POST /api/community/discussions/{id}/vote
- PATCH /api/community/discussions/{id}/resolve
- GET /api/community/discussions/concept-activity/{concept_id}
"""

import os
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    os.environ.setdefault("AKG_TEST", "1")
    from main import app
    return TestClient(app)


# ── Leaderboard API ──────────────────────────────────────


class TestLeaderboard:
    def test_default(self, client):
        """Leaderboard returns ranked entries with user stats."""
        r = client.get("/api/analytics/leaderboard")
        assert r.status_code == 200
        data = r.json()
        assert "leaderboard" in data
        assert "user_rank" in data
        assert "user_stats" in data
        assert isinstance(data["leaderboard"], list)
        assert len(data["leaderboard"]) > 0
        user_entries = [e for e in data["leaderboard"] if e.get("is_self")]
        assert len(user_entries) == 1
        assert user_entries[0]["name"] == "我"
        ranks = [e["rank"] for e in data["leaderboard"]]
        assert ranks == sorted(ranks)

    def test_sort_options(self, client):
        """Leaderboard supports multiple sort keys."""
        for sort_by in ["mastered", "efficiency", "streak", "score"]:
            r = client.get(f"/api/analytics/leaderboard?sort_by={sort_by}")
            assert r.status_code == 200
            data = r.json()
            assert data["sort_by"] == sort_by
            assert len(data["leaderboard"]) > 0

    def test_limit(self, client):
        """Leaderboard respects limit parameter."""
        r = client.get("/api/analytics/leaderboard?limit=5")
        assert r.status_code == 200
        data = r.json()
        assert len(data["leaderboard"]) <= 5

    def test_user_stats_fields(self, client):
        """User stats entry has required fields."""
        r = client.get("/api/analytics/leaderboard")
        assert r.status_code == 200
        user = r.json()["user_stats"]
        required_fields = ["mastered", "learning", "domains_started", "avg_efficiency",
                           "current_streak", "composite_score", "total_sessions"]
        for field in required_fields:
            assert field in user, f"Missing field: {field}"


# ── Peer Comparison API ──────────────────────────────────


class TestPeerComparison:
    def test_returns_structure(self, client):
        """Peer comparison returns percentiles and user metrics."""
        r = client.get("/api/analytics/peer-comparison")
        assert r.status_code == 200
        data = r.json()
        assert "user" in data
        assert "percentiles" in data
        assert "comparison_labels" in data
        for key, val in data["percentiles"].items():
            assert 1 <= val <= 99, f"{key} percentile out of range: {val}"
        assert "mastered" in data["user"]
        assert "avg_score" in data["user"]
        assert "mastery_speed" in data["user"]

    def test_peer_count(self, client):
        """Peer comparison includes peer count."""
        r = client.get("/api/analytics/peer-comparison")
        assert r.status_code == 200
        assert r.json()["peer_count"] > 0


# ── Discussions API ──────────────────────────────────────


class TestDiscussions:
    def test_create(self, client):
        """Create a discussion thread for a concept."""
        r = client.post("/api/community/discussions", json={
            "concept_id": "ai-engineering/ml-fundamentals/supervised-learning",
            "domain_id": "ai-engineering",
            "type": "question",
            "title": "监督学习和非监督学习的关键区别是什么？",
            "content": "我理解了基本概念，但在实际应用场景中如何选择？请分享你的经验。",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["id"].startswith("disc_")
        assert data["concept_id"] == "ai-engineering/ml-fundamentals/supervised-learning"
        assert data["type"] == "question"
        assert data["votes"] == 0
        assert data["reply_count"] == 0
        assert data["resolved"] is False

    def test_list(self, client):
        """List discussions with filters."""
        client.post("/api/community/discussions", json={
            "concept_id": "ai-engineering/ml-fundamentals/neural-networks",
            "type": "insight",
            "title": "神经网络的直觉理解方法",
            "content": "我发现用水管网络来类比神经网络很有效。",
        })
        r = client.get("/api/community/discussions")
        assert r.status_code == 200
        data = r.json()
        assert "discussions" in data
        assert "total" in data
        assert data["total"] >= 1

    def test_filter_by_concept(self, client):
        """Filter discussions by concept_id."""
        cid = "ai-engineering/ml-fundamentals/supervised-learning"
        r = client.get(f"/api/community/discussions?concept_id={cid}")
        assert r.status_code == 200
        data = r.json()
        for d in data["discussions"]:
            assert d["concept_id"] == cid

    def test_reply(self, client):
        """Add a reply to a discussion."""
        create_r = client.post("/api/community/discussions", json={
            "concept_id": "test-concept-reply",
            "title": "测试讨论",
            "content": "这是一个测试讨论内容。",
        })
        disc_id = create_r.json()["id"]

        r = client.post(f"/api/community/discussions/{disc_id}/reply", json={
            "content": "这是一个很好的问题！我觉得关键在于...",
        })
        assert r.status_code == 200
        reply = r.json()
        assert reply["id"].startswith("reply_")
        assert reply["discussion_id"] == disc_id

        disc_r = client.get(f"/api/community/discussions/{disc_id}")
        assert disc_r.json()["reply_count"] == 1
        assert len(disc_r.json()["replies"]) == 1

    def test_vote(self, client):
        """Vote on a discussion."""
        create_r = client.post("/api/community/discussions", json={
            "concept_id": "test-vote",
            "title": "投票测试讨论",
            "content": "请为这个讨论投票。",
        })
        disc_id = create_r.json()["id"]

        r = client.post(f"/api/community/discussions/{disc_id}/vote")
        assert r.status_code == 200
        assert r.json()["votes"] == 1

        r2 = client.post(f"/api/community/discussions/{disc_id}/vote")
        assert r2.json()["votes"] == 2

    def test_resolve(self, client):
        """Mark a discussion as resolved."""
        create_r = client.post("/api/community/discussions", json={
            "concept_id": "test-resolve",
            "title": "解决测试",
            "content": "等待解决。",
        })
        disc_id = create_r.json()["id"]

        r = client.patch(f"/api/community/discussions/{disc_id}/resolve")
        assert r.status_code == 200
        assert r.json()["resolved"] is True

    def test_concept_activity(self, client):
        """Get discussion activity summary for a concept."""
        cid = "test-activity-concept"
        for dtype in ["question", "insight", "resource"]:
            client.post("/api/community/discussions", json={
                "concept_id": cid,
                "type": dtype,
                "title": f"活动测试 - {dtype}",
                "content": f"这是{dtype}类型的讨论。",
            })

        r = client.get(f"/api/community/discussions/concept-activity/{cid}")
        assert r.status_code == 200
        data = r.json()
        assert data["concept_id"] == cid
        assert data["total_discussions"] == 3
        assert data["questions"] == 1
        assert data["insights"] == 1
        assert data["resources"] == 1

    def test_not_found(self, client):
        """404 for non-existent discussion."""
        r = client.get("/api/community/discussions/disc_nonexistent")
        assert r.status_code == 404

        r2 = client.post("/api/community/discussions/disc_nonexistent/reply", json={"content": "test"})
        assert r2.status_code == 404

    def test_sort_options(self, client):
        """Discussion list supports sort options."""
        for sort in ["recent", "popular", "active"]:
            r = client.get(f"/api/community/discussions?sort={sort}")
            assert r.status_code == 200
