---
id: "sprint-planning"
concept: "Sprint规划"
domain: "product-design"
subdomain: "product-management"
subdomain_name: "产品管理"
difficulty: 2
is_milestone: false
tags: ["敏捷"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Sprint规划

## 概述

Sprint规划（Sprint Planning）是Scrum框架中每个迭代周期开始时举行的正式会议，团队在此会议中共同决定在即将到来的Sprint期间要完成哪些工作，以及如何完成这些工作。Sprint规划会议有严格的时间限制（Time-box）：对于两周的Sprint，规划会议通常不超过4小时；对于四周的Sprint，则不超过8小时。这个时间盒规则防止团队陷入无休止的讨论，迫使团队聚焦在最关键的决策上。

Sprint规划的概念随Scrum方法论的发展而成形。Jeff Sutherland和Ken Schwaber在1995年正式提出Scrum框架时，Sprint规划就作为其核心仪式（Ceremony）被纳入其中。2020年更新的《Scrum指南》将Sprint规划明确划分为三个议题：为什么这个Sprint有价值（Why）、这个Sprint能完成什么（What）、以及如何完成选定的工作（How）。这一三段式结构使规划会议从单纯的任务分配升级为价值驱动的承诺过程。

Sprint规划直接决定了产品路线图上的优先需求能否被精确切割并落地交付。一次高质量的Sprint规划，让开发团队对承诺的Sprint目标（Sprint Goal）有共同理解，避免了迭代中途频繁变更范围、导致交付物质量下降的问题。

## 核心原理

### Sprint目标的制定

Sprint目标是Sprint规划会议产出的第一个关键成果，它是一句概括性陈述，说明本次Sprint为产品和用户创造的具体价值。Sprint目标不是任务清单的堆叠，而是一个连贯的业务意图表达。例如，"使用户能够完成自助退款全流程"就是有效的Sprint目标，而"完成退款页面、添加退款逻辑、修复三个Bug"则是任务罗列，不能构成真正的Sprint目标。Sprint目标赋予团队在执行中的灵活性：当某个具体实现方案遇到障碍时，团队可以调整技术路径，只要仍能实现Sprint目标即可。

### 产品待办列表的切割与选取

产品负责人（Product Owner）在规划会议前需准备好经过精化（Refinement）的产品待办列表（Product Backlog）顶部条目，每个条目需附有验收标准（Acceptance Criteria）。团队根据自身速率（Velocity）——即过去3至5个Sprint平均完成的故事点数——来判断本次可以承接多少工作量。若团队过去平均速率为35个故事点，则不应在Sprint规划中承诺超过40个故事点的工作，留出约10%~15%的缓冲以应对技术不确定性。

### 任务分解与工时估算

完成"What"（做什么）的讨论后，开发团队进入"How"（怎么做）的阶段，将每个选中的用户故事（User Story）进一步分解为具体的开发任务（Task），并以小时为单位估算每个任务的工时。单个任务的估算通常不超过8小时；若某任务估算超过8小时，则需要继续拆分。所有任务的工时总和应与团队在本次Sprint中的可用工时（Available Capacity）大致匹配——可用工时计算方式为：团队成员人数 × Sprint天数 × 每日有效工作小时数（通常取6小时，剔除会议、沟通等开销），再乘以每位成员的参与系数（如有人只参与80%的Sprint工作）。

### Sprint承诺的性质

Sprint承诺不是合同义务，而是团队对自身能力的专业预测，以及对Sprint目标的集体认可。《Scrum指南》（2020版）明确指出，Sprint Backlog是开发团队对自己的计划，产品负责人和外部利益相关者无权在Sprint进行中向Sprint Backlog添加新工作，除非与团队协商并取消当前Sprint。

## 实际应用

**电商平台迭代案例**：某电商团队的产品路线图中，第三季度第二个Sprint的目标是"支持买家在移动端完成拼团购买"。规划会议中，产品负责人从产品待办列表中取出"拼团页面展示"（5点）、"成团条件验证逻辑"（8点）、"支付跳转适配"（3点）共16个故事点的条目，低于团队20点的平均速率。开发团队将"成团条件验证逻辑"进一步拆分为"接口定义"（4小时）、"后端逻辑实现"（6小时）、"单元测试"（3小时）三个任务，确保每项任务均在一个工作日内可完成。

**规划会议的常见时序**：前半段（约占时间盒的50%）由产品负责人讲解Sprint目标和选中条目的业务背景，团队提问澄清验收标准；后半段由开发团队独立讨论任务拆解，产品负责人在场但不主导，保证技术估算不受业务压力干扰。

## 常见误区

**误区一：将速率（Velocity）视为硬性生产指标**。许多管理者要求团队Sprint的故事点数只增不减，将速率作为团队效率的考核依据。实际上，故事点是相对估算单位，不同团队之间不可横向比较，同一团队的速率正常波动范围可达±20%。强行提高速率会导致团队故意将故事点虚高估算，或者降低完成定义（Definition of Done）的标准，从而积累技术债务。

**误区二：Sprint规划等同于把积压任务平均分配给团队成员**。这种做法把规划变成了排班表，忽略了Sprint规划的核心目的是建立共同目标和集体承诺。真正的Sprint规划中，任务不在会议上直接分配给个人，而是放入Sprint Backlog，由团队成员在Sprint执行过程中自主认领（Self-organizing），这样更能激发个人主动性和团队协作。

**误区三：细节越多的规划越好**。有些团队在规划会议上将每个任务细化到30分钟粒度，耗费大量时间。然而，Sprint开始后实际遇到的技术问题会使最精细的计划迅速失效。敏捷规划的核心是"够用即可"——在规划阶段识别出主要风险项和依赖关系，而非追求计划的绝对精确。

## 知识关联

Sprint规划依赖**产品路线图**提供战略方向，确保每个Sprint目标与季度/年度产品目标对齐；同时依赖**工作量估算**（特别是故事点估算技术如规划扑克）来判断Sprint的工作范围是否合理，这两项前置技能的缺失会直接导致Sprint规划会议中选取条目时缺乏依据。完成Sprint规划后，团队将进入**Scrum框架**的完整执行周期——每日站会（Daily Scrum）、Sprint评审（Sprint Review）和Sprint回顾（Sprint Retrospective）构成完整的检视与适应闭环，Sprint规划则是这个闭环的起点，其质量直接影响后续三个仪式能否顺畅运行。
