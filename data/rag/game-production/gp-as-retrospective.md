---
id: "gp-as-retrospective"
concept: "Sprint回顾"
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
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Sprint回顾

## 概述

Sprint回顾（Sprint Retrospective）是Scrum框架中每个Sprint结束时召开的团队反思会议，专注于**团队协作流程**而非产品功能本身。与Sprint评审会聚焦于"我们做了什么产品"不同，回顾会回答的核心问题是"我们如何更好地合作"。根据Scrum指南（2020版），回顾会的时间盒为每周Sprint对应最多45分钟，一个两周Sprint的回顾会上限为1.5小时。

这一仪式起源于精益制造中的"改善"（Kaizen）理念，由Jeff Sutherland和Ken Schwaber在1990年代将其整合进Scrum体系。在游戏开发场景中，回顾会尤为关键——因为游戏团队往往跨越策划、美术、程序、QA多个职能，跨职能摩擦点需要专门的结构化机制来暴露和解决，而不能依赖日常站会完成。

Sprint回顾会的法定参与者是**整个Scrum团队**：开发团队全员加上Scrum Master和产品负责人（PO）。PO不是旁观者，而是平等参与者，这一点在游戏制作中意味着制作人也必须暴露自己对流程的阻碍，而非仅仅倾听开发人员的反馈。

---

## 核心原理

### 帆船模型（Sailboat Retrospective）

帆船模型是回顾会中最常用于游戏团队的可视化框架。白板上绘制一艘帆船，分为四个区域：**风（推动力）**、**锚（拖累因素）**、**礁石（即将到来的风险）**、**岛屿（目标）**。每位团队成员将便利贴贴入对应区域。例如，一个游戏团队可能在"锚"区域发现"美术资产审批需要等待外部IP授权方三天"，在"礁石"区域标注"下个Sprint的性能优化可能导致已完成关卡需要返工"。

帆船模型的独特价值在于它同时暴露**当前阻碍**与**未来风险**，而多数其他方法只处理过去。对于游戏开发而言，礁石象限特别重要——因为技术债、引擎升级等风险经常在Sprint结束时已经可以预见，但若无专门环节，团队不会主动讨论。

### 四象限模型（4Ls Retrospective）

四象限模型由Ebony Gooden于2016年提出，四个象限分别是：**Liked（喜欢的）**、**Learned（学到的）**、**Lacked（缺乏的）**、**Longed For（渴望的）**。在游戏Sprint回顾中，"Learned"象限往往产出最有价值的内容，例如"我们发现Unity的Addressable系统在超过500个资产时需要预先分组，否则加载时间超过8秒"。"Longed For"象限则会暴露工具需求，如"我们渴望一个自动化的关卡数据验证脚本"。

相比帆船模型，四象限更适合团队已经相对稳定、需要深度知识沉淀的阶段。建议游戏团队在里程碑节点（Alpha、Beta等）之后的Sprint回顾中使用四象限，以捕捉阶段性经验。

### 行动项的SMART提取与闭环机制

回顾会最容易流于"吐槽大会"的根本原因，是讨论止步于抱怨而不产生具体行动项。Scrum规范要求每次回顾会结束前，团队必须识别出**至少一项**具体改进措施并纳入下一个Sprint的工作中。

行动项必须符合SMART原则：具体（Specific）、可测量（Measurable）、可实现（Achievable）、相关（Relevant）、有时限（Time-bound）。一个反面例子是"改善沟通"——这不是行动项。正确的行动项应写作："从下个Sprint起，每周三下午4点举行15分钟的美术-程序资产交付同步会，由李明负责，持续2个Sprint后评估效果"。

行动项在回顾会结束时被记录进Sprint待办列表（Sprint Backlog），由负责人认领，并在下次回顾会开始时首先检查完成情况，形成PDCA闭环。

---

## 实际应用

**游戏团队回顾会的典型场景**：一支8人独立游戏团队在完成第三个Sprint后发现，所有人对"帆船"锚区都写到了"等待关卡美术完成白盒才能开始功能测试"。Scrum Master引导讨论后，提取出行动项：策划工程师下个Sprint开始使用ProBuilder制作测试用几何体，使功能测试提前3天启动，无需等待正式美术资产。这一改进在第四个Sprint中缩短了15%的反复修改时间。

**里程碑前的强化回顾**：在游戏进入Alpha前的最后一个Sprint，团队使用四象限进行90分钟的深度回顾，产出的"Lacked"象限内容直接用于更新团队Wiki中的"开发规范"文档，供未来成员入职时参阅。

---

## 常见误区

**误区一：回顾会是Scrum Master的汇报会**
很多游戏团队的回顾会变成了Scrum Master单方面总结Sprint问题，开发成员被动接受。这与回顾会的设计初衷相反——每位团队成员都应独立填写便利贴并发言，Scrum Master的角色是**主持人**而非**发言人**。如果团队沉默，通常意味着心理安全感不足，而非没有问题。

**误区二：行动项不进Sprint Backlog**
许多团队将行动项记录在单独的"改进列表"中，但从不在Sprint计划会中分配时间。这导致改进工作永远被新功能挤占。正确做法是在下个Sprint计划时，将回顾行动项作为显性任务估点并分配到Sprint Backlog中，给予与游戏功能任务同等优先级。

**误区三：每次回顾会用相同方法**
连续使用同一框架会导致团队进入"填表"模式，思考深度下降。建议每3~4个Sprint轮换一次方法，除帆船和四象限外，还可选用"疯狂悲伤高兴"（Mad Sad Glad）、"时间线回顾"等方式，保持团队对回顾会的新鲜感和参与动力。

---

## 知识关联

Sprint回顾是Sprint评审之后的最后一个仪式。评审会结束时，团队已经从干系人处获得了产品反馈；而回顾会紧接着处理**团队内部的流程反馈**，两者共同构成Sprint的完整收尾。评审会中发现的流程问题（如"演示环境每次都不稳定"）应带入回顾会转化为行动项，而非在评审会中讨论解决方案。

回顾会产出的改进行动项会直接影响**产品待办列表**（Product Backlog）的维护方式。例如，团队在回顾会中发现用户故事拆分粒度过大导致Sprint超载，这一发现应推动PO调整Backlog梳理会（Backlog Refinement）的规则——要求每张卡片的估算不超过5个故事点。因此，掌握回顾会方法论是有效参与后续Backlog管理的前提。