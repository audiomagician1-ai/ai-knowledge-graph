---
id: "se-dp-command"
concept: "命令模式"
domain: "software-engineering"
subdomain: "design-patterns"
subdomain_name: "设计模式"
difficulty: 2
is_milestone: false
tags: ["行为型"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 命令模式

## 概述

命令模式（Command Pattern）是一种行为型设计模式，其核心思想是将**操作请求封装为独立对象**，使得请求的发起者与执行者完全解耦。在命令模式中，一个"命令对象"包含了操作所需的所有信息：调用哪个对象、调用什么方法、传入什么参数。客户端只需持有命令对象的引用并调用其 `execute()` 方法，无需了解背后的具体逻辑。

命令模式最早在1994年由 Gang of Four（GoF）在《Design Patterns: Elements of Reusable Object-Oriented Software》中正式命名和描述。在此之前，类似思路已出现在早期图形界面框架中——菜单项、按钮等控件需要触发不同操作，而控件本身不应知道操作细节，这一现实需求直接催生了命令模式的抽象。

命令模式的重要性体现在三个具体能力上：**可撤销（Undo）**、**可重做（Redo）** 和**宏命令（Macro Command，即批量顺序执行多个命令）**。这三种能力在文本编辑器、图形编辑软件、游戏系统等场景中极为常见，而普通的直接调用方式无法自然支持这些能力，命令模式通过保存命令对象的历史记录来解决这一问题。

---

## 核心原理

### 四个角色的协作结构

命令模式由四个角色构成：

- **Command（抽象命令接口）**：声明执行方法 `execute()`，通常还声明 `undo()` 方法。
- **ConcreteCommand（具体命令类）**：实现 `execute()` 和 `undo()`，内部持有对 Receiver 的引用，并记录执行时的状态快照。
- **Receiver（接收者）**：真正执行业务逻辑的对象，例如一个文本编辑器的文档对象。
- **Invoker（调用者）**：持有命令对象，调用 `command.execute()`，并维护命令历史栈。

客户端负责将具体命令与接收者绑定，然后将命令交给调用者。调用者不需要知道命令做了什么，只管执行和存储。

### 撤销与重做的实现机制

撤销/重做功能依赖**两个命令栈**：`undoStack` 和 `redoStack`。

- 每次执行命令：将命令对象压入 `undoStack`，清空 `redoStack`。
- 撤销时：从 `undoStack` 弹出最近命令，调用其 `undo()` 方法，将该命令压入 `redoStack`。
- 重做时：从 `redoStack` 弹出命令，再次调用 `execute()`，将其重新压入 `undoStack`。

`undo()` 方法的正确实现要求命令在执行前**保存足够的状态**。例如一个"将文本颜色改为红色"的命令，必须在执行前记录原始颜色，`undo()` 才能将颜色还原。若某操作本质上不可逆（如发送网络请求），则通常将其标记为不支持撤销，或通过补偿操作（Compensating Command）模拟撤销。

### 宏命令的组合结构

宏命令（MacroCommand）是命令模式与组合模式（Composite Pattern）的结合体。宏命令本身也实现 `Command` 接口，其内部持有一个命令列表 `List<Command>`。调用宏命令的 `execute()` 时，它依次调用列表中每个命令的 `execute()`；调用 `undo()` 时，则**以相反顺序**逐一调用各子命令的 `undo()`。

```java
public class MacroCommand implements Command {
    private List<Command> commands = new ArrayList<>();

    public void execute() {
        for (Command cmd : commands) cmd.execute();
    }

    public void undo() {
        ListIterator<Command> it = commands.listIterator(commands.size());
        while (it.hasPrevious()) it.previous().undo();
    }
}
```

逆序撤销是宏命令中最容易忽略的细节：若命令A修改了命令B依赖的状态，正序撤销B会导致状态不一致。

---

## 实际应用

**文本编辑器（如 Microsoft Word）**：每次键盘输入、删除、格式调整都被封装成一个命令对象，存入历史栈。Word 的 Ctrl+Z 最多支持默认100步撤销，背后即是一个有容量上限的 `undoStack`（超出上限时移除最旧命令）。

**图形编辑软件（如 Photoshop）**：图层的移动、滤镜应用、色彩调整均为命令对象。Photoshop 的"历史记录"面板直观展示了命令栈的内容，允许用户跳转到任意历史状态（这是命令模式扩展实现，而非基本双栈模型）。

**数据库事务管理**：数据库的 `ROLLBACK` 机制与命令模式的 `undo()` 高度同源。每条 SQL 操作可视为一个命令，事务日志（Transaction Log）充当命令历史，`ROLLBACK` 相当于批量逆序撤销。

**任务队列与异步处理**：命令对象可被序列化后发送到消息队列（如 RabbitMQ），由不同进程或线程的接收者执行。此时命令对象充当数据传输容器，发送方与执行方可在不同机器上运行，体现了命令模式的时间解耦能力。

---

## 常见误区

**误区一：将业务逻辑写进命令类本身**

命令类应该是"传话人"而非"实干家"。具体业务逻辑（如文字渲染、文件读写）应属于 Receiver，命令类只负责调用 Receiver 的方法并保存必要状态。如果命令类直接包含大量业务代码，则 Receiver 角色形同虚设，违背了单一职责原则，也使命令类无法在不同 Receiver 间复用。

**误区二：认为所有命令都必须支持 `undo()`**

命令模式的接口中声明 `undo()` 是常见做法，但并非所有场景都需要撤销能力。对于"打印文件"或"发送邮件"这类副作用不可逆的命令，强行实现 `undo()` 反而会引入混乱。正确做法是在接口层提供默认空实现，由具体命令类按需覆盖，或通过抽象类提供 `canUndo()` 标志方法。

**误区三：混淆命令模式与策略模式**

两者都将"行为"封装为对象，但目的截然不同。策略模式用于在**运行时选择算法**，命令对象本身没有身份，只关心当前如何执行；命令模式则强调**命令对象的生命周期**——它被创建、存储、传递、执行、撤销，具有独立的身份和历史意义。一个命令对象在执行后仍然存活于历史栈中，而策略对象在切换后通常可以丢弃。

---

## 知识关联

命令模式不依赖其他设计模式作为前提，是初学设计模式时较早接触的行为型模式之一（GoF书中难度评级为较易理解）。

学习命令模式后，可以自然延伸到**责任链模式（Chain of Responsibility）**：两者都涉及请求的传递与处理，但责任链模式中请求沿链依次传递直到被处理，而命令模式中请求被封装后由明确的执行者处理——对比两者有助于理解"请求路由"的不同设计思路。

在**游戏开发领域**，命令模式有专门的扩展应用（即"命令模式——游戏"方向）：游戏角色的输入控制、AI行为序列、回放系统均大量使用命令模式，且游戏场景对命令的序列化、网络同步和时间步管理有更严格的要求，这是对本文基础命令模式概念的直接深化。