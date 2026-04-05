---
id: "3da-hs-decal-mesh"
concept: "Decal Mesh"
domain: "3d-art"
subdomain: "hard-surface"
subdomain_name: "硬表面建模"
difficulty: 3
is_milestone: false
tags: ["技巧"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 贴花网格（Decal Mesh）

## 概述

贴花网格（Decal Mesh）是硬表面建模中一种将额外几何薄片叠加于宿主表面以呈现局部细节的技术。其核心操作是创建一个厚度仅为 **0.001~0.01 个世界单位**、与宿主表面极度贴合的网格片，为该网格单独指定材质或参与烘焙流程，从而在不破坏底层拓扑结构的前提下，将磨损划痕、序列号字符、焊缝、铭牌贴纸、铆钉阵列等细节"锚定"于表面之上。

该技术的概念源自游戏引擎的投影贴花系统——虚幻引擎于 2003 年（Unreal Engine 2.5）正式引入 Decal Actor，通过摄影机空间投影将纹理叠加到场景几何体上，但这种方法在曲面或几何体边缘处会产生拉伸与形变。硬表面建模社区（尤其是以 Tor Frick、Josh Powers 为代表的游戏硬表面艺术家）在 2012 年前后将"贴花"思维迁移至网格层面，通过手工建模出独立的几何贴花片，彻底规避了投影算法的曲面形变问题，并使其可以无缝进入 **High Poly → Low Poly 烘焙流程**，生成精确的法线贴图（Normal Map）与环境光遮蔽贴图（AO Map）。

贴花网格的核心价值在于将"视觉细节密度"与"拓扑复杂度"完全解耦。一块机甲装甲板的基础网格只需约 1500~2500 个三角面，通过叠加 10~20 个贴花网格后，烘焙出的 2K 法线贴图可呈现等效于 15000 面以上的视觉复杂度，最终进入引擎的 Low Poly 仍保持极低面数，满足实时渲染预算。这一工作流已成为 AAA 游戏美术流水线（如《赛博朋克 2077》《守望先锋》系列）中硬表面资产制作的标准环节之一，在影视宣传图（Key Art）的离线渲染场景中同样被广泛采用。

参考资料：《Practical Game Art: Hard Surface Modeling》(Tor Frick & Viktor Öhman, 2017, Marmoset) 以及《Hard Surface Modeling Bible》 中对贴花工作流的系统描述。

---

## 核心原理

### 偏移量与深度冲突（Z-Fighting）控制

贴花网格与宿主表面之间必须维持精确的法线方向偏移，以防止 Z-Fighting。所谓 Z-Fighting，是指两层几何面共享相近深度缓冲值时，GPU 光栅化阶段无法确定哪一层优先，造成像素级别的闪烁条纹。

通用偏移规则：在 Blender（1 BU = 1 m 的默认场景比例）中，贴花网格整体沿宿主表面法线偏移 **0.002~0.005 BU（即 2~5 mm）**。在 ZBrush 的 DynaMesh 工作流中，合并 SubTool 前须对贴花 SubTool 执行 **Inflate Brush 或 Deformation > Inflate，数值约为 +2~5 DynaMesh 分辨率单位**（以 128 分辨率为例，偏移约为模型包围盒对角线的 0.8%）。偏移过小（< 0.001 BU）会导致渲染闪烁；偏移过大（> 0.01 BU）则在 30° 以下的掠射视角下肉眼可见贴花"悬浮"，破坏硬表面的金属质感与可信度。

### 拓扑构建方式：平面型与曲面共形型

贴花网格按宿主表面的形状分为两类：

**平面型贴花网格**适用于机械装甲板正面的序列号文字、矩形铭牌等平整区域。在 Blender 中，可直接使用 `Add > Text` 添加文字对象，在字体属性面板下设置 **Extrude = 0.003 m、Bevel Depth = 0.0005 m**，再执行 `Convert to Mesh`，最终用 **Shrinkwrap 修改器**（模式选 Project，Axis 勾选 Negative Z）将整组顶点投影贴合至宿主表面，确保所有顶点与宿主表面偏移一致。

**曲面共形型贴花网格**适用于圆柱体炮管上的环形焊缝、球形燃料舱上的铆钉线等曲面区域。此类网格需要在建立基础面片后，叠加 **Subdivision Surface 修改器（Level ≥ 2）**，并手动调整边缘循环边（Edge Loop）密度，使其与宿主曲面的曲率变化保持匹配。若循环边密度不足，贴花网格边缘在曲面转折处会出现**法线方向跳变**，烘焙后的法线贴图边缘会出现宽度约 2~4 像素的黑边伪影（Dark Seam Artifact），在 Marmoset Toolbag 的实时预览中尤为明显。

### 材质隔离与 High-to-Low 烘焙配置

贴花网格在烘焙阶段须作为 High Poly 的一部分与 Low Poly 宿主表面打包进同一**烘焙组（Bake Group）**。以 Marmoset Toolbag 4 为例，标准流程如下：

1. 将贴花网格与宿主 High Poly 合并为同一 High Poly 槽位；
2. Low Poly 使用整洁的宿主表面，UV 已展开且无重叠；
3. 在 Bake Group 设置中将 **Cage Offset 设为 0.05~0.1（模型空间单位）**，保证投影光线从贴花几何体最外层出发；
4. 烘焙分辨率建议使用 **2048×2048（2K）**，每像素对应约 0.49 mm（以 1 m 装甲板为例），可完整还原宽度 ≥ 1 mm 的细节线条。

烘焙完成后，贴花网格本身不再进入游戏引擎，所有视觉信息已被压缩至法线贴图的 RGB 通道与 AO 贴图的灰度通道中，**运行时额外面数成本为零**。

---

## 关键公式与参数速查

贴花网格偏移量的选取可用以下经验公式估算：

$$\delta = \frac{L_{bbox}}{D_{mesh}} \times k$$

其中：
- $\delta$ 为建议法线偏移量（世界单位）
- $L_{bbox}$ 为宿主网格包围盒最长边长度
- $D_{mesh}$ 为宿主网格平均边长（即网格密度指标）
- $k$ 为经验系数，通常取 **0.002~0.005**

例如：一块长 1 m、平均边长约 0.05 m 的装甲板，建议贴花偏移量 $\delta = \frac{1.0}{0.05} \times 0.003 = 0.06$ BU，但此值通常超出直觉预期，需结合目视检查调整至 0.002~0.005 BU 范围内，公式主要用于**相对比较不同密度网格时的偏移量比例关系**。

以下为 Blender Python 脚本片段，可批量为选中的贴花网格对象沿各自平均法线方向偏移 0.003 m：

```python
import bpy
import bmesh
from mathutils import Vector

def offset_decal_along_normal(obj, offset=0.003):
    """将贴花网格对象沿平均顶点法线方向整体偏移 offset 个世界单位"""
    mesh = obj.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()

    # 计算所有顶点法线的平均方向
    avg_normal = Vector((0, 0, 0))
    for v in bm.verts:
        avg_normal += v.normal
    avg_normal = avg_normal.normalized()

    # 沿平均法线方向移动对象原点
    obj.location += avg_normal * offset
    bm.free()

for obj in bpy.context.selected_objects:
    if obj.type == 'MESH':
        offset_decal_along_normal(obj, offset=0.003)
```

运行此脚本前，需确保贴花网格已完成 `Apply Scale`（缩放应用），否则偏移量会受非均匀缩放影响而失准。

---

## 实际应用案例

**案例一：机甲胸甲铭牌（游戏资产，Blender + Marmoset Toolbag）**

1. 在宿主装甲板旁新建 `Plane`，缩放至铭牌尺寸（例如 0.12 m × 0.04 m）；
2. 添加 `Solidify` 修改器，`Thickness = 0.003 m`，`Offset = +1.0`（确保厚度向外扩展）；
3. 添加 `Shrinkwrap` 修改器，模式选 **Project**，Target 指定宿主装甲板，勾选 **Negative Z**，`Offset = 0.002 m`；
4. 对铭牌四角执行 `Bevel`（宽度 0.001 m，Segments = 2）模拟金属铭牌的圆角冲压工艺；
5. 将铭牌贴花网格与宿主 High Poly 合并，导入 Marmoset Toolbag，设置 Cage Offset = 0.08，烘焙 2K Normal Map 与 AO Map；
6. 最终资产仅保留宿主 Low Poly（约 800 tri），铭牌细节完全存于 Normal Map 中，引擎侧零面数开销。

**案例二：科幻头盔上的循环焊缝（ZBrush 工作流）**

1. 在 ZBrush 中新建一个圆柱 SubTool，DynaMesh 分辨率设为 256；
2. 将其 Inflate +3 单位后与头盔主体 SubTool 合并（`Merge Down`）；
3. 使用 **TrimDynamic Brush** 清理合并处多余体积，保留约 1.5 mm 宽的环形焊缝突起；
4. 导出合并后的 High Poly 至 Substance Painter，烘焙时 `Max Rear Distance = 0.002 m`，确保焊缝高度被完整采样进 Normal Map。

**案例三：影视宣传图中的大量铆钉阵列**

对于影视级离线渲染（使用 Arnold 或 V-Ray），贴花网格可直接作为**几何体细节**保留，不需要烘焙至贴图。此时可通过 Blender 的 `Geometry Nodes` 在装甲板表面自动分布铆钉贴花实例，每颗铆钉约 64 tri，在一块装甲板上阵列 80 颗，总计 5120 tri 的铆钉网格在离线渲染中仍属极低开销，同时呈现出远优于法线贴图的次表面光照细节与高光准确度。

---

## 常见误区

**误区一：贴花网格偏移量"越小越好"**
许多初学硬表面的建模师认为偏移量越小越接近"真实焊接/铭牌"的物理厚度，因此将偏移量设为 0.0001 BU 甚至更小。然而 Blender 的默认 Eevee/Cycles 渲染器与大多数引擎的深度缓冲区精度为 **24 位或 32 位浮点**，当两层几何面的深度差小于 $2^{-23}$ 个世界单位（约 1.2×10⁻⁷ BU）时必然出现 Z-Fighting。实践中 0.002 BU 是最小安全值，低于此值需依赖多边形偏移（Polygon Offset）的额外配置。

**误区二：贴花网格可以替代所有 UV 细节**
贴花网格只能在**法线贴图采样范围内**呈现突出/凹陷细节，对于需要精确颜色分界（如彩色徽章、多色涂装花纹）的区域，仍需配合宿主网格的颜色贴图（Albedo Map）或遮罩贴图（Mask Map）。将纯颜色细节用贴花网格处理，反而会在烘焙后因法线切线空间的微小误差导致颜色贴图边缘出现 1~2 像素的法线污染。

**误区三：贴花网格在任何曲率的宿主表面都能使用 Shrinkwrap 