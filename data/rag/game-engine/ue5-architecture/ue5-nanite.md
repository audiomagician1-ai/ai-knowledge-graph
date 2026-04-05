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


# Nanite虚拟几何体

## 概述

Nanite是虚幻引擎5（UE5）中引入的虚拟化几何体技术，其核心能力是将数亿乃至数十亿个多边形的高精度网格体实时渲染到屏幕上，同时将GPU绘制调用（Draw Call）的开销压缩到几乎可以忽略不计的程度。Nanite的设计哲学借鉴了虚拟纹理（Virtual Texture）的分层流送思路，将其移植到几何体领域：只有屏幕上实际可见的像素所对应的几何细节，才会从磁盘或内存中加载并提交到GPU光栅化管线。

Nanite技术首次公开亮相于2020年Epic Games发布的《虚幻引擎5早期访问版》演示视频《Lumen in the Land of Nanite》，该演示中Valley of the Ancient场景使用了超过5000万个多边形的山谷地形和建筑资产，全部由Nanite实时渲染。在此之前，游戏引擎普遍依赖美术人员手工制作多层LOD（Level of Detail）模型，每降一级LOD通常需要减少50%左右的面数，这既耗费大量人力，又无法精确匹配屏幕像素密度。

Nanite的重要性在于，它将游戏引擎的几何复杂度上限从"硬件与优化技术共同约束"的数百万面，直接推进到电影级CG资产所用的亿级面，从而使Quixel Megascans之类的扫描级高精度资产无需简化即可直接导入引擎使用。

## 核心原理

### 层级簇（Cluster Hierarchy）与BVH加速结构

Nanite在导入资产时会离线预处理网格体，将整个Mesh切分成若干个**簇（Cluster）**，每个簇固定包含**128个三角形**。随后对这些簇进行层级分组，构建出一棵类似BVH（包围体层次结构）的**DAG（有向无环图）**——父节点对应简化后的低精度簇，子节点对应原始高精度簇。这棵层级树会存储为压缩格式，并在运行时按需流送到显存。

渲染时，Nanite的可见性判断阶段（Visibility Pass）在GPU上并行遍历整棵DAG，对每个节点计算其**屏幕空间投影误差（Projected Error）**：若某节点的投影误差小于1像素（即父节点细节已足够），则停止向该子树继续展开，直接使用当前节点的低精度簇。这一剪枝策略保证了最终提交光栅化的三角形数量始终与屏幕分辨率成正比，而非与场景总面数成正比。

### 软件光栅化（Software Rasterization）

对于屏幕上面积极小的三角形（小于约4个像素），Nanite会绕开传统的硬件光栅化管线，转而使用**计算着色器（Compute Shader）**执行软件光栅化。这是因为GPU硬件光栅化对亚像素三角形存在严重的波前浪费（Wavefront Waste）——一个2x2像素的最小计算单元（Quad Overdraw）可能只有1个像素被实际覆盖，效率仅为25%。Nanite的软件光栅化路径通过原子操作直接写入深度缓冲区（Depth Buffer），规避了这一浪费，在微多边形密集的场景中性能提升可达数倍。

### 材质求值延迟（Deferred Material Evaluation）

Nanite使用**两阶段材质系统**：第一阶段仅完成可见性判断，将每个像素对应的Nanite实例ID与三角形ID写入一张**Visibility Buffer**（又称V-Buffer）；第二阶段再对V-Buffer中记录的信息进行批量材质求值。这与传统G-Buffer延迟渲染的区别在于，Nanite先知道哪个像素最终可见，再进行着色计算，彻底消除了深度测试前的冗余着色（Overdraw Shading）。每个像素的材质求值恰好执行且仅执行一次。

## 实际应用

**静态场景资产直接使用扫描数据：** Quixel Megascans提供的石块、建筑墙面等资产原始精度可达数千万面，开启Nanite后可不经LOD制作直接拖入场景。UE5官方建议对面数超过约**30万个三角形**的静态网格体启用Nanite，以获得最佳性价比。

**大规模地形植被：** 在《黑神话：悟空》等采用UE5开发的商业项目中，岩石、枯树等静态植被资产大量启用Nanite，通过Nanite的自动LOD裁剪替代了以往需要美术手工制作4~5级LOD的流程，单个场景的美术制作时间缩短约40%。

**局限场景——动态蒙皮网格：** Nanite目前（UE5.3版本）**不支持蒙皮骨骼动画**（Skeletal Mesh）和启用了世界位置偏移（World Position Offset）动画的材质（部分实验性支持已在5.2加入）。角色主体、布料、粒子特效等仍需传统LOD流程处理。此外，Nanite对**半透明材质**同样不支持，水面与玻璃等资产需要使用普通网格体渲染路径。

## 常见误区

**误区一："Nanite会自动提升所有网格体的渲染性能"**
实际上，对低多边形网格体（例如面数少于1万的简单道具）启用Nanite反而会引入额外的Cluster处理与流送开销，性能可能低于传统静态LOD方案。Nanite的收益只有在高精度网格体需要跨越多个LOD层级、且场景中同类资产实例数量众多时才能充分体现。

**误区二："Nanite渲染的三角形数量等于原始资产的面数"**
Nanite在每一帧提交给光栅化的实际三角形数量由屏幕投影误差阈值动态决定，通常远小于资产原始面数。Epic官方数据显示，在典型游戏场景中，Nanite最终光栅化的三角形数量与屏幕像素数量处于同一数量级（约为屏幕像素数的1~2倍），而非原始场景几何体的总面数。

**误区三："Nanite替代了LOD系统，因此不需要关心资产面数"**
在Nanite的Cluster构建阶段，超高面数资产会产生更大的磁盘占用和更长的离线预处理时间（Import时间）。一个原始面数5000万的资产，其Nanite预处理数据体积可能达到原始FBX的3~4倍，并在首次导入时消耗数分钟CPU计算时间。资产面数管理的关注点从"运行时性能"转移到了"存储与导入成本"，而非完全消失。

## 知识关联

Nanite的流送机制与UE5模块系统中的**资产管理器（Asset Manager）**和**块加载（Chunk Loading）**模块直接交互——Nanite簇数据以独立Chunk的形式注册到引擎的IOStore打包系统中，运行时由后台IO线程按需异步加载到显存，与普通静态网格体的整体加载模式有本质不同。理解UE5的模块化资产管理，是分析Nanite流送延迟与显存占用的前提。

在掌握Nanite的可见性判断与软件光栅化原理之后，可以进一步学习**GPU驱动渲染（GPU Driven Rendering）**的完整管线。Nanite的Persistent Culling Pass本质上就是一套GPU Driven Culling的具体实现：CPU只提交场景图节点列表，所有剔除、LOD选择、Draw Call生成全部由GPU上的Compute Shader完成。GPU驱动渲染将这一思路推广到非Nanite网格体、粒子、光源等更广泛的渲染对象，形成完整的间接绘制（Indirect Draw）架构。