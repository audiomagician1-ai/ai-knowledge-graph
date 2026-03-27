---
id: "anim-2d-blend"
concept: "2D BlendSpace"
domain: "animation"
subdomain: "blend-space"
subdomain_name: "BlendSpace"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 2D BlendSpace

## 概述

2D BlendSpace 是虚幻引擎（Unreal Engine）动画系统中的一种资产类型，允许动画师在一个二维坐标平面内放置多个动画片段，并通过两个独立的浮点参数同时驱动这些动画之间的混合。与1D BlendSpace只能沿单一轴线插值不同，2D BlendSpace 可以在X轴和Y轴构成的平面上进行双线性插值（Bilinear Interpolation），使角色动画能够响应两个同时变化的运动状态。

2D BlendSpace 最经典的应用场景是八方向移动动画系统，早在虚幻引擎3时代便已作为 AnimTree 节点的一部分存在，UE4 将其独立为专属资产类型（扩展名 `.bs2d`，后统一为 `.bs`）。这一设计允许游戏角色在速度（Speed）和方向（Direction）两个维度上同时驱动不同的行走、奔跑及对角移动动画，而不需要手动编写任何插值代码。

在第三人称动作游戏和射击游戏中，角色需要向前、向后、向左、向右以及四个对角方向移动，单凭1D BlendSpace 无法在保持速度变化的同时区分移动方向。2D BlendSpace 通过同时采样这两个维度，使得"向右慢走"与"向右奔跑"分别对应坐标平面上不同位置的动画采样点，插值结果自然流畅。

---

## 核心原理

### 双线性插值与三角剖分

2D BlendSpace 在编辑器内部对所有动画采样点进行 **Delaunay 三角剖分**，将二维坐标平面划分为若干三角形区域。运行时，当输入参数（如 `Speed=250, Direction=45`）落入某个三角形内，引擎计算该点相对于三角形三个顶点的重心坐标（Barycentric Coordinates），然后以此权重对三个顶点处的动画片段进行加权混合。这意味着**最多同时混合3个动画**，而非坐标平面上所有放置的动画。

混合权重公式如下：若输入点 P 落在由采样点 A、B、C 构成的三角形内，则：

$$\text{权重}_A + \text{权重}_B + \text{权重}_C = 1.0$$

其中每个权重通过解线性方程组由重心坐标得出，保证总权重归一化。

### 两个输入轴的设置

2D BlendSpace 的 X 轴和 Y 轴各自独立配置，每个轴需要设定最小值、最大值，以及网格分辨率（Grid Divisions）。例如，在八方向移动的标准设置中：
- **X 轴（Direction）**：范围 `-180` 到 `180`（度），表示角色移动方向与朝向的夹角；
- **Y 轴（Speed）**：范围 `0` 到 `600`（厘米/秒），对应从静止到全速奔跑的速度区间。

每个轴还有独立的 **Snap to Grid** 选项和 **插值速度（Interpolation Speed）** 参数，后者控制输入参数变化时坐标在平面内移动的平滑程度，防止动画突变。

### 采样点布局与覆盖规则

在 2D 平面上放置采样点时，Delaunay 三角剖分要求点的分布尽量均匀，避免出现长细三角形（Sliver Triangles）。实践中，八方向移动的标准采样点布局为：
- 中心点（`Direction=0, Speed=0`）：Idle 动画；
- 外圈8个方向 × 至少2个速度层级（Walk 和 Run）= 16个动画采样点；
- 外加可选的中速圈（Jog）= 8个额外采样点。

若某个区域内缺少采样点导致三角剖分覆盖不完全，该区域的输入将被**钳制（Clamp）**到最近的有效三角形边界，而不会插值到空白区域，这是2D BlendSpace 区别于某些自定义插值方案的重要行为。

---

## 实际应用

**TPS八方向移动**：在第三人称射击游戏（如《战争机器》风格的掩体系统）中，将角色的 `Velocity Direction`（通过 `CalculateDirection` 节点从速度向量转换为-180°到180°的角度）输入 X 轴，将速度标量输入 Y 轴。中心放置 Idle，外圈按间隔45°分别放置 Forward Walk、Forward Run、Right Walk、Right Run 等动画，即可实现流畅的八方向移动混合。

**马匹或载具步态过渡**：将步态频率（Gait Frequency）设为 Y 轴，地面倾斜角（Slope Angle）设为 X 轴，驱动马匹在上坡慢走与下坡小跑之间的姿态自然过渡，这是2D BlendSpace 在非人形角色上的典型应用。

**UE5 实际操作步骤**：在 Content Browser 右键 → Animation → BlendSpace，打开编辑器后在 Asset Details 面板中分别设置 Horizontal Axis 和 Vertical Axis 的参数范围，然后将动画序列从 Asset Browser 拖入坐标格网中对应位置，预览窗口的绿色十字准心即代表当前输入坐标位置。

---

## 常见误区

**误区1：认为所有采样点都会同时参与混合**
初学者常误以为坐标平面上放置越多动画，混合效果越细腻，但实际上由于 Delaunay 三角剖分的特性，任意时刻只有当前三角形的**3个顶点动画**参与插值。放置过多密集的采样点只会造成每个三角形面积过小，导致动画切换过快、失去过渡感，而不会提升混合质量。

**误区2：混淆 Direction 角度的坐标系来源**
`CalculateDirection` 函数返回的是角色速度向量相对于角色**自身朝向**的偏转角，而不是世界坐标系角度。若将角色的绝对速度方向直接输入2D BlendSpace，会导致角色转身时动画对应关系错乱，Forward Walk 动画反而在侧身时播放。

**误区3：忽视两个轴插值速度的独立配置**
Speed 轴和 Direction 轴的数值变化特征截然不同：Speed 通常渐进变化（加速/减速），而 Direction 可能瞬间大幅跳变（急转弯）。若将两个轴的 Interpolation Speed 设置为相同数值，Direction 过度平滑会导致急转弯时角色脚步动画方向明显滞后于视觉朝向，建议 Direction 轴的插值速度设置为Speed轴的3倍以上。

---

## 知识关联

**前置概念——1D BlendSpace**：1D BlendSpace 只在单轴上插值，仅能处理"速度"或"方向"其中之一，无法同时响应两个独立参数。2D BlendSpace 在其基础上增加了第二个输入维度，并引入 Delaunay 三角剖分代替简单的线性插值，采样点的布局策略也从一维排列升级为二维平面设计，这是两者在技术层面的本质差异。

**后续概念——混合树（Blend Tree / AnimGraph）**：2D BlendSpace 本身是单一资产，在 AnimGraph 中作为一个节点存在。混合树允许将多个 BlendSpace 输出结果通过条件逻辑（状态机、Blend Poses by Bool等）进一步组合，例如在地面移动2D BlendSpace 与游泳循环动画之间根据环境状态切换。

**后续概念——Aim Offset**：Aim Offset 本质上是一种特殊的 2D BlendSpace，其 X 轴为水平瞄准偏移角（Yaw，通常 `-90` 到 `90`），Y 轴为垂直瞄准偏移角（Pitch），但它输出的是**叠加姿势（Additive Pose）**而非完整动画，专门用于驱动角色上半身的瞄准方向，与移动用的2D BlendSpace形成功能互补。

**后续概念——混合遮罩（Blend Mask）与 Motion Matching**：当2D BlendSpace 控制下半身移动的同时，混合遮罩可以将上半身骨骼排除在外，使瞄准动画叠加不受移动混合影响。Motion Matching 则从另一个方向超越了 BlendSpace 的手动采样点布局模式，通过运动数据库自动选帧，但在低预算项目或需要精确控制的情形下，2D BlendSpace 仍是首选的高效解决方案。