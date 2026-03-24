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
quality_tier: "pending-rescore"
quality_score: 41.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 合规测试

## 概述

合规测试（Compliance Testing）是游戏开发流程中针对目标平台官方技术要求所进行的系统性验证过程。在游戏提交至 PlayStation、Xbox、Nintendo Switch、iOS App Store 或 Google Play 等平台之前，开发者必须确保游戏通过该平台发布方制定的全套技术规范检查，否则提交将被拒绝，导致发布延期。

合规测试的规范体系由各平台方独立维护。索尼的规范文档称为 **TCR（Technical Compliance Requirements）**，微软使用 **XR（Xbox Requirements）**，任天堂使用 **LOT CHECK** 流程，移动端则分别遵循苹果的 **App Review Guidelines** 和 Google 的 **Play Policy**。每套规范均包含数十至数百条具体规则，涵盖存档系统、网络错误处理、UI/UX 可访问性、崩溃率阈值等方面。

合规测试的重要性在于，平台方的认证审核团队会使用与开发者相同的测试清单逐条验证游戏行为。一旦某条规则未通过，游戏将收到「Lot Check Failure」或「TCR Violation」通知，开发者需修复后重新提交整个认证流程，通常额外耗费 1-3 周时间。提前进行充分的内部合规测试是缩短上市周期的关键手段。

---

## 核心原理

### 平台规范的分类结构

各平台的合规要求通常被划分为**强制性（Mandatory）**和**建议性（Advisory）**两类。强制性规则必须 100% 满足，任何一条不达标均会导致认证失败；建议性规则不满足不会直接驳回提交，但平台方可能标注备注意见。例如，Xbox XR-015 规定游戏在接收到网络断开事件后必须在 60 秒内向玩家显示明确提示，这是强制性要求，而某些 UI 字体大小建议则属于 Advisory 级别。

### 常见合规检查项目

合规测试清单通常涵盖以下具体技术领域：

- **存档与持久化**：PlayStation TCR 要求游戏在存档写入失败时必须显示错误对话框，且不得在存档进行中允许玩家关闭主机电源而不给出警告。
- **手柄断开处理**：任天堂 LOT CHECK 要求当 Joy-Con 断开时游戏必须暂停并进入「等待控制器重新连接」界面，不得让游戏继续运行。
- **系统通知响应**：Xbox 要求游戏在接收到系统级别的「挂起（Suspend）」信号后必须在 1 秒内完成状态保存并释放 GPU 资源，否则视为 XR 违规。
- **年龄分级与内容标注**：iOS App Store 要求开发者在提交时准确填写内容分级问卷，含有暴力或成人内容的应用若填写不实将被下架。
- **崩溃率标准**：Google Play 要求上架游戏的 ANR（应用无响应）率需低于 0.47%，崩溃率低于 1.09%，否则应用在商店中的可见度会被降级。

### 内部合规测试流程

开发团队通常建立**合规测试矩阵**，将所有平台规则映射为具体的测试用例（Test Case）。以 Xbox XR 测试为例，一个典型的测试矩阵包含规则编号、规则描述、测试步骤、预期结果和实际结果五列。QA 团队按照该矩阵逐条执行测试，并将结果记录为 Pass / Fail / Not Applicable。最终所有强制规则必须标注 Pass，方可提交平台认证。

自动化工具也被广泛用于辅助合规测试，例如 PlayStation 提供的 **PlayStation Dev Kit Checker** 工具可扫描游戏 ROM 中是否使用了禁用的系统调用，任天堂的 **NintendoSDK AuthCheck** 工具可验证 NSP 包体中的权限声明是否符合规范。

---

## 实际应用

**案例一：Joy-Con 断开测试**
在 Nintendo Switch 游戏的合规测试中，测试人员会在游戏进行中拔除 Joy-Con，确认游戏画面是否立即暂停并出现「请重新连接控制器」提示界面。若游戏继续运行，则该测试用例标记为 Fail，对应 Nintendo LOT CHECK 规则 No. 0080。开发者需在代码中监听 `npad::GetStyleSet()` 返回值变化并触发暂停逻辑。

**案例二：Xbox 家庭设置内容过滤**
Xbox XR-045 要求游戏必须尊重账户的家长控制内容过滤设置。合规测试人员会创建一个内容限制级别为「Child」的测试账户，启动游戏，验证成人内容（如暴力场景）是否被正确屏蔽或游戏拒绝启动并提示「此内容不符合您的账户设置」。

**案例三：iOS 崩溃率监控**
提交 App Store 前，开发者应通过 Xcode Organizer 的 Crashes 报告栏目确认 Beta 版本的崩溃率。若崩溃率超过 Apple 内部阈值（通常参考行业标准 < 0.5%），审核团队可能主动联系开发者要求修复主要崩溃路径后再审。

---

## 常见误区

**误区一：认为通过内部测试等同于通过平台认证**
很多开发团队在自有设备上测试无误后，认为认证只是走形式。实际上，平台官方认证团队使用的测试用例包含许多边缘场景，例如在特定网络延迟条件下触发存档、在低电量模式下运行游戏等，这些场景在常规开发测试中往往被忽略，是 TCR/LOT CHECK 失败的高频原因。

**误区二：合规测试只需在发布前做一次**
部分团队将合规测试仅安排在提交前一周进行。然而，当游戏的核心系统（如存档逻辑、控制器处理、网络模块）发生迭代时，对应的合规规则验证需要同步重新执行。例如每次修改存档系统后，必须重新执行所有与存档相关的 TCR/XR 测试用例，而非仅在最终版本统一补测。

**误区三：不同平台版本只需一份合规测试报告**
PlayStation 和 Xbox 的合规规范存在实质性差异，例如 PlayStation 要求游戏进入和退出 Rest Mode 时需保存特定的会话状态，而 Xbox 对 Suspend/Resume 的技术要求则不同。即便是同一款跨平台游戏，也必须针对每个目标平台分别建立和执行独立的合规测试矩阵。

---

## 知识关联

合规测试建立在**平台认证**（Platform Certification）的基础规范之上——平台认证定义了开发者账户资质和提交权限的获取方式，而合规测试则是认证申请提交前的技术验证环节，两者共同构成游戏上架流程的门禁机制。

在游戏引擎的平台抽象层设计中，良好的平台抽象封装（如将控制器断开事件、系统挂起信号统一抽象为引擎事件）可以显著降低合规测试失败的概率，因为平台特定的边界行为被集中处理，而非分散在各业务逻辑代码中。Unity 和 Unreal Engine 均在其平台插件层中预置了部分合规相关的标准处理逻辑，例如 Unreal 的 `FSlateApplication` 在检测到手柄断开时默认触发暂停事件，即对应 Nintendo LOT CHECK 相关规则的内置支持。
