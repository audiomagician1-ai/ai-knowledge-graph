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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 色调映射

## 概述

色调映射（Tone Mapping）是将高动态范围（HDR）图像压缩至显示设备可表示的低动态范围（LDR）的数学变换过程。真实世界的亮度范围可跨越10^5量级（从0.001 nit的暗室到100,000 nit的直射阳光），而标准显示器通常只能表示0.1到300 nit，因此直接截断高亮部分会损失大量细节，色调映射算子（Tone Mapping Operator, TMO）的职责正是在这一压缩过程中尽可能保留视觉信息。

色调映射的概念最早来自摄影暗房技术，柯达于20世纪中期总结出"Zone System"，将亮度分为0到10的11个区域以指导曝光控制。数字图形学领域对其正式建模始于1990年代末，Greg Ward的Larson等人在1997年发表了基于人眼视觉适应的TMO论文，随后2002年Erik Reinhard提出了著名的全局算子公式，标志着实时图形中色调映射研究的起点。

在实时渲染后处理管线中，色调映射是HDR渲染缓冲区转为最终帧缓冲区的最后一道关键转换。不同的算子在高光保留、对比度分布、色彩饱和度上表现各异，直接影响玩家对画面"电影感"或"真实感"的感知判断。

## 核心原理

### Reinhard算子

Reinhard全局算子（2002）是最简洁的实时色调映射公式：

$$L_{out} = \frac{L_{in}}{1 + L_{in}}$$

其中 $L_{in}$ 为输入线性亮度，$L_{out}$ 为映射后亮度，均已归一化至白点。该曲线在低亮度区域近似线性（斜率趋向1），在高亮度区域渐进压缩至1，因此绝不会出现截断（clip），但代价是高光部分永远无法达到纯白，整体画面偏灰。扩展版本引入白点参数 $W$：

$$L_{out} = \frac{L_{in}(1 + L_{in}/W^2)}{1 + L_{in}}$$

当 $W=4$ 时，可使亮度4以上的内容映射至接近1，改善了高光表现，但肩部曲线仍较柔软，缺乏电影胶片的硬肩特征。

### ACES算子

ACES（Academy Color Encoding System）由美国电影艺术与科学学院于2014年正式发布，其RRT（Reference Rendering Transform）与ODT（Output Display Transform）构成完整色彩管线。实时渲染中常用Krzysztof Narkowicz于2015年拟合的近似公式：

$$L_{out} = \frac{L_{in}(2.51 \cdot L_{in} + 0.03)}{L_{in}(2.43 \cdot L_{in} + 0.59) + 0.14}$$

ACES曲线具有明显的"S形"特征：暗部对比度提升（脚部更陡），中间调过渡自然，高光肩部快速压缩。与Reinhard相比，ACES在0.18灰附近的对比度约高出15%，但代价是暗部噪声更加可见，且饱和色在高亮度下会向白色偏移（色相偏移问题）。

### GT Filmic（通用胶片曲线）

GT Filmic（也称GenericFilmic或Haarm-Pieter Duiker曲线系列）是一类参数化曲线框架，允许美术通过调节"toe strength"（脚强度）、"shoulder strength"（肩强度）、"linear angle"（线性段斜率）等6到8个参数自定义整条曲线形状。Unity的官方HDR实现（URP/HDRP中的Tonemapping组件）从2019年起内置了基于此框架的"Custom"模式，允许每个项目独立调整曲线而无需修改着色器代码。GT Filmic的最大优势在于对色相保留更好——通过独立处理亮度通道再重新上色，避免了ACES式的高饱和色向白偏移问题。

### 三种算子的量化对比

| 特性 | Reinhard | ACES近似 | GT Filmic |
|------|----------|----------|-----------|
| 中灰对比度 | 低 | 高（+15%） | 可调 |
| 高光截断 | 无 | 有轻微硬切 | 可配置 |
| 色相保留 | 好 | 中等 | 最佳 |
| GPU指令数（近似） | ~4 | ~8 | ~20-50 |

## 实际应用

**游戏引擎的默认选择**：Unreal Engine 4及5默认使用ACES近似曲线，这使得UE项目在未调整后处理体积的情况下呈现出饱和度略低、高光略硬的典型"虚幻风格"。Unity HDRP在2021.2之后将默认切换至中性（Neutral）曲线，接近GT Filmic的低对比参数配置，偏向摄影自然感。

**VR场景的特殊需求**：VR头显（如Meta Quest 2）峰值亮度约为100 nit，显著低于PC显示器，若使用标准ACES曲线会导致暗部压缩过重、场景显得发黑。VR开发者通常改用修改版Reinhard或降低ACES的脚部斜率，将中灰点从0.18上移至0.25以补偿。

**HDR显示输出**：当目标为HDR10标准（峰值1000 nit，PQ传递函数）时，色调映射曲线的输出范围需从[0,1]扩展至[0, 1000]，并在色调映射后再叠加PQ OETF（光电转换函数）编码，此时Reinhard的"永不截断"特性反而成为劣势，ACES的硬肩更适合HDR10的高亮细节表达。

## 常见误区

**误区一：色调映射等同于Gamma校正**。Gamma校正（sRGB编码，γ≈2.2）是将线性光值转为显示器可识别的非线性编码，是对显示物理特性的补偿；色调映射是对亮度范围进行重新分布的艺术性压缩。两者在后处理管线中顺序固定：色调映射在前，sRGB编码在后。混淆二者会导致在错误阶段对数据进行操作，产生色彩断层或伽马双重校正。

**误区二：ACES曲线即为完整的ACES管线**。实时渲染中常用的"ACES近似公式"仅模拟了ACES色彩管线中的曲线形状，并未真正将场景转换至ACES2065-1色彩空间，也没有进行完整的RRT+ODT变换。Narkowicz的拟合公式与官方ACES在色域边界处最大误差可达0.03（以Lout计），对于需要精确色彩管理的影视制作流程，必须使用完整ACES SDK而非该近似值。

**误区三：色调映射越复杂画面越好**。GT Filmic需要20-50条GPU指令而Reinhard仅需4条，但在移动端每帧后处理预算有限时（Mali G77上后处理总预算约0.5ms），使用高参数GT Filmic可能挤占抗锯齿或Bloom的带宽，实际画面效果反而不如参数精调的简单曲线。选择算子必须结合目标平台的性能余量综合决策。

## 知识关联

学习色调映射需要先理解**后处理概述**中的渲染缓冲区格式（尤其是R11G11B10F与R16G16B16A16F两种HDR缓冲区格式对高光存储精度的影响），以及线性光照工作流的基本概念。

色调映射向后衍生出**色彩分级**（Color Grading），后者在色调映射完成后的LDR空间内对色相/饱和度/亮度进行艺术性调整，通常通过3D LUT（查找表，分辨率常为32³或64³）实现；二者在管线位置相邻但操作对象不同。**自动曝光**（Auto Exposure / Eye Adaptation）则决定了送入色调映射算子之前的场景平均亮度，通过调整曝光值（EV）使中灰点落在算子的线性段，因此自动曝光的标定精度直接影响色调映射的工作区间。最终，这两个模块连同色调映射共同构成完整的**HDR管线**，处理从场景线性光照到最终帧输出的全流程转换。