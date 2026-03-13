"""
苏格拉底式对话引擎
"先导后学"混合模式: AI 先讲解 → 变身好奇学生提问 → 用户解答 → AI 反馈
支持 RAG 知识库文档注入，为 AI 提供准确的概念参考知识
"""

import json
import os
import sys
from typing import AsyncIterator, Optional

from llm.router import llm_router
from engines.dialogue.prompts.feynman_system import (
    FEYNMAN_SYSTEM_PROMPT,
    GRAPH_CONTEXT_TEMPLATE,
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


def _load_rag_content(concept_id: str, subdomain_id: str) -> str:
    """加载概念的 RAG 参考文档内容"""
    rag_dir = _get_rag_dir()
    doc_path = os.path.join(rag_dir, subdomain_id, f"{concept_id}.md")

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


class SocraticEngine:
    """苏格拉底式对话引擎 — 核心对话逻辑"""

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
        )
        if rag_content:
            graph_context += f"\n\n## 参考知识文档（你的讲解素材，请基于以下内容进行教学）\n\n{rag_content}"

        return FEYNMAN_SYSTEM_PROMPT.format(
            concept_name=concept["name"],
            subdomain_name=concept.get("subdomain_id", ""),
            difficulty=concept.get("difficulty", 5),
            content_type=concept.get("content_type", "theory"),
            graph_context=graph_context,
        )

    async def get_opening(self, concept: dict) -> str:
        """生成开场白 — AI 学生表达好奇心"""
        name = concept["name"]
        difficulty = concept.get("difficulty", 5)

        if difficulty <= 3:
            return (
                f"嗨！👋 我听说{name}是编程中很基础但很重要的概念。"
                f"不过我还不太理解它到底是什么意思。你能用最简单的话给我解释一下吗？"
            )
        elif difficulty <= 6:
            return (
                f"嗨！🤔 我最近在学习{name}，感觉挺有意思但又有点复杂。"
                f"你对这个概念了解多少？能试着用最直白的方式给我讲讲吗？"
            )
        else:
            return (
                f"嗨！🧐 {name}这个话题看起来挺深的，我之前一直没搞明白。"
                f"听说你对这方面有研究，能帮我从头捋一下吗？先从最核心的概念开始？"
            )

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
            max_tokens=512,
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
            max_tokens=512,
            user_config=user_config,
        )


# 全局单例
socratic_engine = SocraticEngine()
