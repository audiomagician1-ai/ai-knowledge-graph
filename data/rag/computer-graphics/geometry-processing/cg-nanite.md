---
id: "cg-nanite"
concept: "Nanite架构"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 4
is_milestone: false
tags: ["前沿"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Nanite架构

## 概述

Nanite是Epic Games在虚幻引擎5（UE5，2022年正式发布）中引入的虚拟几何体系统，其核心目标是让场景中每个三角形都足够小以接近像素级别，从而彻底消除传统LOD切换时的视觉跳变问题。与传统LOD系统不同，Nanite不需要美术手动制作多级LOD资产，而是在运行时通过软件光栅化管线自动决定每个区域应该渲染多少几何细节。这一技术使得UE5的演示场景《The Matrix Awakens》能够实时渲染超过3500万个多边形的城市环境，而无需手工优化每个资产。

Nanite的设计思路来自虚拟纹理（Virtual Texture）的类比：正如虚拟纹理只将当前可见的纹理Mip层级页面加载到GPU显存一样，Nanite只将摄像机当前视角下需要的几何细节级别"流式传输"到渲染管线。这一概念在学术上与Hugues Hoppe于1996年提出的"渐进网格"（Progressive Meshes）理论有渊源，但Nanite在工程实现上走了完全不同的路径——它依赖GPU驱动渲染（GPU-Driven Rendering）而非CPU端的LOD选择。

## 核心原理

### 簇层次结构（Cluster Hierarchy）

Nanite在离线预处理阶段将原始网格切分为每组128个三角形的**簇（Cluster）**，再将若干簇组合为更粗粒度的**簇组（Cluster Group）**，并递归构建成一棵BVH（层次包围盒）树形结构。每一层级都存储了该层级的误差度量值（Error Metric），该值定义为：将粗一级几何体替换当前精细几何体时，在屏幕上产生的最大像素误差（单位：像素）。运行时遍历这棵树时，Nanite以屏幕空间误差阈值（默认为1像素）作为截止条件，确保任何可见三角形投影到屏幕后面积都不超过1个像素。

### 软件光栅化（Software Rasterization）

对于覆盖面积极小的三角形（通常是屏幕空间面积小于一定阈值的三角形），Nanite绕过GPU的固定功能硬件光栅化单元，改用Compute Shader实现的**软件光栅化**。这是因为现代GPU的硬件光栅化管线对每个三角形有固定的调度开销（约64个着色线程的最小粒度），当三角形极小时，硬件光栅化的利用率极低。Nanite的软件光栅器直接以原子操作写入深度与VisBuffer，避免了硬件三角形设置（Triangle Setup）阶段的开销。实测中，在高多边形密度场景下，软件光栅化路径可处理超过85%的三角形数量。

### 可见性缓冲区（VisBuffer）与延迟材质求值

Nanite不直接输出GBuffer，而是先渲染一张**VisBuffer**（可见性缓冲区），每个像素存储的是三角形ID和实例ID，而非颜色或法线。材质着色在完全确定可见性之后，以一个独立的Compute Pass针对每种材质批量执行，即"材质深度分类"（Material Depth Classification）技术。这样每个像素的材质着色只执行一次，与传统延迟渲染相比消除了Overdraw导致的重复着色开销。VisBuffer的每像素存储量仅需64位（32位三角形索引 + 32位实例索引）。

### 流式加载与虚拟几何体页面

Nanite将簇数据按页面（Page，约128 KB大小）组织，并实现了类似虚拟纹理的按需流式加载机制。GPU在每帧渲染结束后回读一个反馈缓冲区（Feedback Buffer），告知CPU哪些页面在即将到来的帧中是必需的，CPU据此从磁盘或内存池中调度加载。这使得单个场景可以引用总量远超GPU显存容量的几何数据，常见项目中单场景Nanite数据可达数十GB。

## 实际应用

在游戏《黑神话：悟空》（2024年发布，使用UE5）中，岩石、植被和建筑构件均以Nanite网格导入，美术只需提供一份高精度扫描模型（通常每资产数百万三角形），Nanite自动生成所有细节层级。由于Nanite要求不透明且无顶点动画的静态网格，植物的风吹摆动效果需通过World Position Offset（WPO）节点实现，但WPO在Nanite中仅支持有限的变形幅度（超出簇包围盒范围则会出现裁剪错误）。

在影视实时预览流程（如Epic的MetaHuman影视制作）中，Nanite使得每帧可推送约1亿个三角形的建筑与环境资产，而GPU帧时间仅增加约2毫秒，相比传统LOD工作流节省了美术团队数周的LOD制作时间。

## 常见误区

**误区一：Nanite可以渲染任意类型的网格。** 实际上，Nanite在UE5.0至5.2版本中仅支持不透明（Opaque）静态网格，半透明材质、蒙皮骨骼网格和地形（Landscape）均不受支持。UE5.3开始实验性支持部分蒙皮网格，但需要显式开启且存在精度限制。将带透明通道的植物叶片直接标记为Nanite会导致透明区域错误填充。

**误区二：Nanite等同于无限多边形，不需要优化导入网格。** Nanite确实自动降级，但过度冗余的网格（如CAD导入的曲面细分网格，相邻三角形误差为0）会导致最高细节层的簇数量爆炸，占用大量显存和流式带宽。建议导入网格在最高LOD下控制在单个资产500万三角形以内，并确保网格满足流形（Manifold）条件，否则Nanite的簇边界缝合算法会产生裂缝。

**误区三：Nanite的软件光栅化比硬件光栅化慢。** 这一判断忽略了三角形尺寸分布的前提。对于屏幕空间面积大于约4×4像素的三角形，Nanite实际上切换回硬件光栅化路径，软件光栅化只针对微小三角形。两条路径的分发是在Per-Cluster的Compute Shader中根据投影包围盒面积动态判断的，而非统一使用软件路径。

## 知识关联

理解Nanite需要先掌握**LOD系统**中的误差度量概念——Nanite的屏幕空间误差阈值本质上是传统LOD切换距离计算的像素空间推广，LOD系统中的Simplygon/MeshSimplifier简化算法也是Nanite离线预处理阶段的技术基础。Nanite的VisBuffer机制与**延迟渲染（Deferred Rendering）**的GBuffer思路互补：延迟渲染解决了光照与几何的解耦，而VisBuffer进一步将材质求值与可见性判定解耦。此外，Nanite的GPU驱动渲染架构依赖**GPU Culling**（GPU端剔除）技术——簇层次结构的遍历和剔除完全在Compute Shader中完成，不依赖CPU DrawCall，这与Multi-Draw Indirect等现代图形API特性紧密关联。
