"""对话引擎 API — 费曼对话 + 苏格拉底追问 + 理解度评估"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    conversation_id: str
    concept_id: str
    user_message: str


class ConversationCreate(BaseModel):
    concept_id: str


class AssessmentRequest(BaseModel):
    conversation_id: str
    concept_id: str


@router.post("/conversations")
async def create_conversation(req: ConversationCreate):
    """创建新的对话会话"""
    # TODO: Phase 2 — 对话引擎初始化
    return {
        "conversation_id": "placeholder",
        "message": "对话引擎将在 Phase 2 实现",
    }


@router.post("/chat")
async def chat(req: ChatRequest):
    """发送对话消息（流式响应）"""
    # TODO: Phase 2 — LLM 编排 + 苏格拉底提问策略
    return {
        "message": "费曼对话引擎将在 Phase 2 实现",
        "is_complete": False,
    }


@router.post("/assess")
async def assess_understanding(req: AssessmentRequest):
    """请求理解度评估"""
    # TODO: Phase 2 — 多维度评估
    return {
        "overall_score": 0,
        "message": "理解度评估将在 Phase 2 实现",
    }
