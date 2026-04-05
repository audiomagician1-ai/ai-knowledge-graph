---
id: "cg-fog-pp"
concept: "雾效"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 2
is_milestone: false
tags: ["效果"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 雾效

## 概述

雾效（Fog Effect）是图形渲染中一种模拟大气散射现象的后处理技术，通过将场景颜色与雾的颜色按距离或高度进行混合，营造出能见度受限的大气环境感。雾效的物理依据是光线在穿过含有水汽、尘埃或烟雾颗粒的大气时发生米氏散射（Mie Scattering），导致远处物体的颜色趋向于背景色或天空色。

雾效在早期3D游戏（如1996年的《雷神之锤》）中还承担着遮挡远处低质量几何体的功能，是一种性能优化手段。现代渲染管线中，雾效依然被广泛使用，但目的更多是提升场景氛围与景深感，尤其在恐怖类、写实类游戏中极为常见。

雾效的核心计算本质上是一个插值（lerp）操作：`final_color = lerp(object_color, fog_color, fog_factor)`，其中`fog_factor`由具体的雾类型公式决定，取值范围为[0, 1]，0表示无雾，1表示完全被雾覆盖。

---

## 核心原理

### 线性雾（Linear Fog）

线性雾是最简单的雾模型，其雾因子与摄像机距离d呈线性关系，公式为：

```
fog_factor = (fog_end - d) / (fog_end - fog_start)
```

其中`fog_start`是雾开始出现的距离，`fog_end`是物体完全被雾覆盖的距离。线性雾计算成本最低，但视觉上缺乏真实感——现实中能见度的衰减并非线性，因此线性雾更适合程式化（Stylized）风格的游戏，如早期卡通渲染项目。

### 指数雾（Exponential Fog）

指数雾更符合大气散射的物理规律，有两种变体。标准指数雾公式为：

```
fog_factor = e^(-density × d)
```

平方指数雾（Exponential Squared Fog）公式为：

```
fog_factor = e^(-(density × d)²)
```

其中`density`是雾的密度系数，`d`是片元到摄像机的距离。平方指数雾衰减更快，远处物体更迅速地消失，适合浓雾场景；标准指数雾衰减更平滑，适合轻度薄雾效果。Unity引擎中这三种雾模式（Linear/Exponential/Exponential Squared）均内置支持，可通过`Lighting > Environment > Fog`面板直接切换。

### 高度雾（Height Fog）

高度雾基于片元的世界空间Y坐标（高度）而非摄像机距离来计算雾因子，常用公式为：

```
fog_factor = e^(-max(0, world_y - fog_height) × density)
```

高度雾能模拟低洼处积聚的晨雾或沼泽雾气，片元高度越低（world_y越小），雾浓度越大。实际项目中常将高度雾与指数距离雾叠加使用，最终雾因子取两者的最大值或乘积，以获得兼顾远近和高低的雾效。

### 体积雾（Volumetric Fog）

体积雾是四种雾效中最昂贵但最真实的方案，它通过光线步进（Ray Marching）沿视线方向积分大气密度，并支持光源对雾的散射影响（丁达尔效应）。每条视线被划分为若干步长（通常16到64步），每步采样三维噪声贴图（如Worley Noise）确定局部密度，并计算来自场景光源的散射贡献。体积雾作为后处理实现时，通常先以半分辨率（Half Resolution）渲染体积光散射缓冲区，再上采样合并到主帧缓冲，以降低性能开销。Unreal Engine 5的`Volumetric Fog`组件支持实时阴影投射到雾层，并有温度-密度模拟。

---

## 实际应用

**场景氛围营造**：在恐怖游戏《寂静岭》系列中，雾效是核心视觉语言，初代使用的浓厚指数雾本是PlayStation 1硬件的绘制距离限制所迫，却意外成为游戏恐怖氛围的标志性元素，后续系列刻意保留了这一设计。

**室外写实场景**：在开放世界游戏中，高度雾常用于渲染山谷晨雾或海面薄雾。具体实现中，美术人员会设置`fog_height`参数（例如世界坐标Y=20米以下雾浓度最高），配合天空盒颜色采样保持雾色与天光一致。

**水下效果**：水下场景通常使用距离指数雾，`density`参数设置较高（约0.05到0.1），雾颜色设为深蓝绿色（如`#1A3A4A`），配合轻微颜色偏移模拟水体对光的波长选择性吸收。

**遮挡LOD过渡**：在移动端游戏中，线性雾的`fog_end`参数常被设置为与LOD切换距离对齐，例如同为50米，使低模LOD出现时已被雾色遮盖，消除明显的几何跳变。

---

## 常见误区

**误区一：雾效颜色应始终设为纯灰色或纯白色**  
实际上，雾色应与场景光照环境保持一致。晴天户外的雾应采样天空颜色（蓝偏白），黄昏时应为橙红色，阴天才接近中性灰。直接硬编码为白色`(1,1,1)`会导致场景看起来像被白色漆覆盖，而非自然的大气效果。

**误区二：深度值可以直接作为雾效的距离参数**  
非线性深度缓冲（NDC深度）与视空间距离并不相等。若直接用深度缓冲值d_ndc代入雾公式，近处精度过高、远处精度急剧下降，导致远处雾效呈现分层或马赛克状失真。正确做法是先将NDC深度重建为线性视空间深度（View-space depth）再计算雾因子，公式为：`linear_z = (2 × near × far) / (far + near - d_ndc × (far - near))`。

**误区三：体积雾可以完全取代简单雾**  
体积雾在移动端或低端硬件上的光线步进开销可能高达每帧3到8毫秒，而线性雾或指数雾的全屏后处理Pass开销通常低于0.2毫秒。对于不需要体积光散射或精细密度变化的场景，简单雾在视觉上已足够，强行使用体积雾是明显的性能浪费。

---

## 知识关联

雾效后处理依赖**后处理概述**中介绍的全屏Pass流程：场景先渲染到帧缓冲（含颜色缓冲与深度缓冲），雾效Pass在片元着色器中读取深度缓冲重建世界坐标或视深度，再执行雾色混合，最终输出到屏幕。

雾效与**景深（Depth of Field）**在实现上共享深度重建逻辑，两者均需将深度缓冲值转换为线性距离；在渲染顺序上，雾效通常在景深Pass之前应用，避免雾色被景深模糊后出现颜色溢出（Color Bleeding）伪影。

体积雾与**体积光（Volumetric Lighting）**高度耦合，体积雾密度场本身就是体积光散射积分的输入之一，两者共用同一组光线步进数据，这是现代渲染引擎将两者合并为单一`Volumetric`系统的原因。