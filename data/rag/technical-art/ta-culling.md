---
id: "ta-culling"
concept: "裁剪技术"
domain: "technical-art"
subdomain: "perf-optimization"
subdomain_name: "性能优化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 96.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 裁剪技术（Culling）

## 概述

裁剪技术（Culling）是实时渲染流水线中用于剔除不可见几何体的系统性优化手段，核心目标是让GPU仅处理最终对屏幕像素有贡献的几何体，从而节省顶点着色（Vertex Shading）、图元装配（Primitive Assembly）、光栅化（Rasterization）及像素着色（Fragment Shading）的全链路开销。裁剪操作通常发生在CPU向GPU提交DrawCall之前的场景遍历阶段，或GPU早期流水线阶段，通过数学判断或硬件机制将本帧无需渲染的物体从渲染列表中提前移除。

从历史沿革看，裁剪技术的算法基础最早可追溯至1974年：Ivan Sutherland与Gary Hodgman在论文 *"Reentrant Polygon Clipping"*（Communications of the ACM, 1974）中提出了**Sutherland-Hodgman多边形裁剪算法**，用于将多边形逐边对裁剪平面进行裁剪，这是现代视锥体裁剪算法的直接前身。遮挡裁剪（Occlusion Culling）作为独立系统进入商业引擎则要晚得多——Quake（1996）首先以PVS（Potentially Visible Set）方案解决室内场景遮挡问题，而基于GPU硬件查询的Hi-Z方案在2000年代中期随可编程着色器普及才逐渐成熟。

一个复杂的开放世界关卡可能包含5万至20万个网格实例。若不施加任何裁剪，CPU端仅遍历场景组织DrawCall便可轻易耗尽单帧16.67ms（60fps目标）的时间预算，GPU端处理数以亿计的不可见三角形更是灾难性的浪费。合理配置裁剪系统可将实际提交的DrawCall数量压缩至总场景物体数的5%～20%，这也是现代AAA开放世界游戏维持高帧率的基础条件之一。

---

## 核心原理

### 视锥体裁剪（Frustum Culling）

相机的可见区域在三维空间中表现为一个截锥体（Frustum），由6个平面围成：近裁面（Near Plane）、远裁面（Far Plane）以及上、下、左、右4个侧面。每个平面均可用方程 $Ax + By + Cz + D = 0$ 表示，其中法向量 $(A, B, C)$ 指向视锥体内侧。

判断物体是否位于视锥体内的标准方法是**AABB（Axis-Aligned Bounding Box）六平面测试**：对包围盒的8个顶点 $\mathbf{v}_i$，依次代入每个裁剪平面方程计算符号距离：

$$d_i = A \cdot v_{ix} + B \cdot v_{iy} + C \cdot v_{iz} + D$$

若某一平面对应的所有8个 $d_i < 0$（即8顶点全在该平面外侧），则物体完全位于视锥体外，可安全剔除。该测试最坏情况需要 $8 \times 6 = 48$ 次点面距离计算。实践中常用**正负顶点（p-vertex / n-vertex）优化**将每个平面测试缩减为2次计算（参见《Real-Time Rendering》第4版，Akenine-Möller et al., 2018，第19章）。

Unity引擎在Burst编译器配合SIMD（AVX2）指令的实现中，将大批量AABB视锥体测试速度提升至标量版本的4～8倍，单帧可在约0.3ms内完成对10000个包围盒的测试（以Intel Core i7-9700K为基准）。

视锥体裁剪完全在CPU端执行，属于粗粒度剔除（Broad Phase），无法处理"在视锥体内但被其他物体完全遮挡"的情形，需要遮挡裁剪作为后续精化。

### 遮挡裁剪（Occlusion Culling）

遮挡裁剪解决的是"物体在视锥体内但被遮挡物完全遮盖而不可见"的问题。典型场景为城市街道中被楼宇墙体遮挡的室内家具，或地牢游戏中相机看不到的房间内所有物件。遮挡裁剪主要分为两大技术路线：

**① 预计算PVS / Cell-Portal方案**：Unity集成的Umbra遮挡裁剪系统在编辑器阶段将静态场景划分为空间Cell，预计算每个Cell内摄像机可见的物体集合（即PVS），烘焙结果保存为二进制索引表。运行时根据摄像机所在Cell进行O(1)查表，CPU开销极低，适用于静态建筑密集的室内/城市场景。其局限在于仅支持静态遮挡物，且烘焙时间随场景复杂度显著增长（大型关卡常需数分钟至数十分钟）。

**② 层次Z缓冲（Hierarchical Z-Buffer, Hi-Z）GPU遮挡查询**：UE5的Nanite和传统GPU Occlusion Query均基于此原理。深度缓冲被构建为Mipmap链，从原始分辨率（如1920×1080）至1×1共约11层。测试某物体是否被遮挡时，取其包围盒在屏幕空间投影所对应层级的Hi-Z值，若包围盒最近深度大于该Hi-Z值，则物体完全被遮挡，无需渲染。

Hi-Z方案存在**一帧延迟（One-Frame Lag）**问题：当前帧使用上一帧深度缓冲做遮挡判断，摄像机快速转向时被遮挡物体可能短暂出现（pop-in），这是GPU端异步查询的固有权衡。NVIDIA在2001年提出的CHC（Coherent Hierarchical Culling）算法（Bittner et al., 2004，*"Coherent Hierarchical Culling: Hardware Occlusion Queries Made Useful"*）通过维护可见物体历史队列来缓解该问题。

### 距离裁剪（Distance Culling）

距离裁剪依据物体与相机的世界空间距离 $r = \|\mathbf{p}_{obj} - \mathbf{p}_{cam}\|$ 决定是否剔除，其本质是LOD系统的极端情形——当 $r$ 超过阈值 $r_{max}$ 时直接隐藏物体而非降低网格精度。

合理阈值的工程经验是**屏幕覆盖率（Screen Coverage）**：当物体在屏幕上的投影面积小于约 $10 \times 10 = 100$ 像素时，继续渲染该物体的性价比极低。可通过物体半径 $R$ 与相机距离 $r$ 估算屏幕半径：

$$r_{screen} = \frac{R \cdot f}{r}$$

其中 $f$ 为焦距（以像素为单位，$f = \frac{H}{2\tan(\theta/2)}$，$H$ 为屏幕高度分辨率，$\theta$ 为垂直视角）。当 $r_{screen} < 5$ 像素时即可设为剔除阈值。

在Unreal Engine中，通过Actor的 `Min Draw Distance` 和 `Max Draw Distance` 属性精细控制每个Actor的距离阈值，或在关卡中放置 `Cull Distance Volume`，为整个体积内所有物体统一设置剔除距离表（支持按物体尺寸分档，例如尺寸小于100cm的道具在800cm外剔除，尺寸小于300cm的在2000cm外剔除）。

---

## 关键公式与算法

### AABB视锥体测试（正负顶点优化）

对于裁剪平面法向量 $(A, B, C)$，p-vertex 定义为使 $Ax + By + Cz$ 最大的AABB顶点：

```python
def get_p_vertex(aabb_min, aabb_max, normal):
    # normal = (A, B, C) 为平面法向量
    px = aabb_max[0] if normal[0] >= 0 else aabb_min[0]
    py = aabb_max[1] if normal[1] >= 0 else aabb_min[1]
    pz = aabb_max[2] if normal[2] >= 0 else aabb_min[2]
    return (px, py, pz)

def frustum_cull(aabb_min, aabb_max, planes):
    """
    planes: list of (A, B, C, D), 法向量指向视锥体内侧
    返回 False 表示物体完全在视锥体外（可剔除）
    """
    for (A, B, C, D) in planes:
        px, py, pz = get_p_vertex(aabb_min, aabb_max, (A, B, C))
        if A*px + B*py + C*pz + D < 0:
            return False  # 完全在该平面外侧，剔除
    return True  # 通过所有平面测试，保留
```

该实现将每个平面的测试从8次点乘减少为1次（仅测试p-vertex），6个平面共6次点乘，相比朴素实现减少了87.5%的计算量。

---

## 实际应用

**案例一：《赛博朋克2077》夜之城街道场景**
CDPR在夜之城的开放世界实现中，将遮挡裁剪、距离裁剪与LOD系统三者联合使用：高密度建筑群依赖预烘焙Cell-Portal进行遮挡剔除，路面小物件（垃圾桶、路灯、广告牌）配置了基于尺寸分档的距离裁剪，视锥体裁剪作为最外层过滤。最终实际每帧提交的DrawCall数量控制在10000～20000范围内（GDC 2021技术演讲披露数据）。

**案例二：Unity移动端优化实践**
在移动端（如骁龙888 GPU），GPU端Hi-Z遮挡查询的一帧延迟代价被放大，通常推荐改用CPU端软光栅化遮挡裁剪（Software Occlusion Culling）方案。Intel开源的软光栅库**Masked Software Occlusion Culling**（Hasselgren et al., 2016）在CPU端以AVX2指令维护一个低分辨率（如320×180）深度缓冲，可在约0.5ms内完成数千个物体的遮挡测试，避免了GPU查询的异步延迟问题。

**例如**，在Unity URP移动项目中配置距离裁剪的典型步骤：选中Camera组件 → 勾选 `Occlusion Culling` → 在 `LOD Group` 中为最低级别设置 `Culled` 阈值为屏幕高度的0.5%（即屏幕1080p时约5.4像素高度即剔除）。这一阈值在中高端机型上可减少约30%～40%的无效DrawCall。

---

## 常见误区

**误区一：遮挡裁剪烘焙后一劳永逸**
Unity Umbra的Cell-Portal遮挡裁剪仅对**Static**标记的物体生效，动态生成或运行时移动的物体（如怪物、玩家建造的结构）完全不受其覆盖。在包含大量动态物体的关卡中，若仅依赖烘焙遮挡裁剪，动态物体的遮挡问题需要另行处理（如动态Hi-Z或手动剔除逻辑）。

**误区二：距离裁剪阈值越小越好**
将物体的 `Max Draw Distance` 设置得过小会导致明显的物体在玩家视野中突然消失（Popping），破坏沉浸感。正确做法是结合LOD渐变（Dithering Fade）：在阈值前5%距离范围内通过Alpha Dithering逐渐淡出物体，使消失过渡不可察觉，而非硬切换显隐。

**误区三：视锥体裁剪可以替代遮挡裁剪**
在室内/地下城类场景中，玩家朝向某一走廊时，走廊两侧的大量房间物体虽然完全在视角背后（视锥体裁剪可剔除），但相机稍微转动就会有大量物体重新进入视锥体。而遮挡裁剪可以在相机面向房间时剔除被墙体挡住的其他房间，两者解决的是不同维度的可见性问题，需要配合使用而非替代。

请思考：**在完全由动态物体（如粒子、角色、投射物）构成的战斗场景中，三种裁剪技术各自的有效性如何？是否存在某种技术完全失效的情形？**

---

## 知识关联

**前置知识——性能