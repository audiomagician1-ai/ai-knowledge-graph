---
id: "3da-prop-pivot-setup"
concept: "道具Pivot设置"
domain: "3d-art"
subdomain: "prop-art"
subdomain_name: "道具美术"
difficulty: 1
is_milestone: false
tags: ["引擎"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 道具Pivot设置

## 概述

Pivot（轴心点）是3D道具模型的旋转、缩放和定位的基准坐标原点。在3D软件中，每个道具模型都拥有一个Pivot点，当游戏引擎或动画系统对该物体执行变换操作时，所有计算均以此点为参照中心展开。例如，一把门的Pivot若放置在铰链位置，门在旋转时才能像真实世界一样绕合页转动；若Pivot误放在门板中央，则门会以中心为轴旋转，完全失去现实意义。

Pivot的概念在早期3D工作流中（约1990年代随3ds Max等软件普及）就已是建模基础规范之一。游戏美术工业化流水线形成后，Pivot设置逐渐从个人习惯演变为团队强制标准，因为引擎（如Unity、Unreal Engine 4/5）在导入FBX文件时会直接读取模型的原点坐标作为Pivot依据。一旦Pivot设置错误，程序员在脚本中调用`transform.Rotate()`或蓝图节点旋转物体时，所有偏移量都需要额外代码补偿，极大增加开发成本。

对于难度仅为1/9的入门知识点，Pivot设置的规则相对固定，但理解**为什么**这样设置，需要结合道具的具体功能用途来判断——这正是本文档的核心目标。

---

## 核心原理

### 1. Pivot的三种标准放置位置

道具Pivot的放置位置并非随意，而是遵循三条明确规律：

- **底部中心（Bottom Center）**：适用于静态摆放类道具，如箱子、木桶、桌椅。Pivot置于模型包围盒底面的几何中心，坐标通常表示为 `(0, 0, 0)`（Y轴朝上时Y=0即底面）。这样引擎在将道具放置到地面时，只需将Pivot对齐地面坐标即可，无需额外偏移。
- **功能旋转轴（Functional Rotation Axis）**：适用于有开合或旋转动作的道具，如门、抽屉、瓶盖、旋转机关。Pivot必须放置在实际物理铰接点上，而非几何中心。
- **世界原点对齐（World Origin）**：适用于建筑附属构件或需要与关卡坐标精确对齐的大型道具（如地板砖、墙板模块），Pivot放置在 `(0, 0, 0)` 以便在关卡编辑器中进行网格吸附（Grid Snap）。

### 2. 软件操作：如何移动Pivot而不移动网格

在3ds Max中，移动Pivot使用**Hierarchy面板 > Affect Pivot Only**按钮，激活后移动操作仅作用于轴心点，网格顶点位置不变。在Maya中，对应操作是按住 `D` 键拖动Pivot手柄，或使用 `Modify > Center Pivot` 将Pivot自动归位到包围盒中心。在Blender中，可通过 `右键 > Set Origin` 菜单选择`Origin to Geometry`（几何中心）或`Origin to 3D Cursor`（自定义位置）。

**注意**：上述操作改变的是Pivot在模型局部空间中的位置，不会影响顶点数据本身，因此不会破坏UV展开或顶点法线。

### 3. 导出时Pivot的行为规则

在将模型导出为FBX格式送入Unity或Unreal时，模型的**世界空间原点**即为引擎读取的Pivot位置。因此，最佳实践是：导出前将道具的Pivot移至目标位置后，执行**"重置变换"**（Reset XForm / Freeze Transformations），使模型的局部坐标原点与世界原点对齐，再导出。Unity中若发现道具存在非预期旋转偏差，根本原因99%是导出前未冻结变换矩阵（Transform Matrix未归零）。

---

## 实际应用

**案例1：宝箱道具**
一个游戏中的宝箱需要实现开盖动画。正确做法是将箱盖（Lid）单独作为一个子模型，其Pivot设置在箱盖与箱体的连接边中心（即铰链所在位置）。箱盖绕X轴旋转-110°即可呈现完全打开状态。若Pivot在箱盖几何中心，旋转-110°后箱盖会穿插进箱体内部，产生模型穿模错误。

**案例2：武器道具（剑）**
剑的Pivot应设置在握柄底部（剑柄尾端），而非剑身重心。原因是角色动画系统会将剑的Pivot对接到骨骼手部插槽（Socket）上，握柄底部对齐手骨的坐标后，整把剑自然落入角色手掌，不需要额外的位置偏移调整。

**案例3：道路/地板模块化道具**
模块化地板砖（如1米×1米标准单元）的Pivot应设置在砖块的某一角落（如左下角），使相邻模块可以通过坐标递增的方式（`x+1`, `z+1`）精确拼接，不产生缝隙。

---

## 常见误区

**误区1："Pivot放在几何中心总是对的"**
`Affect Pivot Only` + `Center to Object`是软件默认操作，初学者倾向于对所有道具执行此操作。然而对于门、抽屉等旋转道具，几何中心与铰接点不重合，结果是动画完全错误。Pivot位置取决于**道具的功能行为**，而非几何形状的数学中心。

**误区2："Pivot不影响静态道具，可以随意设置"**
即使是完全静态（不参与动画）的道具，Pivot也直接影响关卡编辑器中的缩放操作结果。例如一根柱子Pivot在顶部，美术在场景中对其执行Y轴缩放时，柱子会向上延伸而非向下，导致柱子底部悬空，需要重新手动对齐地面，效率极低。

**误区3："建模时可以在引擎里再修改Pivot"**
Unity的Inspector面板不提供直接修改Pivot的功能（仅支持修改`Center/Pivot`显示切换，影响的是Gizmo显示而非实际原点）。Unreal Engine同样在导入后不建议修改原始Pivot，否则会影响已经放置在关卡中的所有该道具实例的位置一致性。Pivot必须在**建模阶段**正确设定。

---

## 知识关联

**前置知识：道具美术概述**
了解道具的分类（交互类、静态类、模块化类）是判断Pivot放置位置的前提——不同类型道具对应不同的Pivot标准，本文的三条位置规律直接来源于这套分类体系。

**延伸至引擎工作流**
掌握Pivot设置后，后续学习**道具FBX导出规范**（包括单位设置、坐标轴方向Y-up/Z-up的转换）时会直接用到Pivot冻结变换的操作步骤。同时，理解Pivot也是后续学习**Socket（插槽）系统**和**道具骨骼绑定**的前置操作基础，因为Socket本质上是在角色骨骼上定义一个坐标点，道具的Pivot需要与该点对应才能实现正确的手持或装备效果。