"""
苏格拉底式对话引擎 V2
AI引导式探测学习: 破冰探测 → 自适应讲解 → 理解检验 → 总结深化
每次AI回复都附带2-4个可选选项，支持 RAG 知识库文档注入
"""

import json
import logging
import os
import sys
from typing import AsyncIterator, Optional

logger = logging.getLogger(__name__)

from llm.router import llm_router
from engines.dialogue.prompts.feynman_system import (
    FEYNMAN_SYSTEM_PROMPT,
    GRAPH_CONTEXT_TEMPLATE,
    DOMAIN_SUPPLEMENTS,
    parse_ai_response,
)


def _get_rag_dir() -> str:
    """获取 RAG 文档目录路径"""
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "rag_data")
    # socratic.py is at apps/api/engines/dialogue/ — need 5 levels up to project root
    return os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
        "data", "rag",
    )


def _load_rag_content(concept_id: str, subdomain_id: str, domain_id: str = "ai-engineering") -> str:
    """加载概念的 RAG 参考文档内容"""
    rag_dir = _get_rag_dir()
    # ai-engineering: flat structure {subdomain}/{concept}.md
    # other domains: {domain_id}/{subdomain}/{concept}.md
    if domain_id == "ai-engineering":
        doc_path = os.path.join(rag_dir, subdomain_id, f"{concept_id}.md")
    else:
        doc_path = os.path.join(rag_dir, domain_id, subdomain_id, f"{concept_id}.md")

    if not os.path.exists(doc_path):
        return ""

    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 去掉 YAML frontmatter
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                content = content[end + 3:].strip()

        # 去掉一级标题（# xxx）
        lines = content.split("\n")
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        content = "\n".join(lines).strip()

        # 截断到合理长度（避免 system prompt 过长）
        if len(content) > 3000:
            content = content[:3000] + "\n\n... (参考文档已截断)"

        return content
    except Exception:
        return ""


# The LLM generates the opening as Phase 1 (probe), no hardcoded templates
OPENING_USER_PROMPT = "开始学习「{concept_name}」"


class SocraticEngine:
    """苏格拉底式对话引擎 V2 — AI引导式探测学习"""

    async def build_system_prompt(
        self,
        concept: dict,
        prerequisites: list[str] = None,
        dependents: list[str] = None,
        related: list[str] = None,
    ) -> str:
        """构建注入了图谱上下文和 RAG 文档的 System Prompt"""
        graph_context = GRAPH_CONTEXT_TEMPLATE.format(
            prerequisites=", ".join(prerequisites or []) or "无",
            dependents=", ".join(dependents or []) or "无",
            related=", ".join(related or []) or "无",
            is_milestone="⭐ 是（里程碑节点）" if concept.get("is_milestone") else "否",
        )

        # 加载 RAG 参考文档
        rag_content = _load_rag_content(
            concept["id"],
            concept.get("subdomain_id", ""),
            concept.get("domain_id", "ai-engineering"),
        )
        if rag_content:
            graph_context += f"\n\n## 参考知识文档（你的讲解素材，请基于以下内容进行教学）\n\n{rag_content}"

        # Domain-specific prompt supplement (registry lookup)
        domain_id = concept.get("domain_id", "ai-engineering")
        domain_supplement = DOMAIN_SUPPLEMENTS.get(domain_id, "")
        if domain_supplement:
            graph_context += domain_supplement

        return FEYNMAN_SYSTEM_PROMPT.format(
            concept_name=concept["name"],
            subdomain_name=concept.get("subdomain_name", concept.get("subdomain_id", "")),
            difficulty=concept.get("difficulty", 5),
            content_type=concept.get("content_type", "theory"),
            graph_context=graph_context,
        )

    async def get_opening(
        self,
        concept: dict,
        system_prompt: str,
        user_config: dict | None = None,
    ) -> tuple[str, list[dict]]:
        """LLM 生成开场白 (Phase 1: 破冰探测).

        Returns:
            (opening_text, opening_choices)
        """
        user_msg = OPENING_USER_PROMPT.format(concept_name=concept["name"])

        try:
            raw = await llm_router.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
                tier="dialogue",
                temperature=0.8,
                max_tokens=600,
                user_config=user_config,
            )
            parsed = parse_ai_response(raw)
            return parsed["content"], parsed["choices"]
        except Exception as e:
            logger.warning("Opening LLM call failed for %s: %s", concept["name"], e)
            # Fallback: hardcoded opening for resilience
            name = concept["name"]
            fallback_text = (
                f"👋 今天我们一起来探索「{name}」！\n\n"
                f"这是一个很有意思的概念，让我先简单介绍一下，"
                f"然后我们一步步深入。\n\n"
                f"你之前对 {name} 有了解吗？"
            )
            fallback_choices = [
                {"id": "opt-1", "text": "完全没听说过", "type": "level"},
                {"id": "opt-2", "text": "听过但说不太清楚", "type": "level"},
                {"id": "opt-3", "text": "有一些了解，想深入", "type": "level"},
                {"id": "opt-4", "text": "比较熟悉，直接进阶", "type": "level"},
            ]
            return fallback_text, fallback_choices

    async def chat_stream(
        self,
        system_prompt: str,
        messages: list[dict],
        user_message: str,
        user_config: dict | None = None,
    ) -> AsyncIterator[str]:
        """流式对话 — 返回 AI 回复的文本 chunk"""
        full_messages = [
            {"role": "system", "content": system_prompt},
            *messages,
            {"role": "user", "content": user_message},
        ]

        async for chunk in llm_router.chat_stream(
            messages=full_messages,
            tier="dialogue",
            temperature=0.75,
            max_tokens=800,
            user_config=user_config,
        ):
            yield chunk

    async def chat(
        self,
        system_prompt: str,
        messages: list[dict],
        user_message: str,
        user_config: dict | None = None,
    ) -> str:
        """非流式对话 — 返回完整回复"""
        full_messages = [
            {"role": "system", "content": system_prompt},
            *messages,
            {"role": "user", "content": user_message},
        ]

        return await llm_router.chat(
            messages=full_messages,
            tier="dialogue",
            temperature=0.75,
            max_tokens=800,
            user_config=user_config,
        )


# 全局单例
socratic_engine = SocraticEngine()
