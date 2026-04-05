---
id: "cg-smaa"
concept: "SMAA"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# SMAA（子像素形态学抗锯齿）

## 概述

SMAA（Subpixel Morphological Anti-Aliasing）是由Jorge Jimenez等人于2012年在EUROGRAPHICS会议上发表的一种基于图像空间的抗锯齿算法。它的全称已经揭示了其两大技术支柱：**形态学边缘检测**与**子像素精度重建**。与其前身MLAA（形态学抗锯齿）相比，SMAA将CPU实现迁移至GPU，并引入了精确的子像素信息处理能力，使其成为实时渲染领域中精度与性能最为均衡的后处理抗锯齿方案之一。

SMAA的设计目标是在保持FXAA那样低性能开销的同时，获得接近MSAA 4x甚至8x的视觉质量。其核心创新在于使用预计算的**面积纹理（Area Texture）**和**搜索纹理（Search Texture）**来替代MLAA中昂贵的CPU端形状匹配运算，将整个抗锯齿流程压缩为三个GPU渲染Pass。这种设计让SMAA能够在DirectX 9兼容硬件上以极低的额外开销（通常低于1ms）运行，同时在复杂几何边缘上的表现明显优于FXAA的简单模糊策略。

SMAA重要性不仅体现在视觉质量上，更在于它首次系统化地将**时间性抗锯齿**与空间形态学方法结合，其SMAA T2x变体通过利用相邻帧的历史信息实现了接近SSAA 2x的效果，为后来TAA的普及奠定了实践基础。

## 核心原理

### 三Pass渲染管线

SMAA的完整实现分为三个独立的渲染Pass，每个Pass具有明确的功能职责：

**Pass 1：边缘检测（Edge Detection）**
输入原始帧缓冲，检测场景中存在颜色或深度突变的像素位置，输出一张R/G双通道的**边缘贴图**，分别存储水平方向和垂直方向的边缘信息。SMAA支持三种边缘检测模式：基于亮度（Luma）、基于颜色（Color）和基于深度（Depth），其中颜色模式检测质量最高但开销也最大。检测阈值通常设置为0.1，低于此值的对比度差异会被忽略以避免噪声干扰。

**Pass 2：混合权重计算（Blending Weight Calculation）**
这是SMAA算法最复杂的核心步骤。对于每个被标记的边缘像素，算法沿边缘方向搜索连续的边缘线段端点，最大搜索距离默认为**16个像素**（可配置为32或64）。搜索完成后，通过查询预计算的**面积纹理（160×560像素）**，根据线段两端的形状类型（L形、Z形、U形等7种模式共80种组合）和子像素覆盖率，精确计算出每个像素的RGBA混合权重，输出至混合权重贴图。

**Pass 3：邻域混合（Neighborhood Blending）**
最终Pass读取原始颜色缓冲和上一步的混合权重贴图，对每个像素按照计算出的权重对其上下左右邻居进行加权混合，得到最终的抗锯齿图像。这一步骤是线性的，GPU开销极低。

### 面积纹理与搜索纹理

SMAA最具创意的工程设计在于将形态学的形状匹配问题转化为纹理查找问题。

**面积纹理（Area Texture）**：离线预计算，存储了所有可能的边缘线段端点形状组合所对应的最优混合权重。纹理的两个坐标轴分别代表线段的左端距离`d_left`和右端距离`d_right`，查询返回一个双通道权重值（上侧权重和下侧权重）。这个纹理编码了解析计算的覆盖率积分结果，是SMAA能够实现子像素精度的关键。

**搜索纹理（Search Texture）**：66×33像素的小纹理，用于加速Pass 2中的端点搜索过程，将原本需要逐像素迭代的循环替换为纹理Bilinear采样步进，显著减少了搜索所需的GPU指令数。

### 子像素精度处理

SMAA的"Subpixel"特性来源于其对**水平/垂直边缘的精确覆盖率积分**。对于一条经过像素内部的对角线边缘，SMAA能够计算出像素的实际几何覆盖面积，而非像FXAA那样简单地根据对比度强度估算模糊量。这种基于覆盖率的混合公式可表示为：

$$C_{out} = C_{center} \cdot (1 - w) + C_{neighbor} \cdot w$$

其中混合权重 $w$ 直接来自面积纹理查询结果，对应该像素被边缘跨越的精确面积比例，因此在斜线和曲线边缘上能产生明显优于FXAA的重建效果。

## 实际应用

**游戏引擎集成**：SMAA的HLSL/GLSL参考实现以单头文件（`SMAA.hlsl`）形式分发，各主流引擎均有集成。虚幻引擎4在早期版本中将SMAA T2x作为TAA的备选项，Unity的后处理栈v2（Post Processing Stack v2）也内置了SMAA支持，可通过`Anti-aliasing Mode`直接选择Quality档（等效SMAA 1x）或Performance档。

**质量档位配置**：SMAA官方实现预设了四个质量档位——`SMAA_PRESET_LOW`、`MEDIUM`、`HIGH`和`ULTRA`。ULTRA档将最大搜索距离提升至32像素、搜索步数增至16步，在包含大量细长几何（如栅栏、电线）的场景中效果最为显著。

**SMAA T2x时间性扩展**：通过引入2帧交替的**亚像素抖动偏移**（Jitter Pattern），结合历史帧重投影混合，SMAA T2x在静止画面上可达到接近SSAA 2x的质量，而运动场景下由于历史帧权重衰减机制，鬼影现象得到有效控制。

**控制台平台优化**：在PS4和Xbox One时代，SMAA因为只需要Shader Model 3.0特性且没有硬件光追依赖，成为大量主机游戏的首选抗锯齿方案，典型案例包括《刺客信条：大革命》的主机版本。

## 常见误区

**误区一：认为SMAA只是"更慢的FXAA"**
SMAA与FXAA的本质差异不在速度而在方法论。FXAA通过局部对比度估算**模糊程度**，其结果是一种近似模糊操作，会损失图像清晰度。SMAA通过形状匹配计算**几何覆盖率**，进行精确的亚像素混合，在保留高频细节（如细线条、文字边缘）方面明显优于FXAA。直接比较两者在细密格纹边缘上的输出可以明显看到差距。

**误区二：SMAA能完全替代MSAA**
SMAA是纯后处理算法，处理的是最终帧缓冲图像，因此对**着色器计算的锯齿**（如高光闪烁、次表面散射边缘）完全无效。MSAA在光栅化阶段对几何边缘进行多重采样，能解决几何级别的锯齿问题。在延迟渲染管线中，MSAA实现复杂且开销极高，但SMAA无法弥补延迟渲染固有的着色锯齿问题，两者的适用范围存在本质区别。

**误区三：搜索距离越大越好**
增大搜索距离（如从16增至64像素）会显著提升Pass 2的GPU开销，但在大多数实际场景中收益递减明显——游戏场景中超过32像素的连续直线边缘极少出现，且更长的搜索距离会导致误匹配的概率增大，反而在某些角落产生不自然的过度混合伪影。实践中SMAA HIGH档（搜索距离16）已能覆盖99%以上的典型场景需求。

## 知识关联

**与FXAA的继承关系**：SMAA的边缘检测阈值设计和GPU单Pass思路直接受到FXAA的启发，但FXAA的核心是基于梯度的模糊滤波，而SMAA用形态学图案匹配替换了这一步骤。理解FXAA中亮度梯度计算和局部对比度的工作原理，有助于理解为何SMAA需要独立的边缘检测Pass而非复用FXAA的单步流程。

**与TAA的演进关系**：SMAA T2x是空间形态学抗锯齿与时间性采样融合的早期尝试，其历史帧混合权重计算方式和运动向量重投影逻辑直接预示了后来TAA的核心机制。现代渲染引擎中TAA几乎取代了SMAA的地位，但在不接受TAA鬼影的场景（如2D游戏、UI渲染）中，SMAA 1x仍是一种简洁有效的选择。

**与MLAA的技术溯源**：SMAA的面积纹理设计直接来源于2009年Intel提出的MLAA算法，区别在于MLAA