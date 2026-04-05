---
id: "cg-ambient-occlusion"
concept: "环境光遮蔽"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 2
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 环境光遮蔽

## 概述

环境光遮蔽（Ambient Occlusion，AO）是一种近似模拟全局光照中"角落变暗"现象的渲染技术。其物理直觉来自这样一个观察：当两个表面相互靠近时，它们之间的区域接收到的半球方向入射光线会被遮挡，导致该区域比开阔区域更暗。正式定义为：某点 $p$ 处的遮蔽因子 $A(p) = \frac{1}{\pi} \int_{\Omega} V(p, \omega) \cos\theta \, d\omega$，其中 $V(p, \omega)$ 是可见性函数（沿方向 $\omega$ 未被遮挡时为1，否则为0），$\Omega$ 为法线所在半球。

AO 概念最早在 Zhukov 等人于 1998 年的论文《Ambient Light»中被正式提出，并在 2002 年 Hayden Landis 将其应用于《指环王》视觉特效管线后进入工业界主流。实时渲染领域的突破发生在 2007 年，Crytek 在《孤岛危机》中首次将屏幕空间环境光遮蔽（SSAO）集成进商业游戏引擎，从此 AO 成为实时渲染管线的标配。

AO 在渲染中的重要性在于它以极低的计算成本提供接近真实的接触阴影和空间感。没有 AO 的场景往往显得"悬浮"——椅子腿与地面的连接处、墙角、人物手指缝隙都会缺乏应有的暗化效果，直接破坏场景的可信度。

---

## 核心原理

### SSAO：屏幕空间采样法

Crytek 版 SSAO（2007）的实现思路是：在 G-Buffer 重建的世界空间位置 $p$ 周围，在以法线 $\mathbf{n}$ 为轴的半球内随机采样若干点（通常 16～64 个），将每个采样点的深度与 G-Buffer 深度做比较，若采样点"深于"场景表面则认为该方向被遮挡。遮蔽率由被遮挡采样点的比例估算。

SSAO 存在两个固有缺陷：第一，采样半径固定，不能区分近处小细节与远处大型遮蔽；第二，原始算法采用整球采样而非半球采样，会在内凹曲面产生自遮蔽伪影（self-occlusion bias）。John Chapman 在 2013 年发表的教程中提出的修正版将采样限制在法线半球内，成为 Unity 等引擎内置 SSAO 的基础。

### HBAO：基于水平角的遮蔽算法

HBAO（Horizon-Based Ambient Occlusion）由 NVIDIA 于 2008 年随 GeForce 8 系列 GPU 一同发布，并详细描述于 Louis Bavoil 等人的 SIGGRAPH 2008 论文中。其核心改进在于沿若干方向向外采样，对每个方向求最大仰角（horizon angle）$h(\phi)$，遮蔽量由 $A = 1 - \frac{1}{N}\sum_{\phi} \sin(h(\phi))$ 估算。

相比 SSAO，HBAO 正确使用了深度缓冲的导数信息（$\partial z/\partial x$, $\partial z/\partial y$）来重建局部切平面，因此在平坦表面上的自遮蔽现象大幅减少。典型实现使用 8 个步进方向、每方向 4 步，共 32 次深度采样，性能消耗约为同分辨率 SSAO 的 1.5～2 倍，效果提升则非常明显。NVIDIA 后来发布的 HBAO+ 还加入了时间累积（TAA 复用）以降低噪点。

### GTAO：基于地平线积分的解析近似

GTAO（Ground Truth Ambient Occlusion）由 Jorge Jimenez 等人在 2016 年 SIGGRAPH Advances in Real-Time Rendering 课程中提出。其数学本质是将半球积分转化为对弯曲角（bent angle）的解析积分，公式为：

$$A = \frac{1}{\pi} \int_0^{2\pi} \int_{h_1(\phi)}^{h_2(\phi)} \cos\theta \, d\theta \, d\phi = \frac{1}{2\pi} \int_0^{2\pi} [\sin h_2(\phi) - \sin h_1(\phi)] \, d\phi$$

GTAO 不仅输出遮蔽因子，还同时输出**弯曲法线**（bent normal）——即未被遮挡方向的平均方向向量，这使得它能直接与环境贴图采样联动，得到更准确的间接漫反射着色。《荒野大镖客：救赎 2》（2018）和 UE5 Lumen 前置管线都采用了 GTAO 或其变体。GTAO 的采样数量通常为每像素 8 方向 × 8 步 = 64 次深度采样，配合时间抗锯齿可降到每帧 8 次。

---

## 实际应用

**游戏引擎集成**：Unity HDRP 提供三种 AO 模式——SSAO、GTAO 和 Ray-Traced AO，其中 GTAO 为默认选项。Unreal Engine 5 在 Lumen 关闭时使用 GTAO，开启 Lumen 时 AO 由 Lumen 的短距离 GI 隐式覆盖。

**离线渲染的对比基准**：在 Blender Cycles 等路径追踪渲染器中，AO 通过直接对半球均匀采样 1024 次以上获得，称为"Ground Truth AO"，常用来评测实时算法的误差量。实测中 GTAO 在光滑表面的误差约为 3～5%，而 SSAO 可达 15～20%。

**微表面自遮蔽**：在 PBR 管线中，GTAO 输出的弯曲法线可替换镜面反射的采样方向，粗略模拟镜面 AO（Specular Occlusion），避免凹陷区域出现不真实的高光亮斑。

---

## 常见误区

**误区一：SSAO 使用整个球体采样是正确的**。原始 Crytek 实现确实使用了球体（而非半球）采样，并用深度比较做偏移修正，这实际上是一种 hack。它在背向法线的方向仍然会产生遮蔽贡献，导致大曲率表面出现错误暗化。正确做法（John Chapman 修正版）是将所有采样点限制在法线正半球内，深度比较时排除法线背面的点。

**误区二：AO 可以替代阴影**。AO 只计算短距离的遮蔽积分（采样半径通常 0.5～2 米），无法模拟定向光的投影阴影。它模拟的是天空光或均匀环境光被遮挡的效果，与点光源/方向光阴影在物理上是正交的两个概念，需同时使用。

**误区三：HBAO 比 SSAO 慢太多、不划算**。在现代 GPU 上（如 RTX 3080 级别），1080p 分辨率下 SSAO 约耗时 0.4ms，HBAO+ 约耗时 0.7ms，差距不足 0.3ms，而视觉质量提升显著。GTAO 配合 TAA 的每帧成本约为 0.9ms，在 30fps 或 60fps 的预算分配中均可接受。

---

## 知识关联

学习环境光遮蔽需要先理解**全局光照概述**中的渲染方程和可见性函数 $V(p, \omega)$ 的定义——AO 本质上是对渲染方程中环境光项进行可见性加权积分的近似。G-Buffer 的深度缓冲重建世界坐标的原理（逆投影矩阵应用）是 SSAO/HBAO 实现的前置知识。

在后续学习**屏幕空间 GI（SSGI）**时，GTAO 输出的弯曲法线直接作为 SSGI 的采样起始方向；SSGI 可以看作 GTAO 的延伸——不只检测遮蔽，还对被遮挡方向的 G-Buffer 颜色进行采样，从而把遮蔽信号升级为完整的一次弹射间接漫反射。理解 AO 的积分公式和采样策略，是理解 SSGI 为何需要去噪（denoising）及时间累积的基础。