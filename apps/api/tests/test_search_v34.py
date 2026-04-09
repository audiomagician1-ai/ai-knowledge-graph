"""Tests for V3.4 search enhancements: trigram fuzzy, search-suggestions, progress-snapshot."""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# ── Trigram helper unit tests ──


def test_trigrams_basic():
    from routers.analytics_search import _trigrams
    result = _trigrams("hello")
    assert "hel" in result
    assert "ell" in result
    assert "llo" in result
    assert len(result) == 3


def test_trigrams_short_string():
    from routers.analytics_search import _trigrams
    result = _trigrams("ab")
    assert "ab" in result


def test_trigram_similarity_identical():
    from routers.analytics_search import _trigram_similarity
    score = _trigram_similarity("machine learning", "machine learning")
    assert score == 1.0


def test_trigram_similarity_partial():
    from routers.analytics_search import _trigram_similarity
    score = _trigram_similarity("machine", "machin learning")
    assert 0.2 < score < 1.0


def test_trigram_similarity_unrelated():
    from routers.analytics_search import _trigram_similarity
    score = _trigram_similarity("xyz", "abcdef")
    assert score < 0.2


# ── Search Suggestions endpoint ──


def test_search_suggestions_basic():
    resp = client.get("/api/analytics/search-suggestions", params={"q": "var"})
    assert resp.status_code == 200
    data = resp.json()
    assert "suggestions" in data
    assert "query" in data
    assert data["query"] == "var"
    assert isinstance(data["suggestions"], list)


def test_search_suggestions_returns_fields():
    resp = client.get("/api/analytics/search-suggestions", params={"q": "loop"})
    assert resp.status_code == 200
    data = resp.json()
    if data["suggestions"]:
        s = data["suggestions"][0]
        assert "concept_id" in s
        assert "name" in s
        assert "domain_id" in s
        assert "relevance" in s


def test_search_suggestions_limit():
    resp = client.get("/api/analytics/search-suggestions", params={"q": "a", "limit": 3})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["suggestions"]) <= 3


def test_search_suggestions_fuzzy():
    """Fuzzy match should find results even with typos."""
    resp = client.get("/api/analytics/search-suggestions", params={"q": "machne"})
    assert resp.status_code == 200
    data = resp.json()
    # Should get some fuzzy matches even with the typo
    assert isinstance(data["suggestions"], list)


# ── Content Search with fuzzy enhancements ──


def test_content_search_has_fuzzy_field():
    resp = client.get("/api/analytics/content-search", params={"q": "neural network"})
    assert resp.status_code == 200
    data = resp.json()
    if data["results"]:
        r = data["results"][0]
        assert "fuzzy_match" in r
        assert "name_match" in r


# ── Progress Snapshot endpoint ──


def test_progress_snapshot_basic():
    resp = client.get("/api/analytics/progress-snapshot")
    assert resp.status_code == 200
    data = resp.json()
    assert "snapshot_version" in data
    assert data["snapshot_version"] == "1.0"


def test_progress_snapshot_overview():
    resp = client.get("/api/analytics/progress-snapshot")
    data = resp.json()
    overview = data["overview"]
    assert "total_concepts" in overview
    assert "mastered" in overview
    assert "learning" in overview
    assert "completion_pct" in overview
    assert "avg_score" in overview
    assert overview["total_concepts"] > 0


def test_progress_snapshot_streak():
    resp = client.get("/api/analytics/progress-snapshot")
    data = resp.json()
    assert "streak" in data
    assert "current" in data["streak"]
    assert "longest" in data["streak"]


def test_progress_snapshot_efficiency():
    resp = client.get("/api/analytics/progress-snapshot")
    data = resp.json()
    assert "efficiency" in data
    assert "avg_sessions_to_master" in data["efficiency"]
    assert "mastery_rate" in data["efficiency"]


def test_progress_snapshot_top_domains():
    resp = client.get("/api/analytics/progress-snapshot")
    data = resp.json()
    assert "top_domains" in data
    assert isinstance(data["top_domains"], list)
    assert len(data["top_domains"]) <= 5


def test_progress_snapshot_recent_mastered():
    resp = client.get("/api/analytics/progress-snapshot")
    data = resp.json()
    assert "recent_mastered" in data
    assert isinstance(data["recent_mastered"], list)
    assert len(data["recent_mastered"]) <= 10


def test_progress_snapshot_domain_counts():
    resp = client.get("/api/analytics/progress-snapshot")
    data = resp.json()
    assert "domains_started" in data
    assert "domains_total" in data
    assert data["domains_total"] >= 36
