---
id: "pub-pr-update-policy"
concept: "更新政策"
domain: "game-publishing"
subdomain: "platform-rules"
subdomain_name: "平台规则"
difficulty: 3
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.1
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

# 更新政策

## 概述

更新政策是指游戏发行商在向各平台提交游戏补丁或版本更新时，所必须遵守的提交流程、审核周期及热更新技术限制的规则体系。不同平台的更新政策差异显著：苹果App Store的补丁审核周期通常为1至3个工作日（紧急安全修复可申请加急通道，最快24小时内完成），而Google Play的审核平均在数小时至2个工作日之间完成。Steam平台则几乎不设置内容审核延迟，开发者可通过Steamworks的BuildID机制在数分钟内完成版本切换。

更新政策的概念随着移动游戏平台的兴起在2008至2012年间逐渐成型。苹果在App Store上线初期仅允许开发者提交全量更新包，审核流程长达14天，这严重影响了开发者快速修复线上Bug的能力。随后各平台相继引入了差分包更新（Delta Update）机制，才使补丁体积和审核周期大幅压缩。

掌握各平台的更新政策对游戏发行商而言具有直接的经济意义。一款日活百万的手游若遭遇严重崩溃Bug，在iOS平台等待审核期间每天可能损失数十万元收入。理解平台对热更新脚本语言的限制范围，能帮助开发者在不违反规则的前提下最大化运营灵活性。

---

## 核心原理

### 各平台审核机制与补丁提交流程

**iOS / App Store** 要求所有二进制代码变更必须通过AppReview审核，开发者须在App Store Connect中提交新版本，并在"What's New"字段填写变更说明。苹果明确禁止在审核后动态下载并执行可执行代码（即违反第3.3.2条款），因此原生代码补丁必须走完整审核流程。

**Google Play** 采用基于Android App Bundle（AAB）格式的差分更新，Play Asset Delivery机制可将资源包拆分为install-time、fast-follow和on-demand三种交付方式，允许游戏在不重新提交审核的情况下异步下载资源模块。Google Play的内容审核相对宽松，但违规应用仍会面临自动机器审查标记。

**主机平台（PlayStation/Xbox/Nintendo Switch）** 的补丁提交流程最为严格。PS5补丁包须通过Sony的DevNet提交系统，审核周期约为5至10个工作日，且补丁包必须包含完整的QA测试报告（TRC/TCR合规性报告）。Microsoft的Xbox平台要求补丁通过XDP（Xbox Developer Portal）提交，同样需通过XR规范审查。

### 热更新的平台限制规则

热更新（Hotfix/Live Update）是指在不经过应用商店审核的情况下，于运行时替换游戏内容或逻辑的技术手段。各平台对热更新的限制核心在于"是否执行下载的代码"：

- **允许热更新的内容类型**：文本配置表（JSON/CSV）、图片与音频资源、关卡数据、UI布局文件（如Unity的AssetBundle中的非代码资产）。
- **禁止热更新的内容类型**：iOS平台明确禁止通过Lua、JavaScript等脚本解释器动态执行从服务端下载的逻辑代码。这一规则在2017年苹果开始集中下架使用JSPatch框架的App时得到了强力执行，大量国内手游因违规使用JSPatch而被迫下架整改。

Unity的Addressables系统和Cocos的热更新方案本质上都依赖"资源热更新+预编译脚本"的组合，在iOS上将Lua/TypeScript等脚本预先打包进审核版本而非运行时下载，以此绕过苹果的代码执行限制。

### 紧急更新通道与版本回滚机制

当游戏出现严重安全漏洞或支付系统崩溃时，开发者可向Apple申请"Expedited Review"（加急审核）。苹果对加急审核的受理条件有明确规定：必须是功能性崩溃或安全漏洞，而非新功能添加。每个Apple Developer账号每年可申请的加急审核次数无硬性上限，但滥用会导致申请被拒。

Google Play Staged Rollout（分阶段发布）功能允许开发者将新版本按1%、5%、20%等比例逐步推送给用户，若发现问题可立即暂停发布并回滚至上一版本。Steam的Beta分支机制（Branch/Depot）同样支持多版本并行，开发者可通过BuildID即时切换用户接收的版本。

---

## 实际应用

**案例一：《原神》的iOS热更新架构**  
米哈游在《原神》iOS版中采用了"Lua预置+资源AssetBundle"的热更新策略。所有Lua脚本均在版本审核时作为资源包的一部分提交，服务端仅下发配置数据（如活动开关、掉率参数），而非可执行脚本，从而在不违反App Store第3.3.2条款的前提下实现了活动内容的快速上线。

**案例二：主机DLC与补丁的捆绑提交**  
许多主机游戏开发商为降低审核成本，选择将Bug修复补丁与内容DLC合并为一个更新包同时提交。例如某款RPG游戏将战斗平衡补丁（v1.02）与新角色DLC合并为v1.03提交，避免了两次单独审核所需的10至20个工作日等待时间。

**案例三：Android平台的OBB扩展包策略**  
超过150MB的Android游戏可使用OBB（Opaque Binary Blob）扩展包机制，将主游戏逻辑（APK/AAB）与资源包分离。OBB文件的更新不需要经过Play Store审核，开发者可以在不触发应用商店审核流程的情况下更新游戏美术和音频资源。

---

## 常见误区

**误区一：认为所有平台的热更新限制相同**  
许多开发者错误地将Android平台的热更新自由度移植到iOS开发思路中。Android允许通过DexClassLoader动态加载DEX字节码（在一定条件下），但iOS的沙盒机制与Apple审查规则完全不允许此类操作。将同一套热更新框架直接应用于iOS往往导致应用被下架。

**误区二：认为资源热更新在所有平台上无限制**  
部分开发者认为"只要不是代码就可以随意热更新"。实际上，Nintendo Switch平台要求所有运行时下载的内容均须经过Nintendo的内容审查，即便是图片或音频文件也不例外。此外，苹果在App Review指南第4.2.3条中规定，若热更新内容从根本上改变了App的核心功能或用途，同样视为违规。

**误区三：认为加急审核是解决线上Bug的可靠方案**  
依赖Apple加急审核通道处理紧急Bug是高风险策略，因为即便申请了加急审核，苹果仍保留拒绝或要求修改的权利，实际处理时间可能超过48小时。成熟的发行团队会提前在架构层面设计服务端配置开关（Feature Flag），通过关闭问题功能而非补丁提交来应对突发状况。

---

## 知识关联

**前置概念：平台特性利用**  
理解各平台的技术架构特性（如Android的ClassLoader机制、iOS的代码签名体系）是制定合规热更新方案的技术基础。对平台差分更新算法（如bsdiff算法，补丁大小 = f(旧版本二进制, 新版本二进制)）的了解有助于开发者优化补丁包体积，加快审核通过率。

**后续概念：跨平台发行**  
多平台同步发行时，更新政策的差异会导致各平台版本出现时间错位。iOS补丁可能比Android版本晚3至5天到达玩家，这要求跨平台发行策略中必须设计版本兼容层，确保处于不同版本的玩家能够正常进行联机匹配，同时服务端API需要维护多版本并行支持能力。