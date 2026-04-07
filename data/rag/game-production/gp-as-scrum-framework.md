---
id: "gp-as-scrum-framework"
concept: "Scrum框架"
domain: "game-production"
subdomain: "agile-scrum"
subdomain_name: "敏捷/Scrum"
difficulty: 2
is_milestone: true
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Scrum框架

## 概述

Scrum是一种用于管理复杂产品开发的轻量级框架，由Jeff Sutherland与Ken Schwaber于1995年在OOPSLA（面向对象编程、系统、语言与应用）大会上正式提出，并于2010年发布第一版《Scrum指南》。与瀑布式开发不同，Scrum将整个项目切分为固定长度的迭代周期（称为Sprint，通常为1至4周），每个Sprint结束后交付可工作的产品增量。

Scrum不是一套完整的流程或方法论，它刻意保持框架的精简性：整个框架由3种角色、5个事件（Events）和3个工件（Artifacts）构成，全部核心规则只需约13页的《Scrum指南》即可描述完整。正是这种轻量性，使Scrum成为游戏开发团队中最普遍采用的敏捷框架，尤其适合功能需求频繁变动、需要快速验证玩家反馈的游戏项目。

在游戏制作语境下，Scrum帮助团队解决一个核心难题：游戏的"好玩性"无法在项目初期被完整定义，必须通过反复迭代与测试来发现。每个Sprint结束时可玩的关卡或原型，就是这种迭代验证的具体产物。

## 核心原理

### 三种角色（Scrum Roles）

Scrum团队由三种且仅有三种正式角色构成，不存在"项目经理"这一传统职位。

**产品负责人（Product Owner, PO）** 是唯一负责管理和排序Product Backlog（产品待办列表）的人，对产品的最终价值负责。在游戏项目中，PO通常由制作人或主策划担任，负责决定哪个功能（如多人联机模式、技能系统）应优先进入开发队列。PO必须是一个人，而不是委员会。

**Scrum Master（SM）** 负责确保Scrum框架被正确理解和实践，同时作为服务型领导帮助团队移除阻碍（Impediments）。SM不是项目经理，不对工作内容发号施令，而是对过程负责。例如，SM会在每日站会超过15分钟时及时打断，并将深入讨论引导至会后处理。

**开发团队（Development Team）** 规模建议为3至9人，负责在Sprint内将Backlog条目转化为可交付的产品增量。团队具有跨职能性（Cross-functional），即团队内部应集齐完成工作所需的全部技能——程序、美术、QA等角色均包含其中，无需依赖团队外部资源即可完成Sprint目标。

### 五个正式事件（Scrum Events）

Scrum规定了5个具有固定时间盒（Timebox）的事件，缺少任何一个都意味着框架的不完整：

1. **Sprint**：所有其他事件的容器，时间盒为最长4周，一旦确定长度在项目期间不应改变。
2. **Sprint计划会议（Sprint Planning）**：时间盒为每周Sprint对应最多2小时，即4周Sprint最多8小时，团队在此确定Sprint目标和Sprint Backlog。
3. **每日Scrum（Daily Scrum）**：固定15分钟，仅供开发团队使用，检视进度并调整未来24小时的计划。
4. **Sprint评审（Sprint Review）**：时间盒为每周Sprint对应最多1小时，向利益相关者展示增量并收集反馈，Product Backlog可在此更新。
5. **Sprint回顾（Sprint Retrospective）**：时间盒为每周Sprint对应最多45分钟，团队检视自身工作方式并识别改进项，是Scrum推动持续改进的核心机制。

### 三个工件（Scrum Artifacts）

**Product Backlog** 是一份有序的、动态维护的需求列表，由PO全权负责。它永远不会"完成"，只要产品存在就会持续演化。

**Sprint Backlog** 由Sprint目标（Sprint Goal）、本Sprint选入的Product Backlog条目，以及实现这些条目的计划三部分组成。Sprint Backlog是开发团队在Sprint执行过程中的实时计划，只有开发团队才能修改它。

**产品增量（Increment）** 是Sprint结束时交付的、满足"完成定义（Definition of Done, DoD）"的所有工作总和。增量必须达到可用状态，即使PO决定不发布，增量本身也必须是可发布级别的。

## 实际应用

在一款手机RPG游戏的开发中，团队以2周为一个Sprint周期。PO在Product Backlog中维护了"装备强化系统""公会战功能""新手引导优化"等数十个条目，并按玩家价值排列优先级。在某个Sprint中，团队承诺实现"装备强化系统"这一Sprint目标，Sprint Backlog包含：UI设计稿验收、强化逻辑后端实现、动效制作、QA测试用例执行，共计约23个Story Points的工作量。

每日Scrum在每天上午10:00准时开始，持续不超过15分钟，团队站立讨论各自的工作进展与阻碍。SM注意到美术外包的强化动效因沟通延迟可能影响Sprint目标，立即在站会后与外包负责人处理这一阻碍。

Sprint第14天（即Sprint最后一天）下午，团队举行Sprint评审，向制作人和运营团队演示可运行的强化系统原型，运营团队现场提出"强化失败应有特殊音效反馈"的需求，PO将其记录并加入Product Backlog等待后续排期。

## 常见误区

**误区一：每日Scrum是向SM或PO的汇报会议。**
每日Scrum的参与主体是开发团队，SM和PO参与时仅作为观察者而非被汇报对象。每日Scrum的目的是开发团队内部检视Sprint Backlog的进展并调整计划，不是进行向上汇报的状态会议。将其变成汇报会会导致站会时长失控并损害团队自组织能力。

**误区二：Sprint中途可以随时向Sprint Backlog添加新需求。**
Sprint一旦开始，Sprint目标不能改变，Sprint Backlog的范围也不应被外部干预扩展。如果PO在Sprint中途发现新的高优先级需求，正确做法是加入Product Backlog，在下一个Sprint计划会议时再做决策，而不是打断当前Sprint。若Sprint目标已经完全无效，才可以由PO取消Sprint，但这在实践中极少发生。

**误区三：Scrum框架适用于所有类型的游戏工作。**
Scrum在功能开发和系统迭代中效果显著，但对美术资产量产（如大批量关卡资产制作）等任务更接近Kanban的适用场景。强行将所有工作纳入Sprint往往导致Sprint Backlog中充斥无法在2周内产生可验证增量的任务，团队应根据工作性质选择合适的实践方式。

## 知识关联

学习Scrum框架需要先理解敏捷基础中的迭代交付思想和响应变化原则——Scrum的Sprint本质上就是对敏捷宣言"可工作的软件高于详尽的文档"这一价值观的具体制度化体现。没有对迭代交付价值的认同，团队往往会在Sprint评审中交付"未完成"的工作，这与Scrum的增量定义直接冲突。

掌握Scrum框架的整体结构之后，Sprint计划（Sprint Planning）是最紧迫需要深入学习的下一个主题。Sprint计划会议中涉及的Story Point估算方法、Sprint Goal的撰写技巧，以及如何从Product Backlog中正确拆解Sprint Backlog条目，都是将Scrum框架真正落地的关键技能。Sprint计划做不好，整个Sprint的工作节奏都会受到影响。