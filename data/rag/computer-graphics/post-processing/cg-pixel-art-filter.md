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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 像素化滤镜

## 概述

像素化滤镜（Pixelation Filter）是一种后处理效果，通过将高分辨率渲染图像的分辨率降低至目标"像素尺寸"，再可选地将颜色压缩到有限调色板，从而模拟出80年代至90年代早期游戏机（如NES、Game Boy、Mega Drive）的视觉风格。其核心操作可以概括为两步：**下采样（Downsampling）** 加 **调色板量化（Palette Quantization）**。

像素化滤镜的技术根源来自早期受硬件限制的电子游戏——NES的屏幕分辨率为256×240，颜色数限于54色；Game Boy仅有160×144分辨率与4级灰度。现代像素化滤镜刻意复现这些限制，在高分辨率设备上制造复古感。该效果从2010年代的"像素艺术复兴"浪潮中大量出现于独立游戏后处理管线，如《Celeste》《Shovel Knight》等项目的运行时风格化。

之所以需要后处理实现而非直接以低分辨率渲染，是因为后处理方式可以保留高精度的几何、光照计算，仅在最终输出阶段模拟低分辨率外观，从而避免了真正低分辨率渲染中抗锯齿失效、UI元素模糊等问题。

---

## 核心原理

### 1. 下采样（降分辨率）

下采样的关键参数是**像素块尺寸（Block Size）**，记为 $B$（单位：屏幕像素）。算法将全分辨率图像（宽 $W$、高 $H$）划分为 $\lceil W/B \rceil \times \lceil H/B \rceil$ 个矩形块，每块取左上角（或中心）像素的颜色，将整块填充为同一颜色。

在GLSL着色器中，典型实现如下：

```glsl
vec2 blockUV = floor(uv * resolution / blockSize) * blockSize / resolution;
vec4 color = texture(screenTexture, blockUV);
```

其中 `blockSize` 通常取4到32之间的整数，数值越大，"像素风格"越粗犷。取整操作（`floor`）保证每个块内所有片元采样同一纹素，避免双线性插值带来的模糊。

### 2. 调色板量化

调色板量化将每个像素颜色 $\mathbf{c} = (R, G, B)$ 映射到预定义调色板 $\mathcal{P} = \{p_1, p_2, \ldots, p_N\}$ 中欧氏距离最近的颜色：

$$\hat{c} = \arg\min_{p_i \in \mathcal{P}} \| \mathbf{c} - p_i \|_2$$

常见参考调色板包括：
- **Game Boy调色板**：4色（`#0f380f`、`#306230`、`#8bac0f`、`#9bbc0f`）
- **NES调色板**：54色（官方PPU颜色表）
- **PICO-8调色板**：16色，高饱和度

在GPU实现中，调色板通常编码为一张1D纹理，量化操作在片元着色器中查表完成，实时性能开销可以控制在0.1ms以内（在1080p分辨率下）。

### 3. 抖动（Dithering）

单纯的最近邻量化会产生大面积色块和色带（Banding）。加入**有序抖动（Ordered Dithering）**可以模拟更多中间色。经典Bayer矩阵（4×4，16级阈值）抖动公式为：

$$\mathbf{c}' = \mathbf{c} + \frac{1}{16}\left(M_{ij} - \frac{1}{2}\right) \times \Delta$$

其中 $M_{ij}$ 为Bayer矩阵第 $(i \bmod 4, j \bmod 4)$ 位置的值，$\Delta$ 为调色板相邻颜色间距。抖动后再做最近邻量化，可在4色调色板下模拟出视觉上约8～16级的渐变效果。Game Boy风格游戏中大量使用此技术处理阴影过渡。

---

## 实际应用

**游戏运行时风格化**：Unity的Universal Render Pipeline（URP）可通过自定义`ScriptableRendererFeature`在摄像机后处理阶段插入像素化Pass。典型配置：Block Size = 4，使用PICO-8 16色调色板，配合4×4 Bayer抖动，渲染分辨率保持1080p。

**过场动画效果**：在《星露谷物语》类游戏中，玩家进入特定区域时触发全屏像素化过渡动画，Block Size从1动态增长到16再缩回，历时约0.5秒，给人"传送进入像素世界"的感觉。该效果仅通过修改单个uniform变量`u_blockSize`驱动。

**截图/视频滤镜工具**：Aseprite、Photoshop等工具的"像素化"滤镜本质上也是同样的Block Size采样，但在静态图像上可以使用更慢的全局K-means颜色量化（而非预定义调色板）来最优化颜色精度。

---

## 常见误区

**误区一：直接缩小再放大等同于像素化滤镜**

将图像缩小到目标"像素分辨率"再用最近邻插值放回原尺寸，与后处理像素化滤镜结果看起来相似，但行为不同。后处理版本处理的是每帧的最终合成图像（含UI、粒子），而缩放操作若应用于3D渲染目标可能不包含已合成的UI层，导致HUD元素也被像素化，这通常不是预期效果。正确做法是对3D场景应用像素化，对UI层保持原分辨率，在独立Pass中叠加。

**误区二：Block Size越小效果越好**

Block Size = 1时像素化滤镜退化为原图，毫无效果。Block Size = 2时差异也很微弱（仅在高DPI屏幕上略有感知）。多数像素风格游戏选择Block Size在4到8之间，若目标是模拟真实Game Boy的160×144分辨率，在1080p屏幕上Block Size应约为 $1080 / 144 \approx 7.5$，取整为8。

**误区三：调色板量化与颜色深度降低等价**

将每通道8bit降至每通道2bit（即R2G2B2，64色）与使用精心设计的16色调色板效果截然不同。前者颜色分布均匀但感知质量低，后者通过人工选色优化了色调和饱和度的感知均匀性。NES的54色调色板中完全没有纯白（最亮白为`#FFFFFF`在官方定义中偏暖），这种人工设计是调色板量化区别于机械降位深的核心所在。

---

## 知识关联

**前置知识**：后处理概述中介绍的渲染管线末端Pass机制是像素化滤镜的执行载体——像素化滤镜作为一个后处理Pass读取`_CameraOpaqueTexture`或帧缓冲，写入最终输出缓冲。理解全屏Quad绘制和Blit操作是实现本效果的技术前提。

**横向关联**：像素化滤镜常与**色差滤镜（Chromatic Aberration）**和**扫描线滤镜（Scanline）**组合，共同构成完整的CRT/复古视觉风格包。调色板量化所用的最近邻颜色搜索算法，与色彩空间中的**向量量化（Vector Quantization）**研究密切相关，后者在图像压缩（如早期VQ压缩格式）中有广泛应用。