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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

命令模式（Command Pattern）是一种行为型设计模式，其核心思想是将一个"请求"或"操作"封装为独立的对象。这个对象包含执行该操作所需的所有信息：目标对象（接收者）、操作方法名称以及方法参数。通过这种封装，发出请求的调用者与实际执行请求的接收者之间实现了完全解耦。

命令模式最早由 Gang of Four（四人帮）在1994年出版的《设计模式：可复用面向对象软件的基础》一书中正式归纳。其概念原型来自早期的图形界面工具包设计，开发者需要把菜单项、按钮点击等用户操作统一处理并支持撤销。命令模式解决了"操作"本身不能被存储、传递、排队的根本问题——普通的方法调用是即时执行且无法回溯的，而命令对象则是一等公民（first-class object），可以像数据一样被保存和传递。

命令模式的重要性体现在三个具体能力上：支持撤销（Undo）与重做（Redo）操作、支持操作的延迟执行与队列化、支持将多个命令组合为宏命令（Macro Command）批量执行。文本编辑器、数据库事务日志、游戏中的操作回放系统，都直接依赖命令模式的这些特性。

---

## 核心原理

### 四个角色的职责划分

命令模式由四个角色构成，每个角色有明确且不可替换的职责：

- **Command（命令接口）**：声明执行操作的统一接口，通常只包含 `execute()` 方法，以及支持撤销时所需的 `undo()` 方法。
- **ConcreteCommand（具体命令）**：实现 Command 接口，内部持有对 Receiver 的引用，在 `execute()` 中调用 Receiver 的具体业务方法，同时负责记录执行前的状态以供 `undo()` 使用。
- **Receiver（接收者）**：真正执行业务逻辑的对象，例如文本编辑器中的 `TextBuffer`，它知道如何插入字符、删除字符。
- **Invoker（调用者）**：持有命令对象的引用，调用 `execute()` 触发操作，但完全不知道 Receiver 是谁，也不知道具体执行了什么。

这四个角色缺一不可。如果直接让 Invoker 调用 Receiver 的方法，就退化为普通方法调用，失去了队列化和撤销能力。

### 撤销与重做的实现机制

撤销/重做是命令模式最典型的应用场景。实现方式是在 Invoker 中维护两个栈：`undoStack`（已执行命令栈）和 `redoStack`（已撤销命令栈）。

执行流程如下：
- 调用 `execute(command)`：将命令压入 `undoStack`，清空 `redoStack`。
- 调用 `undo()`：从 `undoStack` 弹出最近一条命令，调用其 `undo()` 方法，并将其压入 `redoStack`。
- 调用 `redo()`：从 `redoStack` 弹出命令，重新调用 `execute()`，并压回 `undoStack`。

每条 ConcreteCommand 必须在 `execute()` 执行前保存足够的状态快照。例如，一个"将第5行文字改为粗体"的命令，必须记录该行原始格式，否则 `undo()` 无法还原。这是命令模式中最容易设计失误的地方。

### 宏命令（Macro Command）

宏命令是命令模式的一种组合变体，通过将多个 Command 对象组合进一个 `MacroCommand` 对象来实现批量操作。`MacroCommand` 自身也实现 Command 接口，其 `execute()` 方法依次调用内部每条子命令的 `execute()`，其 `undo()` 方法则**逆序**调用每条子命令的 `undo()`。

逆序撤销是宏命令正确性的关键。假设宏命令依次执行了"创建文件夹 → 写入文件 → 设置权限"，撤销时必须先撤销"设置权限"，再撤销"写入文件"，最后撤销"创建文件夹"，否则会因依赖关系导致操作失败。

宏命令也支持嵌套：一个宏命令的子命令可以是另一个宏命令，从而形成树状的命令结构，这与组合模式（Composite Pattern）的结构完全一致。

---

## 实际应用

**文本编辑器的撤销系统**：Microsoft Word 的撤销历史默认保留最近100步操作，每一步（输入字符、格式变更、插入图片）都是一个 ConcreteCommand 对象，保存了操作内容和操作前状态。Ctrl+Z 和 Ctrl+Y 分别对应 `undo()` 和 `redo()` 调用。

**数据库操作日志**：关系型数据库的 WAL（Write-Ahead Logging）机制在逻辑上等价于命令模式——每条 SQL 语句被记录为带有参数的命令对象，事务回滚时通过逆序执行补偿操作（undo log）实现。

**GUI 工具栏按钮**：一个"保存"按钮、一个菜单项"文件→保存"、一个快捷键 Ctrl+S，三者绑定同一个 `SaveCommand` 对象。Invoker（按钮/菜单/快捷键监听器）只调用 `command.execute()`，而 `SaveCommand` 内部持有对 `DocumentService`（Receiver）的引用并调用其 `save()` 方法。这样修改保存逻辑只需改 `SaveCommand`，三个触发入口无需任何改动。

**任务队列与线程池**：将 `ConcreteCommand` 对象放入阻塞队列，由线程池中的工作线程逐条取出并调用 `execute()`。命令对象可以在不同线程间传递，因为它封装了执行所需的全部上下文。

---

## 常见误区

**误区一：认为 Receiver 可以省略，直接在 ConcreteCommand 中写业务逻辑**

这种做法让 ConcreteCommand 同时承担"封装操作"和"执行业务"两个职责，违反单一职责原则。当同一业务逻辑被多个命令复用时，就会出现代码重复。正确做法是 ConcreteCommand 只做调度，业务逻辑统一放在 Receiver 中。

**误区二：以为命令模式的 `undo()` 可以自动推导，不需要手动实现**

`undo()` 无法通过反射或自动化机制生成，因为同一操作在不同状态下的"逆操作"可能完全不同。例如"删除选中文字"的 `undo()` 是"在原位置重新插入被删除的文字"，这段文字的内容和位置必须在 `execute()` 时主动保存，没有框架能自动完成这件事。

**误区三：将命令模式与策略模式混淆**

两者都封装了"可替换的行为对象"，但目的不同。策略模式封装的是**算法的选择**（同一任务有多种做法，运行时选一种），命令模式封装的是**操作的请求**（操作需要被存储、排队、撤销）。命令模式的对象通常有 `undo()` 方法和历史记录机制，策略模式的对象没有。

---

## 知识关联

命令模式与**责任链模式**有直接的组合关系：可以将多个命令对象串联成责任链，按顺序尝试处理同一请求，每个命令决定是否处理或传递给下一个。这是理解责任链模式的一个具体切入点。

在**游戏开发场景**中，命令模式的应用进一步扩展为"输入处理与操作回放"架构：玩家的每一帧输入被封装为命令对象，不仅支持撤销，还可以序列化保存到磁盘、网络同步或用于 AI 行为回放。这是命令模式在游戏领域的专项延伸，构成下一阶段的学习内容。