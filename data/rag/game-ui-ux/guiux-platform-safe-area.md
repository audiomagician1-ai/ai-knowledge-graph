---
id: "guiux-platform-safe-area"
concept: "平台安全区域"
domain: "game-ui-ux"
subdomain: "multiplatform"
subdomain_name: "多平台适配"
difficulty: 2
is_milestone: false
tags: ["multiplatform", "平台安全区域"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 平台安全区域

## 概述

平台安全区域（Platform Safe Zone / Safe Area）是指屏幕上能够确保所有关键UI元素完整显示、不被遮挡或裁切的可用矩形区域。在游戏UI设计中，这一概念源于早期电视机的**过扫描（Overscan）**问题——CRT电视为了掩盖信号边缘的噪点，会将画面向外扩展5%到15%，导致屏幕四边实际显示区域小于内容分辨率。这意味着如果把HUD元素放在画面角落，玩家可能根本看不到血量条或小地图。

进入现代显示设备时代后，安全区域的挑战形式发生了转变，但问题本身并未消失。智能手机的刘海屏（Notch）、打孔屏、胶囊形摄像头区域，以及电视、曲面显示器的物理曲率和边框设计，都会对UI的可见性产生实质影响。索尼、微软和任天堂的平台认证要求中均明确规定了安全区域合规标准，开发者若违反这些规定将无法通过上架审核。

## 核心原理

### 电视过扫描安全区域的数值标准

传统广播标准将安全区域分为两个层级：**动作安全区**（Action Safe Area）保留画面外边缘约5%的缓冲，**字幕安全区**（Title Safe Area）则保留约10%。这意味着在1920×1080的分辨率下，字幕安全区的实际可用区域为约**1728×864像素**（左右各减96像素，上下各减108像素）。PlayStation和Xbox的UI指南均建议将所有文本和关键图标置于距离屏幕边缘至少5%的内缩区域。部分老式电视过扫描可达**15%**，因此一些保守的游戏会将核心信息限制在画面中央70%的区域内。

### iOS与Android的刘海屏安全区域机制

iOS 11起，苹果引入了 `safeAreaInsets` API，以UIKit属性形式暴露四个方向的安全内缩值（top、bottom、left、right），单位为逻辑像素pt。iPhone X的刘海高度为**44pt**，底部Home Bar（虚拟指示条）占用**34pt**，这两段区域不应放置可交互的游戏UI按钮。在横屏模式下，刘海位于左侧或右侧，此时左侧或右侧的 `safeAreaInsets` 值会变为**44pt**，导致横版游戏的摇杆、操作按钮必须相应偏移。Android的 `WindowInsets.getDisplayCutout()` API（Android 9.0 / API 28起可用）提供了类似机制，但由于Android碎片化，不同厂商的开孔形状（水滴形、角落打孔、条形刘海）差异极大，需要测试不低于主流的10种屏幕形态。

### 曲面屏与折叠屏的特殊处理

三星Galaxy Edge系列和部分电视的曲面设计会使屏幕两侧边缘的视觉畸变达到**5°到12°**，颜色和对比度在极端曲率处明显下降，即便像素点可以显示，用户的实际阅读体验也会受损。工程上的处理方式是将曲面屏的安全区域**额外向内缩进约3%到5%**，并避免在边缘区域放置小号文字（建议字号不低于18sp）。折叠屏设备如三星Galaxy Z Fold系列展开后的内屏比例为**7.6英寸约22.5:18**，接近正方形，游戏UI布局需要监听 `FoldingFeature` 的状态变化，在折叠和展开两种形态下分别维护不同的安全区域配置。

## 实际应用

**主机游戏的安全区偏移校准界面**：许多TV平台游戏（如《黑暗之魂》系列和《赛博朋克2077》）在首次启动时提供一个"安全区域校准"界面——屏幕上显示一个细边框矩形，要求玩家调整偏移量直到四条边完全可见。这一功能直接对应了老旧电视的过扫描问题，校准值通常以百分比存储，范围0%（无内缩）到15%（最大内缩），对应实际像素偏移会在运行时按当前分辨率换算。

**Unity与Unreal的安全区域组件**：Unity提供了 `Screen.safeArea` 属性，返回一个 `Rect` 结构，包含x、y起始坐标及宽高，开发者需要将Canvas的RectTransform锚点对齐到这个Rect内部而非全屏。Unreal Engine则通过 `GetDisplayMetrics` 和 `FDisplayMetrics::TitleSafePaddingSize` 在C++侧获取TV安全区偏移，同时支持 `USafeZone` 控件在UMG中自动处理刘海偏移。

**微信小游戏的胶囊按钮避让**：微信的右上角"胶囊按钮"（菜单+关闭的组合控件）尺寸固定为**87×32pt**，距右边距**7pt**，开发者需调用 `wx.getMenuButtonBoundingClientRect()` 获取其精确坐标，并据此将游戏内暂停按钮、设置图标等下移至胶囊按钮下方，避免遮挡或误触。

## 常见误区

**误区一：在高分辨率现代电视上不需要考虑安全区域**。实际上，智能电视的操作系统（如三星Tizen、LG webOS）本身会将游戏画面缩放显示，加之用户的电视图像模式（"放大"、"全景"等）会触发硬件级过扫描，即便游戏输出的是4K信号，最终显示在屏幕上的内容也可能被裁切。Xbox Series认证要求（TCR）明确要求TV游戏必须实现安全区域偏移功能，即使在HDMI直连情况下。

**误区二：安全区域只影响UI层，游戏内容可以延伸到全屏**。这一理解在大多数情况下正确——背景美术和游戏世界延伸到全屏出血区（bleed area）是惯常做法。但对于包含**可点击环境元素**（如RPG中的对话NPC、解谜游戏的互动物件）的游戏，若这些元素的点击热区落入刘海遮挡区域或曲面屏边缘畸变区，会导致点击无响应或触发系统级手势，必须将交互元素的有效区域限制在安全区域内部。

**误区三：iOS和Android的安全区域API返回值是像素单位**。iOS的 `safeAreaInsets` 返回的是**逻辑点（pt）**，Android的 `WindowInsets` 返回的是**物理像素（px）**，两者的单位体系不同。在跨平台引擎中混用这两套数值而不做设备像素比（DPR）转换，会导致高DPI设备上安全区偏移量错误地扩大2到3倍，表现为UI元素被过度推向屏幕中央。

## 知识关联

平台安全区域的理解建立在**跨平台文字输入**的基础上——当软键盘弹出时，iOS和Android会进一步压缩可用的安全区域高度（软键盘的高度通过 `keyboardHeight` 事件动态获取），此时游戏UI的布局必须同时响应两套动态变化：安全区insets和键盘遮挡区。掌握安全区域的处理机制后，下一步自然进入**主机认证要求**的学习，索尼PlayStation的TRC（Technical Requirements Checklist）和微软Xbox的TCR对安全区域的具体技术实现提出了明确的合规条款，包括安全区偏移的精度要求（±1%以内）、UI元素的最小尺寸限制以及默认偏移值的规定，这些认证条款是安全区域理论在商业发行流程中的直接落地形式。