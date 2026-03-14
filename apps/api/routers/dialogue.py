"""对话引擎 API — 费曼对话 + 苏格拉底追问 + 理解度评估
无需登录，支持用户自带 LLM API Key (通过请求头传递)
对话数据持久化到 SQLite — 重启不丢失"""

import asyncio
import json
import time
import uuid
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from engines.dialogue.socratic import socratic_engine
from engines.dialogue.evaluator import evaluator
from routers.graph import _load_seed
from db.sqlite_client import (
    save_conversation, save_message, get_conversation,
    get_conversation_messages, update_conversation_status,
    list_conversations as db_list_conversations,
    cleanup_old_conversations,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory caches for active sessions (system prompts + concept data)
# These are rebuilt on first access and don't need persistence
_session_cache: dict[str, dict] = {}
_session_locks: dict[str, asyncio.Lock] = {}

# Limits
_MAX_CACHE = 200
_CACHE_TTL_SEC = 3600  # 1 hour

# Valid LLM providers
_VALID_PROVIDERS = {"openrouter", "openai", "deepseek", "custom"}


def _cleanup_cache():
    """Remove expired cache entries."""
    now = time.time()
    expired = [k for k, v in _session_cache.items() if now - v.get("last_active", 0) > _CACHE_TTL_SEC]
    for k in expired:
        _session_cache.pop(k, None)
        _session_locks.pop(k, None)
    if len(_session_cache) > _MAX_CACHE:
        sorted_keys = sorted(_session_cache.keys(), key=lambda k: _session_cache[k].get("last_active", 0))
        for k in sorted_keys[: len(_session_cache) - _MAX_CACHE]:
            _session_cache.pop(k, None)
            _session_locks.pop(k, None)


def _get_lock(conv_id: str) -> asyncio.Lock:
    if conv_id not in _session_locks:
        _session_locks[conv_id] = asyncio.Lock()
    return _session_locks[conv_id]


async def _ensure_session(conv_id: str) -> Optional[dict]:
    """Get or rebuild session from cache/DB."""
    if conv_id in _session_cache:
        return _session_cache[conv_id]

    # Try loading from SQLite
    conv = get_conversation(conv_id)
    if not conv:
        return None

    # Rebuild cache from DB
    concept = _get_concept_info(conv['concept_id'])
    _session_cache[conv_id] = {
        "id": conv_id,
        "concept_id": conv['concept_id'],
        "concept": concept or {"id": conv['concept_id'], "name": conv['concept_name']},
        "system_prompt": conv.get('system_prompt', ''),
        "messages": conv.get('messages', []),
        "status": conv.get('status', 'active'),
        "last_active": time.time(),
    }
    return _session_cache[conv_id]


class ConversationCreate(BaseModel):
    concept_id: str


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


class AssessmentRequest(BaseModel):
    conversation_id: str


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


def _get_concept_info(concept_id: str) -> Optional[dict]:
    """从种子图谱获取概念信息"""
    seed = _load_seed()
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
async def create_conversation(req: ConversationCreate):
    """创建新的费曼对话会话"""
    _cleanup_cache()
    cleanup_old_conversations()

    concept = _get_concept_info(req.concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail=f"概念不存在: {req.concept_id}")

    conv_id = str(uuid.uuid4())

    system_prompt = await socratic_engine.build_system_prompt(
        concept=concept,
        prerequisites=concept.get("prerequisite_names", []),
        dependents=concept.get("dependent_names", []),
        related=concept.get("related_names", []),
    )

    opening = await socratic_engine.get_opening(concept)

    # Persist to SQLite
    save_conversation(conv_id, req.concept_id, concept["name"], system_prompt,
                      is_milestone=concept.get("is_milestone", False))
    save_message(conv_id, "assistant", opening)

    # Cache in memory
    _session_cache[conv_id] = {
        "id": conv_id,
        "concept_id": req.concept_id,
        "concept": concept,
        "system_prompt": system_prompt,
        "messages": [{"role": "assistant", "content": opening}],
        "status": "active",
        "last_active": time.time(),
    }

    return {
        "conversation_id": conv_id,
        "concept_id": req.concept_id,
        "concept_name": concept["name"],
        "opening_message": opening,
        "is_milestone": concept.get("is_milestone", False),
    }


@router.post("/chat")
async def chat(req: ChatRequest, request: Request):
    """发送消息 — SSE 流式响应"""
    session = await _ensure_session(req.conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    session["last_active"] = time.time()
    user_config = _extract_user_llm_config(request)

    from config import settings
    has_server_key = bool(settings.openrouter_api_key or settings.openai_api_key or settings.deepseek_api_key)
    if not user_config and not has_server_key:
        async def no_key_response():
            msg = "⚠️ 还没有配置 LLM API Key 哦！请到「设置」页面配置你的 API Key，然后就可以开始对话了。"
            async with _get_lock(req.conversation_id):
                session["messages"].append({"role": "user", "content": req.message})
                session["messages"].append({"role": "assistant", "content": msg})
            save_message(req.conversation_id, "user", req.message)
            save_message(req.conversation_id, "assistant", msg)
            yield f"data: {json.dumps({'type': 'chunk', 'content': msg}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'suggest_assess': False}, ensure_ascii=False)}\n\n"
        return StreamingResponse(no_key_response(), media_type="text/event-stream")

    lock = _get_lock(req.conversation_id)
    async with lock:
        session["messages"].append({"role": "user", "content": req.message})
    save_message(req.conversation_id, "user", req.message)

    async def generate():
        full_response = ""
        try:
            async for chunk in socratic_engine.chat_stream(
                system_prompt=session["system_prompt"],
                messages=session["messages"][:-1],
                user_message=req.message,
                user_config=user_config,
            ):
                full_response += chunk
                yield f"data: {json.dumps({'type': 'chunk', 'content': chunk}, ensure_ascii=False)}\n\n"

            async with lock:
                session["messages"].append({"role": "assistant", "content": full_response})
            save_message(req.conversation_id, "assistant", full_response)

            user_turns = sum(1 for m in session["messages"] if m["role"] == "user")
            suggest_assess = user_turns >= 4

            yield f"data: {json.dumps({'type': 'done', 'suggest_assess': suggest_assess, 'turn': user_turns}, ensure_ascii=False)}\n\n"
        except Exception as e:
            logger.warning("Chat stream error for %s: %s", req.conversation_id, e)
            fallback = "抱歉，我刚才走神了 😅 你能再说一遍吗？我保证认真听！"
            async with lock:
                session["messages"].append({"role": "assistant", "content": fallback})
            save_message(req.conversation_id, "assistant", fallback)
            yield f"data: {json.dumps({'type': 'chunk', 'content': fallback}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'suggest_assess': False}, ensure_ascii=False)}\n\n"

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
    session = await _ensure_session(req.conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    user_config = _extract_user_llm_config(request)
    concept = session["concept"]
    messages = session["messages"]

    user_turns = sum(1 for m in messages if m["role"] == "user")
    if user_turns < 2:
        return {"error": "请至少进行 2 轮对话后再评估", "current_turns": user_turns}

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

