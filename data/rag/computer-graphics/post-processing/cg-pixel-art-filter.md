---
id: "cg-pixel-art-filter"
concept: "像素化滤镜"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 2
is_milestone: false
tags: ["风格化"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 像素化滤镜

## 概述

像素化滤镜（Pixelate Filter）是一种后处理技术，通过**降低有效分辨率**并结合**调色板颜色量化**，将原本平滑的高清画面转换为粗粒度的像素艺术风格。其视觉结果是画面被划分为明显可见的色块方格，每个方格内颜色均一，形成复古游戏机的美学效果。

该效果最早的艺术参照来自1970至1980年代早期街机游戏与家用主机（如Atari 2600、FC/NES）受硬件限制产生的视觉风格。当时屏幕分辨率通常仅为256×240或更低，调色板也被限制在16至64色之间。现代图形管线中的像素化滤镜正是对这种历史限制的**主动模拟**，将它从工程约束转化为艺术选择。

在游戏与影视特效中，像素化滤镜经常用于表达"数字世界"、"复古场景"或"信号损坏"等叙事意图。由于其原理简单、GPU开销极低，即便在实时渲染的后处理链中也可以毫无压力地逐帧运行。

---

## 核心原理

### 1. 降分辨率：块采样（Block Sampling）

像素化滤镜的第一步是将屏幕划分为 N×N 的像素块（Pixel Block），其中 N 通常取4、8、16等2的幂次。对于每个块，算法取该块**左上角或中心点**的原始颜色作为整块的代表色，丢弃块内其余所有像素的信息。

在GLSL/HLSL着色器中，核心操作可表达为：

```glsl
vec2 blockSize = vec2(N) / resolution;
vec2 snappedUV = floor(uv / blockSize) * blockSize;
vec4 color = texture(screenTex, snappedUV);
```

这里 `floor(uv / blockSize) * blockSize` 将UV坐标"对齐"到最近的块边界，等价于将实际采样分辨率从原始的 W×H 降至 (W/N)×(H/N)。N=8时，一张1920×1080的画面等效降至240×135的分辨率。

### 2. 调色板量化（Palette Quantization）

仅做降分辨率往往不够"像素风"——真实的老式游戏受制于硬件只能使用有限颜色。调色板量化将块代表色映射到一组预设的离散颜色集合中，通常包含8、16或32种颜色。

映射方法最常见的是**最近邻颜色匹配（Nearest Palette Color）**：计算当前颜色与调色板中每个颜色的欧氏距离，选取距离最小者：

$$c_{out} = \underset{p_i \in \text{Palette}}{\arg\min} \sqrt{(R - R_i)^2 + (G - G_i)^2 + (B - B_i)^2}$$

当调色板仅有16色时，整幅画面所有像素只会呈现这16种颜色之一，色带与硬边界的感觉由此产生。许多实现将量化步独立设计为参数可选，允许美术单独开关降分辨率与颜色限制这两个子效果。

### 3. 抖动（Dithering，可选增强）

为了用有限颜色表达更多色阶感，可在量化前施加**有序抖动（Ordered Dithering）**，最经典的是使用4×4 Bayer矩阵。Bayer矩阵中每个格子存储阈值（0~15的整数，归一化到0~1），在量化前将该阈值乘以抖动强度参数后叠加到颜色分量上，使相邻色块出现交错的颜色图案，视觉上模拟出中间色调。这是GameBoy等仅4色掌机画面的标志性视觉特征。

---

## 实际应用

**游戏UI与场景切换**：《Undertale》（2015）和《Celeste》（2018）均在特定过场动画中使用像素化滤镜强调复古情绪，其实现正是在后处理阶段对整个帧缓冲执行块采样。

**Unity后处理实现**：在Unity的URP（Universal Render Pipeline）中，像素化滤镜可通过自定义`ScriptableRendererFeature`注入，在`AfterRenderingTransparents`阶段执行一个全屏Blit Pass，将块大小N通过`_BlockSize`全局Shader属性传入，运行时可动态调节N值实现"像素化程度渐变"的过渡动画。

**马赛克遮挡**：视频编辑与监控系统中用于隐藏人脸或敏感区域的"马赛克"效果，其本质正是像素化滤镜在局部矩形ROI（Region of Interest）上的应用，块大小通常设为20×20至40×40像素以确保信息不可辨认。

**视觉故障艺术（Glitch Art）**：将像素化滤镜与扫描线滤镜、色差（Chromatic Aberration）组合，可合成完整的CRT/VHS复古屏幕效果，块大小设为3×3至5×5时配合RGB通道错位尤为自然。

---

## 常见误区

**误区一：块越大，"像素风"越好看**

块大小N并非越大越好。N=2至8时，效果接近真实复古游戏机；N超过32后，画面大面积变成单色方块，丧失可读性。同时，N的选择应与目标虚构设备的原始分辨率对应——模拟NES效果时选N=4（从1080p降至近似240p）最为准确，而不是随意填写一个大数字。

**误区二：只做降分辨率就够了**

仅执行块采样而跳过调色板量化，会保留原画面的全色域信息，每个色块颜色各异、平滑过渡，结果看起来是"模糊的低分辨率放大"而非像素艺术风格。真正的像素风必须让颜色同时被量化，两个子步骤缺一不可。

**误区三：像素化滤镜等同于缩小再放大**

许多初学者用"先将渲染目标缩小到低分辨率Render Texture，再以点采样（Point Sampling）放大回屏幕"来替代真正的像素化着色器。这两种方法视觉结果相近，但前者需要额外的Render Texture分配与两次Pass，后者（着色器方式）仅需单次全屏Pass，在移动平台上带宽节省明显；且着色器方式更易于在单帧内动态修改块大小，而无需重建Render Texture。

---

## 知识关联

**前置概念**：像素化滤镜依赖**后处理概述**中介绍的全屏Pass架构——必须理解帧缓冲（Framebuffer）Blit机制，才能知道在哪个阶段将块采样着色器注入到渲染管线中，以及如何读取完整的屏幕颜色纹理作为输入。

**横向关联**：像素化滤镜常与**扫描线滤镜**（模拟CRT行间隔）和**色差滤镜**（Chromatic Aberration，模拟镜头色散）组合使用，三者叠加构成完整的复古屏幕后处理栈；彼此之间均为独立的全屏Pass，执行顺序影响最终效果（通常像素化最先执行，确保后续滤镜作用于已量化的色块而非原始高清信号）。

**技术延伸**：若需要更精确的颜色量化，可研究**中位切割算法（Median Cut）**或**八叉树颜色量化（Octree Quantization）**，这两种算法可根据画面内容自适应生成最优调色板，而非使用静态预设颜色表，适合对画面保真度有更高要求的离线渲染场景。
