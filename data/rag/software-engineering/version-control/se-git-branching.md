---
id: "se-git-branching"
concept: "Git分支策略"
domain: "software-engineering"
subdomain: "version-control"
subdomain_name: "版本控制"
difficulty: 2
is_milestone: true
tags: ["分支"]

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
updated_at: 2026-03-26
---


# Git分支策略

## 概述

Git分支策略是团队约定的、规范化使用Git分支进行协作开发的工作方式，它规定了何时创建分支、如何命名分支、分支何时合并以及合并到哪里。不同策略对发布节奏、团队规模和代码质量门槛有截然不同的假设，选错策略会导致长期未合并的"僵尸分支"、频繁的合并冲突或无法做到持续交付。

Git分支策略的讨论始于2010年，Vincent Driessen在当年发表了题为"A successful Git branching model"的博文，提出了Git Flow模型，引发广泛讨论。此后GitHub于2011年前后推行GitHub Flow，Scott Chacon将其总结为只有`main`和feature分支的轻量模式。Google等公司长期实践的主干开发（Trunk-Based Development）则在2016年由Paul Hammant系统整理成网站trunk-baseddevelopment.com，成为持续集成运动的重要参考。

选择分支策略直接影响CI/CD管道设计：Git Flow的多条长期分支要求分别配置不同的自动化流水线，而Trunk-Based只需一条针对`main`的流水线。错误的策略选型是"合并地狱"和"发布阻塞"最常见的根源。

---

## 核心原理

### Git Flow：双主干 + 三种辅助分支

Git Flow维护两条永久分支：`main`（或`master`）始终代表生产就绪代码，`develop`是集成分支。辅助分支分三类：

- **feature/** ：从`develop`切出，完成后合并回`develop`，生命周期通常为数天到数周。
- **release/** ：从`develop`切出，只允许做bug修复和版本号更新，合并到`main`并打tag，同时回合并到`develop`。
- **hotfix/** ：从`main`切出，修复后同时合并到`main`和`develop`。

这种模型适合**有固定发布窗口**的软件，例如移动端App每两周发一版。其代价是：feature分支存活时间长，`develop`与`feature`之间的差异持续累积，发布前的"集成周"经常出现大量冲突。

### GitHub Flow：单主干 + 短生命周期feature分支

GitHub Flow只有一条长期分支`main`，所有工作均从`main`切出feature分支，完成后通过Pull Request合并回`main`，合并后立即部署到生产。Scott Chacon的原版总结只有6条规则，核心约束是：**`main`上的任何提交必须随时可部署**。

该模型假设团队拥有完善的自动化测试覆盖和一键部署能力。feature分支的推荐存活时间不超过1天到3天，超过则预示着任务拆分不合理。它适合Web服务这类能做到每日多次部署的场景，不适合需要同时维护多个已发布版本的客户端软件。

### Trunk-Based Development：提交直接到主干

TBD（主干开发）要求开发者每天至少一次将代码推送到`main`（主干），几乎不允许存活超过2天的分支。对于大型团队，允许存在"短暂feature分支"（short-lived feature branches），但必须在当天或次日合并。

TBD强依赖两项技术：**Feature Flag**（功能开关）和**Branch by Abstraction**。未完成的功能通过Feature Flag在代码层面隐藏，而非通过分支隔离，这使得`main`始终可构建、可部署。DORA（DevOps Research and Assessment）的研究数据表明，使用TBD的团队比使用长期分支策略的团队交付吞吐量高出约46倍（2019年State of DevOps Report数据）。

### 三种策略的关键指标对比

| 维度 | Git Flow | GitHub Flow | TBD |
|------|----------|-------------|-----|
| 长期分支数 | 2条（main + develop） | 1条 | 1条 |
| feature分支寿命 | 数天～数周 | 1～3天 | ≤1天或不建分支 |
| 适合发布频率 | 周/月级 | 日/小时级 | 日多次级 |
| 版本回滚方式 | revert或tag checkout | revert commit | Feature Flag关闭 |

---

## 实际应用

**移动端App团队使用Git Flow**：iOS应用每两周提交App Store审核，团队从`develop`切出`release/2.4.0`后，只允许合并QA反馈的修复，同时新功能继续在各自的`feature/xxx`分支开发。这样避免了"新功能污染待审核版本"的问题。

**SaaS产品使用GitHub Flow**：一个5人的Web创业团队，每个开发者每天提一个PR，CI跑测试通过后由同事review，合并即触发Heroku自动部署到生产。整个流程平均耗时2小时，无需专职发布经理。

**大厂核心服务使用TBD**：Facebook（Meta）的主仓库长期采用主干开发，新功能通过GateKeeper（内部Feature Flag系统）向1%用户灰度开放，逐步扩大到100%。这使得同一份代码可以同时为不同用户提供不同功能体验，而无需维护多条代码线。

---

## 常见误区

**误区一：Git Flow适合所有"正式"项目**。很多团队认为分支越多、流程越复杂就越"专业"，在5人小团队的Web项目中强行引入Git Flow的6类分支。实际结果是`develop`分支经常两周没有人更新，feature分支在无人关注中悄悄发散，最终合并时需要手动解决数百行冲突。Git Flow的成本只在**需要维护多个并行发布版本**时才值得付出。

**误区二：TBD等于没有代码审查**。看到"直接提交到main"，许多人误以为TBD放弃了代码质量控制。恰恰相反，TBD依赖更高密度的代码审查——Google内部要求每个提交都必须经过至少一名评审者审批，配合Pre-commit Hook和自动化测试保障质量，而非依靠分支隔离来兜底。

**误区三：GitHub Flow就是"没有release分支"**。GitHub Flow确实不设release分支，但这并不意味着没有版本管理。它通过Git Tag标记每次部署到生产的commit（如`v2024.03.15`），需要回滚时直接revert对应commit或重新部署上一个tag，版本历史同样完整清晰。

---

## 知识关联

学习Git分支策略需要先掌握**Git基础**中的分支创建（`git branch`）、切换（`git checkout`/`git switch`）和本地合并（`git merge`）操作，否则无法理解"从`develop`切出feature分支并合并回去"的操作含义。

理解分支策略后，下一步需要深入学习**Merge与Rebase**的区别：Git Flow通常使用`--no-ff`合并保留分支历史记录，而GitHub Flow和TBD的拥护者倾向于使用`rebase`后再`fast-forward merge`，以保持线性的`main`历史。两种做法在策略层面有直接的哲学差异。**Pull Request工作流**则是GitHub Flow和TBD在团队协作中的具体落地机制，PR的粒度直接体现了feature分支应有多小的约束。