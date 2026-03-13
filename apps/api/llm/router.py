"""
LLM 分层调度路由器
支持 OpenAI 兼容 API（OpenRouter / DeepSeek / OpenAI 直连）
httpx 异步 + SSE 流式 + 重试
"""

import asyncio
import json
from typing import AsyncIterator, Optional

import httpx

from config import settings


class LLMRouter:
    """LLM 分层调度 — 按场景选择模型控制成本"""

    MODEL_TIERS = {
        "simple": settings.llm_model_simple,
        "dialogue": settings.llm_model_dialogue,
        "assessment": settings.llm_model_assessment,
    }

    # OpenRouter 统一入口
    OPENROUTER_BASE = "https://openrouter.ai/api/v1"
    OPENAI_BASE = "https://api.openai.com/v1"
    DEEPSEEK_BASE = "https://api.deepseek.com/v1"

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))
        return self._client

    def _resolve_endpoint(self, model: str) -> tuple[str, str]:
        """根据模型名决定 API base 和 key"""
        if settings.openrouter_api_key:
            return self.OPENROUTER_BASE, settings.openrouter_api_key
        if model.startswith("deepseek/") and settings.deepseek_api_key:
            return self.DEEPSEEK_BASE, settings.deepseek_api_key
        return self.OPENAI_BASE, settings.openai_api_key

    async def chat(
        self,
        messages: list[dict],
        tier: str = "dialogue",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """非流式对话 — 用于评估等需要完整响应的场景"""
        model = self.MODEL_TIERS.get(tier, self.MODEL_TIERS["dialogue"])
        base_url, api_key = self._resolve_endpoint(model)

        # OpenRouter 用 model 原名; 直连时去掉 vendor/ 前缀
        model_name = model if "openrouter" in base_url else model.split("/")[-1]

        client = await self._get_client()
        for attempt in range(3):
            try:
                resp = await client.post(
                    f"{base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model_name,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            except (httpx.HTTPStatusError, httpx.ReadTimeout, KeyError) as e:
                if attempt < 2:
                    await asyncio.sleep(1.5 ** attempt)
                    continue
                raise RuntimeError(f"LLM call failed after 3 attempts: {e}") from e

    async def chat_stream(
        self,
        messages: list[dict],
        tier: str = "dialogue",
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncIterator[str]:
        """流式对话 — 用于实时对话 SSE"""
        model = self.MODEL_TIERS.get(tier, self.MODEL_TIERS["dialogue"])
        base_url, api_key = self._resolve_endpoint(model)
        model_name = model if "openrouter" in base_url else model.split("/")[-1]

        client = await self._get_client()
        async with client.stream(
            "POST",
            f"{base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            },
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk["choices"][0].get("delta", {})
                    if "content" in delta and delta["content"]:
                        yield delta["content"]
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()


# 全局单例
llm_router = LLMRouter()
