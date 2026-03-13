"""
LLM 分层调度路由器
根据场景选择最合适的模型，控制成本
"""

from config import settings


class LLMRouter:
    """LLM 分层调度

    分层策略:
    - 简单问答/解释: DeepSeek ($0.14/1M tokens) — 节省95%
    - 复杂推理/对话: GPT-4o-mini ($0.15/1M input) — 节省90%
    - 核心评估/图谱构建: GPT-4o ($2.50/1M input) — 仅在需要时

    预估: 1000 DAU 时月LLM成本约 $150-300
    """

    MODEL_TIERS = {
        "simple": settings.llm_model_simple,
        "dialogue": settings.llm_model_dialogue,
        "assessment": settings.llm_model_assessment,
    }

    # TODO: Phase 2 实现 — httpx 异步调用 + 流式响应 + 缓存
    pass
