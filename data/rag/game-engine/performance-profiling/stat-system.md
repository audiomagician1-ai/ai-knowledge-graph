---
id: "stat-system"
concept: "统计系统"
domain: "game-engine"
subdomain: "performance-profiling"
subdomain_name: "性能剖析"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.5
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



# 统计系统（Stat System）

## 概述

统计系统是游戏引擎中用于实时收集、聚合和展示运行数据的基础设施，其三大核心构件为 **Stat Group（统计组）**、**Stat Counter（统计计数器）** 和 **Stat Timer（统计计时器）**。这三类构件分别负责不同粒度的性能数据：Group 提供分类容器，Counter 记录事件次数或数值，Timer 测量代码块的耗时。以 Unreal Engine 为例，其统计系统通过 `DECLARE_STATS_GROUP`、`DECLARE_CYCLE_STAT` 等宏在编译期注册所有统计项，运行时通过 `stat [GroupName]` 指令在屏幕上实时叠加显示。

统计系统的设计思路可追溯至 1990 年代的游戏开发实践——开发者最初用手写日志文件记录帧率，后逐渐演化为内置于引擎的标准化测量框架。现代引擎（如 Unreal Engine 4/5、Unity）均将统计系统作为性能剖析的第一层入口：它的开销极低（Unreal 的 Cycle Stat 在 shipping 构建中默认被完全剔除），且不依赖外部工具即可工作，这使得它在开发阶段的日常迭代中比 GPU 捕获或完整 Profiler Session 更频繁地被使用。

统计系统的重要性体现在它能够在不中断游戏运行的情况下持续输出数据。一个正确配置的 Stat Timer 可以让你在 30 秒内定位某个每帧调用的函数是否突然从 0.1 ms 飙升到 3 ms，而无需暂停进程或重启引擎。

---

## 核心原理

### Stat Group：统计分组容器

Stat Group 是统计系统的命名空间机制。在 Unreal Engine 中，声明一个组的语法为：

```cpp
DECLARE_STATS_GROUP(TEXT("MySystem"), STATGROUP_MySystem, STATCAT_Advanced);
```

第三个参数 `STATCAT_Advanced` 控制该组是否在默认情况下可见（`STATCAT_Advanced` 表示需要手动启用）。一个 Group 可以包含任意数量的 Counter 和 Timer，但通常按子系统划分，例如 `STATGROUP_AI`、`STATGROUP_Particles`。当你在控制台输入 `stat AI` 时，引擎会渲染该 Group 下所有已注册的统计项，而不会显示其他 Group 的数据，从而避免信息过载。

### Stat Counter：事件与数值计数

Stat Counter 分为两类：**整型计数器**（`DECLARE_DWORD_COUNTER_STAT`）和**浮点计数器**（`DECLARE_FLOAT_COUNTER_STAT`）。其典型用途是记录每帧的对象数量、内存分配次数、Draw Call 总数等离散指标。在代码中更新计数器使用：

```cpp
INC_DWORD_STAT(STAT_MyObjectCount);       // 递增 1
SET_DWORD_STAT(STAT_MyObjectCount, 42);   // 直接设置绝对值
```

Counter 的数值在每帧结束时**不会自动清零**，除非统计项被声明为 `STAT_TYPE_COUNT_DELTA`（增量模式）。这一细节是初学者最常踩的陷阱之一：若错误地对一个累积型 Counter 调用 `INC`，会看到数值持续增长而非每帧的新增量。

### Stat Timer：代码块耗时测量

Stat Timer 基于 CPU 周期（Cycle）计数，其核心宏为：

```cpp
DECLARE_CYCLE_STAT(TEXT("MyFunction"), STAT_MyFunction, STATGROUP_MySystem);

void MyFunction()
{
    SCOPE_CYCLE_COUNTER(STAT_MyFunction);
    // ... 被测量的代码 ...
}
```

`SCOPE_CYCLE_COUNTER` 利用 RAII 机制，在构造时记录 `FPlatformTime::Cycles()` 的起始值，在析构时计算差值并转换为毫秒。公式为：

$$T_{ms} = \frac{C_{end} - C_{start}}{F_{cpu}} \times 1000$$

其中 $C$ 为 CPU 周期数，$F_{cpu}$ 为平台的 CPU 频率（Hz）。Unreal 通过 `FPlatformTime::GetSecondsPerCycle()` 预先缓存频率倒数，避免每帧除法运算带来的开销。

Stat Timer 支持嵌套调用，父级 Timer 的时间包含所有子级 Timer 的耗时，这与 Unreal Insights 中的调用栈层级一一对应。

---

## 实际应用

**场景一：诊断 AI 更新性能**

在一个有 200 个 AI 单位的关卡中，开发者怀疑 AI Tick 导致帧率下降。只需在 AI 的 `Tick` 函数中添加 `SCOPE_CYCLE_COUNTER(STAT_AITick)`，并在控制台输入 `stat AI`，即可实时看到该计时器的每帧耗时、调用次数和平均值。若显示 `AITick: 8.3 ms (calls: 200)`，则可进一步用更细粒度的 Timer 划分 Pathfinding、Perception、Behavior Tree 三个子阶段。

**场景二：监控粒子系统 Sprite 数量**

在粒子系统管理器中声明一个 `DWORD_COUNTER_STAT(STAT_ActiveSpriteCount)`，每次生成粒子时调用 `INC_DWORD_STAT`，每次销毁时调用 `DEC_DWORD_STAT`。运行时 `stat Particles` 会实时展示当前场景中活跃 Sprite 的绝对数量，帮助验证粒子发射器的预算是否超限（例如策划规定最多 5000 个 Sprite）。

**场景三：多线程环境下的统计**

在 Unreal 的渲染线程中，统计系统提供了线程安全版本的宏：`SCOPE_CYCLE_COUNTER` 在任意线程上均可安全调用，因为每个线程持有独立的 `FThreadStats` 实例，主线程在帧末汇总时才合并数据。

---

## 常见误区

**误区一：认为 Stat Timer 的精度足以替代专业 Profiler**

Stat Timer 的时间分辨率依赖平台的 `QueryPerformanceCounter`（Windows）或 `clock_gettime`（Linux），精度通常在 **100 纳秒级别**，这对于测量耗时 5 ms 以上的函数非常可靠。但对于耗时不足 10 微秒的热路径函数，多次调用的测量累积误差可能超过真实耗时，此时应改用 Intel VTune 或 Unreal Insights 的采样模式。

**误区二：在 Shipping 构建中留有统计代码**

Unreal 的 `SCOPE_CYCLE_COUNTER` 宏在 `STATS` 宏未定义时会展开为空语句。`STATS` 宏在 `Debug` 和 `Development` 构建中默认启用，在 `Shipping` 构建中默认禁用。如果开发者手动在项目的 `Build.cs` 中为 Shipping 构建开启 `bWithStats = true`，会导致发布版本的额外性能开销，这不是统计系统的设计意图。

**误区三：混淆 Counter 的累积模式与增量模式**

使用 `SET_DWORD_STAT` 设置的是**当前帧的绝对值**，而 `INC_DWORD_STAT` 是在上一帧数值基础上累加。若要统计"每帧新增的网络包数量"，应使用增量 Counter 并在帧开始时重置，而非直接用 `INC` 而不重置，否则 stat 面板显示的数值会随时间无限增长，完全失去诊断意义。

---

## 知识关联

统计系统建立在**性能剖析概述**所介绍的"最小化测量干扰"原则之上——Stat Timer 的 RAII 设计正是为了确保即使函数提前返回也不遗漏计时结束点。掌握统计系统后，可以进一步学习 **Unreal Insights**：Stat Timer 产生的 Cycle 数据是 Insights 中 CPU Track 的数据来源之一，理解统计系统的注册机制和线程模型，有助于在 Insights 的时间轴视图中正确解读各 Track 的层级结构。此外，统计系统中的 **Stat Group 概念**与 RenderDoc 中的 GPU Marker 分组机制高度类似，两者都通过命名空间将海量性能数据归类，降低认知负担。