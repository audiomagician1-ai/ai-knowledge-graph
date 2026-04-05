---
id: "se-arch-decision"
concept: "架构决策记录"
domain: "software-engineering"
subdomain: "architecture-patterns"
subdomain_name: "架构模式"
difficulty: 2
is_milestone: false
tags: ["文档"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 架构决策记录

## 概述

架构决策记录（Architecture Decision Record，简称 ADR）是一种轻量级文档，用于记录软件项目中每一个重要架构决策的背景、选项、权衡与最终结论。每份 ADR 通常只描述**一个**决策，文件长度控制在一页左右，使团队成员可以快速阅读并理解当时为何做出某个选择。ADR 由 Michael Nygard 于 2011 年在其博客文章 *Documenting Architecture Decisions* 中正式提出并推广，此后成为软件架构社区中记录技术选型的主流方式之一。

ADR 最重要的价值在于解决"为什么这样设计"的失忆问题。当一名新工程师加入团队，面对代码库中看似奇怪的技术选择时，没有 ADR 的情况下他只能猜测原因，甚至重蹈已被团队否定过的方案；而一份清晰的 ADR 可以在几分钟内还原决策时的完整语境。许多架构问题的根源不是技术本身的缺陷，而是后来者在不了解约束条件的情况下推翻了已经过深思熟虑的决策。

ADR 属于"活文档"体系，通常与代码一同存储在版本控制系统（如 Git）中，放在项目根目录的 `docs/adr/` 或 `architecture/decisions/` 文件夹下，每个文件以 `0001-use-postgresql.md`、`0002-adopt-event-sourcing.md` 这样带序号的方式命名，保证历史可追溯。

---

## 核心原理

### ADR 的标准结构

Nygard 最初提出的 ADR 模板包含五个字段：

| 字段 | 说明 |
|------|------|
| **标题（Title）** | 一句话概括决策内容，如"使用 PostgreSQL 作为主数据库" |
| **状态（Status）** | Proposed / Accepted / Deprecated / Superseded |
| **背景（Context）** | 驱动此次决策的技术约束、业务需求与时间节点 |
| **决策（Decision）** | 明确说明选择了什么，以主动语态写出，如"我们将采用……" |
| **后果（Consequences）** | 列出该决策带来的正面与负面影响，不回避代价 |

后续社区在此基础上扩展出 **MADR（Markdown Architectural Decision Records）** 格式，增加了"考虑过的选项（Considered Options）"和"决策驱动因素（Decision Drivers）"两个字段，更适合在技术选型评估场景中横向比较多个候选方案。

### 状态流转机制

ADR 的 Status 字段遵循明确的状态机规则：初始状态为 `Proposed`，经团队评审通过后变为 `Accepted`；若该决策后来被证明存在问题，可标记为 `Deprecated`；若被另一份新 ADR 替代，则标记为 `Superseded by ADR-0015`，并在新 ADR 中注明 `Supersedes ADR-0008`，形成双向引用链。这一机制确保旧决策不会被静默删除，团队可以完整回溯决策演进路径。

### 技术选型评估框架（Decision Matrix）

在撰写 ADR 的"考虑过的选项"部分时，常结合**加权决策矩阵（Weighted Decision Matrix）**进行量化评估。评估步骤如下：

1. 列出所有候选方案（通常 2–4 个）；
2. 确定评估维度，如性能、社区活跃度、运维复杂度、团队熟悉程度；
3. 为每个维度分配权重（所有权重之和为 1.0）；
4. 对每个方案在各维度打分（1–5 分）；
5. 计算加权总分：`Score = Σ(weight_i × rating_i)`

例如，在"消息队列选型"ADR 中，若将"运维复杂度"权重设为 0.4、"吞吐量"权重设为 0.35、"团队经验"权重设为 0.25，则 RabbitMQ 与 Kafka 的最终得分差异会直接体现在文档中，使决策过程对所有利益相关方透明可审计。

---

## 实际应用

**微服务拆分决策**：某电商平台在 2022 年将单体应用拆分为微服务时，团队为每一次服务边界划分都编写了 ADR。其中 `ADR-0003-split-order-and-inventory.md` 明确记录了"订单服务与库存服务分离"这一决策，背景部分写明两个模块的数据库写争用导致超卖，决策部分列出了独立部署后的最终一致性代价，后果部分说明需要引入 Saga 模式处理分布式事务。六个月后，当团队考虑重新合并这两个服务时，这份 ADR 直接阻止了重蹈覆辙，因为原始约束仍然存在。

**API 版本策略选型**：在制定 REST API 版本控制策略时，团队通过 ADR 对比了 URI 路径版本（`/v1/users`）、请求头版本（`Accept: application/vnd.company.v2+json`）和查询参数版本（`?version=2`）三种方案。ADR 最终选择 URI 路径方案，并在"后果"字段中如实记录了该方案导致 URL 变得冗长的缺点，以及为何在该团队的网关架构下这一代价可以接受。

**数据库技术选型**：团队在选择时序数据库时，使用 MADR 格式对比了 InfluxDB、TimescaleDB 和 Victoria Metrics，决策矩阵中明确标注了 InfluxDB 在 2.x 版本引入 Flux 语言后查询语法变更导致的迁移成本，这一具体的版本信息成为否决 InfluxDB 的关键依据并永久保存在 ADR 文档中。

---

## 常见误区

**误区一：将 ADR 写成技术调研报告**。ADR 不是论文，"背景"字段应只包含**驱动此次决策的直接约束**，而非关于某项技术的完整介绍。一份 ADR 若超过 500 字，通常说明边界不清，包含了与本次决策无关的背景知识。正确做法是只写"为什么现在需要做这个决定"，而非"这个技术是什么"。

**误区二：只记录成功的决策，回避失败的选项**。许多团队在 ADR 的"考虑过的选项"部分只写最终选择，把被否决的方案删掉。这恰恰丢失了 ADR 最有价值的部分——为什么某个看起来很好的方案被放弃了。例如，若团队当时因为不熟悉 Rust 而选择了 Go，这个理由本身就应该写进 ADR，否则三年后一名 Rust 专家加入时会重新提议切换，引发不必要的重复辩论。

**误区三：认为 ADR 只适合大型架构决策**。实际上，ADR 同样适合记录"是否引入某个第三方库""统一使用驼峰还是下划线命名""错误码格式约定"这类中等粒度的决策。Michael Nygard 的原则是：**凡是会引起合理工程师之间真实争论的技术选择，都值得一份 ADR**。

---

## 知识关联

学习 ADR 需要具备**软件架构概述**中对架构关注点分离（separation of concerns）和架构约束（architectural constraints）的理解，因为 ADR 的"背景"字段本质上是在描述当时存在哪些架构约束驱动了决策。同时，**API 设计原则**是 ADR 在实践中最高频的使用场景之一——版本控制策略、端点命名规范、认证机制选择，几乎每一个 API 设计决策都值得对应一份 ADR，因此理解 REST 约束、幂等性等 API 基础概念有助于写出高质量的 API 相关 ADR 背景描述。

在工程实践中，ADR 体系常与**架构适应度函数（Fitness Functions）**和 **RFC（Request for Comments）流程**配合使用：RFC 用于决策前的广泛征集意见，ADR 用于记录最终达成共识的决策，适应度函数用于在 CI/CD 中自动验证决策是否被遵守。掌握 ADR 之后，可以进一步学习 C4 模型（Context、Container、Component、Code）等架构可视化方法，将文字决策记录与图形化架构描述结合，构建更完整的架构文档体系。