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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 扩散模型

## 概述

扩散模型（Diffusion Model）是一类基于马尔可夫链的生成模型，其核心思想来源于非平衡热力学中的扩散过程。模型的运作分为两个阶段：**前向扩散过程**（forward process）逐步向数据添加高斯噪声，直至数据完全变为标准正态分布；**反向去噪过程**（reverse process）则训练神经网络从纯噪声中逐步还原出真实数据。2020年，Jonathan Ho等人在论文《Denoising Diffusion Probabilistic Models》（DDPM）中首次系统性地将去噪扩散概率模型用于高质量图像生成，奠定了现代扩散模型的理论基础。

扩散模型之所以受到广泛关注，在于其生成质量显著优于早期GAN模型，且训练过程更稳定。GAN容易出现模式崩溃（mode collapse）问题，而扩散模型通过最大化变分下界（ELBO）进行训练，损失函数具有明确的概率解释。2021年OpenAI的DALL-E 2、2022年Stability AI的Stable Diffusion，以及Google的Imagen均基于扩散模型架构，推动了文本生成图像技术的商业化落地。

## 核心原理

### 前向扩散过程

前向过程定义了一个固定的马尔可夫链，在 $T$ 步内向原始数据 $x_0$ 逐步添加高斯噪声。每一步的转移概率为：

$$q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1-\beta_t} \, x_{t-1}, \beta_t \mathbf{I})$$

其中 $\beta_t \in (0,1)$ 是预设的噪声调度参数（noise schedule），通常从 $\beta_1 = 10^{-4}$ 线性递增至 $\beta_T = 0.02$。利用重参数化技巧，可以直接从 $x_0$ 采样任意时刻的 $x_t$：

$$x_t = \sqrt{\bar{\alpha}_t} \, x_0 + \sqrt{1 - \bar{\alpha}_t} \, \epsilon, \quad \epsilon \sim \mathcal{N}(0, \mathbf{I})$$

其中 $\alpha_t = 1 - \beta_t$，$\bar{\alpha}_t = \prod_{s=1}^{t} \alpha_s$。DDPM通常设置 $T = 1000$，当 $t = T$ 时 $\bar{\alpha}_T \approx 0$，$x_T$ 近似为标准正态分布。

### 反向去噪过程与训练目标

反向过程用参数为 $\theta$ 的神经网络逼近真实后验 $q(x_{t-1}|x_t, x_0)$。DDPM将训练目标简化为**预测添加的噪声 $\epsilon$**，最终简化损失函数为：

$$\mathcal{L}_{\text{simple}} = \mathbb{E}_{t, x_0, \epsilon} \left[ \| \epsilon - \epsilon_\theta(x_t, t) \|^2 \right]$$

即让网络 $\epsilon_\theta$ 在给定带噪样本 $x_t$ 和时间步 $t$ 的条件下，预测原始噪声 $\epsilon$。这一简化形式去除了变分下界中各时间步的权重系数，实验证明效果更好。网络结构通常采用带有时间步嵌入（timestep embedding）的U-Net，时间步 $t$ 通过正弦位置编码注入各层。

### 采样加速：DDIM与其他方法

DDPM的主要缺陷是采样速度慢，需要进行 $T=1000$ 次完整的神经网络前向推理。2021年Song等人提出**DDIM**（Denoising Diffusion Implicit Models），将马尔可夫采样过程改写为确定性的非马尔可夫过程，仅需约50步即可生成质量相当的图像，速度提升约20倍。此外，DPM-Solver利用扩散ODE的半线性结构，进一步将步数压缩至10-20步。Stable Diffusion采用的**潜空间扩散**（Latent Diffusion Model, LDM）则先用VAE将512×512图像压缩到64×64的潜变量空间中再进行扩散，将训练计算量降低约48倍。

### 条件生成与分类器引导

无条件扩散模型无法接收文本提示。**分类器引导**（Classifier Guidance）通过在反向采样中加入分类器梯度来控制生成方向：$\nabla_{x_t} \log p(y|x_t)$。更实用的方法是**无分类器引导**（Classifier-Free Guidance，CFG），由Ho和Salimans于2022年提出：训练时随机以20%的概率丢弃条件，推理时使用：

$$\tilde{\epsilon}_\theta(x_t, c) = \epsilon_\theta(x_t, \varnothing) + w \cdot (\epsilon_\theta(x_t, c) - \epsilon_\theta(x_t, \varnothing))$$

其中 $c$ 为条件（如文本嵌入），$w$ 为引导尺度（guidance scale），Stable Diffusion默认值为7.5。增大 $w$ 可提升图文相关性，但会降低图像多样性。

## 实际应用

**文本生成图像**是扩散模型最成熟的应用。Stable Diffusion 1.5使用CLIP ViT-L/14作为文本编码器，通过交叉注意力机制将512维文本嵌入注入U-Net的每个残差块。用户可通过正向提示词指定期望内容，通过负向提示词（negative prompt）排除不想出现的元素，如"blurry, low quality"。

**图像修复与编辑**方面，DALL-E 2提供inpainting功能，用户可在遮罩区域内基于文本描述重新生成内容，同时保持周边区域一致性。DreamBooth技术仅需3-5张人物照片进行微调，即可让模型学会特定人物的面部特征，实现个性化肖像生成。

**医学图像合成**是新兴应用场景：扩散模型可生成具有病理特征的合成CT/MRI图像用于数据增强，缓解稀有病例数据不足的问题，2023年多项研究证明合成数据可将分割模型AUC提升2-5个百分点。

## 常见误区

**误区一：扩散模型只能生成图像**。事实上，扩散模型已被成功应用于音频合成（WaveGrad、DiffWave）、视频生成（Video Diffusion Models）、蛋白质结构预测（FrameDiff）和点云生成，是一类通用的生成框架，并非图像专用。

**误区二：步数越多生成质量越高**。DDPM的T=1000步是训练时的设定，采样时可通过DDIM在50步内获得几乎等效质量；过度增加推理步数不会带来明显的质量提升，反而线性增加计算时间。许多实践者误以为Stable Diffusion默认的20步不够，盲目增加到100步以上，实际收益微乎其微。

**误区三：CFG引导尺度越大越好**。$w$ 值（guidance scale）超过15时，图像往往出现过饱和、颜色失真和伪影，这是因为高引导尺度本质上是在对数似然空间中进行极端外推，导致生成分布超出训练数据覆盖范围。通常 $w \in [7, 12]$ 是文本生成图像任务的合理区间。

## 知识关联

学习扩散模型需要具备**生成对抗网络（GAN）**的知识背景，方能理解两类模型在训练稳定性、样本多样性和评估指标（FID分数）上的本质差异：GAN通过对抗训练隐式学习数据分布，而扩散模型通过最大化ELBO显式建模扩散过程的逆转。**深度学习入门**中的变分自编码器（VAE）概念是理解证据下界推导的前置知识；U-Net架构的卷积、跳跃连接结构是理解扩散模型网络主干的必要基础；注意力机制则是理解条件控制如何在特征图层面实现的关键。掌握扩散模型后，可进一步延伸至流匹配（Flow Matching）——它将扩散过程的SDE形式统一为更一般的ODE框架，是Stable Diffusion 3和Meta Voicebox所采用的下一代生成范式。