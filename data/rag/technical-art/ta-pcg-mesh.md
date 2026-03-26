---
id: "ta-pcg-mesh"
concept: "程序化网格"
domain: "technical-art"
subdomain: "pcg"
subdomain_name: "程序化生成"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.2
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

# 程序化网格

## 概述

程序化网格（Procedural Mesh）是指通过算法在运行时（Runtime）或离线预处理阶段自动生成三角形或四边形几何体的技术，而非依赖美术人员手工建模的静态网格资产。其输出是一组顶点坐标（Vertex Buffer）和索引列表（Index Buffer），可以直接送入 GPU 渲染管线。与导入 `.fbx` 文件的方式不同，程序化网格的拓扑结构在代码执行时才最终确定，因此能够响应游戏逻辑、玩家操作或物理模拟等动态输入。

这一领域的关键里程碑是 1987 年 Lorensen 和 Cline 在 SIGGRAPH 上发表的论文《Marching Cubes: A High Resolution 3D Surface Construction Algorithm》，首次为体素（Voxel）数据到三角网格的转换提供了系统化方案。此后 Dual Contouring 算法于 2002 年由 Ju 等人提出，针对 Marching Cubes 无法保留锐利边缘（Sharp Features）的缺陷做出了本质性改进。今天，从《我的世界》风格的体素地形到地质模拟可视化，程序化网格已成为实时三维应用中处理动态形状的标准手段。

程序化网格的重要性在于它能以极低的存储成本表达几乎无限细节的几何变体。一个仅 64³ 体素分辨率的地形块，若全部手工建模则需要数千个独立模型，但程序化方法只需一个几 KB 的密度场（Density Field）数组加上生成代码即可覆盖所有变体。

---

## 核心原理

### Marching Cubes 算法

Marching Cubes 将三维空间划分为均匀的立方体格（Cube Cell），每个格的 8 个顶角都采样一个标量值（通常是 SDF 有符号距离场或密度值）。根据每个角是否超过等值面阈值（Isovalue），8 个角形成 2⁸ = 256 种二值模式，利用对称性可化简为 15 种基本拓扑类型，预存于一张 **三角查找表（Triangulation Lookup Table）** 中。对于每条与等值面相交的棱，通过线性插值计算交点位置：

$$
p = p_0 + \frac{v_{iso} - v_0}{v_1 - v_0}(p_1 - p_0)
$$

其中 $v_0, v_1$ 是棱两端的标量值，$v_{iso}$ 是等值面阈值，$p_0, p_1$ 是棱端点的世界坐标。该公式确保生成的顶点精确落在等值面上而非格子边界。Marching Cubes 的缺点是对于 90° 锐角（如建筑墙角）会产生圆润化现象，因为它每个 Cell 最多产生 5 个三角形，无法在单 Cell 内表达锐利的特征线。

### Dual Contouring 算法

Dual Contouring 采用"对偶"策略：不在 Cell 的棱上放置顶点，而是在每个与等值面相交的 Cell **内部**放置一个顶点，称为 QEF 顶点（Quadratic Error Function Vertex）。其最小化目标为：

$$
\text{QEF}(x) = \sum_i \left( n_i \cdot (x - p_i) \right)^2
$$

其中 $p_i$ 是等值面与第 $i$ 条棱的交点，$n_i$ 是该交点处的法线（通过对 SDF 求梯度得到）。求解这个最小二乘问题（通常用 SVD 分解）得到的点 $x$ 自然会被"吸引"到锐利特征处，从而复现 90° 乃至更尖锐的边缘。连接相邻 Cell 的 QEF 顶点即生成最终四边形（Quad）网格，通常再细分为三角形。

### Compute Shader 并行加速

在 Compute Shader 中实现程序化网格时，每个线程组（Thread Group）负责处理一个 Cell。以 Unity HDRP 为例，典型的 Dispatch 尺寸为 `(ChunkSize/8, ChunkSize/8, ChunkSize/8)`，每个线程处理一个 8³ 子块。Marching Cubes 的并行瓶颈在于**顶点去重**——相邻 Cell 共享棱上的顶点，GPU 端通常使用 `AppendStructuredBuffer` + 原子计数器，或预分配固定大小的顶点池（每个 Cell 最多 5 个三角形 × 3 顶点 = 15 个顶点）来规避竞争写入问题，代价是内存浪费约 30%–50%。

---

## 实际应用

**体素地形破坏系统**：游戏中炸弹爆炸产生坑洞时，只需将爆炸半径内的 SDF 值加上球形 SDF（使密度降低），然后对受影响的 Chunk 重新运行 Marching Cubes。由于每个 16³ Chunk 的重生成时间在现代 GPU 上约为 0.2–0.5 ms，可以在单帧内同步完成多个 Chunk 的网格更新，实现真实感破坏而不需预烘焙任何变体。

**医学可视化**：CT/MRI 扫描输出的三维体素数据天然适合等值面提取。将 HU（Hounsfield Unit）骨骼阈值（约 400 HU）作为等值面，直接对扫描数据跑 Marching Cubes 即可重建骨骼三维模型，用于术前规划。医疗场景对锐利特征要求较低，因此 Marching Cubes 的圆润化反而无害。

**程序化洞穴生成**：使用三维 Perlin Noise 或 Worley Noise 生成密度场，密度低于 0 的区域为空气，高于 0 为岩石。通过调整噪声参数（频率、振幅、八度数）即可生成风格迥异的地下洞穴系统，Dual Contouring 在此能保留岩石表面的棱角感。

---

## 常见误区

**误区一：Marching Cubes 的 256 种情况都需要手工编写三角查找表。**
实际上只需手工定义基础的 15 种拓扑类型，其余 241 种通过旋转（Rotation）和镜像（Reflection）变换自动生成。Paul Bourke 于 1994 年发布的公开实现给出了完整的 256 项查找表，现已成为工业界标准参考，几乎所有实现都直接引用或复制该表格。

**误区二：Dual Contouring 总是优于 Marching Cubes。**
Dual Contouring 的 QEF 求解依赖准确的法线信息；若 SDF 的梯度噪声较大（例如来自低精度体素的手工绘制密度场），SVD 分解可能产生 QEF 顶点飞出 Cell 范围外的"顶点爆炸"问题，需要额外做顶点夹取（Clamping）。对于没有锐利特征需求的有机形状（如角色皮肤、自然地形），Marching Cubes 的实现简单、鲁棒性更高。

**误区三：程序化网格运行时生成就意味着不需要 UV 坐标。**
GPU 渲染仍然需要 UV 用于贴图采样。程序化网格通常采用**三平面投影（Triplanar Mapping）**，根据顶点法线分量的绝对值混合 XY、YZ、XZ 三个投影方向的贴图，从而绕过传统 UV 展开步骤。但这会使 Shader 中的贴图采样次数翻 3 倍，是性能权衡。

---

## 知识关联

**依赖 Compute Shader**：程序化网格生成的核心计算量——遍历所有 Cell、查表、插值——全部在 Compute Shader 中以 GPU 并行方式执行。若不使用 Compute Shader 而改用 CPU 单线程，一个 64³ 的 Chunk 生成耗时可从 < 1 ms 升至 30–100 ms，完全无法满足实时破坏的需求。理解 `StructuredBuffer`、`AppendStructuredBuffer` 及线程组索引（`SV_DispatchThreadID`）的用法是实现 GPU 端 Marching Cubes 的必要前提。

**延伸方向**：掌握程序化网格后可进一步探索 **Transvoxel 算法**（由 Eric Lengyel 于 2010 年专为 LOD 无缝过渡设计，解决不同分辨率 Chunk 交界处的裂缝问题）、**Surface Nets**（另一种对偶方法，顶点稳定性优于 Dual Contouring）、以及基于神经网络的隐式表面重建（Neural SDF），后者正在成为实时重建真实世界场景的新兴方向。