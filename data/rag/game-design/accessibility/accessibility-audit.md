---
id: "accessibility-audit"
concept: "可达性审计"
domain: "game-design"
subdomain: "accessibility"
subdomain_name: "可达性设计"
difficulty: 3
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-03-22"

sources:
  - type: "industry-guideline"
    ref: "Game Accessibility Guidelines (gameaccessibilityguidelines.com)"
    url: "https://gameaccessibilityguidelines.com/full-list/"
  - type: "industry-guideline"
    ref: "Xbox Accessibility Guidelines (XAGs) V3.2 - Microsoft Game Dev"
    url: "https://learn.microsoft.com/en-us/gaming/accessibility/guidelines"
  - type: "industry-article"
    ref: "Keywords Studios - 什么是无障碍化QA (AQA)?"
    url: "https://www.keywordsstudios.com/zh-cn/news/什么是无障碍化qa-aqa/"
scorer_version: "scorer-v2.0"
---
# 可达性审计

## 概述

可达性审计（Accessibility Audit）是系统性评估游戏无障碍设计水平的专业方法。它通过结构化的测试计划和检查清单，识别游戏中对残障玩家构成障碍的设计问题，并按严重程度排序以指导修复优先级。

游戏可达性审计的标准化始于 2012 年前后。**Game Accessibility Guidelines**（gameaccessibilityguidelines.com）自 2012 年起持续维护，是业界最早也最广泛使用的游戏可达性指南之一。2023 年微软发布了 **Xbox Accessibility Guidelines (XAGs) V3.2**，由微软与行业专家和残障玩家社区共同开发，包含 23 条结构化指南（编号 XAG 101–123），覆盖从文本显示到心理健康的全方面（Microsoft Game Dev）。

可达性审计是游戏可达性设计体系的验证环节——在学习具体的可达性设计指南和原则后，需要通过审计来检验这些原则是否在实际游戏中得到了正确落地。

## 核心知识点

### 审计覆盖的障碍类别

Game Accessibility Guidelines 将可达性问题划分为**五大障碍类别**：

1. **运动障碍（Motor）**：操控与移动能力相关。检查项包括：是否允许按键重映射、是否支持辅助技术设备（眼动追踪、开关控制）、是否避免了必须快速连按（QTE）、是否提供 0.5 秒的输入冷却期等。
2. **认知障碍（Cognitive）**：思维、记忆和信息处理能力相关。检查项包括：是否使用简洁清晰的语言、是否提供交互式教程、是否允许按自己节奏阅读文本、是否有进度提醒和目标提示。
3. **视觉障碍（Vision）**：检查项包括：文本与背景的高对比度、可调字体大小、不依赖单一颜色传达关键信息、色盲友好选项、屏幕阅读器支持。
4. **听觉障碍（Hearing）**：检查项包括：为所有重要语音提供字幕、关键音频信息同时用视觉方式呈现、提供立体声/单声道切换。
5. **语言障碍（Speech）**：检查项包括：不强制要求语音输入、提供文字转语音/语音转文字聊天选项。

### 审计的三级优先级体系

Game Accessibility Guidelines 按实施难度和影响范围将检查项分为三级（gameaccessibilityguidelines.com）：

| 级别 | 特征 | 典型检查项 |
|------|------|-----------|
| **Basic（基础级）** | 实现简单，覆盖面广，适用于几乎所有游戏机制 | 允许按键重映射、提供字幕、避免闪烁画面、允许暂停 |
| **Intermediate（中级）** | 需要一定规划但通常属于良好的游戏设计 | 色盲模式、可调字体大小、可调游戏速度、交互式教程 |
| **Advanced（高级）** | 针对重度障碍的复杂适配 | 眼动追踪支持、音频GPS/声纳地图、全面屏幕阅读器兼容 |

### XAGs 的结构化指南框架

微软 Xbox Accessibility Guidelines 的每条指南都包含标准化的六部分结构（Microsoft Game Dev）：

1. **Goal（目标）**：该指南正确实施后对玩家的预期影响
2. **Overview（概述）**：背景说明
3. **Scoping Questions（范围界定问题）**：帮助开发者判断该指南是否适用于自己的游戏
4. **Implementation Guidelines（实施指南）**：最低限度的可达性组件要求
5. **Example Content（示例内容）**：来自真实游戏的实施案例
6. **Potential Player Impact（潜在玩家影响）**：哪些障碍类型的玩家最可能受到影响

23 条 XAG 覆盖：文本显示（101）、对比度（102）、视听觉替代通道（103）、字幕与说明（104）、音频可达性（105）、屏幕朗读（106）、输入（107）、难度选项（108）、物体清晰度（109）、触觉反馈（110）、音频描述（111）、UI 焦点处理（113）、UI 上下文（114）、错误信息（115）、时间限制（116）、视觉干扰与动效设置（117）、光敏（118）、语音转文字聊天（119）、通讯体验（120）、功能文档（121）、客服可达性（122）、心理健康最佳实践（123）。

### AQA 的两种执行方法

Keywords Studios（游戏行业无障碍 QA 服务商）总结了两种标准审计方法（Keywords Studios: 什么是 AQA?）：

**方法一：一次性审计（Audit）**
- 团队配置：1–2 名 QA 测试员 + 1 名无障碍化负责人
- 使用预制的详细测试计划，含具体测试用例和场景
- 覆盖 UI、操控、音频、剧情、内容警告等所有方面
- 产出：最终报告，列出每个无障碍障碍及其严重程度
- 通常安排在游戏制作后期（内容较成型时），也可针对特定部分进行早期审计

**方法二：周期测试（Cycle Testing）**
- 按商定周期（每周/每两周/每两月）在新版本上运行测试
- 持续追踪已报告障碍的修复情况
- 将可达性测试内嵌到开发流程，避免被忽视
- 配合残障顾问和真实残障玩家进行游戏测试

## 关键要点

1. **审计不是合规认证**：Xbox XAGs 明确指出自身"不是合规性清单"，而是确保游戏体验"对所有人可玩可享"的最佳实践指南（Microsoft Game Dev）。
2. **五大障碍类别 × 三级优先级**：Game Accessibility Guidelines 的分类体系帮助团队有策略地分阶段推进——先搞定 Basic 级获得最大覆盖，再逐步深入。
3. **结构化测试计划是核心**：审计不是随意试玩，需要预制的测试用例覆盖每个障碍类别和优先级，产出可追踪的障碍报告。
4. **尽早且持续比一次性审计更有效**：Keywords Studios 的实践表明，将 AQA 嵌入开发周期（周期测试）比只在后期做一次审计更能确保问题被及时修复。

## 常见误区

1. **"可达性只关乎残障玩家"**：可达性改进（如字幕、可调字体、按键重映射、难度选项）实际上改善了**所有玩家**的体验。例如，嘈杂环境中的字幕、单手操作时的按键自定义、视力疲劳时的高对比度模式。

2. **"审计只需要在发布前做一次"**：一次性审计只能反映某一时间点的状态。游戏持续更新（DLC、补丁、新内容），每次更新都可能引入新的可达性障碍。持续的周期测试比单次审计更可靠。

3. **"照着检查清单打勾就够了"**：清单只覆盖已知的通用障碍模式。真正有效的审计需要结合残障玩家的实际测试反馈——只有用户自己才知道某个交互在实际使用辅助设备时是否真正可用。

## 知识衔接

**先修概念**：可达性设计导论（理解为什么可达性重要）、可达性设计指南（了解具体的设计原则和检查项）

**后续概念**：
- **可达性测试**：从审计中发现的问题转化为具体的测试用例和回归测试
- **无障碍 UI 设计**：将审计反馈落实到 UI 层面的具体改进
- **可达性设计指南**（更深入学习各类指南的实施细节）

## 参考来源

- [Game Accessibility Guidelines - Full List](https://gameaccessibilityguidelines.com/full-list/) — 自 2012 年维护至今的游戏可达性检查清单，Basic/Intermediate/Advanced 三级分类
- [Xbox Accessibility Guidelines V3.2 - Microsoft Game Dev](https://learn.microsoft.com/en-us/gaming/accessibility/guidelines) — 微软 23 条结构化可达性指南，2023 年 6 月发布
- [Keywords Studios: 什么是无障碍化 QA (AQA)?](https://www.keywordsstudios.com/zh-cn/news/什么是无障碍化qa-aqa/) — AQA 审计与周期测试方法论
