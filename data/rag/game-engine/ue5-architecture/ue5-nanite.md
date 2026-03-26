---
id: "ue5-nanite"
concept: "Nanite虚拟几何体"
domain: "game-engine"
subdomain: "ue5-architecture"
subdomain_name: "UE5架构"
difficulty: 3
is_milestone: false
tags: ["渲染"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 47.4
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.414
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# Nanite虚拟几何体

## 概述

Nanite是虚幻引擎5（UE5）于2022年正式发布时引入的虚拟化几何体系统，其核心目标是让开发者无需手动制作LOD（细节层级）模型即可直接使用影视级高精度网格体。Nanite通过一套专门的数据格式和GPU驱动渲染管线，将原本需要数十万乃至数百万面的网格体实时渲染至屏幕，同时保证实际光栅化的像素数量不超过屏幕分辨率。Epic Games在技术演示《古代山谷》中使用了超过**4.26亿个多边形**的场景作为Nanite能力的首次公开展示。

Nanite的设计灵感来源于**虚拟纹理（Virtual Textures）**的分页流送思想：就像虚拟纹理只加载当前帧实际可见的纹素数据，Nanite也只渲染当前帧实际可见的"微多边形（micro-polygon）"——即面积接近单个像素大小的三角形。这一思想将几何体的管理粒度从整个网格体下降至单个三角形簇（Cluster），使系统能够以远超传统LOD链的精细度进行裁剪与细化。

Nanite对工作流的改变是革命性的：美术人员可以直接将ZBrush或Photogrammetry扫描生成的原始高模导入UE5，引擎自动处理运行时的精度调配，彻底消除了手工制作LOD、法线烘焙等流程中大量的人工干预。

---

## 核心原理

### 1. 层级簇（Cluster Hierarchy）与BVH结构

Nanite在导入阶段将网格体切分为每簇最多**128个三角形**的Cluster，再将这些Cluster按空间关系组织成**有向无环图（DAG）**形式的层级结构，而非传统的线性LOD链。每个父级Cluster是多个子级Cluster合并并简化后的结果，最终形成一棵类似BVH（包围体层次结构）的树。运行时，系统从根节点向下遍历，在误差投影到屏幕空间小于**1像素**的层级处停止，选取对应节点的Cluster进行渲染，从而保证任何视距下都不出现肉眼可见的LOD跳变。

### 2. 软件光栅化（Software Rasterizer）

当三角形投影面积极小（接近微多边形）时，传统硬件光栅化器的固定开销（如三角形建立、深度写入等）反而成为性能瓶颈。Nanite为此实现了一套**运行于Compute Shader的软件光栅化路径**：对于覆盖面积小于约**32×32像素**的小三角形，Nanite绕过硬件三角形建立单元，直接在GPU线程中用原子操作写入可见性缓冲区（Visibility Buffer）。这种分叉式光栅化策略（大三角形走硬件路径，小三角形走软件路径）在密集几何场景中可将光栅化吞吐量提升3到5倍。

### 3. 可见性缓冲区（Visibility Buffer）与延迟材质求值

Nanite不使用传统的GBuffer（几何缓冲）直接存储法线、颜色等信息，而是在首个Pass中只写入一张**64位可见性缓冲区**，每像素存储`InstanceID + TriangleID`这两个整数。材质计算被推迟到第二个Pass，称为**材质求值（Material Evaluation）**：系统按材质类型将像素分类，批量在Compute Shader中根据重心坐标插值顶点属性，再执行材质图表中的逻辑。这种架构使几何渲染成本与材质复杂度完全解耦，场景中使用100种不同材质不会增加几何Pass的开销。

### 4. 流送与压缩

Nanite资产在磁盘上以自定义的**层级页（Hierarchical Page）**格式存储，运行时按需从磁盘或内存池中流入GPU显存。压缩方面，Nanite对顶点位置使用**量化编码**（通常16位整数），对Cluster层级数据使用差分编码，使同等精度网格体相比原始FBX/OBJ体积减少约60%至80%。

---

## 实际应用

**静态建筑与地形场景**是Nanite最典型的应用场景。在Matrix Awakens技术演示中，整个纽约街区场景的建筑外立面、地面铺装均使用了Nanite网格体，单帧多边形调用量超过**9亿个三角形**，而GPU帧时间维持在16ms以内（60fps目标）。

**Photogrammetry扫描资产**是另一核心应用：现实世界的岩石、建筑废墟等扫描模型通常包含数十至数百万面，以往必须经过大量减面处理才可用于实时渲染。使用Nanite后，开发者可将原始扫描网格体（例如Quixel Megascans资产库中的单个岩石模型，约120万面）直接启用Nanite选项后导入，引擎自动构建Cluster层级，无需额外处理。

**限制场景**同样需要了解：Nanite当前不支持蒙皮骨骼动画网格体（Skeletal Mesh）、世界位置偏移（WPO，如树叶摆动）较复杂的材质，以及半透明材质。对于这些类型，仍需使用传统网格体和LOD系统。UE5.1之后逐步开始支持有限的WPO，但有性能和精度上的额外限制。

---

## 常见误区

**误区一：Nanite会渲染网格体的所有多边形**。实际上，Nanite在任何情况下都只渲染投影面积约等于1像素的那一层级的Cluster，多边形总数的增加对运行时成本的影响远小于传统管线。真正影响性能的是**屏幕分辨率**和**Overdraw**（遮挡剔除质量），而非原始面数。

**误区二：Nanite取代了所有LOD需求**。对于角色、植被等使用Skeletal Mesh或需要WPO的资产，Nanite无法启用，传统手工LOD和Imposter（公告板）技术依然不可或缺。将所有资产无差别启用Nanite是错误的工作方式。

**误区三：Nanite对显存没有额外要求**。Nanite的流送系统依赖一个可配置的GPU显存池（默认为**512MB**，可在`r.Nanite.Streaming.PoolSize`中调整），若场景极端复杂导致池溢出，系统会降级到更粗粒度的Cluster，出现短暂的几何精度下降，需要根据目标平台显存合理配置。

---

## 知识关联

**前置概念——UE5模块系统**：Nanite作为独立渲染模块存在于`Engine/Source/Runtime/Renderer/Private/Nanite/`目录下，其初始化、资产构建（NaniteBuilder）与运行时Pass均通过UE5的模块接口与渲染器主流程解耦。理解UE5模块系统的接口注册机制有助于阅读Nanite源码中`INaniteSceneExtension`等扩展点。

**后续概念——GPU驱动渲染**：Nanite的Cluster可见性剔除、软件光栅化、材质求值全部发生在GPU的Compute Shader中，CPU几乎不参与Per-Cluster决策，这正是GPU驱动渲染（GPU-Driven Rendering）架构的典型实践。学习GPU驱动渲染时，Nanite的`CullRasterize`Pass是一个极佳的具体参考：它展示了如何用`IndirectDispatch`、原子操作和GPU持久化线程实现完全去CPU化的几何管线。