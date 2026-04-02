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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 输入上下文

## 概述

输入上下文（Input Context）是游戏引擎输入系统中的一种**状态分组机制**，它将一组输入映射绑定在一个命名的"上下文"容器里，只有当该上下文处于激活状态时，其内部的映射才会生效。举个最直观的例子：玩家在主菜单时，键盘上的 W/A/S/D 控制光标在菜单项之间移动；进入游戏后，同样的 W/A/S/D 变成了角色移动；骑上载具后，W/A/S/D 则变成了油门与转向。三套完全不同的行为共享同一组按键，靠的就是三个独立的输入上下文在运行时被切换激活。

这一概念最早在商业引擎中被系统化。虚幻引擎5（2022年正式发布）在其增强输入系统（Enhanced Input System）里将 `UInputMappingContext` 作为一等公民引入，取代了旧版 `UInputComponent` 中扁平化的绑定列表。Unity 的 Input System Package（1.0版，2020年发布）中对应的概念叫 `InputActionAsset` 中的 `Control Scheme` 与 `Action Map` 组合，其中 `Action Map` 与输入上下文在功能上最为接近。

掌握输入上下文的意义在于：它从架构层面解决了"同一按键在不同游戏状态下有不同含义"的多义性问题。如果没有上下文机制，开发者就必须在每个输入回调里手写大量 `if (isInMenu)`、`if (isInVehicle)` 的条件分支，既难以维护，也容易产生状态冲突漏洞（例如同时激活两套行为）。

---

## 核心原理

### 优先级栈（Priority Stack）

输入上下文通常以**栈结构**管理，而非简单的开关切换。每个上下文被添加到栈时携带一个整数优先级值。在虚幻引擎的增强输入系统中，调用 `AddMappingContext(Context, Priority)` 时，优先级数值越小代表越高优先级（0最高）。当同一个输入事件（如按下空格键）在多个激活的上下文中都有映射时，系统只执行优先级最高的那个上下文中对应的动作，低优先级上下文的映射被**屏蔽（Block）**而非覆盖。

这种设计允许多个上下文**同时激活**。例如，一款角色扮演游戏可以同时激活"通用UI上下文"（优先级0）和"战斗上下文"（优先级1），UI上下文中 Escape 键负责打开系统菜单，战斗上下文中 Q/E/R 负责技能释放。两个上下文共存，互不干扰。

### 上下文的激活与停用

上下文的生命周期管理通常绑定在游戏对象的状态机或场景加载事件上。以虚幻引擎为例，典型的切换代码如下：

```cpp
// 进入载具时
PlayerController->AddMappingContext(VehicleContext, 0);
PlayerController->RemoveMappingContext(FootContext);

// 离开载具时
PlayerController->RemoveMappingContext(VehicleContext);
PlayerController->AddMappingContext(FootContext, 1);
```

`AddMappingContext` 和 `RemoveMappingContext` 都作用于 `UEnhancedInputLocalPlayerSubsystem` 上。注意每次添加都必须明确传入优先级参数，遗漏优先级是初学者最常见的错误之一。

### 上下文与输入映射的关系

一个输入上下文内部包含若干条**输入映射（Input Mapping）**，每条映射定义了"物理按键 → 输入动作（Input Action）"的对应关系，并可附加**修饰器（Modifier）**和**触发器（Trigger）**。上下文本身不处理逻辑，它只是映射的容器和开关。具体的游戏逻辑（如角色移动、开枪）写在绑定到 `InputAction` 的回调函数里。这种三层结构——上下文 → 映射 → 动作——使得按键绑定可以在运行时动态调整，而无需修改任何游戏逻辑代码。

---

## 实际应用

### 菜单 / 游戏 / 载具三状态切换

这是输入上下文最典型的应用场景。一款开放世界游戏通常需要至少以下三个上下文：

| 上下文名称 | 包含的典型映射 | 激活时机 |
|---|---|---|
| `MenuContext` | 方向键导航、Enter确认、Escape返回 | 打开暂停菜单时 |
| `FootContext` | WASD移动、鼠标视角、空格跳跃 | 正常步行状态 |
| `VehicleContext` | W/S油门刹车、A/D转向、F下车 | 进入载具触发器时 |

切换方向：进入菜单时，将 `MenuContext` 以优先级0压入栈顶（不移除 `FootContext`，仅屏蔽冲突映射）；关闭菜单后，移除 `MenuContext` 即可自动恢复行走控制。

### 对话系统中的临时上下文

NPC 对话是另一个精准体现上下文价值的案例。触发对话时，激活专用的 `DialogueContext`（包含 E 键继续对话、1/2/3 选择选项的映射），并以高优先级压栈，使玩家无法在对话期间使用 W/A/S/D 移动角色。对话结束后，一行 `RemoveMappingContext(DialogueContext)` 即恢复全部原有控制——无需保存和恢复任何状态，因为被屏蔽的上下文始终在栈里。

---

## 常见误区

### 误区一：以为切换上下文就是"关闭旧的再开启新的"

许多初学者认为上下文是互斥的，每次只能有一个激活。实际上，如上文所述，输入上下文是**栈式多激活**的。如果在进入载具时直接 `RemoveMappingContext(FootContext)` 然后 `AddMappingContext(VehicleContext, 0)`，下车时就必须记住重新 `Add` 步行上下文。而若改用优先级屏蔽（同时保留两个上下文，载具上下文以更高优先级压顶），下车时只需 `Remove` 载具上下文，步行上下文自动恢复生效，逻辑更健壮。

### 误区二：将上下文混同于输入动作（Input Action）

上下文和动作是完全不同的层次。`InputAction_Jump`（跳跃动作）可以同时出现在 `FootContext`（空格触发）和 `VehicleContext`（不出现，意味着载具内无法跳跃）中。一个 `InputAction` 资产可以被多个上下文引用，一个上下文也可以将同一个动作映射给不同的物理按键。把上下文理解成"一个上下文只对应一个行为模式"是正确的，但认为"上下文是动作的子集"则是错误的——它们是正交的两个维度。

### 误区三：在 Tick 函数中轮询上下文状态

部分开发者会在每帧的 `Tick()` 里根据游戏状态变量反复调用 `AddMappingContext`/`RemoveMappingContext`。这不仅会产生大量冗余调用（每帧向栈中重复添加已有上下文），还可能导致优先级混乱。正确做法是在**状态变化的事件点**（如 `OnEnterVehicle`、`OnExitMenu` 事件委托）中执行上下文切换，而非在轮询中持续操作。

---

## 知识关联

**前置概念**：学习输入上下文之前，必须理解**输入映射（Input Mapping）**——即物理按键与逻辑动作之间的绑定关系。上下文的本质是"对输入映射集合的分组与按需激活"，如果不清楚单条映射如何工作，就无法理解为什么把映射划入不同上下文能改变运行时行为。特别需要先掌握 `InputAction` 资产的创建和 `Modifier`（如死区、归一化）的配置，因为上下文切换后这些属性仍然有效。

**横向关联**：输入上下文与游戏的**状态机（State Machine）**设计高度耦合——每个游戏状态（菜单态、战斗态、过场动画态）通常对应一套上下文激活/停用操作。在实现时，推荐将上下文切换逻辑封装在状态机的 `OnEnter`/`OnExit` 回调里，而非散落在各处的业务代码中，这样当新增一个游戏状态时，只需新建一个上下文并在对应状态中挂载，不会影响其他任何现有状态的输入行为。