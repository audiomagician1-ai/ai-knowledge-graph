---
id: "cg-neural-radiance"
concept: "神经辐射场"
domain: "computer-graphics"
subdomain: "volume-rendering"
subdomain_name: "体积渲染"
difficulty: 5
is_milestone: false
tags: ["前沿"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 神经辐射场（NeRF）

## 概述

神经辐射场（Neural Radiance Field，简称 NeRF）是 2020 年由 Ben Mildenhall 等人在论文《NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis》中提出的三维场景表示方法。其核心思想是用一个多层感知机（MLP）将空间坐标 $(x, y, z)$ 与观察方向 $(\theta, \phi)$ 映射为该点的体积密度 $\sigma$ 和 RGB 颜色值 $(r, g, b)$，从而隐式地编码整个三维场景的外观与几何。

NeRF 的重要性在于它彻底改变了新视角合成（Novel View Synthesis）的精度上限。在 NeRF 出现之前，基于点云或网格的传统方法在处理半透明物体、细腻高光和复杂遮挡时效果有限。NeRF 借助可微分体积渲染公式，使得仅凭数十张二维照片就能重建具有照片级真实感的三维场景，并从任意新视角渲染。原始论文在 Blender 合成数据集上达到了 PSNR 31.01 dB 的精度，显著超越当时的竞争方法。

## 核心原理

### 体积渲染积分公式

NeRF 的渲染基于经典体积渲染方程。对于从相机出发沿方向 $\mathbf{d}$ 投射的光线 $\mathbf{r}(t) = \mathbf{o} + t\mathbf{d}$，像素颜色 $\hat{C}(\mathbf{r})$ 由以下积分给出：

$$\hat{C}(\mathbf{r}) = \int_{t_n}^{t_f} T(t)\, \sigma(\mathbf{r}(t))\, \mathbf{c}(\mathbf{r}(t), \mathbf{d})\, dt$$

其中透射率 $T(t) = \exp\!\left(-\int_{t_n}^{t} \sigma(\mathbf{r}(s))\,ds\right)$ 表示光线从近端 $t_n$ 到 $t$ 处未被遮挡的概率。$\sigma$ 为体积密度（可类比消光系数），$\mathbf{c}$ 为与视角相关的颜色。该积分在实践中通过分层采样离散化为：

$$\hat{C}(\mathbf{r}) = \sum_{i=1}^{N} T_i\,(1 - e^{-\sigma_i \delta_i})\,\mathbf{c}_i, \quad T_i = \exp\!\left(-\sum_{j=1}^{i-1}\sigma_j \delta_j\right)$$

其中 $\delta_i = t_{i+1} - t_i$ 为相邻采样点的间距。每条光线默认采用 64 个粗采样点加 128 个精采样点，共计 192 次 MLP 查询。

### 位置编码（Positional Encoding）

直接输入原始坐标 $(x, y, z)$ 会导致 MLP 无法拟合高频细节，因为神经网络对低频函数有天然偏好（即"频谱偏差"）。NeRF 对每个输入分量 $p$ 应用正弦位置编码：

$$\gamma(p) = \left(\sin(2^0\pi p),\, \cos(2^0\pi p),\, \ldots,\, \sin(2^{L-1}\pi p),\, \cos(2^{L-1}\pi p)\right)$$

空间坐标使用 $L=10$（将 3 维坐标扩展为 60 维），方向向量使用 $L=4$（将 2 维方向扩展为 24 维）。这使得 MLP 能够捕捉砖块纹理、树叶边缘等高频几何与纹理信息。

### 分层采样策略（Hierarchical Sampling）

NeRF 使用粗网络（Coarse Network）与细网络（Fine Network）两个独立的 MLP。粗网络在光线区间 $[t_n, t_f]$ 上均匀采样 $N_c = 64$ 个点，根据其输出的体积密度分布构造概率密度函数（PDF）；细网络再从该 PDF 中额外重要性采样 $N_f = 128$ 个点，集中于表面密集区域。这种从粗到细的策略避免了在空旷空间浪费计算量，是 NeRF 收敛质量的关键设计。

### 训练目标

训练时对所有光线计算渲染颜色与真实像素颜色之间的均方误差，损失函数为：

$$\mathcal{L} = \sum_{\mathbf{r} \in \mathcal{R}} \left[ \left\|\hat{C}_c(\mathbf{r}) - C(\mathbf{r})\right\|_2^2 + \left\|\hat{C}_f(\mathbf{r}) - C(\mathbf{r})\right\|_2^2 \right]$$

粗网络与细网络的误差均参与反向传播。原始 NeRF 使用 Adam 优化器，学习率从 $5\times10^{-4}$ 按指数衰减至 $5\times10^{-5}$，在单块 NVIDIA V100 GPU 上训练 100k 至 300k 次迭代，耗时约 1 至 2 天。

## 实际应用

**室内场景重建**：将 NeRF 应用于 LLFF（Local Light Field Fusion）数据集中的手持拍摄照片，可从 20-50 张前向拍摄图像重建走廊、花卉等场景，并在未见视角下生成清晰的深度感图像。原始论文在该数据集上 PSNR 达 26.50 dB，超过当时所有对比方法。

**合成物体渲染**：在 Blender 渲染的 360° 物体数据集（如乐高推土机、鼓、椅子）上，NeRF 能精确重建非朗伯（non-Lambertian）表面的镜面高光，因为颜色输出 $\mathbf{c}$ 依赖于观察方向 $\mathbf{d}$，可模拟视角相关的反射效果。

**后续工程化应用**：Instant NGP（2022）通过多分辨率哈希编码将训练时间缩短至数秒；Nerfstudio 框架将 NeRF 训练流程模块化，支持 COLMAP 自动求解相机位姿后直接训练。这些工具均以 NeRF 的体积渲染公式为核心不变量。

## 常见误区

**误区一：认为体积密度 $\sigma$ 等同于不透明度**。$\sigma$ 是单位长度的消光率（单位为 $\text{m}^{-1}$），而不透明度是一个区间上的积分量 $(1 - e^{-\sigma\delta})$。当 $\sigma\delta \ll 1$ 时两者近似相等，但在粗采样步长较大时 $e^{-\sigma\delta}$ 的指数形式至关重要，线性近似会导致渲染误差累积。

**误区二：认为 NeRF 的 MLP 直接输出像素颜色**。MLP 输出的是场景中每个三维采样点的局部属性 $(\sigma, \mathbf{c})$，像素颜色由体积渲染积分沿整条光线综合计算而来。这一区别决定了 NeRF 能处理透明物体和烟雾，而传统单点着色器无法做到。

**误区三：认为位置编码可以省略**。去除位置编码后，MLP 仅能拟合极低频的颜色变化，导致渲染结果模糊，无法表现砖缝、文字等高频纹理。实验表明，去掉 $\gamma$ 后 PSNR 在合成数据集上下降约 5-8 dB，这一差距在视觉上对应从清晰照片退化为严重过平滑的图像。

## 知识关联

**前置知识：Ray Marching**。NeRF 的离散体积渲染公式本质上是 Ray Marching 的可微分版本——Ray Marching 沿光线步进并累积密度或颜色，NeRF 将同样的步进框架改造为可反向传播的求和形式，用 $1 - e^{-\sigma_i\delta_i}$ 替代硬阈值判断，从而能以梯度信号训练 MLP。理解 Ray Marching 中"透射率乘以局部贡献"的物理直觉，是推导 NeRF 体积渲染公式的直接起点。

**扩展方向**：NeRF 确立了"隐式神经表示 + 可微渲染"的范式。后续工作包括：用三维高斯基元替代 MLP 的 3D Gaussian Splatting（渲染速度提升 100 倍以上）；将动态场景建模为时间维度输入的 D-NeRF；以及通过语义特征嵌入实现场景编辑的 Semantic-NeRF。这些工作均保留了 NeRF 的体积渲染积分作为基础，差异在于场景表示的数据结构选择。
