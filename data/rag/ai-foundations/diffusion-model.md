---
id: "diffusion-model"
concept: "扩散模型"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 5
is_milestone: false
tags: ["diffusion", "ddpm", "stable-diffusion"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 扩散模型

## 概述

扩散模型（Diffusion Models）是一类基于非平衡热力学原理的生成模型，其核心思想是通过学习逆转一个逐步加噪的随机过程来生成数据。具体来说，模型分为两个阶段：**前向扩散过程**将真实数据逐步添加高斯噪声直至完全变为标准正态分布，**逆向去噪过程**则训练一个神经网络学习从噪声中还原数据。这一框架由Sohl-Dickstein等人于2015年首次提出，2020年Ho等人发表的DDPM（Denoising Diffusion Probabilistic Models）论文使其在图像生成领域取得突破性进展。

扩散模型的崛起直接冲击了GAN（生成对抗网络）在图像合成领域长达数年的统治地位。2021年，OpenAI的DALL-E 2和Stability AI的Stable Diffusion均基于扩散模型构建，后者的开源发布更引发了AI图像生成的全民热潮。与GAN相比，扩散模型训练更稳定（无需博弈均衡），生成的样本多样性更高，且更易于控制生成内容，代价是推理速度较慢——原始DDPM需要1000步去噪才能生成一张图片。

## 核心原理

### 前向扩散过程（Forward Process）

前向过程是一个固定的马尔科夫链，在 $T$ 步内逐渐向数据 $x_0$ 添加高斯噪声，产生一系列中间状态 $x_1, x_2, \ldots, x_T$。每步添加的噪声量由噪声调度表（noise schedule）中的超参数 $\beta_t$ 控制：

$$q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t}\, x_{t-1},\, \beta_t \mathbf{I})$$

其中 $\beta_t$ 通常从约 $10^{-4}$ 线性或余弦递增至约 $0.02$。DDPM中的关键数学技巧是**重参数化**，利用 $\bar{\alpha}_t = \prod_{s=1}^{t}(1-\beta_s)$，可直接从 $x_0$ 一步采样任意时刻的噪声状态：

$$q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar{\alpha}_t}\, x_0,\, (1-\bar{\alpha}_t)\mathbf{I})$$

当 $T=1000$ 且 $\bar{\alpha}_T \approx 0$ 时，$x_T$ 近似等于纯高斯噪声 $\mathcal{N}(0, \mathbf{I})$。

### 逆向去噪过程（Reverse Process）

逆向过程目标是学习条件分布 $p_\theta(x_{t-1}|x_t)$，即从噪声图逐步还原真实图像。由于真实的后验分布 $q(x_{t-1}|x_t)$ 依赖整个数据集，模型使用一个U-Net结构的神经网络 $\epsilon_\theta(x_t, t)$ 来预测在时刻 $t$ 添加的噪声 $\epsilon$，然后据此推算去噪后的状态：

$$p_\theta(x_{t-1}|x_t) = \mathcal{N}(x_{t-1};\, \mu_\theta(x_t, t),\, \sigma_t^2 \mathbf{I})$$

其中均值 $\mu_\theta$ 由预测的噪声 $\epsilon_\theta$ 计算得出。训练目标简化为最小化预测噪声与真实噪声之间的均方误差：

$$\mathcal{L}_{\text{simple}} = \mathbb{E}_{t, x_0, \epsilon}\left[\|\epsilon - \epsilon_\theta(\sqrt{\bar{\alpha}_t}x_0 + \sqrt{1-\bar{\alpha}_t}\epsilon,\, t)\|^2\right]$$

### 加速采样：DDIM

原始DDPM需要1000步去噪，推理极慢。2020年Song等人提出DDIM（Denoising Diffusion Implicit Models），通过将逆向过程改为**非马尔科夫确定性过程**，允许跳步采样——仅用50步甚至10步即可生成高质量图像，速度提升10到100倍，且同一噪声输入在不同步数下能生成语义一致的图像，实现了"隐空间插值"能力。

### 条件生成与引导机制

单纯的扩散模型无法按文本提示生成指定内容。Classifier-Free Guidance（CFG）是目前主流方案：训练时随机丢弃文本条件（约10%~20%的概率），推理时同时计算有条件预测 $\epsilon_\theta(x_t, c)$ 和无条件预测 $\epsilon_\theta(x_t, \varnothing)$，并按引导强度 $w$ 加权合并：

$$\tilde{\epsilon} = \epsilon_\theta(x_t, \varnothing) + w \cdot (\epsilon_\theta(x_t, c) - \epsilon_\theta(x_t, \varnothing))$$

$w$ 值通常在5到15之间，$w$ 越大图像越贴合文本但多样性下降。Stable Diffusion默认设置为7.5。

## 实际应用

**文生图（Text-to-Image）**：Stable Diffusion 1.5将扩散过程在潜空间（Latent Space）中进行，利用预训练VAE将512×512图像压缩为64×64的潜向量，再在其上运行扩散过程，使显存需求从约20GB降至约4GB，消费级GPU即可运行。CLIP模型的文本编码器通过Cross-Attention机制将文字语义注入U-Net每一层。

**图像修复（Inpainting）**：通过在前向加噪阶段仅对待填充区域加噪，保持已知区域的 $x_0$ 不变，逆向去噪时模型自动补全缺失内容并与周围像素保持一致。Adobe Photoshop的"创意填充"功能即基于此原理。

**医学影像增强**：扩散模型被用于低剂量CT图像去噪，相比传统滤波方法可在去除噪声的同时更好地保留病灶边缘细节；也被用于MRI超分辨率重建，通过从低分辨率图像出发的条件扩散生成4倍高分辨率结果。

## 常见误区

**误区一：扩散模型的U-Net与图像分割的U-Net功能相同**。扩散模型的U-Net额外接收时间步嵌入 $t$（通过正弦位置编码转为向量后注入各残差块），并且在SD等模型中增加了Cross-Attention层用于接收文本条件，其本质任务是噪声预测而非像素分类，两者架构虽相似但功能逻辑完全不同。

**误区二：步数越多生成质量越高**。增加采样步数（如从20步增至100步）对最终图像质量的提升在实践中往往边际递减，超过50步后差异肉眼难辨。真正影响质量的是模型规模、训练数据质量、噪声调度设计和CFG引导强度，而非无限叠加采样步数。

**误区三：扩散模型只能生成图像**。AudioLDM和MusicGen的部分变体将扩散框架用于音频频谱生成，FrameDiff将其用于蛋白质骨架结构生成，Sora类模型将其用于视频时序帧生成，扩散模型本质上是一种通用的连续数据生成框架。

## 知识关联

**与GAN的关系**：GAN通过生成器-判别器博弈训练，扩散模型用单一去噪网络的极大似然训练替代了这一不稳定的对抗过程，彻底解决了GAN的模式崩溃（Mode Collapse）问题，但代价是推理需要多次前向传播而非GAN的单次前向。理解GAN的生成器概念有助于对比两种生成范式的目标函数差异。

**与变分自编码器（VAE）的关系**：Stable Diffusion的Latent Diffusion Model（LDM）架构将VAE与扩散模型结合——VAE负责像素空间与潜空间的压缩/重建，扩散模型在低维潜空间学习数据分布，这一组合使高分辨率图像生成在计算上可行。

**与Transformer架构的融合**：DiT（Diffusion Transformer，2022）用Transformer块替换U-Net作为扩散模型的骨干网络，通过自注意力机制更好地建模全局一致性，Sora视频生成模型即基于此架构变体构建，代表了扩散模型从CNN时代向Transformer时代的演进方向。
