---
id: "agent-benchmarks"
concept: "Agent评测基准"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 6
is_milestone: false
tags: ["Agent", "评测"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "B"
quality_score: 54.0
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# Agent评测基准

## 核心概念

Agent评测基准（Benchmarks）是用于系统性评估AI Agent能力的标准化测试集。不同于传统NLP基准（如MMLU、HumanEval）只测单一能力，Agent基准需要评估规划、工具使用、多步推理等综合能力。

## 主要基准

### WebArena / VisualWebArena
- **任务**: 在真实网站上完成操作（搜索、购物、填表）
- **评估**: 任务完成率、步骤效率
- **特点**: 真实浏览器环境，接近人类使用场景

### SWE-bench
- **任务**: 修复真实GitHub仓库的issue
- **评估**: 通过率（patch是否能通过对应测试）
- **特点**: 代码理解+修改的端到端评估

### GAIA
- **任务**: 需要多步推理+工具使用的问答
- **评估**: 答案准确率（Level 1-3难度递增）
- **特点**: 需要搜索、计算、文件处理等多种能力

### AgentBench
- **任务**: 8个环境（OS、数据库、知识图谱、网页等）
- **评估**: 各环境独立得分+综合评分
- **特点**: 多环境广覆盖

### ToolBench / API-Bank
- **任务**: 调用API完成复杂任务
- **评估**: API调用正确率、任务完成率
- **特点**: 工具使用能力专项评估

## 评测维度

Agent基准通常评估以下维度：
1. **规划能力**: 分解复杂任务的能力
2. **工具使用**: 正确调用工具的能力
3. **错误恢复**: 遇到失败时的处理能力
4. **效率**: 完成任务的步骤数/token消耗
5. **安全性**: 是否遵守安全约束

## 评测挑战

- **可复现性**: 外部环境变化导致结果不稳定
- **代表性**: 基准任务与真实场景的差距
- **评分标准**: 部分任务难以自动化评分
- **数据泄露**: 基准数据可能被训练数据覆盖

## 与Agent Evaluation的关系

Agent评测基准是Agent评估（Agent Evaluation）的具体工具和标准。评估关注方法论和指标设计，基准提供可执行的测试集。
