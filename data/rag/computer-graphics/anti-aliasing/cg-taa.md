---
id: "cg-taa"
concept: "TAA"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "research"
    title: "High-Quality Temporal Supersampling"
    authors: ["Brian Karis"]
    venue: "SIGGRAPH 2014 (Epic Games)"
    year: 2014
  - type: "research"
    title: "Temporal Reprojection Anti-Aliasing in INSIDE"
    authors: ["Mikkel Gjoel"]
    venue: "GDC 2016"
    year: 2016
  - type: "textbook"
    title: "Real-Time Rendering"
    authors: ["Tomas Akenine-Moller", "Eric Haines", "Naty Hoffman"]
    year: 2018
    isbn: "978-1138627000"
scorer_version: "scorer-v2.0"
---
# TAA（Temporal Anti-Aliasing）

## 概述

时间抗锯齿（Temporal Anti-Aliasing, TAA）是一种利用多帧历史信息来消除画面锯齿和闪烁的后处理技术。Brian Karis 在 SIGGRAPH 2014 的 UE4 演讲中将其定义为"一种以时间换空间的超采样——不在一帧内采样多次，而是在多帧之间积累采样"。

TAA 已成为现代游戏引擎的 **事实标准抗锯齿方案**：UE5 默认启用 TAA（通过 TSR 扩展）、Unity HDRP 默认使用 TAA、所有 2020+ 的 AAA 引擎都以 TAA 为基础。原因很简单：TAA 是唯一能以低成本同时处理 **几何锯齿** 和 **着色器锯齿**（高光闪烁、阴影锯齿）的方案。

## TAA 的核心原理

### 亚像素抖动（Sub-Pixel Jitter）

每帧对投影矩阵施加微小偏移（通常 ±0.5 像素内），使同一像素在不同帧采样到不同的亚像素位置：

```
帧 0: 像素中心 (0.5, 0.5)
帧 1: 偏移至    (0.25, 0.75)  ← Halton(2,3) 序列
帧 2: 偏移至    (0.75, 0.25)
帧 3: 偏移至    (0.125, 0.625)
...

8帧后 → 该像素累积了8个不同位置的采样
       → 效果近似 8× 超采样（SSAA 8×的 GPU 成本的 ~1/8）
```

抖动序列通常使用 **Halton 序列**（基 2,3）或 **R2 序列**——比随机/均匀网格更均匀地覆盖采样空间。

### 时间重投影（Temporal Reprojection）

用上一帧的 Motion Vector 将历史像素映射到当前帧的对应位置：

```
current_uv = fragment_uv
motion = sample(MotionVectorBuffer, current_uv)
history_uv = current_uv - motion
history_color = sample(HistoryBuffer, history_uv)
```

Motion Vector 来源：
- **相机运动**：从 MVP 矩阵差异计算（所有静态物体共享）
- **物体运动**：顶点着色器中计算当前/前一帧位置差（动态物体）

### 混合（Blending）

将当前帧与历史帧加权混合：

```
output = lerp(history_color, current_color, alpha)
// alpha 通常 = 0.05-0.1（95% 历史 + 5% 当前）
// → 相当于以指数衰减累积约 10-20 帧
```

alpha 越小 → 累积帧越多 → 抗锯齿越好但 ghosting 越严重。

## TAA 的三大伪影及解决方案

| 伪影 | 原因 | 解决方案 |
|------|------|---------|
| **鬼影（Ghosting）** | 历史帧信息在新位置不再有效（遮挡/光照变化） | Neighborhood Clamp：将历史颜色限制在当前帧 3×3 邻域的 min-max 范围内 |
| **模糊（Blurring）** | 运动物体的历史采样位置不准确 | 锐化后处理 + 减小动态物体的混合权重 |
| **闪烁（Flickering）** | 亚像素几何体（栅栏、头发）在抖动中忽隐忽现 | Variance Clipping（基于方差的软裁剪）替代硬 clamp |

Karis（2014）的改进——**Variance Clipping**：不使用 min/max 硬裁剪历史颜色，而是计算 3×3 邻域的均值和标准差，用 μ ± γσ 构建 AABB 进行软裁剪。γ=1.0-1.25 在实践中效果最佳。

## TAA 与其他抗锯齿的对比

| 方法 | 类型 | GPU 成本 | 几何AA | 着色器AA | 运动处理 |
|------|------|---------|--------|---------|---------|
| MSAA | 硬件 | 高（×2-8 带宽） | ✅ | ❌ | N/A |
| FXAA | 后处理 | 极低（0.5ms） | ⚠️模糊 | ❌ | N/A |
| SMAA | 后处理 | 低（1ms） | ✅ | ❌ | N/A |
| **TAA** | **时间** | **低（1-2ms）** | **✅** | **✅** | **需Motion Vector** |
| DLSS/FSR | AI/时间 | 可节省（渲染低分辨率） | ✅ | ✅ | 需Motion Vector |

**关键优势**：TAA 是唯一能有效处理 **着色器锯齿**（Specular aliasing, Shadow map aliasing）的实时方案——MSAA 对这些完全无效。

## TAA 的现代演进

### TSR（UE5 Temporal Super Resolution）

UE5 在 TAA 基础上增加了超分辨率功能——渲染内部分辨率为目标的 50-75%，用 TAA 累积信息重建全分辨率：
- 性能提升 30-50%
- 质量接近原生分辨率 TAA
- 内部使用 Catmull-Rom 插值和改进的 Neighborhood Clamp

### DLSS / FSR / XeSS

AI 驱动的时间超采样——本质上是"TAA + 深度学习上采样"：
- **DLSS 3.5**：NVIDIA RTX 专用，质量最佳
- **FSR 3**：AMD 开源，支持所有 GPU
- **XeSS**：Intel 方案，支持 DP4a 指令集

## 实现速查（UE5 / HLSL 伪代码）

```hlsl
// 简化的 TAA Resolve Pass
float2 motion = MotionVectorTexture.Sample(uv);
float2 history_uv = uv - motion;
float3 history = HistoryTexture.Sample(history_uv);
float3 current = CurrentFrameTexture.Sample(uv);

// Neighborhood Clamp (Variance Clipping)
float3 m1 = 0, m2 = 0;
for (int y = -1; y <= 1; y++)
    for (int x = -1; x <= 1; x++) {
        float3 c = CurrentFrameTexture.Sample(uv + float2(x,y) * texelSize);
        m1 += c; m2 += c * c;
    }
m1 /= 9; m2 /= 9;
float3 sigma = sqrt(abs(m2 - m1 * m1));
float3 cmin = m1 - 1.25 * sigma;
float3 cmax = m1 + 1.25 * sigma;
history = clamp(history, cmin, cmax);

float alpha = 0.05; // 累积约20帧
float3 output = lerp(history, current, alpha);
```

## 常见误区

1. **TAA 只是抗锯齿**：TAA 实际上是一个时间积分框架——除了 AA，还被用于降噪（RTGI 降噪）、超分辨率（TSR/DLSS）、景深/运动模糊的质量提升
2. **提高 alpha 可以减少 ghosting**：alpha 增大 → 历史权重降低 → ghosting 减少，但同时抗锯齿能力下降且闪烁增加。正确做法是改进 clamp/rejection 算法
3. **TAA 不需要 Motion Vector**：没有精确 Motion Vector 的 TAA 在任何运动场景下都会产生严重鬼影。确保所有动态物体输出 per-object motion vector

## 知识衔接

### 先修知识
- **光栅化基础** — 理解像素采样和锯齿产生的原因
- **帧缓冲** — 理解 render target 和后处理管线

### 后续学习
- **DLSS/FSR** — AI 驱动的时间超采样技术
- **运动模糊** — 共享 Motion Vector 管线的后处理效果
- **时间降噪** — TAA 框架在光线追踪降噪中的应用
- **屏幕空间反射** — TAA 累积提升 SSR 质量

## 参考文献

1. Karis, B. (2014). "High-Quality Temporal Supersampling." SIGGRAPH 2014, Epic Games.
2. Gjoel, M. (2016). "Temporal Reprojection Anti-Aliasing in INSIDE." GDC 2016.
3. Akenine-Moller, T. et al. (2018). *Real-Time Rendering* (4th ed.). CRC Press. ISBN 978-1138627000
4. Salvi, M. (2016). "An Excursion in Temporal Supersampling." GDC 2016, Intel.
5. Yang, L. et al. (2020). "A Survey of Temporal Antialiasing Techniques." *Computer Graphics Forum*, 39(2).
