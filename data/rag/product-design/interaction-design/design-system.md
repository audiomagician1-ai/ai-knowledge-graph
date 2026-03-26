---
id: "design-system"
concept: "设计系统"
domain: "product-design"
subdomain: "interaction-design"
subdomain_name: "交互设计"
difficulty: 4
is_milestone: false
tags: ["系统"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 33.3
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.314
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 设计系统

## 概述

设计系统（Design System）是将产品界面中的视觉语言、交互模式、组件库和设计规范整合成一套可复用、可维护的共享体系。它不只是一个 UI 组件库，而是涵盖了设计令牌（Design Token）、使用指南、无障碍规范和品牌语义的完整生态。一个成熟的设计系统至少包含三个层次：原子级别的令牌定义（如颜色、间距、字体比例）、分子级别的组件规范，以及页面级别的布局模式与交互规则。

设计系统的概念在 2010 年代中期随着大规模 Web 产品的复杂度增长而正式成形。2014 年 Google 发布 Material Design，2016 年 IBM 推出 Carbon Design System，2019 年 Shopify 开源 Polaris——这三个里程碑将"设计系统"从内部工具转变为行业标准实践。在此之前，多数团队依赖零散的样式指南（Style Guide）或模式库（Pattern Library），但这类文档与代码实现容易脱节，导致"设计稿与线上效果不一致"的顽疾长期存在。

对于拥有多个产品线或多支并行团队的组织，设计系统解决的核心问题是一致性与效率的双重瓶颈。据 Sparkbox 2021 年设计系统调查，采用设计系统的团队报告 UI 开发速度平均提升 34%，跨团队的视觉一致性问题下降超过 50%。这使得设计系统成为中大型产品团队不可绕过的基础设施投资。

---

## 核心原理

### 设计令牌：系统的原子单位

设计令牌是将设计决策以命名变量的形式存储的机制，是连接设计工具与代码实现的关键桥梁。一个令牌的典型定义如下：

```
color.brand.primary = #0057FF
spacing.base = 8px
font.size.body = 16px
font.weight.medium = 500
```

令牌通常分为三层：**全局令牌（Global Token）** 存储原始值，**别名令牌（Alias Token）** 赋予语义（如 `color.action.default` 引用 `color.brand.primary`），**组件令牌（Component Token）** 则与具体组件绑定（如 `button.background.default`）。这种三层结构允许主题切换（Theme Switching）只修改别名层，无需触动全局和组件层——Figma Variables 与 Style Dictionary 工具链都基于此模型运作。

### 组件规范的结构化表达

设计系统中每个组件的规范文档不仅包含视觉样式，还必须定义：组件状态（Default / Hover / Active / Focus / Disabled / Error）、尺寸变体（如 Small / Medium / Large 对应的 padding 分别为 `4px 8px`、`8px 16px`、`12px 24px`）、组合规则（Composition Rules，描述哪些子组件可嵌套）以及无障碍要求（WCAG 2.1 AA 标准要求正文文字对比度不低于 4.5:1）。

以按钮组件为例，一份完整的组件规范需要覆盖 Primary / Secondary / Tertiary / Destructive 四种语义变体，每种变体在 6 种状态下的令牌引用，以及键盘焦点顺序和 `aria-label` 使用场景。缺少任何一维度，组件就无法被不同团队稳定复用。

### 版本管理与多团队治理模型

设计系统需要像软件库一样进行语义化版本控制（Semantic Versioning：Major.Minor.Patch）。主版本号（Major）升级代表破坏性变更（Breaking Change），如修改了令牌命名空间或移除了某个 prop；次版本号（Minor）升级代表新增组件或令牌；补丁版本（Patch）对应视觉微调或 Bug 修复。

治理模型通常有三种形态：**集中式**（由专职 Design System Team 维护，其他团队消费），**联邦式**（核心团队维护基础层，各业务团队贡献扩展组件），**开放贡献式**（类似开源项目，有 RFC 流程和贡献指南）。Atlassian Design System 采用联邦式，允许各产品线在核心规范之上扩展，但扩展组件须经过评审才能"晋升"为公共组件。

---

## 实际应用

**场景一：多品牌主题支持**
电商平台同时运营多个子品牌时，可通过设计令牌的别名层实现主题切换。将 `color.brand.primary` 在品牌 A 映射为 `#FF6B35`，在品牌 B 映射为 `#2D6BE4`，所有引用该令牌的组件无需任何代码改动即可完成视觉切换。Style Dictionary 支持将同一份令牌 JSON 编译为 CSS Variables、iOS Swift 常量和 Android XML，实现跨平台一致性。

**场景二：设计交付效率优化**
某金融 App 团队在引入设计系统前，设计师标注一个页面平均耗时 3 小时，开发实现需要 2 天；引入后，页面直接由组件拼装，标注工作缩减到 30 分钟，开发实现缩短至半天。关键是 Figma 组件与 React 组件通过令牌共享同一套命名规范，减少了"翻译损耗"。

**场景三：无障碍合规批量修复**
当 WCAG 对比度标准从 AA 升级要求时，通过修改设计令牌层的 `color.text.secondary` 值，整个系统中所有使用该令牌的组件文本自动获得修复，而非逐页检查修改——这是设计系统相对于传统样式表的核心优势之一。

---

## 常见误区

**误区一：把设计系统等同于组件库**
许多团队将"建设设计系统"理解为"封装一批 React 组件"，却忽略了令牌定义、使用文档、决策记录（Decision Log）和贡献流程。没有令牌层的组件库，主题切换时必须逐个修改 hardcode 的颜色值；没有使用文档的组件库，使用者不知道何时用 Modal 何时用 Drawer，组件反而会被误用。

**误区二：设计系统应该追求"大而全"**
初期团队常犯的错误是试图一次性定义所有组件和场景，导致系统迟迟无法落地。Airbnb 的设计系统负责人曾公开表示，其内部系统 DLS（Design Language System）在初期仅覆盖 20 个核心组件，而非 200 个。遵循"先覆盖 80% 的高频场景，再迭代长尾需求"的策略，能更快让系统产生实际价值。

**误区三：设计系统是一次性项目**
设计系统不是"建好就可以不管"的产品，它需要与业务产品同步演进。组件的 API 变更需要发布迁移指南（Migration Guide），令牌的重命名需要给消费团队提供 Deprecation 警告期（通常不少于一个主版本周期）。将设计系统视为"活的基础设施"而非"已完成的文档"，是系统能否长期存活的关键认知。

---

## 知识关联

理解设计系统需要 **React 基础**的支撑：组件的 Props 接口设计直接决定了设计令牌如何在代码层传递，`variant`、`size`、`colorScheme` 等 prop 命名惯例来源于设计规范中的语义变体定义。**CSS-in-JS 与 TailwindCSS** 是设计系统在代码侧的两种主流实现路径：前者（如 styled-components、Emotion）通过 `ThemeProvider` 注入令牌对象，后者通过 `tailwind.config.js` 的 `theme.extend` 将令牌映射为工具类名。

从 **Material Design** 的学习中积累的"状态层叠加模型"（State Layer Model，Hover 状态在背景色上叠加 8% 的主色）和"高程系统"（Elevation System，共 6 级）是理解如何将设计决策系统化的典范，可直接迁移为设计系统的规范制定方法论。

在此基础上，**组件库建设**是将设计系统规范落地为可用代码包的工程实践（涉及 Rollup 打包、Storybook 文档化、npm 发版流程）；**设计令牌**是将本文提到的令牌三层模型深化为工具链选型（Style Dictionary vs. Theo vs. Tokens Studio）的专项课题；**品牌设计**则从设计系统的"消费者"视角出发，研究如何通过令牌体系将品牌标识语言（Brand Identity）转化为可编程的产品视觉规范。