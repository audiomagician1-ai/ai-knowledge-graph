---
id: "guiux-platform-notch-cutout"
concept: "异形屏适配"
domain: "game-ui-ux"
subdomain: "multiplatform"
subdomain_name: "多平台适配"
difficulty: 3
is_milestone: false
tags: ["multiplatform", "异形屏适配"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 异形屏适配

## 概述

异形屏适配是指在游戏UI/UX设计中，针对刘海屏（Notch）、打孔屏（Punch-hole）、折叠屏（Foldable）等非矩形显示区域，制定UI元素的主动避让与空间利用策略。与传统全矩形屏幕不同，异形屏存在硬件遮挡区域，若不处理，HUD元素、操作按钮、关键文字可能直接被刘海或摄像头打孔区域覆盖，导致信息缺失或误触。

异形屏概念最早随2017年iPhone X的"刘海"设计进入主流市场，苹果同期推出了Safe Area（安全区域）API概念，要求开发者将关键UI限制在`safeAreaInsets`定义的矩形内。Android阵营则在2018年Android P（9.0）通过`DisplayCutout` API正式规范化缺口屏适配，定义了`LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES`、`NEVER`、`DEFAULT`三种缺口处理模式。折叠屏则更晚，三星Galaxy Fold于2019年上市，带来铰链区域（Hinge Area）的额外遮挡问题。

在游戏场景中，异形屏适配比普通App更复杂：游戏往往全屏渲染，不依赖系统状态栏给出的安全边距，引擎层必须主动查询设备缺口数据并动态调整UI锚点。忽视适配的游戏会出现虚拟摇杆被刘海遮挡、技能图标嵌入摄像头孔、折叠展开后UI布局错乱等具体问题。

---

## 核心原理

### 安全区域（Safe Area）的获取与坐标映射

安全区域是设备操作系统暴露给应用的"可用矩形"，以四边内边距（insets）描述遮挡量。在Unity中，通过`Screen.safeArea`返回一个`Rect`结构，包含`x`、`y`、`width`、`height`四个字段，单位为屏幕像素。以iPhone 14 Pro为例，其动态岛（Dynamic Island）导致顶部safe area约为59点（@3x分辨率约177px）。开发者需将UI Canvas的锚点从四角（0,0,1,1）收缩至safe area对应的归一化坐标，公式为：

```
anchorMin.x = safeArea.x / Screen.width
anchorMin.y = safeArea.y / Screen.height
anchorMax.x = (safeArea.x + safeArea.width) / Screen.width
anchorMax.y = (safeArea.y + safeArea.height) / Screen.height
```

这套坐标映射必须在每次`Screen.safeArea`数值变化时重新执行，而非仅在启动时执行一次，因为折叠屏展开/收起会实时改变该数值。

### 刘海与打孔区域的三种处理模式

面对遮挡区域，游戏UI设计存在三种策略，而非只有"躲开"一种：

**完全避让模式**：所有可交互UI（摇杆、按钮、菜单）均置于safe area内部。背景图、天空盒、场景渲染延伸至全屏出血边（Bleed Edge），视觉上填满刘海两侧的"耳朵区"，但无任何可点击元素进入该区域。这是策略类、MMORPG类游戏的主流做法，因为这类游戏HUD密集，误操作代价高。

**装饰性利用模式**：将刘海/打孔周围区域填充非交互性装饰UI，例如将状态栏数值（金币、时间）的背景条延伸至刘海两侧，利用视觉欺骗让异形区域"融入"UI框架。《原神》PC版移植移动端时采用了类似策略，在顶部状态栏背景延伸覆盖刘海区域，形成连续的HUD背景带。

**主动占用模式**：在打孔屏上，如果孔径小于8mm（如三星Galaxy S23的3.4mm打孔），部分游戏选择将打孔视为装饰元素，在其周围排布计时器或小型图标，形成"环绕摄像头"的UI布局。此模式风险较高，需精确测量各机型孔径数据。

### 折叠屏的双状态布局适配

折叠屏引入了"折叠态"与"展开态"两套完全不同的显示规格，以三星Galaxy Z Fold5为例：折叠态外屏为6.2英寸、916×2316分辨率，展开态内屏为7.6英寸、1812×2176分辨率，长宽比从约2.5:1骤变为约1.2:1。这意味着游戏UI需要维护两套完全独立的布局方案。

Android通过`WindowInfoTracker`和`FoldingFeature`API通知应用折叠状态变化，Unity 2021.2+通过`Screen.width/height`变化事件触发重新布局，Unreal Engine则需要在`GameViewportClient`中监听视口尺寸变化。关键在于铰链区域（Hinge）本身不可触控且存在显示折痕，其宽度约为2.5mm，开发者必须在展开态中将这一区域标记为禁止放置交互元素的"死区"。

---

## 实际应用

**横版动作游戏的摇杆避让**：以《帕斯卡契约》为代表的横屏手游，将虚拟左摇杆的热区中心锚定在距屏幕左边缘`safeArea.x + 120px`处，而非固定的左边缘固定偏移。这样无论设备刘海方向如何（横屏时刘海在左侧），摇杆始终出现在可触控区域内，避免了左手拇指触控被刘海遮挡识别失败的问题。

**竖屏卡牌游戏的顶部状态栏延伸**：对于竖屏游戏，顶部状态栏（显示血量/费用）背景色块需延伸至屏幕顶部绝对边缘，形成"出血"，而文字和图标仅放置在safe area内。具体实现是将背景Panel的`anchorMax.y`设为1.0（全屏顶），而其子元素文字的`anchorMax.y`使用安全区域计算值，两层分离控制。

**折叠屏RPG的双布局切换**：折叠屏展开后，原本为竖屏设计的UI（单列菜单、居中对话框）在接近正方形屏幕上显得失衡。推荐的解法是在展开态自动切换为"平板双栏布局"：左侧展示角色/地图，右侧展示对话/菜单，以`FoldingFeature.state == FLAT`为触发条件。

---

## 常见误区

**误区一：用固定像素偏移代替Safe Area查询**。许多开发者在首款机型调试后，将刘海高度硬编码为88px（某款iPhone的刘海高度），导致在不同刘海深度的Android机型上出现偏差。正确做法是每帧或每次方向变化时动态查询`Screen.safeArea`，不同机型的缺口高度从28px（小刘海）到132px（早期宽刘海）不等，硬编码无法覆盖。

**误区二：认为横屏游戏无需刘海适配**。横屏时，刘海出现在屏幕左侧或右侧（取决于旋转方向），恰好是虚拟摇杆和操作按钮的默认放置区域。许多开发者仅对竖屏做了safe area处理，横屏时沿用固定左右边距，导致横屏刘海直接覆盖摇杆热区。

**误区三：折叠屏只需缩放现有布局**。对折叠屏展开态单纯等比缩放竖屏UI，会使所有元素过小且居中堆叠，无法利用展开后新增的横向空间。折叠屏展开态需要独立布局设计，而非缩放变换，这是结构性问题，不是缩放问题。

---

## 知识关联

异形屏适配建立在**跨平台字体缩放**的基础上——字体缩放解决了不同DPI下文字大小的一致性，而异形屏适配进一步解决了这些经过正确缩放的文字"放在哪里"的位置问题。已完成字体缩放的系统通常以逻辑分辨率（如dp/pt）为单位管理UI，这与safe area的归一化坐标计算天然兼容，可直接复用坐标转换管线。

掌握异形屏适配后，下一步将进入**跨平台联机UI**的设计。联机UI涉及实时延迟显示、跨平台玩家标识、平台专属邀请界面等元素，这些新增UI组件同样必须遵守异形屏的safe area约束，并在折叠屏双状态下保持可用性。异形屏适配建立的"动态安全区域查询+双布局方案"架构，将直接承载联机UI组件的布局决策。