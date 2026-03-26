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
quality_tier: "B"
quality_score: 48.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
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

UV滚动（UV Scrolling）是一种通过对纹理采样坐标施加随时间变化的偏移量，从而产生纹理持续流动视觉效果的Shader技术。其本质是修改传入`tex2D`函数的UV坐标，而非移动几何体本身，因此几乎零性能开销即可实现水流、岩浆、传送门光效、云层漂移等持续循环动画。

该技术最早在1990年代末的游戏引擎中被广泛采用——《雷神之锤III》（Quake III Arena，1999年）的引擎即通过卷轴UV实现了动态水面效果。现代游戏引擎如Unity和Unreal Engine均将UV滚动视为内置节点提供，例如Unity Shader Graph中的`Tiling and Offset`节点可直接驱动随时间滚动的UV。

UV滚动之所以在特效开发中占据重要地位，是因为它能够以极低的顶点和像素计算成本，将静态纹理变为具有方向性运动感的动态视觉元素，是水体、火焰、能量场等大量常见效果的底层实现方式。

---

## 核心原理

### UV偏移公式

UV滚动的数学核心是在片元着色器中对原始UV坐标加上与时间成比例的偏移量：

```
UV_scrolled = UV_original + float2(speedU, speedV) * _Time.y
```

其中：
- `UV_original` 是顶点插值传入的原始纹理坐标（通常范围为0~1）
- `speedU` / `speedV` 分别控制横向（U轴）和纵向（V轴）的滚动速度，单位为**每秒移动的UV单位数**
- `_Time.y` 是Unity内置变量，表示自游戏开始以来的秒数（`_Time.x`是四分之一秒，`_Time.z`是双倍秒数，`_Time.w`是三倍秒数）

由于纹理默认启用Repeat（重复平铺）采样模式，UV超出0~1范围时会自动回绕，因此产生无缝循环滚动效果。若纹理改为Clamp模式，滚动到边缘后将停止而非循环。

### UV旋转公式

UV旋转是UV滚动的变体，通过围绕某个中心点旋转UV坐标实现纹理自转效果：

```
UV_centered = UV - pivot          // 将旋转中心移至原点
UV_rotated.x = UV_centered.x * cos(θ) - UV_centered.y * sin(θ)
UV_rotated.y = UV_centered.x * sin(θ) + UV_centered.y * cos(θ)
UV_final = UV_rotated + pivot     // 还原旋转中心
θ = rotateSpeed * _Time.y         // 角度随时间递增（弧度制）
```

其中`pivot`通常取`float2(0.5, 0.5)`以围绕纹理中心旋转，`rotateSpeed`的典型值为`3.14159`时表示每秒旋转半圈（π弧度）。

### 多层UV叠加

实际的水面或火焰效果很少使用单层UV滚动，而是对同一张或两张纹理以**不同速度和方向**采样后进行混合。例如水面效果常见的写法：

```hlsl
float2 uv1 = i.uv + float2(0.1, 0.05) * _Time.y;
float2 uv2 = i.uv + float2(-0.07, 0.12) * _Time.y;
float4 col = (tex2D(_MainTex, uv1) + tex2D(_MainTex, uv2)) * 0.5;
```

两层UV方向相反、速度不同，叠加后打破了单层滚动的机械感，产生更接近真实液体的扰动视觉。

---

## 实际应用

**熔岩/岩浆地面**：将一张橙红色噪声纹理以V轴方向`speedV = 0.2`向上滚动，同时叠加一层以`speedV = 0.15, speedU = 0.05`的斜向层，最终颜色乘以自发光强度，形成流淌感强烈的岩浆效果，无需任何骨骼动画或顶点动画。

**传送门/魔法阵旋转**：以`pivot = (0.5, 0.5)`对符文纹理施加UV旋转，内层以`rotateSpeed = 1.0`（约6秒一圈）顺时针旋转，外层以`rotateSpeed = -0.6`逆时针旋转，两层叠加产生典型的传送门能量旋涡视觉。

**瀑布/水流**：对法线贴图而非颜色贴图进行UV滚动是水体高质量效果的关键——以`speedV = 0.3`滚动法线贴图，将结果输入光照计算，使高光随法线流动而移动，水流方向感明确且高光真实。

**UI进度条能量流**：在UI Shader中对Mask纹理进行UV横向滚动，`speedU = 0.5`，可以制作出充能、护盾值等带有流光效果的动态进度条，成本远低于粒子系统方案。

---

## 常见误区

**误区一：滚动速度越快效果越好**

UV滚动速度超过约0.5 UV单位/秒时，人眼会将运动感知为"闪烁"而非"流动"。水流类效果的`speedV`通常在0.05~0.3之间，岩浆略快但很少超过0.5。速度过快还会暴露纹理平铺的接缝，需要配合使用无缝平铺纹理。

**误区二：UV旋转不需要处理旋转中心**

许多初学者直接对UV施加旋转矩阵而忘记将原点移至`(0.5, 0.5)`，导致纹理绕左下角`(0, 0)`旋转，产生纹理整体"公转"而非"自转"的错误效果。必须在旋转前减去`pivot`，旋转后再加回。

**误区三：UV滚动等同于顶点动画**

UV滚动仅改变纹理采样位置，几何体轮廓保持不变。因此对于需要轮廓形变的效果（如水面波浪起伏），UV滚动无法单独胜任——通常需要配合顶点偏移（Vertex Offset）或法线扰动共同使用，UV滚动负责表面细节流动，顶点动画负责宏观形状变化。

---

## 知识关联

**前置概念**：学习UV滚动前需要掌握溶解效果中`step()`和噪声纹理采样的基本用法，以及序列帧Shader中`_Time`内置变量的使用方式——UV滚动的`_Time.y`驱动机制与序列帧Shader中帧索引的时间驱动逻辑相同，区别仅在于序列帧使用`floor(_Time.y * fps)`离散跳帧，而UV滚动直接使用连续值`_Time.y`产生平滑运动。

**后续概念**：折射扭曲（Refraction Distortion）是UV滚动的直接进阶——折射扭曲同样是对采样UV施加偏移，但偏移量不再是固定速度乘以时间，而是从一张法线贴图或噪声贴图中读取的**空间变化偏移量**，并可以对该噪声贴图本身施加UV滚动，形成"滚动噪声驱动扭曲"的双层效果。掌握UV滚动的向量偏移思路是理解折射扭曲的必要前提。