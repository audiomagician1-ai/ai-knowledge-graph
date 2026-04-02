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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# Sprint规划

## 概述

Sprint规划（Sprint Planning）是Scrum框架中每个迭代周期开始时召开的仪式性会议，团队在此会议中共同决定本次Sprint要完成哪些工作、以何种方式完成。根据Scrum指南（2020年版），Sprint规划的时间盒（timebox）上限为8小时（对应一个4周Sprint），更短的Sprint对应更短的规划会议，通常按比例缩短——2周Sprint对应约4小时。

Sprint规划的概念起源于Jeff Sutherland和Ken Schwaber于1995年在OOPSLA会议上正式提出的Scrum框架。其核心设计思想是将长期规划的不确定性拆解为可交付的短期承诺：团队不再被要求预测数月后的结果，而是只对未来1-4周内可完成的工作作出承诺，从而将需求变化的风险降至最低。

Sprint规划对产品管理的价值在于它将产品待办列表（Product Backlog）中抽象的业务需求转化为具体的开发任务，并通过团队集体估算建立现实可行的交付预期。一次质量差的Sprint规划会直接导致Sprint中途范围蔓延、团队过载或产出与业务目标脱节，因此它是连接产品愿景与工程执行的关键节点。

## 核心原理

### Sprint目标的制定

Sprint目标（Sprint Goal）是整个Sprint规划会议的首要产出，它是一句话描述本次迭代的业务价值，而非任务清单的简单堆叠。产品负责人（Product Owner）需要在会议开始前准备好精化（refined）状态的产品待办条目，向团队阐释为什么这个Sprint的内容优先级最高。例如，"本Sprint目标是完成用户注册登录流程，使Beta测试用户能够独立开通账户"，而不是"完成登录页面、注册接口、邮件验证共3个故事"。Sprint目标赋予开发团队在执行层面的灵活性：若某个条目实现遇阻，团队可以调整技术方案，只要Sprint目标不受影响即可。

### 容量计算与速度参考

团队在确定Sprint范围时必须考虑两个量化指标：容量（Capacity）和历史速度（Velocity）。容量指本次Sprint中团队实际可用工时，计算方式为：将每位成员在Sprint时间段内的工作日数相加，再扣除已知的请假、会议占用等时间，最终换算为可用小时数或可用人天数。历史速度则是过去3-5个Sprint中团队平均完成的故事点数，作为本次Sprint能承载多少故事点的参考上限。例如，一个5人团队在2周Sprint中，若历史速度稳定在35-42点之间，本次Sprint选取的故事点总量不应超过42点。仅有速度数据而忽视容量变化（如春节假期导致实际可用天数减少）是常见的过载来源。

### 任务分解与估算方式

Sprint规划的第二阶段，开发团队将已选入Sprint的用户故事（User Story）拆解为具体的开发任务（Task），并对每个任务进行小时级别的估算。此阶段常用的技术是规划扑克（Planning Poker）：每位团队成员持有印有斐波那契数列（1、2、3、5、8、13、20……）的卡牌，同时亮牌，当估算差异超过2个数值档位时需进行讨论，直至达成共识。这种同步亮牌机制防止了"锚定偏差"——避免后出牌成员受到先出牌者影响而改变真实判断。任务粒度建议控制在2-8小时之间，超过8小时的任务需继续拆分，否则在每日站会中难以追踪进度。

### Sprint待办列表的形成

Sprint规划的最终产出是Sprint待办列表（Sprint Backlog），它包含三部分：选定的用户故事、拆解后的具体任务、以及Sprint目标。Sprint Backlog归开发团队所有，产品负责人在Sprint进行中不可直接向其中添加新条目，这是保护团队专注度的硬性规则。团队成员在Sprint Backlog上自我分配任务，而非由Scrum Master或产品负责人指派，以此保障团队对承诺的真实归属感（ownership）。

## 实际应用

**电商App功能迭代场景**：某电商团队计划在2周Sprint中新增"商品收藏夹"功能。产品负责人在规划会议前已将相关4个用户故事精化完毕，团队容量计算显示本Sprint有68人时可用。通过规划扑克，4个故事分别估算为5、8、3、5共21点，处于历史速度区间（18-25点）内。团队随即将"收藏夹列表页"故事拆解为：接口设计（3h）、前端UI还原（6h）、状态持久化逻辑（4h）、单元测试（2h）共4个任务，每项都在8小时以内，纳入Sprint Backlog。

**规划会议中发现故事未精化的处理**：当团队在Sprint规划中发现某个用户故事存在不清晰的验收标准时，正确做法是当场将该故事移回Product Backlog，而非强行估算后带入Sprint，因为验收标准不明确的故事会导致开发完成后被拒绝接受，造成浪费。

## 常见误区

**误区一：把Sprint规划等同于任务分配会议**。许多初学团队将Sprint规划的重心放在"谁做哪件事"上，而忽视Sprint目标的制定。这导致Sprint变成任务流水线而非目标导向的迭代，一旦某个任务受阻，团队无法判断是否可以调整策略，因为根本不清楚这个Sprint要解决的业务问题是什么。

**误区二：用理想工时（ideal hours）直接等同于日历工时**。新团队常犯的错误是将一个故事估算为"8个理想工时"，就认为一名工程师明天一天能完成。实际上，考虑到会议、回复消息、代码审查等中断，工程师每天的有效编码时间通常仅有4-6小时。因此需区分估算所用的"理想工时"与实际日历排期。

**误区三：Sprint规划会议上临时修改优先级**。产品负责人应在规划会议前完成Product Backlog的优先级排序，而不是在会议中让团队等待决策。如果产品负责人在会议中反复更改需求优先级，会导致会议时间大幅超出时间盒限制，通常意味着Backlog精化（Backlog Refinement）工作没有按时完成。

## 知识关联

Sprint规划以**产品路线图**为上游输入：路线图中的季度目标决定了哪些Epic和Feature在近期需要推进，产品负责人据此对Product Backlog进行优先级排序，才能为Sprint规划提供"已就绪"的待办条目。同时，**工作量估算**技能（包括故事点定义、规划扑克方法论、斐波那契数列的使用逻辑）是Sprint规划中容量匹配和任务分解环节的直接前提，缺乏估算校准经验的团队在规划会议中往往出现系统性低估或高估。

向后延伸，Sprint规划是**Scrum框架**五大事件（Sprint、Sprint规划、每日Scrum、Sprint评审、Sprint回顾）中时间最长、决策密度最高的一个，理解Sprint规划的输入输出和参与者职责，是完整掌握Scrum运作机制的基础节点。在Sprint规划积累的速度数据和容量管理经验，也会直接反哺产品路线图中里程碑日期的设定精度。