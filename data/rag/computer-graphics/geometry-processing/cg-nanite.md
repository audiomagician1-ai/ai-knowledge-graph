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
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# Nanite架构

## 概述

Nanite是Epic Games在虚幻引擎5（UE5）中于2022年正式发布的虚拟几何体（Virtualized Geometry）系统，其核心目标是消除传统LOD工作流程中艺术家手动制作多级细节模型的需求。Nanite允许导入数亿乃至数十亿三角形的原始影视级资产（如Quixel扫描资产），并在运行时自动按像素级精度调度所需的几何细节，使得屏幕上每个像素背后的三角形数量趋近于1:1对应关系。

Nanite的设计直接源于电影行业的微多边形（Micropolygon）渲染思想，类似于皮克斯RenderMan所用的REYES算法，但Nanite将这一思路移植到了实时GPU环境中。与传统LOD系统依赖预先烘焙的固定几何级别不同，Nanite在GPU上执行完全动态的层级裁剪与细分，无需CPU参与每帧的LOD切换决策。

Nanite之所以重要，在于它彻底改变了游戏美术资产的制作流程：艺术家不再需要为同一模型制作LOD0到LOD4等多个版本，也不需要手动绘制法线贴图来伪造高频几何细节——直接使用高精度扫描网格即可。对于拥有数十万个静态网格物体的开放世界场景，这一特性节省了巨大的人力成本。

## 核心原理

### 层级簇（Cluster Hierarchy）与BVH结构

Nanite在离线预处理阶段将原始网格切割为由约128个三角形组成的**簇（Cluster）**。多个簇被进一步合并为簇组（Cluster Group），簇组再向上形成层级BVH（Bounding Volume Hierarchy）树。这棵树的每一层都预先计算了在特定屏幕误差（Screen Error）阈值下应使用哪一级的几何表示。

每个簇存储了父簇和子簇的屏幕空间投影误差上下界，GPU在每帧执行**持续LOD（Persistent LOD）**遍历时，通过判断当前视点下某节点的投影误差是否落在其父节点误差和自身误差之间，来决定是否渲染该层级的簇。这一判断公式为：

```
父节点误差(像素) > 阈值 ≥ 当前节点误差(像素)
```

满足此条件的节点被称为**切割（Cut）**，保证在整棵树上仅有满足误差约束的叶子级簇被提交渲染，避免重复绘制。

### 软件光栅化（Software Rasterization）

当一个Nanite簇投影到屏幕后面积极小（通常三角形覆盖面积小于32像素），硬件光栅化的固定管线开销（如三角形设置、属性插值）相对于实际像素填充量而言极其昂贵。为此，Nanite实现了完全在Compute Shader中运行的**软件光栅化器**，直接以原子操作写入64位深度-材质ID组合缓冲（Visibility Buffer）。

软件光栅化的核心是利用GPU Compute的线程灵活性：一个Wave（Warp）中的32个线程可以共同处理单个三角形的所有像素，消除了硬件光栅化中因小三角形导致的线程利用率（Occupancy）低下问题。实测中，软件光栅化处理微小三角形的吞吐量比硬件光栅化快约2至4倍。

### Visibility Buffer与延迟材质求值

Nanite不使用传统的G-Buffer流程。光栅化阶段仅向**Visibility Buffer**写入每像素的实例ID和三角形ID（64位整数打包存储），材质参数（法线、粗糙度、颜色等）在一个独立的延迟Pass中按材质分组批量求值。这种设计将几何处理与着色完全解耦，使得数百万个三角形的可见性判定只需极少量内存带宽——Visibility Buffer仅需每像素8字节，而传统多层G-Buffer通常需要每像素64至128字节。

## 实际应用

**开放世界岩石与建筑资产**：《黑神话：悟空》等使用UE5的游戏直接导入Quixel Megascans的原始扫描网格（单个资产可达500万至1500万三角形），无需手动减面。Nanite在运行时根据摄像机距离和屏幕占比自动控制实际渲染的簇数量，使场景总三角形预算保持稳定。

**大规模植被场景**：Nanite 5.1版本开始支持带遮罩的材质（Masked Materials），允许树叶等需要alpha测试的几何体也进入Nanite流程，解决了早期版本只能处理不透明材质的限制。

**考古与文化遗产可视化**：Nanite被用于实时展示通过摄影测量重建的文物三角网格（精度可达亿级三角形），单帧内可同时呈现完整的场景与微观表面细节，无需预先LOD手工干预。

## 常见误区

**误区一：Nanite替代了法线贴图**。实际上Nanite处理的是几何层面的细节，而不是光照层面的高频细节。对于微观表面粗糙度、毛孔、划痕等视觉效果，仍然需要法线贴图配合PBR着色。Nanite解决的是"LOD切换"问题，而非"法线贴图烘焙"问题——两者针对的几何频率范围不同，前者关注厘米级形状变化，后者关注毫米级光照变化。

**误区二：Nanite适用于所有几何体**。Nanite当前版本（UE 5.3）不支持蒙皮网格（Skeletal Mesh）、地形（Landscape）以及需要世界位置偏移（World Position Offset）的动态变形材质。将大量动态角色尝试通过Nanite渲染会失败并回退至传统管线。此外，Nanite对单个簇128个三角形的硬性约束意味着拓扑极不规则的网格（如过度细碎的边缘）会导致簇质量下降、层级压缩效率降低。

**误区三：Nanite场景多边形数量无限**。Nanite管理的是**屏幕像素级的细节预算**，而非绕过GPU的三角形吞吐限制。如果场景中同时存在大量接近摄像机的Nanite对象，每个对象都需要渲染高密度簇，GPU的光栅化带宽同样会成为瓶颈。Nanite的优势在于远处几何体的自动降级，而非近处超高密度几何的免费渲染。

## 知识关联

Nanite架构是对传统**LOD系统**的根本性延伸：传统LOD在CPU侧按距离切换固定级别的预制网格，而Nanite将这一决策移至GPU侧，并以128三角形的簇为最小粒度实现连续精度调节，消除了LOD切换时的几何跳变（Popping）问题。理解传统LOD中屏幕空间误差（SSE）的计算方式是理解Nanite簇切割判断逻辑的直接前提。

在渲染管线层面，Nanite的Visibility Buffer方案与**延迟渲染（Deferred Rendering）**有本质区别：延迟渲染在几何Pass就填充完整材质属性，而Nanite仅存储最小化的可见性信息并在后续重新求值，可视为**超延迟（Hyper-Deferred）**架构。这与光线追踪的GBuffer重用策略形成了有趣的对比——两者都试图将几何可见性与着色计算解耦，但执行路径截然不同。