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


# 更新政策

## 概述

更新政策是指各大游戏发行平台（如Apple App Store、Google Play、Steam、PlayStation Network等）对游戏开发者提交补丁、版本更新及热更新操作所制定的具体规则与审核机制。每个平台的更新流程存在显著差异：Apple App Store平均审核周期为1至3个工作日，而Google Play的自动化审核在大多数情况下可在数小时内完成，Steam的审核则通常在1至5个工作日内结束，主机平台（如PlayStation、Xbox）的补丁审核则往往需要5至14个工作日。

更新政策的形成源于各平台的商业模式与安全考量。苹果公司自2010年iOS App Store建立起严格的二进制审核机制，主要目的是防止恶意代码通过动态加载绕过审核，这直接催生了移动端热更新技术的受限环境。对游戏发行商而言，理解各平台更新政策的差异是控制运营节奏、快速响应线上BUG以及规划版本发布日历的重要前提。

## 核心原理

### 补丁提交与审核流程的平台差异

各平台对"补丁"的定义和处理方式不尽相同。**Apple App Store**要求每次更新必须提交完整的IPA二进制包，不允许通过动态解释器（如Lua虚拟机独立下发可执行脚本）修改应用逻辑，违反《App Store审核指南》第2.5.2条将面临下架处罚。**Google Play**对Android平台相对宽松，允许使用AAB（Android App Bundle）格式提交，并支持通过Google Play Asset Delivery分批下发资源，但仍禁止从外部服务器动态下载并执行原生代码。

**Steam平台**采用Depot机制管理游戏版本，开发者可在Steamworks后台上传新Depot内容并指定分支（Branch），普通玩家分支（default branch）更新发布前需通过简单的内容审核，而Beta分支可绕过部分审核直接推送给选择加入的玩家。这一机制使Steam成为PC端快速迭代测试的有利平台。

**主机平台（PS5/Xbox Series）**要求提交TCR（Technical Certification Requirements）和TRC（Technical Requirements Checklist）合规审核，索尼的补丁提交需经过QA验证期，最短也需5个工作日，紧急安全补丁可申请"Emergency Submission"通道，但批准率不高且需提供详细故障说明文档。

### 热更新的技术边界与合规路径

热更新（Hot Update / Over-the-Air Update）在不同平台的允许范围存在本质区别。在iOS平台，**仅允许更新纯资源内容**（图片、音频、JSON数据配置、UI布局文件等），严禁通过下载新的Lua字节码或JavaScript代码来改变游戏逻辑。合规的热更新框架（如Unity的Addressables配合CDN方案）必须确保所有代码逻辑在提交审核时已固化在二进制包内。

Android平台允许更宽泛的热更新操作，包括下发Lua脚本、JavaScript逻辑文件等解释型语言代码，但仍不得热更新涉及应用权限变更或Native层（.so文件）的内容。行业中常用的热更新框架如**Cocos2d-x + JSB**或**Unity + ILRuntime**，均在iOS端做了严格的代码加载限制以符合苹果政策。

**热更新包体积限制**也是政策的重要组成部分。部分平台规定单次CDN热更新资源包超过特定阈值（如50MB）时，必须引导用户通过官方商店更新，而非静默下载，以保证用户知情权。

### 版本号管理与强制更新策略

各平台对版本号（Version Code / Build Number）的递增规则有强制要求。Apple App Store要求CFBundleShortVersionString必须严格递增，不允许提交相同版本号的更新包；Google Play同样要求versionCode（整数）每次提交必须大于前一版本。强制更新（Force Update）策略需配合各平台的最低版本支持机制（如Google Play的In-App Update API），开发者可设定当用户版本低于某个versionCode时弹出强制更新弹窗，但此逻辑本身也需通过审核方可生效。

## 实际应用

**案例一：移动端紧急BUG修复**
某款RPG手游上线后发现充值系统存在严重逻辑漏洞，开发团队需要在24小时内修复。在Android端，由于热更新不受限于代码逻辑，可通过下发Lua热更新包在1至2小时内完成线上修复；iOS端则必须立即提交新版本至App Store，同时通过配置参数（JSON远程配置）临时禁用充值入口，待2至3天审核通过后正式修复，此时远程配置作为合规的"功能开关"发挥了关键作用。

**案例二：Steam Early Access版本快速迭代**
独立游戏工作室通常利用Steam的Beta分支机制，每周向选择加入Beta测试的玩家推送实验性版本，无需经过完整内容审核，收集玩家反馈后再将稳定版本合并至default分支。这种分支管理策略在《Hades》开发期间被Supergiant Games广泛采用，实现了长达两年的Early Access快速迭代。

**案例三：主机DLC更新规划**
主机游戏DLC补丁因需经过14天左右的认证流程，发行商通常将版本提交节点安排在预计发布日的3周前，并在Steamworks或PSN后台设定"定时上线"时间戳，以确保多平台同步发布。

## 常见误区

**误区一：认为Android平台热更新完全无限制**
许多开发者误以为Android允许任意热更新，但Google Play政策自2021年起明确禁止通过热更新分发执行原生代码（.so动态库），同时规定热更新内容不得用于绕过Google Play的付费系统。违规可能导致应用在无警告的情况下被下架，甚至开发者账号被封禁。

**误区二：将热更新资源包视为可绕过版本审核的捷径**
部分团队认为将大量功能内容打包成"资源"通过热更新下发可规避审核，实际上Apple的审核团队会关注应用更新前后的功能变化，若发现版本行为与审核提交时显著不同，会依据《App Store审核指南》第2.1条（App完整性）进行处理。历史上曾有多款因热更新引入完整新游戏模块而被苹果警告的案例。

**误区三：主机紧急审核通道可随意使用**
PS5和Xbox的"紧急补丁"通道并非付费加速服务，而是仅面向影响游戏可玩性的崩溃级BUG（Severity 1级别）的特殊申请流程，滥用此通道申请非紧急更新会损害与平台方的合作关系，且被拒绝后仍需回到常规审核队列重新排队。

## 知识关联

更新政策建立在**平台特性利用**的基础之上——只有深入了解各平台的技术架构（如Steam Depot系统、iOS沙箱模型、Android APK/AAB结构），才能在合规范围内最大化利用平台提供的更新机制。例如，理解iOS的二进制签名机制，才能准确判断哪些资源可以绕过审核动态下发，哪些必须随包提交。

掌握各平台更新政策后，将直接支撑**跨平台发行**的版本管理策略。多平台同时发行时，最短审核周期（Android数小时）与最长审核周期（主机约14天）之间的差异要求发行团队建立差异化的版本发布日历：主机版本必须最先提交，移动端版本可最后提交，以确保各平台在同一天同步上线，这是多平台发行计划中处理更新政策差异的核心排期逻辑。