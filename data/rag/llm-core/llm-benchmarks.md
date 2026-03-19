---
id: "llm-benchmarks"
name: "LLM Benchmarks (MMLU/HumanEval)"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 6
tags: ["LLM", "Evaluation", "Benchmarks"]
generated_at: "2026-03-19T18:00:00"
---

# LLM Benchmarks (MMLU/HumanEval)

## 概述

LLM Benchmarks 是用于系统性评估大语言模型能力的标准化测试集合，难度等级 6/9。它们覆盖知识理解、推理、编码、数学等维度，是模型选型和研究对比的核心依据。但基准测试也有显著局限性——数据污染、任务饱和、与实际应用脱节等问题日益突出。

本概念与 LLM 预训练、LLM 评估密切相关，理解基准的方法论和局限性对工程决策至关重要。

## 核心基准测试

### 知识与理解类

| 基准 | 全称 | 任务 | 样本量 | 说明 |
|:---|:---|:---|:---:|:---|
| **MMLU** | Massive Multitask Language Understanding | 57 学科多选题 | 15,908 | 覆盖 STEM/人文/社科/专业，4 选 1 |
| **MMLU-Pro** | MMLU Professional | 10 选 1 + 更难 | 12,032 | 减少猜测概率，加入推理链 |
| **ARC** | AI2 Reasoning Challenge | 小学科学题 | 7,787 | Easy/Challenge 两个子集 |
| **HellaSwag** | — | 常识推理补全 | 10,042 | 选择最合理的故事续写 |
| **TruthfulQA** | — | 事实性判断 | 817 | 测试模型是否会输出常见误解 |

### 编程能力类

```
HumanEval (OpenAI):
  - 164 道 Python 编程题
  - 给定函数签名 + docstring，生成函数体
  - 评估指标: pass@k (k 次生成中至少 1 次通过所有测试)

  示例:
  def has_close_elements(numbers: List[float], threshold: float) -> bool:
      """Check if in given list of numbers, are any two numbers
      closer to each other than given threshold.
      >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
      False
      """
      # 模型需要生成此处的实现

MBPP (Mostly Basic Python Problems):
  - 974 道入门级编程题
  - 包含 3 个测试用例作为验证

SWE-bench:
  - 真实 GitHub Issue 修复任务
  - 模型需要理解 repo + 定位 bug + 生成 patch
  - 更贴近实际开发能力
```

### 数学推理类

| 基准 | 难度 | 特点 |
|:---|:---|:---|
| **GSM8K** | 小学数学 | 8,500 道多步推理应用题 |
| **MATH** | 竞赛数学 | 12,500 道高中/竞赛题，LaTeX 格式 |
| **MathVista** | 多模态数学 | 需要理解图表/几何图形 |

### 综合排行榜

```
Open LLM Leaderboard (Hugging Face):
  - 公开评测，社区维护
  - 使用 6 个基准: MMLU / ARC / HellaSwag / TruthfulQA / Winogrande / GSM8K

Chatbot Arena (LMSYS):
  - 人类盲评对比 (Elo rating)
  - 用户同时与两个匿名模型对话，选择更好的
  - 被认为最接近"真实能力"的排名

MTEB (Massive Text Embedding Benchmark):
  - 专门评估 Embedding 模型
  - 56 个数据集，7 个任务类别
```

## 评估方法论

### pass@k 计算

```python
# HumanEval 的核心指标
# 生成 n 个样本，计算 k 个中至少 1 个通过的概率
import math

def pass_at_k(n: int, c: int, k: int) -> float:
    """
    n: 总生成数
    c: 通过测试的数量
    k: 允许的尝试次数
    """
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)

# 例: 生成 200 个样本，其中 50 个通过
# pass@1 ≈ 25%, pass@10 ≈ 73%, pass@100 ≈ 99.9%
```

### Few-shot vs Zero-shot

```
Zero-shot: 直接给题目，不提供示例
  "What is the capital of France?"

5-shot: 先给 5 个 (问题, 答案) 示例，再给测试题
  "Q: What is 2+2? A: 4
   Q: What color is grass? A: Green
   ...
   Q: What is the capital of France?"

MMLU 标准: 5-shot
GSM8K 标准: 8-shot (含 CoT 推理过程)
```

## 局限性

### 数据污染 (Data Contamination)

```
问题: 训练数据包含测试集 → 分数虚高
  - MMLU 的题目大量出自网络公开资源
  - 模型可能"记住"了答案而非真正理解
  
检测方法:
  - n-gram 重叠检测
  - 扰动测试 (改变选项顺序/措辞后分数变化)
  - 时间截止 (只用基准发布后的题目)
```

### 基准饱和

随着模型进步，老基准分数趋近满分，失去区分度：

| 基准 | GPT-3 (2020) | GPT-4 (2023) | GPT-4o (2024) | 现状 |
|:---|:---:|:---:|:---:|:---|
| HellaSwag | 78% | 95% | 96% | 已饱和 |
| ARC-Easy | 68% | 96% | 97% | 已饱和 |
| MMLU | 43% | 86% | 88% | 接近饱和 |
| MATH | 5% | 42% | 76% | 仍有空间 |

## 常见误区

1. **唯分数论**: MMLU 90% 不代表模型"懂" 90% 的知识，多选题有 25% 基线
2. **忽略评估设置差异**: few-shot 数量、prompt 格式、解码策略都影响分数
3. **将基准等同于实际能力**: 高 HumanEval 分数不代表能胜任复杂工程任务
4. **忽略模型大小/成本**: 同分数下，更小更快的模型可能是更好的选择

## 与相邻概念关联

- **前置**: LLM 预训练、LLM 评估 — 理解模型训练和评估基础
- **关联**: LLM Safety and Alignment — 安全性也有专门的基准（ToxiGen, BBQ）
- **应用**: 模型选型 — 基准分数是选择模型的重要参考
- **进阶**: LLM Evaluation (自定义评估) — 针对特定场景设计评估标准
