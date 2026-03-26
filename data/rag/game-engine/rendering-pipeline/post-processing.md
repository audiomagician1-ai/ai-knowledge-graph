---
id: "post-processing"
concept: "后处理效果"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 2
is_milestone: false
tags: ["后处理"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
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

# 后处理效果

## 概述

后处理效果（Post-Processing Effects）是指在渲染管线完成主要几何体绘制并输出颜色缓冲后，对最终图像进行的全屏像素级操作。与在三维空间中进行的光照计算不同，后处理效果完全在二维屏幕空间中对已有的颜色、深度、法线等缓冲数据执行计算，因此也被称为"屏幕空间效果"。

后处理作为独立管线阶段的概念在2000年代中期随着可编程着色器的普及而成熟。早期游戏引擎如Quake系列使用的是固定功能管线，无法灵活添加全屏效果。DirectX 9引入的Shader Model 2.0（2002年）使开发者可以编写任意全屏着色器，标志着现代后处理时代的开始。虚幻引擎3（2006年发布）将Bloom、DoF等效果统一封装为"Post Process Volume"，成为引擎级后处理框架的早期范本。

后处理效果的重要性在于：用极低的几何处理开销大幅提升画面真实感。一个Bloom效果只需对颜色缓冲执行两次高斯模糊，却能模拟真实摄像机镜头的光晕现象；而如果要在三维空间中实现相同效果则计算量将增加数个数量级。

---

## 核心原理

### Bloom（泛光）

Bloom的实现分为三步：首先用亮度阈值过滤器提取颜色缓冲中亮度超过某个值（通常为HDR空间下1.0）的像素；然后对提取结果执行多次降采样（Downsample）与双线性高斯模糊；最后将模糊结果与原始颜色叠加（Additive Blending）。

现代Bloom实现（如虚幻引擎5的Bloom）采用**多分辨率金字塔卷积**，分别在原图1/2、1/4、1/8、1/16分辨率下进行模糊再逐层上采样合并，每层权重可单独调整。这比单层高斯模糊更符合真实镜头的点扩散函数（Point Spread Function）形态。

### SSAO（屏幕空间环境光遮蔽）

SSAO（Screen Space Ambient Occlusion）由Crytek在《孤岛危机》（2007年）中首次在实时游戏中使用。其核心公式是：对当前像素的切线半球内随机采样N个点（通常N=16或64），将采样点重投影回屏幕空间并与深度缓冲中的深度值比较，被遮挡的采样点占比即为该像素的遮蔽因子AO值（范围0到1）。

SSAO需要深度缓冲和法线缓冲作为输入，这正是延迟渲染架构中G-Buffer天然提供的数据。在随机采样方向的生成上，标准做法是预生成一张4×4像素的随机旋转核心纹理（Noise Texture），让每个像素的采样核心旋转方向不同，然后通过3×3模糊去除由此产生的噪点。HBAO+（Horizon-Based AO Plus）是SSAO的改进版本，将时间累积引入AO计算，噪声更低。

### DoF（景深，Depth of Field）

DoF模拟真实镜头中焦平面以外物体出现模糊的光学现象。引擎中通常使用**弥散圆（Circle of Confusion，CoC）**半径来描述每个像素的模糊程度，计算公式为：

$$CoC = \frac{A \cdot f \cdot (d - d_{focus})}{d \cdot (d_{focus} - f)}$$

其中 $A$ 为光圈直径，$f$ 为焦距，$d$ 为像素深度，$d_{focus}$ 为对焦距离。CoC值大的像素会被大半径模糊核处理。实时DoF常用的算法有Bokeh散景DoF（在CoC大的位置绘制多边形光斑）和Tile-Based DoF（将屏幕分块处理以减少带宽消耗）。

### TAA（时间抗锯齿，Temporal Anti-Aliasing）

TAA通过将当前帧与历史帧混合来消除锯齿，混合权重通常为当前帧0.1、历史帧0.9。为避免相机运动时历史帧错位产生"鬼影"（Ghosting），TAA使用运动向量（Motion Vector）缓冲对历史帧进行**重投影（Reprojection）**：将当前像素坐标减去其运动向量，得到该像素上一帧的屏幕位置，再从历史缓冲中采样对应颜色。当重投影位置超出屏幕范围或历史颜色与当前邻域颜色差异过大时，TAA会将历史权重降低（Clamp/Clip操作），以减少鬼影。虚幻引擎5的TSR（Temporal Super Resolution）是TAA的超分辨率扩展版本，可将内部渲染分辨率降至目标分辨率的50%再通过时间累积还原。

### Motion Blur（运动模糊）

运动模糊分为两类：摄像机运动模糊（全屏）和物体运动模糊（Per-Object）。屏幕空间实现依赖每帧生成的运动向量缓冲，对每个像素沿其运动向量方向采样若干点（通常8到16个样本）并取平均，模拟快门开放期间的积分曝光效果。运动向量过长时通常会对样本数量进行插值限制，以避免过度模糊。

---

## 实际应用

**Unity的URP/HDRP后处理栈**：Unity从2019版本起将后处理统一为Volume框架，Bloom、SSAO、DoF、TAA等均以Volume Override形式挂载到场景中，通过混合权重实现区域性效果过渡。HDRP中的Bloom内置了镜头光晕（Lens Flare）和条纹光晕（Lens Dirt）叠加层。

**《赛博朋克2077》的后处理策略**：CD Projekt Red在该游戏中使用了DLSS（基于TAA框架的神经网络超分辨率）配合Chromatic Aberration（色差）和Film Grain（胶片颗粒）效果，后两者也属于后处理范畴，专门模拟光学镜头的成像缺陷以增强电影质感。

**移动端后处理优化**：在移动GPU上，SSAO的随机采样开销过高，常见替代方案是SSAO样本数降至4个并配合双边滤波上采样，或使用基于深度差异的GTAO（Ground Truth AO）近似。DoF在移动端通常用分桶（Bucket）模糊代替精确CoC计算。

---

## 常见误区

**误区一：认为后处理效果一定要在Tone Mapping之后执行**。实际上，Bloom必须在Tone Mapping（HDR转LDR）之前计算，因为Bloom的亮度阈值过滤依赖HDR值（例如太阳光亮度可达10.0以上）；而Film Grain、Color Grading等效果则需要在Tone Mapping之后对LDR图像操作。执行顺序错误会导致Bloom在暗部出现或高光完全丢失。

**误区二：TAA会完全消除锯齿而无需MSAA**。TAA对静止场景效果极好，但对快速运动的细小物体（如高速旋转的风扇叶片）会产生严重鬼影，并且TAA天然会对图像产生轻微模糊（因为历史帧混合相当于时域低通滤波）。这就是为什么许多引擎会在TAA之后额外施加一次锐化滤波（如Unsharp Mask或RCAS）来补偿模糊损失。

**误区三：SSAO可以替代光照计算中的环境遮蔽**。SSAO只能计算屏幕可见区域的遮蔽，对屏幕边缘外的几何体完全无感知，且完全依赖深度精度，在大型开放场景远处的小型几何细节上效果很差。烘焙的静态光照贴图中包含的全局环境遮蔽与SSAO是互补关系，而非替代关系。

---

## 知识关联

**前置知识——延迟渲染**：SSAO、TAA、DoF等效果的实现高度依赖延迟渲染输出的G-Buffer，具体包括深度缓冲（所有屏幕空间效果的基础）、法线缓冲（SSAO采样方向计算）、速度/运动向量缓冲（TAA重投影、Motion Blur）。在前向渲染管线中实现等价效果需要额外的渲染Pass专门输出这些缓冲，开销更大。

**后续知识——抗锯齿技术**：TAA在本文中已作为后处理效果介绍，但抗锯齿技术这一专题还涵盖MSAA（多重采样抗锯齿，发生在光栅化阶段而非后处理阶段）、FXAA（快速近似抗锯齿，纯后处理但质量低于TAA）以及DLSS/FSR等基于机器学习的超分辨率方案。这些方案在原理上均与TAA的时间累积思路有直接演进关系。