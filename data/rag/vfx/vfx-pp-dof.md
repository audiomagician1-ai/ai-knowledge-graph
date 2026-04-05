---
id: "vfx-pp-dof"
concept: "景深效果"
domain: "vfx"
subdomain: "post-process"
subdomain_name: "后处理特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-06
---



# 景深效果

## 概述

景深效果（Depth of Field，DoF）是模拟真实摄影镜头焦点特性的后处理渲染技术，其物理根源是几何光学中的弥散圆（Circle of Confusion，CoC）理论。当镜头焦距固定于某一距离时，该距离之外的点光源无法在传感器平面上汇聚为理想点，而是扩散为一个圆形光斑——其半径正比于物体偏离焦平面的距离与光圈直径的乘积。实时渲染通过逐像素计算 CoC 半径，将其映射为可变模糊核（Variable Blur Kernel），从而在帧缓冲区级别复现镜头的浅景深外观。

景深后处理在游戏引擎中的商业化应用可追溯至 2004 年 Valve 的《半条命 2》与 Epic Games 在 Unreal Engine 3（2006 年）中引入的 BokehDOF Pass。2012 年，Jorge Jimenez 等人在 SIGGRAPH 发表 "Practical Post-Process Depth of Field"，系统性地提出了基于半分辨率分层合成的实时 DoF 框架，此后成为主流引擎实现的参考基准（Jimenez et al., 2012）。Unreal Engine 5.0（2022 年）进一步将 DiaphragmDOF 系统迁移至 Temporal Super Resolution 管线，以 TAA 的帧间信息弥补单帧散景采样不足的问题。

景深效果的计算复杂度显著高于前置的 Bloom 泛光：Bloom 仅需对全图做固定方向的高斯分离卷积，而 DoF 的模糊核半径随深度连续变化，每像素的采样半径从 0 到最大 CoC（通常 32–64 像素）不等，这使得朴素实现的 ALU 开销与最大 CoC 的平方成正比。

---

## 核心原理

### 弥散圆（Circle of Confusion）的精确计算

CoC 半径的物理公式源自薄透镜模型，完整形式为：

$$
CoC = \left| \frac{A \cdot f \cdot (d - D)}{d \cdot (D - f)} \right|
$$

其中各变量的物理含义如下：
- $A$：光圈直径（mm），等于焦距除以光圈 F 值，即 $A = f / N$
- $f$：镜头焦距（mm），例如 50mm 标准镜、85mm 人像镜
- $d$：被摄物体到镜头的实际物距（mm）
- $D$：对焦距离，即摄影师主动对焦的锐焦平面距离（mm）

以具体数值为例：焦距 $f = 85\text{mm}$，光圈 $F/1.8$（即 $A \approx 47.2\text{mm}$），对焦距离 $D = 2000\text{mm}$（2 米），当背景物体位于 $d = 5000\text{mm}$（5 米）时：

$$
CoC = \left| \frac{47.2 \times 85 \times (5000 - 2000)}{5000 \times (2000 - 85)} \right| \approx \left| \frac{47.2 \times 85 \times 3000}{5000 \times 1915} \right| \approx 1.26\text{mm}
$$

在 35mm 全幅传感器（36mm × 24mm）、输出分辨率 1920×1080 的条件下，1.26mm 传感器尺寸对应约 67 像素的屏幕半径，这正是需要施加的模糊半径。

实时引擎通常以归一化值存储 CoC，将其压缩到 $[-1, 1]$：负值表示近景模糊区（Near Field），正值表示远景模糊区（Far Field），零值对应锐焦区域。Unity HDRP 将 CoC 编码进深度预处理 Pass 的 R 通道（16-bit float），并以 `_CoCTexture` 的形式传递给后续模糊 Pass。

### 散景（Bokeh）的光学形状与滤波核设计

"散景"一词来自日语「ボケ」（boke，模糊之意），指失焦区域的光斑外观。物理上，散景形状由光圈叶片数量决定：5 叶光圈产生五边形光斑，9 叶以上趋近于圆形。在实时渲染中，模拟不同散景形状的常见策略包括：

- **圆形采样核（Circular Disk Sampling）**：在以 CoC 半径为半径的圆盘内均匀或 Poisson 分布采样，每次 DoF Pass 需要 16–64 个样本点。Unreal Engine 4 的 CircleDOF 模式默认使用 **32 个样本**，分布在 3 个同心圆上（半径比为 1:2:3，样本数比为 8:12:12）。
- **多边形核（Polygonal Kernel）**：通过将采样点限制在正多边形区域内模拟刀片状光圈，可实现六角形或八角形散景，常见于 Assassin's Creed 系列的后处理管线。
- **分离式双圆核（Dual Kawase / Hexagonal Blur）**：Morgan McGuire 与 Padraic Hennessy（2018）在 GPU Pro 7 中提出的六边形散景实现，仅需 3 个方向性卷积 Pass 即可在接近 O(1) 的复杂度下逼近六角形散景，在主机平台（PS4/Xbox One）上将 DoF 开销控制在 0.8ms 以内。

### 分层合成策略：近景与远景的分离处理

Jimenez（2012）框架的核心贡献之一是将景深分为三层独立处理，避免近景模糊区的不透明散景光斑"污染"其背后清晰物体的边缘：

1. **远景层（Far Field）**：CoC > 0 的像素，降采样至半分辨率后做圆形卷积，再双线性上采样合成回全分辨率。
2. **近景层（Near Field）**：CoC < 0 的像素，需要额外的 Alpha 扩散（Alpha Spreading）步骤：先用膨胀滤波（Dilate Filter）将近景 CoC 扩展到邻域，防止近景物体边缘出现"锐利轮廓泄漏"伪影。
3. **锐焦层（In-Focus）**：直接输出原始颜色缓冲，与前两层按 CoC 权重混合。

最终合成公式为：

$$
C_{final} = \text{lerp}\bigl(C_{sharp},\ C_{far},\ w_{far}\bigr) + C_{near} \cdot \alpha_{near}
$$

其中 $w_{far} = \text{saturate}(CoC_{far})$，$\alpha_{near}$ 由近景层膨胀后的 CoC 绝对值导出。

---

## 关键算法：瓦片最大 CoC 预处理

朴素的逐像素可变模糊核开销过高，现代实现普遍采用"瓦片最大化（Tile Max）"预处理将开销降至可接受范围。具体流程如下：

```hlsl
// Pass 1: TileMax — 以 8x8 像素为一个 Tile，记录 Tile 内最大 CoC 半径
Texture2D<float> _CoCTexture;

[numthreads(8, 8, 1)]
void TileMaxCS(uint3 id : SV_DispatchThreadID)
{
    float maxCoC = 0.0;
    // 遍历 8x8 邻域，取最大绝对值 CoC
    for (int dy = -4; dy < 4; dy++)
    for (int dx = -4; dx < 4; dx++)
    {
        float2 uv = (id.xy + float2(dx, dy) + 0.5) * _TexelSize.xy;
        maxCoC = max(maxCoC, abs(_CoCTexture.SampleLevel(sampler_point, uv, 0)));
    }
    _TileMaxOutput[id.xy / 8] = maxCoC;
}

// Pass 2: NeighborMax — 在 Tile 图上再做 3x3 邻域最大值扩展
// 确保运动边界上的 Tile 获得足够大的采样半径
float neighborMax = 0.0;
for (int ny = -1; ny <= 1; ny++)
for (int nx = -1; nx <= 1; nx++)
    neighborMax = max(neighborMax, _TileMaxTexture[tileID + int2(nx, ny)]);
```

经过 TileMax 与 NeighborMax 两个 Compute Pass 之后，每个 8×8 像素块只需按照该块的最大 CoC 决定采样半径，避免在锐焦区域浪费采样，将整体 GPU 耗时相较朴素实现减少约 40–60%（视场景远近景分布而定）。

---

## 实际应用

### 游戏与影视中的典型参数配置

景深在不同应用场景中的参数差异极大：

- **第一人称射击（FPS）**：《使命召唤：现代战争》（2019）的近战瞄准镜景深使用极浅景深——焦距等效 200mm、$F/1.4$，背景 CoC 最大值设定为 48 像素（1080p），以强化"镜头感"并干扰玩家对背景细节的注意力。
- **角色扮演（RPG）**：《赛博朋克 2077》（CD Projekt RED，2020）的过场动画使用动态对焦（Auto Focus），根据对话角色的世界坐标实时更新对焦距离 $D$，焦深范围约 $\pm 0.8$ 米，等效模拟 35mm F/2.8 镜头特性。
- **实时电影渲染（Cinematic）**：Unreal Engine 5 的 Sequencer 中，DiaphragmDOF 支持直接输入以 mm 为单位的焦距（推荐 50–135mm）和真实 F 值（常用 $F/1.2$ 至 $F/2.8$），与物理相机参数一一对应，便于 VFX 团队与摄影指导协同工作。

### 性能优化：半分辨率渲染与时域累积

为将 1080p 的 DoF 开销控制在 2ms 以内，主流实现采用以下两级降本策略：

1. **半分辨率 DoF（Half-Resolution DoF）**：在 960×540 纹理上执行全部散景卷积，最后上采样回 1920×1080。由于人眼对失焦区域的高频细节不敏感，半分辨率引入的上采样伪影几乎不可察觉，但节省了 75% 的纹理采样带宽。
2. **时域散景积累（Temporal Bokeh Accumulation）**：每帧在圆盘采样核上随机旋转采样方向（旋转角度基于 Halton 序列的第 8 位），借助 TAA 将连续帧的散景样本在时域上累积，使等效采样数从单帧 32 个提升至时域 128 个以上，显著改善大 CoC 区域的颗粒感噪点。

---

## 常见误区

### 误区一：近景模糊不需要膨胀处理

许多初次实现 DoF 的渲染工程师只为远景层做模糊，直接将近景 CoC 像素同等处理。这会导致近景前景物体（如前景树枝、手持武器）边缘出现"深色光晕"——清晰背景像素渗入失焦前景的采样核，拉低了前景光斑的亮度。正确做法是在近景层卷积前执行 **CoC 膨胀（Dilate）**：以当前像素为中心，在 $5\times5$ 邻域内取 CoC 绝对值的最大值作为该像素的模糊半径，使近景边界的模糊自然向外扩展而非向内收缩。

### 误区二：将 CoC 直接存储为屏幕像素数

CoC 的物理单位是传感器平面上的长度（mm），转换为屏幕像素数时必须考虑**传感器分辨率映射比（pixels per mm）**。若直接将毫米值当作像素数传递给模糊 Pass，在低分辨率（如 720p）与高分辨率（如 4K）之间切换时散景大小会产生 4 倍差异，破坏艺术家预设的视觉意图。正确做法是将 CoC 归一化为传感器宽度的分数，再乘以当前渲染目标的宽度像素数：

$$
CoC_{pixels} = CoC_{mm} \times \frac{renderWidth}{sensorWidth_{mm}}
$$

例如，渲染宽度 1920px，传感器宽度 36mm，则比例系数为 $1920 / 36 \approx 53.3$，1.26mm 的物理 CoC 对应 $1.