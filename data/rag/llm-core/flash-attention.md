---
id: "flash-attention"
concept: "FlashAttention"
domain: "ai-engineering"
subdomain: "llm-core"
subdomain_name: "大模型核心"
difficulty: 8
is_milestone: false
tags: ["LLM"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 64.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.581
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# FlashAttention

## 概述

FlashAttention 是由 Tri Dao 等人于 2022 年在论文《FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness》中提出的一种**精确注意力**计算算法。与近似注意力方法不同，FlashAttention 在数学上与标准 Softmax 注意力完全等价，不引入任何精度损失，但通过重新安排计算顺序，将注意力计算的显存复杂度从 O(N²) 降低至 O(N)，其中 N 为序列长度。

标准注意力实现需要将完整的 N×N 注意力矩阵 S = QKᵀ 写入 GPU HBM（高带宽显存），这在 N = 4096 时已消耗约 1GB 显存（FP16 格式）。FlashAttention 的核心洞察是：GPU 的计算瓶颈不在于浮点运算数（FLOPS），而在于 HBM 与 SRAM 之间的数据传输次数（IO 次数）。A100 GPU 的 HBM 带宽约为 2TB/s，而 SRAM 带宽超过 19TB/s，两者相差近 10 倍，这正是 IO-aware 设计能带来 2~4× 实际加速的根本原因。

FlashAttention 已被 PyTorch 2.0 原生集成（`torch.nn.functional.scaled_dot_product_attention`），并成为 GPT-4、LLaMA 2、Mistral 等主流大模型训练和推理的标配组件。FlashAttention-2（2023）进一步将 GPU 利用率从 30% 提升至约 73%，FlashAttention-3（2024）则针对 Hopper 架构（H100）的异步流水线和 FP8 进行了专项优化。

---

## 核心原理

### 1. 分块计算（Tiling）与在线 Softmax

标准注意力必须先完整计算 S = QKᵀ ∈ ℝᴺˣᴺ，再对每行做 Softmax，最后乘以 V。FlashAttention 通过**分块（Tiling）**打破这一依赖链：将 Q、K、V 分成大小为 B 的块（Block size），每次只将一个 Q 块和 K/V 块载入 SRAM，在 SRAM 内部完成局部运算后只将结果写回 HBM。

然而 Softmax 是全局操作：`softmax(x_i) = exp(x_i) / Σ exp(x_j)`，分块后无法直接计算全局归一化。FlashAttention 采用了 **在线 Softmax（Online Softmax）**技巧，维护两个标量统计量：
- `m_i`：当前已处理的所有元素中的最大值（用于数值稳定）
- `ℓ_i`：对应的归一化因子（指数和）

当处理新的块 j 时，更新规则为：

```
m_new = max(m_old, m_j)
ℓ_new = exp(m_old - m_new) * ℓ_old + exp(m_j - m_new) * ℓ_j
O_new = diag(exp(m_old - m_new)) * O_old + exp(S_j - m_new) * V_j
```

通过这组递推公式，FlashAttention 可以在**不存储完整 N×N 矩阵**的前提下，逐块地流式计算出与标准 Softmax 数学上等价的最终输出 O。

### 2. IO 复杂度分析

设 GPU SRAM 大小为 M，块大小 B = Θ(M/d)（d 为 head dimension，通常为 64 或 128）。

- **标准注意力 HBM 访问次数**：O(Nd + N²)，主要来自写入和读取 N×N 的矩阵 S 和 P。
- **FlashAttention HBM 访问次数**：O(N²d²/M)，当 M ≫ d 时，这比标准实现减少了一个量级。

例如在 N=2048、d=64、HBM=40GB 的 A100 上，标准注意力的 HBM 读写约为 30GB，而 FlashAttention 仅需约 4GB，IO 减少约 7.5 倍，与实测加速比高度吻合。

### 3. 反向传播的重计算（Recomputation）

训练时需要保存前向激活值用于反向传播梯度计算。标准实现需要在显存中保存完整的 N×N 注意力矩阵 P，显存占用为 O(N²)。FlashAttention **不保存 P 矩阵**，而是仅存储每行的 `(m_i, ℓ_i)` 两个标量（共 O(N) 额外存储），在反向传播时**重新计算**局部注意力分数。这种以算力换显存的策略，使得反向传播的显存开销同样维持在 O(N) 级别。实测在序列长度 N=8192 时，FlashAttention 的显存占用仅为标准实现的约 1/5。

### 4. 多头并行与 Causal Masking 的特殊处理

FlashAttention 在块级别原生支持因果掩码（Causal Mask）：对于 Q 块 i 和 K/V 块 j，若 j > i（即未来 token），直接跳过整个块的计算，而非逐元素置为 `-inf`。这使得自回归语言模型的训练效率几乎提升一倍（因为约一半的块计算被跳过）。多头注意力的不同 head 之间完全独立，可在 CUDA kernel 的不同 block 上并行执行，进一步提升 GPU 利用率。

---

## 实际应用

**长序列训练加速**：在使用标准注意力时，Transformer 训练序列长度超过 2048 就会出现显存 OOM（Out of Memory）。使用 FlashAttention 后，LLaMA 2 的训练上下文窗口可达 4096，而 Mistral 7B 通过 FlashAttention + 滑动窗口注意力将有效上下文扩展至 32K。在 A100-80GB 上，FlashAttention-2 在序列长度 8K 下的训练吞吐量比 PyTorch 原生实现高出约 3.1 倍。

**推理延迟优化**：在自回归生成的 decode 阶段，每步只生成一个 token，KV Cache 长度随步骤增长。FlashAttention 在此场景下减少了每步对 KV Cache 的 HBM 读取开销，在长序列推理（N > 2048）时首 token 延迟（TTFT, Time To First Token）可降低 40%~60%。

**与 vLLM 的协同**：vLLM 在 PagedAttention 的 kernel 实现中直接采用了 FlashAttention 的分块 Softmax 思路，对非连续 KV Cache 页进行高效聚合，使得两种技术在显存管理层面相互补充而非冲突。

---

## 常见误区

**误区一：FlashAttention 降低了注意力的计算精度**
FlashAttention 是**精确算法**，其数学输出与标准 `softmax(QKᵀ/√d)V` 完全等价（在浮点舍入误差范围内）。误解来源于将其与 Longformer、Performer 等**近似注意力**方法混淆。近似方法通过稀疏化或随机特征映射来减少计算量，而 FlashAttention 仅优化数据的访问模式，不改变计算结果。

**误区二：FlashAttention 主要减少了 FLOPS（浮点运算次数）**
FlashAttention 的总 FLOPS 数与标准实现基本相同，均为 O(N²d)。它优化的是 **HBM IO 次数**而非 FLOPS。标准注意力在 A100 上实际只使用了约 1~3% 的理论 FLOPS，瓶颈完全在 HBM 带宽，这是 FlashAttention 能大幅加速的根本原因。如果在一个 HBM 带宽极大的假想硬件上，FlashAttention 的优势会明显缩小。

**误区三：FlashAttention 对所有序列长度均有显著加速**
在序列长度较短（N ≤ 512）时，标准注意力的 N×N 矩阵较小，完全可以放入 L2 缓存，此时 IO 瓶颈不突出，FlashAttention 相比 cuBLAS 的标准实现加速比不足 1.2×。FlashAttention 的加速优势随 N 增大而显著提升，在 N ≥ 2048 时加速效果才真正凸显。

---

## 知识关联

**前置概念连接**：理解 FlashAttention 需要牢固掌握标准多头注意力的计算流程，尤其是 Softmax 归一化步骤——正是 Softmax 的全局依赖性使得朴素分块不可行，也正是在线 Softmax 技巧突破了这一限制。同时需要了解 GPU 内存层次结构：HBM（数十 GB，高延迟）→ L2 缓存（数十 MB）→ SRAM/Shared Memory（数百 KB，低延迟），FlashAttention 的所有优化都是针对这一层次结构设计的。

**后续概念延伸**：FlashAttention 直接使能了 LLM Serving 系统的优化空间——vLLM 的 PagedAttention 在非连续内存页上实现分块注意力时，复用了 FlashAttention 的 tiling 算法框架。在稀疏注意力方向，FlashAttention-2