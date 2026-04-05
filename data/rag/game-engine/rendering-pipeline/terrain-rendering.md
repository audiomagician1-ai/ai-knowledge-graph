---
id: "terrain-rendering"
concept: "地形渲染"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["地形"]

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


# 地形渲染

## 概述

地形渲染是游戏引擎渲染管线中专门处理大规模户外地表的技术体系，其核心挑战在于以有限的 GPU 资源呈现数平方公里乃至数百平方公里的连续地表细节。与室内场景不同，地形通常由一张或多张高度图（Heightfield）驱动，GPU 根据顶点的 Y 坐标由灰度值采样计算，从而将平面网格"凸起"成真实山脉或平原。

地形渲染技术的演进始于1990年代的 ROAM（Real-time Optimally Adapting Meshes）算法，该算法通过二叉三角树在 CPU 端动态细分网格。进入2000年代后，Chunked LOD 和 Geometry Clipmap 相继出现，后者由 Losasso 和 Hoppe 于2004年在 SIGGRAPH 发表，奠定了现代地形 LOD 的理论基础。GPU Tessellation 随 DirectX 11（2009年）引入后，细分计算从 CPU 完全转移至 GPU，彻底改变了地形顶点生成的方式。

地形渲染之所以在渲染管线中需要专项处理，是因为普通静态网格的 LOD 策略（如 Nanite 的集群层级）不适用于无缝连续的高度场——地形相邻 LOD 层级间若不处理裂缝（Crack），画面会出现明显黑线撕裂。正确的地形渲染必须同时解决 LOD 过渡、裂缝修补、纹理混合与精度损失四大问题。

---

## 核心原理

### Geometry Clipmap

Geometry Clipmap 将地形划分为以摄像机为中心的同心矩形环带，通常设置 5～8 个 Level，每个 Level 的网格间距是上一级的 2 倍。以 Unreal Engine 5 的 Landscape 系统为例，最内层 Level 0 的网格分辨率可达每顶点 0.5 米，而最外层 Level 7 每顶点间距则扩大至 64 米。摄像机移动时，各 Level 的中心坐标按 2^n 步长离散对齐，避免连续浮点偏移带来的"泳动"伪影（Swim Artifact）。

相邻 Level 边界处的裂缝由 **Skirt** 或 **T-Junction** 修补：Skirt 方法在外层 Level 边缘向下延伸一条裙摆网格，遮挡缝隙；更精确的做法是在顶点着色器中根据边界标志位将边界顶点吸附到外层精度对齐的位置，公式为：

```
finalPos.xz = floor(rawPos.xz / outerSpacing) * outerSpacing
```

其中 `outerSpacing` 为外层 Level 的网格间距。

### Virtual Heightfield Mesh（虚拟高度场网格）

Virtual Heightfield Mesh（VHM）是 Unreal Engine 4.26 引入的技术，它将高度场的 LOD 管理与虚拟纹理（Virtual Texture）系统深度融合。高度图被分块存储为 128×128 或 256×256 像素的物理页面，仅将摄像机视野内需要的高分辨率页面流送进显存，其余区域使用低分辨率 Mip 替代。GPU 根据当前页面分辨率动态决定三角形密度，实现了真正的"按需细分"，峰值显存占用比传统 Clipmap 降低约 40%。

VHM 的渲染流程分为两个 Pass：第一个 Pass 渲染一张屏幕分辨率的 **深度预通道**，确定哪些高度场区域可见；第二个 Pass 用 Indirect Draw 实例化对应的高分辨率网格块，避免 CPU 参与每帧的 Draw Call 组装。

### GPU Tessellation 与位移贴图

DirectX 11 的硬件曲面细分管线包含三个阶段：Hull Shader（壳着色器）→ 固定管线细分器 → Domain Shader（域着色器）。在地形渲染中，Hull Shader 根据 Patch 到摄像机的距离输出细分因子（TessellationFactor），范围通常为 1～64；Domain Shader 再根据重心坐标对高度图进行双线性采样，将新生成的顶点"位移"到正确高度。

细分因子的典型计算公式为：

```
TF = clamp(K / distance(patchCenter, cameraPos), minTF, maxTF)
```

其中常数 `K` 通常取屏幕像素密度目标值（如 16），`minTF = 1`，`maxTF = 64`。GPU Tessellation 的主要瓶颈在于当 TF 过高（>32）时，光栅化阶段出现大量亚像素三角形，造成几何过渡采样（Geometry Overdraw），实测帧时间可上涨 3～5 倍，因此高端地形系统倾向于用 VHM 或 Nanite 替代纯 Tessellation 方案。

---

## 实际应用

**《荒野大镖客：救赎2》** 使用了多层 Clipmap 配合手工绘制的宏观高度图，地形总面积约 75 平方公里，低频地形数据压缩存储于 BC4 格式的高度图（单通道16位精度），保证了山地陡峭处不产生台阶感。

**Unreal Engine 5 的 Landscape** 系统默认采用 Clipmap + Nanite（实验性）混合方案：平缓区域由传统 Clipmap 驱动，悬崖和岩石等高频几何细节转交 Nanite 的集群 LOD 处理，两套系统通过材质层混合权重无缝衔接。

**《最终幻想XV》** 地形渲染使用了 Tessellation + 位移贴图，在 PS4 Pro 上将地表三角形数量从基础网格的约 20 万提升至运行时峰值约 800 万，同时配合曲面法线重建（Crack-free Normal Reconstruction）消除相邻 Patch 法线不连续导致的光照缝隙。

---

## 常见误区

**误区一：认为提高高度图分辨率可以无限提升地形质量**。高度图存储的是标量高度值，无法表达悬挑（Overhang）和洞穴——这类结构需要单独的多边形网格叠加在地形之上。此外，16 位高度图的垂直精度为 `totalHeight / 65535`，若地形总高差为 4000 米，每步精度约 6 厘米，对于需要毫米级精度的近景细节仍然不足。

**误区二：GPU Tessellation 与 LOD 系统等价，二选一即可**。Tessellation 负责在已知 Patch 范围内细化顶点密度，而 LOD（如 Clipmap）负责决定哪些 Patch 应被绘制及其基础网格分辨率——两者作用于不同粒度，缺少 LOD 的纯 Tessellation 方案会在远景浪费大量 GPU 算力在肉眼不可见的细节上。

**误区三：地形裂缝只是视觉瑕疵，不影响渲染正确性**。裂缝本质上是相邻 LOD 边界的几何不连续，若深度缓冲存在间隙，后续的屏幕空间环境光遮蔽（SSAO）和屏幕空间反射（SSR）会沿裂缝产生错误的遮蔽线或反射跳变，尤其在俯视角相机下极为明显。

---

## 知识关联

地形渲染建立在**渲染管线概述**所讲的顶点着色器→光栅化→片元着色器流程之上，Tessellation 阶段插入于顶点着色器与光栅化之间，是对标准管线流程的显式扩展。理解 GPU 管线各阶段的数据流向（顶点缓冲→Hull→Domain→光栅化）是调试 Tessellation 裂缝和性能瓶颈的前提。

地形渲染的纹理部分与**虚拟纹理（Virtual Texture）** 技术深度绑定：VHM 的高度图流送机制本质上是虚拟纹理在几何维度的延伸。地形的 **材质混合** 涉及权重图（Splat Map）采样与多层混合，这些知识延伸到可编程材质系统和 Shader 变体管理。此外，地形渲染产出的深度图会直接影响**阴影贴图**（Shadow Map）的精度分配，大范围地形往往需要 Cascade Shadow Map（CSM）配合使用，通常设置 4 个级联分别覆盖 10/50/200/1000 米范围。