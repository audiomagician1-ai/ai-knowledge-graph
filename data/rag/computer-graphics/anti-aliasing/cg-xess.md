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
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# XeSS（Intel超分辨率技术）

## 概述

XeSS（Xe Super Sampling）是Intel于2022年随Arc显卡系列发布的AI驱动超分辨率技术，全称"Xe Super Sampling"，旨在通过机器学习将低分辨率渲染画面放大至目标分辨率，同时维持接近原生分辨率的视觉质量。与AMD FSR或NVIDIA DLSS不同，XeSS在设计上兼顾了两种运行模式：在Intel Arc GPU上利用专用的XMX（Xe Matrix eXtensions）矩阵运算单元加速神经网络推理，而在其他厂商GPU上则回退至基于DP4a指令（dot product of 4 elements with accumulate）的通用计算路径。

XeSS的历史背景与Intel进入独立显卡市场直接相关。2022年10月，Arc A系列台式机显卡正式上市，XeSS作为其旗舰软件功能同步推出，SDK对第三方开发者开放，并以开源形式发布部分组件。这一策略使XeSS能够与DLSS和FSR在游戏厂商中竞争集成优先级，首批支持游戏包括《死亡循环》和《暗影火炬城》。

XeSS的重要性在于它是唯一同时覆盖AI加速与传统计算路径的超分辨率方案。开发者集成一套SDK即可在所有主流GPU平台上运行，Arc用户获得XMX加速的高质量结果，而NVIDIA和AMD用户也能通过DP4a路径获得性能提升，尽管质量略低于XMX模式。

## 核心原理

### XMX矩阵运算单元与AI推理

XeSS的旗舰路径依赖Arc GPU内置的XMX单元执行神经网络推理。XMX是Intel为Xe-HPG架构设计的矩阵乘法加速器，每个Xe核心包含8个XMX引擎，每个引擎每周期可执行一个8×8×16的INT8矩阵乘法运算。XeSS的上采样网络权重以INT8量化格式存储，XMX硬件直接处理这些低精度矩阵乘法，相比通用着色器核心执行效率显著更高。这与NVIDIA的Tensor Core在技术层面属于同一类硬件设计思路，但XMX在每个Xe核心内的集成密度和指令集接口不同。

### 基于历史帧的时间域累积

XeSS继承并扩展了TAA（时间抗锯齿）的历史帧复用机制。每帧渲染时，引擎在亚像素级别应用抖动偏移（jitter offset），偏移序列采用Halton低差序列（通常取base-2与base-3的Halton序列的前8或16个样本），使相邻帧的采样点覆盖不同亚像素位置。XeSS网络接收当前低分辨率帧、历史高分辨率累积帧、运动向量和深度缓冲四类输入，通过运动向量将历史帧重投影到当前帧坐标系，然后由神经网络决定每个像素如何融合历史信息与当前帧细节。

### DP4a回退路径的计算逻辑

在非Intel GPU上，XeSS使用DP4a（dot product of 4 INT8 values accumulated into INT32）指令实现神经网络推理。DP4a是DirectX 12 Shader Model 6.4引入的指令，NVIDIA Pascal及以上架构和AMD GCN 4代及以上架构均支持。DP4a路径将相同的网络权重重新量化为适合通用着色器处理的格式，以HLSL Compute Shader编写，不依赖任何厂商专有扩展。由于DP4a路径缺少专用矩阵硬件的带宽优势，在相同GPU性能级别下推理耗时约为XMX路径的1.5到2倍，且推理结果在高频细节还原上略逊于XMX模式。

### 质量档位与分辨率缩放比例

XeSS提供五个预设质量档位：Ultra Quality（缩放比1.3×）、Quality（缩放比1.5×）、Balanced（缩放比1.7×）、Performance（缩放比2.0×）和Ultra Performance（缩放比3.0×）。以1080p输出为目标时，Performance模式内部渲染分辨率为540p，Ultra Performance模式仅渲染360p。缩放比越高，对神经网络从稀疏输入重建细节的能力要求越大，幽灵瑕疵（ghosting）和闪烁风险也随之上升。

## 实际应用

在《死亡循环》中，XeSS首次公开演示了其超分辨率效果。在Arc A770（16GB）上，以1440p Ultra Quality输出时，相比原生1440p渲染的帧时间节省约30%至35%，且通过XMX路径的画面锐度被评测人员描述为接近原生。《幽灵行者2》是另一个深度集成案例，该游戏同时支持XeSS、DLSS和FSR 2，为玩家提供直接的跨技术横向对比，多数评测显示XeSS XMX模式在动态场景细节还原上与DLSS 3的质量相当，而DP4a路径与FSR 2相当。

在开发者工作流程中，XeSS通过DirectX 12 API集成，SDK提供C++接口，开发者调用`xessD3D12Execute`函数并传入当前帧纹理、历史帧纹理、运动向量纹理和目标纹理即可完成一次上采样。Intel同时提供了用于验证运动向量正确性的调试覆盖层，帮助开发者排查ghosting问题的根本原因。

## 常见误区

**误区一：XeSS只能在Intel显卡上运行**。事实上XeSS通过DP4a路径支持任何兼容DirectX 12 Shader Model 6.4的GPU，包括NVIDIA GTX 1060（Pascal）及以上和AMD RX 480（Polaris）及以上。XMX加速是Intel Arc的专属优化，但技术本身对硬件平台是开放的。不少玩家因为XeSS与Arc显卡同期发布而误认为这是封闭的厂商专属技术。

**误区二：XeSS与DLSS在技术架构上完全相同**。尽管两者都使用神经网络，但DLSS 2及以后版本使用在NVIDIA服务器集群上离线预训练的固定权重文件（由游戏集成的.nv文件提供），而XeSS的网络权重由Intel预先训练后打包进SDK，所有支持游戏共享同一套权重，不需要针对每款游戏单独训练模型。这意味着XeSS无需NVIDIA那样的内容合作计划，开发者集成SDK即可直接获得最新权重。

**误区三：更高的缩放比例（如Ultra Performance）总是比低质量档位更值得用**。Ultra Performance的3.0×缩放在动态场景中极易产生ghosting和像素化瑕疵，在细节丰富的植被或快速移动物体上，360p→1080p的重建任务超出了当前XeSS网络的重建能力上限，最终结果有时不如原生720p渲染的清晰度，因此Ultra Performance档位主要用于极低性能GPU勉强运行游戏的场景，而非追求画质时的选择。

## 知识关联

XeSS直接建立在TAA的时间域累积原理之上，理解TAA中抖动偏移、历史帧混合系数（通常α=0.1）以及运动向量重投影的工作方式，是理解XeSS为何需要运动向量输入和深度缓冲的前提。TAA中的ghosting抑制问题（通过颜色空间邻域裁剪处理）在XeSS中由神经网络隐式学习，不再依赖手写的裁剪启发式算法，这是XeSS相比纯TAA在鬼影控制上的关键改进点。

从更宏观的抗锯齿技术谱系来看，XeSS与NVIDIA DLSS 2/3和AMD FSR 2/3构成当前主流的三大时间域超分辨率方案，它们的核心差异体现在硬件依赖性（DLSS需要Tensor Core、XeSS偏好XMX但不强制、FSR完全硬件无关）和训练策略（预训练固定权重vs.通用权重）两个维度上。XeSS的DP4a路径在算法上与FSR 2的空间域+时间域混合方法有相似的计算预算约束，两者在中低端硬件上的实际画质差距远小于XMX路径与DLSS之间的差距。
