"""对话引擎 API V2 — AI引导式探测学习 + 选项式交互 + 理解度评估
无需登录，支持用户自带 LLM API Key (通过请求头传递)
对话数据持久化到 SQLite — 重启不丢失

V2 变更:
- 开场白由 LLM 动态生成 (含 choices)
- /conversations 返回 opening_choices
- /chat SSE 新增 choices 事件 (从 LLM 回复中解析)
- ChatRequest 新增 is_choice 标记
"""

import asyncio
import json
import time
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from engines.dialogue.socratic import socratic_engine
from engines.dialogue.prompts.feynman_system import parse_ai_response
from engines.dialogue.evaluator import evaluator
from routers.graph import _load_seed
from rate_limiter import check_rate_limit
from db.sqlite_client import (
    save_conversation, save_message, get_conversation,
    get_conversation_messages, update_conversation_status,
    list_conversations as db_list_conversations,
    cleanup_old_conversations,
)
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter()

# In-memory caches for active sessions (system prompts + concept data)
# These are rebuilt on first access and don't need persistence
_session_cache: dict[str, dict] = {}
_session_locks: dict[str, asyncio.Lock] = {}

# Limits
_MAX_CACHE = 200
_CACHE_TTL_SEC = 3600  # 1 hour
_MAX_MESSAGES_PER_SESSION = 40  # Max messages in a single session (prevents unbounded growth)

# Valid LLM providers
_VALID_PROVIDERS = {"openrouter", "openai", "deepseek", "custom"}


_BUSY_TIMEOUT_SEC = 120  # Auto-release _busy after 120s (handles client disconnect edge cases)


def _cleanup_cache():
    """Remove expired cache entries, orphan locks, and stale _busy flags."""
    now = time.time()
    # Release stale _busy flags (C-03: handles edge cases where GeneratorExit not called)
    for v in _session_cache.values():
        if v.get("_busy") and now - v.get("_busy_since", 0) > _BUSY_TIMEOUT_SEC:
            v.pop("_busy", None)
            v.pop("_busy_since", None)
            logger.warning("Auto-released stale _busy for session %s", v.get("id"))
    expired = [k for k, v in _session_cache.items() if now - v.get("last_active", 0) > _CACHE_TTL_SEC]
    for k in expired:
        _session_cache.pop(k, None)
        _session_locks.pop(k, None)
    if len(_session_cache) > _MAX_CACHE:
        sorted_keys = sorted(_session_cache.keys(), key=lambda k: _session_cache[k].get("last_active", 0))
        for k in sorted_keys[: len(_session_cache) - _MAX_CACHE]:
            _session_cache.pop(k, None)
            _session_locks.pop(k, None)
    # Clean orphan locks (lock exists but cache evicted)
    orphan_locks = set(_session_locks.keys()) - set(_session_cache.keys())
    for k in orphan_locks:
        _session_locks.pop(k, None)


def _get_lock(conv_id: str) -> asyncio.Lock:
    return _session_locks.setdefault(conv_id, asyncio.Lock())


async def _ensure_session(conv_id: str) -> Optional[dict]:
    """Get or rebuild session from cache/DB (double-check locking to prevent concurrent rebuild)."""
    if conv_id in _session_cache:
        return _session_cache[conv_id]

    lock = _get_lock(conv_id)
    async with lock:
        # Double-check after acquiring lock
        if conv_id in _session_cache:
            return _session_cache[conv_id]

        # Try loading from SQLite
        conv = get_conversation(conv_id)
        if not conv:
            return None

        # Rebuild cache from DB
        domain_id = conv.get('domain_id', 'ai-engineering')
        concept = _get_concept_info(conv['concept_id'], domain_id)
        _session_cache[conv_id] = {
            "id": conv_id,
            "concept_id": conv['concept_id'],
            "domain_id": domain_id,
            "concept": concept or {"id": conv['concept_id'], "name": conv['concept_name']},
            "system_prompt": conv.get('system_prompt', ''),
            "messages": conv.get('messages', []),
            "status": conv.get('status', 'active'),
            "last_active": time.time(),
        }
        return _session_cache[conv_id]


class ConversationCreate(BaseModel):
    concept_id: str = Field(..., max_length=200)
    domain_id: str = Field(default="ai-engineering", max_length=100)


class ChatRequest(BaseModel):
    conversation_id: str = Field(..., max_length=200)
    message: str = Field(..., max_length=10000)
    is_choice: bool = False  # True when user clicked a preset choice option


class AssessmentRequest(BaseModel):
    conversation_id: str = Field(..., max_length=200)


def _extract_user_llm_config(request: Request) -> Optional[dict]:
    """从请求头提取用户自定义 LLM 配置"""
    api_key = request.headers.get("x-llm-api-key", "").strip()
    if not api_key:
        return None
    provider = request.headers.get("x-llm-provider", "openrouter").strip().lower()
    if provider not in _VALID_PROVIDERS:
        provider = "openrouter"
    return {
        "provider": provider,
        "api_key": api_key,
        "model": request.headers.get("x-llm-model", "").strip() or None,
        "base_url": request.headers.get("x-llm-base-url", "").strip() or None,
    }


def _get_concept_info(concept_id: str, domain_id: str = "ai-engineering") -> Optional[dict]:
    """从种子图谱获取概念信息"""
    seed = _load_seed(domain_id)
    for c in seed["concepts"]:
        if c["id"] == concept_id:
            prereqs, deps, related = [], [], []
            for e in seed["edges"]:
                if e["relation_type"] == "prerequisite":
                    if e["target_id"] == concept_id:
                        prereqs.append(e["source_id"])
                    elif e["source_id"] == concept_id:
                        deps.append(e["target_id"])
                elif e["relation_type"] == "related_to":
                    if e["source_id"] == concept_id:
                        related.append(e["target_id"])
                    elif e["target_id"] == concept_id:
                        related.append(e["source_id"])
            id_to_name = {cc["id"]: cc["name"] for cc in seed["concepts"]}
            return {
                **c,
                "prerequisite_names": [id_to_name.get(p, p) for p in prereqs],
                "dependent_names": [id_to_name.get(d, d) for d in deps],
                "related_names": [id_to_name.get(r, r) for r in related],
            }
    return None


@router.post("/conversations")
async def create_conversation(req: ConversationCreate, request: Request):
    """创建新的费曼对话会话 — V2: LLM生成开场白含选项"""
    _cleanup_cache()
    cleanup_old_conversations()

    concept = _get_concept_info(req.concept_id, req.domain_id)
    if not concept:
        raise HTTPException(status_code=404, detail=f"概念不存在: {req.concept_id} (domain={req.domain_id})")

    conv_id = str(uuid.uuid4())
    user_config = _extract_user_llm_config(request)

    # Rate limit check — only for free LLM users (no user key)
    allowed, rl_info = check_rate_limit(request, has_user_key=bool(user_config))
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"免费 AI 服务请求过于频繁，请 {rl_info['reset_after']} 秒后重试。或在设置页配置自己的 API Key 获取无限额度。",
            headers={"Retry-After": str(rl_info["reset_after"])},
        )

    system_prompt = await socratic_engine.build_system_prompt(
        concept=concept,
        prerequisites=concept.get("prerequisite_names", []),
        dependents=concept.get("dependent_names", []),
        related=concept.get("related_names", []),
    )

    # V2: LLM generates opening with choices
    opening_text, opening_choices = await socratic_engine.get_opening(
        concept, system_prompt, user_config=user_config,
    )

    # Store the full raw response (with choices) for message history
    # But the opening_message field is clean text only
    opening_raw = opening_text  # text-only for messages history

    # Persist to SQLite
    save_conversation(conv_id, req.concept_id, concept["name"], system_prompt,
                      is_milestone=concept.get("is_milestone", False),
                      domain_id=req.domain_id)
    save_message(conv_id, "assistant", opening_raw)

    # Cache in memory
    _session_cache[conv_id] = {
        "id": conv_id,
        "concept_id": req.concept_id,
        "domain_id": req.domain_id,
        "concept": concept,
        "system_prompt": system_prompt,
        "messages": [{"role": "assistant", "content": opening_raw}],
        "status": "active",
        "last_active": time.time(),
    }

    return {
        "conversation_id": conv_id,
        "concept_id": req.concept_id,
        "concept_name": concept["name"],
        "opening_message": opening_text,
        "opening_choices": opening_choices,
        "is_milestone": concept.get("is_milestone", False),
    }


@router.post("/chat")
async def chat(req: ChatRequest, request: Request):
    """发送消息 — SSE 流式响应"""
    _cleanup_cache()  # Periodically clean expired sessions & locks
    session = await _ensure_session(req.conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session["last_active"] = time.time()
    user_config = _extract_user_llm_config(request)

    # Rate limit check — only for free LLM users (no user key)
    allowed, rl_info = check_rate_limit(request, has_user_key=bool(user_config))
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"免费 AI 服务请求过于频繁，请 {rl_info['reset_after']} 秒后重试。或在设置页配置自己的 API Key 获取无限额度。",
            headers={"Retry-After": str(rl_info["reset_after"])},
        )

    from config import settings
    has_server_key = bool(settings.openrouter_api_key or settings.openai_api_key or settings.deepseek_api_key)
    if not user_config and not has_server_key:
        async def no_key_response():
            msg = "⚠️ 还没有配置 LLM API Key 哦！请到「设置」页面配置你的 API Key，然后就可以开始对话了。"
            async with _get_lock(req.conversation_id):
                session["messages"].append({"role": "user", "content": req.message})
                session["messages"].append({"role": "assistant", "content": msg})
            # DB writes outside lock to avoid blocking event loop while holding lock
            await asyncio.to_thread(save_message, req.conversation_id, "user", req.message)
            await asyncio.to_thread(save_message, req.conversation_id, "assistant", msg)
            yield f"data: {json.dumps({'type': 'chunk', 'content': msg}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'suggest_assess': False}, ensure_ascii=False)}\n\n"
        return StreamingResponse(no_key_response(), media_type="text/event-stream")

    # C-02 fix: single lock block for _busy check + message append (no TOCTOU window)
    lock = _get_lock(req.conversation_id)
    async with lock:
        if session.get("_busy"):
            raise HTTPException(status_code=429, detail="该会话正在处理中，请稍后重试")
        session["_busy"] = True
        session["_busy_since"] = time.time()
        session["messages"].append({"role": "user", "content": req.message})
        # Truncate to sliding window if exceeding limit (keep first + context notice + last N)
        if len(session["messages"]) > _MAX_MESSAGES_PER_SESSION:
            first_msg = session["messages"][:1]  # Keep opening
            recent = session["messages"][-(_MAX_MESSAGES_PER_SESSION - 2):]
            truncation_notice = {"role": "system", "content": "[对话历史已截断，以下为最近的对话记录]"}
            session["messages"] = first_msg + [truncation_notice] + recent
        # M-05 fix: snapshot messages before releasing lock (prevent reads of mutated state)
        messages_snapshot = list(session["messages"])
    await asyncio.to_thread(save_message, req.conversation_id, "user", req.message)

    async def generate():
        full_response = ""
        try:
            async for chunk in socratic_engine.chat_stream(
                system_prompt=session["system_prompt"],
                messages=messages_snapshot[:-1],
                user_message=req.message,
                user_config=user_config,
            ):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"

            # V2: Parse choices from full LLM response
            parsed = parse_ai_response(full_response)
            clean_content = parsed["content"]
            choices = parsed["choices"]

            async with lock:
                session["messages"].append({"role": "assistant", "content": clean_content})
            await asyncio.to_thread(save_message, req.conversation_id, "assistant", clean_content)

            user_turns = sum(1 for m in session["messages"] if m["role"] == "user")
            suggest_assess = user_turns >= 4

            # Send choices as separate SSE event
            yield f"data: {json.dumps({'type': 'choices', 'choices': choices}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'suggest_assess': suggest_assess, 'turn': user_turns}, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.warning("Chat stream error for %s: %s", req.conversation_id, e)
            fallback = "抱歉，我刚才走神了 😅 你能再说一遍吗？我保证认真听！"
            fallback_choices = [
                {"id": "opt-1", "text": "重新说一遍", "type": "action"},
                {"id": "opt-2", "text": "换个方式解释", "type": "explore"},
            ]
            async with lock:
                session["messages"].append({"role": "assistant", "content": fallback})
            await asyncio.to_thread(save_message, req.conversation_id, "assistant", fallback)
            yield f"data: {json.dumps({'type': 'chunk', 'content': fallback}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'choices', 'choices': fallback_choices}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'suggest_assess': False}, ensure_ascii=False)}\n\n"
        finally:
            session.pop("_busy", None)  # Always release — handles client disconnect (GeneratorExit)
            session.pop("_busy_since", None)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/assess")
async def assess_understanding(req: AssessmentRequest, request: Request):
    """请求理解度评估"""
    _cleanup_cache()  # Periodically clean expired sessions & locks
    session = await _ensure_session(req.conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    user_config = _extract_user_llm_config(request)

    # Rate limit check — only for free LLM users (no user key)
    allowed, rl_info = check_rate_limit(request, has_user_key=bool(user_config))
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail=f"免费 AI 服务请求过于频繁，请 {rl_info['reset_after']} 秒后重试。或在设置页配置自己的 API Key 获取无限额度。",
            headers={"Retry-After": str(rl_info["reset_after"])},
        )

    concept = session["concept"]
    messages = session["messages"]

    user_turns = sum(1 for m in messages if m["role"] == "user")
    if user_turns < 2:
        raise HTTPException(status_code=400, detail=f"请至少进行 2 轮对话后再评估，当前 {user_turns} 轮")

    result = await evaluator.evaluate(concept=concept, messages=messages, user_config=user_config)

    if result.get("mastered"):
        session["status"] = "completed"
        update_conversation_status(req.conversation_id, "completed")

    return {
        "concept_id": session["concept_id"],
        "concept_name": concept["name"],
        "turns": user_turns,
        **result,
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation_detail(conversation_id: str):
    """获取会话详情"""
    session = await _ensure_session(conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {
        "id": session["id"],
        "concept_id": session["concept_id"],
        "concept_name": session["concept"]["name"],
        "messages": session["messages"],
        "status": session["status"],
        "turns": sum(1 for m in session["messages"] if m["role"] == "user"),
    }


@router.get("/conversations")
async def list_conversations():
    """列出所有会话"""
    return db_list_conversations()

