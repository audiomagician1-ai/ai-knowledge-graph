---
id: "cg-lod"
concept: "LOD系统"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 40.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# LOD系统

## 概述

LOD（Level of Detail，细节层次）系统是一种根据物体与摄像机的距离或屏幕占用面积，动态切换或过渡不同多边形密度网格的几何处理技术。其核心思想是：距离摄像机越远的物体，其几何细节对最终画面的贡献越小，因此可以用更低面数的代理网格来替代，从而节省GPU的顶点处理和光栅化开销。

LOD概念最早由James Clark于1976年在论文《Hierarchical Geometric Models for Visible Surface Algorithms》中系统提出，随后在1980年代的飞行模拟器中得到工业级应用。Unreal Engine 1（1998年发布）将LOD系统内置为引擎标准功能，标志着实时游戏引擎对该技术的全面采纳。

LOD系统的重要性体现在具体的性能数据上：一个典型的开放世界场景可能同时存在数千个静态网格体，若全部使用LOD0（最高精度）渲染，顶点数可轻易超过一亿；引入LOD后，可将平均渲染顶点数压缩至LOD0的15%–30%，帧渲染时间（Frame Time）显著降低。

---

## 核心原理

### 离散LOD（Discrete LOD）

离散LOD是最经典的实现形式：美术或自动化工具预先生成若干固定精度的网格版本，通常命名为LOD0、LOD1、LOD2、LOD3，每级多边形数量按比例递减，例如 LOD0:5000面、LOD1:1500面、LOD2:400面、LOD3:80面。

引擎通过计算**屏幕覆盖率（Screen Coverage）**来决定当前使用哪一级：

$$\text{Coverage} = \frac{A_{\text{proj}}}{A_{\text{screen}}}$$

其中 $A_{\text{proj}}$ 为物体包围盒在屏幕上的投影面积，$A_{\text{screen}}$ 为屏幕总像素面积。当Coverage低于某阈值（如0.02，即2%）时，系统切换到下一级LOD。离散切换会导致视觉上的**"跳变"（Popping）**问题，常用Cross-Fade（透明度交叉淡化）或Dithering（抖动溶解）来遮蔽切换边界。

### 连续LOD（Continuous LOD / CLOD）

连续LOD不使用预生成的固定版本，而是通过**渐进网格（Progressive Mesh）**算法（Hugues Hoppe，1996年SIGGRAPH）在运行时动态调整多边形数量。该算法将网格的每一次边折叠（Edge Collapse）操作记录为一条可逆记录，形成从最简到最复杂的完整拓扑序列，允许以任意整数面数表示同一物体。

相比离散LOD，连续LOD消除了视觉跳变，但代价是需要在CPU/GPU上实时执行边折叠或顶点分裂操作，计算成本更高。实时连续LOD在早期硬件上难以普及，现代实现通常将其与GPU曲面细分（Tessellation）结合，在顶点着色器阶段动态插值细节。

### HLOD（Hierarchical LOD）

HLOD在离散LOD的基础上引入**空间聚合**概念：将场景中距离极远的多个独立物体（如一片森林中的数百棵树）合并烘焙成一个单一的低模网格，作为该区域的超远距代理。Unreal Engine 4.14版本正式引入HLOD工具，可将数千个Actor自动聚合为若干HLOD代理网格，将Draw Call数量从数千降低到个位数。

HLOD的生成过程包含三个关键步骤：
1. **空间聚类**：基于八叉树或BVH将场景物体分组；
2. **网格合并**：将同组物体的几何体合并并重新UV展开；
3. **贴图烘焙**：将各物体的材质信息烘焙到合并后的单张Atlas贴图上（分辨率通常为512×512到4096×4096）。

HLOD切换发生在摄像机距离数百米乃至数公里处，此时单个像素覆盖大量场景内容，几何精度的损失几乎不可察觉。

---

## 实际应用

**开放世界游戏**：《荒野大镖客：救赎2》使用了四级离散LOD加HLOD的组合管线，远景的城镇、山脉等场景使用HLOD代理渲染，近景物体才切入LOD0。

**Unreal Engine工作流**：在UE5中，静态网格体编辑器默认提供4个LOD槽，LOD1–LOD3可通过内置的简化算法（基于Quadric Error Metrics，即QEM算法）自动生成。QEM算法通过最小化每次边折叠引入的几何误差（用二次误差矩阵 $Q$ 量化）来保留最重要的几何特征，生成视觉质量较高的简化网格。

**移动端优化**：移动端GPU顶点处理能力有限，LOD切换阈值通常比PC端提高2–3倍，即更激进地在较近距离就降级到低模，确保顶点吞吐量不成为瓶颈。

---

## 常见误区

**误区一：LOD级别越多越好**

增加LOD级别会提升内存占用（网格数据需全部驻留显存），并增加Level Designer手动调整阈值的工作量。实践中大多数中小型物体使用3–4个LOD级别已足够，过多的LOD级别带来的渲染节省往往不足以抵消内存和管理成本。

**误区二：LOD切换只与距离相关**

实际上，距离仅是屏幕覆盖率的间接影响因素。视野（FOV）变化同样影响屏幕覆盖率：当FOV从60°增大到90°时，同一物体的屏幕占用面积显著缩小，可能触发LOD降级。部分引擎还引入了**LOD Bias**参数，允许在不修改阈值的情况下全局偏移LOD选择，用于快速调节画质与性能的平衡。

**误区三：HLOD可以完全替代离散LOD**

HLOD处理的是极远距离的跨物体聚合问题，无法替代单个物体自身从近到中距离的精度过渡。在实际管线中，两者必须协同工作：近距离由各物体自身的离散LOD管理，超远距离才由HLOD接管。

---

## 知识关联

**前置概念**：几何处理概述中涉及的网格表示（半边结构、索引缓冲区）是理解LOD如何存储多个精度版本的基础；网格简化算法（QEM等）是LOD自动生成的核心工具。

**后续概念**：Nanite架构（UE5）可视为连续LOD思想的极端延伸，它将每个网格体分解为数以万计的Cluster，通过GPU驱动的运行时选择机制实现"无限LOD"，从而取消了预生成固定级别的必要。替身技术（Impostor）在HLOD的基础上更进一步，用摄像机对齐的广告牌+预烘焙法线/深度信息来替代极远处的三维几何体。网格流式加载（Mesh Streaming）则解决了LOD系统中不同精度网格如何按需从磁盘加载到显存的带宽管理问题，与LOD切换逻辑紧密耦合。