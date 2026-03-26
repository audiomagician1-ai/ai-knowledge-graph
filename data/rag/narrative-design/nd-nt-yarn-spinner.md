---
id: "nd-nt-yarn-spinner"
concept: "Yarn Spinner"
domain: "narrative-design"
subdomain: "narrative-tools"
subdomain_name: "叙事工具"
difficulty: 3
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.2
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

# Yarn Spinner

## 概述

Yarn Spinner 是专为 Unity 引擎设计的开源对话脚本工具，由 Secret Lab 团队（《Night in the Woods》的幕后制作公司）于 2016 年首次发布。它使用一种名为 Yarn 的脚本语言，语法设计上刻意模仿 Twine 的简洁风格，使叙事设计师无需深入学习 C# 即可编写分支对话。截至 Yarn Spinner 2.x 版本，该工具已成为 Unity Asset Store 上下载量最高的对话管理插件之一。

Yarn Spinner 最初是为开发《Night in the Woods》而创建的内部工具，游戏中数千行对话均通过 Yarn 脚本驱动。正是这款游戏的商业成功，使 Secret Lab 决定将其开源并持续维护。与 Ink 语言相比，Yarn Spinner 与 Unity 的集成更为原生——它直接通过 Unity Package Manager 安装，并提供与 Unity UI 组件绑定的内置对话视图系统。

Yarn Spinner 在叙事游戏开发中的重要性体现在它弥合了叙事设计师与程序员之间的工作流隔阂。编剧可以在 VS Code 配合官方 Yarn Spinner 扩展插件独立编写和预览对话树，完成后直接导入 Unity，程序员只需通过 `YarnCommand` 和 `YarnFunction` 属性将游戏逻辑钩入脚本，双方可以并行开发。

## 核心原理

### Yarn 语言的节点结构

Yarn 脚本的基本组织单位是**节点（Node）**，每个节点由三行元数据头部和正文内容构成：

```
title: StartConversation
tags:
---
角色A: 你好，旅行者。
-> 你好。
    角色A: 欢迎来到小镇。
-> 再见。
    <<stop>>
===
```

`---` 标记节点开始，`===` 标记节点结束，这与 Ink 的 `=== knot_name ===` 写法存在明显差异。节点之间通过 `<<jump NodeName>>` 命令跳转，而非 Ink 的 `-> divert` 语法。每个 `.yarn` 文件可以包含多个节点，整个项目的所有节点会被 Yarn Spinner 编译为一个统一的对话图。

### 变量系统与条件分支

Yarn 语言支持三种原生变量类型：`Bool`、`Number` 和 `String`，变量名以 `$` 符号开头（例如 `$player_name`、`$has_key`）。条件判断语法使用 `<<if>>`、`<<elseif>>`、`<<else>>`、`<<endif>>` 块：

```
<<if $has_key == true>>
    守卫: 你可以通过。
<<else>>
    守卫: 你没有钥匙。
<<endif>>
```

Yarn Spinner 2.0 引入了**智能变量（Smart Variables）**概念，允许通过 `<<declare>>` 在节点外声明带默认值的变量，解决了 1.x 版本中变量必须在 C# 端预先注册才能使用的痛点。变量持久化需要开发者实现 `IVariableStorage` 接口，官方提供了 `InMemoryVariableStorage` 作为开发阶段的默认实现。

### 命令与函数的 C# 绑定机制

Yarn Spinner 与 Unity 游戏逻辑的交互通过两种机制实现：

**命令（Commands）**：使用 `<<commandName param1 param2>>` 语法，在 C# 端通过 `[YarnCommand("commandName")]` 属性标记对应方法。命令支持协程（`IEnumerator`），这使得对话可以等待动画播放完成后再继续推进。

**函数（Functions）**：使用 `<<set $result = functionName(arg)>>` 调用，在 C# 端通过 `[YarnFunction("functionName")]` 注册，必须有返回值（`bool`、`float` 或 `string`）。这一机制允许 Yarn 脚本查询游戏状态，例如检查玩家背包中某物品的数量。

## 实际应用

在《A Short Hike》和多款独立 Unity 游戏中，Yarn Spinner 被用于实现 NPC 的**状态感知对话**：编写一个名为 `TalkToFarmer` 的节点，根据 `$weather_is_raining` 和 `$crop_harvested` 两个布尔变量呈现不同的对话内容，无需程序员介入即可由叙事设计师直接完成所有分支的编写。

Yarn Spinner 的**本地化（Localisation）**系统是其 2.x 版本的重大特性。工具链会为每行对话自动生成唯一的 Line ID（格式如 `line:farmer-greeting-001`），配合 CSV 格式的字符串表，翻译人员可以独立于 `.yarn` 源文件进行本地化工作，不会因对话内容修改而导致 ID 失效——只要原始行未被删除，其 ID 就会被保留。

在多人叙事设计团队的版本管理实践中，`.yarn` 文件作为纯文本文件可以直接纳入 Git 管理，合并冲突的可读性远高于 Unity 的 YAML 场景文件，这使得 Yarn Spinner 成为强调叙事协作开发流程的团队的首选工具。

## 常见误区

**误区一：认为 Yarn Spinner 可以完全替代程序员工作**。Yarn 脚本本身无法驱动角色移动、触发过场动画或管理存档，所有此类操作必须通过 `[YarnCommand]` 在 C# 端实现。初学者常见错误是在 `.yarn` 文件中写下 `<<playAnimation "wave">>` 后，发现没有任何效果，原因是 Unity 场景中没有任何 `MonoBehaviour` 注册了名为 `playAnimation` 的命令。

**误区二：混淆 Yarn Spinner 1.x 和 2.x 的 API**。两个版本之间存在破坏性变更：1.x 使用 `DialogueRunner.AddCommandHandler()` 方法注册命令，2.x 改为特性（Attribute）注册方式；1.x 的对话视图使用 `DialogueUI` 组件，2.x 将其拆分为 `DialogueRunner`、`LineView` 和 `OptionsListView` 三个独立组件。网络上大量教程仍基于 1.x 版本，直接复制代码到 2.x 项目会导致编译错误。

**误区三：将 Yarn 节点等同于游戏场景**。一个 Yarn 节点应代表一段具体的对话交互，而非整个游戏关卡或地点。将大量无关对话堆放在单一节点中（超过 50 行对话分支）会导致节点难以维护，正确做法是按交互主题拆分节点并通过 `<<jump>>` 串联。

## 知识关联

有 Ink 脚本语言基础的学习者会发现，Yarn 的选项语法 `->` 与 Ink 的 `*`（一次性选项）和 `+`（可重复选项）存在对应关系，但 Yarn **不区分**这两种选项类型——所有选项在每次到达时均会显示，控制选项可见性必须显式使用 `<<if>>` 条件块包裹，而非依赖 Ink 的自动消耗机制。

Ink 的 `-> DONE` 和 `-> END` 在 Yarn 中对应 `<<stop>>` 命令，但行为略有差异：`<<stop>>` 仅暂停对话，对话历史会被保留，下次调用 `DialogueRunner.StartDialogue("NodeName")` 时可以重新进入任意节点，这与 Ink 故事对象的线性推进模型有根本性区别。

掌握 Yarn Spinner 之后，进阶方向包括为其编写自定义 `DialogueView`（实现打字机效果、角色立绘切换等个性化表现层）以及研究 Yarn Spinner 的编译器架构——Yarn 脚本会被编译为基于栈机器的字节码（`.yarnc` 文件），理解这一底层机制有助于为大型项目优化对话系统的运行时性能。