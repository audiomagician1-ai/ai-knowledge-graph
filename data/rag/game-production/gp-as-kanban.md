---
id: "gp-as-kanban"
concept: "Kanban方法"
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
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Kanban方法

## 概述

Kanban方法是一种以**可视化工作流**和**限制在制品数量**为核心手段的精益生产管理方法，名称来自日文"看板"（かんばん），意为"视觉信号板"。它起源于1940年代丰田汽车工程师大野耐一（Taiichi Ohno）开发的丰田生产系统（TPS），最初用于控制汽车零件的补货节奏。2007年，David Anderson将Kanban正式引入软件开发领域，并发布了《Kanban: Successful Evolutionary Change for Your Technology Business》一书，奠定了现代软件Kanban的理论基础。

在游戏开发中，Kanban特别适合**持续交付型任务流**——例如每日需要处理的Bug修复、资产审核、本地化更新等没有固定冲刺边界的工作。与Scrum以固定Sprint为单位不同，Kanban以**单件流动**（one-piece flow）为目标，强调让每张任务卡片从"待办"到"完成"的时间（即周期时间，Cycle Time）尽可能短且可预测。

## 核心原理

### 看板墙（Kanban Board）的结构

一块标准的游戏开发Kanban墙至少包含三列：**待办（Backlog）、进行中（In Progress）、完成（Done）**。实际项目中往往扩展为5~8列，例如：`需求分析 → 开发 → 代码审查 → QA测试 → 待发布 → 已发布`。每张卡片代表一个独立工作项（Work Item），卡面上记录描述、负责人、创建日期和优先级标签。看板墙的核心价值在于让整个团队**一眼看到所有工作的当前状态**，无需每日站会报告"我在做什么"。

### WIP限制（Work-In-Progress Limit）

WIP限制是Kanban区别于简单任务板的本质特征。每一列都设有最大在制品数量上限，例如"开发"列WIP=3意味着同时最多只能有3张卡片处于开发状态。当某列达到WIP上限，上游人员**必须停止新增工作，转而协助解决下游瓶颈**，这一机制强制暴露团队的真实产能瓶颈。

WIP限制的理论依据来自**利特尔定律（Little's Law）**：

> **L = λ × W**

其中 L 为系统中的平均在制品数量，λ 为平均到达率（每天新增任务数），W 为平均周期时间。在 λ 保持稳定的情况下，降低 L（即收紧WIP限制）可以直接缩短 W（周期时间）。对游戏QA团队而言，若每天新增5个Bug报告（λ=5），当前有40个Bug在处理中（L=40），则平均修复周期为8天；将WIP从40压缩到20后，周期时间理论上缩短至4天。

### 流动效率（Flow Efficiency）

流动效率的计算公式为：

> **流动效率 = 主动工作时间 / (主动工作时间 + 等待时间) × 100%**

大多数未优化的软件团队流动效率仅有**5%~15%**，即一张卡片85%以上的时间在等待而非被处理。游戏开发中常见的等待点包括：等待美术资产、等待主程序代码审查、等待制作人确认需求。Kanban通过WIP限制和可视化等待队列，帮助团队识别并消除这些隐性等待时间，将流动效率提升至30%以上。

### 累积流图（Cumulative Flow Diagram，CFD）

CFD是Kanban的核心度量工具，X轴为时间，Y轴为累积任务数，每条彩色带代表看板上的一个泳道（列）。健康的CFD应呈现**各色带宽度基本稳定、整体平滑向上**的形态。

- **色带变宽**：该列发生堆积，出现瓶颈
- **色带变窄**：工作项被快速消化或停止流入
- **任意两条带线之间的垂直距离**：代表当前该阶段的在制品数量
- **任意两条带线之间的水平距离**：代表平均周期时间

例如，若游戏QA列的色带在发布前两周突然加宽，CFD会立即显示出Bug积压趋势，团队可提前调配人力而非等到里程碑日才发现问题。

## 实际应用

**游戏运营团队的内容更新流水线**是Kanban的典型应用场景。某移动游戏运营团队将活动内容制作流程拆分为：`策划案 → 美术制作 → 前端实现 → QA验收 → 上线审核 → 已上线`，各列WIP限制分别设为3/4/3/5/2/∞。当"前端实现"列频繁触及WIP=3的上限时，CFD显示该列色带持续加宽，团队由此发现前端开发是唯一瓶颈，将一名策划人员临时调配学习前端辅助工作，活动交付周期从平均14天缩短至9天。

**DLC后期Bug修复阶段**也常采用Kanban替代Scrum。Sprint结构在Bug数量不可预测时会导致冲刺目标频繁失败，改用Kanban后团队按Bug优先级拉取工作，CFD实时反映修复速率是否能赶上新增速率，配合燃尽图（来自Scrum经验）预测发布日期。

## 常见误区

**误区一：把Kanban看板等同于任何任务清单软件**。Jira、Trello等工具可以显示卡片和列，但如果没有设置和遵守WIP限制，只是一个电子便利贴板，无法实现流动优化。真正的Kanban要求团队有意识地**在WIP触发上限时停止拉取新任务**，这是行为准则而非工具功能。

**误区二：WIP限制越低越好**。将WIP设为1看似最极致的精益，实际上在游戏开发中会导致开发人员因等待外部反馈（如音效、动画）而大量空闲，降低资源利用率。WIP限制应根据团队实际并发处理能力设定，通常初始值建议设为**团队人数的1.5倍**，再根据CFD数据逐步调整。

**误区三：Kanban没有节奏，完全自由**。Kanban取消了固定Sprint，但并非没有节律。Anderson提倡定期举行**补货会议（Replenishment Meeting）**决定哪些工作项进入待办队列，以及**交付评审（Delivery Review）**检视已完成工作，频率通常为每1~2周一次，维持必要的团队同步节奏。

## 知识关联

学习Kanban之前需要掌握**速率（Velocity）与燃尽图**的概念：Kanban用周期时间（Cycle Time）和吞吐量（Throughput）替代Scrum中的速率作为核心度量指标，理解速率的局限性有助于明白为何流动度量更适合无固定冲刺的场景。CFD可视为燃尽图的多维升级版，将单一剩余工作量曲线扩展为多阶段的流量可视化。

掌握Kanban方法后，可自然过渡到**Scrumban**的学习——Scrumban混合了Scrum的固定冲刺节奏与Kanban的WIP限制机制，适用于游戏开发中功能开发（需要Sprint计划）与维护任务（持续流入）并存的团队。Scrumban中如何设定冲刺边界与WIP上限的协同关系，正是在Kanban单独使用的局限性中产生的实践需求。