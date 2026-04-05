---
id: "gp-pp-approval-workflow"
concept: "审批流程"
domain: "game-production"
subdomain: "production-pipeline"
subdomain_name: "制作管线"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 审批流程

## 概述

审批流程（Approval Workflow）是游戏制作管线中对资产、功能模块和变更请求进行系统化审核与放行的正式程序。其核心目的是在资产进入下一制作阶段之前，通过多级责任人的检查，确保质量标准、技术规范与创意方向三者对齐。一个典型的游戏项目审批流程会覆盖从概念草图到最终提交（Gold Master）的完整生命周期。

审批流程的标准化实践起源于20世纪90年代主机平台的第一方认证体系。任天堂、索尼等平台商要求开发商在游戏上线前通过严格的Lotcheck/TCR（Technical Certification Requirement）测试，这一外部压力倒逼工作室建立了内部的分级审批机制。现代大型工作室的审批流程通常分为3至5个阶段，每个阶段对应不同的责任人权限等级（Level of Authority，LOA）。

在制作管线中，审批流程的价值在于将"返工成本"前置压缩。研究显示，在概念阶段发现并修正一个错误的成本，仅为集成阶段修正成本的1/10。因此，审批节点的密度越高、越靠近制作初期，整体项目的变更代价越低。

## 核心原理

### 资产审批的三级结构

游戏资产审批通常采用**三级放行结构**：第一级为同行评审（Peer Review），由同组的高级美术或程序员检查规范符合度，例如多边形面数是否超过预算（如角色模型移动平台不超过5000 tris）；第二级为主管审批（Lead Approval），检查资产是否符合美术风格指南（Art Bible）；第三级为整合验收（Integration Sign-off），由技术美术（TA）确认资产在引擎中的实际表现，包括LOD、碰撞体和材质实例化是否正确配置。每一级审批必须在项目管理工具（如Jira、Shotgrid）中留下明确的状态标记：Open → In Review → Approved / Rejected。

### 功能审核（Feature Review）的Gate机制

功能审核以里程碑节点为门控（Gate），常见的Gate包括：Pre-Alpha Gate（核心玩法可玩）、Alpha Gate（功能全部可用但未打磨）和Beta Gate（内容完整、Bug数量降至目标阈值以下）。每个Gate对应一份功能退出标准清单（Exit Criteria），例如Alpha Gate要求所有Blocker级Bug清零，主要功能帧率在目标平台上稳定达到30fps或60fps。功能负责人（Feature Owner）须在Gate评审会议上以实机演示形式证明功能达标，评审委员会由制作人、QA主管和技术总监共同组成。

### 变更请求（CR）管理

变更请求（Change Request，CR）是对已批准方案进行修改的正式申请，必须与日常Bug修复区分处理。一份CR需要包含以下五个字段：**变更描述、影响范围分析（Impact Analysis）、工时估算、优先级评级（P0–P3）、申请人与审批人签字**。CR的核心风险在于范围蔓延（Scope Creep）：未经受控的CR累积会导致项目延期。工业实践中常用"CR预算池"机制——每个迭代（Sprint）预留10%至15%的工时专门处理CR，超出预算的CR自动顺延至下一迭代或进入变更控制委员会（CCB，Change Control Board）讨论。

### 审批状态的流转规则

审批流程中资产或功能只能在明确的状态之间单向或双向流转，禁止跳级。典型状态机为：`Draft → Submitted → In Review → Approved` 或 `Draft → Submitted → In Review → Rejected → Rework → Submitted`。"Rejected"状态必须附带具体的拒绝原因标签（如"不符合风格指南第3.2条"），而非模糊反馈，这是审批流程可追溯性的基础。

## 实际应用

**角色模型审批实例**：角色美术完成一个敌人角色模型后，在Shotgrid中将任务状态改为"Pending Review"，并挂载三视图截图与.fbx文件。高级美术在48小时内完成面数、UV展开、命名规范检查后标记通过；主美确认造型与概念图一致后二次批准；TA导入UE5验证材质槽和碰撞胶囊体，全部通过后标记"Final Approved"，资产自动进入引擎资产库的`/Characters/Enemies/`目录。

**功能CR实例**：玩法设计师在Beta阶段提出将双跳高度从200单位调整为280单位，需提交CR，注明影响范围涉及30个关卡的跳跃平台间距校验，估算QA回归测试工时为16小时。制作人评估后将其定级为P2，纳入下一Sprint的CR预算池处理，而非立即插入当前迭代。

## 常见误区

**误区一：口头确认等同于审批通过。** 许多初级团队成员认为在Slack或会议中得到主管口头认可即可继续推进，但口头确认不会在项目管理工具中留下可追溯记录。一旦主管离职或记忆出现偏差，该资产的审批状态将无据可查，可能在后期QA中被标记为"未审批资产"重新进入审批队列，造成返工。

**误区二：CR与Bug Report可以合并处理。** CR是对已批准需求的主动变更，Bug Report是对既有需求实现错误的被动记录，两者走不同的流转路径。将CR混入Bug系统会导致工时统计失真——CR消耗的是功能开发预算，Bug修复消耗的是质保预算，混淆两者会使项目健康度数据完全失效。

**误区三：审批层级越多越严格越好。** 五级以上的审批链会使单个资产的平均等待时间超过72小时，造成美术或程序人员的大量空闲阻塞（Blocking）。优化方向是根据资产风险等级动态调整审批层级：低风险的UI图标可走简化的单级审批，高风险的核心玩法系统走完整的三级审批，而非对所有资产一刀切地施加最重的审批负担。

## 知识关联

审批流程以**项目文档管理**为前置依赖。资产规范文档（Tech Spec）、美术风格指南（Art Bible）和功能设计文档（GDD）必须在审批流程启动前处于已批准状态，因为审批的判断基准来源于这些文档。缺乏文档支撑的审批会退化为主观意见的碰撞，而非标准符合度的客观判断。

向后，审批流程的效率数据（平均审批时长、CR拒绝率、Rejected资产比例）是**管线优化**的核心输入。例如，若统计显示角色资产的一级审批平均等待时间为4天，管线优化阶段可以通过引入自动化规范检查脚本（如自动验证面数、命名规范），将大量机械性检查工作从人工审批中剥离，把人工审批时间压缩至1天以内，从而释放高级美术的创意评审精力。