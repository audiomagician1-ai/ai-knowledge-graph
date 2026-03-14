"""
LLM 分层调度路由器
支持 OpenAI 兼容 API（OpenRouter / DeepSeek / OpenAI 直连）
httpx 异步 + SSE 流式 + 重试
"""

import asyncio
import json
import logging
from typing import AsyncIterator, Optional

import httpx

from config import settings

logger = logging.getLogger(__name__)


class LLMRouter:
    """LLM 分层调度 — 按场景选择模型控制成本"""

    # OpenRouter 统一入口
    OPENROUTER_BASE = "https://openrouter.ai/api/v1"
    OPENAI_BASE = "https://api.openai.com/v1"
    DEEPSEEK_BASE = "https://api.deepseek.com/v1"

    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()

    @property
    def model_tiers(self) -> dict[str, str]:
        """Lazy evaluate model tiers from settings (avoids import-time access to unset env vars)"""
        return {
            "simple": settings.llm_model_simple,
            "dialogue": settings.llm_model_dialogue,
            "assessment": settings.llm_model_assessment,
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            async with self._client_lock:
                # Double-check after acquiring lock
                if self._client is None or self._client.is_closed:
                    self._client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))
        return self._client

    def _resolve_endpoint(self, model: str, user_config: dict | None = None) -> tuple[str, str]:
        """根据模型名决定 API base 和 key
        优先使用用户自带的 API Key.
        Supports custom base_url for internal/proxy endpoints.
        Raises ValueError if no API key is available."""
        # 用户自定义 Key 优先
        if user_config and user_config.get("api_key"):
            key = user_config["api_key"]
            # Custom base URL takes highest priority
            if user_config.get("base_url"):
                return user_config["base_url"].rstrip("/"), key
            provider = user_config.get("provider", "openrouter")
            if provider == "deepseek":
                return self.DEEPSEEK_BASE, key
            elif provider == "openai":
                return self.OPENAI_BASE, key
            elif provider == "custom":
                # custom provider without base_url — try openai-compatible default
                return self.OPENAI_BASE, key
            else:
                return self.OPENROUTER_BASE, key

        # 服务端 Key fallback
        if settings.openrouter_api_key:
            return self.OPENROUTER_BASE, settings.openrouter_api_key
        if model.startswith("deepseek/") and settings.deepseek_api_key:
            return self.DEEPSEEK_BASE, settings.deepseek_api_key
        if settings.openai_api_key:
            return self.OPENAI_BASE, settings.openai_api_key

        raise ValueError("No LLM API key configured. Set one in env or provide via request headers.")

    @staticmethod
    def _is_retryable(status_code: int) -> bool:
        """Only retry on 429 (rate limit) and 5xx (server errors)"""
        return status_code == 429 or status_code >= 500

    async def chat(
        self,
        messages: list[dict],
        tier: str = "dialogue",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        user_config: dict | None = None,
    ) -> str:
        """非流式对话 — 用于评估等需要完整响应的场景"""
        tiers = self.model_tiers
        model = tiers.get(tier, tiers["dialogue"])
        # 用户自定义模型覆盖
        if user_config and user_config.get("model"):
            model = user_config["model"]
        base_url, api_key = self._resolve_endpoint(model, user_config)

        # OpenRouter 用 model 原名; 直连时去掉 vendor/ 前缀
        model_name = model if "openrouter" in base_url else model.split("/")[-1]

        client = await self._get_client()
        last_error: Exception | None = None
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
            except httpx.HTTPStatusError as e:
                last_error = e
                if not self._is_retryable(e.response.status_code):
                    break  # 4xx (except 429) — don't retry
                logger.warning("LLM HTTP %d on attempt %d", e.response.status_code, attempt + 1)
            except (httpx.ReadTimeout, httpx.ConnectError) as e:
                last_error = e
                logger.warning("LLM network error on attempt %d: %s", attempt + 1, type(e).__name__)
            except KeyError as e:
                last_error = e
                break  # malformed response — don't retry

            if attempt < 2:
                await asyncio.sleep(2 ** attempt)

        raise RuntimeError(f"LLM call failed after retries: {last_error}") from last_error

    async def chat_stream(
        self,
        messages: list[dict],
        tier: str = "dialogue",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        user_config: dict | None = None,
    ) -> AsyncIterator[str]:
        """流式对话 — 用于实时对话 SSE"""
        tiers = self.model_tiers
        model = tiers.get(tier, tiers["dialogue"])
        if user_config and user_config.get("model"):
            model = user_config["model"]
        base_url, api_key = self._resolve_endpoint(model, user_config)
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
