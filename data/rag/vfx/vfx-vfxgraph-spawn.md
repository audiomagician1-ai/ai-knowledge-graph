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
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

VFX Graph 的生成系统（Spawn System）负责控制粒子何时、以何种数量被创建并送入模拟流程。不同于传统粒子系统中写死在时间轴上的发射逻辑，VFX Graph 将生成行为抽象为独立的 **Spawn Context**，允许多种生成模式并行存在于同一个 VFX Asset 中。每个 Spawn Context 的输出直接连接到 Initialize Particle Context，形成"生成 → 初始化 → 更新 → 输出"这条数据流的起点。

生成系统的设计思路来自 Unity 在 2018 年随 HDRP 推出 VFX Graph 时的架构决策：把粒子生命周期的每个阶段都显式化为可视节点，而不是隐藏在属性面板背后。这意味着生成速率本身可以被其他节点计算、曲线驱动或事件触发，具备与 Shader Graph 类似的可编程灵活性。

对于特效艺术家而言，生成系统的重要性在于它直接决定粒子池（Particle Pool）的消耗节奏。错误配置 Rate 或 Burst 会导致粒子容量（Capacity）在瞬间耗尽，或产生持续空跑的性能浪费。因此理解各生成模式的精确行为是优化 VFX 性能的第一步。

---

## 核心原理

### Rate（持续速率）

Rate 模式以"每秒 N 个粒子"的恒定速率连续生成粒子，是最基础的生成方式。在 Spawn Context 内添加 **Set Rate** Block，将 Rate 设为浮点数即可激活此模式。Rate = 100 表示每帧（假设 60 fps）约生成 1.67 个粒子，VFX Graph 内部使用**小数累积（Fractional Accumulation）**机制：每帧将 `Rate × deltaTime` 累加到一个内部计数器，当计数器超过 1.0 时生成一个粒子并将其减 1，保证长期平均值精确吻合设定值。该机制使 Rate 在低帧率下仍维持粒子密度，而非漏帧。

Rate 的数值可通过连接外部属性（Exposed Property）或绑定到 Blackboard 上的曲线动态变化，例如将 Rate 与角色速度绑定，实现奔跑时烟尘浓度随速度线性增长。

### Burst（瞬时爆发）

Burst 模式在特定时刻一次性生成固定数量的粒子，适用于爆炸、碰撞火花、技能释放等瞬态效果。在 Spawn Context 中添加 **Set Burst** Block，需要配置三个参数：

- **Count**：单次爆发数量（整数）
- **Delay**：距 Spawn Context 激活后多少秒触发，默认 0
- **Repeat**：重复次数，值为 -1 表示无限循环，值为 0 表示仅触发一次

若设置 Count = 500、Delay = 0.1、Repeat = 3，效果是：激活后 0.1 秒、1.1 秒、2.1 秒各爆发 500 个粒子（重复间隔由 **Period** 属性控制，默认 1 秒）。多个 Burst Block 可叠加在同一 Spawn Context 中，产生多阶段爆发时序。

### GPU Event（GPU 驱动的二次生成）

GPU Event 是 VFX Graph 特有的高级生成机制，允许 GPU 上正在运行的粒子触发新粒子的生成，整个过程无需 CPU 介入。其工作流程如下：

1. 在"父"系统的 Update Context 中添加 **Trigger Event On Die** 或 **Trigger Event Rate** Block，将生成信号写入一个 `GPUEvent` 类型的端口。
2. 将该 GPUEvent 端口连接到新 Spawn Context 的 **GPU Event** 输入端。
3. 新 Spawn Context 的粒子继承父粒子的属性（位置、速度等），通过 **Inherit Attribute** Block 提取。

典型应用：子弹粒子在死亡时触发 16 个弹孔火花粒子，整个链路在 GPU 内闭环执行，CPU 只需在每帧提交一次 DrawCall，无论场景中有多少子弹同时消亡，生成开销均不随数量增长。这是 GPU Event 与普通 Burst 的本质区别。

### Spawn Context 的激活控制

每个 Spawn Context 拥有 **Start** 和 **Stop** 事件输入端口，默认由 VFX Asset 挂载时自动发送 `OnPlay` / `OnStop` 事件驱动。通过 C# 调用 `visualEffect.SendEvent("EventName")` 可手动控制单个 Spawn Context 的开启与关闭，实现同一 VFX 资产中多个生成系统的异步调度。

---

## 实际应用

**技能连段特效**：一个法术效果 VFX Asset 中同时包含三个 Spawn Context：第一个使用 Rate = 50 持续生成法阵光粒子；第二个使用 Burst（Count = 200，Delay = 0）在施法瞬间爆发；第三个通过 GPU Event 让光粒子在屏幕边缘消亡时触发细碎反弹粒子。三者共享同一个 Initialize Context，以不同颜色属性区分。

**载具尾迹**：赛车排气尾迹将引擎转速（0–8000 RPM）映射为 Rate 值（0–300），通过 Exposed Float Property 每帧由 C# 脚本更新，粒子密度实时反映发动机负荷，无需在 CPU 端每帧批量生成粒子对象。

**链式爆炸**：主爆炸使用 Burst（Count = 1，代表中心火球），火球粒子通过 GPU Event On Die 触发 30 个碎片粒子，碎片再通过第二级 GPU Event 各自触发 5 个火星，形成三层 GPU 驱动的链式结构，总计 1 + 30 + 150 = 181 个粒子，CPU 负担仅为单次事件触发。

---

## 常见误区

**误区一：Burst Count 不受 Capacity 限制**
很多初学者认为 Burst Count 只要设置了就一定会全部生成。实际上，VFX Graph 中每个 System 的 Capacity（在 Initialize Context 右键菜单设置）是粒子池的硬上限。若 Capacity = 100 而 Burst Count = 500，实际只会生成 100 个粒子，多余的请求被静默丢弃，不会有任何警告。正确做法是将 Capacity 设为粒子生命周期内理论同屏最大量：`Capacity ≥ Rate × MaxLifetime + 所有Burst总量`。

**误区二：GPU Event 继承属性无需额外配置**
有人以为 GPU Event 子粒子会自动继承父粒子的全部属性。实际上，子 Spawn Context 连接到 GPU Event 后，必须在子系统的 Initialize Context 中**手动添加 Inherit Source Attribute Block**，并逐一指定需要继承的属性（如 Position、Velocity）。未添加该 Block 时，子粒子将在世界原点以零速度生成，与预期效果完全不同。

**误区三：Rate 和 Burst 可以在 Update Context 中控制**
生成逻辑（Rate / Burst）只能存在于 **Spawn Context** 中，不能放入 Update Context。Update Context 仅处理已存活粒子的逐帧更新。若要在粒子存活期间改变生成速率，应通过 Blackboard 属性从外部驱动 Spawn Context 中的 Rate Block，而不是试图在 Update 阶段插入生成节点。

---

## 知识关联

生成系统建立在 **Block 与节点**的操作基础上——Rate、Burst、Trigger Event 等都是具体的 Block 类型，需要熟悉向 Context 添加 Block、连接端口的基本操作才能配置生成逻辑。GPU Event 的端口连接尤其要求理解 Context 之间的数据流向规则。

掌握生成系统后，下一个关键主题是**属性系统（Property System）**。生成系统决定"何时生成多少粒子"，而属性系统决定"这些粒子初始携带哪些数据"——Rate 的动态驱动依赖 Exposed Property，GPU Event 子粒子的属性继承依赖 Source Attribute，两者紧密协作才能构建出参数化、可复用的完整粒子效果。