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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 移动状态机

## 概述

移动状态机是专门用于控制角色行走、跑步等位移动作的有限状态机结构，其最基础的形式由四个离散状态构成：Idle（静止）、Walk（行走）、Run（跑步）、Sprint（冲刺）。每个状态对应角色骨骼网格体上播放的一段特定动画片段，状态之间通过速度阈值或玩家输入信号触发转换。与随意堆叠动画剪辑相比，移动状态机保证了任意时刻角色只处于一种明确的移动语义状态，从而避免了动画混乱叠加的问题。

移动状态机的概念伴随着游戏引擎的成熟而逐步规范化。早在1990年代，《波斯王子》（Prince of Persia，1989）的开发者Jordan Mechner便通过手工编写状态逻辑来管理角色的行走与跳跃切换，这是移动状态机思想的早期体现。到2005年前后，Unreal Engine 3引入AnimTree，Unity 4.0于2012年推出Mecanim系统，才将可视化移动状态机编辑器带入主流工作流，使设计师无需编写代码即可配置Idle→Walk→Run→Sprint的完整转换图。

移动状态机之所以是角色动画系统的起点，在于几乎所有可操控角色都面临"静止时播站立循环、移动时播行走/跑步循环"的基本需求。错误处理这一需求会导致角色在原地滑步（动画播放但位移速度不匹配）或动画跳变（两个不相邻状态之间直接切换）。掌握四状态移动状态机的构建，是后续扩展战斗状态机和子状态机的前置实践基础。

---

## 核心原理

### 四状态拓扑结构

标准移动状态机由四个节点和若干有向边组成。节点分别是 **Idle**、**Walk**、**Run**、**Sprint**，有向边代表允许的状态转换路径。最常见的线性拓扑如下：

```
Idle ↔ Walk ↔ Run ↔ Sprint
```

线性拓扑要求角色必须经过Walk才能到达Run，再经过Run才能到达Sprint，这模拟了真实的加速物理过程，防止角色从静止瞬间跳入冲刺动画。部分设计会额外允许 Sprint→Idle 的直接跳转，用于处理玩家突然松开所有按键的情况，但该边需要配置更长的过渡时长（通常0.2~0.3秒）以避免视觉跳变。

### 速度驱动的转换条件

移动状态机的转换条件通常绑定到角色的**地面速度浮点参数**（Ground Speed，单位 cm/s 或 m/s）。以Unity Mecanim为例，典型阈值设定如下：

| 转换方向 | 条件参数 | 阈值示例 |
|---|---|---|
| Idle → Walk | Speed > 10 cm/s | 大于10 |
| Walk → Run | Speed > 200 cm/s | 大于200 |
| Run → Sprint | Speed > 450 cm/s | 大于450 |
| Walk → Idle | Speed < 5 cm/s | 小于5 |

注意 Idle→Walk 与 Walk→Idle 使用不同阈值（10 vs 5），这种**死区（Deadband）设计**防止角色在边界速度附近反复横跳切换状态，该现象俗称"状态抖动"（State Flicker）。

### 过渡时长与混合曲线

每条转换边除了触发条件外，还需要配置**过渡时长（Transition Duration）**，该参数决定两个动画片段之间线性混合的持续帧数。Idle→Walk 的典型过渡时长为0.15~0.25秒；而 Run→Sprint 因两个动画步幅相近，可以设置更短的0.1秒过渡。过渡时长过长会让角色感觉"黏滞"，过短则产生动画跳变。在Unreal Engine中，过渡曲线默认为线性（Linear），但可改为EaseIn或EaseOut曲线，后者在 Run→Sprint 切换时表现更流畅，因为它模拟了加速初期的肌肉发力延迟。

### 出口时间（Exit Time）

部分移动状态不应在任意帧触发转换，而应等待当前动画播放到特定百分比（即Exit Time）。例如Walk循环的步态周期为0.5秒，若在迈步到一半时切换到Run，脚部位置会出现突变。将 Walk→Run 的Exit Time设为0.0（即0%，立即响应）并配合适当过渡时长，是处理移动状态机中步态连续性的标准做法；而对于有明确起身/落地帧的动作（如跳跃落地），则需要将Exit Time设为接近1.0。

---

## 实际应用

**第三人称跑酷游戏的移动状态机**：在《刺客信条》系列中，角色的地面移动包含Walk（低速混入环境）、Run（标准跑步）和Sprint（全速冲刺翻越）三个核心状态。开发团队在 Run→Sprint 转换上额外加入了一个布尔参数 `IsHoldingSprint`，只有玩家持续按住冲刺键超过0.3秒才触发转换，防止轻触按键误触冲刺状态。

**移动端游戏的简化版本**：受限于触控输入的精度，移动端游戏（如《原神》手游版）的移动状态机通常省略Walk状态，直接使用 Idle↔Run↔Sprint 三状态结构，以虚拟摇杆的偏移量百分比（0~100%）作为转换参数，阈值通常设定为：偏移量＞30%进入Run，偏移量＞85%进入Sprint。

**根运动（Root Motion）与状态机的配合**：当Run和Sprint动画启用Root Motion时，动画片段本身携带位移数据，角色速度由动画驱动而非物理系统驱动。此时移动状态机的转换条件参数需要从物理速度改为玩家输入强度（InputMagnitude），否则会出现"状态机等待速度达到阈值、但速度又依赖状态机先切换"的循环依赖死锁。

---

## 常见误区

**误区一：对所有转换都使用相同的过渡时长**
许多初学者在Mecanim中为Idle→Walk和Run→Sprint设置相同的0.25秒过渡时长。实际上，Idle→Walk需要较长的混合时间（0.2~0.3秒）来掩盖站立与迈步之间的骨骼差异，而Run→Sprint由于两个动画的骨骼姿态极为相似，使用0.25秒反而会导致过渡期间出现明显的"减速感"，应缩短至0.05~0.1秒。

**误区二：用单一Speed阈值同时控制进入和退出转换**
将 Walk→Idle 的条件也设置为 Speed > 10（与 Idle→Walk 相同）会导致严重的状态抖动：速度在10 cm/s附近波动时，每帧都可能触发来回切换。正确做法是始终为进入和退出方向设置不同的迟滞阈值（Hysteresis），进入阈值应高于退出阈值，两者之间的差值建议至少为5~15 cm/s。

**误区三：忽略斜面运动对Ground Speed的影响**
在坡面上行走时，角色的三维速度向量的水平分量（XZ平面投影）会小于实际移动速度，导致Speed参数偏低，使角色在上坡时从Run退回Walk状态，出现"爬坡变慢"的视觉错误。正确的做法是在计算Ground Speed时使用速度向量在地面切线方向的投影，或直接使用输入强度（Input Magnitude）作为补充参数。

---

## 知识关联

移动状态机建立在**状态转换**的核心概念之上——理解转换条件的评估顺序（Unreal Engine中同一状态的多条出边按Priority从上到下依次检测）和过渡的单向/双向属性，是正确搭建Idle→Walk→Run→Sprint图的前提。

掌握移动状态机后，可以自然延伸到**战斗状态机**：战斗状态机通常以移动状态机的某个节点（如Run）作为入口，在受击或发动攻击时分叉出Attack、Stagger等新状态，两者通过层级叠加或状态覆盖方式协同工作。**子状态机**的学习也直接依赖移动状态机的经验——将Idle→Walk→Run→Sprint整体封装为一个名为"Locomotion"的子状态机节点，是子状态机最典型的入门示例。此外，移动状态机中对Speed、InputMagnitude等浮点参数的配置经验，为**参数化状态**和**动画蓝图**中的混合树（Blend Tree）设计提供了直接的参数管理直觉。