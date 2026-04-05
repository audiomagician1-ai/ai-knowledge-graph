---
id: "material-design"
concept: "Material Design"
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
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# Material Design

## 概述

Material Design 是 Google 于 2014 年 Google I/O 大会上正式发布的视觉设计语言，英文全称为 "Material Design"，其名称直接源于"材料"这一物理隐喻。Google 的核心理念是将现实世界中纸张与墨水的物理属性数字化，让界面元素像真实纸张一样具有厚度（海拔高度，Elevation）、投影与层叠关系，同时保留扁平化设计的色彩鲜明特点。

该设计语言的诞生背景是 Android 系统界面长期缺乏统一规范。在 2014 年之前，Android 生态的应用设计风格极为碎片化，各家厂商与开发者各行其是。Material Design 通过一套系统化的规范文档，首次为 Android、Web 乃至 iOS 平台上的 Google 产品建立了统一的视觉语言。2018 年，Google 发布了 Material Design 2（也称 Material Theming），允许品牌在规范框架内进行深度定制；2021 年随 Android 12 推出的 Material You（Material Design 3）进一步引入了动态配色系统，可根据用户壁纸自动生成个性化色彩方案。

Material Design 的重要性在于它不仅仅是一套视觉风格，而是同时涵盖空间模型、运动物理、交互反馈与组件规范的完整体系。它率先将"海拔"概念系统化引入 UI 设计，使视觉层级有了可计算的物理依据。

---

## 核心原理

### 纸张与墨水的空间模型

Material Design 将所有界面元素视为存在于三维空间中的"纸片"（Material Surfaces）。每张纸片都有固定厚度：**1dp**（与屏幕无关的像素单位）。纸片可以在 Z 轴上堆叠，形成不同的 Elevation（海拔高度）值，单位同为 dp。

不同组件对应固定的海拔层级：
- 基础内容层：0dp
- 卡片（Card）：1dp–8dp
- 导航抽屉（Navigation Drawer）：16dp
- 对话框（Dialog）：24dp
- 浮动操作按钮 FAB（Floating Action Button）：6dp，按下后升至 12dp

海拔高度通过 **box-shadow** 的模糊半径与扩散程度来可视化表现，并非简单地给元素加边框。不同海拔对应的阴影参数是通过 Google 实验室精确测量真实纸张在光源下投影计算出来的，而非主观设定。

### 运动的物理依据

Material Design 明确规定动画不能使用线性曲线（Linear），因为现实世界中物体的运动受到惯性影响，总有加速与减速阶段。规范定义了四条标准缓动曲线：

- **标准缓动（Standard Easing）**：cubic-bezier(0.4, 0.0, 0.2, 1)，适用于在屏幕内移动的元素
- **减速缓动（Decelerate Easing）**：cubic-bezier(0.0, 0.0, 0.2, 1)，适用于从屏幕外进入的元素
- **加速缓动（Accelerate Easing）**：cubic-bezier(0.4, 0.0, 1, 1)，适用于离开屏幕的元素
- **尖锐缓动（Sharp Easing）**：cubic-bezier(0.4, 0.0, 0.6, 1)，适用于可能随时被中断的运动

动画时长方面，规范建议简单过渡为 **200ms–300ms**，复杂展开动画不超过 **500ms**，以避免用户感受到等待感。

### 色彩系统与排版规范

Material Design 采用"主色（Primary）、次色（Secondary）、背景色、表面色、错误色"五类色彩角色。官方提供了 **Material Color Tool**，通过 HCT（Hue, Chroma, Tone）色彩空间计算颜色的可访问性对比度，确保文字与背景的对比度符合 WCAG AA 标准（即正文最低 4.5:1）。

排版系统使用 **Roboto** 作为英文默认字体，中文平台推荐使用思源黑体（Noto Sans CJK）。字阶体系从 Display Large（57sp）到 Label Small（11sp）共 15 个级别，每个级别均规定了字重、字号与行高。

### 涟漪效果（Ripple Effect）

所有可点击的 Material 元素均需展示涟漪效果——从触摸点向外扩散的半透明圆形波纹。这一交互反馈机制的目的是让用户明确感知"触点已被系统响应"，解决触屏设备缺乏物理按键反馈的问题。涟漪颜色默认为当前元素的前景色叠加 12% 不透明度。

---

## 实际应用

**Gmail 与 Google Drive 的 FAB 按钮**：浮动操作按钮是 Material Design 最具标志性的组件之一。Gmail 的红色撰写（Compose）按钮固定于屏幕右下角，海拔为 6dp，悬浮于内容层之上，代表页面上最主要的一个操作。这与 iOS 将主操作放置于导航栏的逻辑截然不同。

**Google Maps 的分层卡片**：底部抽屉（Bottom Sheet）在 Maps 中承载搜索结果与地点详情，用户向上滑动时卡片海拔从 8dp 变化，并通过动画展示更多内容。这种交互模式严格遵循纸片"展开"的空间隐喻，而非凭空出现的弹窗。

**Material Design 的跨平台落地**：Google 开源了 **Material Components for Android（MDC-Android）**、**Material Web Components** 以及 Flutter 的 Material 主题包，使开发者可以直接调用规范定义的组件代码，而非仅依赖设计师的视觉稿来还原效果，实现了"设计即代码规范"的工作流。

---

## 常见误区

**误区一：认为 Material Design 就是"卡片 + 阴影"风格**
很多人将 Material Design 简化为"加阴影的卡片界面"。实际上，阴影只是海拔系统的视觉表现之一，Material Design 更核心的是运动物理规范与交互反馈机制。一个界面可以使用 Material 的动画曲线、涟漪效果与色彩体系，但完全不使用卡片布局，依然是合规的 Material Design 实现。

**误区二：以为 Material Design 规范是一成不变的固定标准**
Material Design 自 2014 年发布以来已经历了三个主要版本迭代（M1、M2、M3）。许多设计师至今仍在沿用 2014 年版的海拔规则与组件样式，而 Material You（M3）已将 FAB 的形态、色彩逻辑与组件尺寸做了大幅修改。使用过时版本的规范去评判当前 Google 产品的设计决策，会得出错误结论。

**误区三：将 Material Design 等同于 Android 专属规范**
Material Design 从设计之初就被定位为"跨平台设计语言"，Google 的 Web 产品（如 Google Docs、Workspace）同样遵循该规范。但在 iOS 平台上，Google 官方应用通常会做平台适配，例如将导航逻辑改为符合 iOS 惯例的 Tab Bar，而非强制使用 Navigation Drawer——这种做法本身也是 Material Design 规范的明确建议。

---

## 知识关联

学习 Material Design 需要先理解**拟物设计与扁平化设计**的演变历史：Material Design 的纸张隐喻直接吸收了拟物设计对物理世界的参照逻辑，同时保留了扁平化设计反对过度装饰的简洁主张，海拔系统是两种思路的折中产物。

掌握 Material Design 之后，学习 **iOS Human Interface Guidelines（HIG）** 时会形成强烈的对比感知——HIG 强调"平台原生感"与内容优先，明确反对在 iOS 上使用 Material 式的导航抽屉；而 Material Design 以"物理模型"作为设计决策的底层逻辑，两套体系的根本差异在于各自的认知隐喻不同。

Material Design 也是理解**设计系统（Design System）**的最佳切入案例：它包含设计原则、组件库、标注规范与代码实现四个层次，是目前公开文档最完整的工业级设计系统之一，Google 官方文档地址为 m3.material.io，可作为设计系统构建方法论的参考蓝本。