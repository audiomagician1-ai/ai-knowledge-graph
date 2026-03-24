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
content_version: 4
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

地形几何是实时图形学中专门处理大规模室外地表表示与渲染的技术集合，其核心挑战在于用有限的三角形预算表达数平方公里的连续地面起伏。与静态网格不同，地形数据通常以规则格网（Regular Grid）形式存储，每个格点记录一个垂直高度值，即高度图（Heightmap）。这种结构天然适合GPU并行读取，但在摄像机视角变化时会暴露出严重的细节不均问题：近处三角形过大显得粗糙，远处三角形过密造成浪费。

高度图技术最早在1990年代随着《Comanche》直升机游戏（1992年）的Voxel Space渲染器进入大众视野，彼时以光线投射遍历高度图列。进入可编程着色器时代后，Geometry Shader与曲面细分管线（Tessellation Pipeline，DirectX 11，2009年）将高度图从纯CPU方案转移到GPU驱动的实时细分，使地形几何成为现代开放世界游戏引擎的标准基础设施。

地形几何的重要性体现在性能与视觉质量的精确权衡上：一张4096×4096的高度图若全量展开为三角网格，将产生约3200万个三角形，远超任何实时预算。因此，如何根据视距、坡度和屏幕投影大小动态调整三角形密度，是地形几何研究的根本问题。

---

## 核心原理

### 高度图编码与采样

高度图本质上是一张单通道纹理，灰度值映射到世界空间高度。常见精度为16位（uint16），可表示0到65535个离散高度级，若地形总高度范围为655.35米，则垂直精度恰好为0.01米/级。高度值转换公式为：

$$H_{world} = H_{raw} \times \frac{H_{max} - H_{min}}{65535} + H_{min}$$

其中 $H_{raw}$ 为纹理中的整数值，$H_{max}$ 和 $H_{min}$ 为设计师指定的世界空间高度上下界。法线可由相邻高度差通过中心差分计算：$N_x = H(x-1,z) - H(x+1,z)$，避免存储独立法线图。

### Clipmap 分层结构

Clipmap（裁剪贴图）由Tanner等人于1998年在SIGGRAPH提出，原本用于纹理虚拟化，后被Asirvatham与Hoppe于2005年发表的"Terrain Rendering Using GPU-Based Geometry Clipmaps"移植到地形网格。其思想是以摄像机为中心维护若干同心环状LOD层级（Level），每层覆盖范围是内层的2倍，分辨率保持固定（通常为$n \times n$，如$255 \times 255$）。当摄像机移动时，只有边缘区域需要更新数据，实现O(n)而非O($n^2$)的帧更新代价。

相邻两层之间需要处理T形交叉（T-Junction）问题：内层网格边缘顶点不一定落在外层网格边上，若直接拼接将产生裂缝。解决方案是在边界带插入退化三角形（Degenerate Triangle）或使用"裙边"（Skirt）延伸边缘向下，遮蔽可能出现的缝隙。

### 自适应网格与连续LOD

自适应网格（Adaptive Mesh / CDLOD）依据屏幕空间误差而非固定层级决定细分粒度。Filip Strugar于2010年发表的CDLOD（Continuous Distance-Dependent Level of Detail）算法将地形划分为四叉树（Quadtree），根据节点包围盒到摄像机的距离与预设误差阈值$\epsilon_{screen}$的比较决定是否展开子节点。展开条件为：

$$\frac{d_{geometric} \times \text{screen\_width}}{2 \times d_{camera} \times \tan(\theta/2)} > \epsilon_{screen}$$

其中 $d_{geometric}$ 为该LOD级别引入的最大几何误差（米），$\theta$ 为垂直视角，$\epsilon_{screen}$ 通常设为1~2像素。四叉树叶节点生成固定分辨率的小块（Patch），由GPU曲面细分进一步细化，实现平滑过渡而非突变。

---

## 实际应用

**《地平线：零之曙光》（2017年）**采用基于Clipmap思想的分层地形系统，地形格网分辨率在近景区域降至约25厘米/格，配合曲面细分实现陡坡处的额外细节。引擎在摄像机前方预取数据，通过异步计算着色器将CPU端四叉树决策卸载到GPU时间轴的空闲槽位。

**Unreal Engine 5的Nanite**对地形采用特殊处理路径：Nanite的Cluster层级化不直接适用于高度图地形，因此UE5专门实现了"Nanite Landscape"，将高度图转换为Cluster化的静态虚拟几何，支持与Nanite标准网格统一剔除，但仍要求地形在运行前烘焙（Cook），不支持实时高度图修改。

**地形物理碰撞**通常使用低精度高度场（PhysX HeightField，16位整数格网），分辨率远低于渲染高度图（常用1/4到1/8降采样），在物理查询中节省内存带宽。渲染与物理高度图的不一致是导致角色"悬浮"或"陷入地面"Bug的常见来源，需在导出管线中同步更新两套数据。

---

## 常见误区

**误区一：高度图只能表示平坦地形，无法处理悬崖或洞穴**
高度图本身确实无法表达垂直覆盖的几何，但现代引擎通过"混合地形"（Hybrid Terrain）解决此限制：悬崖和洞穴区域用独立静态网格覆盖，与底层高度图地形无缝拼接，如《我的世界》基岩版使用的多层高度场变体。纯高度图被认为覆盖了90%以上的开放世界地貌需求。

**误区二：Clipmap层级越多越好**
每增加一个Clipmap层级，内存占用按$O(n^2)$增长（每层独立存储$n\times n$的顶点数据）。实践中GPU Geometry Clipmap通常维护5~8层，层数超过10层后更新带宽超过PCIe瓶颈（约16 GB/s），反而降低帧率。层数选择需匹配地形总尺寸与最近观察距离的比值。

**误区三：曲面细分可以完全替代预计算LOD**
硬件曲面细分的最大细分因子为64（Direct3D 11规格），对于细分前已有大三角形的粗糙基础网格，64倍细分仍可能不足以填补低频几何缺口。此外，曲面细分阶段发生在光栅化之前，无法获知最终屏幕像素覆盖，误差控制不如CDLOD基于距离的显式判断精确。

---

## 知识关联

学习地形几何需要掌握几何处理概述中的网格LOD基本思想，尤其是屏幕空间误差度量方法——地形的四叉树剔除逻辑是通用Mesh LOD判断逻辑在规则格网上的特化版本。高度图的GPU采样依赖纹理双线性插值和Mipmap层级选择，与纹理管线章节中的相关内容直接衔接。

后续学习植被渲染时，地形几何提供了植被实例散布的基础：草地和树木的世界位置通过对地形高度图采样获得，法线决定植株朝向，坡度（由相邻高度差计算的梯度幅度）决定植被种类和密度权重。因此地形高度图不只是渲染输入，也是后续生态系统模拟的数据源。
