---
id: "deferred-rendering"
concept: "延迟渲染"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 2
is_milestone: false
tags: ["路径"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 延迟渲染

## 概述

延迟渲染（Deferred Rendering）是一种将几何体处理阶段与光照计算阶段分离的渲染架构。传统前向渲染（Forward Rendering）对场景中每个几何体都要执行一次完整的光照计算，若场景有100个光源和1000个三角形，最坏情况需要100,000次光照计算。延迟渲染通过引入中间缓冲区（G-Buffer），将光照计算推迟到所有几何体渲染完成之后，使光照复杂度从O(几何体数量 × 光源数量)降低到O(屏幕像素数量 × 光源数量)。

延迟渲染的概念最早由Michael Deering等人于1988年在SIGGRAPH论文中提出，但受限于当时显卡的显存带宽，实时应用极为有限。直到2004年前后，随着可编程着色器和大容量显存的普及，延迟渲染才开始在游戏引擎中广泛落地。Killzone 2（2009年）是最早将延迟渲染引入主机游戏的代表作之一，其技术分享文档成为业界学习延迟渲染的经典参考。

延迟渲染在光源密集的场景中具有决定性的性能优势，这也是现代城市类开放世界游戏（如《赛博朋克2077》和《GTA V》）普遍采用这一架构的原因。动态路灯、车灯、霓虹灯等数百个局部光源若采用前向渲染将造成严重的性能瓶颈，而延迟渲染则能将这些光源的开销控制在可接受范围内。

---

## 核心原理

### G-Buffer的结构与内容

G-Buffer（Geometry Buffer，几何缓冲区）是延迟渲染的核心数据结构，本质上是一组与屏幕分辨率相同的多张纹理（MRT，Multiple Render Targets）。在几何处理阶段（Geometry Pass），场景中所有不透明几何体被渲染一次，但不进行光照计算，而是将后续光照所需的属性写入G-Buffer的各个通道。

典型的G-Buffer布局包含以下几张纹理：
- **位置缓冲（Position Buffer）**：存储每个像素在世界空间或视图空间中的三维坐标（RGB32F格式，每通道32位浮点）。实际实现中常用深度缓冲重建位置以节省显存。
- **法线缓冲（Normal Buffer）**：存储表面法线向量（RGB16F或压缩格式），用于漫反射和高光计算。
- **漫反射颜色缓冲（Albedo Buffer）**：存储表面的基础颜色（RGBA8格式）。
- **材质参数缓冲（Material Buffer）**：存储金属度、粗糙度、自发光强度等PBR参数，通常打包到单张RGBA纹理的各通道中。

以1920×1080分辨率为例，一套标准G-Buffer（4张纹理）的原始显存占用约为1920×1080×(12+8+4+4)字节 ≈ 58 MB，这也是延迟渲染对显存带宽要求较高的根本原因。

### 光照计算阶段（Lighting Pass）

几何阶段结束后，延迟渲染进入光照阶段。此阶段对屏幕上的每个像素，从G-Buffer中读取其属性，然后对该像素执行所有光源的光照计算。核心光照公式在PBR框架下为：

**L_out = Σ(L_i × BRDF(ω_i, ω_o, normal, albedo, roughness, metallic) × dot(normal, ω_i))**

其中L_i为第i个光源的辐照度，ω_i为入射方向，ω_o为观察方向，BRDF为双向反射分布函数。

每个光源的影响范围可以通过**光源体积（Light Volume）**来限制计算开销。点光源对应一个球体，聚光灯对应一个圆锥体。光照阶段只对位于光源体积内的像素执行该光源的着色器，这使得大量光源在画面中集中于小范围时，每个光源的实际计算量远小于全屏幕像素数量。

### 深度缓冲重建世界坐标

为了避免在G-Buffer中存储完整的32位浮点位置纹理，现代实现通常利用深度缓冲（Depth Buffer）反推世界坐标。设深度值为d（范围0到1），裁剪空间坐标可由屏幕UV坐标和d构造，再乘以逆投影矩阵（Inverse Projection Matrix）和逆视图矩阵（Inverse View Matrix）即可恢复世界空间坐标。这一做法可节省约12~24 MB的显存带宽，在移动平台上尤为关键。

---

## 实际应用

**Unity HDRP（高清渲染管线）**采用延迟渲染作为默认光照路径。在HDRP的G-Buffer设计中，材质属性被压缩打包进4个MRT目标，法线使用八面体编码（Octahedron Encoding）从3个浮点数压缩为2个浮点数，节约了约30%的法线存储带宽。在游戏《控制（Control）》中，Remedy Entertainment基于延迟渲染架构实现了数百个动态光源同时影响场景的效果，游戏内的粒子系统爆炸产生的瞬时光源也通过延迟渲染的Lighting Pass实时计算。

**虚幻引擎4/5（Unreal Engine）**的延迟渲染路径中，点光源使用球形网格包围盒进行Stencil剔除，先用正面三角形写入模板缓冲，再用背面三角形执行光照计算，避免摄像机进入光源体积内时发生剔除错误。这套Stencil Light Volume技术可将城市场景中200个点光源的光照开销控制在约8ms以内（1080p，GTX 1080）。

**移动平台上的Tile-Based延迟渲染（TBDR）**是另一个重要应用场景。iOS的Metal和Arm Mali GPU内置的Tile Memory允许G-Buffer数据在片上缓存中完成读写，避免写回主存，Apple A系列芯片通过TBDR将传统延迟渲染的带宽开销降低了约60%，使延迟渲染在移动设备上变得实用。

---

## 常见误区

**误区一：延迟渲染可以处理透明物体**
这是最常见的误解。延迟渲染的G-Buffer每个像素只能存储一层表面信息，透明物体（如玻璃、粒子）背后的表面会被覆盖。因此几乎所有延迟渲染管线都需要对透明物体单独启用前向渲染路径进行混合绘制，这正是Unity HDRP同时维护Deferred和Forward两条路径的根本原因。

**误区二：延迟渲染一定比前向渲染快**
延迟渲染的优势仅在光源数量较多时才能体现。若场景只有1~2个方向光，前向渲染的带宽消耗远低于写入和读取整套G-Buffer的开销。此外，延迟渲染无法利用硬件MSAA（多重采样抗锯齿），因为MSAA需要在几何阶段对每个像素的多个子样本执行着色，而G-Buffer存储的是单一像素数据。这也是为什么延迟渲染引擎普遍转向FXAA、TAA等基于图像空间的抗锯齿方案。

**误区三：G-Buffer中必须存储世界空间位置**
如前文所述，利用深度缓冲重建位置已是标准做法。在视图空间下进行光照计算还能省去每帧构建逆视图矩阵的开销，Killzone 2的技术文档明确指出其G-Buffer不存储任何显式位置信息，完全依赖深度重建，节约了整整一张RGB32F纹理（约24 MB）的带宽。

---

## 知识关联

延迟渲染建立在**渲染管线概述**所介绍的顶点着色器、片元着色器、深度测试、MRT输出等基础概念之上。理解了G-Buffer存储的深度数据和法线数据，就能直接进入**阴影映射**的学习——阴影映射本质上是从光源视角生成另一张深度缓冲，与G-Buffer中的深度值进行比较来判断遮挡。延迟渲染框架下的Lighting Pass也是**全局光照**（如屏幕空间环境光遮蔽SSAO、屏幕空间反射SSR）的执行平台，这些技术直接读取G-Buffer中的法线和深度数据进行计算。最后，Lighting Pass输出的线性HDR颜色缓冲是**后处理效果**（如Bloom、色调映射、景深）的输入来源，三者在管线中构成串行关系。