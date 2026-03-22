---
id: "terrain-intro"
concept: "地形设计概述"
domain: "level-design"
subdomain: "terrain-design"
subdomain_name: "地形设计"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "An Architectural Approach to Level Design"
    author: "Christopher Totten"
    year: 2019
    isbn: "978-0815361367"
  - type: "textbook"
    title: "Level Design: Concept, Theory, and Practice"
    author: "Rudolf Kremers"
    year: 2009
    isbn: "978-1568813387"
  - type: "conference"
    title: "Terrain in Open World Games"
    authors: ["Daniel Teece"]
    venue: "GDC 2017"
scorer_version: "scorer-v2.0"
---
# 地形设计概述

## 概述

地形（Terrain）是游戏世界的物理骨架——它定义了玩家可行走的表面、视觉的远景轮廓以及战术空间的基本形态。Rudolf Kremers 在《Level Design: Concept, Theory, and Practice》（2009）中将地形描述为"关卡设计中唯一同时影响美术、玩法和性能三个维度的元素"。

从技术角度看，游戏地形是一个 2D 高度场（Heightfield）在 3D 空间中的投影——每个网格点存储一个高度值（通常为 16-bit 灰度图），渲染引擎将其转换为可行走的 3D 网格。《巫师3》的完整世界地形分辨率为 16384×16384，覆盖 136 km² 的游戏区域，其中 96% 使用程序化生成+手工调整的混合流程。

## 地形的四大生成方法

### 1. 高度图（Heightmap）

最基础的地形表示方式：

| 参数 | 典型值 | 影响 |
|------|--------|------|
| 分辨率 | 1025×1025 至 8161×8161 | 越高越精细，内存成倍增长 |
| 位深 | 16-bit | 8-bit 仅 256 级高度→明显阶梯 |
| 每像素物理尺寸 | 0.5m - 2m | 决定最小可塑造地貌尺寸 |
| 高度范围 | 100m - 2000m | UE5 默认 ±256m |

高度图的本质限制：**无法表示悬崖凹陷和洞穴**——每个 XY 坐标只能有一个 Z 值。解决方案：地形+静态网格组合（UE5 的 Landscape + Mesh Cave），或使用体素系统（Voxel，如《深岩银河》的全体素地形）。

外部工具链：World Machine（侵蚀模拟）→ 导出 16-bit PNG → UE5/Unity 导入。Gaea、Terragen 也是常用选择。

### 2. 程序化生成（Procedural Generation）

核心算法家族：

- **Perlin/Simplex Noise**：Ken Perlin 1983 年发明，通过多个频率（Octaves）叠加生成自然地形。参数：Frequency（频率→山脉密度）、Amplitude（振幅→高度变化）、Lacunarity（频率倍率）、Persistence（振幅衰减）
- **液压侵蚀（Hydraulic Erosion）**：模拟雨水沿地表流动形成沟壑——World Machine 的标志性功能，单次侵蚀迭代约 10-50 万步
- **热侵蚀（Thermal Erosion）**：模拟岩石热胀冷缩碎裂→形成碎石堆。与液压侵蚀组合使用效果最佳
- **Voronoi 分形**：生成尖锐山脊地形，适合火山/外星地貌

《No Man's Sky》使用 6 层嵌套 Perlin Noise + 自定义生物群系规则，可生成 18×10¹⁸ 颗独特行星。

### 3. 手工雕刻（Sculpting）

关卡设计师使用引擎内置或外部 DCC 工具直接雕刻：

- **UE5 Landscape**：Sculpt 工具集（Raise/Flatten/Smooth/Erosion/Noise），笔刷半径 256-8192，强度 0.0-1.0
- **Unity Terrain**：类似工具集但精度较低，推荐配合 Terrain Tools Package
- **外部雕刻**：ZBrush/Blender 雕刻后导出置换贴图→引擎导入

手工雕刻的成本极高——AAA 开放世界项目的典型配置是 3-5 名地形艺术家，周期 6-12 个月。

### 4. 真实世界数据

从卫星/航空测量数据导入：

- **数据源**：USGS 3DEP（美国 1m 精度）、SRTM（全球 30m 精度）、国家基础地理信息中心（中国）
- **流程**：GeoTIFF → QGIS 裁剪→ 重采样到目标分辨率 → 16-bit RAW → 引擎导入
- **应用**：《微软飞行模拟》使用 Bing Maps 全球 DEM + AI 增强至 3m 精度

## 地形设计的五大原则

Christopher Totten（2019）提出的地形设计框架：

1. **可读性（Readability）**：玩家站在任意位置，应能通过地形轮廓识别方向感。**高点 = 兴趣点**——人类天生会注视天际线上的突出物。《塞尔达：旷野之息》的塔+山顶+神庙构成三级地标体系
2. **游玩节奏（Pacing）**：地形起伏控制行进速度——上坡减速（紧张/期待）、下坡加速（释放/自由）、平地过渡（呼吸）。连续 30 秒以上的同质地形 = 节奏失败
3. **战术深度（Tactical Depth）**：高地优势、掩体分布、视线遮挡。《战地》系列的地形设计核心公式：每 50m 至少有 1 个自然掩体（坡、石、沟）
4. **性能预算（Performance）**：LOD 层级（UE5 默认 4 级：0m/50m/200m/1000m+），远处地形三角形数可降至 1/64。渲染预算典型分配：地形占 GPU 时间的 15-25%
5. **材质过渡（Material Blending）**：高度/坡度驱动的自动材质：平地→草、坡度>30°→岩石、高度>500m→雪。UE5 的 Landscape Material 支持 16 层混合

## UE5 地形系统速查

```
核心组件                        关键参数
─────────────────────────────────────────────
Landscape Component    默认 63×63 顶点（127×127 可选）
Section Size           每 Component 包含 1-4 Sections
Overall Resolution     (NumComponents × QuadsPerSection + 1)²
推荐尺寸               2017×2017（小型）→ 8129×8129（大型）
Collision              按 Component 粒度生成，支持 Simple/Complex
Streaming              World Partition 按 Component 级别流式加载
Nanite                 UE5.1+ 支持 Nanite Landscape（实验功能）
```

## 常见误区

1. **平坦世界综合征**：地形过于平坦导致无遮挡、无层次、无方向感。即使看起来"平坦"的区域也应有 ±2m 的微起伏——玩家不会注意到，但相机会
2. **噪声过度**：Perlin Noise 参数过高导致"蛋糕糊"地形——频率和振幅的合理比例：每公里 2-4 个主要山脊。自然地形遵循 1/f 分形分布
3. **忽视比例感**：游戏中的山不是真实高度——真实的 1000m 山在游戏相机中显得平坦。经验法则：游戏山高 = 目标视觉感受 × 0.3-0.5。《天际》的喉咙世界实际高度仅 ~200m，但视觉上像 1000m

## 知识衔接

### 先修知识
- **关卡编辑器概述** — 地形操作需要基本的引擎编辑器使用能力

### 后续学习
- **高度图** — 深入高度图的生成、编辑和优化
- **地形材质** — 多层材质混合、自动地形绘制
- **地形LOD** — Level of Detail 算法和流式加载
- **道路与河流** — 在地形上叠加样条线驱动的线性元素
- **悬崖与洞穴** — 突破高度图限制的非地形地貌

## 参考文献

1. Totten, C. (2019). *An Architectural Approach to Level Design* (2nd ed.). CRC Press. ISBN 978-0815361367
2. Kremers, R. (2009). *Level Design: Concept, Theory, and Practice*. A K Peters. ISBN 978-1568813387
3. Teece, D. (2017). "Terrain in Open World Games." GDC 2017.
4. Perlin, K. (1985). "An Image Synthesizer." *SIGGRAPH '85*, 287-296.
5. Epic Games (2024). "Landscape Technical Guide." Unreal Engine 5 Documentation.
