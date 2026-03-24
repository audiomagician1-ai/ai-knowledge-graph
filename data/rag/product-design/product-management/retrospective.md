---
id: "retrospective"
concept: "迭代回顾"
domain: "product-design"
subdomain: "product-management"
subdomain_name: "产品管理"
difficulty: 2
is_milestone: false
tags: ["敏捷"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 迭代回顾

## 概述

迭代回顾（Sprint Retrospective）是Scrum框架中每个Sprint结束时举行的固定仪式，专注于检视团队的工作方式本身，而非产品功能。它与Sprint评审（Sprint Review）的根本区别在于：评审面向产品"做了什么"，而回顾面向过程"怎么做的"。这一会议由Jeff Sutherland和Ken Schwaber在1990年代系统化Scrum时确立，是将持续改进（Kaizen）思想落地到敏捷团队日常运营的核心机制。

Scrum指南规定，迭代回顾的时间盒（Timebox）为最多3小时（针对一个月长的Sprint），更短的Sprint对应更短的时间。例如两周Sprint的回顾通常控制在1.5小时以内。会议的参与者固定为整个Scrum团队：开发人员、Scrum Master和产品负责人（Product Owner），外部干系人不参加，以确保团队能坦诚讨论。

迭代回顾之所以不可或缺，是因为它是Scrum团队唯一一个专门审视**流程、工具、关系、沟通方式**的会议。没有这个环节，团队容易陷入"重复同样错误"的循环，技术债和协作摩擦会随时间累积而非改善。

## 核心原理

### 三段式结构：收集数据 → 洞察 → 行动

经典的迭代回顾遵循Esther Derby和Diana Larsen在《敏捷回顾》（2006年）中提出的五阶段框架，实践中通常压缩为三个核心步骤：

1. **收集数据（Gather Data）**：聚焦刚结束Sprint中发生的客观事件和主观感受，例如"本次Sprint有3个故事点未完成"或"代码审查等待时间平均超过2天"。
2. **产生洞察（Generate Insights）**：通过结构化讨论找出根本原因，而非停留在表象。常用工具是"5个为什么"（5 Whys）追问法。
3. **决定行动（Decide What to Do）**：从洞察中提炼出1至3条可执行的改进项，明确负责人和完成时间，通常写入下一个Sprint的待办列表。

### 常用回顾技法

**Start/Stop/Continue** 是最简单的回顾格式，要求每位成员分别列出：应该开始做的事、应该停止做的事、应该继续保持的事。这个格式适合新组建的团队，时间可控，约60分钟完成。

**四象限法（Mad/Sad/Glad + Learned）** 让成员从情绪维度表达对Sprint的感受，常配合便利贴和计时投票（Dot Voting）使用。每人通常获得3至5个投票点，票数最多的话题优先讨论。

**时间轴回顾（Timeline Retrospective）** 将Sprint的关键事件按时间顺序排列在白板上，帮助团队共建对Sprint的集体记忆，特别适合刚经历了重大变化（成员更迭、技术事故）的Sprint。

### Scrum Master的角色：引导而非主持

Scrum Master在回顾中承担**引导者（Facilitator）**角色，负责创造安全的对话环境，但不主导结论。具体职责包括：设置保密原则（"Vegas Rule"：讨论内容不向外透露）、管理时间盒、防止讨论偏离流程话题、确保每位成员都有发言机会。产品负责人在回顾中是参与者而非决策者，其主要贡献是分享从外部视角观察到的团队协作问题。

## 实际应用

**案例：电商平台团队的发布流程改进**

某六人产品开发团队在连续三个Sprint中都出现"最后一天集中修复Bug"的现象。在第四次回顾中，Scrum Master使用5 Whys技法追问：为什么最后一天Bug多？→ 因为集成测试太晚 → 因为各功能独立开发 → 因为没有定义"功能可测试"的完成标准。最终团队决定将"通过集成测试"加入Definition of Done（完成标准），并在下个Sprint每日站会中加入"是否可测试"的检查。这一改进在两个Sprint后将发布日故障率从每次平均7个降至2个。

**案例：远程团队的异步回顾**

全球分布式团队因时区差异难以同步参加90分钟回顾，改为使用Miro白板进行24小时异步数据收集（Start/Stop/Continue便利贴），再用45分钟同步视频会议聚焦投票最高的3个话题。这种混合格式将参与率从60%提升至95%。

## 常见误区

**误区一：把回顾变成抱怨会**

回顾的讨论对象应是**流程和系统性问题**，而非特定个人的表现。当讨论滑向"某人总是迟交代码"时，Scrum Master应将问题重新框架为"什么系统性因素导致代码交付延迟？"将个人批评转化为流程审查，这是回顾中最常见也最需要刻意管理的问题。

**误区二：改进项过多且无人负责**

许多团队在回顾结束时列出8至10条改进建议，但没有明确负责人和截止时间，结果下次回顾时没有任何一条得到落实。Scrum指南建议每次回顾的可执行改进项不超过**3条**，且每条必须回答：谁负责、何时完成、如何验证。未完成的改进项应在下次回顾开始时首先检视。

**误区三：认为团队成熟后可以省略回顾**

即使团队运转顺畅，跳过回顾会导致改进节奏断裂，团队逐渐丧失反思习惯。正确做法是根据成熟度调整格式——成熟团队可缩短至45分钟并采用更聚焦的话题讨论，但不应完全取消这一时间盒。

## 知识关联

迭代回顾建立在对**Scrum框架**完整结构的理解之上，特别需要清楚它在Sprint四个事件（计划、每日站会、评审、回顾）中的最后位置——回顾是Sprint的最后一个事件，发生在评审之后、下一个Sprint计划之前，确保改进行动可以立即进入下一个计划周期。

理解回顾还需要掌握**Definition of Done（完成标准）**和**Sprint待办列表（Sprint Backlog）**，因为回顾产生的改进项通常以任务形式直接进入Sprint Backlog，或以条目形式修改Definition of Done。如果一个团队无法清晰定义"完成"，回顾中识别出的流程问题也难以转化为可验证的改进。
