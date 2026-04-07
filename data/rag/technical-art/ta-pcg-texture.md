---
id: "ta-pcg-texture"
concept: "程序化纹理"
domain: "technical-art"
subdomain: "pcg"
subdomain_name: "程序化生成"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 程序化纹理

## 概述

程序化纹理（Procedural Texture）是指通过数学算法和节点图逻辑生成的纹理贴图，而非依赖手工绘制或照片扫描的位图资产。其核心特征是纹理内容由参数和运算规则描述，因此可以在不占用源图片存储空间的前提下，生成任意分辨率的输出贴图。Substance Designer 是当前游戏行业最主流的程序化纹理制作工具，它将整套生成逻辑保存在 `.sbs` 格式文件中，输出结果则导出为 `.sbsar`（压缩后的可执行材质包）。

程序化纹理的概念最早随着 Perlin Noise 的发布而走入实用阶段。Ken Perlin 在 1983 年为电影《创：战纪》（Tron）开发了这一噪声算法，并因此在 1997 年获得奥斯卡技术奖。此后 Worley Noise（1996 年）、Value Noise、Simplex Noise（2001 年，同样由 Perlin 提出）等基础函数相继出现，构成了现代程序化纹理的算法库基础。

在游戏美术流程中，程序化纹理的价值体现在三个可量化的维度：存储体积（一套完整 PBR 材质的 `.sbsar` 通常仅几百 KB，而对应的 4K 位图集合可达数十 MB）、参数可调性（设计师可以在引擎运行时动态修改颜色、磨损程度、瓷砖缩放等参数而无需重新导出）、以及无缝平铺（算法层面天然支持 UV 边界的连续性，无需手工修图）。

---

## 核心原理

### 节点图（Node Graph）结构

Substance Designer 的工作流以有向无环图（DAG）为组织形式。每个节点代表一次独立的图像运算，节点的输出口连接到下一节点的输入口，形成数据流。节点类型分为三大类：

- **生成节点（Generator）**：从零产生灰度或彩色图像，例如 `Noise`、`Shape`、`Tile Generator`；
- **过滤节点（Filter）**：接收一张或多张输入图并进行变换，例如 `Blur`、`Levels`、`Warp`；
- **混合节点（Blend）**：将两张图按指定混合模式（叠加、正片叠底、高度混合等）合并。

最终的材质输出节点（Output Node）通常包含 Base Color、Roughness、Metallic、Normal、Height 五个通道，分别对应 PBR 光照模型所需的贴图类型。

### 噪声函数与频率叠加

程序化纹理中最基础的视觉来源是噪声函数。以 Perlin Noise 为例，其数学表达为多个频率的梯度噪声叠加（即分形布朗运动，fBm）：

$$f(x) = \sum_{i=0}^{n} \frac{1}{2^i} \cdot \text{noise}(2^i \cdot x)$$

其中每一层称为一个"倍频"（Octave），振幅随频率加倍而减半，这种比例关系被称为持续度（Persistence）。在 Substance Designer 的 `FX-Map` 节点中，可以手动控制倍频数量（通常设为 4–8 层）和每层的粗糙度贡献，从而在宏观轮廓与细节纹理之间取得平衡。

### 法线贴图的程序化生成

程序化流程中，法线贴图通常不是直接绘制的，而是由高度图（Height Map）经过 `Normal` 节点转换得到。该节点本质上对高度图做偏导数计算：

$$N_x = \frac{\partial H}{\partial x}, \quad N_y = \frac{\partial H}{\partial y}$$

结果被重映射到 RGB 空间（切线空间法线贴图中蓝色通道固定为正 Z 方向，值约为 0.5–1.0）。因此，程序化纹理设计师通常优先设计高度图的细节层次，法线贴图作为派生结果自动产生，这与传统手绘流程的顺序相反。

### 参数化暴露（Parameter Exposure）

Substance Designer 允许将节点内部的任意数值"暴露"为外部可访问的参数（Exposed Parameter）。暴露后的参数可以在 Substance Player、Unity 或 Unreal Engine 的材质编辑器中由美术或关卡设计师实时调整，而无需重新打开 Substance Designer。常见的暴露参数包括：`Tiling`（瓷砖数量，整数型）、`Roughness Variation`（粗糙度偏移量，浮点型 0.0–1.0）、`Color Hue Shift`（色相偏移，浮点型 -180 至 180）。

---

## 实际应用

**砖墙材质制作**是程序化纹理的经典练习场景。典型节点流程如下：首先用 `Brick Generator` 节点生成砖块遮罩，控制砖缝宽度（默认值约 0.05，代表纹理空间的 5%）和砖块偏移（每行错缝比例）；随后将砖块遮罩输入 `Bevel` 节点生成高度图，得到砖块边缘的弧面轮廓；再通过 `Grunge Map` 节点叠加磨损细节，通过 `Histogram Scan` 节点控制磨损阈值，从而精准决定哪些区域出现破损。最终 Base Color 通道由砖块颜色与砖缝颜色两个纯色节点经遮罩混合得出，整套流程不依赖任何外部图片。

**游戏地面材质**的程序化制作中，`Splatter Circular` 节点常用于生成鹅卵石或泥土凹坑的随机分布，通过调整散布数量（Instance Count）和随机种子（Random Seed）即可获得不同密度和布局的结果，且所有变体保持无缝平铺。

---

## 常见误区

**误区一：程序化纹理等于"无限分辨率"**。实际上，Substance Designer 内部所有节点运算都在固定分辨率的像素缓冲区上执行（常用 1024×1024 或 2048×2048），并非真正的矢量描述。更改输出分辨率时，图形会在新分辨率下重新运算，而非简单缩放，因此高频细节在高分辨率下能得到更清晰的呈现，但这仍是离散采样，存在奈奎斯特极限。

**误区二：所有程序化纹理都适合实时动态修改**。`.sbs` 源文件中的节点图是在离线环境中运算并烘焙成位图后导入引擎的（这是最常见的工作流）；只有打包为 `.sbsar` 并配合 Substance 插件使用时，才能在引擎运行时按参数实时重新运算。直接将未烘焙的程序化纹理用于移动端等性能受限平台，会导致严重的帧率问题。

**误区三：高度图越复杂，法线贴图质量越高**。过度叠加高频噪声会导致法线贴图出现"龟裂"（棋盘状的法线翻转），这是因为相邻像素的高度差超过了切线空间法线的合理范围（法线 Z 分量趋近于零）。在 Substance Designer 中，通常在高度图进入 `Normal` 节点之前插入一个轻度模糊（`Blur HQ` 节点，半径设为 1–2 像素），以消除单像素跳变。

---

## 知识关联

**与程序化生成概述的关系**：程序化纹理是程序化生成思想在二维图像领域的具体落地形式，它直接使用了程序化生成概述中介绍的随机种子控制、参数驱动内容生成等核心思路，但将操作单元从几何体或关卡对象缩小到像素级别的颜色和高度值。

**向上支撑的技术领域**：掌握程序化纹理制作后，可以进一步学习 Substance Designer 中的 `FX-Map` 深度编程（使用 Substance 脚本语言 `sbsdoc` 编写自定义节点）、Houdini 中基于 VEX 的体积纹理生成、以及实时着色器（GLSL/HLSL）中直接在 GPU 上运算的程序化纹理技术——后者将纹理生成从离线预烘焙提升为真正的实时无参数限制方案，代价是需要额外的 GPU 计算开销。