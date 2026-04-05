---
id: "nd-nt-articy-draft"
concept: "Articy:Draft"
domain: "narrative-design"
subdomain: "narrative-tools"
subdomain_name: "叙事工具"
difficulty: 2
is_milestone: true
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# Articy:Draft

## 概述

Articy:Draft 是由德国公司 Nevigo（后被 Nukklear 收购）开发的专业叙事设计软件，最初于 2010 年发布，目前主流版本为 Articy:Draft 3，提供 Steam 和独立授权两种购买方式。该软件专为游戏编剧、叙事设计师和项目团队设计，将对话树、流程图、人物档案、世界观数据库整合在同一个工作环境中，避免了在 Word 文档、Excel 表格和自定义工具之间反复切换的碎片化工作流。

Articy:Draft 的核心定位是"叙事设计的一站式工具"，它既能作为独立的编剧创作软件使用，也能通过官方插件 articy:access 与 Unity 和 Unreal Engine 对接，将设计数据直接导出为可供游戏引擎读取的 JSON 或 XML 格式文件。这种"设计即数据"的工作方式，使得叙事设计师修改对话内容后无需程序员介入即可更新游戏内容，大幅缩短了迭代周期。该工具曾被《Disco Elysium》开发团队 ZA/UM 等知名游戏公司作为叙事原型阶段的参考工具，也被多家 AA 级工作室纳入正式生产流程。

对于初学者而言，Articy:Draft 的难度评级较低（2/9），前置知识只需了解对话中间件的基本概念，即知道"对话系统需要外部工具来组织和导出数据"这一逻辑，便可以快速上手其可视化界面。

## 核心原理

### 流程编辑器（Flow Editor）

Articy:Draft 的流程编辑器是创建对话和叙事分支的主要工作区。它采用节点图（Node Graph）结构，每个对话片段被称为"对话片段节点"（Dialogue Fragment），节点之间通过有向连线表示叙事走向。每个节点内部可以填写说话角色、台词文本、条件脚本（Condition）和指令脚本（Instruction）四类信息。

条件脚本使用 Articy 内置的 Expresso 脚本语言编写，例如：

```
GameVariables.PlayerReputation >= 50 && NPC.IsFriendly == true
```

这段代码决定了某条对话分支是否对玩家可见。指令脚本则用于在对话节点触发时修改变量值，例如 `GameVariables.QuestStage = 2`。Expresso 语法接近 C# 和 JavaScript 的简化版本，即便没有编程背景的叙事设计师也能在数小时内学会基本用法。

### 实体系统（Entity System）

Articy:Draft 将游戏世界的所有组成要素抽象为"实体"（Entity），包括角色（Character Entity）、地点（Location Entity）、物品（Item Entity）和自定义模板实体。每个实体拥有独立的属性面板，设计师可以在此定义角色的背景故事、语音风格标签、初始变量值等非编程性信息，这些信息会在对话节点中通过角色引用自动关联，确保同一个 NPC 在所有对话场景中使用统一的数据源。

实体模板（Template）功能允许团队统一定义属性字段格式，例如规定所有角色实体必须包含"派系""好感度初始值""是否可被杀死"三个字段，避免不同成员创建格式不一致的角色档案。

### 全局变量与本地化支持

Articy:Draft 内置全局变量管理器，支持布尔值（Boolean）、整数（Integer）、浮点数（Float）和字符串（String）四种类型。变量按命名空间（Namespace）分组管理，例如将所有任务进度变量归入 `QuestFlags` 命名空间，将玩家属性变量归入 `PlayerStats` 命名空间。

在本地化方面，Articy:Draft 3 支持直接在软件内创建多语言对照表，所有文本字段均可导出为 XLSX 格式交付翻译团队，翻译完成后再导入覆盖原始文本，全程不需要手动修改原始节点内容。

## 实际应用

一个典型的 RPG 游戏任务对话制作流程在 Articy:Draft 中如下进行：首先在实体系统中创建 NPC 角色档案，填写其背景属性；接着在流程编辑器中创建一个"对话容器"（Dialogue），在其中搭建分支对话树，每个分支节点通过条件脚本 `QuestFlags.MetKing == true` 控制可见性；对话制作完成后，通过 articy:access 插件的 Unity 集成包将整个数据库导出，程序员调用 `ArticyFlowPlayer` 组件播放对话，无需手动硬编码台词内容。

在多人协作场景中，Articy:Draft 的团队许可证（Team License）支持多人同时编辑同一项目文件，并通过内置的变更日志（Change Log）追踪每位成员的修改记录。编剧负责撰写台词，系统设计师负责配置条件变量，美术可以同步在实体面板中上传角色参考图，三条工作线互不阻塞。

## 常见误区

**误区一：将 Articy:Draft 视为游戏引擎的替代品。** Articy:Draft 只负责叙事数据的设计和组织，它输出的 JSON 文件需要在 Unity 或 Unreal 中通过专用插件解析和驱动，软件本身无法运行游戏逻辑或渲染画面。初学者常误以为在 Articy 中"跑通"了对话流程就等于游戏内对话也完成了，实际上还需要引擎端的集成工作。

**误区二：认为 Expresso 脚本等同于完整编程语言。** Expresso 是 Articy 专属的轻量级表达式语言，仅支持条件判断和简单赋值操作，不支持循环、函数定义或复杂数据结构。如果叙事逻辑需要调用游戏内的复杂系统（如战斗结算或动态生成内容），必须在游戏引擎端通过 C# 或 Blueprint 脚本监听 Articy 的回调事件来实现，而非在 Articy 内部完成。

**误区三：忽视模板设计阶段直接开始写对话。** 跳过实体模板定义、变量命名空间规划直接创建对话节点，会导致项目规模扩大后数据结构混乱、变量命名冲突，后期重构成本极高。Articy 官方文档建议在正式创作前先用 1-2 天时间完成"项目架构设计"（Project Setup），包括定义所有实体模板字段和全局变量命名规范。

## 知识关联

学习 Articy:Draft 前需要具备**对话中间件**的基本认知，即理解叙事设计工具在游戏开发管线中扮演"数据生产者"的角色，知道对话数据如何从设计工具流向游戏引擎。有了这一认知，才能理解 Articy 中每个配置选项（如条件脚本、变量命名空间）与引擎端实现之间的对应关系。

掌握 Articy:Draft 之后，可以自然过渡到**叙事图可视化**这一更宏观的概念，Articy 的流程编辑器正是叙事图可视化思维的具体实现，学习叙事图可视化的理论框架（如状态机与对话树的区别、非线性叙事的图论表达）将帮助设计师在 Articy 中做出更具结构性的设计决策。同时，Articy 的节点图界面是学习**节点式对话编辑器**通用操作逻辑的绝佳入门案例，其节点创建、连线、条件配置的工作模式与 Twine、Yarn Spinner 可视化插件等工具高度相似，形成可迁移的操作直觉。