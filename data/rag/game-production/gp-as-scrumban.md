---
id: "gp-as-scrumban"
concept: "Scrumban"
domain: "game-production"
subdomain: "agile-scrum"
subdomain_name: "敏捷/Scrum"
difficulty: 3
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 51.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Scrumban

## 概述

Scrumban是由Corey Ladas于2008年在其著作《Scrumban: Essays on Kanban Systems for Lean Software Development》中正式提出的混合方法论，将Scrum的迭代节奏与Kanban的流动管理结合为一套完整实践体系。它不是简单地把两套工具叠加使用，而是在Scrum的Sprint框架中引入Kanban的WIP限制（Work In Progress Limit）和拉动式调度机制，使团队既保留固定迭代周期的可预测性，又获得持续流动的灵活性。

在游戏开发中，Scrumban的出现解决了一个长期痛点：Scrum的Sprint边界对游戏开发中频繁发生的中途需求变更极不友好，而纯Kanban又缺乏足够的节奏感来驱动里程碑交付。Scrumban通过允许在Sprint中间插入新工作卡（只要不超出WIP上限），让美术资产的紧急返工、关卡设计的临时调整都能在不破坏整体交付承诺的前提下被消化。

该方法在独立游戏工作室中尤为流行，因为小团队成员往往需要同时承担策划、开发、测试多个角色，固定的Scrum仪式（如每日15分钟Standup）有时显得冗余，而Scrumban允许团队裁剪仪式，仅保留按需计划会议（On-Demand Planning）和定期回顾，降低了流程开销。

## 核心原理

### WIP限制与拉动调度的结合

Scrumban最关键的机制是将Kanban的WIP限制嵌入Scrum的看板列中。具体做法是为每个工作状态列（如"进行中""测试中"）设置数值上限，例如一支5人游戏开发团队通常为"进行中"列设置WIP上限为3，意味着同时只能有3张任务卡处于开发状态。当某列工作完成并低于触发阈值（Trigger Point）时，团队从待办列拉取新卡，而非由项目经理推送任务。这一拉动调度机制天然暴露了游戏美术与程序开发之间的产能瓶颈。

### 按需计划会议替代固定Sprint计划

传统Scrum要求每个Sprint开始时锁定Sprint Backlog，而Scrumban将此替换为触发式计划会议：只有当待办队列的任务数量下降到预设的触发点（通常为WIP上限的50%）时，才召开计划会议补充任务。对于游戏开发而言，这意味着关卡设计团队不必在Sprint第一天就冻结所有关卡目标，当上一关卡验收通过、队列空缺时再规划下一个即可，避免了在游戏原型验证阶段就强行细化后续设计的浪费。

### 迭代节奏保留与度量衔接

Scrumban保留了Sprint的时间盒概念，但其主要作用从"锁定承诺范围"转变为"提供度量和同步节奏"。团队每个Sprint（通常仍为1至2周）结束时统计吞吐量（Throughput）和周期时间（Cycle Time）而非传统的故事点速率（Velocity）。吞吐量是指单位迭代内完成的任务卡数量；周期时间是单张任务从进入"进行中"列到完成的耗时。这两个Kanban指标结合Sprint边界，能让制作人更准确地预测游戏功能的交付日期，比单纯的故事点燃尽图更贴近游戏制作的实际节奏。

### 服务类别分层管理

Scrumban引入了Kanban的服务类别（Service Class）概念，将游戏任务分为紧急通道（Expedite）、固定日期（Fixed Date）、普通（Standard）、无形收益（Intangible）四类。例如，游戏展会前的演示Build修复属于固定日期类，可绕过正常队列优先处理；而代码重构则归入无形收益类，仅在其他列WIP宽裕时才被拉取。这套分层机制让游戏开发中常见的"一切都是最高优先级"混乱局面得到系统性管控。

## 实际应用

**独立游戏原型阶段**：一支3人独立团队使用Scrumban时，可将WIP上限设为每人1张卡，共3张，迭代周期设为1周。每当游戏玩法验证卡片完成，立即从游戏概念文档中拉取下一个待验证机制，而不必等到周五计划会议。这让快速迭代的Gameplay Loop测试效率大幅提升。

**AA级游戏美术生产线**：美术总监使用Scrumban的看板墙管理概念原画→3D建模→绑定→特效的流水线，为每个工序设置WIP上限（如3D建模列上限为4个模型），当某工序积压严重时，下游工程师可直接通过看板数据识别并协助上游，而不必等到Sprint回顾会议才暴露问题。

**GaaS游戏（游戏即服务）的版本维护**：对于需要同时维护多个赛季内容的在线游戏，Scrumban的触发式计划会议特别适合：当已排期的赛季功能数量降至触发点以下时，召开补充计划会议，而不是在季初就试图规划所有后续赛季的所有细节。

## 常见误区

**误区一：认为Scrumban就是"用了看板列的Scrum"**。许多团队将物理看板引入Scrum后便声称自己在实践Scrumban，但如果没有WIP限制和拉动调度，只是换了一种任务可视化工具，并未真正引入Scrumban的核心流动机制。判断标准很简单：WIP限制是否被真正执行并触发团队行为改变？

**误区二：保留全套Scrum仪式导致双重开销**。部分游戏团队在引入WIP限制的同时仍维持Sprint计划、评审、回顾、每日Standup全套仪式，结果流程开销反而高于单纯Scrum。Scrumban的设计意图是根据实际需要裁剪仪式：每日Standup可改为异步更新，Sprint评审可与按需计划会议合并，而非机械叠加。

**误区三：将周期时间与Sprint速率混用**。从Scrum迁移到Scrumban的团队常犯的错误是继续用故事点速率来衡量交付能力，而忽视周期时间数据。在Scrumban中，一张任务卡从启动到完成平均耗时（周期时间）远比"这个Sprint我们完成了多少点"更能反映流程健康度，因为它直接揭示了游戏任务在哪个工序发生了等待和阻塞。

## 知识关联

学习Scrumban需要先理解Kanban方法中的WIP限制、看板列设计和拉动原则，因为Scrumban的核心改进点恰恰是将这些机制嵌入Scrum框架——如果不理解Kanban的流动管理哲学，就只会把Scrumban用成"贴了便利贴的Scrum"。同时，熟悉Scrum的Sprint时间盒和仪式体系是理解Scrumban"保留什么、裁剪什么"的前提。

掌握Scrumban之后，学习游戏敏捷适配（Game Agile Adaptation）时会遇到更复杂的情境：如何针对游戏开发中创意探索阶段（Pre-production）、内容生产阶段（Production）、收尾阶段（Post-production）的不同特征，动态切换WIP上限和迭代节奏，以及如何将Scrumban与游戏特有的里程碑评审（如Alpha/Beta/Gold）制度对接，是游戏敏捷适配课题的直接延伸。