---
id: "cg-chromatic-aberration"
concept: "色散"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 2
is_milestone: false
tags: ["效果"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "A"
quality_score: 82.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "academic"
    author: "Hullin, M. B., Hanika, J., & Heidrich, W."
    year: 2012
    title: "Physically-Based Real-Time Lens Flare Rendering"
    venue: "Computer Graphics Forum (EGSR 2012), Vol. 31, No. 4"
  - type: "academic"
    author: "Karis, B."
    year: 2014
    title: "High Quality Temporal Supersampling"
    venue: "SIGGRAPH 2014 Course: Advances in Real-Time Rendering in Games"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---

# 色散

## 概述

色散（Chromatic Aberration，简称 CA）是指光学系统中不同波长的光因折射率不同而产生的分离现象。根据阿贝数（Abbe number）理论，折射率 $n$ 与波长 $\lambda$ 之间存在非线性依赖关系，导致同一镜片对红光（约 700 nm）、绿光（约 546 nm）、蓝光（约 436 nm）的焦距各不相同，成像平面上三个颜色通道因此产生轻微的空间偏移，在画面边缘出现彩色条纹或"幻影"效果。这种效果在物理世界中是镜头像差（Lens Aberration）的体现，在屏幕角落和高对比度边缘处尤为明显。

色散作为后处理效果在游戏和电影工业中的广泛应用始于 2010 年代初，随着基于物理的渲染（PBR）管线在 2012—2014 年间的快速普及而逐渐标准化。经典电影《疾速追杀》（John Wick，2014）和大量 AAA 游戏如《赛博朋克 2077》（CD Projekt Red，2020）、《最后的生还者 Part II》（Naughty Dog，2020）均使用了显著的色散效果，用来强调赛博朋克视觉风格、高速摄影感，或是摄像机受到冲击的瞬间感知。Hullin 等人（2012）在其关于镜头光学效果物理渲染的研究中，系统性地将色差与镜头光晕纳入统一的光学缺陷建模框架，为后续实时渲染中的色散实现提供了重要理论依据。

从技术角度看，色散属于屏幕空间（Screen Space）效果，不依赖场景几何信息，因此计算成本相对较低——在典型的 1080p 分辨率下，单次 Pass 的色散着色器 GPU 耗时通常不超过 0.3 ms（具体数值因平台和着色器实现而异）。色散在艺术上的价值远超"真实感"本身：适度的色散能让画面具有电影质感，而夸张的色散则可以用于传达眩晕、梦境、数字故障等叙事状态。掌握色散实现与参数控制，能让美术和技术美术人员在不重新渲染场景的前提下，用极少的性能预算获得强烈的视觉风格变化。

---

## 核心原理

### 三通道独立采样偏移

色散的最基础实现方式是对渲染结果纹理的 R、G、B 三个颜色通道分别以不同的 UV 偏移量进行采样：

```glsl
vec2 offset = uv - vec2(0.5); // 以屏幕中心为原点
float strength = length(offset); // 距中心越远，色散越强

vec2 rOffset = offset * (1.0 + aberrationStrength);
vec2 gOffset = offset;
vec2 bOffset = offset * (1.0 - aberrationStrength);

float r = texture(screenTex, rOffset + vec2(0.5)).r;
float g = texture(screenTex, gOffset + vec2(0.5)).g;
float b = texture(screenTex, bOffset + vec2(0.5)).b;
```

其中 `aberrationStrength` 通常取值范围为 0.001 到 0.02 之间。偏移量以中心为圆点向外辐射，模拟径向色散（Radial Chromatic Aberration），这与真实镜头中枕形/桶形畸变伴生的色差行为一致。红通道向外扩张，蓝通道向内收缩（或反之），绿通道保持不变，因为人眼对绿色中间频段最敏感，绿通道偏移会破坏亮度感知。

例如，当屏幕分辨率为 1920×1080，`aberrationStrength = 0.01` 时，屏幕右下角（UV 约为 (0.85, 0.85)）的红通道采样点相对绿通道偏移约为 $\Delta x = 0.35 \times 0.01 = 0.0035$，换算为像素约为 $0.0035 \times 1920 \approx 6.7$ 像素，这个偏移量在高对比度边缘上肉眼可见，却不至于让整体画面失焦，是较为理想的基准值。

### 非线性强度映射

真实镜头的色散并非线性分布——边缘区域比中心强度高出数倍。常用的非线性强度映射公式为：

$$\text{dynamicStrength} = S_{\text{base}} \cdot \left(2 \cdot \|UV - 0.5\|\right)^{\gamma}$$

其中 $S_{\text{base}}$ 为基础色散强度参数，$\gamma$ 通常取 2.2。代码实现如下：

```glsl
float edgeFactor = pow(length(uv - 0.5) * 2.0, 2.2);
float dynamicStrength = aberrationStrength * edgeFactor;
```

指数 $\gamma = 2.2$ 并非随意选取，它与 sRGB 的 Gamma 曲线一致，使得色散强度在感知上呈均匀过渡。屏幕角落（UV 距中心约 $\frac{\sqrt{2}}{2} \approx 0.707$ 个单位）的色散强度约为边缘中点的两倍，这符合实拍镜头的光学测量数据。部分实现会将 $\gamma$ 替换为 3.0 来获得更夸张的边角色散，常用于故障（Glitch）艺术风格。

> **思考问题：** 如果将公式中的 $\gamma$ 从 2.2 改为 1.0（线性映射），画面视觉上会发生什么变化？为什么线性映射在感知层面会让中央区域色散显得"过强"？

### 动态色散与事件驱动

静态色散强度会让玩家习惯而失去效果。更高级的做法是将 `aberrationStrength` 与游戏事件绑定，实现动态色散：

- **爆炸/冲击**：在碰撞帧将强度从 0.02 瞬间跳升至 0.08，随后在约 0.3 秒内通过指数衰减（每帧乘以衰减系数，例如 `strength *= 0.85`，60 Hz 下约 18 帧回归基准）回归基准值。
- **慢动作**：在子弹时间期间持续施加 0.012 的恒定色散，配合动态模糊共同营造"时间扭曲"感。
- **屏幕受伤/污染**：仅在画面特定区域（如屏幕四个角落用遮罩图限定）叠加额外 0.015 的色散，模拟镜头沾染血迹或雨水。

例如，《战争机器 5》（The Coalition，2019）的技术分享中提到，他们在角色受击时将色散强度动态推高至基准值的 4 倍，配合画面抖动（Camera Shake）实现了更具冲击力的受击反馈，而不增加任何额外的几何计算开销。

---

## 数学推导与公式汇总

为便于工程实现查阅，此处整理色散核心数学关系如下。

**径向偏移量公式：**

$$\Delta UV_c = \left(\alpha_c - 1\right) \cdot (UV - 0.5)$$

其中 $\alpha_c$ 为各通道缩放系数，通常设红通道 $\alpha_R = 1 + S$，绿通道 $\alpha_G = 1$，蓝通道 $\alpha_B = 1 - S$，$S$ 为色散强度参数。

**带非线性权重的完整采样公式：**

$$UV'_c = 0.5 + \alpha_c \cdot (UV - 0.5) \cdot \underbrace{\left(2\|UV - 0.5\|\right)^{\gamma}}_{\text{边缘权重}}$$

当 $\gamma = 0$ 时退化为全屏均匀色散；当 $\gamma = 2.2$ 时为感知线性的径向色散；当 $\gamma \geq 3$ 时为边缘极端增强的故障风格色散。

**事件驱动衰减模型（离散时间）：**

$$S_t = S_{\text{peak}} \cdot r^t + S_{\text{base}}$$

其中 $r$ 为每帧衰减率（典型值 0.82—0.90），$t$ 为距触发事件的帧数，$S_{\text{peak}}$ 为冲击峰值强度。

---

## 实际应用

### Unity URP 中的自定义色散 Pass

在 Unity URP（通用渲染管线，Unity 2019.3 版本后正式引入）的后处理框架下，色散通常以 `ScriptableRenderPass` 实现，在 `BlitWithMaterial` 步骤中将着色器应用到 `_CameraColorAttachmentA`。关键参数通过继承自 `VolumeComponent` 的自定义组件暴露给美术：`intensity`（基础强度，建议范围 0.0—0.02）、`radialExponent`（非线性指数，默认 2.2）和 `chromaAngle`（可旋转色散方向，实现斜向色差，范围 0—360°）。Unity 官方的 Post Processing Stack v2（PPSv2）在 2018 年后提供了内置的色散组件，但其实现仅支持固定径向方向，自定义方向需要手写 Shader。

### 故障艺术（Glitch Art）中的极端色散

《控制》（Control，Remedy Entertainment，2019）等游戏在角色超自然能力激活时将色散强度推高至 0.05，并同时将 R/G/B 三通道偏移角度设为非对称值（例如 R 通道向右上方偏移向量 (0.008, 0.004)，B 通道向左下方偏移 (-0.006, -0.003)），制造出明显的数字故障感。与普通径向色散不同，这种方向性色散不需要以屏幕中心为轴，可以自定义偏移向量，在视觉上更具冲击力，常与扫描线（Scanline）和噪声纹理叠加使用，共同构成完整的故障美学视觉语言。

### 2D 像素游戏中的色散模拟

在像素风格游戏中，色散需要特殊处理：由于目标分辨率极低（例如 320×180），亚像素级的 UV 偏移在直接采样后无法产生可见的颜色分离效果——以 `aberrationStrength = 0.005` 为例，在 320 像素宽度下偏移仅为 $0.005 \times 320 = 1.6$ 像素，双线性采样会将其平滑掉。解决方案是将场景先渲染到高分辨率缓冲区（目标分辨率的 2× 或 4×），在此分辨率下应用色散，再通过最近邻（Nearest Neighbor）降采样到目标像素分辨率，从而在保留像素风格硬边的同时获得可见的色差效果。

---

## 常见误区

### 误区一：色散强度越高越好

许多初学者为了"有电影感"将 `aberrationStrength` 设到 0.05 以上并全程保持，结果画面文字和 UI 元素变得难以辨读。实际上，人眼对文字边缘的色差极度敏感——根据视觉疲劳相关研究，超过 0.015 的全屏恒定色散在持续 20—30