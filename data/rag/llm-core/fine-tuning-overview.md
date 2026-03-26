---
id: "fine-tuning-overview"
concept: "微调概述(SFT/RLHF)"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 7
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.429
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 微调概述（SFT/RLHF）

## 概述

大型语言模型的微调（Fine-tuning）是指在已经完成预训练的模型基础上，使用特定任务数据对模型参数进行进一步调整的技术过程。与从零开始训练不同，微调利用预训练阶段积累的海量语言知识，仅需相对少量的标注数据即可将通用模型转化为特定场景的专用助手。GPT-3 拥有 1750 亿参数，但其原始预训练版本无法可靠地遵循指令；InstructGPT（2022年）通过对其实施 SFT + RLHF 两阶段微调，在人类偏好评估中以低 100 倍的参数量击败了更大规模的纯预训练模型，这一结果直接推动了 ChatGPT 和现代对话 AI 的诞生。

微调技术之所以在工程实践中不可或缺，根本原因在于预训练目标（下一个词预测）与实际使用目标（有帮助、无害、诚实地回答问题）之间存在本质错位。预训练模型会忠实复制互联网文本中的偏见、有害内容和指令不遵从行为。SFT（Supervised Fine-Tuning，监督微调）和 RLHF（Reinforcement Learning from Human Feedback，人类反馈强化学习）是填补这一鸿沟的两种主流手段，通常按顺序组合使用，前者奠定指令遵循基础，后者进行价值观对齐优化。

## 核心原理

### SFT：监督微调的机制

SFT 使用"指令-回复"对格式的有监督数据集，对预训练模型进行标准的交叉熵损失训练。数据格式通常为 `(system prompt, user instruction, ideal response)` 三元组。损失函数仅计算在 `response` 部分的 token 上：

$$\mathcal{L}_{SFT} = -\sum_{t=1}^{T} \log P_\theta(y_t \mid x, y_{<t})$$

其中 $x$ 为输入指令，$y_t$ 为第 $t$ 个目标 token，$\theta$ 为模型参数。OpenAI 在 InstructGPT 论文中使用了约 13,000 条人工标注的高质量 SFT 样本，证明了数据质量远比数量更关键——1,000 条精心标注的数据往往优于 100,000 条自动生成的低质数据。

SFT 阶段通常使用较低的学习率（1e-5 至 5e-5 量级）并配合余弦衰减调度，以避免灾难性遗忘（Catastrophic Forgetting）预训练阶段习得的世界知识。训练轮次一般控制在 1 至 3 个 epoch，过度训练会导致模型陷入格式化回复模式而降低多样性。

### RLHF：人类反馈强化学习的三阶段流程

RLHF 在 SFT 之后执行，包含三个串联阶段：

**第一阶段——奖励模型训练（Reward Model Training）：** 收集人类对同一指令下多个模型输出的排序偏好数据（如 A > B > C），训练一个独立的奖励模型 $R_\phi$，使其能预测人类偏好分数。损失函数为 Bradley-Terry 成对排序损失：

$$\mathcal{L}_{RM} = -\mathbb{E}_{(x,y_w,y_l)}\left[\log \sigma\left(R_\phi(x, y_w) - R_\phi(x, y_l)\right)\right]$$

其中 $y_w$ 为人类偏好的"获胜"回复，$y_l$ 为"失败"回复。

**第二阶段——PPO 强化学习优化：** 使用近端策略优化算法（PPO）以奖励模型的输出分数作为奖励信号，优化语言模型策略 $\pi_\theta$。为防止模型过度优化奖励模型导致"奖励作弊"（reward hacking），引入 KL 散度惩罚项约束策略与 SFT 模型的偏离程度：

$$\mathcal{J}_{RLHF} = \mathbb{E}\left[R_\phi(x,y) - \beta \cdot \text{KL}\left(\pi_\theta(\cdot|x) \| \pi_{SFT}(\cdot|x)\right)\right]$$

其中 $\beta$ 为 KL 惩罚系数，InstructGPT 论文中设置为 0.02 至 0.2 范围内。

**第三阶段——迭代优化：** 使用更新后的策略模型重新采样回复，再次进行人工排序标注，循环迭代。

### DPO：RLHF 的简化替代方案

2023 年提出的直接偏好优化（Direct Preference Optimization，DPO）绕过了显式奖励模型训练和 PPO 的复杂流程，直接从偏好数据优化策略，其损失函数为：

$$\mathcal{L}_{DPO} = -\mathbb{E}\left[\log \sigma\left(\beta \log \frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)} - \beta \log \frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}\right)\right]$$

DPO 在工程实践中更为稳定，显著降低了 GPU 内存需求和训练复杂度，被 Llama 3、Mistral 等开源模型广泛采用。

## 实际应用

**代码助手专项微调：** GitHub Copilot 的底层模型 Codex 基于 GPT-3 对 159GB 公开代码数据进行 SFT，将代码补全准确率从通用模型的约 14% 提升至 37%（HumanEval 基准）。此场景中 SFT 数据包含函数签名与完整实现的配对，无需 RLHF 即可达到生产要求。

**医疗对话对齐：** 在医疗问答场景中，SFT 阶段使用医生编写的标准问答对训练模型基础能力，RLHF 阶段招募执业医师对模型输出进行安全性排序，重点标注"过度自信的错误诊断"为低分输出。Med-PaLM 2（2023年）通过此流程在 USMLE 风格题目上达到专家级（86.5% 准确率）。

**中文指令遵循：** 阿里通义千问（Qwen）系列在 SFT 阶段使用超过 50 万条中英双语指令数据，RLHF 阶段专门针对中文语境下的礼貌性、准确性和价值观进行人工偏好标注，解决了西方 RLHF 数据集对中文习惯覆盖不足的问题。

## 常见误区

**误区一：SFT 数据越多越好。** 这一认知忽视了数据质量对微调效果的决定性影响。使用 LIMA（2023年）论文展示的极端案例：仅 1,000 条精选多样性数据进行 SFT，在开放式生成任务上的表现可接近使用 52,000 条数据的 Alpaca 模型。大量低质量 SFT 数据会导致模型输出格式僵化、创造力下降，并可能覆盖预训练阶段的真实世界知识。

**误区二：RLHF 中奖励模型越准越好。** 奖励模型本身的泛化误差会被 PPO 强化学习过程放大，导致策略模型找到在奖励模型上高分但实际质量低劣的"作弊"输出，此现象称为"Goodhart 定律"在 RLHF 中的体现。InstructGPT 实验中，过大的 PPO 优化步数会导致模型输出冗长却空洞的回复以刷高奖励分。KL 惩罚项的合理设置以及定期更新奖励模型是缓解这一问题的必要手段。

**误区三：完成 SFT 后可以跳过 RLHF。** SFT 仅能教会模型"怎么回答"（格式与风格），但无法保证模型在面对有害指令、模糊问题或道德边界情境时做出正确判断。RLHF 通过奖励信号显式训练模型拒绝有害请求的能力，这是 SFT 的监督信号覆盖不到的长尾行为空间。

## 知识关联

从**LLM预训练**到 SFT 的过渡是理解微调必要性的前提：预训练通过自回归目标习得语言统计规律，但产出的模型是"文本续写机器"而非"指令助手"，SFT 完成这一身份转换。**迁移学习**的理论框架解释了为何少量微调数据即可取得显著效果——预训练权重已编码了充分的语言表示，微调只需调整任务适应层。

在后续深化方向上，**LoRA 与参数高效微调**解决了全量微调对 GPU 显存需求过高的工程障碍，允许在消费级硬件上对 70B 级模型进行 SFT；**RLHF 人类反馈强化学习**对本文介绍的 PPO 训练流程进行更深入的算法分析，包括 GAE 优势估计和价值网络设计；**Model Distillation** 通常以经过 SFT+RLHF 对齐的教师模型为蒸馏目标，其输出质量直接