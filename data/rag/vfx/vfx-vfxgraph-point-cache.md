---
id: "vfx-vfxgraph-point-cache"
concept: "Point Cache"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 点缓存（Point Cache）

## 概述

点缓存（Point Cache）是一种将三维空间中的点位置数据预先序列化存储，再通过文件读取方式驱动 VFX Graph 粒子系统的技术手段。与运行时实时计算粒子位置不同，点缓存将每一帧的点坐标、法线、颜色等属性固化为 `.abc`（Alembic）或 `.vat`（Vertex Animation Texture）等格式的外部资产，粒子系统直接读取这些数据完成分布和动画。

Unity VFX Graph 在 2019.3 版本中正式将 **Point Cache Bake Tool** 集成进工具链，允许美术师在 Unity 编辑器内直接将网格表面、纹理甚至手工摆放的点集烘焙为 `.pcache` 二进制格式文件。这种格式以每个点的属性通道（Position、Normal、Color 等）连续排列，文件头记录通道数、数据类型（float32/uint8）和点总数，读取效率极高。

点缓存技术的核心价值在于**将动态模拟结果与实时渲染完全解耦**：Houdini 或 Maya 中完成的布料模拟、流体粒子轨迹可以先离线烘焙为点缓存序列，VFX Graph 在游戏运行时按帧索引逐帧播放，使引擎无需承担模拟计算开销，同时保持视觉保真度。

---

## 核心原理

### `.pcache` 文件结构与属性通道

Unity `.pcache` 文件由 ASCII 文件头和二进制数据体两部分组成。文件头声明每个通道的名称、元素类型（`Float`/`UInt`/`Int`）和分量数（如 Position 为 `Float3`，Color 为 `UInt8x4`），以及总点数 `element_count`。数据体中所有点的属性**按通道分块连续存储**，而非逐点交织，这意味着读取单一通道（如仅读 Position）时无需跨步访问，GPU 缓存命中率更高。

在 VFX Graph 中，`Initialize Particle` 阶段通过 **Get Attribute from Map** 节点或专用的 **Point Cache Operator** 节点，以粒子 `particleId` 为索引映射到对应点数据，公式为：

```
attributeValue = pcache[channel][ particleId % elementCount ]
```

`% elementCount` 的取模操作使粒子数量可以超过缓存点数，超出部分会循环复用已有点，适合制造稠密粒子覆盖效果。

### 静态分布与序列帧动画

点缓存分两种使用模式：

**静态点缓存**：单帧数据，仅包含一组点位置，用于在特定几何形态表面初始化粒子位置。例如将角色剪影的轮廓点烘焙为 1024 个点的 `.pcache`，粒子诞生时即分布在轮廓上，之后受速度、重力等 VFX Graph 力节点驱动自由运动。

**序列帧点缓存**：多帧数据以统一命名规则（如 `smoke_0001.pcache`、`smoke_0002.pcache`）存放，VFX Graph 通过 **Flipbook Index** 或自定义 `float` 参数控制当前播放帧索引。每帧的点数必须**严格一致**，否则索引映射将错位。Houdini 导出序列时需在 ROP 节点勾选 `Constant Point Count` 选项以强制约束此条件。

### GPU 实例化与属性绑定

点缓存数据在 VFX Graph 中最终以 **GraphicsBuffer**（结构化缓冲区）形式上传至 GPU，粒子的 `Position`、`Normal`、`Color` 等内置属性在 `Initialize` 阶段一次性写入粒子属性缓冲区。由于写入发生在初始化而非每帧更新，静态点缓存的运行时 GPU 消耗接近于零——所有 N 个粒子的位置数据仅在系统首次生成时读取一次。序列帧模式下，每次帧切换触发一次全量属性写入，其消耗与粒子数量 N 线性相关，因此序列帧点缓存的粒子数通常控制在 **10 万以内**以维持 60fps。

---

## 实际应用

**角色消散特效**：将角色网格表面均匀采样 5 万个点烘焙为静态点缓存，粒子在角色位置诞生后受自定义 `Turbulence Force` 节点驱动向外扩散，结合粒子生命周期的 `Alpha` 渐变，呈现灵魂消散效果。网格表面法线通道同时存入点缓存，用于控制粒子初始飞散方向，使粒子沿原始曲面外法线方向喷出，而非随机四散。

**流体轨迹重放**：在 Houdini 中模拟 120 帧的水花飞溅，以每帧 8192 个点导出序列 `.pcache`，Unity 端 VFX Graph 接收外部 `float` 参数 `SimFrame` 驱动帧索引，配合游戏逻辑实现慢动作回放（将 `SimFrame` 更新速率减半）而无需重新模拟。

**程序化植被散布**：利用地形高度图生成草地分布点缓存，每个点携带 `Normal`（草叶朝向）和 `Color`（基于坡度的枯黄度）通道，VFX Graph 中粒子以面片（Quad）渲染为草叶，点缓存的 Color 通道直接驱动着色器中的色调混合参数。

---

## 常见误区

**误区一：认为序列帧点缓存中每帧点数可以变化**
这是最常见的错误。`.pcache` 序列的索引映射基于固定的 `elementCount`，若第 30 帧的点数从 8192 骤降至 6000，第 6001 至 8192 号粒子将读取无效内存区域，导致粒子瞬移至世界原点（0,0,0）。必须在离线模拟软件端约束恒定点数，而非依赖 Unity 端自动处理。

**误区二：将点缓存与 GPU 粒子模拟混用时忽略坐标空间**
点缓存中存储的 Position 默认为**对象空间（Object Space）**坐标，若将其直接赋值给 VFX Graph 的世界空间粒子位置，角色移动后粒子不会跟随。正确做法是在 `Initialize` 上下文中使用 `Transform Position` 节点，将 VFX Graph 组件的 `localToWorld` 矩阵应用到点缓存坐标上。

**误区三：用点缓存替代蒙皮网格采样处理实时动画角色**
点缓存适合**预录制、离线模拟**的固定动画序列。对于需要实时响应动画状态机（如走、跑、攻击切换）的角色特效，每次动作切换都需要切换对应的点缓存序列文件，管理成本极高。这类需求应改用蒙皮网格采样（Skinned Mesh Sampling），它直接读取 GPU 蒙皮后的顶点位置，天然与角色动画系统同步。

---

## 知识关联

学习点缓存之前，掌握 **Strip 粒子**的意义在于：Strip 粒子已经引入了"粒子按序号排列形成连续结构"的思路，点缓存将这一思路延伸为"粒子序号映射到外部数据文件中的点序号"，两者都依赖 `particleId` 的有序性。

点缓存是理解**蒙皮网格采样**的直接前驱：蒙皮网格采样可以视为一种运行时动态生成的点缓存——每帧由 GPU 计算蒙皮变形后的顶点坐标，以与 `.pcache` 完全相同的 Position/Normal 属性接口提供给 VFX Graph。理解了点缓存的属性通道结构和坐标空间注意事项，蒙皮网格采样中的同类问题将迎刃而解。两者的本质区别是数据来源：一个来自磁盘文件（离线），一个来自 GPU 计算（实时）。