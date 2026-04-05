---
id: "pub-pr-iap-rules"
concept: "内购规则"
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
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 内购规则

## 概述

内购规则（In-App Purchase Rules）是苹果App Store、Google Play、Steam、PlayStation Store、Xbox Marketplace等各大平台强制要求游戏开发者遵守的内置购买实现规范。这套规范涵盖支付接口调用方式、虚拟货币定价梯度、退款处理政策以及未成年人消费保护机制，违规轻则下架产品，重则永久封禁开发者账号。

从历史节点来看，苹果在2008年随iOS 2.0推出IAP（In-App Purchase）API，最初仅允许付费应用使用；2009年扩展至免费应用后，手游内购经济模式才真正爆发。Google Play的内购体系晚于苹果约两年建立，并在2022年9月的反垄断监管压力下，被迫允许部分市场引入第三方支付选项。Epic诉苹果案（2021年）直接推动了各国监管机构对"强制使用平台支付系统"的审查，导致韩国在2021年8月通过全球首部反"应用内付款强制"法律，要求平台开放第三方支付。

对游戏发行商而言，内购规则直接影响收入分成比例——苹果和谷歌标准抽佣均为30%，但年收入低于100万美元的开发者可适用15%的小型开发者计划（Apple Small Business Program，2020年起）。精确理解各平台差异化规则，决定了游戏能否在多平台同价发售，以及虚拟货币体系能否合法运营。

---

## 核心原理

### 强制使用平台支付系统

苹果App Store规则2.4.1条款明确规定：所有数字商品和服务的购买必须通过Apple IAP完成，禁止在应用内引导用户前往外部网站付款（即"反引流条款"）。违反此规则是导致游戏被下架的最常见原因之一。Google Play同样有类似的Payments Policy，但2022年起允许开发者在特定国家提供备选支付方式，且备选方式的手续费折扣仅为4个百分点（即从30%降至26%），实际收益有限。

主机平台（Sony PlayStation、Microsoft Xbox、Nintendo eShop）的内购规则则更为封闭：所有数字内容必须通过官方商店购买，没有任何例外。主机游戏的DLC和虚拟货币包必须在平台商店单独上架SKU，不能绕过商店通过第三方网站销售激活码（Nintendo在2020年明确禁止灰色市场激活码流通）。

### 虚拟货币的二层结构规范

多数平台要求游戏使用"非一比一兑换"的虚拟货币（如钻石、金币），以模糊真实消费金额感知，但苹果和谷歌均要求虚拟货币的具体面值和兑换率在购买界面清晰展示。苹果规则3.1.1要求：所有可消耗型（Consumable）IAP商品必须明确标注用途，不得以"神秘包裹"等模糊描述销售。

平台对虚拟货币的定价梯度有固定档位限制。苹果提供从0.99美元到999.99美元共约100个标准定价档位（Price Tier），2023年苹果将全球定价架构更新为700+个价格点，允许更精细的区域差异化定价。开发者不能自由填写任意金额，必须从平台预设的价格矩阵中选择。Google Play的价格下限为0.10美元（部分国家为当地等值货币最低限额），上限为400美元。

### 反欺诈与退款机制

苹果使用服务器端收据验证（Receipt Validation）机制：游戏客户端收到IAP凭证后，必须将receipt data发送至苹果验证服务器（`https://buy.itunes.apple.com/verifyReceipt`），服务器返回JSON格式的交易状态码，status为0表示合法购买。绕过此验证流程直接解锁内容，将导致应用因"欺诈性解锁"被下架。

Google Play采用Google Play Billing Library的购买令牌（Purchase Token）+ 服务端订单验证双重机制，开发者必须在服务端通过Google Play Developer API调用`purchases.products.get`或`purchases.subscriptions.get`接口验证购买真实性，验证响应中`purchaseState`字段为0才代表已完成支付。

退款规则方面，苹果允许用户在购买后90天内通过`reportaproblem.apple.com`申请退款，退款批准后开发者账期结算时会直接扣除对应金额。Google Play的标准退款窗口为48小时内可无理由退款。针对被滥用的退款漏洞（即购买后立即申请退款获取内容），两平台均有自动检测算法，高退款率账号会触发风险审查。

---

## 实际应用

**订阅型游戏Pass的合规实现**：Xbox Game Pass Ultimate在移动端iOS版本因苹果内购规则限制，长期无法提供订阅购买入口，微软选择将iOS版Xbox应用设计为纯内容浏览器，用户必须通过浏览器前往Xbox官网购买会员——这是内购规则迫使开发者改变商业模式的典型案例。2021年苹果与开发者达成协议，允许"读者类App"在应用外链接购买页，但游戏类App不在此豁免范围内。

**虚拟货币的区域合规**：某款全球发行的手游在中国大陆版本需将"钻石"定价梯度按人民币标准档位（6元、30元、68元、128元、328元、648元）重新配置，同时中国区要求游戏内虚拟货币标注"本虚拟货币不可兑换为法定货币"声明，并在每次购买确认界面以弹窗形式显示。

**主机DLC的SKU拆分**：PlayStation平台要求每个DLC内容包作为独立SKU上架，且季票（Season Pass）必须包含明确的内容列表，不能以"未来内容"为由出售空白季票——这一规则在2022年明确收紧，直接影响了依赖"战斗通行证"模式的发行商在PS Store的上架策略。

---

## 常见误区

**误区一：虚拟货币赠送不受内购规则约束**
部分开发者认为免费赠送的虚拟货币（如登录奖励钻石）不需要走IAP流程，因此在应用内设计"充值赠送"活动时，将赠送部分单独结算。实际上苹果规则明确：只要用户支付行为发生，赠送部分也必须在同一IAP交易内完成，不能拆分为"购买100钻石+独立赠送50钻石"两个流程，否则视为规避平台分成的违规行为。

**误区二：安卓版可以通过APK侧载绕过Google Play内购**
即使用户通过侧载方式安装APK，游戏若在Google Play上架，仍须使用Google Play Billing Library处理付款。若检测到游戏在Play Store版本中使用了第三方支付SDK（如Stripe直连），Google有权将该应用从Play Store下架，且此类违规记录会影响开发者账号信誉评分。

**误区三：退款只是财务问题，不影响内容状态**
当用户退款成功后，平台会通过服务端通知（苹果的`REFUND`类型App Store Server Notification，Google的`voided-purchases` API）告知开发者服务器。若游戏服务端未接入这些退款通知接口，用户在退款后仍保留已解锁内容，会导致游戏内物品状态与平台支付状态不一致，积累大量此类案例后将触发平台欺诈风险审查。

---

## 知识关联

本主题的前置概念**主机送审**中涉及的平台内容政策（如评级、内容分级），与内购规则存在直接交叉：内购物品的内容描述本身也需通过送审，且部分平台（如Nintendo）对恐怖或成人向DLC的内购上架有额外审核流程。**抽卡/开箱规制**所讨论的概率披露要求，在具体执行层面依赖本文所述的IAP界面展示规范——各平台均要求概率公示信息必须在IAP购买弹窗或购买前跳转页面可见，不能仅在游戏内菜单深处展示。

后续学习的**云游戏平台**概念将面临内购规则的延伸挑战：当游戏以云串流形式运行在iOS设备上时（如Xbox Cloud Gaming、NVIDIA GeForce NOW），苹果规定云游戏应用内的每款游戏必须单独在App Store上架并接受审核，其内购行为同样须遵守IAP规范，这使得云游戏平台的商业模式设计需要从内购规则出发重新规划内容分发架构。