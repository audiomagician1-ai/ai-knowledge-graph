---
id: "cg-velocity-buffer"
concept: "速度缓冲"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 2
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 51.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 速度缓冲

## 概述

速度缓冲（Velocity Buffer，也称为 Motion Vector Buffer）是一种屏幕空间的逐像素纹理，存储着每个像素从上一帧到当前帧在屏幕坐标系中的二维位移向量（单位通常为归一化设备坐标 NDC 或屏幕像素数）。与颜色缓冲或深度缓冲不同，速度缓冲记录的是**运动信息**而非静态几何信息，其每个纹素的 RG 两通道分别存储水平方向和垂直方向的像素位移量，数值范围约为 \([-1, 1]\) 的 NDC 位移或直接以像素为单位的整数偏移。

速度缓冲的概念在电影工业的离线渲染中早已存在（用于后期运动模糊合成），但引入实时图形管线是从 2000 年代中期的电影级运动模糊技术开始的。进入 2010 年代后，随着 TAA（时间性抗锯齿）在 Unreal Engine 4 及 Unity 等主流引擎中的普及，速度缓冲成为现代实时渲染管线中几乎不可缺少的 G-Buffer 通道之一。

速度缓冲之所以关键，在于它使 TAA 能够精确地将历史帧的像素重新投影到当前帧，同时也让屏幕空间运动模糊可以在一个独立的后处理 Pass 中高效完成——两者共享同一张纹理，节省了带宽与计算开销。

---

## 核心原理

### 速度向量的计算公式

对场景中的静态几何体，速度来源于相机的运动。对动态物体，还需叠加物体自身的骨骼或刚体变换。逐像素速度向量 \(\mathbf{v}\) 的计算公式为：

$$\mathbf{v} = \mathbf{p}_{curr}^{NDC} - \mathbf{p}_{prev}^{NDC}$$

其中：
- \(\mathbf{p}_{curr}^{NDC}\) 是顶点在**当前帧** MVP 变换后的 NDC 坐标
- \(\mathbf{p}_{prev}^{NDC}\) 是**同一顶点**（或同一世界位置）在**上一帧** MVP 变换后的 NDC 坐标

在顶点着色器中，引擎需要同时传入 `currentMVP` 与 `previousMVP` 两组矩阵，并在专用的 Velocity Pass（或 G-Buffer Pass 中的附加 RT）中输出差值到 RG16F 格式的渲染目标。RG16F 提供半精度浮点（约 3 位小数精度），对亚像素运动已足够，但对高速旋转物体可能需要升级为 RG32F。

### 静态物体与动态物体的分离处理

实现中必须区分两类速度来源：
1. **相机运动引起的静态物体速度**：直接使用当前帧和上一帧的 `ViewProjection` 矩阵逆推世界位置后重投影，静态物体无需在 CPU 侧传递额外的"前一帧模型矩阵"，因为其 `Model` 矩阵不变。
2. **动态物体（蒙皮动画/刚体）速度**：引擎须缓存上一帧的蒙皮后顶点位置（Skinned Position Cache）或物体的前一帧 `Model` 矩阵，并在 Vertex Shader 中将两帧位置同时传入，分别乘以 `currentVP` 和 `previousVP`。

Unreal Engine 4 中，对标记了 `bHasMotionBlurVelocity` 的网格体，引擎会自动在深度预通道（Depth PrePass）后的 `VelocityPass` 中输出这些值；未标记的静态网格体则在 TAA Resolve 时用深度重投影补算相机速度。

### 速度缓冲在 TAA 中的精确用途

TAA 的核心操作是将当前帧颜色与历史帧颜色以权重 \(\alpha \approx 0.1\) 进行混合：

$$C_{out} = (1-\alpha)\,C_{history}(\mathbf{uv} - \mathbf{v}) + \alpha\,C_{current}(\mathbf{uv})$$

其中 \(\mathbf{uv} - \mathbf{v}\) 正是利用速度缓冲采样历史帧的**重投影坐标**。若速度缓冲不准确（例如动态物体缺少前一帧矩阵），该像素处的历史采样会落在错误位置，产生俗称"鬼影"（Ghost）的残影伪影。速度缓冲精度每下降 0.5 像素，在 1080p 分辨率下鬼影半径约增加 1 像素，在快速运动场景中十分明显。

### 速度缓冲在运动模糊中的用途

屏幕空间运动模糊 Pass 直接读取速度缓冲，沿每个像素的速度方向进行多次纹理采样（典型采样数为 8～16 次），模拟相机快门打开期间的累积曝光。速度向量的长度决定模糊半径：向量长度若超过约 40 像素（以 1080p 为基准），通常需要对采样步长做瓦片化（Tile Max）最大值扩散，以避免过采样或过度模糊。

---

## 实际应用

**Unreal Engine 4 / 5 的双 Pass 策略**：UE 在 `VelocityPass` 阶段只渲染动态物体（Movable Components），对全屏静态像素则在 TAA Pass 内用当前深度缓冲和逆矩阵实时计算相机引起的速度，避免对大量静态三角形的冗余 Draw Call。

**Unity HDRP 的 Motion Vector Pass**：Unity HDRP 在相机深度预通道之后插入专用 `MotionVectors` Pass，输出格式为 `RGHalf`（即 RG16F），并额外提供 `_CameraMotionVectorsTexture`（纯相机运动）与 `_MotionVectorTexture`（含物体运动）两张纹理，允许 TAA 和 Motion Blur 分别订阅所需来源，减少错误。

**UI 与粒子系统的特殊处理**：UI 元素和某些透明粒子不参与速度缓冲写入（Stencil Mask 标记跳过），TAA 在这些区域直接使用相机速度或强制 \(\alpha = 1\)（完全使用当前帧颜色），避免 UI 文字在慢速相机移动时出现拖影。

---

## 常见误区

**误区一：速度缓冲存储的是世界空间速度**  
速度缓冲存储的是**屏幕空间 NDC 位移**，而非世界空间的米/秒速度。一个在世界空间高速运动但沿相机视线方向运动的物体，其屏幕投影位置可能几乎不变，速度向量趋近于零；而一个在世界空间缓慢旋转但垂直于视线方向的物体，其屏幕速度向量可能相当大。将速度缓冲误用为世界空间速度来驱动游戏逻辑会产生严重错误。

**误区二：静态物体不需要写入速度缓冲**  
当相机移动时，静态物体在屏幕上的投影位置同样发生变化，必须为其生成速度向量（通过深度重投影计算相机速度分量）。若跳过静态物体，TAA 在相机运动时会对静态背景产生严重鬼影。UE4 中曾有开发者因错误关闭 `r.VelocityOutputPass=0` 而导致 TAA 在相机移动时全屏鬼影的调试案例。

**误区三：RG8 格式足以存储速度向量**  
RG8 仅提供 256 级精度，在 1080p 下每级精度对应约 7.5 像素，远不足以表达亚像素运动。TAA 需要亚像素精度的速度向量才能正确对齐历史帧，因此业界标准是 **RG16F**（半精度浮点），部分实现在极高动态场景下使用 RG32F。

---

## 知识关联

速度缓冲以 TAA 为直接前提——没有 TAA 的历史帧积累需求，速度缓冲的亚像素精度要求就无从谈起。TAA 的 Neighborhood Clamping 和 Variance Clipping 算法依赖速度缓冲区分"运动像素"与"静止像素"，对运动像素降低历史帧权重以减少鬼影。速度缓冲同时向 Motion Blur Pass 供给数据，实现了"一次计算，两处复用"的带宽优化策略，这也是现代延迟渲染管线将其纳入标准 G-Buffer 的工程动机。