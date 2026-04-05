---
id: "human-in-the-loop"
concept: "人在回路(HITL)"
domain: "ai-engineering"
subdomain: "agent-systems"
subdomain_name: "Agent系统"
difficulty: 6
is_milestone: false
tags: ["Agent", "安全"]

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
updated_at: 2026-03-26
---


# 人在回路（HITL）

## 概述

人在回路（Human-in-the-Loop，HITL）是指在AI Agent的决策或执行流程中，在特定节点强制引入人类判断与审批的系统设计模式。与完全自动化的Agent不同，HITL并不意味着人类全程参与，而是通过精确定义的"中断点"（interrupt point）让人类介入关键决策，之后Agent继续执行后续步骤。这一模式最早在军事指挥自动化系统中被正式提出，用于核武器发射授权流程，后逐渐演化为AI工程领域的通用设计范式。

HITL之所以在Agent系统中受到重视，根本原因在于当前LLM-based Agent存在不可消除的幻觉率（hallucination rate）——GPT-4在特定任务上的幻觉率仍可达3%-15%。当Agent执行的是发送邮件、提交代码、执行数据库删除等不可逆操作时，哪怕1%的错误率也会造成真实损失。HITL通过在高风险动作前引入人类确认，将不可逆错误的发生概率限制在人类判断失误的范围内。

## 核心原理

### 中断点的设计与触发条件

HITL系统的核心设计问题是：在哪些条件下触发人工审批？常用的触发策略包括三类：**基于操作类型**（如凡涉及外部API写操作必须审批）、**基于置信度阈值**（如Agent的规划置信分低于0.7时暂停）、以及**基于影响范围**（如涉及资金超过$500或影响超过100名用户的操作）。LangGraph框架中通过`interrupt_before`和`interrupt_after`参数显式配置这些中断点，开发者将特定节点名称传入后，Graph执行引擎会在该节点前/后自动暂停并将状态序列化等待人工响应。

### 状态持久化与恢复机制

HITL不是简单地"暂停等待"，而是需要将Agent的完整执行状态持久化到外部存储（如数据库或Redis），以支持任意时长的等待与跨进程恢复。LangGraph使用Checkpointer机制实现这一点：每次触发中断时，当前的Graph State（包括消息历史、工具调用记录、中间变量）被序列化存入Checkpointer，并生成唯一的`thread_id`和`checkpoint_id`。人类审批后，系统通过`Command(resume=...)`命令注入审批结果，Graph从精确的断点位置恢复执行，而非从头重新运行。这一机制使HITL可以支持异步工作流——审批者可能在数小时后才给出响应。

### 人类干预的三种模式

HITL中人类的干预粒度分为三个层级：

1. **批准/拒绝（Approve/Reject）**：最简单的模式，人类仅确认Agent的既定计划是否可以执行，不修改任何内容。适用于发送邮件审批场景。

2. **编辑后继续（Edit and Resume）**：人类可直接修改Agent生成的输出内容（如修改将要提交的代码）后，将修改版本作为新的状态注入，Agent继续后续步骤。LangGraph中通过`graph.update_state(config, new_values)`实现状态覆盖。

3. **提供反馈并重规划（Feedback and Replan）**：人类不直接修改结果，而是以自然语言形式提供批评性意见，Agent接收反馈后重新执行规划步骤。这是三种模式中人机交互最深的一种，常用于多步骤研究或代码生成任务。

## 实际应用

**自动化代码提交工作流**：一个负责修复GitHub Issue的Agent，在执行`git push`到主分支之前触发HITL中断。Agent将生成的diff、测试结果、以及自然语言解释同时展示给工程师。工程师可以选择批准推送、编辑具体代码后批准，或者添加"你需要同时更新相关测试文件"的反馈让Agent重新规划。中断点配置在`push_to_remote`节点的`interrupt_before`位置。

**财务报销审批Agent**：企业内部的报销处理Agent负责解析发票、核对预算、填写ERP系统。HITL触发规则设定为：金额超过¥5000、供应商名称首次出现、或发票日期与报销日期间隔超过90天的情况必须触发人工审核。审核界面向财务人员展示Agent的解析结果和置信度评分，财务人员确认后Agent完成ERP录入。

**多Agent协作中的HITL**：在一个由规划Agent、执行Agent和审计Agent组成的系统中，HITL可以只配置在Orchestrator Agent的任务分配节点，而非所有子Agent。这种选择性配置使人工介入次数从每次工具调用降至每个高层任务，显著减少了审批疲劳（approval fatigue）。

## 常见误区

**误区一：HITL越多越安全**。频繁的人工审批会产生"审批疲劳"现象——根据研究，当警报或审批请求过于频繁时，人类批准者的错误率会显著上升，甚至出现无意识地批准所有请求的"橡皮图章"行为。正确做法是使用风险矩阵精确区分哪些操作需要HITL，对低风险可逆操作允许Agent自主执行，将人类注意力集中于真正高风险的中断点。

**误区二：HITL等同于Human-on-the-Loop（HOTL）**。HITL要求人类介入后Agent才能继续执行（同步阻塞式），而HOTL是Agent异步执行，人类仅在事后监控结果并在发现问题时主动叫停。两者的关键区别在于控制权的归属：HITL中控制权在人类手中，HOTL中控制权默认在Agent手中。对于不可逆操作（如发送批量邮件），混淆两者会导致在误认为自己有HITL保护的情况下，实际上Agent已在无审批状态下完成操作。

**误区三：HITL只是在Agent前加一个人工审批按钮**。真正的HITL需要状态持久化、断点恢复、审批界面设计、超时处理（审批者长时间不响应时的降级策略）等一系列工程支持。缺少状态持久化的"HITL"在服务器重启后会丢失待审批任务；缺少超时处理的HITL会导致Agent工作流永久挂起。

## 知识关联

理解HITL需要先掌握AI Agent的基本架构——具体来说，必须清楚Agent的规划-行动-观察循环（Plan-Act-Observe cycle）在哪些阶段可以插入中断，以及Agent State的组成结构（LangGraph中State是一个TypedDict，其内容决定了中断时能向审批者展示哪些信息）。

HITL直接引出下一个关键概念：**Agent安全护栏（Guardrails）**。HITL解决的是"如何在关键节点引入人类判断"，而安全护栏解决的是"如何通过自动化规则在不打扰人类的情况下阻止危险行为"。两者构成互补关系：护栏处理可以明确规则化的风险（如禁止访问特定域名），HITL处理需要情境判断的风险（如某封邮件是否合适发送）。在实际Agent系统设计中，通常先用护栏过滤掉明确违规的操作，再用HITL对剩余高风险操作进行人工审核，形成分层防御体系。