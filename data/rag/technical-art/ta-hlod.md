---
id: "ta-hlod"
concept: "HLOD系统"
domain: "technical-art"
subdomain: "lod-strategy"
subdomain_name: "LOD策略"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
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

# HLOD系统

## 概述

HLOD（Hierarchical Level of Detail，层级细节）系统是一种针对大规模开放世界场景优化的渲染技术，其核心做法是将空间上相邻的多个独立物体在超过特定距离后合并为单一的"代理网格"（Proxy Mesh），从而将原本数十乃至数百个DrawCall压缩为一个。与普通LOD仅对单个物体进行网格简化不同，HLOD的层级结构意味着多个物体会被统一纳入一个空间簇（Cluster），整体替换为更粗糙的合并表示。

HLOD概念最早在游戏工业中被大规模采用，是在Unreal Engine 4.13（2016年发布）引入内置HLOD构建工具之后。在此之前，开发团队需要手工制作"远景模型"来模拟类似效果，耗时且难以维护。UE4的HLOD系统将建筑群、道具群等物体按照八叉树（Octree）空间划分自动分组，生成合并的代理网格与合并贴图（Merged Material Atlas），大幅降低了大地图的渲染开销。

HLOD的重要性在于它直接攻克了开放世界场景的"DrawCall爆炸"问题。以一个包含10,000个静态网格体的城镇区域为例，若每个物体保持独立渲染，即使在500米外它们的屏幕占比已低于1个像素，GPU仍然需要处理全部的Draw命令。HLOD将这类远景物体合并后，同等场景的DrawCall数量可降低60%~90%，这对主机和移动端的CPU负担尤为关键。

## 核心原理

### 空间簇划分与层级树结构

HLOD系统在构建阶段将场景划分为层级式的空间簇。在UE5的World Partition系统中，HLOD层级从Level 0开始，每升一级空间覆盖范围翻倍，LOD0簇边长通常为51200厘米（512米），Level 1簇覆盖1024米。每个簇内的静态网格体在烘焙时被合并成一个代理网格，当摄像机距离该簇超过设定的屏幕尺寸阈值（默认为0.01，即屏幕高度的1%）时，引擎切换到该HLOD代理，而非渲染簇内所有原始物体。

### 代理网格生成算法

代理网格的生成过程包含两个关键步骤：**网格合并（Merge）** 与 **网格简化（Simplify）**。合并阶段将簇内所有物体的顶点坐标变换至世界空间后拼接为一个超级网格（Super Mesh），材质也被烘焙为一张或多张Atlas贴图，通常分辨率为2048×2048或4096×4096。简化阶段则对合并后的超级网格应用屏幕空间误差目标（Screen Size Error，默认值为1.0像素），使用Quadric Error Metrics算法减少三角面数，目标面数通常控制在原始簇总面数的5%~15%之间。

### 可见性与切换逻辑

HLOD的切换不依赖于单个物体的屏幕尺寸，而是依赖于整个**簇**的包围盒在屏幕上的投影尺寸。当簇的HLOD代理激活时，引擎同时将该簇内所有原始静态网格体标记为不可见（Cull），避免双重渲染。这一"簇级可见性切换"意味着过渡时所有原始物体同时消失、代理同时出现，因此通常配合Dithered LOD Transition抖动透明度过渡，用约0.3秒的交叉淡入淡出掩盖切换瞬间的突变感。

## 实际应用

**城镇建筑群优化**：在《堡垒之夜》的大地图中，建筑群被划分为多个HLOD簇，每个簇在500米外切换至约2000~5000三角面的代理网格，同时将20余张建筑材质烘焙为一张2048的Atlas。这使得飞行伞降落阶段（俯视整个地图）的DrawCall相比取消HLOD时下降约75%。

**植被与地表物件**：HLOD对密集植被同样有效，但需注意植被的Billboard LOD通常已在单体LOD链中处理，HLOD更适合处理岩石、残骸、建筑装饰等无动画的静态网格体。在UE5中，Nanite几何体目前（5.3版本）不参与HLOD代理生成流程，二者分工明确：Nanite负责近中景几何细节，HLOD负责远景DrawCall合并。

**运行时HLOD（Runtime HLOD）**：UE5的World Partition支持运行时动态加载HLOD数据，玩家在地图上移动时，当前格子之外的区域自动切换至对应级别的HLOD代理网格，无需将完整场景常驻内存，这是超大地图（如《黑神话：悟空》山地场景）得以实现流畅流送的底层支撑之一。

## 常见误区

**误区一：HLOD可以替代单体LOD**。实际上HLOD与单体LOD负责不同距离层级，缺少单体LOD0→LOD2过渡时，物体在进入HLOD簇之前的中距离阶段面数过高，反而增加GPU负担。正确做法是每个静态网格体先完成自身的LOD链（至少3级），再由HLOD接管远距离表示。

**误区二：HLOD代理网格可以在运行时重建**。HLOD代理是**离线烘焙**的产物，存储在专用的HLODLayer资产中。每次场景修改后都需重新运行"Build HLOD"步骤，耗时从数分钟到数小时不等（取决于场景规模）。若开发流程中忽略这一重建步骤，线上版本的HLOD代理将与实际场景不匹配，出现代理与原始物体错位的穿帮现象。

**误区三：HLOD簇划分越小越好**。簇粒度过细会导致DrawCall节省量不足（每簇仅合并3~5个物体），同时产生大量小尺寸Atlas贴图，纹理内存开销反而增大。经验法则是每个HLOD簇在目标切换距离处应覆盖屏幕面积的2%~5%，合并物体数量不低于10个，才能使DrawCall与内存之间的权衡达到最优。

## 知识关联

HLOD系统以**LOD切换策略**为前置知识：理解屏幕空间尺寸阈值（Screen Size Threshold）的计算方式`SS = (ObjectDiameter / Distance) / ScreenHeight`是配置HLOD簇切换距离的基础，否则无法合理设置簇级别的ScreenSize参数。单体LOD中已学习的Dithered过渡、LOD Bias等参数在HLOD层面有直接的对应配置，两套系统共享同一套可见性管理底层逻辑。

HLOD向下衔接**LOD与流送**主题：在UE5 World Partition架构中，HLOD数据本身被封装为可流送的数据资产（HLODLayer Asset），其加载与卸载受到与普通网格流送相同的距离预算管理。掌握HLOD之后，理解流送系统如何按优先级调度HLOD代理、原始网格、Nanite页面三者之间的内存分配，将是顺理成章的下一步。