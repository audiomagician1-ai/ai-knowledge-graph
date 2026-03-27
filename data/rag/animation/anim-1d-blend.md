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
quality_tier: "pending-rescore"
quality_score: 44.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
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

1D BlendSpace 是虚幻引擎（Unreal Engine）动画系统中的一种资产类型，允许开发者沿**单一数值轴**对多个动画片段进行权重混合。与直接在动画蓝图中写死动画状态不同，1D BlendSpace 接收一个浮点参数（如角色移动速度），并根据该参数值在预设的动画样本点之间自动插值，输出平滑过渡的姿态。

该功能自 UE4 引入，资产文件扩展名为 `.uasset`，在编辑器中通过 **Content Browser → 右键 → Animation → BlendSpace 1D** 创建。其核心价值在于用一条轴替代多个硬切换的状态机转换，使 Walk→Jog→Run 等连续运动状态的过渡自然流畅，而无需手工编写插值逻辑。

对于移动速度驱动的角色动画，1D BlendSpace 是最直接的解决方案：开发者只需将角色的 `Speed`（单位：cm/s）值传入，系统便自动计算每帧应混合的比例，大幅降低动画蓝图的节点复杂度。

---

## 核心原理

### 轴定义与样本点布局

创建 1D BlendSpace 后，首先需要在 **Asset Details** 面板中设置水平轴（Horizontal Axis）的参数名称、最小值与最大值。典型的速度轴设置为：

- **Axis Name**：`Speed`
- **Minimum Axis Value**：`0`（站立/Idle）
- **Maximum Axis Value**：`600`（全速奔跑/Run）

在轴上放置**样本点（Sample Points）**，每个样本点绑定一条动画序列。最简配置为三点：
- `0 cm/s` → Idle 动画
- `250 cm/s` → Walk 动画
- `600 cm/s` → Run 动画

样本点数量没有硬性上限，但通常 3–5 个已足够覆盖大多数移动状态。

### 线性插值计算方式

当输入参数值落在两个样本点之间时，引擎执行**线性插值（Lerp）**：

$$
\text{Output Pose} = (1 - t) \times \text{Pose}_A + t \times \text{Pose}_B
$$

其中 $t = \dfrac{v - v_A}{v_B - v_A}$，$v$ 为当前输入值，$v_A$ 和 $v_B$ 分别为相邻两个样本点的轴坐标值。

例如，当 `Speed = 400` 时，处于 Walk（250）和 Run（600）之间：$t = (400 - 250) / (600 - 250) \approx 0.43$，即以 57% Walk + 43% Run 的比例混合姿态。

### 平滑插值与目标权重插值

1D BlendSpace 提供 **Target Weight Interpolation Speed Per Second** 参数（默认值通常为 `0`，表示关闭）。当该值设为正数（如 `5`）时，输入参数的变化会被平滑处理，避免玩家突然松开移动键时动画跳变。该平滑作用于**权重层面**而非参数本身，因此与角色控制器中的速度平滑是两个独立机制，两者叠加可能造成过度滞后，需谨慎调节。

---

## 实际应用

### 速度驱动 Walk→Run 渐变

在第三人称角色项目中，标准做法是：

1. 在动画蓝图的 **Event Graph** 中，每帧获取角色速度向量的长度：`Speed = GetVelocity().Size()`；
2. 将 `Speed` 存入动画蓝图变量；
3. 在 **AnimGraph** 中拖入 1D BlendSpace 节点，将 `Speed` 变量连接到其输入引脚。

这样当玩家轻推摇杆（速度约 150 cm/s）时，输出姿态为 Walk 与 Idle 之间的混合，推满摇杆（600 cm/s）时完全播放 Run 动画，过渡全程无缝。

### 武器持握状态下的移动动画

同一套移动速度轴可用于持枪行走场景：将 Idle_Rifle、Walk_Rifle、Run_Rifle 三条动画以相同轴坐标（0 / 250 / 600）放置在另一个 1D BlendSpace 中。结合动画蓝图的状态机，在"武器未装备"与"武器装备"之间切换使用不同的 BlendSpace 资产，即可实现两套移动表现的分离管理。

---

## 常见误区

### 误区一：将平滑参数与控制器速度平滑混为一谈

许多初学者同时在角色移动组件中开启 `Braking Deceleration` 减速，又在 BlendSpace 中设置较高的 Target Weight Interpolation 值。两层平滑叠加导致角色停步后动画仍持续走动超过 0.5 秒，用户体验明显滞后。正确做法是**只选其一**：要么让移动速度本身平滑变化（BlendSpace 插值速度保持 0），要么让速度硬切但由 BlendSpace 平滑动画权重。

### 误区二：样本点间距不均匀导致过渡不自然

若将三个样本点设为 0 / 50 / 600，则速度从 0 到 50 的极小范围内已完成 Idle→Walk 的全部过渡，而从 50 到 600 的漫长区间内 Walk 权重从 100% 缓慢降至 0%，视觉上 Walk 动画会持续"拖尾"很久。样本点应按**感知均匀**或实际游戏速度段分布，而非随意摆放。

### 误区三：将 1D BlendSpace 用于需要方向信息的场景

1D BlendSpace 只有单轴，无法同时编码速度与方向。当需要区分前进、后退、侧步时，单轴 Speed 变量会导致所有方向播放同一套混合动画。此类场景必须升级至 **2D BlendSpace**，以 Speed 和 Direction（-180°～180°）作为双轴输入。

---

## 知识关联

**前置概念——混合基础**：理解姿态插值（Pose Lerp）和动画权重（0.0–1.0 范围）是读懂 BlendSpace 插值公式的前提。混合基础中讲解的 `Blend Poses by Bool` 节点实质上是 BlendSpace 的特殊二值情形（t 只取 0 或 1）。

**后续概念——2D BlendSpace**：在 1D BlendSpace 掌握单轴样本布局之后，2D BlendSpace 增加垂直轴（通常为 Direction），形成二维网格采样，混合计算从线性插值扩展为**双线性插值（Bilinear Interpolation）**，需要同时管理两个输入变量的范围与样本密度。

**后续概念——同步组（Sync Group）**：当 1D BlendSpace 中的 Walk 与 Run 动画周期不同（例如 Walk 为 0.8s/步，Run 为 0.5s/步）时，直接混合会导致脚步相位错位。同步组通过指定 Leader/Follower 角色，强制多条动画在混合时对齐关键帧，是 BlendSpace 在实际项目中必须搭配使用的机制。

**后续概念——步幅调整（Stride Warping）**：1D BlendSpace 解决了动画过渡的视觉平滑问题，但动画实际步幅与角色真实移动速度仍可能存在滑步（foot sliding）偏差。步幅调整通过程序化缩放腿部骨骼运动范围来匹配实时速度，是对 BlendSpace 速度驱动方案的精度补充。