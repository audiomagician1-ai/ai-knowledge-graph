# EnTT框架

## 概述

EnTT（Entity-Component-System Template Library）是由意大利软件工程师 Michele "skypjack" Caini 于2017年在 GitHub 上发布的开源 C++ 库，专为游戏开发与高性能实体模拟场景设计，完整实现了 ECS（Entity-Component-System）架构模式。该项目采用 MIT 许可证，以纯头文件（header-only）形式分发，仅依赖 C++17 标准特性，无需外部依赖。截至2024年，EnTT 在 GitHub 上已积累超过 10,000 颗星，Mojang Studios 的 Minecraft Bedrock Edition 是其最知名的商业采用者之一，此外还有 ArcGIS Runtime SDK 等工业级应用。

EnTT 的核心设计哲学源自 Caini 本人在博客系列文章《Let's write an ECS》中阐述的"零成本抽象"原则：通过 C++17 模板元编程和稀疏集合（sparse set）数据结构，在不引入任何运行时虚函数调度开销的前提下，提供语义清晰、类型安全的 API。与 Unity 的 DOTS（Data-Oriented Technology Stack）或 Flecs 等同类框架相比，EnTT 更侧重于 STL 习惯用法的一致性，使得熟悉标准库的 C++ 开发者能够极低门槛地上手。

使用 EnTT 的最小代码量仅需一行 include：`#include <entt/entt.hpp>`，这使其可以无缝嵌入 CMake、Bazel 或任何构建系统，而无需修改现有项目结构。

---

## 核心原理

### 实体标识符的二进制布局

`entt::entity` 在默认配置下是一个 32 位无符号整数，其位域划分遵循固定规则：**低 20 位**存储实体的数组索引（entity index），**高 12 位**存储版本号（generation/version）。这一设计直接决定了单个 registry 最多同时存活 $2^{20} = 1{,}048{,}576$ 个实体，版本计数器最大为 $2^{12} = 4{,}096$。若项目需要更多实体，可通过特化 `entt::entt_traits` 将底层整数类型升级为 64 位，此时索引位宽可扩展至 32 位，支持逾 42 亿实体。

版本号机制解决了"ABA 问题"（ABA Problem）：当实体 $e_0$ 被销毁后，其索引槽位被复用并创建新实体 $e_1$，此时 $e_0$ 与 $e_1$ 的索引相同，但版本号不同。旧代码持有的 $e_0$ 句柄在调用 `registry.valid(e0)` 时会因版本不匹配而返回 `false`，彻底杜绝了悬空实体引用导致的数据损坏问题。

### 稀疏集合（Sparse Set）存储架构

EnTT 为每种组件类型 $T$ 独立维护一个 `entt::storage<T>`，其底层数据结构是**稀疏集合（sparse set）**。稀疏集合由两个互相配合的数组构成：

- **稀疏数组（sparse array）**：以实体索引为下标，每个槽位存储该实体对应组件在密集数组中的位置（packed index），不存在该组件时为哨兵值 `entt::null`；
- **密集数组（packed array）**：按紧凑顺序连续存储活跃的组件实例，与一个平行的实体 ID 数组一一对应。

这一结构实现了以下复杂度特性：

| 操作 | 复杂度 |
|------|--------|
| `emplace<T>(entity)` 添加组件 | $O(1)$ 平均 |
| `remove<T>(entity)` 移除组件 | $O(1)$（swap-and-pop） |
| `get<T>(entity)` 随机访问 | $O(1)$ |
| 全组件类型线性迭代 | $O(n)$，内存连续 |

移除操作采用"交换-弹出"（swap-and-pop）策略：将目标组件与密集数组末尾元素交换后截断数组，从而避免内存碎片，维持密集数组的紧凑性。这意味着迭代顺序在删除后不保证稳定，这是使用 EnTT 时需要注意的行为特性。

### Registry：中央实体数据库

`entt::registry` 是 EnTT 的核心 API 入口，管理所有实体的生命周期和组件绑定关系。典型的实体与组件操作如下：

```cpp
entt::registry registry;

// 创建实体并附加组件
auto entity = registry.create();
registry.emplace<Position>(entity, 0.0f, 0.0f);
registry.emplace<Velocity>(entity, 1.5f, 0.0f);

// 就地构造，避免拷贝
registry.emplace_or_replace<Health>(entity, 100);

// 批量销毁满足条件的实体
registry.destroy(entity);
```

`registry.create()` 的实现优先复用已销毁实体的索引槽（来自内部的空闲列表 freelist），只有空闲列表耗尽时才扩展稀疏数组，因此内存分配呈摊销 $O(1)$ 特性。

---

## 关键方法与查询机制

### View：惰性多组件查询

`entt::view` 是实现"系统（System）"逻辑的主要工具，用于迭代同时持有指定组件类型的全部实体。View 采用**惰性求交集**策略：在迭代时以组件数量最少的类型为主集合，逐个检查其他组件是否存在，无需预先构建实体交集列表。

```cpp
// 迭代所有同时拥有 Position 和 Velocity 组件的实体
auto view = registry.view<Position, Velocity>();
view.each([](auto entity, auto& pos, auto& vel) {
    pos.x += vel.x;
    pos.y += vel.y;
});
```

对于**只读访问**，可使用 `entt::exclude` 和 `const` 修饰符明确语义，同时允许 EnTT 进行潜在的并行优化：

```cpp
auto view = registry.view<const Position, const Velocity>(entt::exclude<Dead>);
```

### Group：预排序的高性能查询

`entt::group` 是 EnTT 独有的高级查询机制，通过在组件存储层面强制将满足条件的实体索引**物理排列在一起**，实现比 View 更优的缓存局部性。Group 分为三类：

- **所有权 Group（owning group）**：获取对指定组件存储的排序控制权，迭代时多个组件数组的同一偏移位置严格对应同一实体，支持 SIMD 友好的访问模式；
- **部分所有权 Group（partial owning group）**：仅拥有部分组件类型的排序控制权；
- **非所有权 Group（non-owning group）**：不改变任何存储布局，退化为类似 View 的行为。

```cpp
// 创建对 Position 和 Velocity 同时拥有所有权的 Group
auto group = registry.group<Position, Velocity>();
// 此后 Position 和 Velocity 的密集数组在 [0, group.size()) 范围内完全对齐
```

所有权 Group 的代价是：同一组件类型在同一 registry 中只能被一个所有权 Group 拥有，多个 Group 争抢所有权将在编译期报错，这迫使开发者在架构层面显式规划组件的归属关系。

### 信号与事件系统

EnTT 内置了基于委托（delegate）的事件总线 `entt::dispatcher` 和响应式观察者 `entt::observer`。当需要在组件添加/删除时触发回调时，可通过 registry 的 `on_construct`、`on_update`、`on_destroy` 信号连接监听器：

```cpp
registry.on_construct<Position>().connect<&onPositionAdded>();
registry.on_destroy<Position>().connect<&onPositionRemoved>();
```

`entt::observer` 则跟踪满足特定条件（如组件被更新）的实体变化集合，避免了每帧全量扫描的开销，适合实现脏标记（dirty flag）模式。

---

## 实际应用

### 案例：游戏物理更新系统

在一个典型的 2D 游戏物理系统中，使用 EnTT 的实现方式完整体现了 ECS 的数据导向优势：

```cpp
struct Position { float x, y; };
struct Velocity { float vx, vy; };
struct Gravity  { float g = -9.8f; };

void physicsSystem(entt::registry& reg, float dt) {
    // 重力系统：为所有有重力组件的实体更新速度
    reg.view<Velocity, const Gravity>().each([dt](auto& vel, const auto& grav) {
        vel.vy += grav.g * dt;
    });
    // 运动系统：根据速度更新位置
    reg.view<Position, const Velocity>().each([dt](auto& pos, const auto& vel) {
        pos.x += vel.vx * dt;
        pos.y += vel.vy * dt;
    });
}
```

由于 `Position` 和 `Velocity` 的密集数组在内存中连续排列，CPU L1/L2 缓存可以有效预取，在拥有 10 万个实体的场景中，实测帧处理时间约为 0.8ms（Apple M1，单线程），而等效的基于继承多态的实现约为 8ms，性能差距约 10 倍（Caini, 2019，《ECS Back and Forth》系列博文数据）。

### 场景：Minecraft Bedrock Edition 的采用背景

Mojang Studios 在 Bedrock Edition 中使用 EnTT 管理游戏世界中的实体行为系统，包括生物 AI、物理交互和方块实体（Block Entity）逻辑。其选择 EnTT 的关键原因包括：C++ 原生集成无需运行时绑定层、稀疏集合对不均匀组件分布（大多数实体仅拥有少数几种组件）的高效处理，以及单头文件形式对多平台（PC/移动/主机）构建系统的友好性。

---

## 常见误区

### 误区一：将 Group 当作 View 的简单升级

Group 的所有权机制会重新排列组件存储，这意味着：创建 Group 之后，向 registry 添加新实体时存储的插入位置受 Group 约束影响；销毁 Group 所有权的逻辑需显式规划。许多开发者在不理解这一副作用的情况下随意创建所有权 Group，导致运行时 assertion 失败（同一组件被两个所有权 Group 声明）。正确做法是在架构设计阶段确定各组件的 Group 归属，并在代码中以 `static` 或单例形式管理 Group 生命周期。

### 误区二：在迭代中直接删除/添加实体

在 `view.each()` 或 `group.each()` 的回调中调用 `registry.destroy()` 或 `registry.emplace()` 会导致底层稀疏集合的 swap-and-pop 操作破坏迭代器，引发跳帧或越界访问。EnTT 的正确模式是在迭代中收集待处理的实体 ID 列表，在迭代结束后统一执行销毁/添加操作：

```cpp
std::vector<entt::entity> toDestroy;
registry.view<Dead>().each([&](auto entity) {
    toDestroy.push_back(entity);
});
for (auto e : toDestroy) registry.destroy(e);
```

### 误区三：混淆 `patch` 与直接修改对信号的影响

`registry.patch<T>(entity, func)` 会在修改组件后触发 `on_update<T>` 信号，而直接通过 `registry.get<T>(entity)` 获取引用并修改则**不会**触发信号。当系统依赖响应式更新（如脏标记、空间分区树的自动重建）时，必须统一使用 `patch` 接口，否则观察者逻辑将静默失效，这类 bug 极难调试。

---

## 知识关联

### 与 ECS 架构理论的关系

EnTT 是 Adam Martin 在2007年《Entity Systems are the Future of MMOG Development》中奠定的 ECS 理论的现代 C++ 工程化实现。Martin 提出的三条核心原则——实体是纯 ID、组件是纯数据、系统是纯逻辑——在 EnTT 中分别对应 `entt::entity`（32/64 位整数）、任意 POD 或非 POD 结构体（无需继承任何基类）、以及普通函数或 lambda（接受 registry 引用作为参数）。

### 与数据导向设计（DOD）的关系

En