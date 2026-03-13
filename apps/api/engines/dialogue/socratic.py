"""
苏格拉底式对话引擎
费曼学习法 + 追问/反问/引导式对话
"""

import json
from typing import AsyncIterator, Optional

from llm.router import llm_router
from engines.dialogue.prompts.feynman_system import (
    FEYNMAN_SYSTEM_PROMPT,
    GRAPH_CONTEXT_TEMPLATE,
)


class SocraticEngine:
    """苏格拉底式对话引擎 — 核心对话逻辑"""

    async def build_system_prompt(
        self,
        concept: dict,
        prerequisites: list[str] = None,
        dependents: list[str] = None,
        related: list[str] = None,
    ) -> str:
        """构建注入了图谱上下文的 System Prompt"""
        graph_context = GRAPH_CONTEXT_TEMPLATE.format(
            prerequisites=", ".join(prerequisites or []) or "无",
            dependents=", ".join(dependents or []) or "无",
            related=", ".join(related or []) or "无",
            is_milestone="⭐ 是（里程碑节点）" if concept.get("is_milestone") else "否",
        )

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
        ):
            yield chunk

    async def chat(
        self,
        system_prompt: str,
        messages: list[dict],
        user_message: str,
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
        )


# 全局单例
socratic_engine = SocraticEngine()
