---
id: "cg-ray-marching"
concept: "Ray Marching"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 光线步进（Ray Marching）

## 概述

光线步进是一种通过沿光线方向以固定或自适应步长离散采样来渲染体积介质的算法。与解析求交不同，Ray Marching 不要求场景几何具有闭合解析形式，因此能够处理云、烟、火焰、大气散射等无法用多边形网格精确描述的现象。

该算法的思想最早可追溯到1984年 James Kajiya 和 Brian Von Herzen 在 SIGGRAPH 发表的论文《Ray Tracing Volume Densities》，文中首次系统地将光线追踪框架扩展到连续密度场。此后 Ken Perlin 在1989年将其与噪声函数结合，使体积云的实时渲染成为可能。

Ray Marching 之所以重要，在于它将三维体积积分问题转化为一维数值积分问题：沿每条观察光线逐步累积透射率和辐射亮度，最终合成像素颜色。这一转化使得在 GPU 着色器中并行执行成为标准做法——现代游戏引擎（如虚幻引擎的体积雾系统）和离线渲染器均采用这一框架。

---

## 核心原理

### 基本迭代流程

Ray Marching 的主循环非常直接：从相机出发，沿视线方向 $\mathbf{d}$（单位向量）以步长 $\Delta t$ 逐步前进，在每个采样点 $\mathbf{x}_i = \mathbf{o} + t_i \cdot \mathbf{d}$ 处查询密度场 $\sigma(\mathbf{x})$，并按以下递推式累积结果：

$$t_{i+1} = t_i + \Delta t$$

$$T_i = \exp\!\left(-\sum_{j=0}^{i-1} \sigma(\mathbf{x}_j)\,\Delta t\right)$$

$$C_{\text{out}} = \sum_{i} T_i \cdot \mathbf{L}(\mathbf{x}_i) \cdot \sigma(\mathbf{x}_i) \cdot \Delta t$$

其中 $T_i$ 为当前点的透射率（Transmittance），$\mathbf{L}(\mathbf{x}_i)$ 为该点的辐射亮度（来自光源或散射），$\sigma$ 为消光系数。循环在 $T_i < \varepsilon$（常取 $10^{-3}$）或光线离开体积包围盒时终止。

### 固定步长与自适应步长

**固定步长**实现最为简单，适合均匀密度场。步长 $\Delta t$ 通常设置为体积包围盒尺寸除以采样数（典型值为 64～256 步）。步长过大会产生"阶梯状"伪影（Banding Artifact），步长过小则显著增加计算量。

**自适应步长**（也称 Sphere Tracing 或 Distance-Aided Marching）利用有符号距离场（SDF）来动态调整步长：在空旷区域使用当前点到最近表面的距离作为步长，仅在接近边界时缩小步长。这一技术由 John C. Hart 在1996年正式提出，可将平均步进次数从数百次减少到20～40次，同时保持亚像素精度。

### 抖动采样（Jittered Sampling）

固定步长会使所有像素的采样位置呈规律性分布，放大时产生同相位的周期性噪声。标准做法是在第一步 $t_0$ 处加入均匀随机偏移 $\xi \in [0, \Delta t)$：

$$t_0 = t_{\min} + \xi$$

这将系统性误差转化为白噪声，之后可以用时间累积（TAA，Temporal Anti-Aliasing）或空间滤波消除。虚幻引擎的体积雾渲染默认启用此技术，仅用 8 步即可取得接近 64 步的视觉质量。

---

## 实际应用

### GPU 着色器实现

在 GLSL/HLSL 中，Ray Marching 通常作为全屏后处理 Pass 实现：顶点着色器输出四边形覆盖屏幕，片段着色器对每个像素重建世界空间光线方向，随后执行步进循环，查询三维纹理（3D Texture）或程序噪声（如 FBM Perlin Noise）作为密度场，最终将累积颜色与不透明度混合写入帧缓冲。在 RTX 3080 上，以 1920×1080 分辨率执行 64 步查询约耗时 2～3 毫秒，在实时游戏预算内可行。

### 体积云渲染

Guerrilla Games 在《地平线：零之黎明》（2017）中公开了其体积云方案：使用两层 3D 噪声纹理（低频 Perlin-Worley 定形 + 高频 Worley 侵蚀细节），结合 Ray Marching 在 $1/4$ 分辨率下渲染云层，步数约为 128，再通过重投影将结果升采样到全分辨率，整体帧消耗控制在 1.5 毫秒以内。

---

## 常见误区

**误区一：步长越小精度一定越高。** 对于程序噪声生成的密度场，极小步长会在高频噪声处过采样，同时放大浮点精度误差。实践中存在一个有效步长下限（通常为体素大小的 1/2 至 1 倍），低于此值时误差不再减小，计算量却线性增加。

**误区二：Ray Marching 只能渲染"软"体积，无法处理硬表面。** 实际上，当密度场为 SDF 时，Ray Marching（即 Sphere Tracing）可以精确渲染隐式曲面，包括曼德尔堡集、齿轮、融合球等几何。Inigo Quilez 维护的 Shadertoy 上有数千个此类示例，完全基于 Ray Marching 而无任何多边形几何。

**误区三：透射率累积需要保存所有历史采样点。** 逐步递推公式 $T_{i+1} = T_i \cdot \exp(-\sigma_i \Delta t)$ 是单值递推，只需维护一个标量 $T_{\text{current}}$，无需存储沿线所有密度值，内存复杂度为 $O(1)$。

---

## 知识关联

Ray Marching 依赖**体积渲染概述**中建立的辐射传输方程（RTE）作为物理基础，步进循环本质上是对 RTE 积分的黎曼和近似。

掌握 Ray Marching 后，可直接进入以下专题：**Beer-Lambert 定律**给出了透射率指数衰减的解析推导，使 $T_i$ 的计算有了精确的物理诠释；**体积云实现**和**体积雾**在 Ray Marching 框架上叠加噪声建模与相位函数（Henyey-Greenstein）；**体积光**（Volumetric Lighting / God Rays）利用 Ray Marching 对阴影光线再次步进以计算透射遮蔽；**火焰与爆炸**则引入发射项 $\mathbf{e}(\mathbf{x})$，将 Ray Marching 的累积公式扩展为包含自发光的完整形式。
