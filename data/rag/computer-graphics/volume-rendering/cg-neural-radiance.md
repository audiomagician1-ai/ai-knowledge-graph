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

神经辐射场（Neural Radiance Field，简称 NeRF）由 Ben Mildenhall 等人于 2020 年发表在 ECCV 上，论文标题为《NeRF: Representing Scenes as Neural Radiance Fields for View Synthesis》。其核心思想是将三维场景隐式地编码在一个多层感知机（MLP）的权重中，使得给定任意视角的射线方向，均可通过体积渲染积分合成对应的二维图像像素颜色。

与传统的显式三维表示（如三角网格、点云、体素）不同，NeRF 不直接存储几何结构，而是让 MLP 学习一个连续函数 $F_\Theta: (\mathbf{x}, \mathbf{d}) \to (\mathbf{c}, \sigma)$，其中输入为三维空间坐标 $\mathbf{x} = (x,y,z)$ 与观察方向 $\mathbf{d} = (\theta, \phi)$，输出为该点的 RGB 颜色 $\mathbf{c}$ 和体积密度 $\sigma$（单位：$\mathrm{m}^{-1}$）。这种隐式表示在有限的二维监督图像下仍能重建出极为细腻的三维场景，推动了新视角合成（Novel View Synthesis）技术的重大突破。

NeRF 的重要性在于，它将可微分渲染与神经网络紧密结合，使得整个训练流程端到端可微分，无需任何三维真值标注，只需约 50-200 张已知相机位姿的照片即可完成场景重建。

---

## 核心原理

### 1. 体积渲染积分公式

NeRF 的渲染过程直接源于经典的体积渲染方程。沿相机射线 $\mathbf{r}(t) = \mathbf{o} + t\mathbf{d}$，从近裁剪面 $t_n$ 积分到远裁剪面 $t_f$，像素颜色的期望值为：

$$
C(\mathbf{r}) = \int_{t_n}^{t_f} T(t)\, \sigma(\mathbf{r}(t))\, \mathbf{c}(\mathbf{r}(t), \mathbf{d})\, dt
$$

其中透射率（Transmittance）定义为：

$$
T(t) = \exp\!\left(-\int_{t_n}^{t} \sigma(\mathbf{r}(s))\, ds\right)
$$

$T(t)$ 表示光线从 $t_n$ 传播至 $t$ 时，未被任何粒子遮挡的概率。$\sigma$ 越大，光线被"吸收"越多，$T(t)$ 衰减越快。实现中使用数值积分，将射线离散化为 $N$（通常为 64 或 128）个采样点，并用以下离散形式近似：

$$
\hat{C}(\mathbf{r}) = \sum_{i=1}^{N} T_i \left(1 - e^{-\sigma_i \delta_i}\right) \mathbf{c}_i, \quad T_i = \exp\!\left(-\sum_{j=1}^{i-1} \sigma_j \delta_j\right)
$$

其中 $\delta_i = t_{i+1} - t_i$ 为相邻采样点之间的距离。

### 2. 位置编码（Positional Encoding）

直接将 $(x,y,z,\theta,\phi)$ 输入 MLP 会导致网络偏向低频信息，场景细节（高频纹理、锐利边缘）无法重建。NeRF 引入了傅里叶位置编码：

$$
\gamma(p) = \left(\sin(2^0\pi p),\, \cos(2^0\pi p),\, \dots,\, \sin(2^{L-1}\pi p),\, \cos(2^{L-1}\pi p)\right)
$$

对三维坐标 $\mathbf{x}$ 使用 $L=10$（共 60 维），对方向 $\mathbf{d}$ 使用 $L=4$（共 24 维）。这一设计使 MLP 能够高效拟合高频几何和纹理细节，是 NeRF 重建质量的关键。

### 3. 网络结构与分层采样

NeRF 的 MLP 包含 8 层全连接层，每层 256 个神经元，在第 5 层引入跳跃连接（Skip Connection）重新注入位置编码。方向输入 $\mathbf{d}$ 仅在最后一层引入，保证密度 $\sigma$ 与视角无关、颜色 $\mathbf{c}$ 与视角相关（建模镜面反射等视角依赖效果）。

为提升采样效率，NeRF 采用**粗网络 + 细网络（Coarse + Fine）**的分层采样策略：粗网络用 64 个均匀采样点估计密度分布，再根据该分布通过逆变换采样在高密度区域额外采集 128 个点喂给细网络，最终渲染质量由细网络输出决定。

### 4. 损失函数与训练

训练损失为渲染像素颜色与真实像素颜色的均方误差（MSE），同时对粗网络和细网络均施加约束：

$$
\mathcal{L} = \sum_{\mathbf{r} \in \mathcal{R}} \left[\|\hat{C}_c(\mathbf{r}) - C(\mathbf{r})\|_2^2 + \|\hat{C}_f(\mathbf{r}) - C(\mathbf{r})\|_2^2\right]
$$

原始论文在单场景上训练约 100K-300K 次迭代，使用 Adam 优化器，学习率从 $5\times10^{-4}$ 指数衰减至 $5\times10^{-5}$，在单张 V100 GPU 上训练时间约为 1-2 天。

---

## 实际应用

**新视角合成**：在电影特效与文化遗产数字化领域，NeRF 可从手持相机拍摄的照片集合中重建完整场景，随后从任意相机轨迹渲染平滑视频，省去传统多视角摄影机阵列（如百余台同步相机）的高昂硬件成本。

**三维资产生成**：NeRF 生成的隐式场景可通过 Marching Cubes 算法提取出显式网格，导出为标准 3D 格式用于游戏引擎或 AR/VR 应用。工具链如 instant-ngp 将训练时间缩短至数秒（通过哈希编码替代位置编码），大幅降低了工业落地门槛。

**医学影像**：在 CT/MRI 数据稀疏视角重建中，NeRF 的连续密度场与 X 射线投影的物理模型（Beer-Lambert 定律）天然契合，可以少量投影图像重建三维体数据，减少患者辐射剂量。

---

## 常见误区

**误区一：混淆体积密度 $\sigma$ 与不透明度 $\alpha$**

$\sigma$ 是连续的消光系数（物理单位为 $\mathrm{m}^{-1}$），而离散化后的不透明度 $\alpha_i = 1 - e^{-\sigma_i \delta_i}$ 才是"该段射线被遮挡的概率"。若 $\delta_i \to 0$，即使 $\sigma_i$ 有限，$\alpha_i$ 也趋近于零；若 $\delta_i$ 很大，$\alpha_i$ 可趋近于 1。因此调大采样间距会错误地增大不透明度，导致渲染结果偏浑浊。

**误区二：认为 NeRF 可实现实时渲染**

原始 NeRF 每渲染一张 $800\times800$ 分辨率图像需要约 30 秒，因为每个像素需要进行 192 次 MLP 前向推理（64 粗 + 128 细）。实时化需要额外技术手段，如 instant-ngp 的哈希网格或将 NeRF 烘焙为 3D Gaussian Splatting 等后继方法，原始架构本身不支持实时渲染。

**误区三：以为增大 MLP 层数一定提升质量**

NeRF 的高频重建能力主要来自位置编码而非网络深度。论文消融实验表明，去掉位置编码的 NeRF（即使使用相同的 8 层 256 神经元网络）PSNR 下降约 5-7 dB；而在保留位置编码的情况下，将网络加深到 12 层仅带来微小提升。制约重建质量的瓶颈通常是采样策略与训练视角覆盖度，而非网络容量。

---

## 知识关联

**与 Ray Marching 的承接关系**：Ray Marching 提供了沿射线逐步采样并累积颜色/密度的基本框架。NeRF 的离散体积渲染公式本质上就是 Ray Marching 的可微分版本——将原先查询预存体素的步骤替换为查询 MLP，从而使整个采样-渲染流程端到端可微，支持梯度反传训练网络权重。理解 $T_i$ 的递推计算方式（从近到远乘积累积）与 Ray Marching 的 front-to-back 合成顺序完全一致。

**向后续方法的延伸**：NeRF 固定了隐式场景表示与体积渲染结合的范式，催生了 Mip-NeRF（抗锯齿锥形采样）、NeR
