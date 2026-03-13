"""对话引擎 API — 费曼对话 + 苏格拉底追问 + 理解度评估
无需登录，支持用户自带 LLM API Key (通过请求头传递)"""

import json
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from engines.dialogue.socratic import socratic_engine
from engines.dialogue.evaluator import evaluator
from routers.graph import _load_seed


router = APIRouter()

# 内存会话存储（MVP 阶段，后续迁移到 Redis/Supabase）
_sessions: dict[str, dict] = {}


class ConversationCreate(BaseModel):
    concept_id: str


class ChatRequest(BaseModel):
    conversation_id: str
    message: str


class AssessmentRequest(BaseModel):
    conversation_id: str


def _extract_user_llm_config(request: Request) -> Optional[dict]:
    """从请求头提取用户自定义 LLM 配置
    Headers:
      X-LLM-Provider: openrouter | openai | deepseek
      X-LLM-API-Key: sk-...
      X-LLM-Model: (optional) model name override
    """
    api_key = request.headers.get("x-llm-api-key", "").strip()
    if not api_key:
        return None
    return {
        "provider": request.headers.get("x-llm-provider", "openrouter").strip(),
        "api_key": api_key,
        "model": request.headers.get("x-llm-model", "").strip() or None,
    }


def _get_concept_info(concept_id: str) -> Optional[dict]:
    """从种子图谱获取概念信息"""
    seed = _load_seed()
    for c in seed["concepts"]:
        if c["id"] == concept_id:
            # 收集先修和后续
            prereqs = []
            deps = []
            related = []
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

            # 名称映射
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
    concept = _get_concept_info(req.concept_id)
    if not concept:
        raise HTTPException(status_code=404, detail=f"概念不存在: {req.concept_id}")

    conv_id = str(uuid.uuid4())[:12]

    # 构建 system prompt
    system_prompt = await socratic_engine.build_system_prompt(
        concept=concept,
        prerequisites=concept.get("prerequisite_names", []),
        dependents=concept.get("dependent_names", []),
        related=concept.get("related_names", []),
    )

    # 生成开场白
    opening = await socratic_engine.get_opening(concept)

    # 保存会话
    _sessions[conv_id] = {
        "id": conv_id,
        "concept_id": req.concept_id,
        "concept": concept,
        "system_prompt": system_prompt,
        "messages": [
            {"role": "assistant", "content": opening},
        ],
        "status": "active",
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
    session = _sessions.get(req.conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    user_config = _extract_user_llm_config(request)

    # 验证有可用的 LLM Key
    from config import settings
    has_server_key = bool(settings.openrouter_api_key or settings.openai_api_key or settings.deepseek_api_key)
    if not user_config and not has_server_key:
        async def no_key_response():
            msg = "⚠️ 还没有配置 LLM API Key 哦！请到「设置」页面配置你的 API Key，然后就可以开始对话了。"
            session["messages"].append({"role": "user", "content": req.message})
            session["messages"].append({"role": "assistant", "content": msg})
            yield f"data: {json.dumps({'type': 'chunk', 'content': msg}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'suggest_assess': False}, ensure_ascii=False)}\n\n"
        return StreamingResponse(no_key_response(), media_type="text/event-stream")

    # 添加用户消息到历史
    session["messages"].append({"role": "user", "content": req.message})

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

            # 保存完整的 AI 回复
            session["messages"].append({"role": "assistant", "content": full_response})

            # 检查是否应该提示评估（4轮用户消息后）
            user_turns = sum(1 for m in session["messages"] if m["role"] == "user")
            suggest_assess = user_turns >= 4

            yield f"data: {json.dumps({'type': 'done', 'suggest_assess': suggest_assess, 'turn': user_turns}, ensure_ascii=False)}\n\n"
        except Exception as e:
            fallback = "抱歉，我刚才走神了 😅 你能再说一遍吗？我保证认真听！"
            session["messages"].append({"role": "assistant", "content": fallback})
            yield f"data: {json.dumps({'type': 'chunk', 'content': fallback}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'suggest_assess': False, 'error': str(e)}, ensure_ascii=False)}\n\n"

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
    session = _sessions.get(req.conversation_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    user_config = _extract_user_llm_config(request)
    concept = session["concept"]
    messages = session["messages"]

    # 至少需要 2 轮用户消息才能评估
    user_turns = sum(1 for m in messages if m["role"] == "user")
    if user_turns < 2:
        return {
            "error": "请至少进行 2 轮对话后再评估",
            "current_turns": user_turns,
        }

    result = await evaluator.evaluate(concept=concept, messages=messages, user_config=user_config)

    # 更新会话状态
    if result.get("mastered"):
        session["status"] = "completed"

    return {
        "concept_id": session["concept_id"],
        "concept_name": concept["name"],
        "turns": user_turns,
        **result,
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """获取会话详情"""
    session = _sessions.get(conversation_id)
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
    """列出所有会话（MVP 阶段）"""
    return [
        {
            "id": s["id"],
            "concept_id": s["concept_id"],
            "concept_name": s["concept"]["name"],
            "status": s["status"],
            "turns": sum(1 for m in s["messages"] if m["role"] == "user"),
            "last_message": s["messages"][-1]["content"][:100] if s["messages"] else "",
        }
        for s in _sessions.values()
    ]
