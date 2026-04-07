---
id: "vfx-shader-uv-scroll"
concept: "UV滚动"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# UV滚动

## 概述

UV滚动（UV Scrolling）是一种通过在每帧持续偏移或旋转贴图的UV坐标，使静态纹理呈现出流动、旋转、波动等连续动画效果的Shader技术。其核心操作是在片元着色器中将UV坐标加上随时间变化的偏移量，从而让采样位置不断移动，视觉上表现为纹理"流动"。

这项技术早在固定管线时代就已被广泛使用，DirectX 8时代的多重纹理单元就支持UV变换矩阵。进入可编程着色器时代后，UV滚动被完整移植到HLSL/GLSL着色器中，成为游戏特效中成本最低、效果最稳定的动画手段之一。一张512×512的普通噪声贴图配合UV滚动，可以模拟出火焰、熔岩、流水、传送门等多种视觉效果，而无需任何动画帧数据。

UV滚动之所以在特效制作中占据重要地位，原因在于它的GPU开销极小——整个操作仅需一次向量加法和一次纹理采样，即使在移动端也几乎不产生性能负担。与序列帧Shader需要存储多帧图像不同，UV滚动用单张贴图即可产生持续无限循环的动态感。

## 核心原理

### UV偏移公式

UV滚动的基础公式为：

```
UV_scrolled = UV_original + float2(speedU, speedV) * _Time.y
```

其中 `UV_original` 是网格的原始UV坐标，`speedU` 和 `speedV` 分别控制U轴和V轴的滚动速度（单位：UV单位/秒），`_Time.y` 是Unity中以秒为单位的运行时间变量（`_Time.x` 为 `t/20`，`_Time.z` 为 `t*2`，`_Time.w` 为 `t*3`）。当 `speedU = 0.2` 时，纹理每5秒完整滚动一个UV周期。由于UV坐标在采样时会自动根据Wrap Mode（通常设为Repeat）进行取模，滚动效果天然无缝循环。

### UV旋转公式

旋转型UV滚动需要以UV中心点（通常为0.5, 0.5）为轴旋转坐标系，公式为：

```
float2 center = float2(0.5, 0.5);
float2 uv = UV_original - center;
float angle = _RotationSpeed * _Time.y;
float s = sin(angle), c = cos(angle);
float2 UV_rotated = float2(uv.x * c - uv.y * s, uv.x * s + uv.y * c) + center;
```

旋转速度 `_RotationSpeed` 单位为弧度/秒，设置为 `6.283`（即2π）时每秒旋转一整圈。旋转型UV滚动常用于制作漩涡、龙卷风、传送门等具有离心感的特效。

### 多层UV叠加

单层UV滚动往往显得过于规律。实际特效制作中，常用两层UV以不同速度和方向滚动同一张噪声贴图，再将采样结果相乘或相加：

```
float noise1 = tex2D(_NoiseTex, uv + float2(0.1, 0.0) * _Time.y).r;
float noise2 = tex2D(_NoiseTex, uv + float2(-0.07, 0.05) * _Time.y).r;
float combined = noise1 * noise2;
```

两层UV方向相互偏斜（例如第一层向右、第二层向左上），相乘后会产生随机闪烁的亮斑，这是模拟火焰湍流的经典做法。使用同一张贴图进行两次采样的总显存占用为零，仅增加一次纹理读取指令。

## 实际应用

**流动熔岩地板**：将一张泰勒噪声纹理的UV在V轴方向以0.15的速度向上滚动，采样结果输入色阶映射，用橙红色渐变色板输出颜色，即可得到连续翻涌的熔岩表面效果，无需任何骨骼动画或顶点动画。

**传送门旋转光晕**：对环形UV（通过极坐标转换得到的角度分量）施加旋转滚动，速度设为 `1.0` 弧度/秒，配合径向渐变遮罩，产生逆时针缓慢旋转的能量环特效。传送门外圈和内圈可以分配不同旋转速度（如外圈0.8、内圈-1.2），形成反向对转感。

**流水/河流表面**：主纹理UV在U轴方向以0.3滚动，同时叠加一张法线贴图也以0.25的速度滚动但方向略微偏转5度，法线贴图的扰动叠加在高光计算中，产生水面波光粼粼的折射感，这一技术在许多3A游戏的次级水面渲染中均有应用。

**UI能量条流动光泽**：在UI Shader中对高光遮罩纹理施加水平方向UV滚动（speed = 0.5），使能量条表面持续流动一道白色光泽带，增强满血或充能状态的视觉反馈。

## 常见误区

**误区一：认为UV滚动速度越快越好**。当speedU或speedV超过1.0时，在低帧率设备上（如30fps），单帧UV偏移量超过0.033 UV单位，肉眼可感知到纹理"跳跃"而非平滑流动。对于需要精细流动感的效果，速度通常设定在0.05至0.3之间，并确保贴图本身有足够的细节频率支撑。

**误区二：将UV滚动与溶解效果混用时忘记分离UV采样通道**。溶解效果通常使用同一张噪声贴图的单通道（如R通道）作为阈值Mask，若对该贴图同时施加UV滚动，溶解边界会随时间移动，破坏预期的溶解方向。正确做法是为滚动层和溶解Mask层使用独立的UV变量，分别采样后再组合。

**误区三：认为UV旋转必须以(0.5, 0.5)为中心**。对于非正方形网格或需要偏心旋转效果（如星系旋臂），旋转中心应根据美术意图调整。将旋转中心移至(0.3, 0.3)会产生明显的偏心涡旋，而错误地固定在(0.5, 0.5)会导致对称感破坏。

## 知识关联

UV滚动在技术实现上依赖对UV坐标系的基本理解，序列帧Shader的学习中已涉及UV的分块采样（将UV空间划分为N×M的格子），UV滚动则是在此基础上操作整体UV的平移和旋转变换，两者都在片元着色器的UV操作层面工作但目的不同——序列帧依赖帧索引切换，UV滚动依赖连续时间偏移。

掌握UV滚动后，下一个进阶方向是折射扭曲（Refraction Distortion）。折射扭曲同样操作UV坐标，但不是简单的线性偏移，而是使用一张法线贴图或扰动贴图的采样值来扭曲屏幕空间UV，产生透过玻璃或水波看背后物体的变形效果。理解UV滚动中"偏移向量控制采样位置"这一核心思维，是理解折射扭曲中"扰动向量控制屏幕UV偏移"的直接前提。