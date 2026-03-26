---
id: "qa-bl-wont-fix"
concept: "Won't Fix决策"
domain: "game-qa"
subdomain: "bug-lifecycle"
subdomain_name: "Bug生命周期"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.483
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Won't Fix决策

## 概述

Won't Fix（不修复）是Bug生命周期中的一种正式关闭状态，由项目决策者在Bug评审会上投票通过，将某个已确认存在的缺陷标记为"已知问题，不予修复"。与"Invalid"（无效Bug）不同，Won't Fix承认Bug确实存在，但基于特定理由主动放弃修复。这一决策必须记录在缺陷追踪系统（如Jira、Bugzilla）中，并附上明确的理由说明，供团队和QA部门存档。

该决策标准最早在微软内部的Bug分级体系中被系统化，后被游戏行业广泛采用。在游戏QA流程中，临近黄金版（Gold Master）送审时，Won't Fix的使用频率会显著上升——通常在送审前两周内，原本计划修复的Low/Medium优先级Bug中有30%～50%会被重新评估并标记为Won't Fix，以冻结版本、避免引入新的回归风险。

理解Won't Fix决策的价值在于：它不是懈怠，而是一种风险管理工具。游戏项目的时间与人力资源有限，盲目修复所有Bug有时会导致版本不稳定性上升，反而降低发布质量。Won't Fix为团队提供了一个有据可查的机制，平衡"完美"与"可发布"之间的张力。

## 核心原理

### 四项判断标准

Won't Fix决策通常基于以下四个维度进行量化评估，任意一项达到阈值即可触发该状态：

**成本（Cost）**：修复所需的开发工时与测试回归时间之和超过Bug影响的可接受上限。例如，修复一个UI文字错位Bug需要美术、程序、QA各投入4小时，合计约1.2个人天，而该问题仅影响1%的玩家且无功能损害，此时成本/收益比不合理，倾向Won't Fix。

**风险（Risk）**：修复该Bug引入新回归缺陷的概率高于Bug本身的危害程度。在游戏引擎层面（如修改物理碰撞参数），牵一发而动全身，一个低优先级碰撞穿模Bug的修复可能破坏10个已通过回归测试的关卡。当评估风险系数 R = P(回归) × 影响面 > 原始Bug严重度时，选择Won't Fix是合理的工程判断。

**影响（Impact）**：Bug触发路径复杂、复现率极低（通常定义为复现率 < 5%），或仅在极端边缘条件下出现（如持续游戏时长超过200小时才能触发的存档溢出）。影响范围若限定在少于0.1%的玩家群体，且不造成数据丢失或闪退，通常符合Won't Fix标准。

**临近发布（Near Release）**：版本代码进入Feature Freeze或Content Lock阶段后，原则上拒绝非Blocker/Critical级别的修复提交。此时即使是Medium级别的视觉Bug，也会因为"版本稳定性优先"原则被归类为Won't Fix，并在补丁计划中重新登记为候选修复项。

### 决策流程与权限

Won't Fix不能由单个QA工程师单方面关闭，必须经过Bug评审会（Triage Meeting）中至少包含制作人（Producer）或主策划（Lead Designer）在内的多方确认。在评审系统中，该状态的设置权限通常被配置为"Lead级别以上"，防止开发人员绕过评审自行关闭不想修复的Bug。决策通过后，QA负责人需在Bug报告的Comment字段填写标准化理由，格式通常为：`[Won't Fix] 原因类型: 成本/风险/影响/发布临近 | 详细说明 | 后续计划（如有）`。

### 与Deferred的区别

Won't Fix与Deferred（延期）的本质区别在于：Deferred意味着"这个版本不修，下个版本修"，而Won't Fix意味着"在可预见的未来不计划修复"。在实践中，Won't Fix的Bug会进入Known Issues List（已知问题列表），可能随版本更新被重新激活（Reopen），但没有明确的修复承诺；Deferred的Bug则会与特定里程碑绑定，具有明确的重新评估时间节点。

## 实际应用

**案例一：开放世界RPG中的NPC路径Bug**
某开放世界游戏中，一个NPC在特定地形下会原地打转5秒后恢复正常。该Bug复现需要玩家在精确坐标点触发，复现率约2%，且NPC最终能自我恢复。程序评估修复需要重写局部寻路逻辑，风险涉及全图300+个NPC的路径系统。评审会最终以"影响低 + 修复风险高"为双重理由标记Won't Fix，并在游戏Known Issues页面公开说明。

**案例二：多人射击游戏发布前两周的音效Bug**
某FPS游戏在发布前12天发现，特定地图角落会出现约0.3秒的错误脚步音效。音频工程师评估修复时间为6小时，但需要提交新版音频中间件配置文件，QA回归测试该系统至少需要2天。制作人以"临近发布 + 时间成本超限"为理由通过Won't Fix，该Bug被列入Day-1 Patch候选列表。

## 常见误区

**误区一：Won't Fix等于开发团队不重视Bug**
Won't Fix是经过正式决策流程的主动选择，而非忽视。每一条Won't Fix记录必须附带理由，并经过Lead级别审批。将其理解为"懒得修"会导致QA人员错误地对该状态产生抵触情绪，实际上它是版本质量控制的必要工具。

**误区二：Won't Fix之后Bug报告可以删除**
Won't Fix的Bug必须在缺陷追踪系统中永久保留，状态改为关闭但记录不得删除。原因有三：其一，Known Issues文档需要引用这些记录；其二，若同类Bug在下个版本再次被提交，去重逻辑（见"重复Bug管理"）需要比对历史记录；其三，若玩家投诉该问题，客服团队需要查阅官方已知问题依据。

**误区三：任何Bug在临近发布时都应标记Won't Fix**
临近发布只是四项标准之一，并非万能理由。Blocker级别（如游戏无法启动、存档无法读取）和Critical级别（如核心玩法功能缺失）的Bug无论距离发布多近，都不适用Won't Fix，必须修复或推迟发布。将"临近发布"滥用为关闭高优先级Bug的借口，是导致游戏发布质量崩坏的常见管理失误。

## 知识关联

Won't Fix决策是Bug评审会（Triage Meeting）输出结果的直接体现：评审会确立了Bug优先级分级体系（Blocker/Critical/Major/Minor/Low）和修复决策权限，Won't Fix正是在该体系框架内、针对特定优先级区间（通常为Minor和Low）作出的关闭决策。没有评审会建立的优先级共识，Won't Fix的四项判断标准将失去评估基准。

在后续的重复Bug管理中，Won't Fix记录扮演着重要的去重基准角色：当新版本测试中提交了与历史Won't Fix条目高度相似的Bug时，QA工程师需要判断新Bug是否属于同一根因（Root Cause），若是则标记为Duplicate并关联至原始Won't Fix条目，而不是重新开启一轮完整的修复评估流程。这一机制避免了已知问题被反复提交、消耗评审资源的问题。