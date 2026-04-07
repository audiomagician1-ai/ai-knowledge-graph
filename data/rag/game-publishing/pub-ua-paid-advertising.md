---
id: "pub-ua-paid-advertising"
concept: "付费广告投放"
domain: "game-publishing"
subdomain: "user-acquisition"
subdomain_name: "用户获取(UA)"
difficulty: 1
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 付费广告投放

## 概述

付费广告投放（Paid User Acquisition）是游戏发行中通过向广告平台直接付费购买流量，将潜在玩家引导至游戏下载页面或内购转化路径的获客方式。与自然流量不同，付费投放的核心逻辑是：花费一定广告费用（Ad Spend）换取可量化的安装量或付费用户，其盈利可行性由 **ROAS（广告支出回报率）= 广告收入 ÷ 广告支出** 这一公式直接衡量。当 ROAS > 1 时广告盈利，低于 1 则亏损。

付费广告投放在移动游戏行业大规模兴起于 2012 年前后，随着 Facebook Mobile App Install Ads 和 Google UAC（Universal App Campaigns）的推出而成熟。2021 年 Apple 推出 ATT（App Tracking Transparency）隐私框架后，行业经历了重大转型——基于 IDFA 的精准定向能力大幅下降，促使买量团队转向聚合竞价、概率建模等新方法论。TikTok 则在 2020 年后迅速成为超休闲游戏和中重度游戏并重的主力投放渠道。

对游戏发行商而言，付费投放是唯一能在上线初期快速堆积用户规模、拉升 App Store 排名并形成社会证明效应的手段。与此同时，投放数据（CPM、CTR、IPM、CPI）也是验证游戏市场吸引力（Market Fit）的量化依据，是 GTM 策略落地的执行环节。

---

## 核心原理

### 三大主流平台的差异化逻辑

**Meta（Facebook/Instagram）** 的广告系统依赖用户兴趣标签和 Lookalike Audience（相似受众）建模。投放游戏时，通常以现有付费用户上传至 Meta Business Manager 构建 1%~3% 的 LAL 受众，再结合 AEO（App Event Optimization）或 VO（Value Optimization）出价方式，让系统自动寻找高价值用户。Meta 广告账户结构分三层：广告系列（Campaign）→ 广告组（Ad Set）→ 广告（Ad）。

**Google UAC** 则将 Google Play、YouTube、Google 搜索、展示网络四个渠道合并优化，投放侧重"目标 CPA 出价"或"目标 ROAS 出价"，学习期通常需要 7～14 天、积累约 50 个目标转化事件后才能退出冷启动阶段。游戏中设置合理的深度转化事件（如完成第 3 关、首次付费）是 UAC 起量的关键前提。

**TikTok Ads** 的算法更依赖创意素材本身的点击率（CTR）来驱动分发，而非依赖精准定向。超休闲游戏投放 TikTok 时，**IPM（每千次展示安装量）≥ 40** 通常被视为素材有效的基准线。TikTok 的素材生命周期较短，平均 7～14 天进入疲劳期，因此需要持续的 UGC 风格或 Playable 素材供给。

### 关键出价模型与成本结构

付费投放的出价模型主要分为：
- **CPM（Cost Per Mille）**：每千次展示付费，适合品牌曝光阶段；
- **CPI（Cost Per Install）**：每次安装付费，是手游买量最常见的结算方式；
- **CPA（Cost Per Action）**：按深度行为付费，如付费、注册，风险由平台承担更多；
- **ROAS 出价**：直接以收入回报为优化目标，需要 MMP（Mobile Measurement Partner，如 AppsFlyer、Adjust）回传精准的收入数据至广告平台。

健康的投放漏斗遵循公式：**CPI = CPM ÷ 1000 × 1/CTR × 1/CVR**，其中 CTR 是素材点击率，CVR 是商店页转化率。降低 CPI 的路径只有两条：提升素材 CTR，或优化商店页 CVR（即 ASO）。

### 广告素材的分层测试逻辑

付费投放中，素材测试通常采用 **A/B 测试**分阶段进行：首先以小预算（每个素材每日 $20～$50）测试 CTR，筛选出 CTR > 均值的素材进入第二轮，再以中等预算测试 CPI 和 D1 留存，最终保留能达到 ROAS 目标的素材放量。"广撒网，快迭代"是头部买量团队的素材策略——Voodoo、Zynga 等公司日均产出素材量超过 50 条。

---

## 实际应用

**超休闲游戏的投放实践**：典型超休闲游戏的目标 CPI 在 $0.20～$0.50（iOS 美国市场约 $0.80～$1.50），主要投放渠道为 TikTok 和 Meta，素材以 15 秒竖版视频为主，内容直接展示核心玩法的前 10 秒操作，尽量避免"游戏外"叙事。

**中重度 RPG 的投放实践**：目标用户 LTV 较高，可接受 CPI $5～$20，投放重心在 Meta VO 和 Google UAC ROAS 出价，素材多采用剧情化长视频（30～60 秒）展现游戏叙事深度。归因窗口设置为 7 天点击 + 1 天浏览，以匹配用户较长的决策周期。

**预注册期投放**：游戏未上线时，可通过 Meta "流量目标"广告引流至 Google Play 预注册页，同步积累 Lookalike 种子用户池，为正式上线首周买量做冷启动准备。

---

## 常见误区

**误区一：预算越大，效果越好**。付费投放存在"规模效应递减"规律——每日预算翻倍并不会使安装量等比翻倍，因为系统在高预算下会接触到意向更低的用户群体，导致 CPI 上升、ROAS 下降。正确做法是分阶段放量，每次预算调整幅度不超过 20%，等待系统重新学习后再评估。

**误区二：归因数据等于真实效果**。ATT 框架后，Meta 广告后台显示的安装数与 AppsFlyer 等 MMP 统计的安装数存在系统性差异（通常 Meta 高报 20%～60%），这是概率归因与确定性归因的模型差异导致的，而非数据造假。投放决策应以 MMP 数据为准，同时结合混合 MMP 报告（MMM）做宏观校验。

**误区三：好素材可以持续跑**。不少团队发现一条高 ROAS 素材后反复复用，忽视素材疲劳。实际上，同一受众群体多次看到相同素材后，CTR 会在 1～2 周内下降 30%～50%，需要基于原始素材做变体迭代（更换片头钩子、结尾 CTA、配色方案），而非从零开发全新素材。

---

## 知识关联

付费广告投放建立在 **UA 基础**（用户获取的漏斗模型、LTV/CPI 的基础概念）和 **GTM 策略**（目标市场选择、发行节奏、预算分配框架）之上，这两个前置概念决定了"在哪里投、投多少、投给谁"的战略方向。掌握这些前提后，投放团队才能将平台工具用于正确的目标受众和阶段。

付费投放的效果上限直接受 **ASO（应用商店优化）** 制约：即使素材 CTR 极高，若商店页转化率（CVR）低于 25%，CPI 依然难以达标。因此，ASO 是降低付费投放成本的结构性杠杆，是学习付费投放后必须并行掌握的下一个环节。从数据流向看，付费投放产生的用户行为数据（D1/D7 留存、付费率）也会反哺 ASO 的关键词策略和视频素材方向，形成闭环。