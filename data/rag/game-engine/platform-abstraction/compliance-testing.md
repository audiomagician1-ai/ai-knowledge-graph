---
id: "compliance-testing"
concept: "合规测试"
domain: "game-engine"
subdomain: "platform-abstraction"
subdomain_name: "平台抽象"
difficulty: 2
is_milestone: false
tags: ["QA"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 合规测试

## 概述

合规测试（Compliance Testing）是游戏发布流程中的强制性质量门控环节，具体指游戏开发者在向各平台官方提交审核之前，依照平台方提供的技术规范文档（Technical Requirements Checklist，简称TRC/TCR/lotcheck）逐项自查游戏是否满足上架条件的过程。不同平台的规范文档名称不同：索尼PlayStation平台使用TRC（Technical Requirements Checklist），微软Xbox平台使用XR（Xbox Requirements），任天堂平台使用lotcheck规范，苹果App Store使用App Review Guidelines。

合规测试的制度化起源于主机游戏时代的早期质量管控需求。1988年任天堂推出"官方授权"（Official Nintendo Seal of Quality）计划，要求所有第三方发行商的卡带在压制前必须通过任天堂的技术与内容审查，这是现代合规测试体系的雏形。此后，索尼在PlayStation时代建立了更为系统化的TRC文档，将崩溃处理、存档机制、手柄震动反馈等数百项技术要求明文规范化。

对于游戏引擎的平台抽象层而言，合规测试直接决定了抽象接口的设计边界——引擎的存档API、成就系统、网络会话管理等模块，均需在底层针对各平台的合规要求做出差异化实现。一次合规测试失败，轻则延迟上市两至四周（等待重新提交审核的周期），重则导致整个发布档期错失。

---

## 核心原理

### 平台技术规范的层级结构

各平台的合规要求通常分为两个严格程度层级：**强制项（Mandatory）** 和 **建议项（Advisory）**。强制项对应TRC/XR中标记为"FAIL"的测试项，任何一项不通过都会导致提交直接被拒绝；建议项标记为"WARNING"，不强制但会被记录在审核报告中。

以PlayStation的TRC为例，其强制项覆盖以下典型领域：
- **系统资源管理**：游戏必须在系统请求时于规定帧数内（通常为2秒内）完成暂停或释放前台资源
- **存档与数据**：存档写入失败时必须显示标准化错误弹窗，不得静默丢失数据
- **网络错误处理**：断网状态下的行为必须降级至离线模式，不得崩溃或无限Loading

Xbox的XR要求中有一条XR-015，规定游戏必须在用户按下Home键后的2秒内响应系统层级的暂停命令，这条要求在引擎的输入事件分发层需要专门处理。

### 合规检查清单的结构化执行

执行合规测试不是随机抽查，而是遵循结构化的测试矩阵。标准流程分为四个阶段：

1. **文档对齐（Document Alignment）**：对照平台最新版TRC文档，识别与上一版本相比新增或修改的条目。PlayStation TRC会随固件版本更新，例如PS5固件6.0曾新增关于Activity Cards（活动卡片）的必须实现条目。

2. **测试用例映射**：将每条TRC条目转化为可执行的测试用例，记录测试步骤、预期行为和判断标准。例如TRC条目"存档空间不足处理"需要测试者手动将主机存储空间填满后触发存档操作。

3. **回归测试集成**：将高频失败的合规项纳入自动化回归测试，在每次构建后自动验证，防止代码修改引入合规退化。

4. **证据收集（Evidence Package）**：部分平台（如Xbox的ID@Xbox计划）要求提交方附上截图或视频证明各强制项已通过测试。

### 跨平台合规差异的处理

同一游戏功能在不同平台的合规要求可能存在冲突，引擎的平台抽象层必须隔离这些差异。以用户生成内容（UGC）的审核为例：苹果App Store要求包含UGC的应用必须内置举报机制（App Review Guideline 1.2），而Xbox的XR对UGC举报UI的样式有具体规定，不允许使用与系统UI高度相似的自定义UI组件。引擎层通常通过条件编译（`#if PLATFORM_IOS / PLATFORM_XBOX`）或平台服务抽象类来封装这些差异。

---

## 实际应用

**案例：成就系统的跨平台合规实现**

PlayStation Trophy系统要求每款游戏必须包含至少1个铂金奖杯（Platinum Trophy），且所有奖杯的Bronze/Silver/Gold/Platinum点数加总必须落在180至285点之间（PlayStation奖杯规范2.0）。Xbox成就系统（Achievements）则要求基础游戏的总GamerScore必须为1000分，每个DLC包不超过500分。任天堂Switch没有强制成就系统。

基于此，引擎的成就抽象层（AchievementSubsystem）在设计时必须将"总分验证"作为编辑器工具集的一部分，在开发阶段即提示奖杯配置是否符合目标平台规范，而非等到提交阶段才发现问题。

**案例：评级系统（PEGI/ESRB/CERO）的合规嵌入**

不同地区的游戏内容评级机构对游戏内购、随机道具箱（Loot Box）有不同的合规要求。比利时和荷兰于2018年裁定随机战利品箱违反赌博法，这直接影响了面向这两个地区发行的游戏必须在合规测试中增加"随机道具购买在目标地区的合法性检测"用例。Steam平台在2020年更新了合规要求，强制要求开发者在商店页面披露战利品箱的掉落概率。

---

## 常见误区

**误区一：通过了平台功能测试就等于通过了合规测试**

功能测试验证游戏功能是否正常运行，合规测试验证运行方式是否符合平台规范。例如，存档功能可以正常写入（功能测试通过），但如果在存储空间不足时没有显示平台标准的错误对话框而是显示自定义UI，则TRC条目"SAVE-04"会判定为FAIL。很多团队混淆两者，导致功能测试全绿但提交被拒。

**误区二：合规测试只在最终提交前做一次**

合规测试应在开发生命周期的多个里程碑节点介入，而非仅在黄金版本（Gold Master）提交前执行一次。如果将合规验证推迟到发布前两周，一旦发现底层架构性问题（如存档系统的错误处理逻辑与TRC不符），修复成本极高。业内建议在Alpha和Beta里程碑各执行一次完整合规扫描，并在引擎日常CI（持续集成）流程中覆盖可自动化的合规检查项。

**误区三：上一版本通过即代表本次更新也通过**

平台TRC文档会随系统固件和政策更新而修订。PS5在2023年引入了关于无障碍功能（Accessibility）的新强制条目，要求游戏必须支持至少一项官方无障碍选项（如字体大小调整或字幕功能）。即使游戏1.0版本已获认证，1.1版本提交补丁时同样需要针对最新版TRC重新确认。

---

## 知识关联

合规测试建立在**平台认证**（Platform Certification）的基础知识之上——平台认证定义了开发者账户、SDK授权和提交渠道的整体框架，而合规测试是认证流程中技术验证阶段的具体操作内容。理解PlayStation开发者门户（DevNet）、Xbox Partner Center、Nintendo Developer Portal的账户体系，是获取各平台TRC文档的前提。

从引擎架构角度看，合规测试结果直接反哺**平台抽象层**的接口设计决策：存档抽象接口是否暴露错误码枚举、手柄震动的力度参数范围、网络状态回调的触发时机，这些设计细节均受各平台合规要求约束。一套经过充分合规验证的平台抽象层，能够将未来移植新平台时的合规风险从不可预期降低为有文档可查的已知差异集合。