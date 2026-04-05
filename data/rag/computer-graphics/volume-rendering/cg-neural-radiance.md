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
content_version: 4
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 神经辐射场（NeRF）

## 概述

神经辐射场（Neural Radiance Field，NeRF）是2020年由Ben Mildenhall等人在论文《NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis》中提出的一种三维场景表示与新视角合成方法。其核心思想是用一个多层感知机（MLP）将三维空间坐标 $(x, y, z)$ 和视角方向 $(\theta, \phi)$ 映射到该点的体积密度 $\sigma$ 与颜色 $(r, g, b)$，从而将整个连续场景编码进神经网络的权重中。

NeRF的重要意义在于它将隐式神经表示与经典体积渲染方程直接结合，绕过了显式几何重建（如点云或网格）的中间步骤，仅凭一组带有相机位姿的二维图像即可合成任意新视角的逼真图像。该方法在当时的新视角合成任务上将PSNR（峰值信噪比）提升了约3~5 dB，远超此前的隐式表示方法。

## 核心原理

### 辐射场的数学定义

NeRF将场景表示为一个连续函数：

$$F_\Theta: (x, y, z, \theta, \phi) \rightarrow (\mathbf{c}, \sigma)$$

其中 $\mathbf{c} = (r, g, b)$ 是颜色，$\sigma$ 是体积密度（单位：1/距离），表示光线在该点被遮挡的概率微分。注意，体积密度 $\sigma$ 只依赖于位置 $(x,y,z)$，而颜色 $\mathbf{c}$ 同时依赖于位置和视角方向，这一设计使模型能够表达视角相关的高光效果。网络架构包含8层全连接层（隐藏维度256），并在第5层将位置编码特征重新拼接以缓解梯度消失问题。

### 体积渲染积分公式

给定一条从相机出发的光线 $\mathbf{r}(t) = \mathbf{o} + t\mathbf{d}$，沿近裁剪面 $t_n$ 到远裁剪面 $t_f$ 积分，像素的期望颜色为：

$$C(\mathbf{r}) = \int_{t_n}^{t_f} T(t)\,\sigma(\mathbf{r}(t))\,\mathbf{c}(\mathbf{r}(t), \mathbf{d})\,dt$$

其中透射率 $T(t)$ 表示光线从 $t_n$ 到 $t$ 未被阻挡的概率：

$$T(t) = \exp\!\left(-\int_{t_n}^{t} \sigma(\mathbf{r}(s))\,ds\right)$$

在实现中，将光线离散化为 $N$ 个采样点后，颜色估计公式变为：

$$\hat{C}(\mathbf{r}) = \sum_{i=1}^{N} T_i\,(1 - e^{-\sigma_i \delta_i})\,\mathbf{c}_i$$

其中 $\delta_i = t_{i+1} - t_i$ 是相邻采样点的间距，$T_i = \exp(-\sum_{j=1}^{i-1}\sigma_j\delta_j)$，$(1-e^{-\sigma_i\delta_i})$ 为该段的不透明度（alpha值）。此公式正是Ray Marching框架下的Alpha合成在神经网络场景中的直接应用。

### 位置编码（Positional Encoding）

直接将坐标输入MLP会导致网络倾向于学习低频函数，无法重建高频细节。NeRF采用傅里叶位置编码将输入映射到高维空间：

$$\gamma(p) = \left(\sin(2^0\pi p),\cos(2^0\pi p), \ldots, \sin(2^{L-1}\pi p),\cos(2^{L-1}\pi p)\right)$$

对位置坐标取 $L=10$（输出60维），对视角方向取 $L=4$（输出24维）。这一操作将原始3+2维的输入扩展为63维，是NeRF能够重建精细纹理和尖锐边缘的关键。

### 分层采样策略（Coarse-to-Fine Sampling）

NeRF使用两个网络——粗网络（coarse）和细网络（fine）——来提升采样效率。粗网络在光线上均匀采样64个点，根据粗网络预测的密度分布，利用逆变换采样在密度较大的区域重采样128个额外点，再将共192个点输入细网络得到最终颜色。整体损失函数为：

$$\mathcal{L} = \sum_{\mathbf{r} \in \mathcal{R}}\left[\|\hat{C}_c(\mathbf{r}) - C(\mathbf{r})\|_2^2 + \|\hat{C}_f(\mathbf{r}) - C(\mathbf{r})\|_2^2\right]$$

粗、细网络的重建误差均参与反向传播，整个训练过程在单块NVIDIA V100 GPU上需约1~2天（约100万次迭代）。

## 实际应用

**新视角合成**：NeRF在Blender合成数据集（如Lego、Drums等8个场景）上达到了31.01 dB的平均PSNR，在真实场景数据集LLFF上达到26.50 dB，这两个指标在2020年均为当时最优。只需30~100张图像作为输入，训练完毕后可从任意位置渲染照片级真实感图像。

**三维内容创作**：影视制作公司使用NeRF对实景拍摄的道具进行数字化重建，替代传统的多视图立体视觉（MVS）加手工修复流程。Instant-NGP（2022年NVIDIA）通过哈希编码将训练时间压缩至数秒，使NeRF进入实时级应用门槛。

**机器人导航与SLAM**：iMAP和NICE-SLAM等系统将NeRF嵌入实时SLAM框架，用密度场 $\sigma$ 直接表示占用概率，无需维护离散体素地图。

## 常见误区

**误区一：NeRF的体积密度等同于几何表面**。$\sigma$ 是概率密度而非二值占用标志，同一位置的 $\sigma$ 值为100与1000的渲染差异主要体现在透射率衰减速度上，而非表示"有表面"或"无表面"。提取显式几何需要额外操作（如Marching Cubes阈值化），且结果对阈值敏感。

**误区二：位置编码中的频率数 $L$ 越大越好**。实验表明，对位置使用 $L>10$ 时网络容易过拟合训练视角，在新视角上出现浮影（floater）伪影；对视角方向使用 $L>4$ 时会过度拟合视角相关噪声。论文中的 $L=10/4$ 是经过消融实验确认的平衡点。

**误区三：NeRF可以直接处理动态场景**。原始NeRF假设场景是静态的，对运动物体或光照变化不具备泛化能力。其MLP权重对应唯一一个场景实例，更换场景必须重新训练，这与通用三维重建方法有本质区别。D-NeRF等变体需要显式引入时间维度 $t$ 作为额外输入来建模动态场景。

## 知识关联

NeRF直接建立在Ray Marching的基础上：Ray Marching提供了沿光线离散采样并累积颜色的框架，而NeRF将每个采样点的属性从查找表或解析函数替换为MLP的前向推断输出。理解透射率 $T(t)$ 的指数积分形式需要掌握Beer-Lambert定律，该定律描述光在均匀介质中的指数衰减，$\sigma$ 正是吸收系数的神经网络参数化版本。

在训练机制上，NeRF依赖随机梯度下降（通常使用Adam优化器，学习率从 $5\times10^{-4}$ 衰减至 $5\times10^{-5}$）通过渲染损失端到端地学习场景几何与外观，无需任何三维监督信号，这一特性使其成为纯图像驱动三维重建的代表性范式，并直接催生了3D Gaussian Splatting等后续显式表示方法的发展。