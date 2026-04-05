---
id: "cg-dlss"
concept: "DLSS"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["AI"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# DLSS（深度学习超采样）

## 概述

DLSS（Deep Learning Super Sampling，深度学习超采样）是NVIDIA于2018年随RTX 20系列显卡推出的图像质量增强技术，利用专用的张量核心（Tensor Core）在GPU硬件层面加速神经网络推理，将低分辨率渲染帧升频至更高分辨率，同时执行抗锯齿处理。与传统超采样（如SSAA）需要在目标分辨率下直接渲染不同，DLSS允许游戏以1080p渲染后输出4K画质，理论上将帧率提升2倍至4倍。

DLSS经历了显著的技术迭代：DLSS 1.0（2018年）依赖针对特定游戏训练的卷积神经网络，部署灵活性极差；DLSS 2.0（2020年）引入了通用化模型，结合运动向量与深度缓冲区，不再需要逐游戏重新训练；DLSS 3.0（2022年，仅限RTX 40系列）新增帧生成（Frame Generation）模块，可在两个真实渲染帧之间插入AI生成帧，进一步提升显示帧率。DLSS 3.5（2023年）引入光线重建（Ray Reconstruction），专门改善光线追踪场景的降噪质量。

DLSS的实际意义在于它将"感知质量"与"渲染分辨率"解耦：开发者可以用更低的GPU负载获得视觉上接近甚至优于原生分辨率的图像，这对光线追踪场景尤为重要，因为光追本身已消耗大量GPU算力。

---

## 核心原理

### 神经网络架构与训练流程

DLSS 2.x及后续版本的核心是一个卷积神经网络，其训练数据由NVIDIA内部超级计算机生成：以目标游戏在**16K超高分辨率**下渲染"Ground Truth"参考帧，同时生成对应的低分辨率输入帧、运动向量与曝光数据。网络通过最小化生成图像与16K参考帧之间的感知损失函数（Perceptual Loss）来学习升频映射关系。最终部署的通用模型体积约为数MB，足以在游戏运行时实时推理。

### 时序信息整合机制

DLSS 2.0的关键创新在于对时序信息的利用，这与TAA的核心思路一致但实现更复杂。每一帧渲染时，渲染器使用**Halton序列抖动**（Halton Sequence Jitter）对摄像机投影矩阵施加亚像素偏移，使得连续多帧覆盖不同的采样位置。DLSS网络接收以下输入：

- **当前低分辨率RGB帧**（含抖动）
- **运动向量缓冲区**（Motion Vectors，屏幕空间2D位移）
- **深度缓冲区**（用于遮挡检测）
- **前一帧高分辨率输出**（经运动向量反向映射后对齐）
- **曝光/亮度元数据**

网络利用这些信息在单帧推理中等效地"看到"多帧数据，从而重建亚像素细节。相比TAA的简单指数加权平均（EMA），DLSS的注意力机制可以更智能地判断历史帧中哪些像素值可信、哪些已被遮挡或失效。

### DLSS 3帧生成原理

帧生成（Frame Generation）是DLSS 3独有的功能，依赖RTX 40系列的第四代光流加速器（Optical Flow Accelerator）。其流程为：

1. 游戏引擎正常渲染第N帧和第N+1帧
2. 光流加速器计算两帧之间逐像素的运动场（Optical Flow Field）
3. 专用AI网络以运动场、两帧图像及深度/UI信息为输入，**生成**一个全新的中间帧
4. 最终向显示器输出序列变为：真实帧N → AI帧 → 真实帧N+1

帧生成可将有效显示帧率提升约**1.5×至2×**，但AI生成帧不包含新的游戏逻辑输入，因此不降低游戏延迟（输入延迟由NVIDIA Reflex另行优化）。

### 质量模式与分辨率倍数

DLSS提供多种预设模式，对应不同的内部渲染分辨率比例：

| 模式 | 渲染分辨率（输出4K时） | 缩放倍数 |
|------|-----------------------|----------|
| 质量（Quality） | 2560×1440 | 1.5× |
| 平衡（Balanced） | 2259×1270 | ~1.7× |
| 性能（Performance） | 1920×1080 | 2.0× |
| 超性能（Ultra Performance） | 1280×720 | 3.0× |

---

## 实际应用

**《赛博朋克2077》**是DLSS应用的典型案例：开启光线追踪"超级光线追踪"模式后，原生4K帧率在RTX 4090上约为40fps，开启DLSS质量模式后可达100fps以上，且用户主观评价图像质量与原生相近甚至更优（因DLSS有效消除了TAA的模糊）。

在VR应用中，DLSS以"固定注视点渲染"（Fixed Foveated Rendering）结合使用：眼动追踪确定注视点后，周边区域以低至50%分辨率渲染，DLSS负责升频，最终在保证中心清晰度的同时大幅降低GPU负担。

游戏引擎集成层面，NVIDIA提供统一的**NGX SDK**（NVIDIA Graphics Extension），Unreal Engine 5自4.26版本起内置DLSS插件，开发者只需在Unreal的后期处理管线中启用节点即可接入，无需手动管理运动向量或缓冲区传递。

---

## 常见误区

**误区一：DLSS只是放大算法**
许多人将DLSS与双线性插值或ESRGAN等单帧超分辨率方法混淆。DLSS的质量优势大部分来源于**时序信息整合**：单帧情况下DLSS的输出与双线性放大差距有限，但利用历史帧后，它能重建在当前帧渲染分辨率下根本不存在的亚像素细节。禁用运动向量输入会使DLSS质量大幅退化。

**误区二：帧生成降低了输入延迟**
DLSS 3帧生成提升的是**显示帧率**，不是游戏逻辑帧率。AI生成帧不来自CPU对新输入的响应，因此从键鼠操作到画面响应的延迟（Input Latency）并未改善，甚至在不配合NVIDIA Reflex的情况下可能略有增加。玩家在对延迟敏感的竞技游戏中需特别注意这一区别。

**误区三：DLSS 2.0是通用模型所以质量一致**
DLSS 2.0虽然使用通用网络，但仍依赖游戏引擎正确输出**线性空间运动向量**和**精确深度缓冲区**。若游戏引擎在透明物体、粒子系统等处不提供正确的运动向量（这是常见实现缺陷），DLSS会在这些区域产生"鬼影"（Ghosting），与TAA存在相同类型的时序稳定性问题。

---

## 知识关联

**前置概念——TAA（时序抗锯齿）**：DLSS 2.0的设计直接继承了TAA的核心架构——亚像素抖动采样、运动向量重投影、历史帧混合。理解TAA的EMA混合公式 $C_t = \alpha \cdot C_{current} + (1-\alpha) \cdot C_{history}$ 有助于理解DLSS用神经网络替换这一混合步骤的动机：EMA无法区分有效历史与遮挡失效区域，而神经网络可以学习更精细的融合策略。

**后续概念——超分辨率技术**：DLSS开创的"基于时序的神经网络超分辨率"范式促使AMD推出FSR 2.0（基于时域但无需机器学习）和Intel推出XeSS（同样使用深度学习），形成了跨厂商的超分辨率技术竞争格局，超分辨率的评估指标如SSIM、VMAF也成为该领域标准工具。

**后续概念——帧生成**：DLSS 3的帧生成模块将AI的介入从单帧质量增强扩展到帧率合成，AMD的FSR 3 Frame Generation和NVIDIA的DLSS 3.5 Ray Reconstruction代表了帧生成技术的进一步发展方向，其核心挑战在于处理快速运动和UI元素的正确性。