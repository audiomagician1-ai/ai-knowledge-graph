---
id: "visibility-system"
concept: "可见性系统"
domain: "game-engine"
subdomain: "scene-management"
subdomain_name: "场景管理"
difficulty: 3
is_milestone: false
tags: ["剔除"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 可见性系统

## 概述

可见性系统（Visibility System）是游戏引擎场景管理中用于判断哪些物体需要被渲染的一套机制，其核心目标是在每一帧内尽可能快速地排除摄像机不可见的几何体，从而减少向GPU提交的渲染批次。与视锥剔除（Frustum Culling）仅测试物体是否在视锥体六个平面内不同，可见性系统还要处理**遮挡关系**——即便一个物体在视锥体内，若它完全被另一个不透明物体挡住，同样无需渲染。

可见性系统的雏形出现在1993年约翰·卡马克（John Carmack）为《Wolfenstein 3D》设计的列渲染器中，而真正系统化的技术则随1996年《Quake》的BSP树与PVS预计算流行开来。现代引擎如Unreal Engine 5和Unity的可见性系统已演变为多层管线：先经过视锥剔除做粗过滤，再由PVS、Portal或遮挡查询（Occlusion Query）做精细过滤，最终发往渲染线程的物体集合仅包含真正可见的对象。

可见性系统的性能意义可以用一个具体数字衡量：在一个包含10,000个静态网格的开放世界关卡中，若不做任何可见性剔除，每帧的Draw Call数量可能高达数千；而正确配置可见性系统后，同一摄像机位置实际提交的Draw Call往往可以降低到原数量的5%–20%，这对于维持60 FPS的帧预算至关重要。

---

## 核心原理

### PVS（Potentially Visible Set，潜在可见集合）

PVS是一种**离线预计算**的可见性方案，首先将场景空间划分为若干凸多边形区域（称为"叶节点"或"区域单元"），然后为每个区域预先计算出所有可能被看见的其他区域集合，存储为位字段（Bitset）。《Quake》引擎的PVS数据使用RLE（行程长度编码）压缩后，128×128个叶节点的可见性矩阵可以从约2 MB压缩到约20 KB。运行时，引擎只需查找摄像机所在叶节点的PVS位字段，即可用一次O(1)的位运算确定候选可见区域列表，随后对这些区域内的物体再做视锥剔除。

PVS的关键限制是**静态性**：可见性数据在关卡构建（Lightmass/BSP编译）阶段生成，动态改变场景结构（如摧毁一堵墙）会使原有PVS失效。Unreal Engine 4之前版本的PVS构建工具（`recompile vis`命令）在大型关卡上耗时可达数小时，这是其被Portal系统或实时遮挡方案逐渐取代的主要原因。

### Portal系统（门户系统）

Portal系统将场景划分为相互连接的封闭"房间"（Cell），房间之间的通道用矩形或多边形的"门户"（Portal）描述。渲染时，引擎从摄像机所在房间出发，通过当前视锥体裁剪每个可见门户，生成缩小的子视锥体，再递归地检查子视锥体能看到哪些相邻房间，直到子视锥体被完全裁剪或深度超过预设阈值（通常为4–6层）。

Portal系统的核心公式是门户裁剪：对于一个从房间A穿过门户P进入房间B的视锥体，新视锥体 `V_new = Frustum_clip(V_current, P)` 其中 `P` 是门户多边形在当前视图空间的投影边界。Portal系统的突出优势是**支持动态开关**——关闭一扇门等同于移除对应门户，几乎不产生额外计算开销。虚幻引擎的`APortalVolume`、Godot 3的`Portal/Room`系统均基于此原理实现。

### 距离剔除（Distance Culling）

距离剔除通过设置每个物体的最大可见距离（`MaxDrawDistance`）来排除超出范围的物体，其判断条件为：

```
distance(Camera.position, Object.boundingSphere.center) > Object.MaxDrawDistance
```

Unreal Engine 5中，`Cull Distance Volume`组件允许按物体尺寸分级设置剔除距离，例如直径小于1米的道具设为500 cm可见距离，直径大于10米的建筑设为10,000 cm可见距离。距离剔除是纯CPU端操作，开销极低，但会在距离边界产生物体突然消失（Pop-in）的视觉问题，通常需要配合LOD系统的逐渐淡出来掩盖。

### 硬件遮挡查询（Hardware Occlusion Query）

GPU端可见性测试通过`GL_ARB_occlusion_query`（OpenGL）或`D3D11_QUERY_OCCLUSION`（DirectX 11）将遮挡测试交给硬件完成：引擎先用简化的包围盒几何体提交深度测试，待GPU返回通过像素计数后，若结果为0则跳过真实网格的渲染。由于GPU查询结果存在1–2帧的延迟，实践中通常使用"上一帧的结果"来剔除当前帧，这会导致物体从遮挡物后快速出现时产生一帧闪烁，称为**时序遮挡误差**（Temporal Occlusion Artifact）。

---

## 实际应用

**城市场景中的层次化可见性**：在《赛博朋克2077》这类高密度城市关卡中，可见性系统通常以三层叠加运行：最外层用距离剔除排除2,000米以外的建筑内部细节；中间层用Portal系统处理室内/室外的边界（通过门窗的视线判断）；最内层用硬件遮挡查询进一步排除被建筑物遮挡的街道家具。

**Unreal Engine 5的Nanite与可见性**：Nanite的虚拟几何体管线内置了基于Hierarchical Z-Buffer（Hi-Z）的屏幕空间遮挡剔除，将传统可见性系统的CPU判断下沉到GPU Compute Shader中，以64×64像素为单位构建Hi-Z金字塔，对每个Cluster（约128个三角形）做并行深度测试，实现了比传统CPU PVS更细粒度的可见性判断。

**移动平台的简化策略**：由于移动GPU不支持异步遮挡查询，Unity的移动端可见性系统通常仅组合使用视锥剔除和距离剔除，配合遮挡烘焙（Occlusion Baking）生成的静态遮挡数据，避免运行时GPU查询的同步开销。

---

## 常见误区

**误区一：视锥剔除已经足够，PVS/Portal是多余的**。视锥剔除只能剔除视锥体外的物体，对于摄像机正对的一堵墙后面的整个城区完全无效。在室内场景测试中，仅使用视锥剔除时摄像机正对走廊仍需渲染走廊另一侧所有房间，而Portal系统能将可见物体数量从数百减少到十几个。

**误区二：PVS适合所有类型的场景**。PVS依赖场景空间可以被分解为封闭凸区域的假设，对于完全开放的地形场景（如无边界的草原），BSP叶节点划分会退化为极大量的区域，PVS位字段的内存占用和构建时间会爆炸式增长。此时应改用基于四叉树或BVH的距离剔除与视锥剔除组合方案。

**误区三：关闭可见性系统可以提升CPU性能**。可见性测试本身确实消耗CPU时间（在大型场景中每帧约0.5–2 ms），但其节省的渲染线程时间和GPU时间通常是这一开销的数十倍。仅在极少数Draw Call场景（如少于100个物体的简单场景）中，禁用可见性系统才能带来净收益。

---

## 知识关联

**前置概念——视锥剔除**：可见性系统在每个Pipeline阶段内部仍然依赖视锥剔除作为最基础的过滤步骤。PVS查询给出候选房间列表后，对房间内每个物体依然要经过视锥的六平面测试；Portal生成的子视锥体本质上也是一个收窄的视锥体，其内部物体依然用AABB-Frustum相交测试判断。理解视锥剔除的AABB测试公式（将包围盒顶点投影到各平面法线方向比较符号距离）是读懂Portal裁剪代码的前提。

**后续概念——场景优化综合**：可见性系统输出的可见对象列表直接输入LOD选择器、批处理合并器和渲染排序器，三者共同构成完整的场景渲染优化管线。场景优化综合还会引入基于GPU驱动渲染（GPU-Driven Rendering）的间接绘制（Indirect Draw），此时可见性剔除结果以GPU Buffer的形式直接传递，无需回读到CPU，彻底消除了传统硬件遮挡查询的延迟问题。