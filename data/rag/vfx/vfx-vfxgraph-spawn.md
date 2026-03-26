---
id: "vfx-vfxgraph-spawn"
concept: "生成系统"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 生成系统

## 概述

生成系统（Spawn System）是 VFX Graph 中负责决定"何时、以何种速率、在什么条件下"向粒子池注入新粒子的模块。在 VFX Graph 的节点图中，生成系统以专用的 **Spawn Context**（生成上下文）节点块存在，与 Initialize、Update、Output 等 Context 并列，但处于整个粒子生命周期的最前端——它输出的粒子数量和触发信号直接决定后续 Initialize Context 被执行多少次。

生成系统的概念来源于粒子系统设计中最根本的问题：是每帧稳定地"滴水"式产生粒子，还是在某个瞬间"爆炸"式全量释放，还是等待某个 GPU 端事件再触发下一批？Unity 从 VFX Graph 正式进入 Package Manager（2019.3 版本）起，就将这三种主流生成策略——Rate、Burst、GPU Event——封装为相互独立但可叠加使用的 Block，允许开发者在同一个 Spawn Context 中混合配置多套生成规则。

理解生成系统的意义在于：粒子数量×粒子生命周期≈粒子池容量上限，而粒子池容量是在 VFX Asset 的 **Capacity** 属性中静态预分配在 GPU 显存里的。如果生成速率计算错误，要么粒子池溢出导致新粒子被无声地丢弃，要么显存浪费严重。因此准确配置生成系统是控制性能开销的第一道关卡。

---

## 核心原理

### Rate（持续速率生成）

Rate Block 的工作方式是将目标速率（单位：**粒子/秒** 或 **粒子/帧**）除以当前帧的时间步长，计算出本帧应生成的粒子数。其核心公式为：

> **本帧生成数 = Rate × Δt**（当模式为 Per Second 时）

由于 Δt 是浮点数，本帧计算结果通常不是整数。VFX Graph 内部维护一个**小数累加器**（Fractional Accumulator），将余量保留到下一帧，确保长期平均速率精确等于设定值。例如设定 Rate = 100 粒子/秒，在 60fps 下每帧应生成 1.6667 个粒子：第1帧生成1个，余0.6667；第2帧累计1.3333，生成1个，余0.3333；第3帧累计1.0000，生成1个——三帧共5个，等于 100÷60×3≈5，与理论值完全吻合。

Rate Block 还提供 **Rate Over Distance** 变体，此时 Δt 被替换为发射器在两帧之间的位移量，适合拖尾、轮胎烟雾等需要均匀铺设粒子的效果。

### Burst（瞬发批量生成）

Burst Block 在指定的 **延迟时间**（Delay）之后，一次性向粒子池注入固定数量的粒子，注入完成后可选择是否**循环**（Loop）并等待指定间隔再次触发。其配置参数包含四个关键字段：

- **Count**：单次爆发数量（支持随机范围，如 Min=50, Max=100）
- **Delay**：首次触发前的等待时间（秒）
- **Loop**：是否重复，填 `-1` 表示无限循环
- **Delay Between Bursts**：每两次爆发之间的间隔（秒）

与 Rate 不同，Burst 的触发由 Spawn Context 内部的**事件时钟**管理，和帧率无关，因此在低帧率下不会产生额外粒子。多个 Burst Block 可堆叠在同一 Spawn Context 中，分别设置不同 Delay，从而实现烟花多重爆炸的时序编排。

### GPU Event（GPU 端事件驱动生成）

GPU Event 是 VFX Graph 独有的生成机制，它允许一个粒子在 GPU 上"死亡"或满足某条件时，直接在 GPU 端触发另一批粒子的生成，**全程无需回读到 CPU**。实现路径为：

1. 在父粒子的 Update Context 中添加 **Trigger Event On Die**（或 **Trigger Event Rate** / **Trigger Event On Collision**）Block；
2. 将该 Block 的输出端口连接到子系统的 **GPUEvent Spawn Context**；
3. 子系统的 Spawn Context 类型选择 **GPU Event**，其生成数量由 **Count** 属性决定，可为每个触发粒子生成 1 至 N 个子粒子。

GPU Event 的性能关键点在于：子粒子的 Capacity 必须 ≥ 父粒子最大存活数 × 每次触发的 Count，否则超出部分静默丢弃。例如父粒子 Capacity=500、每粒子死亡触发 Count=3，则子粒子 Capacity 至少需设置为 1500。

---

## 实际应用

**营火火花效果**：主系统用 Rate=80 粒子/秒持续生成向上漂移的火焰粒子；当火焰粒子生命结束时，通过 GPU Event（Count=2~4，随机范围）触发更小的火花粒子向四周散射。整个链路在 GPU 内封闭执行，CPU 帧消耗几乎为零。

**爆炸冲击波**：使用单个 Burst Block，Delay=0，Count=360，Loop=1，Delay Between Bursts=99999（实际上只触发一次），一次性在球面上均匀生成360个碎片粒子，配合 Initialize Context 中的球面分布初始化速度。

**子弹轨迹拖尾**：Rate Block 切换为 **Per Distance** 模式，Rate=5，即子弹每移动1单位产生5个烟雾粒子，无论子弹速度快慢，轨迹密度始终均匀，不受帧率波动影响。

---

## 常见误区

**误区一：认为 Burst 的 Count 是精确值**
当 Burst Count 设为随机范围（如 Min=50, Max=100）时，每次循环触发都会重新随机取值，而不是在效果播放开始时固定一次。如果需要整个效果生命周期内 Burst 数量保持一致，应改用 Constant 绑定或将随机采样移至外部属性传入。

**误区二：混淆 Rate 的 Per Second 与 Per Frame 模式**
Per Frame 模式下本帧生成数 = Rate（无 Δt 乘法），不存在小数累加器。这意味着在 120fps 下使用 Per Frame Rate=2 会比 60fps 多出一倍粒子，而 Per Second 模式则与帧率无关。对于需要固定帧率表现的主机游戏可使用 Per Frame，跨平台项目应优先使用 Per Second。

**误区三：GPU Event 子系统的 Capacity 不需要单独计算**
很多开发者复制父系统的 Capacity 给子系统，导致当父粒子大量同时死亡时子粒子严重丢失。子系统的实际峰值粒子数取决于"同一时刻最多有多少父粒子同时死亡 × Count"，而非父粒子的总 Capacity，需要结合父粒子的寿命分布单独估算。

---

## 知识关联

生成系统直接依赖 **Block 与节点**的概念：Rate、Burst、GPU Event 本质上都是挂载在 Spawn Context 下的 Block，理解 Block 的堆叠规则（同一 Context 内多个 Block 顺序执行并累加输出）才能正确组合多种生成策略。

生成系统向下衔接 **属性系统**：Spawn Context 计算出的粒子数量会以 **SpawnEvent** 数据包的形式传递给 Initialize Context，其中可携带自定义属性（如触发位置、颜色种子），这些携带的属性值正是属性系统中 **Spawn Attribute** 类别的来源，初学者在学习属性系统时会频繁回头参考生成系统的事件传递机制。