---
id: "cg-tone-mapping"
concept: "色调映射"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 色调映射

## 概述

色调映射（Tone Mapping）是将高动态范围（HDR）图像的亮度值压缩至显示设备可表示的低动态范围（LDR，通常为 [0, 1]）的过程。现实世界的光照亮度范围可达 10⁻⁶ 到 10⁸ 尼特，而普通显示器仅能呈现 100~300 尼特，直接截断会丢失大量高光与暗部细节，因此必须使用色调映射算子进行非线性压缩。

色调映射的概念源于传统胶片摄影：胶片的曝光响应曲线（H&D 曲线）天然地对高光进行了柔和压缩，形成了人眼视觉上最舒适的明暗过渡。数字渲染领域在 2000 年代初引入了这一概念，Erik Reinhard 于 2002 年在 SIGGRAPH 发表的论文《Photographic Tone Reproduction for Digital Images》标志着现代色调映射研究的开端。

在实时渲染后处理管线中，色调映射通常是最后几步之一，在 Gamma 校正之前执行。若不进行色调映射，线性空间中超出 1.0 的亮度值（如太阳直射、爆炸光效）会被硬截断至纯白，画面会呈现大片死白区域，失去视觉层次感。

---

## 核心原理

### Reinhard 算子

Reinhard 算子是最经典的色调映射公式，由 Erik Reinhard 在 2002 年提出，其基础形式为：

$$L_{out} = \frac{L_{in}}{1 + L_{in}}$$

其中 $L_{in}$ 是线性空间的输入亮度，$L_{out}$ 是映射后的输出亮度。该公式的特性是：输入趋向无穷大时，输出渐近于 1.0，永远不会截断；输入为 0 时，输出也为 0，保留了暗部细节。

扩展形式引入了白点参数 $W$（场景中最亮像素的亮度值）：

$$L_{out} = \frac{L_{in} \left(1 + \frac{L_{in}}{W^2}\right)}{1 + L_{in}}$$

Reinhard 算子的缺点是对比度偏低，整体画面偏灰，且无法模拟胶片的饱和度响应，因此逐渐被更复杂的算子取代。

### ACES 算子

ACES（Academy Color Encoding System）是美国电影艺术与科学学院于 2014 年建立的行业标准色彩管理体系。在实时渲染中广泛使用的是由 Krzysztof Narkowicz 拟合的近似公式：

$$L_{out} = \frac{L_{in}(aL_{in} + b)}{L_{in}(cL_{in} + d) + e}$$

其中常用参数为 $a=2.51, b=0.03, c=2.43, d=0.59, e=0.14$，此公式对完整的 ACES RRT（Reference Rendering Transform）+ ODT（Output Device Transform）流程进行了廉价拟合。ACES 曲线的特点是中间调对比度强、高光压缩快、暗部轻微提升，整体观感更接近电影胶片效果，颜色更鲜明。Unreal Engine 4.15 版本后将 ACES 设定为默认色调映射算子。

### GT Filmic（Gran Turismo Filmic）算子

GT Filmic 算子由 Hajime Uchimura 在 2017 年 SIGGRAPH 的演讲《HDR Theory and practice》中提出，原名 Piece-wise Power Curve。该算子通过若干可调参数精确控制曲线形状，包括最大亮度 $P$、线性段斜率 $m$、暗部偏移 $a$、线性段长度 $l$ 等，具有极高的美术可控性：

$$f(x) = \left(\frac{x}{P}\right)^{c_3} \cdot P$$（简化版示意）

完整公式为分段函数，在暗部使用幂函数提升，在亮部使用对数收敛，线性过渡段保证中间调不变形。GT Filmic 的优势在于美术人员可以直接调节黑点、白点、肩部曲率等参数而不破坏整体曲线一致性，适合追求极高美术品质的项目，如《Gran Turismo Sport》的实时渲染管线。

---

## 实际应用

在 Unity URP/HDRP 中，色调映射通过 Volume 组件挂载，可在 Neutral、ACES 和自定义 Curve 三种模式间切换。在 Unreal Engine 中，ACES 被内置为默认选项，并在后处理体积中暴露了 FilmSlope（对应曲线斜率）、FilmToe（暗部提升量）、FilmShoulder（高光压缩强度）等参数供美术调整。

以一个典型的室外场景为例：太阳盘亮度在 HDR buffer 中可能高达 50.0（线性值），使用 Reinhard 算子时该区域压缩后为 50/51 ≈ 0.98，视觉上与 10.0 的区域（≈0.91）差距极小，导致天空整体偏白；使用 ACES 算子时，高光肩部压缩更快，太阳盘与天空之间的亮度梯度更突出；而 GT Filmic 则可由美术指定太阳盘必须映射到 0.95 的精确白点，同时保留云层高光的层次。

---

## 常见误区

**误区一：色调映射等于 Gamma 校正。** 两者是不同的操作：Gamma 校正（将线性值转换为 sRGB 值，幂次约为 1/2.2）是为了补偿显示器的非线性响应，而色调映射是将 HDR 范围压缩至 [0,1] 的亮度重映射。正确顺序是先执行色调映射，再执行 Gamma 校正，若顺序颠倒会导致高光截断与色彩失真同时出现。

**误区二：ACES 一定优于 Reinhard。** ACES 的高对比度和强饱和度对于写实风格场景效果显著，但对于需要低饱和度、柔和色调的日系动画风格游戏，ACES 的强烈肩部压缩会使皮肤色调过度偏红，Reinhard 或自定义 Filmic 曲线反而更符合目标美术风格。

**误区三：色调映射只作用于亮度通道。** 部分实现只对 luminance 值进行色调映射然后等比缩放 RGB，而 ACES 等完整算子对 RGB 三个通道分别映射，这会改变高饱和度区域的色相，即"色相漂移"（Hue Shift）。ACES 的橙色高光向黄色偏移是其有意为之的胶片特性，而并非实现错误。

---

## 知识关联

**前置概念——后处理概述：** 理解色调映射需要知道它在后处理栈中的位置：它接收 HDR Render Target（浮点格式，如 R11G11B10 或 RGBA16F）的输出，并产生 SDR 的 8-bit 结果，这一步是 HDR 渲染管线与最终显示输出之间的桥梁。

**后续概念——色彩分级：** 色彩分级（Color Grading）通常在色调映射之后通过 LUT（Look-Up Table，典型尺寸为 32×32×32 的 3D 纹理）实现，因此色调映射算子的选择直接决定了 LUT 的烘焙空间；若改变色调映射算子，已有的 LUT 资产需要重新制作。

**后续概念——自动曝光：** 自动曝光（Auto Exposure / EV 调整）在色调映射之前执行，它通过分析场景平均亮度动态调整曝光值（EV），使得进入色调映射算子的 $L_{in}$ 值保持在合适范围（通常目标中间灰为 0.18），避免整体过曝或欠曝后色调映射曲线工作在低效区段。

**后续概念——HDR 管线：** 在支持 HDR 输出的显示器（亮度可达 1000~10000 尼特，如符合 HDR10 或 Dolby Vision 标准的设备）上，色调映射的目标不再是 [0,1] 的 SDR 空间，而是需要输出 PQ（Perceptual Quantizer）或 HLG 编码的信号，此时 ACES 的完整 ODT 流程与 ST 2084 标准的对接方式成为核心技术问题。
