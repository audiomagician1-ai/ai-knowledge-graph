"""
Tests for RAG module (engines/graph/rag.py).

Tests the RAGRetriever's exact match, fuzzy match, file fallback,
and search functionality.
"""
import json
import os
import sys
import tempfile
import textwrap
from pathlib import Path

import pytest

# Make sure project root is in sys.path
api_dir = Path(__file__).resolve().parent.parent
if str(api_dir) not in sys.path:
    sys.path.insert(0, str(api_dir))


@pytest.fixture(autouse=True)
def reset_cache():
    """Clear RAG module's internal cache between tests."""
    from engines.graph import rag
    rag._index_cache.clear()
    yield
    rag._index_cache.clear()


@pytest.fixture
def rag_dir(tmp_path, monkeypatch):
    """Create a minimal RAG directory structure for testing."""
    domain = "test-domain"
    sub = "fundamentals"

    # Create directory structure
    doc_dir = tmp_path / domain / sub
    doc_dir.mkdir(parents=True)

    # Create a concept document
    (doc_dir / "concept-a.md").write_text(
        textwrap.dedent("""\
        ---
        title: Concept A
        ---
        # 概念 A

        这是概念A的详细教学内容。

        ## 核心原理
        概念A是一个重要的基础概念，由Smith (2020) 提出。
        其核心公式为 $E = mc^2$。

        ## 实际应用
        例如，在实际工程中应用广泛。

        ## 常见误区
        一个常见误区是将A与B混淆。
        """),
        encoding="utf-8",
    )

    (doc_dir / "concept-b.md").write_text(
        "# 概念 B\n\n概念B的简短内容。",
        encoding="utf-8",
    )

    # Create _index.json
    index = {
        "documents": [
            {
                "id": "concept-a",
                "name": "概念A",
                "subdomain_id": "fundamentals",
                "file": f"{domain}/{sub}/concept-a.md",
            },
            {
                "id": "concept-b",
                "name": "概念B",
                "subdomain_id": "fundamentals",
                "file": f"{domain}/{sub}/concept-b.md",
            },
        ]
    }
    (tmp_path / domain / "_index.json").write_text(
        json.dumps(index, ensure_ascii=False), encoding="utf-8"
    )

    # Monkeypatch _get_rag_dir to return our test directory
    from engines.graph import rag
    monkeypatch.setattr(rag, "_get_rag_dir", lambda: str(tmp_path))

    return tmp_path


@pytest.fixture
def retriever(rag_dir):
    """Create a RAGRetriever pointed at the test RAG directory."""
    from engines.graph.rag import RAGRetriever
    r = RAGRetriever()
    r._rag_dir = str(rag_dir)
    return r


class TestRAGDocument:
    def test_dataclass_fields(self):
        from engines.graph.rag import RAGDocument
        doc = RAGDocument(
            concept_id="test",
            name="Test",
            domain_id="domain",
            subdomain_id="sub",
            content="Hello",
            char_count=5,
        )
        assert doc.match_type == "exact"
        assert doc.match_score == 1.0
        assert doc.char_count == 5


class TestRAGRetriever:
    def test_exact_match(self, retriever):
        doc = retriever.retrieve("concept-a", domain_id="test-domain")
        assert doc is not None
        assert doc.concept_id == "concept-a"
        assert doc.match_type == "exact"
        assert doc.match_score == 1.0
        assert "概念A" in doc.name
        assert "核心原理" in doc.content
        assert doc.char_count > 50

    def test_exact_match_strips_frontmatter(self, retriever):
        doc = retriever.retrieve("concept-a", domain_id="test-domain")
        assert doc is not None
        # Should not contain YAML frontmatter
        assert "---" not in doc.content
        assert "title:" not in doc.content
        # Should not contain H1
        assert not doc.content.startswith("# ")

    def test_exact_match_not_found(self, retriever):
        doc = retriever.retrieve("nonexistent-concept", domain_id="test-domain")
        assert doc is None

    def test_fuzzy_match(self, retriever):
        # "koncept-a" should fuzzy-match "concept-a" (typo)
        doc = retriever.retrieve("koncept-a", domain_id="test-domain")
        assert doc is not None
        assert doc.match_type == "fuzzy"
        assert doc.match_score >= 0.6
        assert doc.match_score < 1.0

    def test_fuzzy_match_underscore_normalization(self, retriever):
        # "concept_a" (underscore) normalizes to "concept-a" and gets exact fuzzy score
        doc = retriever.retrieve("concept_a", domain_id="test-domain")
        assert doc is not None
        assert doc.match_type == "fuzzy"
        assert doc.match_score >= 0.9  # Very high because normalized forms are identical

    def test_file_fallback(self, retriever, rag_dir):
        """When concept isn't in index but file exists at expected path."""
        # Create a file not in the index
        sub_dir = rag_dir / "test-domain" / "advanced"
        sub_dir.mkdir(exist_ok=True)
        (sub_dir / "hidden-concept.md").write_text(
            "# Hidden\n\n这是一个隐藏概念的内容。详细内容在此。",
            encoding="utf-8",
        )
        doc = retriever.retrieve(
            "hidden-concept",
            domain_id="test-domain",
            subdomain_id="advanced",
        )
        assert doc is not None
        assert doc.match_type == "file_fallback"
        assert doc.match_score == 0.9

    def test_max_chars_truncation(self, retriever):
        doc = retriever.retrieve("concept-a", domain_id="test-domain", max_chars=50)
        assert doc is not None
        assert doc.char_count <= 80  # 50 + truncation notice

    def test_search_returns_results(self, retriever):
        results = retriever.search("概念", domain_id="test-domain", limit=5)
        assert len(results) >= 1
        for r in results:
            assert r.match_type == "search"
            assert r.match_score > 0

    def test_search_by_id(self, retriever):
        results = retriever.search("concept-a", domain_id="test-domain", limit=1)
        assert len(results) == 1
        assert results[0].concept_id == "concept-a"

    def test_search_empty_query(self, retriever):
        results = retriever.search("zzzzzzzzz_nomatch", domain_id="test-domain")
        assert len(results) == 0

    def test_nonexistent_domain(self, retriever):
        doc = retriever.retrieve("concept-a", domain_id="no-such-domain")
        assert doc is None


class TestReadAndStrip:
    def test_strips_yaml_and_h1(self, tmp_path):
        from engines.graph.rag import _read_and_strip
        p = tmp_path / "test.md"
        p.write_text("---\ntitle: X\n---\n# Title\n\nBody content here.", encoding="utf-8")
        result = _read_and_strip(str(p))
        assert "title:" not in result
        assert "# Title" not in result
        assert "Body content here." in result

    def test_no_frontmatter(self, tmp_path):
        from engines.graph.rag import _read_and_strip
        p = tmp_path / "test.md"
        p.write_text("# Just Title\n\nParagraph.", encoding="utf-8")
        result = _read_and_strip(str(p))
        assert "# Just" not in result
        assert "Paragraph." in result

    def test_missing_file(self):
        from engines.graph.rag import _read_and_strip
        assert _read_and_strip("/nonexistent/path.md") == ""


class TestPathSecurity:
    def test_path_traversal_blocked(self, retriever, rag_dir):
        """Ensure path traversal via index file entries is blocked."""
        from engines.graph.rag import _index_cache
        # First, trigger a load so the domain is in cache
        retriever.retrieve("concept-a", domain_id="test-domain")
        # Now inject a malicious index entry
        _index_cache["test-domain"]["by_id"]["evil"] = {
            "file": "../../etc/passwd",
            "name": "Evil",
            "subdomain_id": "hack",
        }
        doc = retriever.retrieve("evil", domain_id="test-domain")
        # Should return None because path traversal check fails
        assert doc is None
