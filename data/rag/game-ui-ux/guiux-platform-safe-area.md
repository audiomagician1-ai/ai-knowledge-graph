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

平台安全区域（Platform Safe Zone）是指屏幕上能够保证UI元素完整显示、不被遮挡或裁切的矩形区域。由于不同显示设备存在物理边框、软件遮挡层或屏幕曲率等差异，游戏开发者必须将所有关键UI元素（血条、小地图、对话框、操作提示等）限制在这个安全矩形范围内渲染。

安全区域问题最早在CRT电视时代就已出现。1950年代的广播电视标准定义了"动作安全区"（Action Safe Area，屏幕面积的90%）和"字幕安全区"（Title Safe Area，屏幕面积的80%），因为CRT显像管的过扫描（Overscan）会将图像边缘4%至8%的内容推到物理边框之外。这一传统延续至今，PlayStation和Xbox平台至今仍要求UI强制适配安全区域设置。

进入移动设备时代后，安全区域问题因iPhone X（2017年11月发布）的刘海屏设计而重新引发广泛关注。苹果引入了`safeAreaInsets`这一CSS和原生API概念，要求所有应用避免将可交互元素放置在顶部传感器凹槽（高度44pt）或底部Home指示条区域（高度34pt）之内。游戏UI若不遵守这一规范，操作按钮会被刘海遮挡，导致不可点击的严重体验问题。

## 核心原理

### 电视过扫描安全区域

过扫描（Overscan）源于CRT电视的模拟信号时代，显像管驱动电路会故意让扫描线超出可见范围以隐藏信号噪声。现代HDTV虽然多数默认关闭过扫描，但索尼PlayStation 5和微软Xbox Series平台的认证规范仍要求游戏提供"屏幕安全区域"滑动调节选项，允许玩家将UI内缩范围设置为屏幕宽高各5%至10%。

具体计算方式：若显示分辨率为1920×1080，默认安全区域通常为距离屏幕四边各5%，即左右各减去96像素，上下各减去54像素，实际可用UI区域为1728×972像素。开发者需在引擎设置中将UI摄像机的视口边距（Viewport Margin）设置为对应比例，而非直接将血量条定位到坐标(0,0)处。

### 刘海屏与打孔屏安全区域

苹果设备通过`UIView.safeAreaLayoutGuide`提供精确的安全边距，该值在iPhone 14 Pro上为：顶部59pt、底部34pt、左右各0pt（竖屏状态）。Android阵营则通过`WindowInsetsCompat.getDisplayCutout()`获取异形屏区域数据，由于Android设备碎片化严重，三星Galaxy S系列打孔屏的开孔半径约为4mm，而折叠屏展开状态下铰链区域同样需要作为"软性安全区"处理。

Unity引擎的`Screen.safeArea`属性（Unity 2017.2起支持）会返回一个`Rect`结构，包含`x`、`y`、`width`、`height`四个字段，直接给出当前设备安全区域的像素坐标。开发者应将Canvas的RectTransform锚点与`Screen.safeArea`动态绑定，而非硬编码偏移量，否则在iPhone SE（无刘海）和iPhone 14 Pro Max（深刘海）上会出现截然不同的错位效果。

### 曲面屏与折叠屏的特殊处理

三星Galaxy Edge系列的曲面屏在屏幕两侧约15至20像素区域存在视觉畸变，触控精度也低于中央区域。游戏中的技能按钮若放置在此区域，玩家误触率会显著上升，因此建议将横屏游戏的左右UI边距设置为不低于屏幕宽度的3%（约合1080p下32像素）。折叠屏在折叠状态（封面屏约2268×832分辨率）和展开状态（主屏约2208×1768分辨率）之间切换时，游戏必须监听`onConfigurationChanged`回调并重新计算安全区域，否则UI布局会在切换时产生元素重叠。

## 实际应用

《原神》在适配iPhone系列刘海屏时，将顶部状态栏（体力、时间显示）整体下移至安全区域内，同时利用刘海两侧的"犄角"区域放置装饰性背景图而非功能性按钮。这一设计将刘海视为视觉分割线而非障碍物，属于行业内常见的处理策略。

主机游戏《战神：诸神黄昏》在TV安全区域方面提供了精细的校准界面：进入设置后展示一个矩形校准图，玩家通过调整滑块直到矩形四角恰好完整可见为止，系统据此计算实际的边距百分比并存储在本地配置文件中。这符合Sony PlayStation发布认证技术要求（TRC）中R4004条款的规定。

在Unity开发中，一段典型的安全区域适配代码会在`Start()`中读取`Screen.safeArea`，计算出相对于`Screen.width`和`Screen.height`的归一化坐标（范围0到1），然后分别设置Canvas子节点RectTransform的`anchorMin`和`anchorMax`为这两个归一化值，从而使整个UI面板自动收缩到安全边界内。

## 常见误区

**误区一：认为现代4K电视不存在过扫描问题，可以跳过TV安全区域适配。**
实际上，市面上仍有相当比例的电视（尤其是价格较低的40英寸以下型号）默认开启"画面过扫描"或"全屏拉伸"模式，且许多玩家从不更改电视设置。PlayStation 4平台统计数据显示，约18%的玩家在首次进入游戏时屏幕边缘存在裁切问题，这正是平台方强制要求提供安全区域调节选项的原因。

**误区二：将全部UI元素都强制压缩进最小安全区域，导致界面过于拥挤。**
安全区域保护的是"关键交互元素"，背景装饰、全屏特效和不影响操作的视觉元素完全可以延伸到安全区域之外直至屏幕边缘，这种设计称为"出血区域"（Bleed Area）布局。血条、技能按钮、重要提示文字才是必须严格约束在安全区域内的内容，若将装饰背景也一并内缩，反而会在屏幕四周产生明显的黑边或空白感。

**误区三：iOS和Android的安全区域API返回相同格式的数据，可以共用一套代码直接读取。**
iOS的`safeAreaInsets`以pt（逻辑点）为单位，需要乘以设备的`UIScreen.scale`（通常为2或3）才能转换为实际像素；Android的`DisplayCutout`直接返回像素值，但不同厂商的实现存在偏差，部分Android 8.0以下设备甚至不支持该API，需要额外的兼容性处理分支。

## 知识关联

平台安全区域的适配工作建立在**跨平台文字输入**所形成的多平台意识基础上——理解不同平台拥有不同的输入方式，才能自然延伸到理解不同平台拥有不同的显示边界约束。掌握了安全区域的精确计算和动态适配方法后，开发者进入**主机认证要求**阶段时，会发现PlayStation的TRC和Xbox的XR（Xbox Requirements）中有多达十余条与安全区域显示直接相关的强制规则，包括字体最小尺寸、按钮最小点击区域等均以安全区域为基准参照系进行测量和验证。两个方向的知识形成完整的"多平台显示规范"体系。