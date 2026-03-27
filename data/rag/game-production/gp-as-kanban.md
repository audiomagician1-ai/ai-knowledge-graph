---
id: "gp-as-kanban"
concept: "Kanban方法"
domain: "game-production"
subdomain: "agile-scrum"
subdomain_name: "敏捷/Scrum"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.7
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Kanban方法

## 概述

Kanban（看板）方法起源于丰田汽车公司20世纪40年代的精益生产体系，由大野耐一于1953年前后正式提出，最初用于控制零件补货流动。2007年，David J. Anderson将其引入软件开发领域，出版《Kanban: Successful Evolutionary Change for Your Technology Business》，系统性地定义了适用于知识工作的Kanban实践。游戏开发团队自2010年代起广泛采用Kanban，特别用于美术资产生产、QA测试流水线和运营维护阶段。

与Scrum以固定Sprint周期为核心不同，Kanban不设迭代边界，工作项在准备好时立即进入流程，完成后立即交付。这一特性对游戏开发中任务粒度差异巨大的场景尤为适合——一个角色模型可能需要3天，一段过场动画可能需要3周，强制把它们塞进同一个2周Sprint往往制造浪费。Kanban通过可视化工作流和限制在制品数量（WIP Limit）来暴露瓶颈、提升流动效率，而不是通过固定节奏来创造交付节律。

## 核心原理

### 看板墙与工作流可视化

看板墙是Kanban方法的物理或数字载体，将工作流拆解为若干列（Column），每列代表一个工作状态。一个典型的游戏美术生产看板墙可能包含：**待办（Backlog）→ 设计（Design）→ 建模（Modeling）→ 贴图（Texturing）→ 审核（Review）→ 集成（Integration）→ 完成（Done）**。每张卡片代表一个工作项，卡片上标注负责人、预估规模（通常用T恤码S/M/L/XL）和进入当前列的日期。进入日期是计算周期时间（Cycle Time）的起点，是衡量流动速度的关键数据。

### WIP限制（Work In Progress Limit）

WIP限制是Kanban方法中最具区分性的机制。每一列或每个工人都被赋予一个最大并发任务数，超过此数量则不允许拉入新任务。根据利特尔法则（Little's Law）：

**平均周期时间 = 平均WIP数量 ÷ 平均吞吐量**

即 **CT = WIP / TH**，其中CT为Cycle Time，WIP为在制品数量，TH为单位时间完成的工作项数（Throughput）。这个公式直接说明：当WIP增加而吞吐量不变时，每个任务从开始到完成的平均等待时间会线性增长。在游戏开发中，一个常见问题是程序员同时持有6-8张需求卡，看似"忙碌"，实则每张卡的推进速度极慢，前端功能等后端接口、UI等设计稿，全部形成队列堵塞。设置WIP限制（如每人不超过2张进行中卡片）会迫使团队优先完成已开始的工作，而不是不断开新任务。

### 流动效率（Flow Efficiency）

流动效率的计算公式为：

**流动效率 = 主动工作时间 ÷ 总周期时间 × 100%**

例如一个关卡设计任务的总周期时间是10天，但设计师实际工作仅花费2天，其余8天处于等待评审、等待资源或等待反馈状态，则流动效率为20%。行业研究显示，大多数软件和游戏开发团队的流动效率在5%–15%之间，意味着任务有85%–95%的时间在等待而非被推进。Kanban通过暴露这些等待时间（通常用卡片在某列停留的天数来显示，即"老龄化卡片"警告）来推动流程改进，而不是让问题隐藏在Sprint数字背后。

### 累积流图（Cumulative Flow Diagram，CFD）

累积流图是Kanban的核心数据仪表盘，X轴为日期，Y轴为工作项累计数量，每条彩色带代表一个工作状态的累计曲线。CFD的解读规则如下：

- **各色带的垂直宽度**代表该状态下当前的WIP数量。色带突然变宽意味着该状态积压增加，即该环节是当前瓶颈。
- **水平方向的宽度**（从一个状态进入到离开该状态之间的水平距离）代表平均周期时间。
- 健康的CFD中各色带应保持平行且宽度稳定；如果某条带持续扩张，说明该环节消化速度低于上游输入速度，必须采取行动。

在游戏项目中，CFD常用于监控QA阶段——如果"待测试"色带持续变厚，说明开发速度已超过QA消化能力，这是加人或降低开发节奏的信号。

## 实际应用

**游戏美术流水线管理**：育碧等大型工作室将Kanban用于3D资产生产线，设置明确的WIP限制：建模列最多5张卡，贴图列最多3张卡，每张卡对应一个资产包。当贴图列满员时，建模师不能继续新建模，而需要帮助贴图师消化存量，或者对流程进行改进。

**游戏运营与热更新**：游戏上线后的运营阶段（Live Ops）通常没有明确的版本周期，Kanban比Scrum更契合这种持续交付节奏。Bug修复、活动策划、平衡性调整可以按优先级随时拉入看板，完成即上线，无需等待Sprint结束。

**多项目并行的独立团队**：小型独立工作室同时维护多个项目时，Kanban可以通过泳道（Swimlane）将不同项目的工作项并排显示，帮助负责人直观判断资源分配是否合理，避免某个项目长期被挤压。

## 常见误区

**误区一：把看板墙等同于Kanban方法**。很多团队在Jira或Trello上建了一个带列的面板就宣称"我们在用Kanban"，但从不设置WIP限制，也不追踪周期时间和流动效率。这只是电子便利贴，不是Kanban方法。Kanban的价值在于WIP限制触发的行为改变——当某列满了，团队必须讨论为什么它满了，而不是继续添加卡片。

**误区二：认为Kanban没有计划，等于无管理**。Kanban取消了Sprint计划会议，但引入了补货会议（Replenishment Meeting）和服务类别（Service Classes）。服务类别将工作项按紧急程度和影响分为"加急（Expedite）""固定日期（Fixed Date）""标准（Standard）""无固定日期（Intangible）"四类，不同类别有不同的优先级规则和WIP策略，这是一套精细的优先级管理框架。

**误区三：Kanban适合所有游戏开发阶段**。在游戏主体研发（Alpha/Beta）阶段，团队往往需要Scrum式的节奏压力和固定发布节点来驱动里程碑进度。Kanban更适合前期原型探索（任务高度不确定，不适合Sprint估算）和上线后的运营维护（任务持续流入，无自然迭代边界）这两个阶段。

## 知识关联

学习Kanban之前，掌握**速率（Velocity）与燃尽图（Burndown Chart）**的概念有助于对比两种流量管理思路：燃尽图追踪剩余工作量（面向Sprint终点），而累积流图追踪流动状态（面向持续吞吐）。两者都关心"工作能否按时完成"，但燃尽图回答的是"我们在Sprint内进展如何"，CFD回答的是"我们的系统吞吐量是否稳定健康"。

在掌握Kanban之后，下一个自然延伸是**Scrumban**——一种混合方法，保留Scrum的迭代节奏和角色结构，同时引入Kanban的WIP限制和流动效率追踪。Scrumban特别适合从Scrum过渡到更成熟流程管理的游戏团队，团队无需完全放弃已熟悉的Sprint仪式，同时获得Kanban在瓶颈可视化方面的能力。