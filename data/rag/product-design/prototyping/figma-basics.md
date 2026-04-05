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
updated_at: 2026-03-27
---


# Figma基础：组件、自动布局与原型连线

## 概述

Figma是一款运行于浏览器的协作式界面设计工具，由Dylan Field和Evan Wallace于2012年创立，2016年正式发布公测版。与Sketch、Adobe XD等桌面端工具不同，Figma将设计文件存储于云端，多名设计师可在同一画布上实时看到彼此的光标和编辑操作，无需导出文件进行版本合并。这种实时多人协作特性使Figma迅速成为产品团队的主流设计平台，2022年Adobe宣布以约200亿美元收购（后因监管原因终止），足以说明其在行业的地位。

Figma的基础能力集中在三个核心模块：**组件（Components）**、**自动布局（Auto Layout）**和**原型连线（Prototyping）**。掌握这三个模块，设计师可以从零开始构建可交互的产品原型，并将设计规格直接交付给开发团队，无需额外的标注工具。对于产品设计师来说，Figma的学习曲线比传统工具更短，因为它将设计与原型演示合并在同一文件内，而不是分割成两个独立的软件流程。

## 核心原理

### 组件系统：主组件与实例

Figma的组件系统基于**主组件（Main Component）**与**实例（Instance）**的父子关系。在画布上按下`Option+Command+K`（Mac）或`Ctrl+Alt+K`（Windows）可将选中图层转为主组件，所有从主组件拖拽出来的复制品称为实例。修改主组件的属性（颜色、文字样式、图层结构）时，所有实例会自动同步；但若对某个实例进行了本地覆盖（Override），该实例的特定属性将不再跟随主组件变化。

组件属性（Component Properties）是Figma在2022年引入的增强功能，分为三种类型：**Boolean Property**（控制图层显隐）、**Text Property**（绑定文本内容）和**Variant Property**（切换组件变体）。例如，一个按钮组件可定义"状态"属性，包含Default、Hover、Disabled三个变体，设计师在实例面板中直接切换下拉菜单即可改变按钮外观，无需手动修改图层。

### 自动布局：响应式排列逻辑

自动布局（Auto Layout）于2019年首次推出，其核心逻辑是让容器根据内容动态调整尺寸。选中一个Frame后按`Shift+A`激活自动布局，可设置以下关键参数：

- **方向（Direction）**：水平（Horizontal）或垂直（Vertical）排列子元素
- **间距（Gap）**：子元素之间的像素间距，支持"自动"模式（类似CSS的`justify-content: space-between`）
- **内边距（Padding）**：容器四边的内缩量，支持单独设置上下左右
- **子元素对齐（Alignment）**：控制交叉轴方向的对齐方式（等同于CSS Flexbox的`align-items`）

自动布局的子元素可设置为**固定尺寸**、**填充容器（Fill Container）**（等同于`flex-grow: 1`）或**适应内容（Hug Contents）**。这套属性体系与CSS Flexbox高度对应，开发者在Figma中查看设计时，工具会自动将这些属性换算为CSS数值并显示在右侧代码面板中。

### 原型连线：交互触发与动画设置

在Figma右侧面板切换到"Prototype"选项卡后，可为任意图层添加交互连线。一条完整的连线由三部分构成：

1. **触发器（Trigger）**：如On Click、On Hover、On Drag、After Delay等
2. **目标帧（Destination）**：点击后跳转到画布上的哪个Frame
3. **动画过渡（Animation）**：包括Instant（无动画）、Dissolve（淡入淡出）、Smart Animate（智能补间）等类型

其中**Smart Animate**是Figma原型演示的核心技术：只要两个相邻帧中存在**同名且同类型**的图层，Figma会自动计算两帧之间的位置、尺寸、不透明度差异，并生成补间动画，无需手动定义关键帧。动画时长默认300毫秒，缓动曲线支持自定义贝塞尔曲线输入，格式为`cubic-bezier(x1, y1, x2, y2)`。

## 实际应用

**构建导航栏组件**：将Logo、菜单链接文字和右侧按钮放入同一Frame并激活自动布局，设置水平方向、左右两端对齐（通过将中间区域的Gap设为Auto实现）。将整个Frame转为主组件后，在不同页面拖入实例，修改主组件中的品牌色时，所有页面的导航栏会同步更新，仅需修改一处。

**制作可跳转的登录流程原型**：新建三个Frame分别代表"登录页"、"密码错误提示"和"首页仪表盘"，在登录页的"登录"按钮上连线至首页，触发器设为On Click，动画选Smart Animate，持续时间设为250ms。再从"登录"按钮连线至密码错误提示帧，触发器不变，形成分支逻辑。完成后点击右上角▶按钮即可在浏览器中演示该可交互原型，并可将演示链接分享给产品经理和开发人员，无需安装任何软件。

## 常见误区

**误区一：将主组件放在工作页面中使用**
许多初学者直接在设计页面中使用主组件本身，而不是其实例。正确做法是将所有主组件集中放置在一个单独的"组件库页面"（通常命名为`_Components`或`_Library`），在设计页面中只使用从主组件拖出的实例。若主组件与实例混放，当主组件被意外移动或修改结构时，容易造成全局样式错乱且难以排查。

**误区二：认为自动布局只能处理规则排列**
初学者常以为自动布局只适合按钮、列表等简单横排竖排场景，遇到复杂布局就手动拖拽绝对定位。实际上，自动布局框架可以嵌套使用（例如外层垂直排列，内层水平排列），并且子元素可单独设为`Absolute Position`脱离自动布局流，在容器内自由定位，类似CSS的`position: absolute`。组合这两种模式几乎可以还原任何复杂的界面布局。

**误区三：Smart Animate同名图层匹配大小写不敏感**
Smart Animate匹配两帧之间同名图层时，**图层名称严格区分大小写且必须完全一致**，例如`icon_arrow`和`Icon_arrow`会被识别为两个不同图层，导致补间动画失效，直接跳切而非平滑过渡。检查Smart Animate不生效时，第一步应在左侧图层面板逐一核对两帧中对应图层的命名。

## 知识关联

学习Figma基础不依赖任何前置工具知识，但熟悉HTML/CSS布局概念（尤其是Flexbox）的学习者能更快理解自动布局的参数含义，因为Figma的研发团队在设计自动布局时明确参照了CSS Flexbox规范。

掌握本节内容后，可以进入**Figma高级**模块，学习Variables变量系统（2023年发布，支持跨帧的数值/颜色动态绑定）、Interactive Components（组件内部状态切换原型）和组件库发布流程。同时，Figma基础也为**线框图**模块提供直接的工具支撑：理解组件和自动布局后，可以在Figma中高效搭建低保真线框图，利用现有的线框图组件套件（如Wireframe Kit）快速迭代页面结构方案。