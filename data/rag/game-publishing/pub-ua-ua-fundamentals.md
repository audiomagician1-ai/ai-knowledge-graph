---
id: "pub-ua-ua-fundamentals"
concept: "UA基础"
domain: "game-publishing"
subdomain: "user-acquisition"
subdomain_name: "用户获取(UA)"
difficulty: 1
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# UA基础

## 概述

用户获取（User Acquisition，简称UA）是游戏发行商通过付费或自然渠道将潜在玩家转化为实际安装用户的商业行为。在移动游戏领域，UA团队的核心任务是以可盈利的成本批量获取高质量用户，而非单纯追求安装量。一款游戏的UA策略直接决定其能否在 Apple App Store 或 Google Play 的排行榜上获得足够曝光，从而形成自然量的正向循环。

UA作为独立的专业分支，在2010年前后随着智能手机普及和应用商店生态成熟而兴起。彼时，Facebook Ads和AdMob开始向开发者提供基于用户行为的精准定向投放能力，UA从此脱离传统品牌营销范畴，演变为以数据驱动、ROI导向为核心的科学化运营体系。如今，一款中重度手游上线首月的UA预算可能高达数百万美元，UA团队的决策质量直接影响产品的生死。

与定价策略不同，UA的价值在于精确衡量每一分钱的投入产出比——而这套衡量体系的基础，正是CPI、CPA和ROAS三个核心指标。理解这三个指标的定义、计算方式和互动关系，是入门UA工作的第一步。

## 核心原理

### CPI：每次安装成本

CPI（Cost Per Install）是UA中最基础的采购指标，计算公式为：

**CPI = 广告总花费 ÷ 获得的安装总数**

例如，在某渠道花费10,000元获得2,000次安装，则CPI = 5元/次安装。CPI的高低受广告创意质量、目标受众竞争程度、目标国家市场（Tier）层级等多重因素影响。以美国市场（Tier 1）为例，休闲游戏的平均CPI约为1–2美元，而策略类游戏因目标受众更窄，CPI常高达5–15美元。CPI是UA团队判断渠道效率的快速筛选指标，但它只衡量获客成本，不反映用户质量。

### CPA：每次行为成本

CPA（Cost Per Action）将衡量维度从安装延伸至用户的后续行为，例如完成新手教程、达到关卡10、首次付费（First Purchase）或注册账号。计算公式为：

**CPA = 广告总花费 ÷ 完成目标行为的用户数**

假设上述2,000名安装用户中，有200人完成了首次付费，则首次付费CPA = 10,000元 ÷ 200 = 50元/付费用户。CPA比CPI更能反映用户质量，因为它过滤掉了只安装不活跃的"僵尸用户"。在程序化购买（Programmatic Buying）中，UA经理通常会为不同行为节点分别设置CPA目标值，并以此优化算法出价策略。

### ROAS：广告支出回报率

ROAS（Return On Ad Spend）是UA中最直接的盈利性指标，衡量每投入1元广告费能回收多少收入。公式为：

**ROAS = 广告带来的总收入 ÷ 广告总花费 × 100%**

业内通常以天数为维度来追踪ROAS，最常见的节点是D1（第1天）、D7（第7天）、D14、D30和D180。例如，某渠道D30 ROAS达到80%，意味着30天内已收回80%的投入成本；若D180 ROAS超过100%，则表明该批用户已实现盈利。不同品类的ROAS达标周期差异巨大：超休闲游戏依赖广告变现，通常要求D7 ROAS > 100%；而RPG类游戏的LTV（生命周期价值）释放周期可长达12–24个月，D30 ROAS可能仅有30–40%，但最终仍能盈利。

### UA基本流程

一次完整的UA投放流程包含以下五个步骤：
1. **选渠道**：根据目标用户画像选择Meta（Facebook/Instagram）、Google UAC、TikTok Ads、Unity Ads等投放平台；
2. **制作素材**：开发视频广告（通常15–30秒）、可试玩广告（Playable Ad）或横幅图片；
3. **设定归因**：接入AppsFlyer、Adjust或Singular等移动归因工具，追踪安装来源；
4. **小额测试**：以小预算（如每渠道每日100–500美元）跑量，收集初始数据；
5. **放量优化**：对CPI/CPA/ROAS表现达标的渠道和素材逐步增加预算（Scale），同时淘汰表现不佳的组合。

## 实际应用

**案例：某三消游戏冷启动UA决策**

一款三消游戏在软上线（Soft Launch）阶段，UA团队在加拿大市场测试了三个渠道。Meta渠道CPI为1.8美元，D7 ROAS为65%；Google UAC的CPI为2.3美元，但D7 ROAS为82%；TikTok的CPI最低为0.9美元，但D7 ROAS仅为31%。

尽管TikTok的CPI看起来最吸引人，UA经理选择优先放量Google UAC——因为更高的ROAS说明Google带来的用户付费能力更强，即使单次安装成本更高，整体投资回报更优。这个决策体现了UA工作中"不能只看CPI"的核心原则。

**归因窗口的实际影响**

AppsFlyer默认的归因窗口为点击后7天（Click-Through Attribution Window）。这意味着用户点击广告后7天内安装游戏，该安装才会归因到对应广告渠道。若将窗口错误设置为30天，会导致自然量被错误地计入付费渠道，虚报渠道效果，UA预算决策因此失准。

## 常见误区

**误区一：CPI越低代表UA效果越好**

这是UA新手最常见的错误认知。低CPI可能意味着广告定向过于宽泛，吸引了大量与游戏目标用户不匹配的人群，导致次日留存率（D1 Retention）极低，ROAS惨淡。正确的做法是将CPI与CPA和ROAS结合评估，三个指标共同构成UA效果的完整判断依据。

**误区二：ROAS超过100%就可以无限放量**

某个渠道在小预算下实现了D30 ROAS 110%，并不意味着预算扩大10倍后效果等比例复制。随着出价提高，广告系统会触及质量更低的受众群体，CPI上升而ROAS下降——这一现象称为"规模递减效应"（Diminishing Returns）。UA团队需要持续监控放量过程中的指标变化，通常预算翻倍后ROAS下降10–20%是可接受的范围。

**误区三：归因数据完全可信**

iOS 14.5发布后，Apple推出的ATT（App Tracking Transparency）框架大幅限制了IDFA的收集，导致移动归因的信号丢失率高达60–80%。这意味着UA团队看到的渠道数据存在系统性低估，需要结合MMM（媒体组合模型）和增量测试（Incrementality Test）进行交叉验证，而非完全依赖归因平台的报告数据。

## 知识关联

**与定价策略的关系**：定价策略决定了游戏的付费点设计（如首充礼包定价9.9元还是30元），这直接影响CPA中"首次付费用户"的转化率，以及ROAS的绝对值水平。若游戏内最低付费门槛过高，会导致CPA飙升，UA成本无法收回。

**通往付费广告投放的路径**：掌握CPI/CPA/ROAS的计算逻辑和基本流程后，下一步是深入学习各主要渠道（Meta、Google、TikTok）的算法机制、出价策略（目标CPA出价 vs. 手动出价）、素材制作方法论以及大规模放量技巧——这些构成了付费广告投放的完整操作体系。UA基础是进行任何渠道投放决策的前提：没有清晰的指标定义，就无法判断一次投放是否成功。