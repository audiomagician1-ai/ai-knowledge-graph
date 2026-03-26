---
id: "figma-basics"
concept: "Figma基础"
domain: "product-design"
subdomain: "prototyping"
subdomain_name: "原型与测试"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.484
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Figma基础

## 概述

Figma是一款基于浏览器运行的矢量设计工具，于2016年由Dylan Field和Evan Wallace共同创立，2021年被Adobe以约200亿美元收购。与Sketch、Adobe XD等传统桌面工具不同，Figma将设计文件存储在云端，支持多人同时编辑同一个文件，这一特性使它迅速成为产品团队的主流协作平台。

Figma的核心功能围绕三个支柱展开：**组件系统（Components）**、**自动布局（Auto Layout）**和**原型连线（Prototyping）**。掌握这三项功能，就能完成从界面搭建到可交互原型的完整设计流程，这也是本文的核心内容。

Figma对产品设计师的重要性体现在它统一了设计与交付两个环节——设计师在Figma中绘制的每个图层都带有可导出的CSS属性，开发者通过Inspect面板可以直接读取颜色值（如#1A1A1A）、字号（如14px/1.5倍行高）和间距数值，减少了设计与开发之间的信息损耗。

---

## 核心原理

### 1. 组件系统（Components）

Figma的组件分为**主组件（Main Component）**和**实例（Instance）**。在画布上按下 `Ctrl/Cmd + Alt + K` 可将任意图层或图层组转换为主组件，随后每次复制该组件得到的都是实例。修改主组件的属性（颜色、文字、圆角等）时，所有实例会同步更新；而在单个实例上做的修改称为**覆盖（Override）**，只影响该实例本身。

组件还支持**变体（Variants）**功能，允许将按钮的Default、Hover、Pressed、Disabled四种状态封装在同一个组件集合（Component Set）中。通过在右侧属性面板切换属性，可以快速预览不同状态，而不需要在画布上放置四个独立图形。组件库（Component Library）可以发布到团队，其他成员启用后即可调用，实现设计语言的统一管理。

### 2. 自动布局（Auto Layout）

自动布局是Figma于2019年推出、2022年升级至第四版的排列系统，快捷键为 `Shift + A`。它将容器内的子元素按照**水平（Horizontal）**或**垂直（Vertical）**方向排列，并自动管理元素之间的间距（Gap）和容器内边距（Padding，分别控制上/下/左/右）。

自动布局的核心逻辑是三种尺寸模式的组合：
- **Fixed**：固定宽高，子元素不会撑开容器
- **Hug（包裹内容）**：容器大小由内部元素总和决定，适合按钮组件
- **Fill（填充父容器）**：元素自动占满父级自动布局容器的剩余空间，类似CSS的 `flex: 1`

这套逻辑与CSS Flexbox高度对应，设计师理解Auto Layout的方式也直接影响开发者能否快速还原界面。例如，一个导航栏通常设为Horizontal Auto Layout，左侧Logo设为Fixed，中间间距设为Fill，右侧操作区设为Hug，三段配合实现自适应宽度。

### 3. 原型连线（Prototyping）

切换到顶部菜单的**Prototype标签页**后，选中任意图层都会在右侧出现蓝色的连接锚点。从锚点拖拽到目标画板（Frame）即可建立一条交互连线。每条连线包含三个参数：
- **触发方式（Trigger）**：On Click、On Hover、After Delay（毫秒级延迟）等
- **动作类型（Action）**：Navigate To、Open Overlay、Scroll To等
- **过渡动效（Transition）**：Instant、Dissolve、Smart Animate（智能补间）等

其中**Smart Animate**是Figma原型连线的独特功能：只要两个画板中存在**名称相同且属性不同**的图层，切换时Figma会自动插值生成补间动画，无需手动设置关键帧。例如，将Card组件在列表页和详情页中保持相同图层命名，切换时会呈现流畅的展开效果。

---

## 实际应用

**场景一：搭建登录页面**
新建一个375×812的Frame（对应iPhone 13尺寸），使用自动布局将输入框、按钮垂直排列，设置Gap为16px、左右Padding各为24px。从组件库拖入预设的Input和Button组件，通过覆盖修改占位文字内容。整个搭建过程无需手动对齐，拖动一个元素时其他元素自动重新分布。

**场景二：制作可点击原型演示**
将登录页与主页两个Frame放在同一个Page内，切换到Prototype模式，从"登录"按钮连线至主页Frame，设置触发方式为On Click，动效选择Slide In（从右侧滑入）。点击右上角的播放按钮（`Ctrl/Cmd + P`）在浏览器中预览，即可得到一个可分享链接，产品经理和用户测试参与者无需安装任何软件即可在手机浏览器中体验该原型。

---

## 常见误区

**误区一：把Frame当Group使用**
Frame（快捷键 `F`）和Group（快捷键 `Ctrl/Cmd + G`）看起来相似，但Frame是独立的坐标容器，子元素的X/Y坐标相对于Frame计算；Group只是临时聚合，子元素坐标仍相对于整个画布。原型连线的目标只能是Frame，自动布局也只能添加到Frame上，因此养成用Frame而非Group管理界面区域的习惯至关重要。

**误区二：直接修改主组件导致全局污染**
初学者常在画布上看到某个按钮并直接双击进入主组件修改颜色，结果导致所有实例都变色。正确做法是：如果只需修改单个按钮，应在实例上通过Override修改；如果需要全局更新，才进入主组件编辑。识别主组件的方式是图层面板中图标为实心紫色菱形，而实例为空心菱形。

**误区三：自动布局嵌套层级混乱**
复杂界面往往需要多层嵌套的自动布局（如卡片内嵌列表，列表内嵌标签组）。常见错误是在子级设置了Fixed宽度后，又期望它能在父级中Fill，导致溢出或不对齐。正确做法是从外层向内层逐级建立自动布局，先确定父容器的排列方向，再设置子元素的尺寸模式。

---

## 知识关联

**与前置知识的关系**：Figma基础不依赖特定前置工具知识，但对有CSS Flexbox基础的学习者来说，Auto Layout的Hug/Fill/Fixed模式会非常直观，因为两者在水平/垂直轴上的逻辑几乎一一对应。

**通向Figma高级**：掌握本文三项基础后，下一步学习**Figma高级**将涉及变量（Variables）系统——2023年发布的Variables功能允许将颜色、数字、布尔值绑定到组件属性上，实现深色/浅色模式一键切换，以及基于条件的原型交互逻辑。

**通向线框图**：理解Figma的Frame和Auto Layout之后，绘制**线框图**时可以直接在Figma中用低保真组件（灰色色块、占位图标）搭建结构，利用自动布局保持间距一致性，而不必依赖纸笔或其他专用线框图工具。