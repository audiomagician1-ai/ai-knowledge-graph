---
id: "cg-xess"
concept: "XeSS"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# XeSS（Intel 超分辨率扩展技术）

## 概述

XeSS（Xe Super Sampling）是Intel于2022年随Arc显卡发布的AI驱动超分辨率技术，全称为"Xe超级采样"。它通过以较低分辨率渲染场景，再利用深度学习模型将图像放大至目标分辨率，在保持较高画质的同时显著提升帧率。XeSS 1.0随《魔女传说》（Shadow of the Witch）等首批支持游戏于2022年9月正式面向公众推出。

XeSS的独特之处在于它针对Intel Arc显卡（Alchemist架构及以后）的XMX（Xe Matrix eXtensions）矩阵运算单元进行了专门优化。XMX单元是Arc GPU中专门执行矩阵乘法的硬件加速器，与NVIDIA的Tensor Core功能类似，可高效执行深度学习推理所需的大量点积运算。在非Intel硬件上，XeSS会自动退回到基于DP4a（4元素点积）指令的通用路径运行，因此也能在AMD和NVIDIA GPU上使用，只是无法享受XMX的全速硬件加速。

XeSS的工程意义在于打破了超分辨率技术只服务于单一硬件平台的格局：开发者只需集成一套XeSS SDK，即可让游戏同时惠及Intel、AMD、NVIDIA三家GPU用户，无需分别适配多套专有方案。

## 核心原理

### XMX矩阵加速与网络推理

XeSS的放大核心是一个轻量化卷积神经网络。在配备XMX单元的Intel Arc GPU上，该网络通过矩阵乘法累加（MMA）指令以INT8或FP16精度执行，XMX单元每个时钟周期可完成大批量矩阵运算，相比通用着色器执行同等推理任务效率高出数倍。网络输入包括当前帧的低分辨率颜色缓冲、运动向量（Motion Vectors）以及历史帧反投影数据，输出为目标分辨率下的高质量图像。

### 多帧历史累积与运动向量

与基础的空间超采样不同，XeSS引入了TAA式的时域累积策略。渲染引擎在每帧使用亚像素级的Halton序列抖动（Jitter）偏移相机，使连续多帧的像素采样位置互相错开，从而在累积后获得比单帧更丰富的高频细节。运动向量用于将上一帧的历史像素反投影到当前帧坐标系中，XeSS网络随后判断哪些历史像素可信并加以融合，哪些因遮挡或快速运动应予抛弃，从而抑制传统TAA中常见的"鬼影（Ghosting）"伪影。

### 放大质量档位

XeSS提供六个预设质量档位，以输入分辨率与输出分辨率的比值定义：

| 档位 | 输入分辨率比例 | 放大倍率（线性） |
|------|--------------|----------------|
| Ultra Quality Plus | 77%（约1/1.3x） | ~1.3x |
| Ultra Quality | 77% | 1.3x |
| Quality | 67%（2/3） | 1.5x |
| Balanced | 59% | 1.7x |
| Performance | 50% | 2x |
| Ultra Performance | 33% | 3x |

在4K（3840×2160）目标分辨率下，Performance档的实际输入为1920×1080，即以1080p渲染最终输出4K，帧率收益可达约70%~100%，具体取决于GPU瓶颈位置是在渲染还是后处理阶段。

### DP4a回退路径

当硬件不支持XMX时，XeSS切换至DP4a通用路径。DP4a是Vulkan和DirectX 12中均支持的INT8点积指令，几乎所有现代桌面GPU（包括AMD RDNA2和NVIDIA Turing及以后）均支持该指令集。回退路径使用同一神经网络权重但以软件方式调度矩阵运算，性能低于XMX路径，但画质与XMX路径基本一致。XeSS SDK会在初始化时自动检测硬件能力并选择对应路径，对上层应用透明。

## 实际应用

在《赛博朋克2077》中启用XeSS Quality档位（1440p目标，实际渲染960p）后，Intel Arc A770在光线追踪中等画质下帧率从约35fps提升至约58fps，画质损失主要集中在极细边缘处的轻微模糊，远景几何细节保留良好。

《杀手3》等支持XeSS的游戏通过DirectX 12的资源接口向SDK传入以下必要数据：当前帧颜色缓冲（HDR或LDR均可）、深度缓冲、运动向量缓冲以及曝光值，SDK内部管理历史帧缓存和网络权重，游戏引擎无需自行实现累积逻辑。XeSS SDK以开源形式托管于GitHub（github.com/intel/xess），开发者可直接查看集成示例和着色器实现。

在移动平台，XeSS也被引入部分搭载Intel Arc集成显卡的超薄本，使这类功耗受限设备在轻度游戏场景下通过降低渲染分辨率并由XeSS补全细节，来维持可接受的视觉质量。

## 常见误区

**误区一：XeSS只能在Intel显卡上运行。** 实际上XeSS通过DP4a回退路径支持AMD和NVIDIA GPU。区别仅在于性能：在Intel Arc上运行XeSS的推理开销可借助XMX大幅压缩，而在其他GPU上则完全由着色器单元承担，帧率提升比例略低，但不存在画质差异。

**误区二：XeSS与TAA互斥，启用XeSS后TAA自动无用。** XeSS本身内嵌了时域累积逻辑，因此启用XeSS时引擎层面的独立TAA通道应当关闭，否则两层时域操作叠加会导致过度模糊和双重鬼影。但XeSS并不是"替代TAA"，而是将TAA的累积策略与神经网络放大融合为一个统一通道。

**误区三：XeSS Quality档位的输入分辨率比例与DLSS Quality完全相同。** DLSS Quality档在4K目标下使用约67%输入（约2560×1440），与XeSS Quality的67%比例相近，但XeSS的Ultra Quality Plus档提供77%的更高比例输入，这是DLSS 2.x中未提供的额外档位，专门面向画质优先的使用场景。

## 知识关联

XeSS以TAA为直接前驱：若无对TAA中Halton抖动、运动向量重投影和历史帧融合权重的理解，便无法解释XeSS为何需要抖动偏移以及历史缓冲的用途。XeSS在TAA基础上引入了神经网络决策层，替代了TAA中固定权重的混合公式（通常为`output = lerp(history, current, 0.1)`），以学习到的权重动态判断历史像素可信度，从而抑制Ghosting并恢复TAA难以保留的高频锐度。

在超分辨率技术谱系中，XeSS与NVIDIA DLSS 2/3（Tensor Core加速）、AMD FSR 2（纯空间+时域，无专用AI硬件）构成同一层级的对比参照。FSR 2依赖启发式算法而非神经网络，可在任意GPU甚至主机平台运行；XeSS则以神经网络为核心但借助DP4a保持跨平台兼容，处于两者之间的技术定位。理解XeSS的XMX加速路径与DP4a回退路径的性能差异，是评估图形API中AI加速硬件价值的具体案例。