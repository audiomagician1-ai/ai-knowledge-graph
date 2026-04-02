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
updated_at: 2026-04-01
---



# iOS发行基础

## 概述

iOS发行是指将游戏或应用提交至苹果公司的App Store进行审核并公开销售或免费分发的完整流程。开发者必须持有有效的**Apple Developer Program**会员资格（年费99美元，企业账号299美元），通过App Store Connect平台完成所有配置、提交和管理操作。

苹果的App Store于2008年7月10日正式上线，是全球第一个移动应用商店。经过十余年演进，其审核标准日趋严格，目前官方公布的《App Store审核指南》（App Store Review Guidelines）包含5大类别：安全性、性能、商业行为、设计和法律合规，每项均有细化的具体条款。对于游戏发行商而言，熟悉这份文件是顺利上架的前提。

iOS平台的特殊性在于苹果对应用生态的高度管控：所有.ipa安装包只能通过官方渠道安装（测试阶段使用TestFlight），内购系统必须使用苹果的IAP（In-App Purchase），且苹果从中抽取**30%**的分成（首年后或年收入低于100万美元的小型开发者享受**15%**优惠税率）。这与Steam的30%分成结构类似，但iOS的强制性远高于Steam——开发者无法绕过IAP系统。

---

## 核心原理

### App Store Connect配置

App Store Connect（原iTunes Connect，2018年更名）是苹果官方的应用管理后台，网址为appstoreconnect.apple.com。上架游戏前，开发者需要在此创建**App记录**，填写以下关键信息：

- **Bundle ID**：格式为反向域名（如`com.studio.gamename`），必须在Apple Developer Portal中预先注册，与Xcode工程中的Bundle Identifier完全一致，上架后**不可更改**。
- **SKU**：自定义的唯一标识符，仅内部使用，不对用户显示。
- **主要语言**：决定App Store页面的默认展示语言。
- **版本号**：遵循语义化版本规范（如1.0.0），每次提交新构建包时需递增CFBundleShortVersionString。

截图要求极为严格：iPhone 6.7英寸（iPhone 14 Pro Max等）和iPad 12.9英寸的截图为**必填项**，分辨率分别为1290×2796像素和2048×2732像素，最多上传10张。预览视频时长限制为15至30秒，格式须为M4V、MP4或MOV。

### Xcode与构建包提交

开发者使用**Xcode**（最新稳定版为Xcode 15，截至2024年）将游戏打包为.ipa文件并上传。提交流程如下：

1. 在Xcode中选择**Any iOS Device**作为目标设备，执行Archive操作生成归档文件。
2. 通过**Xcode Organizer**或命令行工具`altool`（已被`notarytool`逐步替代）上传至App Store Connect。
3. 上传成功后，构建包在后台处理期间状态显示为"正在处理"，通常需要**10至30分钟**。
4. 处理完成后，在App Store Connect中将该构建包关联至对应版本并提交审核。

Unity、Unreal Engine等引擎均支持导出Xcode工程，再由Xcode完成最终打包，因此引擎选择不影响提交流程本身。

### 审核流程与《审核指南》关键条款

苹果审核团队全年无休，平均审核时间为**24至48小时**，约90%的应用在3天内完成审核（苹果官方数据）。被拒绝后开发者可在App Store Connect中查看具体拒绝原因，修改后重新提交。

对游戏发行商影响最大的审核条款包括：

- **条款4.1（复制品）**：游戏玩法或美术风格被认定为抄袭其他应用将直接拒绝，尤其针对仿制热门游戏的"克隆产品"。
- **条款4.2（最低功能要求）**：简单地将网页包装为应用、或功能严重不完整的游戏不予通过。
- **条款3.1.1（应用内购）**：所有数字内容、虚拟货币、订阅均必须通过苹果IAP实现，不可引导用户至外部网页购买（2021年反垄断案后有限度开放外链声明，但仍禁止直接跳转购买页面）。
- **条款1.4.3（赌博）**：真实货币赌博类游戏须持有目标市场的合法赌博许可证，且仅可在法律允许的地区上架。
- **条款5.1.1（数据隐私）**：要求提供隐私政策URL，并在App Store Connect中填写**隐私营养标签**（Privacy Nutrition Label），列明应用收集的数据类型及用途。

### 年龄分级与内容描述

iOS游戏必须在App Store Connect中完成**年龄分级问卷**，系统根据回答自动生成4+、9+、12+或17+的分级结果。问卷涉及卡通暴力、写实暴力、性暗示内容、恐怖元素、赌博、烟草、酒精等12个维度，每项提供"无/轻微/频繁"三档选择。**17+的游戏不会出现在屏幕时间儿童限制下**，但仍可正常搜索和购买。

---

## 实际应用

**案例：Unity手游上架全流程**

某独立开发团队使用Unity 2022制作了一款休闲益智游戏，上架流程如下：

1. 在Apple Developer Portal注册Bundle ID `com.indiedev.puzzlegame`，创建**Distribution证书**和**App Store Provisioning Profile**。
2. 在App Store Connect创建App记录，填写游戏名称、副标题（最长30字符）、描述（最长4000字符）、关键词（最长100字符，用逗号分隔）。
3. Unity导出Xcode工程，在Xcode中配置Signing & Capabilities，使用Distribution证书Archive打包并上传。
4. 配置IAP商品：在App Store Connect的"功能→应用内购买"中创建消耗型产品（如"100颗宝石"），填写产品ID、价格档位（苹果提供固定价格档位，如档位1对应0.99美元/6元人民币）。
5. 使用**TestFlight**邀请最多10000名外部测试人员进行Beta测试，TestFlight构建包同样须经过苹果的简化审核（通常**24小时**内完成）。
6. 提交正式版本审核，附上**审核备注**（Review Notes），说明游戏的测试账号和特殊功能入口，避免因审核员无法进入核心玩法而被拒。

**分区发行与价格策略**

iOS支持按地区（175个国家和地区）独立设置价格和上架状态，适合先在少数市场进行软发布（Soft Launch）再全球铺开的策略。价格须从苹果提供的**价格档位表**（约100个档位）中选择，不支持自定义价格。

---

## 常见误区

**误区一：以为审核时间固定，不预留缓冲期**

许多新手开发者假设审核一定在24小时内完成，将上线时间与某个营销节点（如游戏展会、节假日）精确对齐。实际上，苹果在重大节假日前后（如圣诞节、中国春节）审核量激增，时间可能延长至**5至7天**，且苹果不接受"紧急上线"的加速请求（仅在极少数情况下可通过开发者支持申请加急，不保证成功）。建议在目标上线日至少**提前2周**提交审核。

**误区二：内购产品可以自行定价**

开发者无法像Steam或Google Play那样输入任意价格数字。苹果的价格档位体系意味着人民币端的价格与美元端并不总是按汇率精确对应，例如同一档位在美国定价0.99美元，在中国可能定价6元。苹果会定期根据汇率调整各地区价格档位，开发者须在App Store Connect中手动确认调整或设置自动跟随。

**误区三：上架后可以随时修改App信息**

游戏名称（App Name，最长30字符）、Bundle ID、主类别一旦设定，修改均受到限制：Bundle ID**完全不可更改**，App Name的修改须随版本更新一起提交审核，不能在不发版的情况下独立修改（与Google Play允许随时修改商店页面不同）。

---

## 知识关联

学习iOS发行基础之前，已掌握的**Steam发行基础**提供了发行流程的通用认知框架（如构建提交、版本管理、分成比例概念），但iOS的强制IAP、证书体系和封闭审核机制与Steam的开放式发行存在本质差异，不可直接套用Steam的经验。

在掌握iOS发行基础后，下一个学习目标是**Android发行基础**（Google Play平台）。两者的对比学习价值极高：Android使用.aab（Android App Bundle）而非.ipa，Google Play的审核周期通常比App Store更短但审核标准不同，IAP分成比例同为30%但Google的政策在2021年后略有松动。掌握两个平台的差异，是完整移动游戏发行能力的基本要求。