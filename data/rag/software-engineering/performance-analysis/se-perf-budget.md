---
id: "se-perf-budget"
concept: "性能预算"
domain: "software-engineering"
subdomain: "performance-analysis"
subdomain_name: "性能分析"
difficulty: 2
is_milestone: false
tags: ["规划"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.481
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 性能预算

## 概述

性能预算（Performance Budget）是一种将前端或系统性能指标量化为具体阈值，并在开发过程中强制执行这些阈值的工程实践。它的核心思想是：像控制财务预算一样控制性能指标，当某个功能的引入会"超支"时，必须削减其他地方的"开销"才能提交。这一概念由设计师 Tim Kadlec 于 2013 年在其博客文章《Setting a Performance Budget》中正式提出并推广。

性能预算的意义在于它将"网页要快"这样的模糊目标，转化为"首次内容绘制（FCP）必须在 1.5 秒以内、总脚本体积不超过 200KB（gzip 后）"这样可量化、可自动检测的工程约束。Google 的研究表明，页面加载时间超过 3 秒，移动端用户的跳出率会上升 32%。性能预算让团队在 CI/CD 流水线中捕捉性能退化，而不是等到用户投诉才发现问题。

性能预算的适用范围不仅限于前端网页，也被应用于移动 App 的冷启动时间、后端 API 的 P99 延迟、以及机器学习推理服务的吞吐量限制等场景。

## 核心原理

### 性能指标的三种分类

性能预算所监控的指标分为三类：

**基于数量的指标（Quantity-based）**：直接度量资源大小，如图片总大小不超过 500KB、第三方脚本数量不超过 3 个、总 HTTP 请求数不超过 50 个。这类指标最容易在构建阶段自动检测，但与用户实际感受的相关性较间接。

**基于时间的指标（Timing-based）**：度量关键时间点，如最大内容绘制（LCP）≤ 2.5 秒、首字节时间（TTFB）≤ 600 毫秒、总阻塞时间（TBT）≤ 200 毫秒。这些数字直接源自 Google Core Web Vitals 的"良好"评分门槛，代表真实用户体验。

**基于规则的指标（Rule-based）**：使用 Lighthouse 评分或 WebPageTest 的 Speed Index 等综合评分，如 Lighthouse 性能分数不得低于 85 分。这类指标综合了多个维度，但当某次提交导致分数下降时，定位具体原因相对困难。

### 预算的制定方法

制定性能预算有两种常见起点：**竞品对标法**与**用户研究法**。竞品对标法是将竞争对手在中位数设备（如 Moto G4）和 4G 网络条件下的性能数据作为基准，将自身目标设置为比竞品快 20%。用户研究法则根据用户使用的网络和设备分布来反推预算，例如，如果目标用户中 60% 使用 3G 网络，则 LCP 预算应按 3G 条件（约 4Mbps 下行）倒推计算。

计算资源体积预算时，一个常用公式是：

> **可用时间 = 传输时间 + 解析时间 + 执行时间**

若目标 TTI（可交互时间）为 5 秒，在 3G（1.6Mbps）条件下，仅传输 JavaScript 就消耗了大量时间，因此社区通常建议单页面 JS 总体积（压缩前）不超过 170KB，这对应约 53KB gzip 后的大小。

### 预算的执行机制

性能预算必须集成到自动化工具链中才有意义。常见工具包括：

- **Bundlesize / size-limit**：在 CI 中检查 webpack 构建产物的文件大小，超出预算则构建失败并返回非零退出码。
- **Lighthouse CI**：在每次 Pull Request 时运行 Lighthouse 并与预算配置文件（`.lighthouserc.json`）对比，支持 GitHub Status Check 集成。
- **WebPageTest API**：通过定时任务测量线上真实性能，并在指标超阈值时触发告警。

一个典型的 `budget.json` 配置示例（Lighthouse CI 格式）会指定如 `"resourceSizes": [{"resourceType": "script", "budget": 125}]`，表示脚本资源总大小预算为 125KB。

## 实际应用

**电商平台的结账页面**：Pinterest 在 2016 年将 PWA 的 JS 包体积从 2.5MB 削减至 200KB，首屏加载时间缩短 40%，同期注册转化率提升 15%。他们的做法是为结账流程的每个页面组件设置独立的 JS 体积预算，超出预算的 PR 无法合入主干。

**新闻媒体网站**：BBC 为其新闻页面设定了"第一次可用内容在 1000ms 内渲染"的预算，并据此限制了首屏加载的字体文件数量（最多 2 个字重），因为一个未子集化的中文字体文件可达 5MB，直接击穿所有时间预算。

**API 服务的 SLA 预算**：在后端服务中，性能预算体现为 SLO（服务级别目标），如"P95 延迟 ≤ 100ms，P99 延迟 ≤ 300ms"，并通过 Prometheus + Alertmanager 在延迟超标时自动通知值班工程师。

## 常见误区

**误区一：以平均值代替百分位数作为预算指标**。将"平均响应时间 ≤ 200ms"设为预算目标会掩盖尾部延迟问题——即便平均值达标，P99 延迟可能高达 2 秒，对 1% 的用户体验极差。正确做法是同时设定 P50、P90、P99 三个分位数的预算。

**误区二：只设置预算却不阻断流水线**。许多团队将性能预算配置为"警告模式"（warning），超出预算只发邮件通知但不阻塞合并。这会导致"破窗效应"——开发者逐渐忽视警告，预算名存实亡。性能预算必须以构建失败（build failure）的形式强制执行，才能真正约束行为。

**误区三：把性能预算设置为当前性能水平**。如果当前 LCP 是 3.2 秒，就把预算设成 3.2 秒，这只能防止退化，无法驱动改进。合理的预算应设置在目标值（如 LCP ≤ 2.5 秒），并配合专项优化冲刺来逐步达标。

## 知识关联

**关联前置知识**：使用性能预算需要先了解各项具体性能指标的含义，例如 LCP、FCP、TBT 的计算方式，以及浏览器渲染管线（Critical Rendering Path）如何影响这些指标的数值。

**关联扩展主题**：性能预算是性能监控（Performance Monitoring）实践的入门步骤。在掌握预算管理后，可进一步学习真实用户监控（RUM, Real User Monitoring）与合成监控（Synthetic Monitoring）的区别——前者基于真实用户数据，后者（如 Lighthouse CI）在实验室环境中运行，两者共同构成完整的性能监控体系。此外，性能预算的制定决策会直接影响性能优化策略的优先级排序，例如当 JS 体积超预算时，团队需要在代码分割（Code Splitting）、Tree Shaking 和移除第三方库之间做出取舍。