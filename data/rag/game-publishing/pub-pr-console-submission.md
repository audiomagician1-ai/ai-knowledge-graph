---
id: "pub-pr-console-submission"
concept: "主机送审"
domain: "game-publishing"
subdomain: "platform-rules"
subdomain_name: "平台规则"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.0
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


# 主机送审

## 概述

主机送审是指游戏开发商在将游戏发布到PlayStation、Xbox或Nintendo Switch平台之前，必须通过各平台官方技术合规审核的强制性流程。三大主机平台分别制定了自己的技术要求规范文档：索尼的TRC（Technical Requirements Checklist）、微软的TCR（Title Certification Requirements）和任天堂的LOT Check（Lotcheck）。这些规范文档动辄数百页，涵盖从存档系统、网络错误处理到本地化文字显示的几乎所有技术细节。

主机送审制度起源于1990年代任天堂对第三方游戏质量的强力管控。彼时雅达利大崩溃（1983年）的教训尚在，任天堂通过严格的"官方授权"审查机制重建了玩家对游戏产品的信任。现代三大平台的TRC/TCR/LOT Check体系正是继承了这一传统，演变成了覆盖技术、内容、合规等多维度的认证体系。

主机送审对于游戏发行商的商业节奏至关重要。一次送审失败（通称"Fail"）不仅意味着需要修复Bug后重新提交，整个周期通常会延误上市时间2至4周，而固定档期的营销资源浪费往往造成数十万元的额外损失。

## 核心原理

### TRC/TCR/LOT Check的结构差异

索尼的TRC文档按照"必须满足（Must）"和"应当满足（Should）"两类条目组织，违反任何一条"Must"项目都会导致直接Fail。PlayStation平台的TRC通常有超过300个检查项，涉及PS Button响应时间（要求在玩家按下PS Button后，系统界面必须在固定时间内呼出），存档数据损坏保护机制，以及奖杯（Trophy）系统集成规范。

微软的TCR在Xbox Series X/S上强调了"快速继续（Quick Resume）"兼容性检查——游戏必须能正确处理从Quick Resume状态恢复的场景，不得出现画面冻结或存档回滚。此外，Xbox平台要求所有在线功能必须在离线状态下提供替代体验或给出明确提示，这一条款是Xbox TCR中最常见的失败原因之一。

任天堂的LOT Check以严格著称，对Nintendo Switch卡带版和数字版分别有不同的检查流程。Switch的LOT Check特别关注Joy-Con振动（HD Rumble）实现方式、睡眠模式唤醒后的画面恢复，以及Nintendo Account系统的集成规范。任天堂的审核团队通常在收到提交后10个工作日内给出结果。

### 送审准备流程

送审前的准备分为内部QA验证和平台提交两个阶段。内部QA阶段需要使用开发机（Dev Kit）对照TRC/TCR文档逐条检测，通常由专职的Certification QA工程师执行。以PlayStation为例，开发商需要在索尼的DevNet开发者门户上传最终ROM版本，并同步提交一份LOT Information Sheet，详细描述游戏功能、已知问题列表（Known Issues）及测试矩阵。

提交版本必须是锁定版本（Gold Master候选版），任何提交后的代码变更都意味着需要重新走完送审流程。三大平台都提供"缺陷豁免（Exemption）"申请机制，允许开发商对极少数无法修复的已知问题申请特例许可，但豁免申请需要提供充分的技术说明，且最终批准权在平台方。

### 常见检查项技术要求

存档系统是三大平台送审中失败率最高的技术领域之一。PlayStation要求游戏在存档过程中断电后，不得出现存档文件完全损坏的情况，必须实现存档的原子写入或备份机制。Xbox要求使用Xbox Storage API进行云存档同步，若自行实现存档系统绕过官方API则直接违反TCR。Switch要求存档数据必须绑定Nintendo Account，不得以本地裸文件形式独立存储。

网络错误处理是另一高频失败点。三大平台均要求游戏在网络连接中断时给出明确的用户提示，不得出现无限加载状态（Infinite Loading Screen），且必须允许玩家在网络不可用时正常退出游戏。

## 实际应用

某款动作RPG游戏首次提交PlayStation TRC审核时，因奖杯系统实现存在两处问题而获得Fail结果：第一，存在一个奖杯在游戏正式存档创建之前可被解锁的逻辑漏洞；第二，铂金奖杯（Platinum Trophy）的解锁条件设置与TRC要求不符——TRC明确规定铂金奖杯只能在其余所有奖杯全部解锁后自动触发，不得为单独可触发的独立奖杯。开发团队花费约一周修复问题后重新提交，最终通过审核。

Nintendo Switch的LOT Check在中文版游戏中常见的失败原因是字体授权问题。Switch系统对第三方中文字体的嵌入有明确规范，若游戏使用了未经授权的商业字体，LOT Check团队会在技术审核中标记为违规。建议开发商统一使用思源黑体等开源授权字体，或在合同中明确取得字体商业发行授权并在提交时附上授权证明文件。

## 常见误区

**误区一：通过PC/移动端测试就等同于通过主机送审。** 许多从移动端转型的开发团队认为游戏逻辑通过测试即可，但主机TRC/TCR条款中大量要求是主机平台专有的，例如PS Button响应、Joy-Con震动反馈、Xbox成就系统集成等，在PC或移动端根本不存在对应概念，必须针对主机平台专项开发和测试。

**误区二：送审Fail后只需修复报告中列出的问题。** 平台审核团队的检查是抽样检查，而非穷举测试。Fail报告列出的问题是审核员发现的问题，并不代表游戏中只有这些问题。若开发团队仅修复报告中的条目而不进行全面自查，二次提交后很可能因新发现的其他违规条目再次Fail，这种情况在实际项目中极为常见。

**误区三：三大平台的送审可以并行推进而互相等价。** 实际上三者在时间线、格式要求和技术规范上存在显著差异。索尼和微软通常接受滚动提交并在约2周内出结果；任天堂LOT Check的时间节点更为固定，且对提交材料格式的要求更严格，卡带版还需要额外的物理媒体测试周期，整体周期可能比数字版多出2至3周。

## 知识关联

主机送审建立在**应用审核应对**的基本经验之上——熟悉移动端App Store/Google Play审核逻辑的团队已具备"审核即合规检查"的思维框架，但需要额外学习主机平台特有的硬件集成规范和平台服务API要求。主机送审与**内购规则**密切相关：三大平台的TRC/TCR均包含IAP（In-App Purchase）合规章节，要求游戏内购必须使用平台官方支付系统，且虚拟货币的定价、展示和退款逻辑均需符合平台规定，这构成了后续学习主机平台内购规则的直接技术背景。