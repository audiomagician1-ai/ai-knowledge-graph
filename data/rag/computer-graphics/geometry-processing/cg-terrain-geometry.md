---
id: "cg-terrain-geometry"
concept: "地形几何"
domain: "computer-graphics"
subdomain: "geometry-processing"
subdomain_name: "几何处理"
difficulty: 3
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 地形几何

## 概述

地形几何是图形学中专门处理大规模地表数据表示与渲染的技术体系，其核心挑战在于以有限的三角形预算表达跨越数公里乃至数百公里的地形细节。与一般网格不同，地形几何天然具有高度场（Height Field）属性——每个水平坐标 (x, z) 对应唯一的垂直高度 y，这一约束使得 2.5D 的高度图成为最主流的底层数据结构。

地形几何的现代技术框架成形于 1990 年代末期。1997 年 Seumas McNally 提出 ROAM（Real-time Optimally Adapting Meshes）算法，首次将二叉三角树用于地形细分；2004 年 Losasso 与 Hoppe 在 SIGGRAPH 上发表了 Geometry Clipmaps 方案，奠定了现代引擎地形渲染的基础结构。Unreal Engine、Unity 等主流引擎的地形模块均在这两条技术路线上演进。

地形几何之所以在游戏与仿真中不可或缺，是因为它必须同时满足三个相互矛盾的需求：远距离低面数、近距离高细节、帧间连续无跳变。解决这三者之间的张力，正是高度图、Clipmap 与自适应网格三类方案分别着力的方向。

---

## 核心原理

### 高度图（Heightmap）

高度图是一张灰度图像，其像素值直接映射为地表高度。对于一张分辨率为 N×N 的高度图，地形顶点数为 N² 个，三角形数为 2×(N-1)² 个。常见的存储格式为 16 位无符号整数（uint16），可表示 65536 级高度精度，对应真实世界精度约为 1cm（当总高差设定为 655.36m 时）。

高度图读取顶点高度的公式为：

$$h(x,z) = \text{texel}(x,z) \times \frac{H_{max}}{65535}$$

其中 $H_{max}$ 为地形最大高差，$\text{texel}(x,z)$ 为对应像素的原始整数值。高度图的优势在于 GPU 可直接在顶点着色器中通过纹理采样驱动顶点位移，省去 CPU 上传几何数据的带宽开销。缺陷在于它无法表示垂直悬崖或洞穴等高度不唯一的地貌。

### Geometry Clipmap

Clipmap 方案将地形划分为以摄像机为中心的多级同心环形区域，每一级的纹素世界尺寸是内层的 2 倍，类似 Mipmap 的 LOD 层级思想但专为地形定制。Losasso & Hoppe 的原始论文使用了 $k$ 层 Clipmap，每层固定为 $n \times n$ 个顶点（典型值 $n=255$），外层顶点间距是内层的 2 倍。

Clipmap 的关键实现步骤包括：
1. **环形更新（Toroidal Update）**：摄像机移动时，仅更新即将进入视野的边缘数据条带，而非重载整层，带宽需求降至 $O(n)$ 而非 $O(n^2)$；
2. **裙边过渡（Skirt / Transition Region）**：相邻 LOD 层之间设置约 $n/4$ 宽度的过渡区域，通过顶点混合避免 T 形接缝（T-junction）产生的裂缝；
3. **GPU Clipmap**：在现代实现中，整个 Clipmap 层级存储于 Texture Array 或 Virtual Texture 中，顶点着色器按层索引采样，完全绕过 CPU 几何更新。

### 自适应网格（Adaptive / Tessellation-based Mesh）

自适应网格根据屏幕空间误差（Screen-Space Error, SSE）动态调整三角形密度。基本判据为：

$$\text{SSE} = \frac{\delta \cdot f}{d}$$

其中 $\delta$ 是几何误差（简化后顶点偏离真实高度的最大值，单位米），$f$ 是近裁平面焦距（像素/米），$d$ 是该区块到摄像机的距离。当 SSE 超过阈值（通常设为 1~2 像素）时触发细分。

现代 GPU 管线中，DirectX 11 引入的 Hull Shader + Domain Shader 可在 GPU 侧动态细分四边形 Patch，Unreal Engine 的 Nanite 虚拟几何体也对地形提供了类似的微三角形级细化方案。相比 CPU 端的 ROAM 或四叉树，GPU Tessellation 将细分决策延迟至光栅化阶段，减少了 CPU-GPU 通信瓶颈。

---

## 实际应用

**《荒野大镖客：救赎 2》**的地形系统使用了分辨率约 8km×8km、单像素精度 0.25m 的地形格网，结合 Virtual Heightfield Mesh 技术，实现了视差遮蔽与真实几何的混合细节表现。

**Unreal Engine 5 的 Landscape 系统**将地形划分为多个 Component，每个 Component 默认由 $63\times63$ 个顶点构成一个 LOD 单元，支持 7 级 LOD，最低 LOD 面数仅为最高级的 1/64。地形高度图以 16 位精度存储于专用的 .uasset 格式，法线贴图则由引擎实时从高度图导数计算生成。

在地形编辑工具中，高度图笔刷半径与衰减曲线直接影响雕刻平滑度；Clipmap 的层数设置（如从 5 层增至 7 层）会将最远可见地形距离提高 4 倍但同时使显存占用翻倍，这是实际项目中常见的权衡点。

---

## 常见误区

**误区一：高度图精度越高越好**
将高度图从 8 位升级到 16 位可消除"台阶感"（Quantization Artifact），但继续升级到 32 位浮点在大多数地形场景中并无收益——标准 16 位在 1000m 高差下已有约 1.5cm 的垂直精度，超出了地表建模的实际需求，反而浪费显存带宽。

**误区二：Clipmap 与 Mipmap 完全相同**
Mipmap 是预计算的固定级别纹理，读取时只需索引。Clipmap 是以摄像机位置为中心的**动态裁切区域**，必须在摄像机移动时进行增量更新。二者的采样逻辑与 GPU 缓存行为存在本质差异：Mipmap 由驱动自动管理，Clipmap 需要应用层显式维护每层的有效数据窗口和脏区域标记。

**误区三：自适应网格必然消除所有 LOD 接缝**
基于四叉树或二叉树的自适应细分，若未正确实现"强制相邻等级差不超过 1"（T-crack restriction），粗粒度与细粒度块交界处仍会出现可见裂缝。ROAM 算法通过"菱形队列"维护相邻约束，Clipmap 通过裙边过渡区解决，但简单的四叉树 LOD 实现如果遗漏了这步修复，渲染结果会出现明显的三角形空洞。

---

## 知识关联

从**几何处理概述**的视角来看，地形几何是高度场约束下的网格简化（Mesh Simplification）与细化（Refinement）的特化应用，其 SSE 误差度量与通用 LOD 中的 QEM（Quadric Error Metrics）在思路上一脉相承，但地形的规则格网结构使得细分树维护成本远低于任意拓扑网格。

后续**植被渲染**模块将直接依赖地形几何输出的两类数据：一是顶点高度与法线，用于确定植株放置的坐标和朝向；二是地形 LOD 信息，用于剔除远处不可见地块上的植被实例（GPU Instancing Culling）。植被密度贴图（Density Map）在坐标系上与高度图共享同一 UV 空间，因此高度图的分辨率和世界尺度设置直接决定了植被散布的精度上限。
