---
id: "prompt-chaining"
concept: "提示链"
domain: "ai-engineering"
subdomain: "prompt-engineering"
subdomain_name: "Prompt工程"
difficulty: 6
is_milestone: false
tags: ["Prompt"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 67.4
generation_method: "ai-batch-v1"
unique_content_ratio: 0.966
last_scored: "2026-03-21"
sources: []
---
# 提示链

## 核心概念

提示链（Prompt Chaining）是将复杂任务分解为多个子任务，每个子任务使用一个独立的prompt，前一个prompt的输出作为下一个prompt的输入，形成链式调用的技术。

## 与CoT的区别

| 特征 | Chain-of-Thought | Prompt Chaining |
|------|-----------------|-----------------|
| 调用次数 | 单次LLM调用 | 多次LLM调用 |
| 分解方式 | LLM自行分步 | 人工预定义步骤 |
| 中间检查 | 无法干预 | 可在每步检查/修正 |
| 适用场景 | 推理问题 | 复杂工作流 |

## 链式模式

### 1. 顺序链（Sequential Chain）
```
[Prompt A] → outputA → [Prompt B(输入=outputA)] → outputB → [Prompt C(输入=outputB)] → 最终结果
```

示例：文档分析流水线
1. Prompt 1: 从文档提取关键信息
2. Prompt 2: 对关键信息进行分类
3. Prompt 3: 基于分类结果生成摘要

### 2. 分支链（Branching Chain）
```
[Prompt A] → 条件判断 → 路径1: [Prompt B1] → ...
                       → 路径2: [Prompt B2] → ...
```

### 3. 聚合链（Aggregation Chain）
```
[Prompt A1] →┐
[Prompt A2] →├→ [聚合Prompt B] → 最终结果
[Prompt A3] →┘
```

### 4. 迭代链（Iterative Chain）
```
[Prompt A] → output → [评估Prompt] → 不满意? → [改进Prompt(输入=output)] → 新output → ...
```

## 设计原则

1. **单一职责**: 每个prompt只负责一个明确的子任务
2. **明确接口**: 定义清晰的输入/输出格式
3. **可验证**: 每步输出可以独立验证
4. **降级处理**: 某步失败时有备选方案
5. **最小化依赖**: 减少步骤间的耦合

## 实际应用

- **代码生成**: 需求分析→架构设计→代码编写→代码审查
- **内容创作**: 大纲生成→段落展开→风格调整→最终校对
- **数据处理**: 数据清洗→特征提取→分析→可视化描述

## 与Chain-of-Thought的关系

CoT让LLM在单次调用中分步推理，Prompt Chaining将分步推理外显化为多次调用。Chaining提供了更多控制点，但延迟和成本更高。
