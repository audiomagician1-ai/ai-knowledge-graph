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



# Scrum框架

## 概述

Scrum是一种轻量级敏捷框架，由Jeff Sutherland和Ken Schwaber于1995年在OOPSLA大会上正式提出，并通过《Scrum指南》（最新版本为2020年版）持续迭代规范化。它将复杂产品开发工作拆分为固定时长的迭代周期（Sprint，通常为1至4周），通过三类角色、五种仪式和三类工件的协同运转，帮助团队持续交付可用产品增量。

Scrum的核心价值观包含承诺、专注、开放、尊重和勇气五项，这五项价值观直接驱动着框架中每一个具体实践的设计意图。与瀑布式开发不同，Scrum不要求在开发开始前锁定完整需求，而是允许Product Backlog在每个Sprint之间持续调整，适用于需求频繁变化或高度不确定的产品环境。

Scrum框架之所以在产品管理领域被广泛采用，是因为它将"交付频率"和"反馈循环"制度化。每个Sprint结束时必须产出可发布的增量（Potentially Shippable Increment），而非仅完成文档或阶段性里程碑，这使产品团队能以平均2周为单位获得真实用户反馈并调整方向。

## 核心原理

### 三类角色的职责划分

Scrum仅定义三个角色，刻意排除项目经理这一传统职位。**产品负责人（Product Owner）**对Product Backlog拥有唯一决策权，负责对条目进行排序并确保每个条目的商业价值描述清晰可执行。**Scrum Master**是框架的守护者，负责移除团队障碍、辅导组织理解Scrum实践，但不对团队的工作内容做指令性管理。**开发团队（Developers）**由3至9名成员组成，团队自组织决定如何完成Sprint Goal，没有内部层级分工。三角色任何一方的权责模糊都会直接导致Backlog积压或Sprint失控。

### 五种仪式的时间盒规则

Scrum的五种仪式均设有严格时间盒（Timebox），以防会议膨胀：

- **Sprint规划（Sprint Planning）**：每个Sprint开始时举行，最长8小时（以4周Sprint为基准），输出Sprint Backlog和Sprint Goal。
- **每日站会（Daily Scrum）**：每天固定15分钟，开发团队同步进度、识别阻碍，Product Owner和Scrum Master不强制参与。
- **Sprint评审（Sprint Review）**：Sprint结束时举行，最长4小时，向利益相关者展示增量并收集反馈，输出更新后的Product Backlog。
- **Sprint回顾（Sprint Retrospective）**：Sprint评审之后进行，最长3小时，聚焦团队工作方式的改进，而非产品内容本身。
- **Backlog梳理（Backlog Refinement）**：非正式仪式，通常占Sprint时长的10%以内，用于拆分和估算未来条目。

### 三类工件与透明性

Scrum的三类工件各自对应一个"承诺"以强化透明度：

- **Product Backlog**对应**产品目标（Product Goal）**，是所有已知需求的单一有序清单，由Product Owner维护，条目以用户故事形式描述，包含验收标准和估算值。
- **Sprint Backlog**对应**Sprint Goal**，是团队在当前Sprint内承诺完成的工作子集，加上达成Sprint Goal的计划。
- **增量（Increment）**对应**完成的定义（Definition of Done）**，每个Sprint结束时至少产出一个满足DoD的增量。DoD是团队共同制定的质量检查清单，例如"代码通过单元测试覆盖率≥80%且完成代码审查"。

## 实际应用

某电商产品团队采用2周Sprint节奏开发移动端购物车功能。Product Owner在Sprint规划前维护好Product Backlog，将"用户可将商品加入购物车并修改数量"排在最高优先级，拆分为5个用户故事，总估算为34个故事点（使用斐波那契数列估算）。开发团队在Sprint规划中确认本次Sprint Goal为"完成购物车核心交互流程的可测试版本"，并将34个故事点中的21点纳入Sprint Backlog。

两周后的Sprint评审中，团队展示了可在测试环境运行的购物车原型，产品运营提出"需要展示实时库存数量"的新需求，Product Owner当场将其记入Product Backlog并标注优先级，而非打断当前Sprint。随后的Sprint回顾中，团队发现每日站会常因讨论技术细节超时，决定下个Sprint起将技术讨论移到站会后的专项会议中处理。这一调整在下一个Sprint的实际数据中使平均站会时长从22分钟降回到14分钟。

## 常见误区

**误区一：把Scrum Master当项目经理**。Scrum Master不负责分配任务、制定进度计划或对外汇报项目状态。一旦Scrum Master开始给开发团队成员安排具体任务，团队自组织能力会逐步萎缩，Sprint规划也会退化为任务分发会议，违背Scrum框架的根本设计。

**误区二：Sprint可以随时追加需求**。Sprint一旦开始，Sprint Backlog内容原则上不可更改，除非Product Owner判断当前Sprint Goal已无商业价值而终止整个Sprint。利益相关者的新需求应进入Product Backlog排队，而非直接插入进行中的Sprint，否则Sprint Goal形同虚设，团队无法建立可预测的交付节奏。

**误区三：Scrum等于每天开站会**。每日站会仅是五种仪式之一，缺少Sprint Goal、没有Product Backlog排序机制、不执行Sprint回顾的团队只是在形式上模仿Scrum，实质上仍是任务跟踪式管理。完整的Scrum必须三类角色、五种仪式、三类工件同时运转。

## 知识关联

Scrum框架以**Sprint规划**为起点——理解如何将Product Backlog条目转化为Sprint Backlog和Sprint Goal，是运转整个框架的前提。没有有效的Sprint规划，团队无法建立清晰的迭代承诺，其他仪式的价值也随之削弱。

掌握Scrum框架后，自然延伸至两个方向：**看板方法（Kanban）**提供了另一种敏捷框架视角，它不使用时间盒Sprint，而以持续流动和WIP（在制品）限制为核心，适合需求到达节奏更不规则的运营团队，与Scrum的对比学习能帮助产品经理根据团队特征选择合适框架。**迭代回顾**则将Scrum回顾仪式的实践技巧深入展开，包括具体的回顾工具（如"开始-停止-继续"矩阵）和如何将回顾结论转化为下一Sprint的可执行改进项。