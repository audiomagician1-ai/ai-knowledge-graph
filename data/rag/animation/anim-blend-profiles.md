---
id: "anim-blend-profiles"
concept: "混合曲线"
domain: "animation"
subdomain: "blend-space"
subdomain_name: "BlendSpace"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
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

# 混合曲线

## 概述

混合曲线（Blend Curve）是 BlendSpace 系统中控制动画权重在时间或空间轴上如何过渡的数学函数。当角色从行走动画过渡到跑步动画时，混合曲线决定了这个权重值是以恒定速率线性增加，还是先慢后快地加速过渡，或是按照设计师手动绘制的自定义形状变化。

BlendSpace 中的混合曲线概念源自于样条插值数学，Unreal Engine 在 UE4 时期将其正式暴露为可配置参数，允许美术和技术动画师为每个轴独立指定插值方式。这种设计让同一个 BlendSpace 资产中，水平轴（如速度）可以使用 Cubic 曲线，垂直轴（如倾斜角度）可以使用 Linear 曲线，互不干扰。

选择错误的混合曲线会直接导致动画"弹跳"或"停滞"的视觉瑕疵。例如对于速度轴使用纯 Linear 曲线时，角色在刚开始加速的瞬间不会有任何缓入效果，动作变化显得机械；而 Cubic 曲线的 S 形过渡则能模拟肌肉惯性，使动作衔接自然。

---

## 核心原理

### Linear（线性曲线）

Linear 混合曲线使用公式 **w = t**，其中 t 为归一化输入值（0.0 到 1.0），w 为输出权重。权重与输入值完全成正比，斜率恒为 1。这意味着在 BlendSpace 编辑器中，角色速度每增加 10% ，对应动画片段的混合权重也精确地增加 10%。Linear 曲线计算成本最低，适合速度与步幅之间本身就呈线性关系的情况，例如四足动物的小跑到飞奔过渡中的步幅拉伸。

### Cubic（三次曲线）

Cubic 混合曲线采用三次 Hermite 插值，标准 Ease-In/Ease-Out 变体的公式为 **w = 3t² - 2t³**。这条 S 形曲线在 t=0 和 t=1 两端的斜率均为 0，中间段斜率最大值约为 1.5，出现在 t=0.5 处。实际效果是权重变化在过渡起点和终点附近"缓入缓出"，消除了线性过渡的突兀感。在 UE5 的 BlendSpace 编辑器中，Cubic 是大多数轴的默认设置，因为它最接近真实的人体运动惯性曲线。

### Custom（自定义曲线）

Custom 混合曲线允许设计师通过 UE 的曲线编辑器（Curve Editor）手动放置关键帧，绘制任意形状的权重函数。一个典型用法是格斗游戏中的攻击收招动画：希望在输入值从 0 到 0.6 的区间内权重快速升至 0.9，然后在 0.6 到 1.0 区间内非常缓慢地从 0.9 过渡到 1.0，这种非对称的停顿感无法由 Linear 或标准 Cubic 实现，必须使用 Custom 曲线。Custom 曲线数据以 UCurveFloat 资产的形式存储，可在多个 BlendSpace 之间共享引用。

### 曲线对称性与轴向绑定

BlendSpace 的每条轴（X轴、Y轴）各自持有一个独立的混合曲线设置，互不继承。修改 X 轴的曲线类型不会影响 Y 轴。在 1D BlendSpace 中只有单轴曲线；在 2D BlendSpace 中，引擎在计算最终权重时先沿 X 轴对每列样本做插值，再沿 Y 轴对行做插值，两次插值各自使用对应轴的曲线函数。

---

## 实际应用

**第三人称角色移动**：设速度轴范围为 0–600 cm/s，对该轴使用 Cubic（`3t²-2t³`）曲线。当玩家按下摇杆到底后，前 0.2 秒内速度增量对应的混合权重增速非常慢（曲线斜率接近 0），随后快速追上目标，最终在接近最大速度时再次减缓。这个特性天然匹配了 UE CharacterMovementComponent 中 `MaxAcceleration` 造成的速度渐变，两者叠加使动画与物理表现高度一致，无需额外代码同步。

**瞄准偏移（Aim Offset）**：Aim Offset 本质上是一种特殊的 BlendSpace，其俯仰角（Pitch）和偏转角（Yaw）轴通常均使用 Linear 曲线，因为瞄准方向与骨骼旋转量之间需要 1:1 的精确线性映射——使用 Cubic 曲线会导致准心在屏幕中央附近的灵敏度偏低，玩家会感受到"粘滞感"。

**布料/尾巴摆动叠加**：对摆动幅度轴使用 Custom 曲线，在 0–0.3 区间内斜率设为 0（静止时无摆动），在 0.3–0.7 区间内斜率快速抬升（速度阈值触发摆动），模拟布料在低速时的静摩擦力效果。

---

## 常见误区

**误区一：认为 Cubic 曲线一定优于 Linear 曲线**。Cubic 的 S 形特性在需要"缓入缓出"时表现优异，但对于数值本身已经经过平滑处理的输入信号（如已带有插值的 IK 目标值），再叠加 Cubic 曲线会产生双重平滑，导致过渡时长感觉比设定值长 30%–50%，动画滞后感明显。此时 Linear 才是正确选择。

**误区二：以为修改混合曲线会改变 BlendSpace 的样本排列位置**。混合曲线仅影响在已有样本之间插值时的权重分配方式，不会移动任何样本点在编辑器网格上的坐标。很多初学者在看到动画过渡节奏变化后，误以为是样本位置偏移导致的，从而去调整样本坐标，反而破坏了 BlendSpace 的意图结构。

**误区三：在 Custom 曲线中将输出值设置超出 [0, 1] 范围**。BlendSpace 的权重规范化逻辑要求所有样本权重之和为 1.0。如果 Custom 曲线在某个 t 值处输出 1.3，引擎会将其钳制（Clamp）到 1.0 后再规范化，导致与预期完全不同的混合结果，且编辑器不会弹出任何警告。

---

## 知识关联

混合曲线的使用以**混合基础**为前提，需要理解 BlendSpace 中样本权重的含义以及归一化的机制，才能正确解读曲线输出值对动画混合结果的实际影响。掌握混合曲线后，设计师对 BlendSpace 轴参数的调控能力会从"移动样本点"这一粗粒度操作，扩展到"精确塑造过渡手感"的细粒度操作。对于需要在代码层面动态切换曲线类型的情况，可通过 `UBlendSpaceBase::SetBlendParameter` 配合自定义 `UCurveFloat` 资产在运行时替换曲线，实现基于游戏状态（如战斗/探索模式切换）的动态混合行为调整。