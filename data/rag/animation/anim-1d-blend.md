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
---
# 1D BlendSpace（一维混合空间）

## 概述

1D BlendSpace 是 Unreal Engine 动画系统中的一种资产类型，允许开发者沿**单一数值轴**对多个动画片段进行加权混合。与直接切换动画剪辑不同，1D BlendSpace 根据一个浮点参数（如角色移动速度）计算相邻动画之间的插值权重，从而输出一段平滑过渡的混合姿势。该资产在 Unreal Engine 内容浏览器中以 `.uasset` 格式保存，扩展名显示为 **BlendSpace1D**。

1D BlendSpace 最典型的应用场景是速度驱动的步态过渡：将 Idle（静止，0 cm/s）、Walk（行走，150 cm/s）、Run（奔跑，400 cm/s）三段动画挂载到同一条水平轴上，当速度参数从 0 线性增加到 400 时，引擎自动在相邻两段动画之间做线性插值，角色的腿部迈步频率与幅度随之连续变化，避免了"瞬切"造成的视觉跳帧。

与完整的 2D BlendSpace 相比，1D BlendSpace 只管理一个自变量轴，资产配置更简单，采样点呈一字排列，运行时混合计算量更小，适合只需单一驱动参数的角色运动场景。

---

## 核心原理

### 采样点与轴范围配置

在 1D BlendSpace 编辑器中，开发者需要首先设置轴（Axis）的参数名称、最小值和最大值。以速度轴为例，通常将 **Horizontal Axis** 命名为 `Speed`，范围设为 `0` 到 `600`（单位：cm/s）。然后在轴上放置若干**采样点（Sample Point）**，每个采样点绑定一个动画序列（Animation Sequence）并指定其对应的轴值，例如：

| 轴值（cm/s） | 绑定动画 |
|---|---|
| 0 | Idle |
| 150 | Walk |
| 400 | Run |
| 600 | Sprint |

当运行时传入的 `Speed` 值落在两个采样点之间时，引擎对两侧的采样动画按**线性插值**计算每块骨骼的旋转四元数与位置，混合权重公式为：

$$w_{\text{left}} = \frac{v_{\text{right}} - v}{v_{\text{right}} - v_{\text{left}}}, \quad w_{\text{right}} = 1 - w_{\text{left}}$$

其中 $v$ 为当前参数值，$v_{\text{left}}$ 与 $v_{\text{right}}$ 分别为相邻左右采样点的轴值。

### 平滑时间与插值惰性

1D BlendSpace 提供 **Target Weight Interpolation Speed** 参数，默认值通常为 `0`（即不做额外惰性平滑，直接跟随输入值）。若将该值设为 `5`，则混合权重以每秒最多改变 5 单位的速率向目标权重逼近，使角色在急停时不会瞬间切回 Idle 动画，而是在约 0.2 秒内完成过渡。这与动画蓝图节点层面的 `Blend`节点不同——BlendSpace 的平滑作用在参数空间而非姿势空间完成。

### 动画同步与帧对齐

当 Walk 与 Run 两段动画的**步幅周期长度**不同时（例如 Walk 循环 60 帧、Run 循环 40 帧），混合区间内双脚的触地时机可能错位，产生"滑步"感。Unreal Engine 通过在 BlendSpace 内启用**同步组（Sync Group）**来解决此问题：将两段动画设为相同的同步组名称后，引擎按混合权重对各动画的规范化播放时间做加权平均，使两段动画的步态相位始终对齐。具体机制在后续"同步组"章节展开，但同步行为本身在 1D BlendSpace 资产的属性面板中通过 **Sync Group Name** 字段直接配置。

---

## 实际应用

### 第三人称角色移动步态

在标准第三人称模板中，动画蓝图的 AnimGraph 将角色的地面速度（Ground Speed，通过 `TryGetPawnOwner → GetVelocity → VectorLength` 计算得到 cm/s 浮点值）驱动一个 1D BlendSpace。该 BlendSpace 挂载 Idle（0）、Walk（150）、Run（500）三段动画，速度从静止加速到奔跑的整个过程中步态连续渐变，无需任何状态机切换逻辑介入。

### 面部表情强度控制

1D BlendSpace 并不局限于腿部运动。可将 `Neutral` 面部动画置于轴值 `0`，`HappyFull` 面部动画置于轴值 `1`，用一个 `EmotionIntensity` 参数（范围 0–1）驱动面部骨骼的混合，实现高兴表情从无到满的连续变化，而不必手动在两段 MorphTarget 之间做蓝图插值。

### 武器后坐力动画叠加

将轻微后坐力（轴值 0.3）与强烈后坐力（轴值 1.0）动画置于同一 1D BlendSpace，用射击冲量值驱动，再以 **Additive** 模式叠加到基础瞄准姿势上，可在不增加状态机状态数量的情况下表达连续强度的后坐力响应。

---

## 常见误区

### 误区一：采样点可以任意稀疏放置

有些开发者只在 0 和 500 两个极端值放置采样点，期望中间过渡"自然"产生。实际上 1D BlendSpace 仅做相邻采样点之间的**线性**插值，如果步态在某速度段（如 200–350 cm/s）有明显的动作风格变化而缺少中间采样点，混合结果将呈现机械的线性姿势叠加，而非自然的中速步态外观。正确做法是在动作变化明显的速度区间补充独立的 Walk_Fast 采样点。

### 误区二：Target Weight Interpolation Speed 越大越平滑

该参数的含义是"权重每秒变化的最大速率"，数值越大意味着权重跟随输入的速度越快，而非越慢。若将其设为 `20`，则权重几乎立即跟上输入，与设为 `0` 的效果几乎无差别。想要获得缓慢的平滑过渡，应将该值设为 `2`–`6` 之间的较小数值。

### 误区三：1D BlendSpace 等同于动画蓝图中的 Lerp 节点

`Lerp (Poses)` 节点只能在两段固定动画之间混合，且混合比例需手动在蓝图中计算。1D BlendSpace 支持**任意数量**的采样点，自动处理区间定位与权重计算，并原生支持同步组对齐，是面向多采样点连续混合的专用资产，而非蓝图姿势节点的简单替代。

---

## 知识关联

学习 1D BlendSpace 需要先掌握**混合基础**中的姿势插值概念（骨骼旋转四元数球面线性插值 SLERP）以及 Unreal Engine 动画蓝图的 AnimGraph 工作流——这两项知识决定了 BlendSpace 节点的输出数据类型（Pose）和参数传递方式（蓝图变量 → AnimGraph 节点引脚）。

在掌握 1D BlendSpace 之后，**2D BlendSpace** 将在此基础上引入第二根独立轴（例如同时控制速度与方向偏移），采样点从一字排列扩展为二维网格，混合权重从两点线性插值升级为三角重心坐标插值，复杂度显著上升。**同步组**则专门解决本文第三小节提到的多采样点步态相位对齐问题，是 1D BlendSpace 实战中必然遇到的配套机制。**步幅调整（Stride Warping）**进一步在 1D BlendSpace 输出的混合姿势之上，根据实际地面速度实时拉伸骨骼步幅，从根本上消除低速或超速时脚步滑动的残留问题。
