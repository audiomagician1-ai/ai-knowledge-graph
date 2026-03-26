---
id: "certification"
concept: "平台认证"
domain: "game-engine"
subdomain: "platform-abstraction"
subdomain_name: "平台抽象"
difficulty: 2
is_milestone: false
tags: ["发行"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 平台认证

## 概述

平台认证（Platform Certification）是游戏发行商在将游戏发布到特定主机平台之前，必须通过该平台持有者官方质量审核程序的强制性流程。Sony、Microsoft和Nintendo各自维护独立且互不兼容的认证标准，分别称为TRC（Technical Requirements Checklist）、XR（Xbox Requirements）和Lotcheck。未通过认证的游戏无法在对应平台的数字商店上架，也无法进行物理介质生产授权。

认证体系起源于1990年代任天堂推出"质量保证"印章（Seal of Quality）时期。彼时Nintendo 64和Super Nintendo的Lotcheck流程主要检测游戏是否会损坏存档数据或导致硬件崩溃。随着PlayStation的兴起，Sony建立了自己的TRC体系，从PS1时代延续至今，每一代主机（PS4、PS5）都会发布更新版本的TRC文档，版本号格式如"SCE_TRC_Version_3.x"。

平台认证对游戏引擎开发者的意义在于：引擎必须内置或提供符合各平台TRC/XR/Lotcheck要求的API封装和默认行为，否则基于该引擎开发的每款游戏都需要单独处理合规问题，成本极高。Unity和Unreal Engine在各自的平台SDK集成层中均预置了大量合规辅助逻辑，正是为了降低开发者通过认证的门槛。

## 核心原理

### TRC（Sony技术要求清单）

Sony的TRC文档按功能域分组，典型类别包括：用户数据处理（Save Data）、奖杯系统（Trophy）、网络连接行为、辅助功能（Accessibility）等。PS5的TRC新增了Activity Card强制要求，即游戏必须为主要关卡或游戏模式提供可从主机UI直接跳转的Activity入口点。TRC条款被标记为"必须（Must）"或"应该（Should）"两级，其中Must条款若有任何一条不满足，游戏提交将被直接拒绝（Fail），不存在豁免机制。PS5 TRC文档在SDK发布时随附，版本随固件更新同步迭代，开发者必须针对目标发行时间对应的TRC版本进行测试。

### XR（Microsoft Xbox要求）

Microsoft的XR文档目前覆盖Xbox Series X/S和Xbox One跨代发布场景，对游戏在两代硬件上的行为一致性有明确约束。XR-004条款规定游戏不能因运行于低规格设备而在基本功能上产生差异（即不允许Xbox One版本缺少核心玩法功能）。XR-015专门约束辅助功能，要求游戏UI文本不能小于特定磅值，并需提供字幕开关选项。XR文档通过Xbox开发者门户（Partner Center）访问，与GDK（Game Development Kit）SDK版本绑定，开发者需在Partner Center中选定认证目标版本并提交构建包（Submission Package）。

### Lotcheck（Nintendo任天堂检测）

Nintendo的Lotcheck是三大平台中审核周期最长、反馈最细致的认证流程。Switch平台的Lotcheck要求游戏在睡眠模式唤醒后10秒内恢复到可操作状态（若超时则为Fail）。Lotcheck还包含物理测试阶段：对于卡带版本，Nintendo实验室会检测实际芯片数据完整性。提交Lotcheck前，开发者须完成NintendoSDK自带的Logo Check工具（NintendoSDK\Tools\LogoCheck）的全部自检通过。Lotcheck的典型审核周期为7至10个工作日，若出现Fail则重新排队，再次审核需要额外7天，这使得发行时间规划极为敏感。

### 认证提交流程

三大平台均采用"构建提交→自动化测试→人工审核→结果报告"的流程，但细节不同。Sony使用DevNet提交入口；Microsoft使用Partner Center的Ingestion API；Nintendo使用NDev Portal。提交时开发者必须附上自测报告（Self-Check Report），声明已逐条验证各平台强制条款。若提交材料不完整，平台方可在不开始审核的情况下直接拒绝接收（Administrative Reject），这不计入正式Fail次数但会浪费档期。

## 实际应用

在Unreal Engine开发PS5游戏时，引擎的OSS（Online Subsystem）PS5插件默认实现了Trophy解锁接口，符合TRC中关于奖杯触发时机的约束（TRC要求奖杯不能在玩家明确完成条件前触发）。开发者若绕过OSS直接调用PSN SDK的奖杯API，极易因时序问题导致TRC违规。

对于Nintendo Switch开发，Unity的Switch平台层内置了对NX Logo Check要求的静态资源检测，会在构建时警告不符合Lotcheck尺寸规范的启动画面图片。这使得Unity开发者能够在提交前的本地阶段发现违规，而非等待Lotcheck失败报告。

一个典型的实际违规案例：若游戏在Xbox上未实现"快速恢复"（Quick Resume）状态的正确序列化，XR-049条款判定不合规，该功能属于Must级别，Xbox平台团队曾因此拒绝多款知名独立游戏的首次提交。

## 常见误区

**误区一：认为一次认证覆盖所有平台**
TRC、XR、Lotcheck是完全独立的认证体系，在一个平台通过认证对其他平台没有任何效力。更重要的是，同一平台的DLC或更新补丁通常也需要独立提交认证，不能沿用主游戏的认证结果。Sony明确规定，改变游戏核心玩法的补丁必须重新执行完整TRC合规验证。

**误区二：认为认证只检查崩溃和Bug**
三大平台的认证条款中包含大量与技术稳定性无关的用户体验和内容规范。例如，Nintendo Lotcheck包含对游戏内文字显示字体的规范限制（不允许使用与任天堂品牌字体混淆的字形）；Sony TRC包含关于成人内容分级声明显示位置的具体像素要求；XR包含对游戏不得出现特定地缘政治地图表示的内容规范。这些条款与代码质量无关，引擎层面无法自动保证合规。

**误区三：SDK版本与认证版本总是一致**
开发者常误以为使用最新SDK即等同于满足最新认证要求。实际上，平台方会在SDK之外独立更新认证文档，新增的Must条款可能在SDK发布数周后才生效，开发者需要主动订阅平台开发者通讯（如Nintendo的NDev邮件列表）来跟踪认证文档变更。

## 知识关联

学习平台认证之前，需要掌握平台抽象概述中的硬件分层模型，理解为何Save Data API、Trophy API等功能会在引擎抽象层中被单独封装——这些封装的设计决策直接由各平台TRC/XR/Lotcheck的具体条款驱动。

掌握平台认证的概念框架后，自然进入合规测试（Compliance Testing）主题，后者聚焦于如何在开发周期内系统性地针对TRC/XR/Lotcheck条款设计测试用例、搭建自动化验证流水线，以及如何使用Sony的CTKIT、Microsoft的XCertification工具集进行预提交自检。平台认证定义了"什么必须满足"，合规测试解决"如何验证已满足"。