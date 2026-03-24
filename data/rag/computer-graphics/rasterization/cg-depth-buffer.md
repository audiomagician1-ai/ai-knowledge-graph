---
id: "cg-depth-buffer"
concept: "深度缓冲"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 深度缓冲

## 概述

深度缓冲（Depth Buffer），也称为Z-Buffer，是光栅化管线中用于解决**可见性问题**的标准算法。其核心思想是：为帧缓冲中的每个像素维护一个额外的浮点数值，记录当前写入该像素的片元距摄像机的深度，当新片元到来时，比较其深度与缓冲中已存储值，仅保留更近的片元。1974年，Edwin Catmull 在其博士论文中正式提出了 Z-Buffer 算法，使得实时渲染摆脱了对几何体排序（画家算法）的依赖。

深度缓冲之所以在现代GPU中成为标配，是因为它将可见性判断的复杂度从画家算法的 O(n log n) 降至 O(1)（每像素常数次比较），代价仅是一块与帧缓冲等大的内存区域。一块 1920×1080 分辨率的 32 位深度缓冲占用约 8 MB 显存，这在现代硬件上完全可接受，却换来了对任意复杂场景的正确遮挡处理。

---

## 核心原理

### Z-Buffer 算法流程

Z-Buffer 算法在每帧开始时将深度缓冲全部初始化为最大深度值（OpenGL 默认为 1.0，代表远裁切面；DirectX 同样如此）。随后，对每个光栅化产生的片元执行以下逻辑：

```
if (fragment.depth < zBuffer[x][y])
{
    zBuffer[x][y] = fragment.depth;
    frameBuffer[x][y] = fragment.color;
}
```

片元的深度值来自顶点阶段输出的裁切坐标经透视除法后得到的 NDC（Normalized Device Coordinates）z 分量，再映射到 [0, 1] 区间。属性插值阶段负责在三角形内部对裁切空间坐标进行透视正确插值，因此深度缓冲中存储的是**透视正确**的深度，而非线性插值深度。

### 深度值的非线性分布

经过透视投影矩阵变换后，NDC 空间中的 z 值并非线性分布于 [zNear, zFar]，其映射公式为：

$$z_{ndc} = \frac{z_{far}(z_{view} - z_{near}) + z_{near} \cdot z_{far}}{z_{view}(z_{far} - z_{near})}$$

（此处以 OpenGL 约定，zView 为负值）

这导致深度缓冲的精度在靠近摄像机处极度密集，而在远处极度稀疏。例如，当 zNear=0.1、zFar=1000 时，约 **90%** 的 24 位整数深度值都被分配给了 [0.1, 1.0] 这前 1 米范围内，这一现象称为**深度精度崩溃（Z-fighting）**，在远处物体表面相互贴合时尤为明显。

### 反向Z（Reversed-Z）技术

反向 Z 是解决深度精度问题的现代标准方案，由 Emil Persson 等人在 2010 年代广泛推广。其核心做法是：将深度缓冲的初始化值从 1.0 改为 **0.0**，深度比较函数由 `LESS` 改为 `GREATER`，并将 NDC z 映射到 [1, 0] 而非 [0, 1]（即近处映射到 1.0，远处映射到 0.0）。

当配合**浮点深度缓冲格式**（如 `D32_FLOAT`）使用时，反向 Z 的效果尤为显著。IEEE 754 浮点数在 [0, 1) 区间内的精度分布天然集中于接近 0 的一侧，而反向 Z 恰好让远处的深度值落在浮点精度更高的小数端，从而**抵消了透视投影引入的非线性精度损失**。实测表明，反向 Z 配合 32 位浮点深度缓冲，可将有效深度范围从传统方案的数百米扩展至数万米乃至无限远（配合无限远裁切面使用时）。

---

## 实际应用

**地形与开放世界渲染**：当场景视距超过 10 公里时，传统 24 位整数深度缓冲在远处必然出现 Z-fighting。《荒野大镖客2》等开放世界游戏使用反向 Z + `D32_FLOAT` 格式，将 zFar 推至 100,000 单位而无明显精度问题。

**半透明物体排序**：深度缓冲仅对不透明物体有效；半透明物体写入深度缓冲会错误遮挡后续片元，因此通常在渲染半透明物体时**关闭深度写入**（`glDepthMask(GL_FALSE)`），但保留深度测试，使其仍能被不透明物体遮挡。

**深度图采样（Shadow Mapping）**：将场景从光源视角渲染一次，把深度缓冲保存为深度纹理，后续主渲染Pass采样该纹理进行遮挡比较，即 PCF（Percentage Closer Filtering）阴影的基础。深度纹理格式常用 `GL_DEPTH_COMPONENT16` 至 `GL_DEPTH_COMPONENT32F`，精度直接影响阴影偏移（Shadow Bias）的最小可设值。

---

## 常见误区

**误区一：深度缓冲存储的是线性距离**
许多初学者认为深度缓冲中存的是片元到摄像机的欧氏距离或线性 z 值。实际上存储的是经透视投影和 NDC 映射后的**非线性**值。若需重建线性深度（如用于SSAO），必须用投影矩阵参数反推：`linearDepth = (2.0 * zNear) / (zFar + zNear - zNDC * (zFar - zNear))`。

**误区二：增大 zNear 可以提升远处精度**
实际结论相反。将 zNear 从 0.1 调整到 0.01 会**恶化**远处精度，因为透视矩阵的精度分布使得 zNear 越小，远处可用的深度精度越少。正确做法是尽量增大 zNear（在不裁切近处物体的前提下），或使用反向 Z。

**误区三：深度测试在片元着色器之后执行**
OpenGL/DirectX 规范允许实现在片元着色器**之前**执行深度测试（即 Early-Z），但这要求片元着色器不修改 `gl_FragDepth` 且不执行 discard。一旦着色器中使用了 `discard` 或写入深度，GPU 将退回到 Late-Z，导致性能下降。

---

## 知识关联

**前置概念——属性插值**：深度缓冲中的每个像素深度值，来自光栅化阶段对三角形三顶点 z 坐标的透视正确插值。若不理解透视除法在属性插值中的作用，则无法理解为何深度值呈非线性分布。

**后续概念——模板缓冲**：模板缓冲与深度缓冲共享同一块内存区域（如 `D24_S8` 格式中，24 位存深度、8 位存模板），两者的测试阶段在管线中紧密相邻，深度测试失败时模板缓冲的 `zfail` 操作才有意义。

**后续概念——Early-Z 优化**：Early-Z 是对深度测试执行位置的硬件优化，将深度测试提前到片元着色器之前以剔除被遮挡片元，节省着色计算开销。理解深度缓冲的基本工作流程是理解 Early-Z 为何能优化性能的前提。

**后续概念——间接绘制**：在间接绘制（Indirect Draw）与 GPU Driven Rendering 流程中，深度缓冲的 Hierarchical-Z（Hi-Z）版本被用于 GPU 侧遮挡剔除，决定哪些Draw Call实际提交。
