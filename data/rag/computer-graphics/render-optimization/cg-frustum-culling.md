---
id: "cg-frustum-culling"
concept: "视锥剔除"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

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
updated_at: 2026-03-26
---



# 视锥剔除

## 概述

视锥剔除（Frustum Culling）是一种渲染优化技术，通过在CPU端判断场景中的物体是否位于摄像机视锥体（View Frustum）内，将完全在视锥体外部的物体从渲染队列中提前剔除，避免将这些物体的顶点数据提交给GPU进行后续变换和光栅化。这一操作发生在Draw Call提交之前，属于几何阶段的剔除手段。

视锥剔除的理论基础来源于计算机图形学的可见性判断研究。1984年，James Clark在其关于层次式包围盒的论文中系统阐述了利用包围体加速可见性测试的框架，奠定了现代视锥剔除的算法基础。与逐像素的深度测试不同，视锥剔除以对象（Object）为粒度进行判断，一次测试即可跳过整个网格的所有三角形，因此性能收益极为显著。

视锥剔除之所以重要，是因为现代游戏场景往往包含数千甚至数十万个物体，而摄像机的水平视角（FOV）通常仅为60°~90°，垂直视角更小，大量物体天然处于视野之外。以一个包含10000个物体的开放世界场景为例，有效的视锥剔除可以将实际提交渲染的Draw Call减少70%以上。

---

## 核心原理

### 视锥体的六平面表示

视锥体由六个裁剪平面围合而成：近裁剪面（Near）、远裁剪面（Far）、左平面（Left）、右平面（Right）、上平面（Top）、下平面（Bottom）。每个平面用点法式方程表示为：

$$Ax + By + Cz + D = 0$$

其中法向量 $(A, B, C)$ 指向视锥体**内部**，$D$ 为平面偏移量。对于空间中任意一点 $P$，将其代入上式得到**有符号距离**：若结果 $> 0$，点在该平面内侧；若结果 $< 0$，点在该平面外侧。当一个点对六个平面的有符号距离均为正时，该点位于视锥体内部。

通常从视图投影矩阵 $\mathbf{M} = \mathbf{P} \cdot \mathbf{V}$ 中直接提取六个平面参数，这是Gribb & Hartmann于2001年提出的方法：以左平面为例，其参数为矩阵第四列加上第一列所得的向量。

### 球体（Sphere）与视锥体的相交测试

球体是计算最快的包围体，测试步骤为：取球心 $C$ 和半径 $r$，对视锥体的每个平面计算球心到平面的有符号距离 $d = A \cdot C_x + B \cdot C_y + C \cdot C_z + D$。若存在某个平面使得 $d < -r$，则球体完全在该平面外侧，判定为剔除。此测试仅需6次点积和6次比较，是最轻量级的包围体测试。

球体测试的缺点是**假阳性率**（False Positive）较高：当物体实际不可见但包围球足够大时，球体可能仍与视锥体相交，导致物体被错误保留。

### AABB（轴对齐包围盒）与视锥体的相交测试

AABB由最小顶点 $\mathbf{P_{min}} = (x_{min}, y_{min}, z_{min})$ 和最大顶点 $\mathbf{P_{max}} = (x_{max}, y_{max}, z_{max})$ 定义。对每个裁剪平面，需要找出AABB上距离该平面**有符号距离最大**的顶点（称为P顶点）和**距离最小**的顶点（称为N顶点）。

P顶点的选取规则：对平面法向量的每个分量，若分量为正则选取对应轴的最大值，否则选取最小值。若P顶点的有符号距离 $< 0$，则整个AABB完全在该平面外侧，执行剔除。若N顶点的有符号距离 $\geq 0$，则AABB完全在该平面内侧。中间情况为相交。AABB测试的假阳性率低于球体，但每个平面需要更多的分支判断。

### OBB（有向包围盒）与视锥体的相交测试

OBB由中心点 $\mathbf{C}$、三个局部轴方向向量 $(\mathbf{u}, \mathbf{v}, \mathbf{w})$ 及对应半长度 $(e_u, e_v, e_w)$ 定义。对某一裁剪平面（法向量 $\mathbf{n}$），OBB在该法向量方向的有效"投影半径"为：

$$r = e_u |\mathbf{n} \cdot \mathbf{u}| + e_v |\mathbf{n} \cdot \mathbf{v}| + e_w |\mathbf{n} \cdot \mathbf{w}|$$

若中心点到平面的有符号距离 $d < -r$，则剔除。OBB测试精度最高，但每个平面需要3次额外点积，计算量比AABB更大，通常用于对剔除精度要求较高的大型静态物体。

---

## 实际应用

**Unity引擎**的内置视锥剔除对MeshRenderer组件自动使用AABB测试，包围盒由网格的`bounds`属性提供，在每帧的`CullResults`阶段执行。开发者可通过`GeometryUtility.TestPlanesAABB(planes, bounds)`接口手动触发测试，`planes`数组由`GeometryUtility.CalculateFrustumPlanes(camera)`提取。

**Unreal Engine 5**在视锥剔除之前还会执行距离剔除（Distance Culling），两者结合使用：距离剔除负责剔除超出`MaxDrawDistance`的远处物体，视锥剔除再对剩余物体进行视野范围过滤。UE5的Nanite虚拟几何体系统在Cluster级别（约128个三角形一个Cluster）单独执行视锥剔除，粒度远比传统物体级别更细。

在**移动端游戏**中，视锥剔除通常结合八叉树（Octree）或BVH（层次包围体树）空间加速结构使用：首先在BVH树上自顶向下遍历，当父节点的包围体被完全剔除时，其所有子节点无需测试，将O(N)的遍历代价降低为O(logN)。

---

## 常见误区

**误区一：视锥剔除可以替代背面剔除**。背面剔除（Backface Culling）在GPU的三角形装配阶段剔除朝向背离摄像机的三角面，粒度是单个三角形；视锥剔除在CPU端剔除整个物体，粒度是包围体。两者针对的冗余类型完全不同，对一个完全在视锥体内的封闭网格，视锥剔除无法剔除其背面三角形，必须依赖GPU的背面剔除完成。

**误区二：包围体越精确越好**。OBB的精度高于AABB，但对于一个拥有5000个动态物体的场景，若每帧都为所有物体执行OBB测试，其CPU开销（每个物体约18次浮点乘加）可能超过Draw Call减少带来的GPU收益。实践中通常对小物体使用Sphere，对中等物体使用AABB，仅对面积很大的静态建筑使用OBB。

**误区三：视锥剔除对GPU无法感知的物体同样有效**。如果物体虽在视锥体内但被其他不透明物体完全遮挡，视锥剔除不会将其剔除——这是遮挡剔除（Occlusion Culling）需要解决的问题。视锥剔除只处理"是否在摄像机视野范围内"，而非"是否真正可见"。

---

## 知识关联

视锥剔除以**渲染优化概述**中介绍的Draw Call开销作为优化目标，是学习渲染剔除体系的第一个具体算法。它要求学习者已理解MVP变换矩阵和裁剪空间的概念，因为六平面提取依赖于投影矩阵 $\mathbf{P} \cdot \mathbf{V}$ 的列向量运算。

在视锥剔除之后，下一个进阶主题是**遮挡剔除**（Occlusion Culling）。遮挡剔除解决视锥体内部物体之间互相遮挡的可见性问题，典型实现包括PVS（预计算可见性集合）和HZB（层次Z缓冲）。视锥剔除与遮挡剔除通常形成串联流水线：先用视锥剔除淘汰视野外物体，再对剩余物体执行遮挡剔除，两级过滤后才提交最终的Draw Call列表。