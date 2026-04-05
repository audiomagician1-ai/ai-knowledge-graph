---
id: "3da-retopo-shrinkwrap"
concept: "ShrinkWrap投射"
domain: "3d-art"
subdomain: "retopology"
subdomain_name: "拓扑重构"
difficulty: 2
is_milestone: false
tags: ["工具"]

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
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# ShrinkWrap投射

## 概述

ShrinkWrap投射是在Blender中使用ShrinkWrap修改器（Modifier），将低面数重拓扑网格自动贴合到高精度雕刻模型表面的拓扑辅助技术。其核心机制是将编辑中的顶点沿指定方向投射到目标网格的最近表面点，免去手动逐顶点调整空间坐标的繁琐操作。该修改器自Blender 2.63版本起正式支持"最近表面点"、"投影"和"最近顶点"三种稳定投射模式，自2.80版本重写的EEVEE/Cycles渲染管线起，ShrinkWrap在视口中的实时计算性能提升约40%，成为游戏角色和影视资产拓扑重构流程的标准辅助工具。

ShrinkWrap修改器最初源于建筑可视化领域对"曲面包裹"的需求——将二维地形网格包裹到地形扫描点云，后来被角色美术师大量用于重拓扑（Retopology）场景。相比纯手动拓扑，ShrinkWrap投射能将顶点实时吸附到参考高模表面，使艺术家在连接边循环或填充多边形面时，不必担心新网格悬浮在空中或穿插进高模内部，显著降低拓扑过程中的空间对齐失误率。

本文所使用的参考资料包括Blender官方文档《Blender Reference Manual: ShrinkWrap Modifier》（Blender Foundation, 2023）以及《数字角色制作》第3版（吴亚峰，北京大学出版社，2021）中的重拓扑章节。

---

## 核心原理

### 三种投射模式的算法差异

ShrinkWrap修改器提供三种主要投射模式，底层算法各不相同，适用情形也有明显区别：

**最近表面点（Nearest Surface Point）**：对每个源网格顶点 $v$，遍历目标网格的BVH树（Bounding Volume Hierarchy），找到目标表面上欧氏距离最短的点 $p$，将 $v$ 直接移动到 $p$。数学表达为：

$$p = \arg\min_{q \in S_{target}} \|v - q\|_2$$

此模式适合整体曲率变化平缓的身体躯干、头盔外壳或背部等区域，因为"最近点"在这些区域与视觉贴合直觉高度一致。当目标表面存在深度凹陷（如腋窝、耳道内壁）时，该模式会将顶点投射到凹槽最近壁面，而非艺术家期望的正面轮廓，需手动切换其他模式或使用顶点权重遮罩。

**投影（Project）**：沿指定轴向（X/Y/Z）或法线方向进行单向或双向射线投射，类似光线追踪中的碰撞检测。修改器面板中需勾选 **Positive** 和/或 **Negative** 以控制射线朝向，并可限定 **Limit Distance**（最大投射距离，单位米）避免远处无关表面干扰。该模式常用于面部正面建模和服装平铺展开：将服装平面沿-Y轴投射到角色躯干表面，可批量贴合衣摆和袖口的顶点行。

**最近顶点（Nearest Vertex）**：将源网格每个顶点吸附到目标网格上**拓扑顶点**（而非表面插值点）中距离最近者，适合两模型拓扑密度相近时的精确对齐。当高模面数远大于低模（例如50万面高模对应8000面低模）时，该模式容易导致大量顶点堆叠在高模同一顶点处，产生网格畸变，此时应优先使用"最近表面点"模式。

### 修改器堆叠顺序与"Apply as Shape Key"

Blender的修改器堆栈按从上到下的顺序执行，ShrinkWrap修改器在堆栈中的位置对最终结果影响显著。标准角色重拓扑的推荐堆叠顺序为：

```
① Mirror（镜像）
② ShrinkWrap（表面投射）
③ Subdivision Surface（细分，可选）
```

ShrinkWrap必须放在Mirror**下方**：若顺序颠倒，Mirror会在ShrinkWrap投射后再对称，导致中线顶点偏离X=0平面，产生肉眼难以察觉但会在法线贴图烘焙时暴露的接缝错误。ShrinkWrap应放在Subdivision Surface**上方**：若顺序颠倒，细分后新增的顶点也会被投射，造成表面过度粘连，损失细分平滑效果。

完成拓扑布线后，可执行修改器面板中的 **Apply as Shape Key** 按钮，将ShrinkWrap形变存储为名为"Basis"之外的形态键，保留原始网格坐标用于后续比对；若直接点击 **Apply**，修改器结果将永久写入网格坐标，原始悬浮位置数据不可恢复。

### Offset参数与Z-Fighting控制

ShrinkWrap修改器的 **Offset** 参数（单位与场景单位一致，Blender默认为米）控制新网格距目标表面的法线偏移距离。不同资产类型的推荐值如下：

| 资产类型 | 推荐Offset值 |
|----------|-------------|
| 皮肤/裸体低模 | 0.000 m |
| 贴身服装（T恤、紧身衣） | 0.001–0.002 m |
| 宽松服装（外套、盔甲） | 0.003–0.005 m |
| 硬表面装备（护甲片） | 0.005–0.010 m |

Offset设为0时皮肤低模与高模完全重叠，用于烘焙法线贴图时投射精度最高；为服装低模设置0.002–0.005 m的偏移可避免GPU深度缓冲区精度不足引发的Z-fighting（深度冲突）。过大的Offset（超过0.01 m，在1:1真实比例场景中）会导致布料边缘翘离高模轮廓，失去参考贴合的意义，因此当场景缩放为厘米单位时，上述数值需整体乘以100。

---

## 关键操作流程

ShrinkWrap辅助重拓扑的标准操作步骤如下（以Blender 3.6为例）：

```python
# 以下为Blender Python API等效操作，用于批量设置ShrinkWrap参数
import bpy

obj = bpy.context.active_object  # 选中重拓扑目标对象（低模）

# 添加ShrinkWrap修改器
mod = obj.modifiers.new(name="ShrinkWrap", type='SHRINKWRAP')

# 指定高模为目标（需场景中存在名为"HighPoly_Head"的对象）
mod.target = bpy.data.objects["HighPoly_Head"]

# 设置为最近表面点模式
mod.wrap_method = 'NEAREST_SURFACEPOINT'

# 设置法线偏移（皮肤低模设为0）
mod.offset = 0.0

# 开启"在编辑模式中保持修改器"（关键！）
mod.show_in_editmode = True
mod.show_on_cage = True  # 开启Cage显示，顶点拖动时实时贴合
```

其中 `show_on_cage = True` 对应界面中修改器面板的"编辑模式中显示（网格笼）"按钮（铁丝笼图标），这是实现拓扑时顶点实时贴合的关键开关——若不开启，编辑模式下移动顶点时不会触发ShrinkWrap投射，顶点仅在退出编辑模式后才跳至目标表面。

---

## 实际应用案例

**案例1：角色头部重拓扑**

导入ZBrush雕刻的头部高模（约50万面，使用Decimation Master压缩至15万面后导出OBJ）作为目标对象，新建一个仅含4个顶点的平面，添加ShrinkWrap修改器（模式：最近表面点，Offset：0），开启 `show_on_cage`，进入编辑模式手动用 `E`（挤出）和 `Ctrl+R`（环切）连接眼眶、嘴角的边循环。每次挤出顶点后，修改器实时将顶点压贴到颧骨、眉弓等凹凸区域。完成全部面部布线后，最终低模面数约为4000–8000面（游戏角色头部行业标准范围），烘焙法线贴图时高低模最大偏差控制在0.5 mm以内。

**案例2：服装贴体二次拓扑**

对角色夹克衫的高模袖子（约8万面，含细密布料褶皱）进行重拓扑时，先将袖筒高模单独隔离显示，新建一个圆柱形低模（32段，24环，共约770面），添加ShrinkWrap修改器（模式：投影，轴向：法线，勾选Positive，Offset：0.002 m），再通过 `Ctrl+R` 沿袖长方向逐步增加环切线并调整走向，使布线跟随手肘弯曲方向排列。最终袖子低模约1200面，在Unity引擎中蒙皮权重绑定测试时肘部弯曲90°无明显穿插。

**思考问题**：若在上述角色头部案例中，将ShrinkWrap修改器的模式从"最近表面点"改为"最近顶点"，在高模为15万面、低模为5000面的情况下，会出现什么问题？哪些区域最先出现畸变？为什么"最近表面点"的BVH加速查询比逐顶点线性遍历在大面数高模上性能优越？

---

## 常见误区

**误区1：未开启"在编辑模式中显示网格笼"**
新手最高频的操作失误是添加ShrinkWrap后进入编辑模式，发现顶点并不贴合高模。原因是修改器面板中"显示网格笼"（Show on Cage，铁丝笼图标）默认关闭。必须同时开启"编辑模式中显示"（铅笔图标）和"显示网格笼"两个按钮，实时投射才会在编辑操作中生效。

**误区2：将高模设为可选中状态导致误操作**
在重拓扑过程中，高模（目标对象）应设置为不可选中（在大纲视图中关闭"可选择"图标），否则在编辑模式外误触高模后切换激活对象，会中断当前低模的编辑状态，ShrinkWrap目标引用有时会在复杂场景中失效。

**误区3：Offset值与场景单位不匹配**
角色美术资产通常以厘米（cm）为场景单位（1 Blender单位 = 1 cm），此时推荐Offset值应扩大100倍（例如皮肤低模用0 cm，服装用0.2–0.5 cm）。若直接照搬以米为单位的教程参数（0.002 m），在厘米场景中等效0.000002 cm，偏移量接近零，Z-fighting问题依旧存在；若设为0.002（单位实为cm），则偏移0.02 mm，仍可能不足。

**误区4：对称拓扑时先Apply再添加Mirror**
正确流程是先添加Mirror再添加ShrinkWrap（Mirror在堆栈上方），只需对左半边进行拓扑布线，Mirror自动生成右侧对称网格，ShrinkWrap再将全部顶点投射到高模表面。若先Apply ShrinkWrap后再加Mirror，中线顶点由于已被投射到高模表面而非精确位于X=0，对称时会产生明显的中缝裂口（约0.1–1 mm，取决于高模中线曲率）。

---

## 知识关联

**前置知识——手动拓扑重构**：ShrinkWrap投射仅负责顶点的空间贴合，边循环的走向规划（如眼眶的圆形环线、嘴角的放射状布线）仍需艺术家手动决策。掌握手动重拓扑的肌肉导向布线原则（遵循面部表情肌走向的五环理论：眼轮匝肌、口轮匝肌、颧肌、鼻翼扩张肌、额肌方向各一组环线）是合理使用ShrinkWrap辅助的前提。

**相关工具对比——RetopoFlow插件**：Blender的第三方插件RetopoFlow（由CG Cookie开发，最新版本3.4）将ShrinkWrap投射封装为自动背