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
quality_tier: "pending-rescore"
quality_score: 42.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 裁剪技术

## 概述

裁剪技术（Culling）是实时渲染管线中的一类优化手段，其核心目标是在提交任何绘制调用（Draw Call）之前，将屏幕上不可见的几何体从渲染队列中剔除，从而节省顶点处理、光栅化和像素着色的全部开销。GPU 无法自动"跳过"不可见物体——如果没有裁剪，场景中每一个网格都会进入渲染管线并消耗 GPU 时间，即便它完全在摄像机后方或被建筑物遮挡。

裁剪的概念在软件渲染时代已存在。1969 年 Ivan Sutherland 与 Gary Hodgman 提出了 Sutherland–Hodgman 多边形裁剪算法，专门处理视锥体边界上的多边形截断问题，这是最早被系统化描述的裁剪方法之一。进入现代 GPU 时代后，硬件级的视锥体裁剪被集成到光栅化阶段，而遮挡裁剪（Occlusion Culling）和距离裁剪（Distance Culling）则主要在 CPU 侧由引擎执行，两类裁剪的职责分工非常明确。

对于开放世界或城市场景，裁剪技术往往能将每帧的 Draw Call 数量从数千降到数百，是场景规模得以扩大的前提条件，而非次要的锦上添花。

## 核心原理

### 视锥体裁剪（Frustum Culling）

视锥体是由摄像机近裁剪面（Near Plane）、远裁剪面（Far Plane）和四个侧面共六个平面围成的截锥体。视锥体裁剪的判断方法是将物体的包围盒（通常是轴对齐包围盒 AABB）与这六个平面逐一进行半空间测试：若 AABB 的全部八个顶点都位于某一平面的外侧（法线反方向），则该物体完全在视锥体外，直接剔除。这一测试在 CPU 上每帧执行，时间复杂度与场景物体数量成线性关系。Unity 的静态批处理和 Unreal Engine 的场景管理器均使用 BVH（Bounding Volume Hierarchy）加速结构，将平均比较次数从 O(n) 优化到 O(log n)。

### 遮挡裁剪（Occlusion Culling）

遮挡裁剪解决的是视锥体内部仍有大量物体相互遮挡的问题。典型实现方式有两种：

- **软件遮挡裁剪（Software Occlusion Culling）**：在 CPU 上以极低分辨率（如 256×128）光栅化"遮挡体"（Occluder），生成深度缓冲，再将待测物体的 AABB 投影到该缓冲上进行深度比较，若 AABB 最近点的深度大于缓冲深度则剔除。Intel 开源的 Masked Software Occlusion Culling 库可在现代 CPU 上每帧处理超过 100,000 个遮挡查询。
- **硬件遮挡查询（Hardware Occlusion Query）**：通过 OpenGL 的 `GL_SAMPLES_PASSED` 或 Vulkan 的 `VK_QUERY_TYPE_OCCLUSION` 查询，让 GPU 统计某个包围盒通过深度测试的像素数；若结果为 0 则下一帧剔除该物体。缺点是 CPU-GPU 回读引入 1-2 帧延迟，存在"幽灵帧"闪烁问题。

Unity 的 Umbra 遮挡系统和 Unreal 的 PVS（Potentially Visible Set）均属于预计算遮挡，离线将场景划分为小格子并预烘焙可见性数据，运行时查表而非实时计算，以内存换取运行时开销。

### 距离裁剪（Distance Culling）与 LOD 配合

距离裁剪按物体到摄像机的距离设置最大可见距离阈值，超过阈值的物体直接跳过渲染。在 Unreal Engine 中，每个 Actor 可设置 `Max Draw Distance`，也可通过 `Cull Distance Volume` 对某个区域内的所有小物件批量设置剔除距离（例如草丛对象通常设置为 2000 UU，约 20 米）。距离裁剪常与 LOD（Level of Detail）分级衔接：近处使用高精度网格，中距离切换低精度网格，最远距离直接剔除，三段式管理使渲染预算可预期。

距离裁剪的计算公式为球形测试：

$$d = \sqrt{(x_{obj}-x_{cam})^2 + (y_{obj}-y_{cam})^2 + (z_{obj}-z_{cam})^2}$$

若 $d > D_{max}$（最大可见距离），则物体被裁剪。实际引擎为避免开方运算，通常比较 $d^2$ 与 $D_{max}^2$，节省一次 `sqrt` 调用。

## 实际应用

**城市场景优化**：在《赛博朋克 2077》类型的城市关卡中，路面以下的下水道网格完全被地面遮挡，使用软件遮挡裁剪可将地下几何体全部剔除，实测在 CPU 侧节省约 15%–30% 的渲染提交时间。

**植被系统**：开放世界草地中可能存在数十万个草丛实例，通过 `Cull Distance Volume` 设置 15–25 米的裁剪距离，配合 GPU Instancing，可将草丛的 Draw Call 从每帧数千次降至数十次。

**Unity 中的配置步骤**：在 Window → Rendering → Occlusion Culling 面板中，将场景静态物体标记为 `Occluder Static` 或 `Occludee Static`，烘焙后 Unity 自动在运行时调用 Umbra 进行查表裁剪。烘焙的 `.asset` 文件大小通常在 5–50 MB，与场景精细度直接相关。

## 常见误区

**误区一：视锥体裁剪会剔除所有不可见物体**。视锥体裁剪只剔除视锥体外的物体，对于在视锥体内但被其他物体完全遮挡的物体（如被墙壁遮挡的整个房间），必须额外使用遮挡裁剪才能剔除。两者解决的问题不同，不可互相替代。

**误区二：遮挡裁剪总是比不裁剪更快**。遮挡裁剪本身有 CPU 计算开销，如果场景物体数量少或遮挡关系不明显（如开阔草原），遮挡裁剪带来的收益可能小于其自身的查询开销，此时开启遮挡裁剪反而会降低性能。适合遮挡裁剪的场景特征是"有大量实心遮挡体"，如室内走廊、城市街道。

**误区三：裁剪是 GPU 完成的**。视锥体裁剪有硬件级（在 Clip Space 之后由光栅化器自动处理三角形边界）和软件级（CPU 对整个物体的包围盒判断）之分。引擎级的物体级裁剪全部在 CPU 上完成，目的是减少 Draw Call 提交数量，这个阶段 GPU 尚未参与。学生常将"GPU 自动裁剪三角形"误以为等同于"引擎级物体裁剪"，混淆了粒度。

## 知识关联

裁剪技术的有效实施建立在场景管理的数据结构（BVH、八叉树）之上，对这些结构的理解有助于判断裁剪查询的时间开销来源。裁剪技术与 **LOD（细节层次）** 紧密配合：裁剪决定"是否渲染"，LOD 决定"以多少面数渲染"，二者共同管控场景的面数预算。

在掌握裁剪技术之后，**阴影性能**优化是自然的延伸话题：阴影贴图渲染（Shadow Map Pass）会对场景进行一次独立渲染，裁剪逻辑（尤其是阴影视锥体裁剪和阴影距离设置）直接决定阴影 Pass 的 Draw Call 数量。未对阴影 Pass 单独配置裁剪参数是许多项目阴影开销过高的直接原因。
