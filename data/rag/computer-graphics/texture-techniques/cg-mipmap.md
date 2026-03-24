---
id: "cg-mipmap"
concept: "Mipmap"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# Mipmap（多级渐远纹理）

## 概述

Mipmap 是一种预计算的纹理序列技术，将同一张纹理图像按照2的幂次方逐级缩小，生成一组分辨率递减的纹理层级。原始纹理（Level 0）保持完整分辨率，每向上一个级别，宽度和高度各缩减一半，直至最终变为1×1像素的单色纹理。例如，一张256×256的基础纹理将产生 Level 0（256×256）、Level 1（128×128）……Level 8（1×1）共9个级别，总内存占用约为原纹理的4/3倍（即原大小的133%）。

这项技术由 Lance Williams 于1983年在论文《Pyramidal Parametrics》中首次正式提出，名称"Mip"来源于拉丁语短语"multum in parvo"，意为"在小空间中放入多量内容"。Williams 的核心洞察是：当纹理在屏幕上以小于其原始尺寸显示时，直接采样会引发走样（aliasing）现象，而预先对纹理进行下采样可以显著抑制这种高频噪声。

Mipmap 的重要性在于它同时解决了两个对立的纹理渲染问题：**欠采样走样**（纹理远离摄像机时产生闪烁摩尔纹）和**渲染性能**（GPU 可以访问更符合屏幕像素密度的纹理级别，避免大量无效的纹素读取，提升缓存命中率）。现代图形 API（OpenGL、DirectX、Vulkan）均将 Mipmap 作为标准纹理功能内置支持。

---

## 核心原理

### LOD 级别计算

GPU 通过计算**纹理坐标的屏幕空间导数**来确定应该采样哪个 Mipmap 层级。具体公式为：

$$\lambda = \log_2\left(\max\left(\sqrt{\left(\frac{\partial u}{\partial x}\right)^2 + \left(\frac{\partial v}{\partial x}\right)^2},\ \sqrt{\left(\frac{\partial u}{\partial y}\right)^2 + \left(\frac{\partial v}{\partial y}\right)^2}\right)\right)$$

其中 $u, v$ 为纹理坐标，$x, y$ 为屏幕像素坐标，$\lambda$ 即为 LOD 值（Level of Detail）。当 $\lambda = 0$ 时使用完整分辨率纹理；$\lambda = 1$ 时使用半分辨率的 Level 1；$\lambda$ 为非整数时，则在相邻两个级别之间进行**三线性插值**（Trilinear Filtering）——先在各自级别内做双线性采样，再对两个结果按比例混合。

### LOD 偏移（Bias）机制

LOD Bias 是一个加法偏移值，直接修改 $\lambda$ 计算结果：$\lambda' = \lambda + \text{bias}$。负偏移值（如 bias = -1.0）会迫使 GPU 向更高分辨率的 Mipmap 级别采样，使纹理看起来更清晰但可能引入走样；正偏移值则反之，使纹理更早模糊，常用于模拟景深效果或优化某些卡通渲染风格。在 OpenGL 中，通过 `GL_TEXTURE_LOD_BIAS` 参数设置；DirectX 的 HLSL 语法中，`SampleBias()` 函数接受一个 float 类型的 bias 参数。

### 下采样滤波算法

生成 Mipmap 各级别时，下采样方式直接影响纹理质量。最简单的方法是**盒式滤波（Box Filter）**：将2×2像素块取平均值，计算速度快但会导致细节损失过于激进。更高质量的选择包括 **Kaiser 滤波**（一种基于贝塞尔函数的窗函数滤波器，能保留更多高频细节）和 **Lanczos 重采样**（使用 sinc 函数的截断近似，下采样后纹理更锐利）。游戏引擎如 Unreal Engine 5 默认使用 Lanczos 滤波生成 Mipmap，而 GPU 硬件实时生成（如 OpenGL 的 `glGenerateMipmap`）通常使用盒式滤波。

---

## 实际应用

**地形渲染中的 Mipmap 分层**：在开放世界游戏中，地面纹理在近处以 Level 0（如2048×2048）显示，随距离增加自动切换到 Level 4（128×128）乃至更低级别。《荒野大镖客：救赎2》的地形系统利用 Mipmap 与流式加载结合，使得地形纹理在不同观察距离下始终保持最优的性能与画质平衡。

**UI 与粒子特效的 Mipmap 关闭情形**：屏幕空间 UI 纹理通常**不应**启用 Mipmap，因为 UI 元素与屏幕像素一一对应，启用后反而会浪费显存（额外33%）且在某些缩放情形下引入模糊。粒子系统中，面向摄像机的 Billboard 纹理也常见禁用 Mipmap 的配置，以保留烟雾、火焰边缘的清晰度。

**调试 Mipmap 级别可视化**：开发者常使用"Mipmap 可视化纹理"——为不同级别分别赋予红、绿、蓝等纯色——来直观检查场景中 LOD 切换是否合理，识别由于 UV 展开问题导致意外跳级的区域。Unity 和 Unreal 的 Scene Debug View 均提供此功能。

---

## 常见误区

**误区1：Mipmap 一定会让纹理变模糊**  
这一判断只在使用 Nearest（最近点）Mipmap 模式时成立，此模式会在级别边界产生明显的"突变线"。启用三线性过滤（Trilinear Filtering）后，相邻 Mipmap 级别之间平滑插值，模糊感显著降低，且无论如何都比不使用 Mipmap 时在远处出现的闪烁走样更可接受。

**误区2：Mipmap 只节省显存**  
Mipmap 的主要收益并非显存节省（实际上多消耗33%显存），而是**纹理缓存命中率的提升**。当纹理以较小尺寸覆盖屏幕时，低分辨率 Mipmap 级别的数据量更小，GPU 的纹理缓存（L1/L2 cache，通常为16KB～512KB）能够容纳更多有效纹素，减少显存带宽压力，这才是 Mipmap 带来性能提升的根本机制。

**误区3：非2的幂次纹理无法使用 Mipmap**  
早期 OpenGL（2.0之前）确实要求纹理尺寸为2的幂次方，但 OpenGL 2.0 起引入 NPOT（Non-Power-Of-Two）纹理支持，DirectX 9.0c 及之后版本也完整支持非2幂纹理的 Mipmap 生成，现代 GPU 对此无硬件限制，只是非2幂纹理在向下采样时边界像素处理需要特殊对齐处理。

---

## 知识关联

Mipmap 建立在**纹理映射概述**的基础上——必须先理解 UV 坐标如何将三维表面映射到二维纹理，才能理解为何屏幕空间导数 $\partial u/\partial x$ 能反映纹理的缩放程度。没有纹理映射的基础，LOD 公式中"纹素与像素的比率关系"将无从理解。

Mipmap 是**各向异性过滤**（Anisotropic Filtering）的前置概念：各向异性过滤正是发现了 Mipmap 的局限性——标准 Mipmap 对纹理坐标导数取最大值，当纹理在一个轴向上拉伸（如以斜角观察地面时），会选择过于低分辨率的级别。各向异性过滤通过沿主导方向采集多个 Mipmap 样本来修正这一问题，因此它本质上是 Mipmap 采样策略的延伸与优化。

此外，**纹理流式加载**（Texture Streaming）系统正是以 Mipmap 的层级结构为基础设计的：流式加载按需将高分辨率的低层级（Level 0、Level 1）从磁盘动态载入显存，而始终在显存中保留高层级（如 Level 6 之后的小尺寸层级）作为后备，使得即便高清层级未加载完成，场景中也不会出现空白纹理，而是显示模糊但正确的低分辨率版本。
