---
id: "agent-reflection"
concept: "Agent反思机制"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 7
is_milestone: false
tags: ["Agent", "推理"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 60.1
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# Agent反思机制

## 核心概念

Agent反思（Reflection）是让AI Agent在执行任务后对自身行为进行自我审视和改进的机制。反思使Agent能够从错误中学习、优化决策策略、提高任务完成质量。

## 反思的类型

### 1. 行动反思（Action Reflection）
Agent执行一个动作后，评估该动作的效果：
- 结果是否符合预期？
- 是否有更好的替代方案？
- 出现了什么意外情况？

### 2. 推理反思（Reasoning Reflection）
对推理过程本身进行审视：
- 推理链是否有逻辑漏洞？
- 前提假设是否正确？
- 是否遗漏了重要信息？

### 3. 策略反思（Strategy Reflection）
对整体策略进行回顾：
- 当前策略是否最优？
- 是否需要调整方向？
- 资源分配是否合理？

## 实现模式

### Reflexion 框架
```
[初始尝试] → [执行] → [评估结果] → [生成反思] → [改进后重试]
```

反思生成的关键prompt要素：
1. **任务描述**: 原始目标是什么
2. **执行轨迹**: Agent做了什么
3. **结果评估**: 成功/失败及原因
4. **改进建议**: 下次应该怎么做

### Self-Refine 模式
Agent对自己的输出进行迭代改进：
1. 生成初始输出
2. 自我评价输出质量
3. 根据评价改进输出
4. 重复直到满意或达到上限

## 反思的质量评估

好的反思应该具备：
- **具体性**: 指出具体问题而非泛泛而谈
- **可操作性**: 给出明确的改进方向
- **因果分析**: 解释为什么出错
- **积累性**: 能在多次反思中逐步改进

## 与Agent Loop的关系

反思机制是Agent Loop中的关键环节。在标准的Observe-Think-Act循环中，反思发生在Act之后、下一轮Observe之前，形成闭环学习。

## 常见误区

- 反思不等于简单重试（需要分析原因）
- 反思深度需要控制（过度反思浪费token和时间）
- 反思需要外部信号辅助（纯自我评估可能陷入盲区）
