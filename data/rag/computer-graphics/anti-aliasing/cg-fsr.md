---
id: "cg-fsr"
concept: "FSR"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# FSR（AMD FidelityFX Super Resolution）

## 概述

FSR（FidelityFX Super Resolution）是 AMD 于 2021 年 6 月发布的开源空间升采样技术，通过将低分辨率渲染帧放大到目标输出分辨率，在保持较高画质的同时显著提升帧率。与英伟达的 DLSS 不同，FSR 1.0 不依赖机器学习或专用硬件，可在任意支持 DirectX 11/12 或 Vulkan 的 GPU 上运行，包括 AMD、英伟达和 Intel 的显卡。

FSR 从第一代到第三代经历了根本性的技术演进。FSR 1.0 是纯空间算法，仅利用单帧信息；FSR 2.0（2022 年 5 月）引入了基于时间累积的技术方案，利用运动向量和深度缓冲区跨帧融合信息，画质大幅提升；FSR 3.0（2023 年）进一步加入了帧生成（Frame Generation）功能，能在两帧渲染帧之间插入人工合成帧，进一步提升流畅度。

理解 FSR 对于现代实时渲染优化至关重要，因为它代表了一种将渲染分辨率降低 40%–75%、同时将帧率提升 1.5–3 倍的工程实践路径。

---

## 核心原理

### FSR 1.0：EASU + RCAS 空间升采样

FSR 1.0 由两个连续 Pass 构成：**EASU**（Edge Adaptive Spatial Upsampling，边缘自适应空间升采样）和 **RCAS**（Robust Contrast Adaptive Sharpening，鲁棒对比度自适应锐化）。

EASU 的核心是利用 Lanczos 类核函数对输入图像做加权采样，同时检测边缘方向，对核函数进行各向异性拉伸，使升采样沿边缘方向而非穿越边缘方向进行插值，从而减少锯齿与模糊。EASU 对每个输出像素采样输入图像中 **12 个相邻像素**，并根据局部梯度动态调整采样权重。

RCAS 在 EASU 输出的放大图像上执行锐化，采用对比度自适应策略，仅对中频细节进行增强而抑制噪声放大，避免因过度锐化产生光晕（halo）瑕疵。

FSR 1.0 定义了四个质量档位：
- **Ultra Quality**：输入分辨率为输出的 77%（约 1.7× 放大）
- **Quality**：输入 67%（约 1.5× 放大）
- **Balanced**：输入 59%（约 1.7× 放大）
- **Performance**：输入 50%（2× 放大）

### FSR 2.0：时间累积与运动向量

FSR 2.0 在概念上与 TAA 类似，但针对升采样任务做了专门优化。其核心流程包含以下步骤：

1. **Depth Clip**：利用深度值检测像素的遮挡变化，丢弃已被遮挡的历史样本。
2. **Create Locks**：对静止区域（运动向量接近零）的像素建立"锁定"，允许更长时间的历史样本累积，实现超采样精度提升。
3. **Reconstruct & Dilate**：通过深度缓冲最小化（depth dilation）将运动向量从几何边缘向外膨胀，确保前景物体边缘使用正确的运动向量而非背景运动向量。
4. **Lanczos Resampling + Temporal Accumulation**：将当前帧低分辨率像素用 Lanczos 核重采样至高分辨率格，与经运动向量对齐的历史高分辨率帧加权混合，混合因子 α 通常在 0.1–0.2 之间（新帧权重），使历史帧对当前输出的贡献约为 80%–90%。

FSR 2.0 使用的 Lanczos 核半径为 2，即在 4×4 邻域内进行插值计算。时间 Jitter 模式采用 **Halton 序列**（基 2 和基 3），通常使用 8 帧或 16 帧的 Jitter 周期，以实现亚像素覆盖均匀分布。

### FSR 3.0：帧生成

FSR 3.0 的帧生成模块基于光流估计（Optical Flow），分析相邻两帧渲染帧之间的运动场，通过对两帧之间的中间时刻进行插值合成一帧新的图像。帧生成要求显卡支持 DirectX 12 并使用 `VK_EXT_frame_boundary` 或 DirectX 12 的 Swap Chain 插帧接口。帧生成不依赖 AI 硬件，但为了避免 UI 元素抖动，需要游戏提供单独的 UI 渲染层（UI Composition）。

---

## 实际应用

**游戏集成示例**：《赛博朋克 2077》于 FSR 2.0 发布初期即集成该技术，在 4K 输出时以 Quality 模式（67% 输入分辨率，即约 2560×1440 输入）运行，相比原生 4K 帧率提升约 40%–50%，PSNR 损失约 1–2 dB。

**对比 TAA 的实际差异**：FSR 2.0 相比原生 TAA 在快速运动场景中的"鬼影"（ghosting）问题更少，原因是其 Depth Clip 和 Create Locks 步骤能更积极地识别和丢弃失效的历史样本。而标准 TAA 通常只使用速度向量重投影，缺乏深度一致性验证。

**开源优势**：FSR 的 HLSL/GLSL 源码在 [GPUOpen](https://gpuopen.com/fidelityfx-superresolution/) 以 MIT 许可证开放，开发者可直接将 `ffx_fsr2.h` 等头文件嵌入自有引擎，接入成本远低于 DLSS 的 SDK 模式。

---

## 常见误区

**误区一：FSR 1.0 和 FSR 2.0 是同类算法的迭代优化**
两者在算法本质上截然不同。FSR 1.0 是纯空间单帧算法，输入只有当前帧低分辨率图像；FSR 2.0 是时间算法，必须输入**运动向量**和**深度缓冲区**，若游戏不提供这两项数据，则无法接入 FSR 2.0，只能使用 FSR 1.0。很多玩家和开发者混淆了两者的接入要求，导致误判集成难度。

**误区二：FSR 不需要 Jitter 也能正常工作**
FSR 2.0 的时间累积效果强依赖相机的 Jitter（亚像素偏移），通常通过修改投影矩阵的 XY 偏移实现。若游戏未正确启用 Jitter，FSR 2.0 无法收集足够的亚像素样本，输出分辨率的细节恢复能力将退化至类似 FSR 1.0 的水准，边缘细节损失明显。

**误区三：FSR 的帧生成等同于真实帧率提升**
FSR 3.0 帧生成插入的合成帧虽然显示到屏幕上，但其**输入延迟（input latency）并不减少**，反而会增加约 0.5 帧的延迟，因为合成帧是基于已渲染完成的两帧数据生成的，不包含最新输入信息。AMD 建议配合 Anti-Lag+ 技术同时使用以补偿延迟增加。

---

## 知识关联

**前置概念 TAA**：FSR 2.0 的时间累积模块借鉴了 TAA 的历史帧融合思路，但将其扩展到跨分辨率场景。掌握 TAA 的运动向量重投影、历史样本混合权重计算是理解 FSR 2.0 为何需要 Depth Clip 和 Dilate 步骤的前提——这些步骤正是为了解决 TAA 在升采样场景下边缘重投影误差被放大的问题。

**后续概念 超分辨率技术**：FSR 是图形学超分辨率领域由纯空间方法向时间方法演进的代表性案例，学习完 FSR 后，可进一步比较基于深度学习的超分辨率方案（如 DLSS 3 使用的 Transformer 网络、以及 Intel XeSS 使用的 XMX 矩阵引擎加速推理），理解神经网络方案在处理高频细节和复杂运动场景时相比 FSR 的权衡取舍。