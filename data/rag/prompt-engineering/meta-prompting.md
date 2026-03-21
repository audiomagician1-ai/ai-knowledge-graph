---
id: "meta-prompting"
concept: "元提示工程"
domain: "ai-engineering"
subdomain: "prompt-engineering"
subdomain_name: "Prompt工程"
difficulty: 7
is_milestone: false
tags: ["Prompt", "高级"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 66.7
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# 元提示工程

## 核心概念

元提示工程（Meta-Prompting）是使用LLM来生成、优化和改进提示词本身的技术。不是人类直接编写prompt，而是让AI帮助设计更好的prompt——"用prompt优化prompt"。

## 主要方法

### 1. APE（Automatic Prompt Engineering）
自动搜索最优prompt：
1. 让LLM根据任务描述生成多个候选prompt
2. 在验证集上评估各候选prompt的效果
3. 选择效果最好的prompt
4. 迭代优化

### 2. PromptBreeder
进化式prompt优化：
- 初始化一组prompt种群
- 通过变异和交叉生成新prompt
- 适应度评估筛选优秀prompt
- 多代进化逐步改进

### 3. DSPy（Declarative Self-improving Python）
声明式prompt优化框架：
- 定义任务的输入/输出签名
- 自动搜索最优的prompt模板和示例
- 支持多步推理管道的联合优化

### 4. 元提示模式（Meta-Prompt Pattern）
在prompt中嵌入自我改进指令：
```
你是一个prompt工程专家。请为以下任务设计最优的prompt：
任务描述: [...]
目标模型: [...]
评估标准: [...]

请输出:
1. 推荐的系统prompt
2. 用户prompt模板
3. 少样本示例
4. 预期效果和局限性
```

## 优化维度

元提示可以优化的方面：
- **指令措辞**: 更精确的任务描述
- **示例选择**: 最有效的few-shot examples
- **格式约束**: 输出格式和结构
- **推理引导**: 思考链和分步策略
- **参数调优**: temperature、top_p等生成参数

## 评估循环

```
[初始Prompt] → [测试] → [评估分数] → [LLM分析弱点] → [生成改进版] → [再测试] → ...
```

关键：需要明确的评估指标和测试集。

## 局限性

- 需要足够的评估数据
- 优化可能过拟合到测试集
- 元prompt本身的质量影响优化效果
- 计算成本高（多次LLM调用）

## 与Chain-of-Thought的关系

CoT是元提示优化时常用的目标技术之一。元提示工程可以帮助找到最佳的CoT引导方式——什么样的"让我们一步步思考"表述最有效。
