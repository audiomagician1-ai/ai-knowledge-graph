---
id: "cg-ddgi"
concept: "DDGI"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 4
is_milestone: false
tags: ["前沿"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
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

# DDGI：动态漫反射全局光照

## 概述

DDGI（Dynamic Diffuse Global Illumination）是由NVIDIA于2019年在论文《Dynamic Diffuse Global Illumination with Ray Trtraced Irradiance Fields》中提出的实时全局光照技术，其核心机制是通过**动态更新的探针网格**（Probe Grid）持续追踪场景辐照度变化，从而以低开销实现多次漫反射弹跳的间接光照效果。与传统烘焙光照图不同，DDGI中的每个探针每帧都可以发射新的光线（每个探针默认发射64至512条射线），依据最新场景状态累积更新辐照度数据，因此能响应动态光源、移动物体和昼夜循环等实时变化。

该技术的历史背景源于光线追踪硬件的普及——RTX 20系显卡于2018年引入DXR（DirectX Raytracing）API，使每帧发射数百万条探针射线变得可行。DDGI正是利用这一能力，将辐照度存储在三维均匀分布或分层分布的探针阵列中，每个探针以八面体映射（Octahedral Mapping）将球面辐照度压缩到一张小型2D纹理（通常为8×8或16×16像素），整个探针网格被打包进一张图集纹理以便GPU高效采样。

DDGI之所以重要，在于它填补了实时渲染中"动态场景+多次漫反射弹跳"这一长期空白。屏幕空间环境光遮蔽（SSAO）只能近似一次弹跳且受视锥限制，而DDGI理论上支持无限次弹跳——将上一帧的探针辐照度作为当前帧射线的入射光，形成递归的光照传播链，代价仅是多轮探针更新。

---

## 核心原理

### 探针布局与辐照度存储

DDGI将探针以均匀网格（Uniform Grid）部署于世界空间，典型间距为0.5米至2米，具体取决于场景规模。每个探针存储两张八面体纹理：一张记录**辐照度**（Irradiance，RGB颜色，代表到达该点的漫反射光通量），另一张记录**平均遮挡距离及其平方**（Mean Distance / Mean Distance²），后者用于实现切比雪夫可见性测试（Chebyshev Visibility Test）以抑制漏光（Light Leaking）。两张纹理合并后每个探针占用的显存约为数百字节，完整网格通常在数MB量级。

### 探针射线投射与时域累积

每帧，每个探针沿伪随机旋转的方向（使用Fibonacci球面采样加帧间旋转偏移）发射固定数量的射线，命中点的辐亮度与法线信息被写回探针纹理。关键更新公式为：

$$E_{n+1} = \text{lerp}(E_n,\ E_{\text{new}},\ \alpha)$$

其中 $E_n$ 为当前帧辐照度，$E_{\text{new}}$ 为本帧新射线采样结果，$\alpha$ 为混合权重（论文推荐值为 $\alpha \approx 0.03$，对应约33帧的指数移动平均时间常数）。这种时域超采样（Temporal Accumulation）意味着一个探针不需要在单帧内覆盖全部方向，而是以极低的每帧射线数（低至64条）随时间积分出完整的球面辐照度。

### 探针自适应偏移（Probe Relocation）

静止在墙体内部的探针会采样错误的几何背面辐照度，导致严重漏光。DDGI引入**探针重定位**机制：在初始化或场景变化时，利用遮挡距离纹理检测探针是否位于几何体内部，若是则沿梯度方向将其偏移至最近的可见空域，偏移量限制在网格单元尺寸的50%以内以防破坏网格插值一致性。此外，对于长时间处于完全遮挡状态的探针，可将其标记为**停用（Disabled）**，跳过射线投射以节省开销。

### 着色时的探针插值

渲染几何体时，对于表面着色点，系统在周围8个相邻探针之间进行三线性插值（Trilinear Interpolation），并以基于法线方向的余弦权重过滤背向探针，同时用切比雪夫可见性权重抑制被遮挡探针的贡献，最终输出用于漫反射着色的辐照度值 $E(\mathbf{n})$，其中 $\mathbf{n}$ 为表面法线方向。整个着色查询只需若干次纹理采样，无需实时光线追踪。

---

## 实际应用

**《赛博朋克2077》与RTXGI**：NVIDIA将DDGI开源为RTXGI SDK（Real-Time Global Illumination），CD Projekt RED在《赛博朋克2077》的Path Tracing模式前的早期光追版本中集成了基于DDGI原理的间接光照系统，用于处理室内霓虹灯的多次反弹色溢（Color Bleeding）效果，探针网格在建筑内部使用约0.5米间距的密集层次。

**Lumen的前驱对比**：虚幻引擎5的Lumen系统部分借鉴了DDGI的辐照度探针思路，但Lumen在屏幕空间中额外叠加了表面缓存（Surface Cache），而纯DDGI方案则完全依赖世界空间探针，这使得DDGI在缺少屏幕信息的反射场景或VR应用中更具可预测性。

**VR中的应用**：因为VR双眼渲染不存在稳定的单一屏幕空间，DDGI探针的世界空间特性恰好规避了SSR、SSAO等技术的固有缺陷。Meta在其PC VR内容开发中已将RTXGI作为推荐间接光照方案之一，探针以0.8米至1.5米间距覆盖主要活动区域。

---

## 常见误区

**误区一：探针数量越多效果越好**
探针间距过小会导致插值权重退化——当着色点与探针距离趋近于零时，可见性权重的计算精度下降，反而引入噪声。同时每帧射线总数随探针数量线性增长，探针从10³增至10⁴会将射线投射开销提升10倍。正确做法是根据场景几何复杂度分层部署，室外大空间使用2～4米间距，室内使用0.5～1米间距。

**误区二：DDGI能处理镜面反射**
DDGI存储的是**球面辐照度**（对入射辐亮度按余弦加权积分的结果），这一信息已丢失高频方向细节，因此天然只适用于**漫反射（Lambertian）着色**。用DDGI结果驱动镜面高光会产生模糊、失真的反射。镜面间接光照需要另外的技术，例如屏幕空间反射（SSR）或反射捕捉（Reflection Capture）。

**误区三：$\alpha=0.03$是通用最优值**
混合权重 $\alpha$ 控制探针对场景变化的响应速度与噪声的权衡。光照变化剧烈的场景（如闪光弹、昼夜切换）需要较大的 $\alpha$（0.1甚至0.3）以快速收敛，而静态或缓变场景使用0.03可以充分积累历史样本降低噪声。引擎实现中通常将 $\alpha$ 设计为动态值，当检测到探针辐照度突变超过阈值时临时提升混合速率。

---

## 知识关联

**前置概念——光探针（Light Probe）**：DDGI本质上是对传统静态光探针的动态化扩展。传统光探针通过预计算将场景某点的球面辐照度烘焙为球谐函数（Spherical Harmonics，通常取L2阶即9个系数），而DDGI保留了探针的空间布局思路，但用逐帧射线更新取代了离线烘焙，并以八面体纹理而非球谐系数存储辐照度，从而保留更高的方向分辨率（避免球谐的低频截断误差）。理解光探针的球面采样和插值权重是正确使用DDGI的前提。

**扩展方向——探针层次结构与自适应密度**：均匀网格在空旷区域浪费探针，研究方向包括基于场景几何密度的自适应探针放置（Adaptive Probe Placement）以及多分辨率层次网格（Cascaded Probe Grid），后者类似级联阴影贴图，在摄像机近处使用密集小网格、远处使用稀疏大网格，是将DDGI扩展到开放世界场景的关键技术路径。