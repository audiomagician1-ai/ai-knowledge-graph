---
id: "se-accessibility-review"
concept: "可访问性审查"
domain: "software-engineering"
subdomain: "code-review"
subdomain_name: "代码审查"
difficulty: 2
is_milestone: false
tags: ["可访问"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.536
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 可访问性审查

## 概述

可访问性审查（Accessibility Review）是代码审查流程中专门检验软件产品是否符合无障碍标准的环节，目标是确保残障用户——包括视觉、听觉、运动及认知障碍人群——能够平等地使用软件产品。审查内容围绕四个技术支柱展开：WCAG 合规性、ARIA 语义标注、键盘导航逻辑以及屏幕阅读器兼容性。

WCAG（Web Content Accessibility Guidelines）由 W3C 的 WAI 工作组制定，当前主流版本为 2.1（2018 年发布），2.2 于 2023 年正式发布。WCAG 将可访问性要求划分为 A、AA、AAA 三个合规等级，大多数国家法规（如美国《508 条款》修正版、欧盟 EN 301 549 标准）要求达到 AA 级。可访问性审查在代码合并前执行，能够将修复成本降低到上线后修复成本的约 1/30，这一数据来自 Forrester Research 的研究报告。

## 核心原理

### WCAG 四大原则与具体检查项

WCAG 2.1 以 POUR 原则为基础：**可感知（Perceivable）、可操作（Operable）、可理解（Understandable）、健壮（Robust）**。审查时需对应具体成功标准（Success Criteria）逐项验证。

- **对比度检查（1.4.3 AA 级）**：正文文字与背景的对比度不得低于 4.5:1，大号文字（18pt 或 14pt 加粗）不得低于 3:1。审查者使用 Chrome DevTools 的 Accessibility 面板或 axe 插件即可自动检测。
- **替代文本（1.1.1 A 级）**：所有非装饰性 `<img>` 元素必须含有描述性 `alt` 属性；装饰图片应设置 `alt=""`，禁止省略 `alt` 属性。
- **焦点可见性（2.4.7 AA 级）**：CSS `outline: none` 若无等效替代焦点样式，直接标记为不合规。

### ARIA 语义标注审查

ARIA（Accessible Rich Internet Applications）规范提供了 `role`、`aria-*` 属性体系，用于向辅助技术暴露语义信息。审查中最常发现的问题有以下几类：

1. **角色误用**：用 `<div role="button">` 替代原生 `<button>` 时，若缺少 `tabindex="0"` 和键盘事件处理，审查应标记为缺陷。
2. **状态同步缺失**：动态组件（如下拉菜单）展开时必须更新 `aria-expanded="true"`，折叠时还原为 `false`，遗漏此属性是常见问题。
3. **ARIA 第一规则（First Rule of ARIA）**：能用原生 HTML 元素表达语义时，禁止使用 ARIA 覆盖。审查者发现 `<h2 role="heading" aria-level="2">` 这类冗余写法时应提示重构。

`aria-live` 区域的审查也不可忽视：`aria-live="polite"` 适用于非紧急提示，`aria-live="assertive"` 仅用于错误等紧急信息，滥用 `assertive` 会打断屏幕阅读器当前朗读，产生负面体验。

### 键盘导航审查

键盘导航审查要求审查者实际拔除鼠标，仅用 Tab、Shift+Tab、Enter、Space、方向键完成页面全部操作。检查要点包括：

- **焦点顺序（2.4.3）**：Tab 键遍历顺序应与视觉布局一致，审查者若发现焦点在页面中"跳跃"，需检查 `tabindex` 的正值使用是否破坏了 DOM 顺序。
- **焦点陷阱（2.1.2）**：模态对话框打开时焦点必须锁定在对话框内，关闭后焦点须返回触发元素。焦点泄露到背景页面是 AA 级违规。
- **快捷键冲突（2.1.4 AA 级，WCAG 2.1 新增）**：自定义单字符快捷键（如按 S 触发搜索）必须提供关闭或重映射机制，避免与屏幕阅读器内置快捷键冲突。

### 屏幕阅读器兼容性测试

审查中需使用至少两种屏幕阅读器验证：桌面端常用 NVDA（免费，Windows）配合 Firefox，或 JAWS 配合 Chrome；macOS/iOS 使用内置 VoiceOver；移动 Android 使用 TalkBack。不同屏幕阅读器对 ARIA 的实现存在差异，因此跨平台测试是审查的必要步骤。

审查者应特别关注表单标签关联：`<label for="email">` 与 `<input id="email">` 的绑定缺失时，NVDA 只会朗读"编辑框"而无任何上下文信息，这是最高频的屏幕阅读器障碍。

## 实际应用

**场景一：电商结账页面审查**
审查者在 Pull Request 中发现 `<button class="btn-pay">` 的文本为"→"（箭头图标），缺乏描述性内容。应要求开发者添加 `aria-label="确认付款"` 或将按钮文本改为可见文字，否则屏幕阅读器用户无法理解该按钮功能。

**场景二：数据可视化组件**
图表组件仅用 `<canvas>` 渲染时，屏幕阅读器无法获取数据内容。审查应要求在 `<canvas>` 内部或旁边提供数据表格的替代呈现，或使用 `aria-label` 描述图表结论，符合 WCAG 1.1.1 及 1.3.1 要求。

**场景三：自动化与手工结合**
axe-core 等自动化工具仅能检测约 30%～40% 的 WCAG 问题（Deque Systems 数据），因此审查流程规定：CI 管道运行 axe 扫描通过后，仍需人工执行键盘导航和屏幕阅读器测试，两者缺一不可。

## 常见误区

**误区一：通过自动化扫描即等于完成可访问性审查**
axe、Lighthouse 等工具无法检测焦点顺序逻辑错误、屏幕阅读器朗读顺序问题以及动态内容的 ARIA 状态同步缺陷。将自动化报告零错误等同于 AA 级合规，是最危险的误判。

**误区二：`alt` 属性填写文件名即可**
将图片文件名（如 `IMG_20231105.jpg`）直接复制到 `alt` 属性，不仅没有意义，反而会让屏幕阅读器用户听到一串无意义字符。审查时发现文件名格式的 `alt` 值应一律要求返工，改为描述图片实际内容的文字。

**误区三：可访问性只影响少数用户，优先级低**
根据 WHO 2023 年报告，全球约 13 亿人存在某种形式的残障。此外，键盘导航优化同样改善了习惯键盘操作的高级用户体验，高对比度设计在强光环境下也对非残障用户有益。将可访问性视为小众需求而降低审查优先级，会导致产品违反《美国残疾人法》（ADA）等法律法规并面临诉讼风险。

## 知识关联

可访问性审查以 HTML 语义化基础知识为前提——理解 `<button>` 与 `<div>` 的原生键盘行为差异，是判断 ARIA 补充标注是否必要的关键。对于已掌握 WCAG 2.1 AA 级要求的团队，后续可深入研究 WCAG 2.2 新增的九条成功标准（主要涉及认知障碍和移动端操作），以及 APCA（高级感知对比度算法）这一 WCAG 3.0 草案中的新对比度计算模型。在代码审查流程层面，可访问性审查结论通常与设计系统（Design System）的组件规范联动——组件库若在源头保证 ARIA 模式正确，可大幅降低每次 PR 审查的重复工作量。