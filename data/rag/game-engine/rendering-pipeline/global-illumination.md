---
id: "global-illumination"
concept: "全局光照"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 3
is_milestone: false
tags: ["光照"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 全局光照

## 概述

全局光照（Global Illumination，简称GI）是一类模拟光线在场景中多次弹射、最终抵达摄像机的渲染技术集合。与仅计算光源直接照射表面的局部光照模型不同，全局光照的核心在于捕捉**间接照明**——即光线从光源出发后经历一次或多次漫反射/镜面反射后照亮其他表面的现象。典型可见效果包括：封闭角落的漏光、彩色墙壁在相邻白色表面上投射的颜色溢出（Color Bleeding），以及天花板被间接光均匀照亮等。

全局光照的理论基础是1986年由James Kajiya提出的**渲染方程**（Rendering Equation）：

$$L_o(\mathbf{x}, \omega_o) = L_e(\mathbf{x}, \omega_o) + \int_\Omega f_r(\mathbf{x}, \omega_i, \omega_o)\, L_i(\mathbf{x}, \omega_i)\, (\omega_i \cdot \mathbf{n})\, d\omega_i$$

其中 $L_o$ 为出射辐射度，$L_e$ 为自发光，$f_r$ 为BRDF，$L_i$ 为入射辐射度，$\Omega$ 为法线方向的半球空间。该积分的求解正是全局光照算法彼此竞争的战场。

在游戏引擎渲染管线中，全局光照直接影响场景的"真实感"基线——没有间接光的场景中，阴影内部完全黑暗，这与现实世界中天空光和反弹光普遍存在的情况截然不同。正因如此，各大引擎（Unreal、Unity、Godot）都将GI系统视为画质分级的核心指标。

---

## 核心原理

### 1. 光照贴图（Lightmap Baking）

光照贴图是将场景中静态物体的间接照明预计算后存储为UV展开纹理的方法。离线计算阶段通常使用路径追踪（Path Tracing）对每个纹素（Texel）发射数百至数千条光线并求平均，得到高质量的辐照度值，再在运行时以几乎零额外开销采样该纹理。

Unreal Engine的Lightmass系统在烘焙时会在光照贴图中额外存储**定向辐照度**（Directional Irradiance），使用球谐函数（SH2，即二阶球谐，共9个系数）编码照明方向信息，以便动态物体通过插值获得近似匹配的间接光。光照贴图的分辨率通常在16×16到4096×4096之间，Texel密度（Texels per meter）是控制质量与内存开销的关键参数，常见设置为2–8 texels/m。

**最大缺陷**：光照贴图无法响应动态光源变化或可移动遮挡体，场景中一旦有物体移动就会出现与烘焙结果不符的"漏光"。

### 2. 动态漫反射全局光照（DDGI）

DDGI（Dynamic Diffuse Global Illumination）由NVIDIA于2019年随DirectX Raytracing（DXR）扩展提出，其核心思想是在场景内规则或稀疏布置**辐照度探针（Irradiance Probe）**网格，每帧用硬件光线追踪向每个探针发射少量光线（典型为每探针每帧64–256条），将结果以**球八面体（Octahedral）编码**存储为小尺寸2D纹理图集（通常8×8或16×16像素/探针），再由附近表面双线性插值采样探针颜色获得间接漫反射。

探针网格的典型密度为每1–3米一个探针，大型开放世界场景需要分层级（Cascades）管理探针密度。Unreal Engine 5中的Lumen虽采用了完全不同的Screen Space + Ray Tracing混合策略，但DDGI的探针思想已被Unity的HDRP Probe Volume（APV）系统直接采用，并在Unity 6中成为正式功能。

### 3. 辐照度缓存与屏幕空间GI

早于硬件光线追踪普及之前，**辐照度缓存（Irradiance Cache）**通过在视锥空间中稀疏采样点存储半球积分近似值并外推内插，减少了蒙特卡洛积分的样本数量。屏幕空间全局光照（SSGI）则完全依赖G-Buffer中已有的深度、法线、颜色信息，在屏幕UV坐标内做短程随机步进（Ray March）收集来自可见像素的反弹光，计算代价极低但存在屏幕边缘信息缺失的根本性局限。

SSGI的辐照度估算公式通常基于半球积分的蒙特卡洛近似：

$$\hat{L}_{indirect} = \frac{1}{N}\sum_{i=1}^{N} \frac{f_r \cdot L_{sample_i} \cdot \cos\theta_i}{p(\omega_i)}$$

其中 $p(\omega_i)$ 为重要性采样的概率密度函数，$N$ 为屏幕空间样本数（典型运行时值为8–16个）。

---

## 实际应用

**静态室内场景**：建筑可视化和关卡内固定场景最适合使用光照贴图。Unreal Engine的Content Examples关卡使用128–512分辨率的Lightmap，间接光弹射次数设置为5–10次，以确保多层楼之间的光线传播正确。

**开放世界动态天气**：《堡垒之夜》（Fortnite）从UE4迁移到UE5后启用了Lumen GI，其Sky Light与Lumen结合实现了动态日出/日落时全场景色温变化，所有树木、建筑实时响应间接光——这在光照贴图方案下完全不可能实现。

**主机/PC中端配置**：PlayStation 5上的多款游戏（如《Ratchet & Clank: Rift Apart》）采用DDGI探针 + 屏幕空间反射（SSR）的组合策略：DDGI负责漫反射间接光，SSR负责短程镜面反弹，两者叠加接近离线渲染质量，全帧GI预算控制在2–3ms以内。

---

## 常见误区

**误区1：全局光照等同于光线追踪**
光线追踪是求解全局光照渲染方程的一种方法，而非全局光照本身。光照贴图烘焙（离线路径追踪）、DDGI（稀疏探针+实时光线追踪）和SSGI（无光线追踪）都能实现不同质量等级的全局光照效果。混淆两者会导致错误地认为"不支持RTX的显卡就无法实现GI"。

**误区2：间接光只影响阴影区域**
间接光对亮面同样贡献显著。在晴天室外场景中，蓝色天空的漫反射辐照度（约12000 lux天顶方向）会给朝上的白色表面叠加蓝色色调。忽略间接光的画面通常呈现出人工照明的刺眼感，即便是被直接光照亮的表面也会缺乏"融入环境"的层次感。

**误区3：提高光照贴图分辨率就能解决GI质量问题**
光照贴图的视觉质量瓶颈往往不在于分辨率，而在于**光线弹射次数**和**UV接缝处理**。将Lightmass的Indirect Light Bounces从默认值3提高至10，对封闭走廊等高遮蔽场景的视觉改善远大于将光照贴图分辨率加倍，且内存开销不增加。

---

## 知识关联

全局光照依赖**延迟渲染**管线提供的G-Buffer（深度、法线、反照率、粗糙度），SSGI和DDGI的间接光合成步骤在延迟着色的Lighting Pass阶段执行，脱离了延迟管线的信息结构，这两种技术的着色器实现都需要重大改写。

在技术演进链上，DDGI和Lumen所使用的**辐照度探针**概念与传统的**反射捕捉球（Reflection Capture）**是对偶关系——后者存储镜面反射信息，前者存储漫反射辐照度；两者共同构成延迟渲染管线中的完整间接光贡献。

理解全局光照的探针机制和光线追踪加速结构（BVH）后，可以自然过渡到**引擎光线追踪**专题，后者涉及硬件加速的DXR/VK_KHR_ray_tracing扩展如何将GI的每探针光线数从64条扩展至实时路径追踪所需的每像素数百条的工程优化路径。
