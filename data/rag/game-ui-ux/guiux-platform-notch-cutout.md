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
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

异形屏适配是指在刘海屏（Notch）、打孔屏（Punch-hole）、折叠屏（Foldable）等非矩形显示区域的设备上，通过专项策略保证游戏UI元素既不被硬件遮挡、又能充分利用延伸显示面积的开发实践。与普通全面屏适配不同，异形屏适配需要精确识别"安全区域"（Safe Area）之外的"危险像素带"，并针对刘海、摄像头打孔的具体坐标位置做出动态规避或主动利用。

这一需求随着2017年iPhone X发布而进入主流视野——该设备引入了高度44pt（约132px @ 3x）的刘海区域以及底部34pt的Home指示条，迫使开发者第一次系统性地面对非矩形安全区问题。此后Android阵营在2018年推出DisplayCutout API（对应Android 9/API Level 28），正式将异形区域的坐标查询标准化。折叠屏则在2019年随三星Galaxy Fold商用后带来了铰链遮挡区（Hinge Area）这一全新挑战维度。

对于游戏UI而言，异形屏适配直接影响摇杆、血条、小地图等高频交互控件的可点击性与可读性。若血条恰好落在打孔区后方，玩家在战斗中将无法读取关键信息；若摇杆热区覆盖了Home指示条，系统手势会与游戏操作产生冲突，导致误返回桌面。

---

## 核心原理

### 安全区域（Safe Area）与环境内嵌量（Environment Insets）

iOS通过`UIView.safeAreaInsets`暴露上下左右四个方向的内嵌量（单位：点pt）。iPhone X系列设备的典型值为：顶部44pt、底部34pt、左右0pt（竖屏）；横屏时左右各为44pt，底部21pt。Unity引擎可通过`Screen.safeArea`（返回像素坐标的`Rect`）直接获取此矩形，开发者将UI Canvas的RectTransform约束到该Rect内即可实现基础避让。

Android的`DisplayCutout`对象通过`getInsets(WindowInsets.Type.displayCutout())`返回各方向的挖孔内嵌量，并额外提供`getSafeInsetTop()`等方法。与iOS不同，Android设备的打孔位置高度分散——华为Mate 40 Pro的椭圆打孔中心位于顶部约17px处，而三星Galaxy S21的打孔半径约为4.25mm，各厂商均有差异，需要在运行时动态查询而非硬编码。

### 刘海与打孔的主动利用策略

避让仅是消极策略，积极的做法是将刘海/打孔区域两侧的"耳朵"空间（Ear Area）纳入UI布局。以横屏游戏为例，iPhone X横屏时左右各有44pt × 屏幕高度的耳朵区域。常见做法是将状态栏级别的非交互信息（金币数量、网络信号）放置于此，而把摇杆、技能按钮等需要精确触控的控件限制在安全区内。

折叠屏的铰链遮挡区（Hinge Occlusion Rect）在三星设备上通过`FoldingFeature.bounds`获取（Jetpack WindowManager库）。游戏UI必须确保铰链宽度约6mm的遮挡带内不放置任何交互元素，同时可将该带两侧的双屏区域分别渲染左右操控区——左屏用于地图/技能列表，右屏用于主视角——这是折叠屏异形适配的独特机遇。

### 动态检测与分级适配逻辑

实用的异形屏适配框架通常分三个层级：
1. **零适配设备**：Insets全为0，按标准布局渲染；
2. **单边刘海/打孔设备**：顶部或侧边存在单一切口，只需单向偏移UI锚点；
3. **多区域复合设备**：同时存在打孔（顶部）＋下巴（底部）＋铰链（中部），需对每个UI组件单独注册监听器，在屏幕旋转或折叠状态改变时触发重新布局。

Unity的`Screen.safeArea`在模拟器中无法真实模拟所有Android厂商的打孔形状，因此推荐使用`Android Device Preview`插件或直接连接真机通过ADB输出`getDisplayCutoutInfo`进行验证。

---

## 实际应用

**《原神》移动端横屏布局**：该游戏将小地图固定于右上角，并在刘海屏设备上自动向左平移，确保小地图圆形图标完整显示在安全区内，同时左上角的体力值/任务名称文字会随`safeAreaInsets.left`值进行水平偏移，最大偏移量在iPhone 14 Pro上约为59pt。

**折叠屏展开态的双栏化**：三星官方推荐折叠屏展开后（内屏宽度≥600dp）将游戏UI切换为"双栏模式"，左侧面板显示技能冷却/装备栏，右侧保留游戏主画面。部分RPG已采用此方案，展开态UI的布局代码与折叠态完全分离，通过`WindowSizeClass.EXPANDED`枚举触发切换。

**打孔区碰撞体排除**：在触控层面，需将打孔区的像素矩形从触摸响应区中剔除（Android的`exclusionRects` API），防止玩家触摸到打孔区域时触发误操作——尤其对于实时战斗类游戏，该区域的误触率在未处理时可高达12%（据Google开发者文档引用的用户研究数据）。

---

## 常见误区

**误区一：用固定像素偏移代替动态Safe Area查询**。部分开发者在iPhone X上测试通过后，将顶部偏移硬编码为44pt，但该值在iPhone 14 Pro Max上为59pt（因动态岛取代了刘海），在iPad Pro上为24pt，在Android旗舰机上差异更大。正确做法是每次场景加载和屏幕旋转时重新读取`Screen.safeArea`。

**误区二：将Safe Area等同于无刘海区域，忽略底部手势条**。Safe Area底部的34pt（iPhone X系列）并不是"黑边"，而是可见但存在系统手势冲突的区域。若在此区域放置技能按钮，玩家快速下划时会触发iOS的应用切换手势，而游戏本身不会收到该触摸事件，造成技能"失灵"的体验投诉。

**误区三：认为折叠屏只需处理展开态**。折叠屏存在"半折叠态"（Tabletop Mode，铰链角度约90°至150°），此时`FoldingFeature.state`为`HALF_OPENED`，上下半屏分别可见。若游戏仅适配展开与折叠两种状态，在半折叠态下UI会出现被铰链截断的情况。

---

## 知识关联

异形屏适配建立在**跨平台字体缩放**的基础之上：当文字因字体缩放规则已经确定了基础字号和行高后，异形屏的Safe Area内嵌量会进一步压缩可用宽度，两者叠加可能使原本合适的文字在刘海横屏设备上溢出。因此字体缩放的基准Rect必须在应用Safe Area偏移之后再进行计算，执行顺序不可颠倒。

在异形屏适配完成之后，后续的**跨平台联机UI**会面临一个新问题：不同平台玩家的HUD布局因安全区差异而不同，在联机邀请、好友坐标指引等跨平台共享UI组件中，需要传递的不仅是游戏逻辑坐标，还要附带对端设备的Safe Area信息，以便接收方正确渲染指引箭头的锚点位置，避免指引箭头指向被刘海遮挡的区域。