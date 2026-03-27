---
id: "gp-as-backlog"
concept: "产品待办列表"
domain: "game-production"
subdomain: "agile-scrum"
subdomain_name: "敏捷/Scrum"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 产品待办列表

## 概述

产品待办列表（Product Backlog）是Scrum框架中由产品负责人（Product Owner）维护的一份有序工作清单，记录了产品需要完成的所有功能、改进、修复和技术任务。在游戏开发中，这份清单可能包含"实现双人合作模式"、"修复敌人AI路径寻找卡顿"或"添加成就系统"等各种类型的条目。Product Backlog不是普通的任务列表——它的每一项条目都应附有优先级排序、估算工作量和验收标准。

Product Backlog的概念由Jeff Sutherland和Ken Schwaber在1995年正式确立Scrum框架时提出，并在《Scrum指南》（Scrum Guide）中明确定义为"对产品目标实现所需工作的有序清单"。2020年版《Scrum指南》将其描述进一步简化，强调它是一份"突现性"（emergent）文档，会随着产品理解的深入而持续演进和精炼。

在游戏制作中，产品待办列表解决了一个核心问题：如何在有限的Sprint周期（通常2~4周）内，确保团队始终在做最有价值的工作。没有维护良好的Backlog，开发团队容易陷入"什么都想做、什么都做不完"的困境，导致游戏核心玩法长期无法完成。

---

## 核心原理

### 条目的组成结构（Backlog Item格式）

产品待办列表的每一个条目（Product Backlog Item，简称PBI）通常包含四个要素：**标题、描述、优先级顺序编号、以及工作量估算（以故事点Story Points计量）**。在游戏开发中，一个完整的PBI示例如下：

> **标题**：玩家死亡后显示"Game Over"界面  
> **描述**：当玩家HP归零时，暂停游戏并弹出包含"重试"和"退出"按钮的界面  
> **优先级**：第3位  
> **估算**：3故事点

故事点（Story Points）并非实际工时，而是团队约定的相对复杂度单位。常用斐波那契数列（1、2、3、5、8、13、21）来表示，数字越大代表工作越复杂或不确定性越高。

### 优先级排序方法

Product Backlog中的条目必须从上到下按价值排序，排在最前面的永远是当前对玩家/产品最有价值的条目。游戏团队常用以下两种排序工具：

**MoSCoW方法**将条目分为四类：Must Have（发布前必须完成）、Should Have（应该完成）、Could Have（有余力再做）、Won't Have（本次版本不做）。例如对于一款手机休闲游戏，"核心关卡循环"属于Must Have，"社交分享功能"可能属于Could Have。

**WSJF（加权最短工作优先）**是一种更精确的排序公式：

```
WSJF = （用户业务价值 + 时间紧迫性 + 风险降低）/ 工作量估算
```

WSJF值越高的条目越应排在前面。游戏团队在临近发布节点时，经常用这个公式决定哪些Bug修复应优先于新功能开发。

### Backlog精炼（Backlog Refinement）

Backlog精炼（也叫Backlog Grooming）是Scrum团队定期对待办列表进行审查和更新的活动，官方建议每个Sprint投入不超过10%的时间在精炼上（即2周Sprint中约4小时）。精炼会议的产出包括：将模糊的大条目拆分为具体的小条目（史诗Epic→用户故事User Story→任务Task）、更新估算值、删除已过期的需求。

在游戏开发中，精炼特别重要，因为玩法需求经常因游戏测试（Playtesting）的反馈而改变。例如，一个原本估算为5故事点的"武器升级系统"，在游戏测试后可能被拆分为"基础升级UI（3点）"+"数值平衡调整（8点）"两个独立条目。

---

## 实际应用

**案例：独立游戏团队管理Backlog**

一支5人独立游戏团队在开发像素风Roguelike游戏时，初始Backlog包含约120个条目。产品负责人（通常由游戏设计师担任）将条目按以下逻辑排序：

1. **核心游戏循环必须先行**：角色移动、攻击、房间生成、死亡机制——这些条目占据Backlog前20位
2. **可演示的垂直切片（Vertical Slice）次之**：能在第一个Sprint结束时展示给投资人看的完整玩法片段
3. **美术润色、成就系统、排行榜等放在Backlog末尾**

通过这种排序，团队在第6个Sprint（约12周）时就完成了可以上传Steam抢先体验的基础版本，而不是等到全部120个条目完成才发布。

**工具支持**：游戏团队常用Jira、Trello、Notion或专用工具Hacknplan管理Product Backlog。Hacknplan专为游戏开发设计，支持按游戏模块（战斗系统、关卡设计、音效）分类显示Backlog条目。

---

## 常见误区

**误区一：把Product Backlog当成"愿望清单"**

许多游戏团队将所有曾经想到的功能都加入Backlog，导致清单膨胀至500+条目，大量条目从未被重新审视。正确做法是定期删除超过3个Sprint未被讨论的低优先级条目，保持Backlog的"可动性"（Actionable）——通常健康的Backlog中，前两个Sprint的条目应已精炼到可以直接执行的程度。

**误区二：优先级由开发者而非产品负责人决定**

在游戏团队中，程序员常常倾向于优先处理技术债务或他们感兴趣的技术挑战，而不是玩家最需要的功能。Scrum明确规定：**Product Backlog的排序权归属于产品负责人（Product Owner）**，开发团队可以提供估算和技术建议，但最终排序决策权不在开发者手中。

**误区三：Backlog一旦确定就不应更改**

有团队错误地将Backlog视为固定合同，认为Sprint中途不能修改Backlog。实际上，Backlog的"突现性"（Emergent）特质意味着它必须随新信息而更新——玩家测试反馈、竞品分析或市场变化都可能要求产品负责人在Sprint结束后重新排序。Sprint内部的Backlog保持稳定，但Sprint之间的Backlog调整完全正常且必要。

---

## 知识关联

**与Sprint回顾的关系**：Sprint回顾会议（Sprint Retrospective）的改进行动项可以直接转化为Backlog条目。例如，团队在回顾中发现"代码合并冲突频繁导致效率低下"，可以在Backlog中新增"建立分支管理规范"的技术条目，并由产品负责人赋予合理的优先级排序。

**通往用户故事**：产品待办列表中的条目主要以**用户故事（User Story）**的格式编写，其标准句式为"作为[角色]，我希望[功能]，以便[价值]"。例如："作为玩家，我希望能保存游戏进度，以便下次继续上次的关卡。"用户故事是Product Backlog条目的标准表达方式，学习如何编写高质量的用户故事是管理Backlog的下一个重要技能点。