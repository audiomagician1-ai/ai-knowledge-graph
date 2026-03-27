---
id: "pub-pr-ios-basics"
concept: "iOS发行基础"
domain: "game-publishing"
subdomain: "platform-rules"
subdomain_name: "平台规则"
difficulty: 1
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 51.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.452
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# iOS发行基础

## 概述

iOS发行基础是指通过苹果官方平台App Store Connect将游戏应用提交至App Store的完整流程，涵盖开发者账号注册、应用配置、审核规则遵守与最终上架发布。苹果App Store于2008年7月10日正式上线，目前拥有超过175个国家和地区的销售市场，是全球最重要的移动游戏发行渠道之一。与Steam的PC端发行不同，iOS发行受苹果审核团队（App Review Team）的严格把关，平均审核周期约为1至3个工作日，但首次提交往往会遇到更多合规问题需要来回修改。

iOS游戏发行对开发者的商业影响极为直接：苹果对所有应用内购买（In-App Purchase）征收30%的平台分成（年收入不超过100万美元的小型开发者可享15%的优惠税率，即App Store小型企业计划）。这一分成结构与Steam的30%标准税率相同，但iOS平台要求所有付费交易必须走苹果支付系统，不允许游戏内引导用户通过第三方渠道付款。理解这一强制性规则是避免被拒审或下架的首要前提。

## 核心原理

### 开发者账号与证书体系

上架iOS游戏的第一步是注册苹果开发者账号（Apple Developer Program），年费为99美元（个人或公司均适用）；企业分发账号（Apple Developer Enterprise Program）年费为299美元，但该账号不能用于App Store公开发行。注册后，开发者需要在苹果开发者后台生成以下关键证书和配置文件：**Distribution Certificate（发行证书）**、**App ID（应用标识符）**、以及**Provisioning Profile（配置描述文件）**。这三者共同构成Xcode打包签名的基础，缺少任何一项都无法生成可提交的IPA文件。Bundle ID一旦在App Store Connect中与游戏关联并发布，就无法更改，因此命名时需按照反向域名格式（如`com.studio.gamename`）仔细规划。

### App Store Connect配置要点

App Store Connect是管理iOS应用上架信息的核心后台，网址为`appstoreconnect.apple.com`。在创建游戏条目时，需要填写以下关键信息：

- **应用名称**：最多30个字符（注意：App Store上的显示名称受此限制，而Xcode工程内的Display Name可以更长但不影响商店显示）
- **副标题**：最多30个字符，用于提升搜索可见性
- **关键词**：最多100个字符，不同关键词用英文逗号分隔
- **截图规格**：iPhone 6.7英寸屏（如iPhone 15 Pro Max）截图为必需项，尺寸为1290×2796像素；iPad Pro 12.9英寸截图也建议提供以覆盖平板用户
- **年龄分级**：通过问卷自动生成，游戏中涉及暴力、博彩或成人内容会影响分级结果，进而影响可见受众范围
- **隐私政策URL**：2018年后苹果强制要求所有应用提供

### 审核指南的核心规则（App Store Review Guidelines）

苹果审核指南（当前版本持续在`developer.apple.com/app-store/review/guidelines/`更新）将规则分为五大类：安全、性能、商业、设计与法律。游戏开发者最常触发的拒审条款包括：

- **条款2.1（App Completeness）**：提交的构建版本不能含有占位内容、测试按钮或明显未完成的功能
- **条款3.1.1（In-App Purchase）**：游戏内所有虚拟物品、道具、去广告等付费功能必须使用苹果IAP系统，违反此条款会导致直接拒审
- **条款4.2（Minimum Functionality）**：游戏必须提供足够的原创内容，简单的HTML5套壳应用通常会被拒绝
- **条款5.1.1（Privacy - Data Collection and Storage）**：自iOS 14.5起，应用访问IDFA（广告标识符）前必须通过ATT框架弹出用户授权弹窗（即`AppTrackingTransparency`框架），否则直接被拒

### 构建版本提交流程

使用Xcode完成打包后，通过Xcode的Organizer或命令行工具`xcrun altool`（已被`xcrun notarytool`替代，适用于macOS端）将IPA上传至App Store Connect。上传后构建版本需等待苹果处理（通常15分钟至1小时），之后才能在App Store Connect中将其关联至某个版本条目并提交审核。提交审核时可选择**手动发布**或**审核通过后自动发布**，手动发布允许开发者控制上线时间窗口（自审核通过后最多保留30天，超过则需重新提交）。

## 实际应用

一款独立手游首次上架的典型时间线如下：开发者提前2周准备商店截图与宣传视频，提前1周完成App Store Connect的元数据填写与构建版本上传，随后进入等待审核阶段（约1至3天），审核通过后选择在周四发布（苹果商店全球更新通常在周四进行，利于获得编辑推荐曝光）。若游戏含有抽卡或随机礼包机制，根据苹果2017年12月更新的审核条款（条款3.1.1(b)），必须在游戏内或商店页面明确披露每种道具的掉落概率，否则将触发拒审。

对于已在Steam发行过游戏的开发者，移植至iOS时还需特别注意：Steam的成就系统、好友列表、Steam云存档等功能在iOS版本中均不可用，需替换为苹果原生的Game Center（成就、排行榜）或iCloud存档方案，否则涉及Steam SDK的残留代码可能影响应用稳定性并触发条款2.1。

## 常见误区

**误区一：认为TestFlight内测通过就等于审核通过。**
TestFlight的外部测试（External Testing，最多支持10000名测试者）确实需要苹果进行Beta审核，但Beta审核的标准与正式版审核不完全相同，尤其是IAP合规性和隐私权限声明在Beta阶段可能被跳过检查。许多开发者因此误以为正式版提交也会顺利通过，实际上正式审核会更严格地检查这些细节。

**误区二：关键词字段可以塞入竞品名称以蹭流量。**
苹果审核指南条款2.3.7明确禁止在元数据中包含其他应用的名称或品牌词。此类操作不仅会导致拒审，情节严重时可能触发开发者账号警告乃至封禁，且苹果有权在无事先通知的情况下下架违规应用。

**误区三：游戏一旦上架便不需要再维护合规性。**
苹果会定期更新审核指南，并要求现有应用跟进。例如2023年苹果要求所有应用在提交新版本时必须填写隐私营养标签（Privacy Nutrition Labels），描述应用收集的数据类型；未来若再次提交更新版本但隐私标签信息不准确，同样会被拒审。

## 知识关联

在学习iOS发行基础之前，了解Steam发行基础有助于建立"平台审核"与"版本管理"的基本概念框架——Steam的Steamworks后台与App Store Connect在构建版本管理逻辑上有相似之处，但苹果的强制IAP规则和证书签名体系是Steam所没有的，需要单独建立认知。完成iOS发行基础的学习后，Android发行基础是自然的下一步：Google Play Console与App Store Connect在元数据结构上有诸多相似字段，但Android平台允许侧载APK、支持第三方支付（部分地区和条件下），审核周期也与苹果不同，形成鲜明对比，两者对照学习有助于建立完整的移动平台发行认知。