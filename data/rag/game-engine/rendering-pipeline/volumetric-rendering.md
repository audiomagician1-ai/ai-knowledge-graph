---
id: "volumetric-rendering"
concept: "体积渲染"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["特效"]

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
updated_at: 2026-03-31
---

# 体积渲染

## 概述

体积渲染（Volumetric Rendering）是一种将三维空间中的半透明介质（如雾、烟、云、光柱）可视化的渲染技术。与传统表面渲染只处理几何体表面的像素着色不同，体积渲染需要对光线穿越整个三维体积介质时的散射、吸收和发射过程进行模拟。典型的应用场景包括体积雾（Volumetric Fog）、丁达尔效应产生的体积光（God Rays / Volumetric Light）以及游戏中大面积的云层渲染。

该技术的物理基础来自于辐射传输方程（Radiative Transfer Equation，RTE），最早在医学成像领域（CT扫描重建）被大量使用，随后在1980年代由James Blinn等研究者引入计算机图形学用于模拟烟雾和星云。进入实时渲染领域则要等到GPU可编程着色器普及之后，现代游戏引擎（如Unreal Engine 4.x起、Unity HDRP）均内置了基于物理的体积渲染系统。

在游戏引擎渲染管线中，体积渲染通常作为后处理或延迟管线的扩展阶段执行。它之所以重要，是因为大气散射产生的可见光柱和雾感是玩家感知空间深度与光照氛围的关键视觉线索，缺少体积效果的场景往往显得"干净但不真实"。

---

## 核心原理

### 辐射传输方程与参与介质

体积渲染的数学核心是简化版的辐射传输方程，沿光线方向 $s$ 积分：

$$L(x, \omega) = \int_0^d T(x, x_s) \cdot \sigma_s(x_s) \cdot L_{scat}(x_s, \omega) \, ds + T(x, x_d) \cdot L_{bg}$$

其中：
- $\sigma_s$ 是**散射系数**（Scattering Coefficient），控制介质散射光的强度
- $\sigma_a$ 是**吸收系数**（Absorption Coefficient），光被介质吸收转化为热能
- $T(a,b)$ 是**透射率**（Transmittance），即 $e^{-\int_a^b \sigma_t \, ds}$，$\sigma_t = \sigma_s + \sigma_a$
- $L_{bg}$ 是背景（场景几何体）贡献的亮度

实时渲染中无法对连续介质精确积分，因此引擎将视锥空间划分为**3D体素纹理（Froxel，Frustum Voxel）**，每个 Froxel 存储散射系数、消光系数和相位函数参数。Unreal Engine 默认将视锥划分为 $144 \times 80 \times 64$ 个 Froxel，以此近似连续体积。

### 相位函数与光散射方向

参与介质中光的散射方向分布由**相位函数**描述。游戏引擎最常用的是 **Henyey-Greenstein 相位函数**（1941年提出）：

$$p_{HG}(\cos\theta) = \frac{1 - g^2}{4\pi (1 + g^2 - 2g\cos\theta)^{3/2}}$$

其中 $g \in [-1, 1]$ 是各向异性参数：$g=0$ 为均匀散射（雾），$g>0$ 为前向散射（云层内部），$g<0$ 为后向散射。云通常使用双瓣 Henyey-Greenstein（将前向与后向散射叠加）来模拟银边效果（Cloud Corona）。

### 光线步进（Ray Marching）

实时体积渲染的核心执行算法是**光线步进**：从摄像机对每个像素发射一条光线，沿光线方向以固定步长 $\Delta s$（通常为8至64步）采样体积密度，逐步累积散射光和透射率：

```
T = 1.0;  L = 0.0;
for each sample i:
    density = sampleVolume(pos_i);
    sigma_t = density * extinction;
    T *= exp(-sigma_t * stepSize);
    L += T * density * scatteredLight(pos_i) * stepSize;
```

步数越多，精度越高，但计算开销线性增长。Unreal Engine 5 的 Lumen 系统对体积介质采用了时间性复用（Temporal Accumulation），在多帧间复用 Froxel 计算结果，使得每帧实际计算量约等效于 8 步 Ray March 的开销。

---

## 实际应用

**体积雾**：在 Unity HDRP 中，Local Volumetric Fog 组件允许设计师在场景中放置任意形状的雾体，使用3D噪声纹理（如Worley噪声）控制密度分布。雾的边缘淡出距离（Blend Distance）参数避免了硬边切割感。

**体积光/丁达尔光柱**：当定向光（Directional Light）照射含有参与介质的空间时，光线绕过障碍物产生阴影投射进体积，形成可见光柱。Unreal Engine 通过在 Shadow Map 采样阶段将阴影信息注入到 Froxel 的散射计算中实现这一效果，需开启 **Volumetric Scattering Intensity** 参数（默认值 1.0 对应物理真实比例）。

**程序化云渲染**：Horizon: Zero Dawn（2017）的云系统将低频 Perlin 噪声与高频 Worley 噪声相组合（FBM叠加），利用球形 Ray March 从大气层底部向上步进采样云密度，再用双散射近似（Dual Scattering Approximation）计算云内多次散射，最终在 1/4 分辨率下渲染再上采样，帧耗时约控制在 2ms 以内。

---

## 常见误区

**误区一：体积雾与深度雾（Depth Fog / Exponential Fog）等价**。传统指数雾仅根据摄像机距离计算透明度，是一个纯数学近似，不模拟光散射，因此不会产生光柱或雾中阴影。体积渲染的雾是对真实参与介质的物理模拟，计算成本高出数十倍，两者不可互换使用。

**误区二：步长越小结果一定越准确**。光线步进中如果步长过小导致采样点超出深度缓冲精度范围，反而会引入数值积分误差（尤其在 Half-Precision 浮点下）。实践中应配合 **Jitter（抖动采样）+ 时间性抗锯齿（TAA）** 使用稀疏步长，这是 Dice 工程师在《战地1》开发时总结并公开的权衡方案。

**误区三：体积渲染仅在后处理阶段执行**。部分教程将体积光实现为屏幕空间后处理（如 Screen Space God Rays，本质是径向模糊），但真正的体积渲染发生在 3D 空间中，能正确处理遮挡关系和多光源散射，而屏幕空间方法在边缘遮挡时会产生光晕穿墙等错误。

---

## 知识关联

体积渲染依赖**渲染管线概述**中的延迟渲染（Deferred Rendering）或前向渲染框架来获取深度缓冲和 Shadow Map，这两项数据是 Froxel 注入阴影信息的前提。体积渲染生成的半透明散射结果需要与主渲染目标进行 Alpha 合成，遵循渲染管线中透明物体处理的 Porter-Duff over 合成公式。

在进一步学习方向上，体积渲染的采样策略与**光线追踪**（Path Tracing）中的体积路径追踪（Volumetric Path Tracing）直接相关；云和大气散射的精确模拟则延伸至**大气散射模型**（如 Bruneton 2008 的预计算大气散射），理解体积渲染的相位函数和透射率计算将为这些进阶方向提供直接的数学铺垫。