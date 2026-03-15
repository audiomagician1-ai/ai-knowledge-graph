"""
理解度评估器
多维度评估: 完整性 + 准确性 + 深度 + 举例能力
通过 LLM 分析对话历史给出结构化评分
"""

import json
import logging
from typing import Optional

from llm.router import llm_router
from engines.dialogue.prompts.feynman_system import ASSESSMENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class UnderstandingEvaluator:
    """理解度评估引擎 — 分析费曼对话后给出结构化评分"""

    async def evaluate(
        self,
        concept: dict,
        messages: list[dict],
        user_config: dict | None = None,
    ) -> dict:
        """评估用户在对话中展示的理解程度

        Args:
            concept: 概念信息 (name, difficulty 等)
            messages: 对话历史 [{"role": "user/assistant", "content": "..."}]
            user_config: 用户自定义 LLM 配置

        Returns:
            评估结果 dict: completeness, accuracy, depth, examples, overall_score, gaps, feedback, mastered
        """
        system_prompt = ASSESSMENT_SYSTEM_PROMPT.format(
            concept_name=concept["name"],
            difficulty=concept.get("difficulty", 5),
        )

        # 构建对话摘要供评估
        dialogue_text = self._format_dialogue(messages)

        eval_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"以下是用户在费曼对话中的完整对话记录，请评估用户对「{concept['name']}」的理解程度：\n\n{dialogue_text}"},
        ]

        try:
            response = await llm_router.chat(
                messages=eval_messages,
                tier="assessment",
                temperature=0.2,  # 评估用低温度保证稳定性
                max_tokens=1024,
                user_config=user_config,
            )

            # 提取 JSON
            result = self._parse_json(response)
            if result:
                # 校验必填字段
                return self._validate_result(result)
        except Exception as e:
            logger.warning("Assessment LLM call failed: %s", e)

        # Fallback: 基于消息长度和轮数粗略评估
        return self._fallback_evaluate(messages)

    def _format_dialogue(self, messages: list[dict]) -> str:
        """格式化对话记录"""
        lines = []
        for msg in messages:
            role = "用户（学习者）" if msg["role"] == "user" else "AI（学习伙伴/老师）"
            lines.append(f"[{role}]: {msg['content']}")
        return "\n\n".join(lines)

    def _parse_json(self, text: str) -> Optional[dict]:
        """从 LLM 响应中提取 JSON"""
        # 尝试直接 parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 尝试从 ```json ... ``` 中提取
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.find("```", start)
            if end == -1:
                end = len(text)  # no closing ```, take rest
            try:
                return json.loads(text[start:end].strip())
            except (json.JSONDecodeError, ValueError):
                pass

        # 尝试从 { ... } 中提取
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

        return None

    def _validate_result(self, result: dict) -> dict:
        """校验评估结果并补充缺失字段"""
        defaults = {
            "completeness": 50,
            "accuracy": 50,
            "depth": 50,
            "examples": 50,
            "overall_score": 50,
            "gaps": [],
            "feedback": "评估完成",
            "mastered": False,
        }

        for key, default in defaults.items():
            if key not in result:
                result[key] = default

        # 确保分数在 0-100
        for key in ["completeness", "accuracy", "depth", "examples", "overall_score"]:
            try:
                result[key] = max(0, min(100, int(float(result[key]))))
            except (ValueError, TypeError):
                result[key] = defaults[key]

        # 重新计算 mastered
        result["mastered"] = (
            result["overall_score"] >= 75
            and all(result[k] >= 60 for k in ["completeness", "accuracy", "depth", "examples"])
        )

        return result

    def _fallback_evaluate(self, messages: list[dict]) -> dict:
        """无 LLM 时的粗略评估"""
        user_msgs = [m for m in messages if m["role"] == "user"]
        total_words = sum(len(m["content"]) for m in user_msgs)
        num_turns = len(user_msgs)

        # 简单启发式
        base = min(40 + num_turns * 8 + total_words // 50, 85)
        result = {
            "completeness": base,
            "accuracy": base - 5,
            "depth": base - 10,
            "examples": base - 15,
            "overall_score": base - 5,
            "gaps": ["评估服务暂时不可用，此为粗略估计"],
            "feedback": f"你进行了 {num_turns} 轮对话，表现不错！建议继续深入探讨。",
        }
        # Use same mastered logic as _validate_result: overall >= 75 AND all dims >= 60
        result["mastered"] = (
            result["overall_score"] >= 75
            and all(result[k] >= 60 for k in ["completeness", "accuracy", "depth", "examples"])
        )
        return result


# 全局单例
evaluator = UnderstandingEvaluator()
