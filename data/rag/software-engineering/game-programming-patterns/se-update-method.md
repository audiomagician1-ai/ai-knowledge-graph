---
id: "se-update-method"
concept: "更新方法"
domain: "software-engineering"
subdomain: "game-programming-patterns"
subdomain_name: "游戏编程模式"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 更新方法

## 概述

更新方法（Update Method）是一种游戏编程模式，其核心思想是为游戏世界中的每个对象定义一个统一的 `update()` 接口，让游戏循环在每一帧统一调用所有活跃对象的该方法，从而将"时间如何推进"的逻辑从"对象如何响应时间"中彻底分离。这个模式最早由 Bjarne Stroustrup 等面向对象先驱的设计思想衍生而来，但在游戏工程领域由 Robert Nystrom 在其2014年著作《游戏编程模式》（*Game Programming Patterns*）中作为独立模式正式命名和系统化阐述。

在没有此模式之前，一款游戏若有敌人、子弹、特效三类对象，开发者往往需要在主循环中手动枚举每类对象的逻辑：先更新所有敌人，再更新所有子弹……代码耦合严重，新增一种对象类型就必须修改主循环代码。更新方法通过引入统一接口，使主循环只需遍历一张"可更新对象"列表并依次调用 `update(elapsed)` 即可，主循环代码永远不需要知道列表里装的是什么类型的对象。

该模式的重要性体现在它是几乎所有商业游戏引擎的架构基础——Unity 的 `MonoBehaviour.Update()`、Unreal Engine 的 `AActor::Tick(float DeltaSeconds)`、Godot 的 `_process(delta)` 全部是此模式的具体实现变体。

## 核心原理

### 统一接口定义

更新方法的最小化实现只需一个抽象基类和一个纯虚函数：

```cpp
class Entity {
public:
    virtual ~Entity() {}
    virtual void update(double elapsed) = 0;  // elapsed 单位为秒
};
```

`elapsed`（或 `delta`）参数携带自上一帧以来经过的真实时间（单位通常为秒或毫秒）。主循环的职责被压缩为：

```cpp
while (running) {
    double elapsed = measureFrameTime();
    for (auto& entity : entities) {
        entity->update(elapsed);
    }
    render();
}
```

主循环与具体对象之间的依赖关系从"知道所有类型"退化为"只知道 Entity 接口"，这是开闭原则（OCP）在游戏编程中最直接的体现。

### 帧时间参数的传递与使用

传入 `elapsed` 的目的是实现**帧率无关运动**。若一个敌人每帧固定移动 3 像素，在 60fps 下每秒移动 180 像素，在 30fps 下却只移动 90 像素——这会导致低帧率设备上的游戏角色移动缓慢。正确做法是将速度定义为"像素/秒"，再乘以帧时间：

```
position += velocity * elapsed
```

例如设 `velocity = 180 px/s`，则无论帧率是 60fps（elapsed ≈ 0.0167s）还是 30fps（elapsed ≈ 0.033s），每秒累积位移均约等于 180 像素。这一公式是更新方法中最关键的数学关系，所有依赖 `elapsed` 的计算本质上都是这个积分的离散近似。

### 对象生命周期与列表管理

更新方法要求维护一张活跃实体列表（`std::vector<Entity*>` 或类似结构）。对象的创建（spawn）和销毁（destroy）不能在 `update()` 执行期间直接修改该列表，否则会导致迭代器失效或跳过更新。常见的解决方案是引入**延迟删除队列**：在 `update()` 中将待销毁对象标记为 `dead = true`，待本帧所有 `update()` 调用结束后，主循环再统一清除标记为 `dead` 的对象。Unity 的 `Destroy()` 函数采用的正是这一策略——调用后对象不会立即消失，而是在当前帧结束时才真正被移除。

### 更新顺序的确定性问题

当多个对象的 `update()` 之间存在依赖关系时，调用顺序影响结果。例如，若玩家角色的 `update()` 先于摄像机的 `update()` 执行，摄像机本帧会紧跟玩家；若顺序相反则摄像机总是滞后一帧。Unity 为此提供了 `LateUpdate()` 接口，专门用于需要在所有普通 `update()` 完成后才执行的逻辑（如摄像机跟随、骨骼附件定位）。这说明一个简单的接口约定之下，顺序管理可以演化出相当复杂的工程方案。

## 实际应用

**敌人AI巡逻**：一个巡逻敌人的 `update(elapsed)` 内部维护一个状态机，每次调用时根据 `elapsed` 推进沿路径的位移量，到达路径端点后切换行进方向。整个逻辑完全封装在该类内部，主循环无需任何修改即可支持新增的敌人实例。

**子弹生命周期管理**：子弹对象在 `update(elapsed)` 中累加已存活时间，当累加值超过 `maxLifetime`（例如 2.5 秒）时将自身标记为 `dead`。对象池（Object Pool）模式通常与更新方法配合使用：被标记为 `dead` 的子弹对象不销毁内存，而是返回池中供下次发射复用，避免高频内存分配带来的GC压力（在 C# 游戏中这一点尤为重要）。

**动画系统驱动**：Spine 2D 骨骼动画运行时（libspine）中，每个 `SkeletonAnimation` 对象持有一个 `AnimationState`，其 `update(delta)` 方法按帧时间推进动画时间轴、触发关键帧事件，这正是更新方法模式在商业中间件中的标准应用形式。

## 常见误区

**误区一：在 `update()` 内部直接修改实体列表**
初学者常在一个敌人的 `update()` 中直接调用 `entities.erase()`，导致正在遍历的迭代器失效，引发未定义行为或崩溃。正确做法始终是"标记-延迟清除"两步分离，`update()` 只负责修改对象自身状态，列表结构的变动由主循环统一处理。

**误区二：`elapsed` 不设上限导致"时间爆炸"**
当游戏窗口被拖动、调试断点暂停或系统休眠后恢复时，`elapsed` 可能突然变为数秒甚至数十秒。若物理或AI直接使用这个值，对象会瞬间跳跃到离谱位置。工程实践中必须对 `elapsed` 做截断处理，常见上限值为 `0.25` 秒（即假设最慢运行帧率约为 4fps），超过此值一律按 `0.25` 秒处理。

**误区三：把所有逻辑都塞进单一 `update()` 方法**
更新方法定义的是一个**调用约定**，并不要求所有逻辑都写在一个函数体中。当 `update()` 逻辑超过约50行时，通常意味着该类承担了过多职责，需要配合组件模式将输入处理、物理更新、动画驱动等拆分到独立组件各自的 `update()` 中，再由宿主对象的 `update()` 依次委托调用。

## 知识关联

**与游戏循环的关系**：更新方法是游戏循环模式的直接下游。游戏循环负责控制"何时驱动整个世界前进一步"以及测量帧时间，而更新方法负责定义"世界中每个对象如何响应这一步"。两者共同构成游戏时间系统的完整闭环：若游戏循环采用固定时间步长（fixed timestep，如每步 `1/60` 秒），则 `update(elapsed)` 中的 `elapsed` 始终为常数，帧率无关问题转移到插值渲染层解决；若采用可变时间步长，则帧时间截断和物理稳定性成为 `update()` 实现的核心约束。

**与组件模式的关系**：更新方法是组件模式的必要前提。组件模式将单个游戏对象（如一个"角色"）拆分为多个功能组件（输入组件、物理组件、渲染组件），每个组件独立实现 `update(elapsed)` 接口。宿主对象的 `update()` 按顺序委托各组件，从而将巨大的单体类分解为小型、可替换的功能单元。换言之，组件模式是在更新方法所建立的统一接口之上，进一步解决单个对象内部逻辑膨胀问题的方案。