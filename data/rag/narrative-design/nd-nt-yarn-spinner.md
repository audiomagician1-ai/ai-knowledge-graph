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
quality_tier: "S"
quality_score: 83.0
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


# Yarn Spinner

## 概述

Yarn Spinner 是专为 Unity 游戏引擎设计的对话与叙事脚本系统，由 Secret Lab 团队开发，最初作为 2013 年独立游戏《Night in the Woods》的内部工具而诞生。该工具使用一种名为 Yarn 的自定义脚本语言，让编写者能够以接近自然写作的格式定义游戏对话分支、角色台词和叙事逻辑，而无需深入掌握 C# 编程。

Yarn Spinner 2.0 版本于 2021 年发布，这次重大更新彻底重写了解析器架构，引入了虚拟机（VM）执行模式，并支持通过 NuGet 在非 Unity 环境中使用。目前 Yarn Spinner 已在 Unity Asset Store 免费提供，其核心运行时库基于 MIT 许可证开源，这使它成为中小型叙事游戏团队最常见的对话系统选择之一。

对于叙事设计师而言，Yarn Spinner 的意义在于它将程序员和编剧的工作流明确分离：编剧在 `.yarn` 文件中撰写对话内容，程序员通过 `DialogueRunner` 组件和 C# 事件系统将其接入游戏逻辑，两者通过明确的接口解耦，减少跨职能协作摩擦。

---

## 核心原理

### Yarn 语言语法结构

Yarn 脚本以**节点（Node）**为基本单位，每个节点以 `title:` 标签开头，以 `===` 结尾。节点内部的台词直接书写，选项使用 `->` 前缀标记，跳转使用 `<<jump NodeName>>` 命令实现：

```yarn
title: MeetGuard
---
守卫: 你是什么人？
-> 我是旅行者。
    <<jump TravellerPath>>
-> 我不需要向你解释。
    守卫: 那就离开这里。
===
```

变量以 `$` 符号开头（如 `$has_key`），支持布尔值、数字和字符串三种类型。条件语句格式为 `<<if $variable == value>> ... <<endif>>`，这套语法使不懂编程的编剧也能编写带状态判断的分支逻辑。

### DialogueRunner 与 Unity 集成机制

在 Unity 中，Yarn Spinner 的核心组件是 `DialogueRunner`，它充当 Yarn 虚拟机与 Unity 场景之间的桥梁。`DialogueRunner` 挂载在场景对象上，引用 `YarnProject`（编译后的对话资产）和 `VariableStorage`（变量存储组件）。对话的显示由单独的 `DialogueView` 组件处理，官方提供了 `LineView`（单行文本显示）和 `OptionsListView`（选项列表显示）两种默认实现，开发者也可以继承 `DialogueViewBase` 类自定义显示逻辑。

命令注册是 Yarn Spinner 与游戏逻辑交互的关键机制。通过在 C# 方法上添加 `[YarnCommand("command_name")]` 特性，或在 `DialogueRunner` 上调用 `AddCommandHandler()` 方法，可以让 Yarn 脚本内的 `<<command_name param>>` 语句触发具体的游戏行为（如播放动画、触发音效、修改游戏状态）。

### YarnProject 编译流程

`.yarn` 源文件在 Unity 编辑器中会被自动编译为 `YarnProject` 资产，这是一个包含字节码、元数据和本地化字符串表的二进制对象。Yarn Spinner 的本地化系统将所有对白文本提取到 CSV 格式的字符串表中，每条对白都有唯一的 Line ID（如 `line:a1b2c3`），便于多语言翻译团队独立处理文本而不触碰原始 `.yarn` 文件。

---

## 实际应用

**《Night in the Woods》**是 Yarn Spinner 最著名的使用案例，游戏中数万行对话均通过 Yarn 脚本管理，涵盖主线剧情、可选闲聊和环境交互三个层级。该游戏的成功证明了 Yarn Spinner 能够支撑叙事密集型项目的对话规模。

在实际项目工作流中，叙事设计师通常使用官方提供的 **Visual Studio Code 插件**（插件 ID：`SecretLab.yarn-spinner`）来获得语法高亮、节点跳转预览和错误提示功能。该插件还内置了对话节点图可视化视图，能够以图形方式展示节点之间的跳转关系，帮助设计师在不运行游戏的情况下审查对话结构。

对于需要动态生成台词的场景，Yarn Spinner 支持在 C# 端注册**函数（Function）**，通过 `AddFunction()` 方法将返回值传递给 Yarn 脚本中的表达式，例如 `<<if visited("NodeName")>>` 这种内置函数可检测某节点是否已被访问过，帮助编写根据游戏进度变化的对话内容。

---

## 常见误区

**误区一：认为 Yarn Spinner 与 Ink 功能完全等同，可随意互换。**
Ink 和 Yarn Spinner 虽然定位相似，但架构差异显著。Ink 拥有更强大的"织入（weave）"流程控制和内置的 `knot/stitch/divert` 层级结构，适合线性叙事密度更高的场景；Yarn Spinner 的节点模型更扁平，更适合开放世界中大量 NPC 各自维护独立对话树的架构。从 Ink 迁移到 Yarn Spinner 后，原来依赖 Ink 嵌套 `stitch` 的段落结构必须手动拆分为多个独立节点。

**误区二：以为可以直接在 Yarn 脚本中处理复杂游戏逻辑。**
Yarn 变量系统只支持三种基本类型，不支持数组、字典或对象引用。试图在 `.yarn` 文件内用变量模拟物品栏或复杂状态机的做法会迅速使脚本难以维护。正确做法是将复杂状态保留在 C# 的游戏逻辑层，通过自定义 `VariableStorage` 组件将 C# 属性映射为 Yarn 可读变量，而非在 Yarn 端存储原始数据。

**误区三：忽略 Line ID 管理导致本地化工作返工。**
若在项目中期才启用 Yarn Spinner 的本地化功能，此前没有 Line ID 的台词需要重新生成 ID，已完成的翻译文件与源文件的对应关系会完全断裂。正确做法是在项目早期就通过编辑器菜单"Yarn Spinner > Add Line Tags to Scripts"为所有对白自动添加唯一 ID，并将 `.yarn` 文件纳入版本控制，确保 ID 不会在多人协作中重复或丢失。

---

## 知识关联

学习 Yarn Spinner 之前掌握 **Ink 脚本语言**有助于建立对话分支设计的基本思维模型：理解"结（knot）"跳转的 Ink 用户能够快速类比 Yarn 的"节点（Node）"概念，但需要重新适应 Yarn 更依赖外部 C# 命令而非内置逻辑的设计哲学。

Yarn Spinner 的 `VariableStorage` 接口直接对接 Unity 的组件系统，因此对 Unity `MonoBehaviour` 生命周期和 C# 事件有基础认知的开发者能更顺畅地实现自定义存储逻辑。对于希望进一步扩展的团队，Yarn Spinner 的开源字节码格式和 NuGet 包结构也允许在 Godot 或自研引擎中移植使用，其 GitHub 仓库（`YarnSpinnerTool/YarnSpinner`）提供了完整的虚拟机规范文档供参考。