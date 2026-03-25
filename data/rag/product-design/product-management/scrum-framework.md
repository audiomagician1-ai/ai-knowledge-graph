---
id: "scrum-framework"
concept: "Scrum框架"
domain: "product-design"
subdomain: "product-management"
subdomain_name: "产品管理"
difficulty: 2
is_milestone: false
tags: ["敏捷"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.438
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Scrum框架

## 概述

Scrum框架是一种用于管理复杂产品开发的轻量级敏捷框架，由Jeff Sutherland和Ken Schwaber于1993年共同创立，并在1995年的OOPSLA大会上正式发表论文加以描述。Scrum这个名称来源于橄榄球运动中的"争球"动作，象征团队协作推进目标的精神。2020年，Schwaber和Sutherland联合发布了最新版《Scrum指南》，将Scrum精简为仅13页的精华描述，删去了大量规定性内容，强调原则而非细节。

Scrum框架将产品开发拆解为固定长度的迭代周期（Sprint），每个Sprint通常为1至4周，其中以2周最为常见。框架规定了三种角色、五个仪式和三种工件，形成一套完整的闭环工作机制。它之所以在产品管理领域广泛采用，在于它将不可预测的复杂开发工作转化为可检视、可适应的短周期交付节奏，帮助团队在需求频繁变化的环境中持续产出可用增量。

## 核心原理

### 三种核心角色

Scrum框架明确规定了三个且仅三个角色，任何额外的"项目经理"或"技术负责人"头衔在纯粹的Scrum中并不存在。

**产品负责人（Product Owner）** 负责维护和排序产品待办列表（Product Backlog），对产品价值最大化负全责。产品负责人有且只有一人，其决策对团队具有约束力——开发者不能绕过产品负责人接受来自外部利益相关者的需求。

**Scrum Master** 是框架的守护者和服务型领导者，职责是清除障碍、辅导团队遵循Scrum理论，同时帮助组织理解Scrum。Scrum Master不是项目经理，不分配任务，不对交付结果负直接责任。

**开发者（Developers）** 是实际完成工作的人，负责创建每日可发布的产品增量。2020年版《Scrum指南》将原来的"开发团队"更名为"Developers"，并明确指出这一角色包含所有承担Sprint工作的人员，不限于程序员，也包括设计师、测试工程师等。

### 五个Scrum仪式

Scrum规定了五个正式事件，每个事件都有明确的时间盒（Timebox）限制：

- **Sprint本身**：1至4周的固定时间盒，是所有其他事件的容器
- **Sprint规划（Sprint Planning）**：Sprint开始时举行，时间盒为每周Sprint对应最多2小时，即4周Sprint最长8小时
- **每日Scrum（Daily Scrum）**：每天15分钟，由开发者自行组织，检视Sprint目标进展
- **Sprint评审（Sprint Review）**：Sprint末尾举行，向利益相关者展示增量并获取反馈，时间盒为每周Sprint对应最多1小时
- **迭代回顾（Sprint Retrospective）**：Sprint评审之后举行，团队内部审视工作方式，时间盒为每周Sprint对应最多45分钟

### 三种Scrum工件

**产品待办列表（Product Backlog）** 是产品所有已知需求的唯一来源，由产品负责人负责排序，条目越靠前越详细、估算越准确。其承诺（Commitment）是产品目标（Product Goal）。

**Sprint待办列表（Sprint Backlog）** 由Sprint目标、从产品待办列表中选取的条目以及完成这些工作的计划组成，属于开发者的工作计划，其承诺是Sprint目标（Sprint Goal）。

**增量（Increment）** 是每个Sprint产出的、满足完成定义（Definition of Done）的可用产品功能集合。完成定义是判断增量是否满足质量标准的正式描述，由Scrum团队制定并严格遵守。

## 实际应用

在实际产品开发中，一个典型的2周Scrum Sprint运作如下：第1天上午举行不超过4小时的Sprint规划，产品负责人介绍优先级最高的待办条目，团队讨论并拆解任务，共同确定Sprint目标；第2天至第13天，每天举行15分钟的每日Scrum，团队成员相互同步进展和障碍；第14天下午先举行1小时Sprint评审，邀请业务方查看实际可运行的功能，再举行不超过1.5小时的迭代回顾，团队讨论流程改进点并记录下一Sprint要实施的改进措施。

在SaaS产品团队中，产品待办列表通常包含用户故事（如"作为注册用户，我希望能通过微信一键登录，以节省输入密码的时间"）和技术债条目。产品负责人每周至少进行一次Backlog梳理（Backlog Refinement），确保排名靠前的条目足够详细，满足进入下一个Sprint规划的"就绪定义（Definition of Ready）"。

## 常见误区

**误区一：每日Scrum是进度汇报会议。** 许多团队错误地将每日Scrum演变为对管理层的逐一汇报，每人回答"昨天做了什么、今天做什么、有没有障碍"三个问题。2020年版《Scrum指南》已删去这三个固定问题，强调每日Scrum的唯一目的是开发者检视Sprint目标进展并调整计划，形式由团队自行决定。Scrum Master和产品负责人不是每日Scrum的必须参与者，除非他们同时承担开发工作。

**误区二：Scrum Master必须是全职专职角色。** 在小型团队中，Scrum Master可以由团队成员兼任，《Scrum指南》并未要求Scrum Master必须是专职岗位。然而，同一人同时担任Scrum Master和产品负责人则是明确被禁止的，因为这两个角色存在利益冲突——产品负责人追求最大化价值交付，而Scrum Master的职责之一是保护团队不被过度压榨。

**误区三：Sprint中途可以随意加入新需求。** Sprint一旦开始，Sprint目标不变，产品负责人不应在Sprint进行中添加新工作。如果出现紧急需求，正确的处理方式是在当前Sprint结束后通过Sprint规划纳入，或在极端情况下与Scrum Master协商取消当前Sprint（这是产品负责人的唯一特权）。频繁中途加需求是Sprint目标失去意义的首要原因。

## 知识关联

Scrum框架建立在Sprint规划的基础上——Sprint规划是Scrum五个仪式的起点，理解如何制定Sprint目标、拆解待办条目是正确运行Scrum的前提。没有有效的Sprint规划，产品待办列表与Sprint待办列表之间的转化就无法完成，后续所有仪式也失去依托。

在掌握Scrum框架之后，**看板方法**提供了与Scrum截然不同的流式管理视角：看板没有Sprint时间盒，通过在制品限制（WIP Limit）控制工作流，更适合运维类或需求持续到达的场景。许多团队将Scrum与看板结合形成Scrumban混合实践。**迭代回顾**则是Scrum框架中持续改进机制的具体操作方法，专注于如何有效地引导回顾会议、选择改进实验，是将Scrum框架真正落地为团队学习机器的关键实践。