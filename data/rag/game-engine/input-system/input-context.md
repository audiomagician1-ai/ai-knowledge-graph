---
id: "input-context"
concept: "输入上下文"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 2
is_milestone: false
tags: ["上下文"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 输入上下文

## 概述

输入上下文（Input Context）是游戏引擎输入系统中的一种分层管理机制，用于定义"在什么状态下，哪些输入映射处于激活状态"。不同于单一的全局输入映射，输入上下文允许开发者将输入行为划分为多个独立的"情境集合"，例如步行模式、载具驾驶模式、UI菜单模式，每个情境只响应与其逻辑相关的按键绑定。

这一概念最早在商业引擎中被系统化，Unreal Engine 5 的 Enhanced Input 插件将其明确命名为 `UInputMappingContext`，并允许在运行时通过 `AddMappingContext` 和 `RemoveMappingContext` 函数动态增删上下文。Unity 的 Input System 包也采用了类似机制，称为 Input Action Map，同样支持 `Enable()` / `Disable()` 的切换。

输入上下文的意义在于它彻底解决了"同一按键在不同游戏状态下需要执行完全不同操作"的冲突问题。例如，`Space` 键在步行时是"跳跃"，进入载具后变为"手刹"，打开菜单后变为"确认选项"——如果没有上下文机制，开发者必须在每个动作的回调里写大量的状态判断代码，而输入上下文将这种判断提升到系统架构层面来处理。

## 核心原理

### 上下文的优先级栈结构

输入上下文通常以**优先级栈（Priority Stack）**的方式工作，而非简单的互斥切换。在 Unreal Engine 5 的 Enhanced Input 中，`AddMappingContext` 接受一个整数类型的 `Priority` 参数（数值越高优先级越高）。当两个上下文同时激活且都绑定了同一个物理按键时，优先级更高的上下文的映射会生效，低优先级上下文的对应绑定被屏蔽。

这意味着"菜单上下文"可以被设置为优先级 10，"游戏角色上下文"设置为优先级 1，当玩家打开菜单时只需将菜单上下文压入栈中，角色移动的输入会自动被遮蔽，关闭菜单时移除菜单上下文即可恢复角色控制——无需手动禁用角色输入。

### 上下文的激活与停用

上下文的切换本质上是对一组输入映射的批量启停操作。以 Unity Input System 为例，一个 `InputActionMap`（等同于上下文）可通过以下方式切换：

```
playerActionMap.Disable();
vehicleActionMap.Enable();
```

这两行代码的效果是：将"玩家行走"相关的所有 Action（移动、跳跃、冲刺）全部停用，同时启用"载具驾驶"相关的所有 Action（油门、刹车、转向、手刹）。批量操作是上下文机制相比逐一启停单个 Action 的关键优势。

### 上下文与输入映射的关系

输入上下文本身不定义具体的按键与行为，它是**输入映射（Input Mapping）的容器**。一个上下文包含若干条输入映射，每条映射将物理按键绑定到逻辑 Action。例如"载具上下文"可能包含如下映射：

- `W / Left Stick Y+` → `Throttle`（油门）
- `S / Left Stick Y-` → `Brake`（刹车）
- `Space / B Button` → `Handbrake`（手刹）
- `F / Triangle Button` → `ExitVehicle`（下车）

同一个 `ExitVehicle` Action 在步行上下文中不存在对应映射，因此 `F` 键在步行时不会触发任何与下车相关的逻辑，而不是被某段 `if` 代码拦截。

### 上下文叠加与部分覆盖

上下文不必完全互斥。例如"潜水上下文"可以叠加在"角色基础上下文"之上，仅覆盖`Space`（从跳跃变为上浮）和`Ctrl`（从下蹲变为下潜），其余移动按键仍由基础上下文处理。这种**增量叠加**模式避免了为每种特殊状态创建完整的全量上下文副本。

## 实际应用

**第三人称射击游戏的上下文设计**：典型实现包含三个上下文——`FootContext`（步行，Priority=1）、`VehicleContext`（载具，Priority=1）、`UIContext`（菜单，Priority=10）。正常游玩时只有 `FootContext` 激活；进入载具时停用 `FootContext`，激活 `VehicleContext`；任何时候打开暂停菜单都将 `UIContext` 压入，屏蔽所有游戏操作。

**对话系统的临时上下文**：在 RPG 对话场景中，触发对话时激活一个 `DialogueContext`（Priority=5），它只响应方向键（选项导航）和 `Enter`（确认）。对话结束后立即移除该上下文，玩家控制无缝恢复，整个流程不需要修改任何角色控制器代码。

**辅助功能的全局上下文**：某些游戏将截图、字幕切换等辅助功能绑定在一个低优先级的全局上下文（Priority=0）中，该上下文始终激活。由于这些按键（如 `F12`）不与其他上下文冲突，叠加在任意状态下都能响应。

## 常见误区

**误区一：以为上下文切换等同于删除输入映射**。输入上下文的停用是可逆的运行时操作，原始的映射配置数据始终存在于资产中。许多初学者在切换上下文时错误地修改了映射表本身（如删除绑定），导致上下文恢复后按键失效。正确做法是调用 `RemoveMappingContext` 或 `Disable()`，而不是修改映射数据。

**误区二：默认所有平台共用同一套上下文**。手柄和键盘可以在同一个上下文内通过同一个 Action 的多个绑定共存（例如 `W` 和 `Left Stick Y+` 同时映射到 `Move`），但载具上下文中"手柄震动反馈"的触发逻辑需要区分平台。误认为上下文切换能自动处理平台差异会导致手柄玩家进入载具后缺少振动反馈。

**误区三：优先级数字越小优先级越高**。在 Unreal Engine 5 Enhanced Input 中，`Priority` 值**越大**表示优先级越高（与部分 UI 框架的 Z-Order 语义相反）。将菜单上下文设置为 Priority=0 而角色上下文为 Priority=1，会导致菜单打开时角色输入依然响应，这是非常常见的初学者错误。

## 知识关联

输入上下文直接建立在**输入映射**的基础上：输入映射定义了单条"物理按键 → 逻辑 Action"的规则，而输入上下文是这些规则的分组容器与激活开关。理解输入映射中 Action 的类型（Button、Axis1D、Axis2D）是正确设计上下文内映射集合的前提，例如载具上下文中的油门 Action 应为 Axis1D 类型以支持模拟扳机的力度输入。

在更大的系统架构中，输入上下文的切换时机通常由**游戏状态机**或**场景管理器**驱动——当状态机转移到"载具驾驶"状态时，其 `OnEnter` 回调负责切换上下文。这使得输入系统与游戏逻辑保持解耦，每个系统只负责自己的职责边界。
