---
id: "vfx-shader-soft-particle"
concept: "软粒子"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 软粒子（Soft Particles）

## 概述

软粒子是一种利用深度缓冲（Depth Buffer）与粒子深度进行比较运算，从而在粒子与场景几何体交叉区域产生透明度渐变的粒子渲染技术。在传统硬粒子（Hard Particles）渲染中，当烟雾、火焰或爆炸粒子穿过地面或墙壁时，会出现明显的矩形截切边缘，产生强烈的视觉割裂感。软粒子技术通过在粒子接近不透明几何体时动态降低其Alpha值，使粒子"融入"场景而非被生硬截断。

该技术由 Evan Hart 和 John McDonald 于 2007 年在 NVIDIA 的 GPU Gems 3 中系统性阐述，核心公式为：`softAlpha = saturate((sceneDepth - particleDepth) / fadeDistance)`，其中 `fadeDistance` 通常设为 0.5 到 2.0 个世界单位，具体数值依据粒子体积大小调整。软粒子在当代游戏引擎中已成为粒子特效的标配渲染路径，Unity 的 Particle System 和 Unreal Engine 的 Niagara 均内置了软粒子支持，对应参数分别叫做 "Soft Particles" 和 "Soft Edge Fade Distance"。

## 核心原理

### 深度采样与比较

软粒子 Shader 需要在片元（Fragment）阶段读取屏幕空间深度缓冲中的值。具体流程是：先由不透明几何体的渲染 Pass 将场景深度写入深度缓冲贴图（Depth Texture），粒子渲染 Pass 再将此贴图作为额外采样输入。在 HLSL 中，通过 `tex2Dproj(_CameraDepthTexture, screenPos)` 采样当前像素的场景深度，然后用线性化后的场景深度减去粒子自身的线性深度，得到深度差值 `depthDiff`。

场景深度从 NDC（归一化设备坐标）的非线性 [0,1] 范围转换为线性视空间深度，必须使用 `LinearEyeDepth()` 函数（Unity）或等效的手动反推公式 `z = near * far / (far - depth * (far - near))`，跳过此线性化步骤是新手最常犯的错误，会导致靠近远裁面的粒子产生错误的透明度。

### Alpha 衰减计算

将深度差值 `depthDiff` 除以用户设定的淡化距离 `_InvFade`（其实存储的是 `1 / fadeDistance` 以节省除法开销），再通过 `saturate()` 将结果钳制到 [0,1]。完整的 Alpha 混合公式为：

```
finalAlpha = originalAlpha * saturate(depthDiff * _InvFade)
```

当粒子恰好贴合场景几何体表面时 `depthDiff ≈ 0`，`finalAlpha` 趋近于 0，粒子完全透明；当粒子远离几何体达到 `fadeDistance` 距离时，`finalAlpha` 恢复为原始 Alpha 值，粒子正常显示。

### 渲染管线依赖

软粒子必须要求渲染管线支持在粒子渲染阶段读取场景深度贴图，这意味着：延迟渲染（Deferred Rendering）可以直接复用 G-Buffer 中的深度，前向渲染（Forward Rendering）则需要额外的深度预渲染 Pass（Depth Prepass）。在移动端，额外的深度贴图采样会增加带宽压力，部分项目会在低端设备上通过宏定义 `#pragma multi_compile` 动态禁用软粒子路径，回退到硬粒子渲染。

## 实际应用

**地面烟雾效果**：战场烟雾粒子系统落地时，若使用硬粒子，烟雾四边形底部会与地形产生锯齿状交叉线。启用软粒子并将 `_InvFade` 设为 `2.0`（即淡化距离 0.5 米）后，烟雾底部会自然地"扩散"在地面上，视觉上接近真实烟雾在地表蔓延的形态。

**水面泡沫**：粒子系统模拟水面泡沫与礁石交界区域时，软粒子可令泡沫白色粒子在礁石边缘平滑消退，`_InvFade` 通常设置更小的值（淡化距离约 0.1 到 0.3 米），配合纹理流动制造泡沫沿岩石轮廓流动的效果。

**爆炸冲击波**：半透明冲击波四边形穿过建筑物或角色几何体时，软粒子避免了冲击波圆盘被墙壁"切断"的硬边，淡化距离通常需要设置为 1.0 至 3.0 米以匹配冲击波的体量。

## 常见误区

**误区一：认为软粒子可以解决粒子与半透明物体的穿插问题**。软粒子的深度比较依赖的是不透明几何体写入深度缓冲的值，而半透明物体在标准渲染管线中不写入深度缓冲，因此粒子穿越玻璃窗或水面等半透明物体时，软粒子完全不起作用，边缘依然会出现硬截切。

**误区二：把淡化距离（fadeDistance）设得过大以期获得更"柔和"的效果**。将淡化距离设为 5 米以上会导致粒子在远未接触几何体时就开始变透明，烟雾或火焰会莫名其妙地在空中消失，反而破坏真实感。正确的调试方法是先观察粒子与场景的实际交叉深度范围，将淡化距离设为该交叉范围的 1.2 至 1.5 倍。

**误区三：在所有粒子上无差别启用软粒子**。对于不会接触场景几何体的高空粒子（如天空中的云朵粒子），启用软粒子仅带来额外的深度贴图采样开销而没有任何视觉收益，会不必要地增加 Overdraw 的着色成本。

## 知识关联

软粒子以**纹理流动**技术提供的 UV 动画为输入基础——流动纹理负责控制粒子表面的视觉细节形态，而软粒子控制粒子整体与场景的融合方式，两者在同一个粒子 Shader 中分别处理不同维度的视觉质量。

从软粒子出发，可以自然地引出**边缘侵蚀**技术：软粒子通过深度差控制整体 Alpha，边缘侵蚀则通过噪声贴图阈值控制粒子的逐像素消融效果，两者都属于粒子生命周期视觉过渡的手段，但侵蚀效果适用于粒子自身消散动画，软粒子适用于与场景的空间接触过渡。此外，大规模粒子系统的软粒子额外深度采样会加剧 **Overdraw 控制**面临的带宽和填充率压力，因此软粒子的应用范围决策与 Overdraw 控制策略必须联动考量。
