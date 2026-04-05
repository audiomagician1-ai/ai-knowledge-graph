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


# 可访问性审查

## 概述

可访问性审查（Accessibility Review）是代码审查流程中专门针对残障用户使用体验的检查环节，核心目标是确保软件产品符合 WCAG（Web Content Accessibility Guidelines，网页内容无障碍指南）标准，并验证 ARIA 属性、键盘导航路径与屏幕阅读器兼容性均达到可用水平。与普通功能代码审查不同，可访问性审查需要审查者具备对辅助技术（Assistive Technology）工作机制的专项理解。

WCAG 标准由 W3C 于 1999 年首次发布，目前广泛应用的版本为 2.1（2018年发布），最新版本 2.2 于 2023 年 10 月正式成为推荐标准。该标准按"POUR"原则组织：可感知（Perceivable）、可操作（Operable）、可理解（Understandable）、健壮性（Robust）。可访问性审查的检查项直接映射这四个维度，每个维度下有具体的成功标准（Success Criteria），共分 A、AA、AAA 三个合规等级，大多数政府及企业项目要求达到 AA 级。

可访问性审查的重要性体现在法律合规与用户覆盖两方面。美国《康复法》第 508 条款和欧盟 EN 301 549 标准均具有法律强制力，违规可面临诉讼。全球约有 13 亿残障人士，其中视障、运动障碍、听障用户是辅助技术的主要使用群体，忽视可访问性意味着主动排除这部分用户群。

## 核心原理

### WCAG 合规检查

审查者需逐一核对代码是否满足 WCAG 2.1 AA 级的 50 项成功标准中与当前功能相关的部分。最常被忽视的包括：

- **1.4.3 色彩对比度**：普通文本要求前景色与背景色对比度不低于 4.5:1，大文本（18pt 或 14pt 粗体）不低于 3:1。审查时需使用工具（如 axe DevTools 或 Colour Contrast Analyser）验算实际渲染颜色，而非设计稿标注颜色，因为 CSS 透明度叠加会改变最终值。
- **1.1.1 非文本内容**：所有 `<img>` 标签必须有 `alt` 属性；装饰性图片使用 `alt=""`（空字符串），而非省略该属性；图标按钮需通过 `aria-label` 提供文字描述。
- **2.4.7 焦点可见性**：任何交互元素在获得键盘焦点时必须有可见的视觉指示，审查时需检查是否存在 `outline: none` 或 `outline: 0` 的 CSS 规则覆盖了默认焦点样式。

### ARIA 属性审查

ARIA（Accessible Rich Internet Applications）属性为原生 HTML 语义不足的自定义组件补充无障碍语义，但错误使用 ARIA 往往比不使用危害更大。审查重点包括：

- **角色（Role）正确性**：`role="button"` 的元素必须能响应 `Enter` 和 `Space` 键盘事件；`role="dialog"` 的模态框必须配合 `aria-modal="true"` 且焦点须被限制在对话框内部（焦点陷阱，Focus Trap）。
- **状态与属性同步**：展开/折叠的手风琴组件必须在 JavaScript 切换状态时同步更新 `aria-expanded` 值（`true`/`false`）；禁用的表单控件需同时设置 HTML `disabled` 属性和 `aria-disabled="true"`。
- **ARIA 第一原则**：审查时优先建议使用原生 HTML 元素（如 `<button>` 替代 `<div role="button">`），因为原生元素自带键盘行为和语义，减少手动维护 ARIA 的负担。

### 键盘导航检查

键盘导航审查需验证用户在不使用鼠标的情况下能完成所有核心操作。具体检查项包括：

- **Tab 顺序逻辑性**：`tabindex` 正整数值（如 `tabindex="3"`）会打乱自然 DOM 顺序，应避免使用；合法用法仅为 `tabindex="0"`（加入 Tab 序列）和 `tabindex="-1"`（仅允许程序化聚焦）。
- **键盘陷阱排查**：WCAG 2.1.2 要求用户能通过键盘离开任何获得焦点的组件，审查时需特别检查第三方嵌入内容（如地图、视频播放器）是否存在键盘无法退出的情况。
- **快捷键冲突**：若组件自定义了单字符快捷键（如 `s` 触发搜索），WCAG 2.1.4 要求提供关闭或重新映射该快捷键的机制，防止与屏幕阅读器内置命令冲突。

### 屏幕阅读器兼容性

主流屏幕阅读器包括 NVDA（Windows 免费）、JAWS（Windows 商业）和 VoiceOver（macOS/iOS 内置）。审查代码时需考虑其读取机制：屏幕阅读器通过浏览器暴露的无障碍树（Accessibility Tree）获取信息，而非直接解析视觉界面。常见问题：动态内容更新后必须使用 `aria-live` 区域（`aria-live="polite"` 或 `aria-live="assertive"`）通知屏幕阅读器；表单错误信息须通过 `aria-describedby` 关联到对应输入框，否则屏幕阅读器用户填写表单时无法获知错误内容。

## 实际应用

**电商结账流程审查示例**：审查工程师发现"立即购买"按钮的 HTML 为 `<div class="buy-btn" onclick="checkout()">立即购买</div>`，问题有三：缺少 `role="button"`、无法响应 `Enter` 键、不在 Tab 顺序中。修复方案是替换为 `<button type="button" onclick="checkout()">立即购买</button>`，一次改动解决所有问题。

**模态对话框审查**：一个确认删除的弹窗在打开后焦点未移入弹窗，且用户按 `Escape` 键无法关闭。审查者需要求开发者在弹窗挂载后调用 `dialog.focus()` 或聚焦弹窗内第一个可交互元素，同时绑定 `keydown` 事件监听 `Escape` 键关闭弹窗，并在弹窗关闭后将焦点归还至触发按钮。

**自动化工具辅助审查**：axe-core 库可集成至 Jest 或 Cypress 测试套件，在 CI/CD 管道中自动检测约 57 类可访问性规则。审查时可要求开发者提供 axe 测试报告，但需向团队说明自动化工具仅能发现约 30%-40% 的可访问性问题，手动键盘测试和屏幕阅读器测试不可省略。

## 常见误区

**误区一：`alt` 属性写图片文件名或"图片"二字**。许多开发者习惯写 `alt="banner.jpg"` 或 `alt="图片"`，这对屏幕阅读器用户完全无意义。`alt` 的正确写法是描述图片传递的信息内容，例如 `alt="2024年春季促销活动，全场八折"`；若图片仅作装饰无信息价值，则使用 `alt=""`。

**误区二：认为颜色对比度仅影响视觉设计，与代码无关**。开发者常认为对比度是 UI 设计师的责任。但代码实现时，CSS 的 `opacity`、`rgba` 颜色值、渐变背景叠加、`mix-blend-mode` 等属性都会影响最终渲染对比度，需要在代码审查阶段重新验算，而非仅看设计稿。

**误区三：为所有元素添加 `tabindex="0"` 以"提升可访问性"**。有开发者误认为让更多元素可获焦点就等于更好的可访问性，导致纯展示性的 `<div>` 或 `<span>` 进入 Tab 序列，屏幕阅读器用户需要按更多次 Tab 键才能到达目标控件，实际降低了使用效率。

## 知识关联

可访问性审查以 HTML 语义化标签的理解为基础，掌握 `<nav>`、`<main>`、`<article>`、`<button>` 等地标元素的原生语义，能直接减少 ARIA 的使用需求。CSS 布局知识（尤其是视觉顺序与 DOM 顺序分离的场景，如 `order` 属性或绝对定位）是理解键盘 Tab 顺序问题的必要背景，因为屏幕阅读器按 DOM 顺序而非视觉顺序读取内容。

在代码审查实践中，可访问性审查通常与安全审查、性能审查并列作为专项审查类别，建议在 Pull Request 模板中加入可访问性检查清单（Checklist），将 WCAG AA 级关键检查项转化为审查者必须逐条确认的条目，避免依赖审查者的个人经验和记忆。