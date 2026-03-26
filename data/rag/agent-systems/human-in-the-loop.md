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
quality_tier: "B"
quality_score: 46.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
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

人在回路（Human-in-the-Loop，简称HITL）是一种AI系统设计模式，要求在Agent的决策或执行流程的特定节点处，强制暂停自动化执行并等待人类操作员的审批、修正或确认，才能继续后续步骤。与完全自主的Agent不同，HITL系统将人类判断力嵌入工作流的关键检查点，而非只在事后审查结果。

HITL这一术语最早源于20世纪60年代的控制系统工程，最初用于描述导弹制导、核武器授权等高风险场景中必须由人类做出最终发射决定的机制。随着大语言模型驱动的Agent系统在2022年后快速普及，HITL被移植到AI工程领域，成为防止Agent"失控执行"的标准架构模式之一，LangGraph、AutoGen等主流Agent框架均内置了HITL检查点接口。

HITL之所以在Agent系统中不可或缺，根本原因在于当前LLM存在幻觉（hallucination）问题，且Agent往往拥有操作文件系统、调用外部API、发送邮件或执行数据库写入等不可逆动作的权限。一旦允许完全自主执行，单次错误决策的代价可能远超人工介入的时间成本。

---

## 核心原理

### 检查点触发机制

HITL的核心结构是在Agent状态机中定义**中断节点（interrupt node）**。以LangGraph为例，开发者通过`interrupt_before=["node_name"]`参数声明哪些节点在执行前必须暂停。当Agent运行到该节点时，整个执行图的状态会被序列化保存至持久化存储（如Redis或PostgreSQL），系统向人类操作员发出通知，等待其通过`graph.update_state()`注入新指令或直接批准原始计划后，执行才得以恢复。这一"暂停-持久化-恢复"的三步流程是HITL区别于普通条件分支的本质特征。

### 三种干预粒度

HITL干预可分为三个粒度等级：

- **批准/拒绝（Approve/Reject）**：最轻量级，人类只需对Agent已生成的计划给出二元判断，适用于邮件发送、订单提交等离散操作。
- **内容修正（Edit）**：人类可直接修改Agent下一步要执行的工具调用参数或消息内容，例如在Agent调用`send_email(to="all@company.com")`前将收件人范围缩小。
- **重新规划（Replan）**：人类完全推翻Agent的当前子目标，注入新的指令集，要求Agent从当前状态重新规划后续步骤，适用于Agent产生严重方向性偏差的场景。

### 同步HITL与异步HITL

同步HITL要求Agent实时等待人类响应，整个对话线程阻塞，适合低延迟交互任务。异步HITL则允许Agent将当前任务挂起，同时处理其他工作，待人类响应到达后从持久化状态恢复执行。异步模式下，**任务超时策略**至关重要：若人类在设定时限（如24小时）内未响应，系统必须有明确的降级行为——是自动拒绝操作、还是升级通知给更高权限操作员，这一策略必须在设计阶段显式声明，不能依赖Agent自行决定。

---

## 实际应用

**金融交易Agent**：一家使用LLM Agent自动化处理采购订单的企业，将HITL检查点设置在"金额超过5000元的付款指令生成后、实际API调用前"。Agent将起草好的付款JSON传给财务审核员，审核员可在企业内部审批系统中修改供应商账户或金额，点击"确认"后Agent才执行真实的银行转账接口调用。

**代码部署Agent**：在CI/CD流水线中使用Agent自动生成Terraform基础设施变更方案时，HITL检查点被插入`terraform plan`输出之后、`terraform apply`执行之前。运维工程师审查资源变更差异，确认不涉及生产数据库的意外删除操作后，再授权Agent执行`apply`命令。

**医疗文档辅助Agent**：帮助医生生成病历摘要的Agent中，HITL要求医生对每份AI生成的摘要进行逐条确认，尤其是涉及诊断结论和用药剂量的句子，医生可直接编辑错误内容再提交至电子病历系统，此类场景下Agent的角色严格限定为"起草助手"而非"最终决策者"。

---

## 常见误区

**误区一：在所有节点都加入HITL就是最安全的设计。** 这一做法会使Agent退化为人类手动操作的复杂UI，彻底失去自动化价值。正确做法是根据操作的**不可逆性**和**影响范围**来决定是否插入检查点：读取操作通常无需HITL，写入/删除/对外通信等操作才需要评估风险级别后决定。过度的HITL会造成"警报疲劳"，使操作员对每次审批请求都习惯性地点击批准，反而降低安全性。

**误区二：HITL是Agent系统不成熟的临时补丁，未来完全自主Agent将取代它。** 这混淆了"技术能力"与"责任归属"两个维度。即便LLM技术大幅进步，在法律合规、医疗诊断、金融授权等领域，人类监督的存在是监管要求和责任链条的一部分，而非仅仅是技术缺陷的弥补。欧盟AI法案（EU AI Act，2024年正式生效）明确要求高风险AI系统必须保留人类监督机制，这与LLM能力强弱无关。

**误区三：HITL干预后Agent能自动理解人类修改的意图。** 实际上，人类通过`update_state`修改了Agent的工具调用参数后，Agent在下一步执行时并不自动"感知"到被修改的原因。若不在系统提示或状态消息中显式告知修改原因，Agent可能在后续步骤中再次犯相同错误。良好的HITL设计应将人类修改内容作为带标注的反馈写回Agent上下文，而非仅替换参数值。

---

## 知识关联

从**AI Agent概述**中学习的"感知-规划-行动"循环是理解HITL插入位置的基础：检查点通常位于"规划输出"到"行动执行"之间的边界处，即拦截Agent即将调用工具或产生外部副作用的瞬间。HITL本质上是对Agent自主行动权的条件性授予，需要学习者已掌握Agent工具调用机制和状态管理的基本概念。

在后续的**Agent安全护栏**主题中，HITL将作为一类"主动拦截"机制与其他防护手段形成对比：护栏（Guardrails）侧重于自动化的内容过滤和策略检测，而HITL侧重于将人类判断力引入决策链路。两者可以组合使用——护栏先过滤明显违规输出，通过护栏但仍存在不确定性的高风险操作再提交HITL审批，从而在自动化效率与人类监督之间取得精确平衡。