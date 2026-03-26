---
id: "command-pattern"
concept: "命令模式"
domain: "ai-engineering"
subdomain: "oop"
subdomain_name: "面向对象编程"
difficulty: 2
is_milestone: false
tags: ["模式"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.387
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: "content-copy-from-sibling"
updated_at: "2026-03-26"
---
# 命令模式

## 概述

命令模式（Command Pattern）是一种行为型设计模式，其核心思想是将"请求"本身封装成一个独立对象，使调用者与执行者完全解耦。在 GoF（Gang of Four）于1994年出版的《设计模式：可复用面向对象软件的基础》中，命令模式被正式定义：将操作封装为对象，从而支持参数化请求、操作队列、日志记录以及可撤销操作。

在游戏引擎的脚本系统中，命令模式最典型的用途是实现 Undo/Redo（撤销/重做）功能以及命令队列（Command Queue）。当玩家在关卡编辑器里移动一个物体、调整一个属性值，或者脚本执行一系列操作时，这些操作若以"普通函数调用"的形式存在，则无法被记录、撤销或重放。而命令模式将每个操作变成拥有 `execute()` 和 `undo()` 方法的对象，从根本上解决了这一问题。

## 核心原理

### 基本结构：四个角色

命令模式由四个明确角色构成：

- **Command（抽象命令接口）**：声明 `execute()` 方法，通常也声明 `undo()` 方法。
- **ConcreteCommand（具体命令）**：持有对 Receiver 的引用，实现 `execute()` 和 `undo()` 的具体逻辑，并保存执行前的状态快照（Snapshot）。
- **Receiver（接收者）**：实际执行操作的对象，如游戏场景中的 `GameObject`。
- **Invoker（调用者）**：持有命令历史栈，负责调用 `execute()` 并管理 Undo/Redo 栈。

以伪代码表示抽象命令接口：

```
interface ICommand {
    void execute();
    void undo();
}
```

### Undo/Redo 栈机制

Undo/Redo 的实现依赖两个栈：`undoStack`（撤销栈）和 `redoStack`（重做栈）。其操作规则如下：

- **执行新命令**：调用 `cmd.execute()`，将 `cmd` 压入 `undoStack`，同时**清空** `redoStack`（因为新分支产生，旧的重做历史失效）。
- **撤销操作**：从 `undoStack` 弹出栈顶命令，调用其 `undo()`，再将其压入 `redoStack`。
- **重做操作**：从 `redoStack` 弹出栈顶命令，调用其 `execute()`，再将其压入 `undoStack`。

Unreal Engine 的编辑器系统（`FTransaction` 与 `GEditor->UndoTransaction`）和 Unity Editor 的 `Undo.RegisterCompleteObjectUndo` API，都是这一双栈结构的工业级实现。Unreal 的撤销栈默认保存最多 **16** 步历史记录（可通过 ini 配置修改）。

### 命令队列与宏命令

命令模式天然支持**命令队列**：将若干 `ICommand` 对象按时序存入一个队列，由调度器逐帧或逐帧批量执行。这在 RTS（即时战略）游戏的单位行为系统中极为常见——玩家下达"移动→攻击→撤退"三条指令后，单位依次出队执行每条命令，中途可随时插队或清空队列。

**宏命令（Macro Command）**是命令模式的组合变体：创建一个 `CompositeCommand`，其内部包含一个 `ICommand` 列表，`execute()` 依次调用所有子命令，`undo()` 则以**逆序**依次调用所有子命令的 `undo()`。这样，一次复杂操作（如"批量删除10个场景节点"）可以作为一个原子操作被整体撤销。

### ConcreteCommand 必须保存前状态

每个具体命令必须在 `execute()` 执行之前记录足够的状态信息，否则无法实现 `undo()`。例如，一个"移动物体"命令需保存物体的**执行前位置**（previousPosition），而非执行后位置：

```
class MoveCommand : ICommand {
    GameObject target;
    Vector3 newPosition;
    Vector3 previousPosition;  // 执行前快照

    void execute() {
        previousPosition = target.position;
        target.position = newPosition;
    }
    void undo() {
        target.position = previousPosition;
    }
}
```

## 实际应用

**游戏关卡编辑器**：Godot Engine 的 `EditorUndoRedoManager` 类使用命令模式管理编辑器内所有可撤销操作，每个操作被封装为含有 `do_method`（正向方法）和 `undo_method`（撤销方法）的命令对象，并统一由历史管理器维护。

**脚本录制与回放**：将玩家的每帧输入封装成命令对象并序列化存储，即可实现游戏录像或 AI 训练数据采集。《星际争霸2》的录像文件本质上是一系列命令对象的序列化流。

**网络同步中的锁步协议（Lockstep）**：多人游戏中，所有客户端不直接传输游戏状态，而是将玩家操作封装为命令对象广播，每帧所有客户端执行相同的命令序列，保证确定性同步。

## 常见误区

**误区一：将命令对象与策略模式混淆。** 策略模式（Strategy Pattern）封装的是**算法本身**（"如何做"），可以在不同上下文中反复调用，本身不保存状态，也没有 `undo()` 语义。命令模式封装的是**一次具体操作**（"做什么"），必须保存执行前的状态快照以支持撤销，二者目的截然不同。

**误区二：认为 `undo()` 只需反向执行即可，无需保存前状态。** 对于非幂等操作（如旋转物体 45 度），`execute()` 的逆操作（旋转 -45 度）在多次调用后可能因浮点精度误差累积而导致状态偏差。正确做法是在命令对象中明确保存 `previousRotation`（执行前的旋转四元数），`undo()` 时直接赋值恢复，而非做逆运算。

**误区三：命令队列等同于消息队列。** 消息队列（Message Queue）传递的是无状态的数据消息，接收方自行决定如何处理；而命令队列传递的是封装了接收者引用和具体行为的命令对象，执行逻辑内置于命令对象本身。二者在解耦层次和职责归属上有本质区别。

## 知识关联

**前置概念**：理解**策略模式**有助于区分"封装算法"与"封装操作"的不同意图；**脚本系统概述**提供了命令对象在脚本解释器中运行的宿主环境背景，例如脚本语言的 `Action` 或 `Closure` 常被用作轻量级命令对象的替代实现。

**横向联系**：命令模式与**观察者模式**经常协同出现——观察者模式负责检测输入事件，命令模式负责将事件包装成可执行、可撤销的命令对象。在 Unity 的 Input System 包（2019年发布）中，`InputAction` 的 `performed` 回调触发命令对象创建，即是二者的典型协作场景。

**工程权衡**：命令模式的代价是每个可撤销操作都需要一个独立的类（或闭包），当操作种类超过数十种时，类爆炸（Class Explosion）问题会影响代码可维护性。现代引擎常通过反射机制自动生成命令类，或使用带有泛型的通用命令模板 `GenericCommand<TReceiver>` 来缓解这一问题。
