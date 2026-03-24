---
id: "cg-spherical-harmonics"
concept: "球谐函数"
domain: "computer-graphics"
subdomain: "global-illumination"
subdomain_name: "全局光照"
difficulty: 3
is_milestone: false
tags: ["数学"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 球谐函数

## 概述

球谐函数（Spherical Harmonics，简称SH）是定义在单位球面上的一组正交基函数，最早由物理学家威廉·汤姆森（Lord Kelvin）和彼得·塔特于19世纪在求解拉普拉斯方程时引入。在图形学中，球谐函数用于将球面上的低频光照信号（如环境光、漫反射辐照度）压缩编码为一组系数，实现高效的光照存储与重建。

球谐函数之所以在实时全局光照中受到青睐，原因在于漫反射BRDF本身是一个低通滤波器——它将入射光照平滑化，使得最终辐照度仅含低频成分。研究表明，用前3阶（共9个）SH系数即可捕获超过99%的漫反射光照能量，这使得原本需要整张立方体贴图才能表示的环境光，可以压缩为仅27个浮点数（每个RGB通道9个系数）。

Ravi Ramamoorthi和Pat Hanrahan于2001年在SIGGRAPH的经典论文《An Efficient Representation for Irradiance Environment Maps》中严格证明了这一结论，奠定了SH光照在实时渲染中的理论基础，此后成为游戏引擎中环境漫反射光照的标准方案。

---

## 核心原理

### 球谐基函数的数学定义

球谐函数 $Y_l^m(\theta, \phi)$ 由带阶数 $l$（band index，$l \geq 0$）和阶次 $m$（$-l \leq m \leq l$）共同确定，其实数形式为：

$$Y_l^m(\theta,\phi) = \begin{cases} \sqrt{2}\, K_l^{-m} \sin(-m\phi)\, P_l^{-m}(\cos\theta) & m < 0 \\ K_l^0\, P_l^0(\cos\theta) & m = 0 \\ \sqrt{2}\, K_l^m \cos(m\phi)\, P_l^m(\cos\theta) & m > 0 \end{cases}$$

其中 $P_l^m$ 是伴随勒让德多项式，$K_l^m$ 是归一化系数。第 $l$ 阶共有 $2l+1$ 个基函数，前 $n$ 阶合计 $n^2$ 个基函数：0阶1个、1阶3个、2阶5个，共9个，这正是实时渲染中最常用的截断阶数。

### 投影与重建

任意球面函数 $f(\omega)$ 可向SH基函数投影，求取系数：

$$c_l^m = \int_{S^2} f(\omega)\, Y_l^m(\omega)\, d\omega$$

重建时，用系数线性组合基函数还原近似信号：

$$\tilde{f}(\omega) = \sum_{l=0}^{n-1} \sum_{m=-l}^{l} c_l^m\, Y_l^m(\omega)$$

在漫反射光照场景中，$f(\omega)$ 即为环境光的辐亮度分布 $L(\omega)$。由于SH基函数正交，投影过程相互独立，各系数互不干扰，这使得SH光照支持线性混合——两套SH系数直接插值即可得到过渡光照，无需重新采样环境贴图。

### 漫反射卷积与Clamped Cosine核

漫反射辐照度是入射辐亮度与余弦加权函数的卷积：

$$E(\mathbf{n}) = \int_{S^2} L(\omega)\, \max(\omega \cdot \mathbf{n},\, 0)\, d\omega$$

在SH域中，卷积等价于逐系数乘以对应阶的滤波权重 $\hat{A}_l$。Clamped Cosine核的SH系数已有解析解：$\hat{A}_0 = \pi$，$\hat{A}_1 = 2\pi/3$，$\hat{A}_2 = \pi/4$，而 $l \geq 3$ 的高阶项迅速趋近于零，这从数学上解释了为何仅需前3阶SH便能精确表示漫反射辐照度。

---

## 实际应用

**游戏引擎中的环境漫反射**：Unity和Unreal Engine均将场景中Light Probe采集的环境光编码为L1（4个系数，仅0阶+1阶）或L2（9个系数）SH，存储在每个探针节点。运行时GPU只需执行一次点积运算即可对任意法线方向查询辐照度，开销远低于采样立方体贴图。

**SH光照贴图（SHMAP）**：将SH系数直接烘焙到纹理中，每个纹素存储27个浮点数，可随表面插值。《光环》系列等AAA游戏使用此技术表示次表面散射和动态角色在复杂场景中的受光，相比传统光照贴图可保留低频方向信息。

**球谐系数的实时更新**：对于动态天空（昼夜交替），可在CPU上每帧对新的天空辐亮度重新投影，更新9组SH系数，然后上传至GPU Uniform Buffer。这比每帧重新生成辐照度立方体贴图的代价低约两个数量级。

---

## 常见误区

**误区一：SH可以表示高光反射**。SH仅适合低频信号，无法表示尖锐高光。当粗糙度（Roughness）小于约0.4时，前3阶SH的重建误差已显著可见；高光应改用预过滤环境贴图（Prefiltered Environment Map）或Ambient Cube等方案。将SH用于镜面反射是一种典型的过度使用错误。

**误区二：阶数越高精度越好，应尽量提高阶数**。提升至4阶（16个系数）和5阶（25个系数）在漫反射场景中几乎没有可见收益，却增加了存储和传输开销。对于漫反射，截断在第3阶（9个系数）是经过理论与实测双重验证的最优权衡点，而非保守选择。

**误区三：SH系数可以直接用于次表面散射（SSS）的精确模拟**。SH仅描述球面上的方向分布，无法编码空间位置变化引起的光照差异。皮肤等SSS材质需要结合辐照度体积或屏幕空间方法，单独依赖SH系数会导致漏光和边缘过亮等伪影。

---

## 知识关联

球谐函数的应用直接建立在**辐照度贴图**的概念之上：辐照度贴图本质上是预卷积后的球面函数，而SH是对这一球面函数进行压缩表示的数学工具。理解辐照度贴图的构建过程（采集环境辐亮度、与余弦核卷积）有助于直观理解SH投影的物理意义，以及为何截断误差在漫反射场景中可以接受。

掌握SH光照之后，自然延伸至**辐照度体积（Irradiance Volume）**：辐照度体积在三维空间中规则排布大量Light Probe，每个Probe存储一组SH系数，通过空间插值为场景中任意位置的动态物体提供近似全局光照。SH的线性可插值特性——系数空间中的线性混合对应物理空间中辐照度的平滑过渡——正是辐照度体积能够高效运行的数学保证。
