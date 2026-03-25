---
id: "design-token"
concept: "设计令牌"
domain: "product-design"
subdomain: "visual-design"
subdomain_name: "视觉设计"
difficulty: 3
is_milestone: false
tags: ["系统"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 43.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 设计令牌

## 概述

设计令牌（Design Token）是将颜色、字体、间距、圆角、阴影等视觉属性存储为具名变量的技术规范，最早由 Salesforce 的 Lightning Design System 团队在 2016 年正式提出并开源推广。其本质是一种"平台无关的设计决策容器"——将 `#0070D2`（Salesforce 品牌蓝）这样的具体值抽象为 `color-brand-primary` 这样的语义化名称，再由各平台的构建工具将其转换为 CSS 变量、Swift 常量或 Android XML 资源。

设计令牌解决了跨平台设计一致性的根本矛盾：同一个品牌色在 Web、iOS、Android、小程序四个平台的代码实现方式完全不同，若直接硬编码颜色值，改一次品牌色需要修改数十甚至上百处文件。引入设计令牌后，修改只发生在单一数据源（Single Source of Truth）上，通过 Style Dictionary 等转换工具自动同步到所有平台的代码产物中。

---

## 核心原理

### 令牌的三层架构

业界主流实践将设计令牌分为三个层级：

1. **全局令牌（Global Token）**：存储原始值，不附带语义。例如 `color-blue-500 = #0052CC`、`font-size-16 = 16px`。全局令牌是整个系统的调色盘，通常包含 50–200 个颜色值和完整的字号/字重序列。

2. **语义令牌（Alias Token）**：引用全局令牌并赋予使用场景含义。例如 `color-action-primary → color-blue-500`、`color-text-danger → color-red-600`。语义令牌与具体数值解耦，是实现明暗主题切换的关键层级。

3. **组件令牌（Component Token）**：将语义令牌绑定到具体组件的具体属性。例如 `button-primary-background → color-action-primary`。组件令牌使单个组件的样式调整不影响全局语义。

这种三层引用链保证了"改一个全局令牌值 → 自动更新所有引用它的语义令牌 → 进而更新所有使用该语义令牌的组件"的级联效果。

### 令牌的数据格式与转换

设计令牌的标准存储格式是 JSON（或 YAML），每个令牌包含 `value`、`type`、`description` 三个核心字段：

```json
{
  "color-brand-primary": {
    "value": "#0070D2",
    "type": "color",
    "description": "品牌主色，用于主要交互元素"
  }
}
```

W3C Design Tokens Community Group 正在制定 DTCG 规范（草案版本截至 2024 年已迭代至 0.x 阶段），统一 `$value`、`$type` 等字段命名。转换工具 **Style Dictionary**（Amazon 开源）读取此 JSON，输出平台专属代码：CSS 中生成 `--color-brand-primary: #0070D2;`，Swift 中生成 `static let colorBrandPrimary = UIColor(hex: "0070D2")`。

### 命名规范的构成公式

令牌命名通常遵循以下结构：

```
[命名空间]-[类别]-[属性]-[变体]-[状态]
```

例如 `button-primary-background-hover`，其中：
- **命名空间**：组件名（button）或范围（global）
- **类别**：color / font / spacing / radius / shadow
- **属性**：background / text / border
- **变体**：primary / secondary / danger
- **状态**：default / hover / active / disabled

命名层级不宜超过 4 段，否则维护成本急剧上升。Atlassian Design System 在实践中将其令牌库控制在约 700 个命名令牌以内，以确保可维护性。

### Figma 中的令牌实现

Figma 通过 **Variables** 功能（2023 年正式发布）原生支持设计令牌，允许设计师在画布中直接引用变量而非硬编码色值。Variables 支持创建 Mode（模式），一个变量集可以同时存储 Light 和 Dark 两套值，切换模式时所有引用该变量的图层同步更新。第三方插件 Token Studio（Figma Tokens）则更早实现了与代码仓库的双向同步，支持将 Figma 变量直接推送为 GitHub Pull Request。

---

## 实际应用

**品牌主题定制**：B2B SaaS 产品为不同企业客户提供白标（White-label）服务时，只需替换一套全局令牌文件（修改 `color-brand-primary`、`color-brand-secondary` 等约 10–20 个令牌），即可生成完全不同品牌外观的产品，而无需动任何组件代码。

**多平台同步发布**：某电商 App 改版主色调，设计师在 Figma Variables 中修改 `color-action-primary` 的值，通过 CI/CD 流水线触发 Style Dictionary 重新构建，同时输出 Web CSS 文件、iOS Swift 文件和 Android `colors.xml`，三端在同一次发布中保持视觉一致。

**间距系统的令牌化**：使用 4px 基础网格时，间距令牌序列为 `spacing-1=4px`、`spacing-2=8px`、`spacing-3=12px`、`spacing-4=16px`……以此类推。组件内边距引用 `spacing-3`（12px）而非直接写 12，当基础单位从 4px 调整为 5px 时，整个间距系统统一更新。

---

## 常见误区

**误区一：将颜色值直接命名为令牌即完成令牌化。** 仅定义 `blue-500=#0052CC` 而不建立语义层，等同于给硬编码换了个名字。当需要切换暗色主题时，依然找不到"哪个令牌代表背景色"，因为没有 `color-background-default → blue-500` 这样的语义映射。真正的令牌化必须包含语义层的引用链。

**误区二：令牌粒度越细越好。** 为 Button 的每种状态、每个属性都创建独立组件令牌，会导致令牌数量爆炸（超过 2000 个时维护成本不可控）。正确做法是组件令牌只覆盖"需要在品牌定制或主题切换时被替换的属性"，其余属性直接引用语义令牌即可。

**误区三：设计令牌等同于 CSS 变量。** CSS 变量是设计令牌在 Web 平台的一种输出形式，而设计令牌本身是平台无关的 JSON 数据。同一套令牌定义还可以输出为 iOS 的 `.xcassets` 颜色集、Android 的 `dimens.xml`、React Native 的 TypeScript 常量文件，这是两者本质上的区别。

---

## 知识关联

设计令牌依赖**设计系统**作为前置基础——只有当组件规范、视觉规范已系统化整理后，令牌的语义命名才有稳定的依据；若设计系统尚未建立，令牌的分类和命名将频繁变动，反而增加维护负担。

掌握设计令牌的三层架构（尤其是语义令牌层对值与语境的分离）后，**明暗主题设计**自然成为下一个实践方向：暗色模式的实现机制正是在语义令牌层为同一个语义名称配置两套不同的全局令牌引用（Light Mode 下 `color-background-default → gray-50`，Dark Mode 下 `color-background-default → gray-900`），通过切换 Mode 而非逐一修改组件来完成主题切换。