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
quality_tier: "B"
quality_score: 44.7
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
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

Articy:Draft 是由德国软件公司 Nevigo GmbH 于 2012 年正式发布的专业叙事设计软件，专为游戏开发者、编剧和叙事设计师提供结构化的故事创作与对话管理平台。2017 年，Nevigo 被 Codecks 的母公司收购后，Articy:Draft 3 作为独立产品在 Steam 及官网发布，并推出了免费的 Free 版本（限制 30 个对象节点），使中小型工作室也能以低成本接入专业叙事工作流。

Articy:Draft 的核心价值在于它同时解决了三个传统叙事工具难以兼顾的问题：角色与世界数据库的统一管理、可视化流程图编辑，以及与游戏引擎的直接导出集成。它通过将人物档案、地点信息、对话流程、任务逻辑整合在同一个项目文件中，消除了 Excel 表格、Word 文档和专属对话工具之间频繁切换导致的数据不一致问题。对于具有分支叙事需求的 RPG、视觉小说和冒险类游戏，Articy:Draft 提供了从概念到引擎就绪资产的完整制作管道。

## 核心原理

### 对象模型与模板系统

Articy:Draft 使用基于对象的数据模型，所有内容——无论是角色、地点、对话节点还是任务——都以"实体（Entity）"的形式存储，并通过**模板（Template）**定义其属性结构。设计师可以创建一个名为"NPC角色"的模板，为其附加"好感度（Affection）: Integer"、"阵营（Faction）: String"等自定义属性，随后在项目中所有同类角色实例上批量引用和编辑这些属性。这种模板继承机制避免了为每个角色单独手动填写重复字段的工作，也保证了属性命名在整个项目中的一致性，便于后续脚本逻辑引用。

### 流程图编辑器与节点类型

Articy:Draft 的流程图（Flow）编辑器是其最核心的可视化工作区，支持以下五种主要节点类型：
- **对话节点（Dialogue Fragment）**：存储具体台词，可绑定说话角色实体和语音文件路径；
- **集线器节点（Hub）**：分发多条出边，用于无条件并行叙事岔路；
- **条件节点（Condition）**：通过 Expresso 脚本语言（Articy 内置的类 C# 表达式语言）判断变量真假来决定走向；
- **指令节点（Instruction）**：执行变量赋值等副作用操作，例如 `GameState.PlayerGold -= 50`；
- **跳转节点（Jump）**：引用项目中任意其他流程图的入口，实现跨场景叙事复用。

Expresso 脚本支持直接引用实体属性，语法格式为 `EntityName.PropertyName`，例如 `Merchant_Hira.Affection >= 3` 可直接在条件节点中判断特定角色的好感度阈值。

### 项目导出与引擎集成

Articy:Draft 提供官方 Unity 插件（articy:draft Unity Importer，开源于 GitHub）和 Unreal Engine 插件，导出格式为基于 JSON 的 `.articyue4` 或 `.articydraft` 文件。Unity 插件通过生成 C# 静态类来映射所有模板属性，使程序员在引擎端可以用强类型代码访问 `ArticyDatabase.GetObject<NPC>("Merchant_Hira").Template.CharacterFeature.Affection`，而无需手动解析 JSON 字符串。该插件还支持**运行时数据库（Runtime Database）**，允许在游戏运行时动态修改实体属性并与 Articy 流程执行器同步，实现状态持久化。

## 实际应用

**《太空堡垒卡拉狄加：死刑》（Battlestar Galactica Deadlock）** 的开发团队 Black Lab Games 公开表示使用 Articy:Draft 管理游戏内超过 12,000 行对话及相关任务条件，其任务分支逻辑直接通过 Articy 流程图维护，并导出至 Unity 运行时执行，大幅减少了程序员介入纯叙事逻辑修改的需求。

在独立开发场景中，Articy:Draft 的典型应用流程为：①叙事设计师在 Flow 编辑器中完成对话分支；②使用内置的**演练模式（Playthrough Mode）**在 Articy 内部模拟对话走向，无需启动游戏引擎即可验证分支逻辑；③通过 Export 功能生成 JSON 文件交付给引擎端；④程序员通过官方插件的 `ArticyFlowPlayer` 组件驱动运行时对话播放，叙事设计师后续修改台词或条件后只需重新导出，无需改动引擎代码。

Articy:Draft 的**全局变量（Global Variables）**面板允许集中定义整个项目所用的布尔、整数、浮点和字符串型变量，这些变量在 Expresso 条件节点中直接可用，也会随导出文件同步至引擎端的运行时变量命名空间，确保叙事逻辑与游戏状态共享同一套数据源。

## 常见误区

**误区一：将 Articy:Draft 当作纯粹的写作工具**
部分初学者将 Articy:Draft 仅用于打字记录台词，忽略了其模板系统和条件脚本的功能，等同于用专业 DAW 软件只播放 MP3。正确的使用方式是从项目初期就设计实体模板和全局变量结构，让对话节点的条件分支与游戏设计文档中的状态变量直接对应，而非后期手动翻译。

**误区二：认为 Expresso 脚本功能足以替代引擎端逻辑**
Expresso 语言设计目标是轻量级条件判断与变量操作，不支持循环结构和复杂数据类型，无法执行库存系统遍历或 AI 行为树调用等引擎层逻辑。试图在 Articy 内部的指令节点中编写复杂游戏逻辑会导致维护困难；正确做法是在引擎端注册**自定义函数（Custom Script Methods）**供 Expresso 调用，保持 Articy 侧逻辑的简洁性。

**误区三：混淆"流程图嵌套"与"跳转节点"的使用场景**
Articy:Draft 支持将一个流程图作为子节点嵌套在另一个流程图中（Dialogue 内嵌 Dialogue），也支持通过跳转节点引用外部流程。嵌套适合封装可复用的对话片段（如通用问候语），跳转适合在不复制数据的前提下引用其他场景的流程入口；若将大型主线流程全部嵌套为单一超级流程图，会导致 Articy 渲染性能下降并使协作编辑出现文件锁冲突。

## 知识关联

学习 Articy:Draft 之前，理解**对话中间件**的概念有助于明确 Articy 在整个叙事技术栈中所处的位置——它属于"设计-导出"层，而非运行时执行引擎本身，这与 Yarn Spinner 或 Ink 等运行时解释型工具存在架构差异。掌握 Articy:Draft 的流程图节点结构和数据模型后，可以进一步学习**叙事图可视化**的设计原则，理解如何评估和优化分支密度与可读性；同时，Articy 的流程图编辑器本身即是**节点式对话编辑器**的典型实现范例，对比研究其节点类型设计与 Twine、Dialogue System for Unity 等工具的差异，能够帮助叙事设计师在不同项目规模和技术约束下做出合理的工具选型决策。