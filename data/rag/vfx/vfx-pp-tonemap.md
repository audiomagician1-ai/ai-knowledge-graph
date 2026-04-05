---
id: "vfx-pp-tonemap"
concept: "色调映射"
domain: "vfx"
subdomain: "post-process"
subdomain_name: "后处理特效"
difficulty: 2
is_milestone: false
tags: ["基础"]

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
updated_at: 2026-03-26
---


# 色调映射

## 概述

色调映射（Tone Mapping）是将高动态范围（HDR，High Dynamic Range）图像转换为低动态范围（LDR，Low Dynamic Range）图像的数学变换过程。真实世界的亮度范围可达 $10^{-4}$ 到 $10^8$ cd/m²，跨越约12个数量级，而普通显示器只能呈现约100 cd/m²的亮度范围。色调映射正是要将这个巨大的亮度差距"压缩"到显示设备可表达的范围内，同时尽量保留视觉上的明暗层次感。

色调映射技术的系统研究始于1990年代的计算机图形学领域。Greg Ward 在1994年提出了基于人眼适应机制的早期算法，而 Erik Reinhard 等人在2002年发表的论文《Photographic Tone Reproduction for Digital Images》中提出了至今仍被广泛引用的 Reinhard 算子，奠定了现代实时色调映射的基础。在游戏和实时渲染领域，色调映射是 HDR 渲染管线的终端环节，直接决定玩家看到的最终画面色彩质感。

## 核心原理

### 亮度压缩的数学本质

色调映射本质上是一个将输入亮度 $L_{in} \in [0, +\infty)$ 映射到输出亮度 $L_{out} \in [0, 1]$ 的单调递增函数 $f$。所有色调映射算子都需要满足：$f(0) = 0$，$f(+\infty) \leq 1$，且 $f$ 在低亮度区域斜率接近1（保留暗部细节），在高亮度区域斜率趋向0（防止高光过曝）。不同算子之间的核心差异在于这条压缩曲线的具体形状，尤其是中间调的对比度保留方式。

### Reinhard 算子

Reinhard 算子是最简洁的经典算法，其公式为：

$$L_{out} = \frac{L_{in}}{1 + L_{in}}$$

这个公式将任意正值亮度映射到 $[0, 1)$ 区间，当 $L_{in} = 1$ 时输出为 0.5。扩展版本引入了"白点"参数 $L_{white}$：

$$L_{out} = \frac{L_{in}(1 + L_{in}/L_{white}^2)}{1 + L_{in}}$$

其优点是计算成本极低，缺点是整体画面偏灰、饱和度损失明显，高光区域缺乏胶片感。

### Filmic 曲线（John Hable / Uncharted 2）

2010年，John Hable 在为《神秘海域2》开发渲染管线时提出了 Filmic 色调映射曲线（又称 Uncharted 2 Tone Mapping）。其核心思路是模拟胶片的感光特性，公式包含肩部（Shoulder）和脚部（Toe）两段弯曲区域：

$$f(x) = \frac{x(Ax + CB) + DE}{x(Ax + B) + DF} - \frac{E}{F}$$

其中 $A$ 控制肩部强度，$B$ 控制肩部角度，$C$ 控制脚部强度，$D$ 控制脚部角度，$E/F$ 控制线性缩放。Hable 给出的默认参数为 $A=0.15, B=0.50, C=0.10, D=0.20, E=0.02, F=0.30$，这套参数在实际游戏中产生了具有胶片质感的温暖色调，中间调对比度明显高于 Reinhard。

### ACES（Academy Color Encoding System）

ACES 是美国电影艺术与科学学院（AMPAS）于2014年正式发布的工业标准色彩管理系统，其色调映射曲线（RRT + ODT）被 Unreal Engine 4.15 版本起设为默认选项。ACES 的近似曲线由 Krzysztof Narkowicz 简化为：

$$f(x) = \frac{x(2.51x + 0.03)}{x(2.43x + 0.59) + 0.14}$$

与 Filmic 相比，ACES 的蓝色和紫色在高光处会向白色偏移（这是真实胶片的物理现象），中间调对比度更高，整体画面更鲜艳。其代价是在某些低饱和度场景中可能出现轻微的色相偏移，且计算量略高于 Reinhard。

### 曝光参数的作用

在应用色调映射曲线之前，渲染引擎通常会乘以一个曝光系数 $E$，即 $L_{mapped} = f(E \cdot L_{in})$。曝光值（EV，Exposure Value）每增加1，输入亮度翻倍，等效于摄影中的光圈或快门调整。自动曝光（Auto Exposure / Eye Adaptation）系统会根据当前画面的平均亮度动态调整 $E$，模拟人眼从明暗环境进入另一环境时的适应过程。

## 实际应用

在 Unity 的 Universal Render Pipeline（URP）中，Post Processing Volume 组件下的 Tonemapping 模块提供了 Neutral 和 ACES 两种预设。Neutral 模式接近 Reinhard 的无偏移版本，适合需要精确颜色还原的医疗可视化场景；ACES 模式则适合追求电影感的游戏项目。

在 Unreal Engine 5 中，ACES 色调映射曲线通过 `r.TonemapperGamma` 和 `r.TonemapperFilmContrast` 等控制台变量进行微调。美术团队可以在 ACES 基础上通过后续的颜色分级（Color Grading）的 LUT（查找表）进一步定制视觉风格，两者协同工作而非相互替代。

HDR 显示器普及后，色调映射的目标发生了变化：在支持 HDR10 或 Dolby Vision 的显示设备上，输出范围扩展到 1000 cd/m²甚至更高，此时需要改用专为 HDR 显示设计的映射曲线，而非传统的 LDR 色调映射算子。

## 常见误区

**误区一：色调映射等同于伽马校正（Gamma Correction）。** 这是两个完全不同的操作。伽马校正是将线性光照值转换为显示器的非线性编码空间（如 sRGB 的 $\gamma \approx 2.2$），目的是适配显示硬件的电压-亮度响应曲线；而色调映射是在线性空间内对亮度范围进行压缩。正确的渲染管线顺序是：HDR 线性渲染 → 色调映射 → 伽马校正输出，二者不能颠倒或合并省略。

**误区二：ACES 一定比 Reinhard 效果好。** ACES 曲线专为模拟胶片色彩响应设计，其特有的色相偏移在风格化游戏或卡通渲染中可能破坏美术的色彩设计意图。例如纯蓝天空在 ACES 高曝光下会向青色偏移，这在写实场景中是真实的物理现象，但在需要精确颜色控制的场景中则是干扰。选择色调映射算子应与美术风格目标一致，而非盲目追求"最先进"。

**误区三：色调映射可以在 LDR 渲染管线中应用。** 色调映射必须在 HDR 浮点缓冲区（通常为 fp16 或 fp32 格式）上操作，输入值必须包含大于1.0的高光信息。如果渲染管线从一开始就将颜色值 clamp 到 $[0, 1]$，则色调映射曲线的肩部区域将完全没有输入数据，应用任何算子都只是在已经过曝的数据上进行无意义的变换。

## 知识关联

色调映射在后处理特效管线中紧接运动模糊之后执行。运动模糊在 HDR 线性空间中对相邻帧的亮度进行加权混合，模糊计算完成后才能进入色调映射阶段——若顺序颠倒，LDR 空间的运动模糊会导致高光边缘产生不真实的暗色条带（称为"黑边伪影"），这是实现时需要严格注意的顺序依赖。

色调映射完成后，画面进入**颜色分级**（Color Grading）阶段。颜色分级使用 LUT 对已映射到 $[0, 1]$ 范围的图像进行风格化色彩调整，如增强橙青对比、添加胶片颗粒色偏等。颜色分级依赖色调映射提供稳定的 $[0, 1]$ 输入范围——若跳过色调映射直接进行颜色分级，高光区域的溢出值会导致 LUT 采样越界，产生颜色错误。