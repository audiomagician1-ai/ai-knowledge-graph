"""
RAG 知识检索模块 — 独立于对话引擎的知识文档检索层

当前实现: 精确匹配 (via _index.json) + 模糊匹配 fallback
未来扩展: 向量语义检索 (sqlite-vss / Cloudflare Vectorize)

设计决策 (ADR-014):
- 精确匹配覆盖 97.7% 概念 (6156/6300)，满足当前需求
- 模糊匹配处理 concept_id 不完全匹配的 2.3% 边缘情况
- 向量检索作为 Phase 2 保留，当前 ROI 不足（需嵌入模型成本）
"""

from __future__ import annotations

import json
import os
import sys
import threading
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class RAGDocument:
    """A retrieved RAG document."""
    concept_id: str
    name: str
    domain_id: str
    subdomain_id: str
    content: str
    char_count: int
    match_type: str = "exact"  # exact | fuzzy | alias
    match_score: float = 1.0


def _get_rag_dir() -> str:
    """Get RAG document root directory."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "rag_data")
    # rag.py is at apps/api/engines/graph/
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))))),
        "data", "rag",
    )


# ── Index Cache ──────────────────────────────────────────

_index_cache: dict[str, dict] = {}
_index_lock = threading.Lock()


def _load_index(domain_id: str) -> dict:
    """Load RAG index for a domain (thread-safe, cached)."""
    if domain_id in _index_cache:
        return _index_cache[domain_id]
    with _index_lock:
        if domain_id not in _index_cache:
            rag_dir = _get_rag_dir()
            idx_path = os.path.join(rag_dir, domain_id, "_index.json")
            if not os.path.exists(idx_path):
                # Legacy fallback for ai-engineering
                if domain_id == "ai-engineering":
                    idx_path = os.path.join(rag_dir, "_index.json")
            if os.path.exists(idx_path):
                with open(idx_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Build lookup by ID
                docs = data.get("documents", [])
                _index_cache[domain_id] = {
                    "by_id": {d["id"]: d for d in docs},
                    "by_name": {d.get("name", ""): d for d in docs if d.get("name")},
                    "all_ids": [d["id"] for d in docs],
                }
            else:
                _index_cache[domain_id] = {"by_id": {}, "by_name": {}, "all_ids": []}
    return _index_cache[domain_id]


# ── Content Loading ──────────────────────────────────────

def _read_and_strip(filepath: str, max_chars: int = 3000) -> str:
    """Read a markdown file, strip frontmatter and H1, truncate if needed."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return ""

    # Strip YAML frontmatter
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            content = content[end + 3:].strip()

    # Strip H1
    lines = content.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    content = "\n".join(lines).strip()

    # Truncate
    if max_chars and len(content) > max_chars:
        content = content[:max_chars] + "\n\n... (参考文档已截断)"

    return content


# ── Public API ───────────────────────────────────────────

class RAGRetriever:
    """Knowledge document retriever with exact + fuzzy matching."""

    def __init__(self):
        self._rag_dir = _get_rag_dir()

    def retrieve(
        self,
        concept_id: str,
        domain_id: str = "ai-engineering",
        subdomain_id: str = "",
        max_chars: int = 3000,
    ) -> Optional[RAGDocument]:
        """Retrieve RAG document for a concept.

        Strategy:
        1. Exact match via _index.json (97.7% hit rate)
        2. File path fallback (legacy ai-engineering flat structure)
        3. Fuzzy match on concept names (for inexact IDs)
        """
        # Strategy 1: Exact index match
        index = _load_index(domain_id)
        doc_entry = index["by_id"].get(concept_id)

        if doc_entry:
            filepath = os.path.join(self._rag_dir, doc_entry["file"])
            filepath = os.path.normpath(filepath)
            # Security: path traversal check
            if not os.path.normcase(filepath).startswith(
                os.path.normcase(os.path.normpath(self._rag_dir))
            ):
                return None
            if os.path.exists(filepath):
                content = _read_and_strip(filepath, max_chars)
                if content:
                    return RAGDocument(
                        concept_id=concept_id,
                        name=doc_entry.get("name", concept_id),
                        domain_id=domain_id,
                        subdomain_id=doc_entry.get("subdomain_id", subdomain_id),
                        content=content,
                        char_count=len(content),
                        match_type="exact",
                        match_score=1.0,
                    )

        # Strategy 2: File path fallback
        if subdomain_id:
            if domain_id == "ai-engineering":
                fallback_path = os.path.join(
                    self._rag_dir, subdomain_id, f"{concept_id}.md"
                )
            else:
                fallback_path = os.path.join(
                    self._rag_dir, domain_id, subdomain_id, f"{concept_id}.md"
                )
            if os.path.exists(fallback_path):
                content = _read_and_strip(fallback_path, max_chars)
                if content:
                    return RAGDocument(
                        concept_id=concept_id,
                        name=concept_id,
                        domain_id=domain_id,
                        subdomain_id=subdomain_id,
                        content=content,
                        char_count=len(content),
                        match_type="file_fallback",
                        match_score=0.9,
                    )

        # Strategy 3: Fuzzy match on IDs
        best_match = self._fuzzy_match(concept_id, index)
        if best_match:
            matched_entry = index["by_id"][best_match[0]]
            filepath = os.path.join(self._rag_dir, matched_entry["file"])
            if os.path.exists(filepath):
                content = _read_and_strip(filepath, max_chars)
                if content:
                    return RAGDocument(
                        concept_id=best_match[0],
                        name=matched_entry.get("name", best_match[0]),
                        domain_id=domain_id,
                        subdomain_id=matched_entry.get("subdomain_id", ""),
                        content=content,
                        char_count=len(content),
                        match_type="fuzzy",
                        match_score=best_match[1],
                    )

        return None

    def _fuzzy_match(
        self,
        concept_id: str,
        index: dict,
        threshold: float = 0.6,
    ) -> Optional[tuple[str, float]]:
        """Find best fuzzy match for a concept ID.

        Uses SequenceMatcher ratio. Returns (matched_id, score) or None.
        """
        best_id = None
        best_score = 0.0
        normalized = concept_id.lower().replace("_", "-")

        for candidate_id in index["all_ids"]:
            candidate_norm = candidate_id.lower().replace("_", "-")
            score = SequenceMatcher(None, normalized, candidate_norm).ratio()
            if score > best_score:
                best_score = score
                best_id = candidate_id

        if best_score >= threshold and best_id:
            return (best_id, round(best_score, 3))
        return None

    def search(
        self,
        query: str,
        domain_id: str = "ai-engineering",
        limit: int = 5,
    ) -> list[RAGDocument]:
        """Search RAG documents by fuzzy name/ID matching.

        Returns top-N matches sorted by relevance score.
        Future: replace with vector similarity search.
        """
        index = _load_index(domain_id)
        scored: list[tuple[str, float]] = []
        query_lower = query.lower()

        for doc_id in index["all_ids"]:
            entry = index["by_id"][doc_id]
            # Score based on ID match + name match
            id_score = SequenceMatcher(
                None, query_lower, doc_id.lower()
            ).ratio()
            name = entry.get("name", "").lower()
            name_score = SequenceMatcher(
                None, query_lower, name
            ).ratio() if name else 0
            score = max(id_score, name_score)
            if score > 0.3:
                scored.append((doc_id, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        results: list[RAGDocument] = []

        for doc_id, score in scored[:limit]:
            entry = index["by_id"][doc_id]
            filepath = os.path.join(self._rag_dir, entry["file"])
            if os.path.exists(filepath):
                # Only read first 500 chars for search results
                content = _read_and_strip(filepath, 500)
                results.append(RAGDocument(
                    concept_id=doc_id,
                    name=entry.get("name", doc_id),
                    domain_id=domain_id,
                    subdomain_id=entry.get("subdomain_id", ""),
                    content=content,
                    char_count=len(content),
                    match_type="search",
                    match_score=round(score, 3),
                ))

        return results


# Module-level singleton
rag_retriever = RAGRetriever()