---
id: "cg-vol-fog"
concept: "体积雾"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 3
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.5
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



# 体积雾

## 概述

体积雾（Volumetric Fog）是一种基于体积渲染的大气效果技术，通过模拟光线在介质中的散射与吸收来产生真实感雾气。与传统的深度雾（Depth Fog）不同，体积雾能够响应场景中的实际光源，使雾气在光照区域变亮、在阴影区域变暗，形成丁达尔效应（Tyndall Effect）般的光柱与体积阴影。

体积雾的现代实现方案以 **Froxel（Frustum Voxel，视锥体素）** 体素化方案为主流，由 Bart Wronski 在 2014 年 SIGGRAPH 演讲 "Volumetric fog: Unified, compute shader-based solution to atmospheric scattering" 中系统化提出并推广。Froxel 方案将摄像机视锥体划分为一个三维格网，每个格子称为一个 Froxel，在这个格网空间中完成所有体积光照的积分计算，避免了传统 Ray Marching 对每条像素光线独立迭代的高昂开销。

Froxel 体积雾之所以在游戏引擎中被广泛采用（Unreal Engine 4.14 正式引入、Unity HDRP 同样使用此方案），根本原因在于它将时间复杂度从 O(像素数 × 步进次数) 降低到一次固定分辨率的三维纹理计算，并天然支持时间积累抗噪（Temporal Accumulation）。

---

## 核心原理

### Froxel 格网的构建

Froxel 格网通常在 XY 方向以屏幕分辨率的 1/8 对齐划分，Z 方向（深度方向）按对数分布划分 64 或 128 个切片，得到一张分辨率约为 **160×90×64** 的三维纹理（以 1280×720 渲染为例）。Z 方向采用对数分布而非线性分布，是因为近处雾的视觉变化更敏感，对数分布能让近处切片密集、远处切片稀疏，与人眼感知一致。

每个 Froxel 存储以下信息：
- **散射系数 σ\_s**（Scattering Coefficient）：光线被散射的概率密度
- **吸收系数 σ\_a**（Absorption Coefficient）：光线被吸收的概率密度
- **消光系数 σ\_t = σ\_s + σ\_a**
- **自发光/内散射贡献 L\_i**

### 体积光照注入（Lighting Injection）

在 Compute Shader 中，遍历每个 Froxel，对当前体素位置累积来自各光源的内散射（In-Scattering）贡献。定向光需采样级联阴影贴图（CSM）判断当前体素是否在阴影中；点光源与聚光灯则通过 Clustered Deferred 结构找到影响该体素的灯光列表。

相位函数（Phase Function）决定光的散射方向分布。Froxel 方案中常用 **Henyey-Greenstein 相位函数**：

$$p(\theta) = \frac{1}{4\pi} \cdot \frac{1 - g^2}{(1 + g^2 - 2g\cos\theta)^{3/2}}$$

其中 g 为各向异性参数，范围 [-1, 1]，g=0 表示各向同性散射，g=0.85 左右模拟真实大气的前向散射特性。

### 沿视线方向的体积积分（Ray Marching in Froxel Space）

光照注入完成后，沿 Z 方向对三维纹理执行前向散射积分（Front-to-Back Integration）。对第 k 个切片，维护两个累积量：

- **累积透射率** $T_k = \exp\left(-\sum_{i<k} \sigma_{t,i} \cdot \Delta d_i\right)$
- **累积内散射** $S_k = \sum_{i<k} T_i \cdot L_i \cdot \sigma_{s,i} \cdot \Delta d_i$

这一步骤在 Compute Shader 中通过对 Z 轴方向的前缀扫描（Prefix Scan）实现，结果写入另一张三维纹理，存储每个 Froxel 位置处的 (散射颜色, 透射率)。

### 最终合成

在全屏后处理阶段，对每个屏幕像素，根据其线性深度在 Z 方向对预积分纹理进行三线性采样，将体积雾的 (S, T) 与场景颜色 C\_scene 合成：

$$C_{final} = C_{scene} \times T + S$$

此步骤仅需一次三维纹理采样，GPU 开销极低。

---

## 实际应用

**Unreal Engine 4 的实现**：在 UE4 的体积雾系统中，默认 Froxel 分辨率为屏幕 1/8，Z 方向 128 切片，支持最多 2 个级联阴影的定向光体积阴影，以及 Clustered 光照下的点光源体积散射。开启后额外 GPU 开销约为 1.5ms（在 GTX 980 上）。

**时间积累降噪**：由于 Froxel 分辨率较低，直接渲染会产生明显的块状噪声。实践中对光照注入阶段引入 Halton 序列抖动（每帧偏移 Froxel 采样位置），并将当前帧结果与前一帧三维纹理按 0.05 的权重混合（指数移动平均），可在 4-8 帧内收敛到无噪声结果。

**高度雾集成**：Froxel 体积雾可在注入阶段对密度应用高度衰减函数 $\rho(y) = \rho_0 \cdot \exp(-\beta \cdot y)$，参数 β 控制雾随高度消散的速率，从而同时模拟高度雾效果，无需额外 Pass。

---

## 常见误区

**误区一：Froxel 体积雾与 Ray Marching 是对立的两种技术**
实际上 Froxel 方案本质上是将 Ray Marching 的步进过程迁移到统一的三维纹理空间中预计算。Z 方向的前缀积分就是 Ray Marching 的向量化执行，只不过所有像素共享同一套步进结果，而非各自独立步进。Froxel 是 Ray Marching 的结构化优化，而非替代品。

**误区二：Froxel 分辨率越高越好**
Z 方向切片数加倍（如从 64 到 128）会使三维纹理内存与光照注入 Compute 开销同步加倍，而视觉收益受限于时间积累的平滑效果往往不成比例。更有效的提升路径是优化 Halton 抖动与时间混合系数，而非盲目提升静态分辨率。

**误区三：体积雾会自动产生正确的体积阴影**
体积阴影需要场景光源主动将其阴影贴图提供给体积光照注入阶段采样，默认情况下非主方向光（如点光源）不产生体积阴影，需额外配置光源的体积散射标志位并保证其拥有有效的阴影贴图。

---

## 知识关联

**前置知识 - Ray Marching**：Froxel 体积雾的 Z 方向积分本质是 Ray Marching 的批量化形式。理解 Beer-Lambert 定律（$T = e^{-\sigma_t d}$）和步进累积是读懂 Froxel 积分公式的必要前提，Froxel 将逐像素的变步长 Marching 替换为在统一对数深度格网上的前缀扫描。

**并行扩展 - Clustered Shading**：Froxel 方案的光照注入阶段高度依赖 Clustered Deferred 或 Tiled 结构，以便在 Compute Shader 中快速查询影响每个体素的局部光源列表；若场景仅有方向光，则可以简化注入阶段，去掉灯光列表索引的部分。

**延伸方向 - 参与介质渲染（Participating Media）**：体积雾是参与介质渲染的简化特例，假设介质均匀且无表面散射。更完整的参与介质渲染需引入多次散射（Multiple Scattering）近似，如 Frostbite 在 2015 年提出的基于球谐函数的多次散射预积分方法，以及路径追踪中的 Delta Tracking 算法。