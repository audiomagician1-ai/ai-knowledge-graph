---
id: "anim-1d-blend"
concept: "1D BlendSpace"
domain: "animation"
subdomain: "blend-space"
subdomain_name: "BlendSpace"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 1D BlendSpace（一维混合空间）

## 概述

1D BlendSpace 是虚幻引擎（Unreal Engine）动画系统中的一种资产类型，允许开发者沿**单条数轴**对两个或多个动画片段进行插值混合，输出一个随参数连续变化的合成姿势。它只接受一个浮点数作为驱动变量（通常命名为 `Speed`），并根据该值在预设的采样点之间自动计算各动画的权重。

1D BlendSpace 最早随虚幻引擎 4 的动画蓝图系统一同发布（约 2014 年），用来解决在固定动画片段之间生硬切换的问题。在此之前，开发者只能用状态机做离散跳转，导致角色从步行瞬间切至跑步时出现明显的动作抽搐（popping）。1D BlendSpace 将这一离散跳转转化为连续插值，消除了帧间穿帮。

在运动系统中，速度是驱动 1D BlendSpace 最典型的参数：将 `Idle`（0 cm/s）、`Walk`（150 cm/s）、`Run`（600 cm/s）三个动画放置在同一条轴上，当角色速度为 300 cm/s 时，系统自动以 50% Walk + 50% Run 的权重输出混合姿势，无需任何额外代码。

---

## 核心原理

### 采样点与轴范围设置

创建 1D BlendSpace 后，必须在 **Axis Settings** 面板中定义轴的最小值（Minimum Axis Value）和最大值（Maximum Axis Value），以及网格分辨率（Grid Divisions）。例如，速度轴常设置为 0–600，Grid Divisions 设为 4，则引擎在轴上每隔 150 单位预计算一次采样权重。采样点（Sample Point）是手动拖入编辑器的动画序列，每个采样点绑定一个轴坐标值；若采样点坐标为 0、150、600，引擎会在相邻两点之间进行**线性插值（Lerp）**：

$$
\text{Output Pose} = \text{Pose}_A \times (1 - t) + \text{Pose}_B \times t
$$

其中 $t = \dfrac{V - V_A}{V_B - V_A}$，$V$ 为当前输入值，$V_A$、$V_B$ 为相邻采样点坐标。

### 平滑插值与目标权重插值速度

1D BlendSpace 内置 **Target Weight Interpolation Speed Per Second** 参数（默认为 0，表示瞬时跳变）。将其设为 5.0 意味着权重每秒最多变化 5 个单位，相当于对输入值施加了一阶低通滤波。这与在蓝图中手动用 `FInterp To` 平滑速度变量不同——BlendSpace 的平滑作用于**动画权重**本身，即使输入参数突变，输出姿势仍会缓慢过渡，防止角色在加速瞬间出现骨骼抖动。

### 循环与脚步同步

1D BlendSpace 的每个采样点动画应设置为**循环（Loop）**，否则当角色持续移动时动画会在末帧冻结。更关键的是：Walk 动画与 Run 动画的**步幅节奏**必须对齐——如果 Walk 动画周期为 0.8 秒而 Run 为 0.6 秒，混合中间值时左右脚会出现相位错位，角色看起来像在拖行。解决方法是配合**同步组（Sync Group）**将两个动画钉在同一相位，但该功能属于独立话题，将在后续章节介绍。

---

## 实际应用

**角色移动速度驱动（Walk→Jog→Run）**
在第三人称模板中，动画蓝图的 EventGraph 每帧通过 `GetVelocity → VectorLength` 获取角色速度，将结果传入 1D BlendSpace 的 `Speed` 参数。采样点配置示例：

| 轴坐标（cm/s） | 动画片段         |
|--------------|----------------|
| 0            | Idle           |
| 175          | Walk           |
| 375          | Jog            |
| 600          | Run            |

当玩家按下冲刺键使速度从 375 升至 600，BlendSpace 在约 0.2 秒内（取决于 Target Weight Interpolation Speed）完成 Jog→Run 的平滑融合。

**武器持握状态下的移动层**
在 Additive 层动画结构中，1D BlendSpace 常单独负责下半身移动，上半身叠加瞄准姿势。此时 1D BlendSpace 采样点只包含腰部以下的 Walk/Run 骨骼动画，通过 **Blend Poses by Bool** 节点与非武装状态的混合空间切换，避免维护两套完整角色动画。

---

## 常见误区

**误区一：采样点越多越平滑**
增加采样点并非总是改善混合效果。若在 0–600 的轴上添加 10 个采样点，但相邻动画在艺术上差异极小，插值结果与 3 个采样点几乎无法区分，却增加了内存占用和维护成本。实测中，速度轴通常 3–4 个采样点已足够；过多采样点反而会因相邻动画根骨骼偏移不一致而产生轻微抖动。

**误区二：Target Weight Interpolation Speed 可以替代骨骼平滑**
该参数只平滑**混合权重的变化速率**，不修改单个动画片段内部的骨骼轨迹。如果 Run 动画本身的根骨骼在第一帧存在偏移，权重平滑无法消除该偏移带来的瞬移。根骨骼问题需要在 DCC 工具（如 Maya、Blender）中修正动画数据本身。

**误区三：1D BlendSpace 可以直接处理方向混合**
1D BlendSpace 只有一条轴，无法同时表达速度和方向（前进/后退/左移/右移）。若在单轴上依次放置 Forward Walk、Strafe Walk、Backward Walk，混合结果会将三个方向的骨骼姿势线性叠加，产生错误的躯干旋转。方向混合必须使用 2D BlendSpace，以速度和方向角各占一轴。

---

## 知识关联

**前置概念——混合基础**：理解骨骼姿势插值（Pose Lerp）和动画权重归一化是读懂上文公式 $t = (V - V_A)/(V_B - V_A)$ 的必要条件；混合基础章节解释了为何所有采样点权重之和必须等于 1.0。

**后续概念——2D BlendSpace**：1D BlendSpace 是 2D BlendSpace 的子集——2D 版本在水平轴放速度、垂直轴放方向角，可视为两条正交的 1D 轴联合求解双线性插值。掌握 1D 版本的采样点布局和 Target Weight 参数后，迁移至 2D 版本时只需额外学习三角形剖分（Delaunay Triangulation）权重求解逻辑。

**后续概念——同步组**：1D BlendSpace 的脚步相位错位问题直接引出同步组的应用场景——同步组通过将 Walk 和 Run 归入同一 Group Name（如 `LocoGroup`），强制两者共享归一化的播放位置（0.0–1.0），从而消除混合时的步伐相位差。

**后续概念——步幅调整（Stride Warping）**：步幅调整是 1D BlendSpace 的进阶替代方案之一。它允许只保留单一速度的步行动画，通过在运行时拉伸腿部骨骼来匹配任意速度，减少对多个离散采样点的依赖，适用于需要精确脚步接地的 AAA 级项目。