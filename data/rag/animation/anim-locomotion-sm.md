---
id: "anim-locomotion-sm"
concept: "移动状态机"
domain: "animation"
subdomain: "state-machine"
subdomain_name: "状态机"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 40.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.387
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 移动状态机

## 概述

移动状态机（Movement State Machine）是游戏角色动画系统中专门用于管理地面移动行为的有限状态机实现，包含 Idle（静止）、Walk（行走）、Run（跑步）、Sprint（冲刺）四个核心状态及其之间的转换逻辑。这四个状态以角色速度值为主要驱动参数，形成一张有向图，每条边代表一个速度阈值触发的状态转换条件。

移动状态机的概念随着 3D 游戏动画技术的发展而成熟，在 2000 年代中期被 Unreal Engine 3 的 AnimTree 系统正式引入引擎级工具链，此后成为几乎所有商业游戏引擎（UE4/5 的 AnimGraph、Unity 的 Animator Controller）中角色动画的标准起点。它之所以重要，是因为人类行走和奔跑的姿态差异显著，如果不通过状态机明确区分这四种运动模式，动画混合就会在速度连续变化时产生明显的滑步或肢体抖动，严重影响游戏表现力。

与通用状态机不同，移动状态机的特殊性在于它的状态数量少但转换频率极高——一名玩家在 10 分钟内可能触发数百次 Walk↔Run 转换，因此每条转换边的触发时机（如速度滞后带设计）直接影响动画观感。

## 核心原理

### 四状态结构与速度阈值

标准移动状态机的四个状态对应四段速度区间，典型数值如下：

- **Idle**：速度 = 0 cm/s，播放静止待机循环动画
- **Walk**：速度 0 ~ 180 cm/s，播放行走循环动画
- **Run**：速度 181 ~ 400 cm/s，播放跑步循环动画
- **Sprint**：速度 > 400 cm/s，播放冲刺循环动画（通常需要额外的"冲刺输入"布尔值作为第二条件）

这些阈值并非固定标准，但 UE5 第三人称模板使用 150/300 cm/s 双阈值作为参考，开发者需根据具体角色胶囊体半径和摄像机视野调整。

### 转换条件与迟滞带（Hysteresis）

若从 Walk 进入 Run 和从 Run 返回 Walk 使用相同的速度阈值（如 180 cm/s），当角色速度在 178~182 cm/s 之间波动时，状态机会在两个状态之间每帧反复横跳，导致动画剧烈抖动。解决方案是为每条转换边设置不对称阈值，例如：

- Walk → Run 触发条件：速度 ≥ **190** cm/s
- Run → Walk 触发条件：速度 ≤ **160** cm/s

这个 30 cm/s 的迟滞带（Dead Zone）确保状态切换具有稳定性。在 Unity Animator 中，可通过为 Trigger 参数添加 `Has Exit Time` 并设置最短持续时间（如 0.1 秒）实现类似效果。

### 状态转换图的拓扑结构

移动状态机的转换图并非全连接图。标准设计中，状态只能向相邻速度级别迁移（Idle↔Walk↔Run↔Sprint），**禁止跳跃式转换**（如 Idle 直接跳到 Sprint）。这一约束的原因是动画连续性：如果角色从静止直接进入冲刺动画，缺少中间过渡帧会造成肢体突变。实现上，这意味着状态图中只需维护 6 条转换边（每对相邻状态各 2 条双向边），而非 12 条全连接边。

Sprint 状态通常还要求满足复合条件：`速度 > 400 AND bSprintInput == true`，防止角色被外力弹飞时误触冲刺动画。

### 动画混合时间

每条转换边需要设置混合时长（Blend Duration），典型值：

- Idle → Walk：0.2 秒（慢启动感）
- Walk → Run：0.15 秒
- Run → Sprint：0.1 秒（越快越要干脆）
- 任意 → Idle：0.3 秒（减速需要更多缓冲时间）

混合时长过短会产生突兀感，过长则让角色响应迟钝。

## 实际应用

**UE5 第三人称项目**：在 AnimGraph 中创建状态机节点，添加四个状态并引用对应的动画序列资产（`MM_Idle`、`MM_Walk`、`MM_Jog`、`MM_Sprint`）。在每条转换规则中引用 `Speed` 浮点变量，该变量由 AnimInstance 的 `NativeUpdateAnimation` 函数每帧从 `CharacterMovementComponent` 读取角色速度向量的长度（`GetVelocity().Size()`）。

**Unity 人形角色**：在 Animator Controller 中用 `Speed` Float 参数驱动四状态图，配合 `SetFloat("Speed", rb.velocity.magnitude)` 每帧更新。Unity 的 Blend Tree 可以进一步将 Walk 和 Run 合并为一个混合节点，由速度值在 0~1 范围内插值，但这属于对基础移动状态机的优化扩展。

**手机游戏优化**：在低端设备上，常将移动状态机简化为三状态（合并 Run 和 Sprint），并将转换检测频率降低到每 3 帧检测一次，以减少动画系统 CPU 开销。

## 常见误区

**误区一：将移动方向与移动速度混入同一个状态机**

初学者经常把前进、后退、左右移动做成 Idle/Walk\_Forward/Walk\_Backward/Walk\_Left/Walk\_Right 等多达十几个状态。正确做法是将移动方向交给 2D 混合树（Blend Space 2D）处理，移动状态机只负责速度级别的切换。把方向状态堆入移动状态机会使转换边数量爆炸式增长（10 个方向 × 4 个速度 = 40 个状态，780 条潜在转换边）。

**误区二：Sprint 状态仅用速度阈值触发**

纯速度驱动的 Sprint 状态会在角色被击飞、从斜面滑落时意外激活冲刺动画。Sprint 必须同时检测玩家的显式输入（如 Shift 键或手柄左摇杆完全推满），速度只是充要条件的一半。

**误区三：所有转换边使用相同的混合时间**

移动状态机中加速和减速的体感不对称——人类加速快、减速慢。将 Idle→Walk 和 Walk→Idle 设置为相同的 0.15 秒混合时间，会让角色刹车感觉过于机械。减速方向的混合时间通常应比加速方向长 30%~50%。

## 知识关联

移动状态机建立在**状态转换**的基础概念之上——转换条件、转换优先级、进入/退出通知（Enter/Exit Notify）都是前置知识，在移动状态机中以速度阈值和混合时间的具体形式体现出来。

掌握移动状态机后，下一步自然延伸到**战斗状态机**：战斗状态机需要与移动状态机并行运行（角色可以边走边攻击），这引出了多层状态机的架构问题。**子状态机**则将 Sprint 的起跳、加速、全速、减速细分为嵌套状态，使冲刺动画表现更丰富。**参数化状态**在移动状态机中的直接应用是用同一个 Run 状态通过速度参数混合不同步幅的跑步动画，而非为每种步幅单独建一个状态。学习**状态机调试**时，移动状态机的高频转换特性使它成为最理想的调试练习对象，可以在编辑器的状态机可视化窗口中实时观察四个状态的激活和切换。
