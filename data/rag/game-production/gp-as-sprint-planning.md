---
id: "gp-as-sprint-planning"
concept: "Sprint计划"
domain: "game-production"
subdomain: "agile-scrum"
subdomain_name: "敏捷/Scrum"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.438
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Sprint计划

## 概述

Sprint计划（Sprint Planning）是Scrum框架中每个Sprint正式开始前举行的时间盒会议。根据Scrum指南（2020年版）的规定，每个Sprint的计划会议时长上限为Sprint时长的8:1比例——即一个为期两周的Sprint对应最多4小时的计划会议，四周Sprint对应最多8小时。这个时间盒约束防止团队在讨论上无限延伸，迫使优先级决策在有限时间内完成。

Sprint计划由三个核心问题驱动：**这次Sprint为什么有价值？（Sprint目标）**、**这次Sprint能完成什么？（选择待办事项）**、**如何完成所选工作？（工作分解）**。这三个问题的顺序非常重要：必须先确认Sprint目标，再从Product Backlog中选取条目，最后分解为具体任务。在游戏开发场景中，这意味着团队必须先对齐"本轮迭代交付什么玩家价值"，才能讨论具体的功能实现细节。

Sprint计划的重要性在于它是整个Sprint的契约起点。开发团队在会议结束时做出的承诺不是面向管理层的汇报，而是团队内部对Sprint目标可实现性的集体判断。

---

## 核心原理

### Sprint目标的设定机制

Sprint目标是本次Sprint必须实现的单一、明确的业务承诺，由产品负责人提出初稿，经开发团队确认后最终定稿。一个合格的Sprint目标应满足SMART原则中的明确性（Specific）和可测量性（Measurable）——例如"完成角色移动系统的基础实现，使QA能够对地面移动和跳跃进行功能测试"，而非笼统的"推进角色系统开发"。

在游戏开发中，Sprint目标往往与某个可玩里程碑挂钩，例如"本Sprint结束时，关卡1具备可进行内部测试的完整通关流程"。这种可玩性导向的目标设定方式，能帮助团队在中途遭遇阻塞时做出取舍决策——哪些条目必须完成以满足目标，哪些可以推迟。

### 待办事项精炼与容量计算

Sprint计划会议依赖产品待办事项列表（Product Backlog）中已经过精炼（Refinement）的条目。精炼工作通常在Sprint进行过程中持续开展，确保排在列表前端的条目具备"就绪定义"（Definition of Ready）：用户故事清晰、验收标准明确、故事点估算已完成。

容量（Capacity）计算是Sprint计划的关键输入。团队需要统计本Sprint内每位成员的实际可用工时，扣除假期、例行会议、代码审查等非开发时间后得出净容量。例如，一个5人团队在两周Sprint中，若每人每天6小时可用于开发，则总容量约为300小时。结合上一Sprint的速率（Velocity，以故事点计），团队可以评估本次能承诺多少故事点的工作量。

### 工作分解与承诺机制

选定Sprint Backlog条目后，开发团队将每个用户故事拆解为具体的开发任务，每个任务的预估时间通常以小时为单位，且不超过8小时（即一个工作日）。这一颗粒度要求确保任务在每日站会中的进度可追踪。

承诺（Commitment）在2020版Scrum指南中被明确定义为针对Sprint目标的承诺，而非针对所有Sprint Backlog条目的承诺。这一区别至关重要：团队承诺尽最大努力实现Sprint目标，但Sprint Backlog中的具体条目可以随Sprint内信息变化而调整范围，只要不影响Sprint目标的达成。

---

## 实际应用

**游戏关卡设计迭代场景：** 某手游团队进行为期两周的Sprint，Sprint目标设定为"完成第二章第一关的灰盒关卡，可供用户体验测试"。产品负责人从Product Backlog中选取了以下已精炼条目：敌人生成点布置（5点）、玩家出生点逻辑（3点）、关卡边界碰撞（2点）、通关触发器（3点）。团队评估总容量后确认可承诺13故事点，与上一Sprint速率（12点）相吻合。会议中，关卡设计师将"敌人生成点布置"拆解为：设计敌人分布文档（2小时）、在引擎中放置生成器（3小时）、参数调试（2小时）三个任务。

**常见冲突处理：** 当产品负责人期望本Sprint纳入的条目超出团队容量时，Sprint计划会议提供了一个结构化的协商机制。团队可用实际容量数据和历史速率拒绝超载，同时与产品负责人协商缩减某些条目的范围（如将"完整的背包系统"缩减为"装备槽的拾取与装备功能"），以在不破坏Sprint目标的前提下达成双方均认可的承诺。

---

## 常见误区

**误区一：将Sprint计划会议变成技术方案评审会。** 部分团队在Sprint计划中花费大量时间讨论架构细节和技术实现路径，导致4小时时间盒严重超时。Sprint计划的任务分解环节只需将故事拆解至8小时以内的任务即可，详细的技术讨论应在Sprint过程中通过专项技术会议或配对编程解决。

**误区二：把Sprint承诺理解为"保证完成所有列出的条目"。** 这一误解会导致团队在Sprint末期为了"兑现承诺"而降低质量标准，赶工合入未经充分测试的代码。正确理解是：团队承诺全力实现Sprint目标，当某个条目的实现威胁到Sprint目标时，应立即在每日站会中提出，而非到Sprint Review时才暴露。

**误区三：产品负责人在Sprint计划前未完成待办事项精炼。** 如果排在Product Backlog前端的条目到Sprint计划会议时仍缺乏验收标准或未经估算，团队将被迫在会议中现场做分析工作，严重压缩计划时间。这种情况的根源是将Backlog Refinement视为可选活动，而实际上Scrum指南建议团队每Sprint花费不超过10%的时间用于持续精炼。

---

## 知识关联

**前置概念——Scrum框架：** Sprint计划依赖对Product Backlog、Sprint Backlog、用户故事、故事点估算等Scrum基础元素的理解。没有预先建立并优先级排序的Product Backlog，Sprint计划会议无法有效进行。

**后续概念——每日站会：** Sprint计划产出的Sprint Backlog和Sprint目标构成每日站会的核心参照物。每日站会中"今天做什么"的问题直接对应Sprint Backlog任务列表，"是否有阻碍"的问题则反映Sprint目标的达成风险。

**后续概念——迭代规划：** 多个Sprint的累积速率数据和Sprint目标完成率，是上层迭代规划（Release Planning）的重要输入。团队通过分析历史Sprint计划的精准度，可以改善容量估算模型，使长期交付预测更加可靠。