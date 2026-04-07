# 布局引擎

## 概述

布局引擎（Layout Engine）是UI系统中负责将声明式约束规则转化为像素级位置与尺寸数值的算法模块。其输入是一棵携带样式属性的节点树（每个节点描述"希望如何排列"），输出是每个节点在屏幕坐标系中的最终矩形区域（x, y, width, height）。与锚点定位系统要求开发者手写每个元素的坐标不同，布局引擎在运行时动态计算结果，使背包格子从32格扩展到256格、对话框文本从两行变为十行时，容器能无缝自适应，无需任何代码介入。

布局引擎的算法体系主要源自Web标准。CSS Flexbox规范由W3C于2009年发布第一个草案（Working Draft），经历多次迭代后于2012年定稿为现代版本（W3C Candidate Recommendation）；CSS Grid Layout则于2017年3月正式成为W3C推荐标准（Recommendation）。游戏引擎随后将这些算法移植到各自的UI框架：Unity的UI Toolkit底层采用 **Yoga** 引擎——由Facebook在2016年开源的C++实现的Flexbox算法库，同时被React Native和Litho所使用；Unreal Engine的UMG系统则在其`SBoxPanel`、`SGridPanel`等Slate组件中内置了类似的线性与网格布局计算逻辑（Epic Games, UE5 Slate Architecture Docs）。

理解布局引擎在游戏UI工程中的价值，需要认识到现代移动游戏面临的分辨率碎片化问题：Android平台存在从4:3到21:9的数十种常见宽高比，iOS设备从iPhone SE的375×667逻辑点到iPad Pro的1024×1366逻辑点跨度极大。布局引擎将"元素如何排列的规则"与"元素最终坐标的结果"彻底分离，这一设计原则直接来源于CSS的盒模型（Box Model）与正常流（Normal Flow）理念（Bert Bos & Håkon Wium Lie, CSS: The Definitive Guide, 2023）。

---

## 核心原理

### Flexbox的单轴自由空间分配算法

Flexbox沿**主轴（main axis）**线性排列子元素，算法核心是自由空间（free space）的计算与分配。设容器主轴尺寸为 $C$，第 $i$ 个子元素的基础尺寸为 $b_i$，外边距总和为 $m_i$，则：

$$\text{free\_space} = C - \sum_{i=1}^{n}(b_i + m_i)$$

当 $\text{free\_space} > 0$ 时，引擎遍历所有 `flex-grow` 值 $g_i \neq 0$ 的子元素，按比例分配多余空间：

$$\Delta w_i = \text{free\_space} \times \frac{g_i}{\sum g_j}$$

当 $\text{free\_space} < 0$ 时，按收缩因子加权比例收缩，第 $i$ 个元素的缩减量为：

$$\Delta w_i = |\text{free\_space}| \times \frac{g^{\text{shrink}}_i \cdot b_i}{\sum_j (g^{\text{shrink}}_j \cdot b_j)}$$

这里收缩计算使用 $\text{flex-shrink} \times \text{flex-basis}$ 作为权重，而非单独使用 `flex-shrink`，目的是让基础尺寸更大的元素承担更多收缩量，避免小元素被压缩至负宽度。Yoga的C++源码（`YGNode.cpp`）中通过多轮冻结（freeze）迭代处理 `min-width`/`max-width` 约束冲突：当某元素因 `min-width` 限制无法继续收缩时，该元素被冻结，剩余自由空间在未冻结元素中重新分配，直至所有冲突解决或自由空间耗尽。

**换行决策**发生在测量阶段（Measure Pass）：当 `flex-wrap: wrap` 开启时，算法沿主轴逐一放置元素，累计占用宽度超过容器宽度时另起一行（line），形成多条交叉轴行。每行独立执行自由空间分配，多行之间再由 `align-content` 决定如何分配剩余的交叉轴空间。最终坐标的写入发生在布局阶段（Layout Pass），严格晚于测量阶段。

### 网格布局的双轴轨道系统

CSS Grid将容器划分为由**行轨道（row tracks）**和**列轨道（column tracks）**构成的二维结构。Unity UGUI的 `GridLayoutGroup` 是其简化实现，使用固定轨道尺寸：所有格子的 `cellSize` 相同，第 $n$ 个子元素（从0计）的列号与行号为：

$$\text{col} = n \bmod N_{\text{col}}, \quad \text{row} = \left\lfloor \frac{n}{N_{\text{col}}} \right\rfloor$$

对应的左上角像素坐标为：

$$x = x_{\text{start}} + \text{col} \times (w_{\text{cell}} + s_x), \quad y = y_{\text{start}} + \text{row} \times (h_{\text{cell}} + s_y)$$

其中 $s_x, s_y$ 分别是水平与垂直方向的 `spacing`。

CSS Grid的完整规范则支持弹性轨道单位 `fr`（fraction unit）：$1\text{fr}$ 代表可用空间的一份份额，其分配逻辑与 `flex-grow` 相似，但在Grid中轨道尺寸由 `minmax(min, max)` 函数约束，算法在满足所有 `min` 约束后再按 `fr` 比例分配剩余空间。

### 堆栈布局（Stack Layout）与Z轴叠加

堆栈布局（如Unity UI Toolkit中的 `VisualElement` 默认绝对定位模式，以及Unreal的 `SOverlay`）将子元素沿Z轴叠放于同一矩形区域。其布局计算本质上不沿主轴分配空间，每个子元素的位置由其自身的 `top`、`left`、`right`、`bottom` 属性相对于父容器计算，容器自身尺寸由最大子元素包络决定（或由明确指定的尺寸覆盖）。堆栈布局是游戏UI中血条覆盖头像、弹窗遮罩覆盖主界面的标准技术手段。

### 约束求解器：Cassowary算法

Apple的AutoLayout（iOS UIKit）和部分跨平台UI框架（如Flutter早期研究方向）采用Cassowary线性约束求解器（Badros & Borning, 2001），其思路截然不同于Flexbox的单轮分配：开发者声明任意元素间的线性等式/不等式约束（如"A的右边 = B的左边 + 8pt"），求解器以单纯形法（Simplex Method）的变体求解方程组，输出所有元素坐标。Cassowary的时间复杂度在约束数量线性增长时表现为均摊 $O(n)$，但常数项较大，因此iOS UIKit在约束数量超过约100条时常见性能警告。游戏引擎通常不采用此方案，而倾向于结构更简单、性能更可预测的Flexbox/Grid轨道分配模型。

---

## 关键方法与公式

### 测量-布局两阶段协议

几乎所有布局引擎均采用两阶段协议（Two-Pass Protocol）：

1. **测量阶段（Measure / Intrinsic Size Pass）**：自下而上遍历节点树，每个叶节点报告其"固有尺寸"（如文本节点根据字体和内容长度计算所需宽高），父节点在收到所有子节点固有尺寸后计算自身所需尺寸，直至根节点获得整棵树的尺寸需求。

2. **布局阶段（Layout / Placement Pass）**：自上而下遍历，根节点获得实际分配尺寸（通常等于屏幕尺寸），依次按Flexbox/Grid算法向子节点分发具体的 `(x, y, w, h)` 矩形。

Unity UI Toolkit的 `IVisualElementScheduler` 在帧开始时批量执行脏标记（dirty flag）触发的重新布局，仅对标记了 `LayoutDataVersion` 改变的子树重新运行两阶段计算，避免全树重算带来的性能开销。

### 脏标记传播策略

当某节点的尺寸或样式发生变化时，布局引擎不立即重算，而是向上传播脏标记直至最近的**布局边界（Layout Boundary）**节点，在下一帧批量处理。UGUI中 `Canvas` 即是一个布局边界：子 `RectTransform` 的改变不会触及其他 `Canvas` 下的元素，每个Canvas独立批量重建其布局数据（Unity Technologies, UGUI Source Code, 2022）。

### 示例：Flexbox换行背包格子

例如，在Unity UI Toolkit中实现一个自适应宽度的背包格子容器：

```css
/* USS样式 */
.inventory-container {
    flex-direction: row;
    flex-wrap: wrap;
    align-content: flex-start;
    width: 100%;
    padding: 8px;
}

.item-slot {
    width: 64px;
    height: 64px;
    margin: 4px;
    flex-shrink: 0;   /* 禁止格子收缩，保持固定64px */
    flex-grow: 0;     /* 禁止格子拉伸 */
}
```

当容器宽度为340px时，每行可容纳 $\lfloor (340 - 16) / (64 + 8) \rfloor = 4$ 个格子；当设备切换为横屏宽600px时，每行自动容纳 $\lfloor (600 - 16) / 72 \rfloor = 8$ 个格子。全程无需任何C#脚本计算坐标，布局引擎自动完成重排。

---

## 实际应用

### 游戏UI中的典型布局场景

**技能栏（Skill Bar）**：使用 `flex-direction: row` + `justify-content: space-between`，使技能图标在任意屏幕宽度下等间距分布，是Flexbox `justify-content` 属性最直接的应用。

**属性面板（Stat Panel）**：标签列（左对齐）与数值列（右对齐）可用CSS Grid的双列布局实现，`grid-template-columns: auto 1fr` 使标签列收紧至内容宽度，数值列占据剩余空间。在UGUI中等价实现需要两个并排的 `VerticalLayoutGroup` 共同填满一个 `HorizontalLayoutGroup`。

**对话气泡（Dialog Bubble）**：文本内容长度动态变化，气泡背景需随文本自动撑开。UI Toolkit中将容器设为 `width: auto`（自适应内容），配合 `max-width` 限制最大宽度，`white-space: normal` 允许换行，测量阶段的文本测量（`MeasureMode.AtMost`）会返回实际渲染所需高度，驱动气泡背景正确缩放。

**响应式主界面**：采用 `@media` 查询等价物（UI Toolkit中的 `StyleSheet` 条件规则，或Unreal的 `DPI Scaling` 规则），在宽屏设备显示侧边栏布局（Grid双列），在窄屏设备折叠为单列垂直堆栈，无需维护两套VisualTree。

### 性能敏感的布局优化

布局引擎的主要性能瓶颈集中在以下三点：

1. **频繁触发全树重布局**：在Update中每帧修改子元素尺寸会导致每帧重算，应批量修改后在帧末统一触发。
2. **嵌套Flex容器的多轮测量**：当内层Flex容器需要从外层继承自由空间时，Yoga可能触发多次测量Pass（worst case $O(n^2)$），应尽量将深度控制在3层以内。
3. **文本测量的高代价**：字符串渲染尺寸需调用字体系统计算，是布局中代价最高的单次操作，应对不变文本缓存测量结果（`ITextHandle` 缓存机制）。

---

## 常见误区

**误区一：将 `flex-grow: 1` 等同于"占满剩余空间"**  
`flex-grow: 1` 仅表示该元素参与自由空间分配且权重为1。若所有兄弟元素均设置 `flex-grow: 1`，则每人平分自由空间——不是"某元素占满"，而是"所有人等量扩张"。要让单个元素独占剩余空间，需确保其他兄弟元素 `