---
id: "ios-human-interface"
concept: "iOS Human Interface"
domain: "product-design"
subdomain: "visual-design"
subdomain_name: "视觉设计"
difficulty: 2
is_milestone: false
tags: ["规范"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# iOS Human Interface Guidelines（人机交互指南）

## 概述

iOS Human Interface Guidelines（简称HIG）是Apple公司自1987年首次为Macintosh发布以来持续演进的官方设计规范文档，针对iOS平台的版本随2007年第一代iPhone发布而正式确立。HIG并非仅是视觉风格手册，而是一套规定用户与苹果设备交互方式的完整哲学体系，覆盖组件规范、手势逻辑、动效标准、无障碍要求直至App Store审核标准。

Apple的HIG以"清晰（Clarity）、遵从（Deference）、深度（Depth）"三大核心设计原则为纲领，这三条原则在2013年iOS 7的扁平化大变革中被明确写入文档。遵从原则尤为独特——它要求界面服务于内容而非喧宾夺主，这也是iOS系统图标背景统一使用圆角矩形（Squircle，数学上基于超椭圆曲线 |x/a|^n + |y/b|^n = 1，n≈5）而非安卓系统多样化图标形状的根本原因。

掌握iOS HIG对产品设计师的实际意义在于：不符合HIG规范的应用可能直接被App Store拒绝上架，同时iOS用户长期形成的交互习惯（如从屏幕左边缘右滑返回）若被破坏，会直接导致用户流失。这与Material Design的"建议性"框架性质截然不同，HIG在苹果生态中具有更强的约束力。

## 核心原理

### 导航与信息架构模式

iOS HIG定义了三种标准导航结构：层级式（Hierarchical）、扁平式（Flat）和内容驱动式（Content-or Experience-Driven）。层级式导航使用`UINavigationController`实现，每次只能前进或后退一层，"设置"应用是典型案例。扁平式导航通过Tab Bar（底部标签栏，最多5个标签）实现，"App Store"和"音乐"均采用此模式。HIG明确禁止在同一界面混用汉堡菜单（Hamburger Menu）与Tab Bar，因为这违背了可发现性原则——iOS用户预期所有主要功能入口始终可见于屏幕底部。

### 触控目标尺寸与间距规范

HIG规定所有可点击元素的最小触控热区为44×44点（points，注意不是像素）。在Retina屏幕上，1点=2像素（@2x）或3像素（@3x），因此iPhone 14 Pro的实际最小触控热区为132×132物理像素。这一44pt标准来源于人类食指指尖的平均宽度约为44-57毫米，经工程换算得出的最优触控精度阈值。状态栏高度在有刘海的机型上为44pt，无刘海旧款机型为20pt，安全区域（Safe Area）的bottom inset在iPhone X之后的机型上固定为34pt，设计稿必须预留这些空间。

### 系统字体与排版规则

iOS使用San Francisco（SF）字体家族作为系统字体，SF Pro用于大多数文本，SF Compact用于Apple Watch，SF Mono用于代码显示。HIG定义了完整的动态字体（Dynamic Type）规模，从Caption 2（最小11pt）到Large Title（最大34pt）共11个层级。设计师不得在应用中硬编码字号，必须支持动态字体缩放——这既是无障碍要求，也是HIG的强制规范。与Material Design允许设计师自由选用Google Fonts不同，HIG强烈建议优先使用SF字体，使用第三方字体需在HIG框架内严格测试可读性与本地化兼容性。

### 手势与交互反馈标准

iOS平台定义了7种标准手势：Tap、Double Tap、Swipe、Scroll、Pinch、Rotate、Long Press，每种手势均有固定的系统语义。例如，从屏幕顶部下拉固定触发通知中心（iOS 11之前）或分别触发通知中心与控制中心（iOS 11之后左/右区分），应用内部不得拦截这些系统级手势。触觉反馈（Haptic Feedback）通过`UIImpactFeedbackGenerator`实现，分为Light、Medium、Heavy三个强度等级，HIG规定触觉反馈必须与视觉/听觉反馈同步出现，不得单独使用触觉作为唯一反馈通道。

## 实际应用

**模态视图的使用场景**：HIG规定模态（Modal）视图仅应用于需要用户明确完成或取消的独立任务，如撰写邮件、填写表单。iOS 13引入的卡片式模态（Sheet）默认可下拉关闭，设计师必须为下拉关闭手势提供明确的保存/丢弃提示。错误用法的典型案例是将信息详情页设计为模态——这违反HIG，因为详情页属于层级导航，应使用Push而非Present。

**深色模式适配**：自iOS 13起，HIG要求所有应用支持深色模式（Dark Mode）。苹果提供了语义化颜色（Semantic Colors）如`UIColor.label`（自动在浅色模式为黑色、深色模式为白色），设计师应使用这套语义颜色系统而非硬编码`#000000`，以确保在两种模式下均符合WCAG 2.1的4.5:1对比度最低要求。

## 常见误区

**误区一：将iOS HIG与Material Design混为相同性质的规范**。Material Design是Google发布的跨平台建议性设计语言，iOS HIG则是苹果对其生态产品的约束性规范。在Android应用中偏离Material Design通常不会有商业后果，但在iOS应用中忽略HIG（如使用汉堡菜单替代Tab Bar、自定义返回手势冲突）会导致用户投诉率上升并存在App Store被拒风险。

**误区二：认为遵循HIG会使产品失去个性**。HIG规范的是结构与交互逻辑，并非视觉风格。Spotify、微信等个性化极强的应用均在遵守HIG导航与手势规范的基础上建立了独特视觉体系。设计师常犯的错误是将"品牌个性化"延伸至系统交互层——比如重写左滑返回手势或隐藏Tab Bar——这些改动才是HIG真正禁止的。

**误区三：认为HIG是静态文档**。苹果通常在每年WWDC（全球开发者大会，每年6月举行）期间更新HIG，iOS 17版本新增了对空间计算（Spatial Computing/visionOS）的设计参考内容。设计师应订阅developer.apple.com/design的更新，否则使用的组件规范可能已过时——例如iOS 15废弃了旧版标签栏模糊效果的具体实现参数。

## 知识关联

学习iOS HIG之前，Material Design的学习经历提供了有益的对比基础——两者都是平台级设计语言，但Material Design的"海拔（Elevation）"概念通过阴影表达层次，而iOS HIG的"深度（Depth）"原则则更多依赖半透明、模糊（Blur）和缩放动画实现空间感，底层设计哲学存在根本差异。理解这一差异有助于设计师在切换平台时不将安卓的阴影思维直接移植到iOS设计中。

iOS HIG的掌握还直接连接到Xcode中的UIKit/SwiftUI组件库——设计规范中的每一个标准组件（如`UITabBar`、`UINavigationBar`、`UIAlertController`）都有对应的系统实现，设计师理解HIG越深入，与iOS开发工程师的协作效率越高，能够准确预判哪些设计在系统组件层面可以低成本实现，哪些需要完全自定义开发。