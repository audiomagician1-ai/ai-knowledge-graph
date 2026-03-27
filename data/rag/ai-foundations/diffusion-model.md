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

扩散模型（Diffusion Model）是一类基于热力学扩散过程的生成式深度学习框架，其核心思想是学习如何将纯噪声逐步还原为真实数据样本。与GAN通过生成器-判别器博弈生成图像不同，扩散模型将生成过程拆分为数百至数千个去噪步骤，每步只做微小的概率预测，从而获得更稳定的训练信号。

扩散模型的理论根基来自2015年Sohl-Dickstein等人发表的论文《Deep Unsupervised Learning using Nonequilibrium Thermodynamics》，但真正引发业界关注的是2020年Ho等人提出的**去噪扩散概率模型（DDPM, Denoising Diffusion Probabilistic Models）**。DDPM通过引入简化的训练目标，将生成质量提升到与GAN媲美的水平。2021年后，OpenAI的DALL-E 2、Stability AI的Stable Diffusion、Google的Imagen等产品均以扩散模型为基础构建，证明了该架构在文生图任务中的主导地位。

扩散模型的重要性在于它彻底解决了GAN长期存在的训练不稳定和模式崩溃问题。由于每个去噪步骤都有明确的概率解释，模型的损失函数来自严格的变分下界推导，而非博弈均衡的近似。这使得扩散模型可以在不增加训练技巧复杂度的前提下，生成分辨率高、多样性丰富的图像。

---

## 核心原理

### 前向过程：逐步加噪

扩散模型的前向过程（Forward Process）定义了一条将真实数据 $x_0$ 逐步破坏为标准高斯噪声 $x_T$ 的马尔可夫链。每一步按如下公式添加噪声：

$$q(x_t | x_{t-1}) = \mathcal{N}(x_t; \sqrt{1 - \beta_t} \, x_{t-1}, \beta_t \mathbf{I})$$

其中 $\beta_t \in (0, 1)$ 是预设的噪声调度参数（noise schedule），通常为线性或余弦曲线。DDPM原论文使用线性调度，$\beta_1 = 0.0001$，$\beta_T = 0.02$，总步数 $T = 1000$。

利用重参数技巧，可以直接从 $x_0$ 一步跳到任意时刻 $x_t$：

$$q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar{\alpha}_t} \, x_0, (1 - \bar{\alpha}_t) \mathbf{I})$$

其中 $\bar{\alpha}_t = \prod_{s=1}^{t}(1 - \beta_s)$。当 $t$ 足够大时，$\bar{\alpha}_t \approx 0$，即 $x_t$ 几乎完全变成了标准高斯噪声。这个一步公式让训练过程可以高效地在任意噪声水平上采样，无需逐步迭代。

### 反向过程：学习去噪

反向过程（Reverse Process）的目标是学习 $p_\theta(x_{t-1} | x_t)$，即给定第 $t$ 步的噪声图像，预测前一步的分布。Ho等人的关键发现是：让神经网络 $\epsilon_\theta(x_t, t)$ 预测每一步中加入的噪声 $\epsilon$，比直接预测 $x_0$ 效果更好。训练损失简化为：

$$\mathcal{L}_{\text{simple}} = \mathbb{E}_{t, x_0, \epsilon} \left[ \| \epsilon - \epsilon_\theta(x_t, t) \|^2 \right]$$

这是一个普通的均方误差回归目标，$t$ 从 $[1, T]$ 均匀采样，$\epsilon \sim \mathcal{N}(0, \mathbf{I})$。去噪网络 $\epsilon_\theta$ 通常采用带时间步嵌入的U-Net架构，以Sinusoidal Position Embedding编码时间步 $t$。

### DDIM加速采样

原始DDPM在推断时需要进行1000步去噪，在GPU上生成一张256×256图像耗时约数十秒。2020年Song等人提出的**DDIM（Denoising Diffusion Implicit Models）**通过重新定义非马尔可夫的采样轨迹，将采样步骤压缩至50步甚至20步，同时保持生成质量。DDIM的更新规则不再需要添加随机噪声，每步是确定性的，这也意味着相同的初始噪声 $x_T$ 总会生成相同的图像，赋予了扩散模型图像插值和隐空间编辑能力。

### 条件引导：Classifier-Free Guidance

文生图任务要求模型接受文本条件 $c$，生成与之对应的图像。**Classifier-Free Guidance（CFG）**是2022年Ho & Salimans提出的主流方案：训练时随机丢弃条件（以概率10%-20%用空token替换 $c$），推断时将条件去噪方向与无条件去噪方向加权混合：

$$\tilde{\epsilon}_\theta(x_t, c) = \epsilon_\theta(x_t, \varnothing) + w \cdot (\epsilon_\theta(x_t, c) - \epsilon_\theta(x_t, \varnothing))$$

引导系数 $w$ 通常设为7～15，$w$ 越大图像与文本越匹配，但多样性越低。Stable Diffusion默认使用 $w = 7.5$。

---

## 实际应用

**文本生成图像**：Stable Diffusion 1.5在512×512分辨率上运行，其U-Net参数量约860M，CLIP文本编码器提供768维的条件向量。通过潜空间扩散（Latent Diffusion Model, LDM）将去噪过程从像素空间移至VAE压缩后的64×64隐空间，推断速度提高了约8倍，显存需求从数十GB降至4-8GB。

**图像修复与编辑**：Repaint算法（2022）将扩散模型用于图像修复，在每个去噪步骤中将已知区域的像素强制替换为前向过程的噪声版本，仅让模型自由填充缺失区域。Adobe Firefly的生成填充（Generative Fill）功能采用了类似原理。

**药物分子设计**：2022年发布的DiffSBDD模型将扩散过程应用于三维分子构象生成，在给定蛋白质口袋的条件下生成具有结合活性的小分子配体。分子的原子坐标和化学键被联合建模为连续与离散的混合扩散过程，展示了扩散模型超出图像域的生成能力。

---

## 常见误区

**误区一：步数越多效果越好**。DDPM的1000步是训练时的设定，推断时使用DDIM可以用20-50步达到接近质量，且过度增加步数收益边际递减。Stable Diffusion XL Turbo通过蒸馏技术甚至将步数压缩至1-4步，质量依然可用。

**误区二：扩散模型本质上比GAN慢**。这一说法仅对原始像素空间的DDPM成立。现代LDM（潜空间扩散模型）将计算搬入低维隐空间，加上DDIM采样和模型蒸馏，推断速度已与GAN相当甚至更快。2023年发布的Consistency Models更是直接学习去噪轨迹的一致性映射，单步生成成为可能。

**误区三：噪声调度（$\beta_t$）是超参数，随意设置即可**。噪声调度直接决定了 $\bar{\alpha}_t$ 的衰减曲线，进而影响模型在不同噪声水平上的训练样本分布。DDPM原始线性调度在高分辨率图像上效果欠佳，因为高分辨率图像在接近 $T=1000$ 时仍残留结构信息。余弦调度（Improved DDPM, 2021）正是为修复这一问题而提出，使 $\bar{\alpha}_t$ 呈S型曲线衰减，在低噪声和高噪声区域均有充足的训练信号。

---

## 知识关联

**前置概念**：理解扩散模型需要掌握**变分自编码器（VAE）**中的重参数技巧，因为训练时从 $q(x_t|x_0)$ 采样 $x_t = \sqrt{\bar{\alpha}_t} x_0 + \sqrt{1-\bar{\alpha}_t}\epsilon$ 正是该技巧的直接应用。**生成对抗网络（GAN）**作为前驱工作提供了高质量生成的基线标准，DDPM论文中的FID分数（最低3.17，超越当时的GAN基线）正是以GAN为对照系。U-Net的跳跃连接结构和注意力层是去噪网络的标配架构，来自**深度学习入门**中的卷积网络知识。

扩散模型的理论框架与**得分匹配（Score Matching）**和**随机微分方程（SDE）**密切相关：Song Yang于2021年证明DDPM是SDE框架的离散化特例，统一了扩散、得分匹配和流模型三条技术路线。进一步延伸方向包括**Flow Matching**（2022），它用更直接的常微分方程轨迹替代扩散过程，训练速度更快，是2024年前沿生成模型（如Stable Diffusion 3、Meta Transfusion）的主要