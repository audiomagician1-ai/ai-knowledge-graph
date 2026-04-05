---
id: "pub-pr-android-basics"
concept: "Android发行基础"
domain: "game-publishing"
subdomain: "platform-rules"
subdomain_name: "平台规则"
difficulty: 1
is_milestone: true
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
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


# Android发行基础

## 概述

Android发行基础是指通过Google Play商店发布游戏应用所需掌握的Console配置、政策合规与上架流程体系。与iOS的App Store Connect相比，Google Play Console的开发者账号注册一次性收费25美元（而Apple Developer Program每年收费99美元），且审核周期通常为数小时至3个工作日，明显短于App Store的平均1-3天。

Google Play自2008年10月以"Android Market"名称正式上线，2012年3月更名为Google Play，目前覆盖全球超过190个国家和地区。对于游戏开发者而言，理解Android发行流程意味着能够触达全球约30亿台活跃Android设备，这是任何移动游戏发行策略中不可忽视的市场规模。

Android采用APK（Android Package Kit）或AAB（Android App Bundle）两种上架格式，其中Google自2021年8月起强制要求新应用必须以AAB格式提交，AAB相较于APK可将安装包体积平均减少15%，这直接影响用户的下载转化率与游戏的市场表现。

---

## 核心原理

### Google Play Console账号配置

注册Google Play Console需要一个Google账号，缴纳25美元一次性费用后，开发者需完成以下必填信息：开发者名称（显示在商店页面）、联系邮箱、隐私政策URL、物理地址（用于税务合规）。

账号类型分为个人（Individual）和组织（Organization）两种。组织账号需填写DUNS编号（邓白氏编号），适合有团队协作需求的发行商，因为组织账号支持多成员权限管理，可细分为Admin、Release Manager、Financial Reports Viewer等不同角色。对于游戏发行，建议至少配置一名Release Manager专门负责版本上架操作。

### 应用内容分级与政策合规

Google Play要求所有应用填写内容分级问卷（IARC系统，International Age Rating Coalition），该系统依据玩家所在地区自动生成PEGI、ESRB、USK等各地区评级，无需单独向每个评级机构申请，这与iOS需要自行选择分级的方式不同。

游戏内容必须遵守Google Play的《开发者计划政策》，尤其要注意以下三点：
1. **赌博内容**：包含机率性付费道具（即"盲盒"或"扭蛋"）的游戏，在部分国家（如比利时、荷兰）需要额外的博彩许可证明，否则必须对该地区屏蔽此功能。
2. **面向儿童的内容**：若目标受众包含13岁以下儿童，应用必须符合COPPA（儿童在线隐私保护法案）要求，且不得投放个性化广告。
3. **虚假评分刷榜**：使用激励手段诱导用户留评属于违规行为，一经发现可导致应用下架乃至账号封禁。

### AAB打包与上架流程

标准的Google Play上架流程分为以下步骤：

1. **创建应用**：在Play Console中选择"创建应用"，填写默认语言、应用名称（最多50个字符）、应用类型（游戏）及免费/付费属性。注意付费属性一旦设为"免费"则**无法**改回付费，因此初期策略需谨慎决策。
2. **商店信息配置**：上传至少2张屏幕截图（最大尺寸3840×2160像素）、1张512×512像素的应用图标、1张1024×500像素的特色图片（Feature Graphic），以及可选的宣传视频（YouTube链接）。
3. **版本管理**：Play Console提供四种发布轨道——内部测试（Internal，最多100位测试者）、封闭测试（Closed Alpha）、开放测试（Open Beta）、正式发布（Production）。游戏首次上架建议先经过封闭测试轨道收集崩溃数据，再推进至正式发布。
4. **分阶段发布**：正式轨道支持按百分比灰度发布，例如先向5%的用户推送新版本，确认稳定性后再扩展至100%，这是Android独有的风险控制机制，iOS不提供等效的原生灰度功能。

---

## 实际应用

**游戏本地化上架案例**：某休闲游戏团队在将游戏提交Google Play时，因商店描述中包含"FREE"字样但游戏内含付费项目，触发了Google的"虚假宣传"政策警告。修改方案是将描述改为"Free to Play with in-app purchases"，并在应用详情页勾选"包含应用内购买项目"，同时确保应用的AndroidManifest.xml中包含`com.android.vending.BILLING`权限声明。

**目标API级别合规**：Google Play要求2024年8月后新上架的游戏必须目标API级别（targetSdkVersion）≥34（对应Android 14），这意味着游戏引擎（如Unity 2022 LTS或Unreal Engine 5.3+）必须选用支持该API级别的版本进行构建，否则提交时会收到政策不合规拒绝通知。

---

## 常见误区

**误区一：APK与AAB可以互换使用**
部分开发者认为现有APK打包流程沿用即可，但自2021年8月起，Google Play强制新应用必须以AAB格式提交，APK格式仅在Play内部测试轨道中仍被允许。AAB由Google的服务器动态生成针对不同设备的优化APK，开发者本地无法直接运行AAB文件，调试时仍需使用APK，这是两种格式在工作流中的根本区别。

**误区二：通过内容分级问卷即可合规发行含抽奖内容的游戏**
IARC分级系统只解决年龄评级问题，不等同于博彩合规审查。包含随机付费道具的游戏若要在荷兰上架，需要向荷兰博彩管理局（Kansspelautoriteit）提交合规证明，否则必须在Play Console的"分发国家/地区"设置中将荷兰排除，这与单纯填写内容问卷是完全不同的合规维度。

**误区三：Google Play审核比App Store宽松因此无需提前准备**
虽然Google Play的平均审核时间较短，但Google采用自动化+人工审核结合的机制，且近年政策收紧后，涉及博彩、儿童内容、VPN工具的应用被拒率大幅提升。一旦账号因违规被终止，该Google账号名下所有应用将全部下架，且25美元注册费不予退还，恢复难度极高。

---

## 知识关联

在学习Android发行基础之前，已有的**iOS发行基础**知识帮助建立了商店上架的整体认知框架，例如商店元数据配置、应用内购买声明等通用概念。但Android的AAB格式要求、灰度发布机制、Play Console权限分级以及IARC分级系统，是区别于App Store Connect的独有知识点，需要单独记忆。

完成Android发行基础学习后，下一个关键主题是**平台分成模式**。Google Play的标准抽成比例为30%，但2021年起对年收入低于100万美元的开发者降至15%，这与Apple同期推出的"App Store Small Business Program"策略高度相似。了解Android的发行流程后，才能进一步分析Google Play分成规则对游戏定价策略、IAP设计与收益规划的具体影响。