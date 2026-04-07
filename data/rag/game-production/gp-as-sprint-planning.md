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


# Sprint计划

## 概述

Sprint计划（Sprint Planning）是Scrum框架中每个Sprint开头必须举行的时间盒会议，用于确定本轮迭代要完成的工作范围并建立团队承诺。根据Scrum指南（2020版）的规定，一个为期两周的Sprint对应的Sprint计划会议最长不超过**8小时**，时长与Sprint周期等比缩短——1周Sprint对应最多4小时的计划会议。

这种会议形式由Jeff Sutherland和Ken Schwaber在20世纪90年代初系统化并写入Scrum框架，其设计初衷是解决游戏开发团队常见的"需求无底洞"问题：在瀑布式开发中，策划文档在整个项目周期内持续膨胀，导致程序员和美术人员无法确定任何时间点的交付优先级。Sprint计划将这种不确定性压缩到一个短时窗口内做出决策。

对游戏团队而言，Sprint计划的核心价值在于把产品负责人（Product Owner，通常是主策划或制作人）的长期愿景转化为开发团队在接下来7至14天内**可交付的具体功能**。每次会议结束时，团队必须能够回答两个具体问题：这个Sprint要实现什么目标？这个目标将如何完成？

---

## 核心原理

### Sprint目标的制定方式

Sprint目标是整个Sprint计划会议产出的单一句子级别的承诺，而非任务列表的简单集合。它描述为什么要执行本次Sprint，而不是做什么。例如，"本Sprint交付角色基础攻击手感的可验证原型，供玩法测试组评估"就是有效的Sprint目标，而"完成攻击动画、碰撞检测和音效"则只是任务清单，不构成目标。

好的Sprint目标必须满足**SMART原则**中的具体性和可验证性——游戏团队尤其要注意"可验证"这一点，因为"手感好"或"画面流畅"这类描述会在Sprint评审时引发争议。建议在目标中明确验收标准，例如"角色格挡动作的帧预算不超过16ms，并通过QA的60fps压力测试"。

### 待办事项精炼与Story Point估算

Sprint计划的顺利进行依赖于产品待办事项（Product Backlog）在会议前已经过**精炼（Refinement）**。精炼不是Sprint计划会议本身的一部分，而是一个持续进行的活动，Scrum指南建议团队每周花费不超过产能10%的时间在精炼上。未精炼的条目进入Sprint计划会议会导致会议超时和估算偏差。

开发团队在Sprint计划第二阶段使用Story Points对精炼后的待办事项（Product Backlog Item，PBI）进行相对估算。常见的斐波那契数列（1, 2, 3, 5, 8, 13, 21）用于体现工作量的非线性增长——估算值为13或21的条目通常意味着该需求尚未被充分拆解，应当退回精炼。游戏团队的经验法则是：单个Sprint内不放入估算超过**8个Story Point**的单条PBI。

### 团队速度与容量计算

Sprint计划中，开发团队依据**团队速度（Velocity）**来决定本次Sprint能承接多少工作量。速度取最近3至5个Sprint的平均完成Story Points，而非理论最大值。容量（Capacity）则在此基础上进一步扣除成员假期、跨组支援等因素——若团队速度为40点，但本Sprint有成员请假导致实际工作日减少20%，则计划时纳入的工作量应控制在32点左右。

游戏工作室在节假日（如春节、黄金周）前后的Sprint中，Speed与Capacity的差距尤为显著，这是许多项目延期的隐性原因之一。

---

## 实际应用

**案例：关卡编辑器功能Sprint**

某手游项目团队（7人，含2名程序、2名美术、1名关卡策划、1名QA、1名产品负责人）在Sprint计划中面对以下情况：产品待办列表顶部有"实现关卡编辑器撤销/重做功能"（估算8点）、"导出地图数据为JSON格式"（估算5点）、"关卡对象吸附网格"（估算3点）三个PBI，团队近三Sprint平均速度为14点。

产品负责人在会议第一阶段解释背景：撤销功能直接影响关卡策划的每日工作效率，是本Sprint最高优先级。团队随后拟定Sprint目标："本Sprint使关卡编辑器支持完整的撤销/重做与网格吸附，令策划可独立完成关卡搭建而无需程序干预。"三个PBI共16点略超速度，团队与产品负责人协商后，决定将JSON导出功能推入下一Sprint，以保护Sprint目标的完整性。

会议第二阶段，程序人员将8点的撤销功能拆解为：命令模式架构设计（1天）、5类操作的可撤销化实现（3天）、边界条件测试（1天），从而生成了可以每日追踪进度的Sprint待办列表（Sprint Backlog）。

---

## 常见误区

**误区一：Sprint计划等同于任务分配会议**

很多游戏团队的Sprint计划演变成主管逐一指派任务的会议，开发人员被动接受而非主动承诺。Scrum框架明确规定开发团队自行决定如何完成工作——产品负责人澄清"做什么"，但"怎么做"由程序、美术、QA等成员自行组织。强制分配的Sprint Backlog往往导致团队成员缺乏责任感，Sprint中途遇到阻碍时也不会主动寻求解决。

**误区二：承诺等于保证完成所有任务**

Sprint承诺是针对**Sprint目标**的承诺，而非对Sprint Backlog中每一行任务的交付保证。游戏开发中技术风险普遍存在——若某个渲染特性在Sprint中期发现需要重构着色器，团队可以调整Sprint Backlog（替换或删减低优先级任务），只要最终Sprint目标仍然达成，本次Sprint就是成功的。将承诺理解为"任务100%完成"会导致团队人为压低估算，进而产生技术债。

**误区三：在Sprint计划中直接修改估算来"凑数"**

当Sprint计划发现工作量超过团队速度时，部分团队会倒推式地降低某些条目的Story Point估算，使总分恰好等于速度。这破坏了估算的一致性基准——若本Sprint把某个功能估为3点，而下次类似功能仍被估为5点，跨Sprint的速度数据将失去参考价值。正确做法是缩减PBI范围或推后部分条目至下一Sprint。

---

## 知识关联

Sprint计划以**Scrum框架**中产品待办列表（Product Backlog）的存在为前提——没有经过优先级排序的PBI，Sprint计划会议无法产出有意义的Sprint目标。同时，产品负责人对业务价值的判断能力直接决定了Sprint目标的质量。

Sprint计划会议结束后，产出的Sprint Backlog成为**每日站会（Daily Scrum）**的核心参照物：开发团队每天检视Sprint Backlog的进度，判断是否能在Sprint结束前达成既定目标。此外，Sprint计划中确立的速度基准数据，也是**迭代规划（Release Planning）**中估算整体项目工期的关键输入——若产品路线图包含200点的功能，团队速度稳定在40点，则理论上需要5个Sprint完成，制作人可据此制定发行时间表。