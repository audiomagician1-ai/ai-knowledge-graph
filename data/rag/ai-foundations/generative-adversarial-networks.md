---
id: "generative-adversarial-networks"
concept: "生成对抗网络"
domain: "ai-engineering"
subdomain: "ai-foundations"
subdomain_name: "AI基础"
difficulty: 7
is_milestone: false
tags: ["AI", "生成模型"]

# Quality Metadata (Schema v2)
content_version: 1
quality_tier: "A"
quality_score: 62.8
generation_method: "ai-batch-v1"
unique_content_ratio: 1.0
last_scored: "2026-03-21"
sources: []
---
# 生成对抗网络（GAN）

## 核心概念

生成对抗网络（GAN, Generative Adversarial Network）由两个神经网络组成——生成器和判别器——它们相互对抗训练。生成器学习生成逼真数据，判别器学习区分真实数据和生成数据。

## 架构

```
噪声 z → [生成器 G] → 生成数据 G(z) →┐
                                        ├→ [判别器 D] → 真/假
真实数据 x ─────────────────────────→┘
```

- **生成器 G**: 将随机噪声z映射为数据空间的样本
- **判别器 D**: 判断输入数据是真实的还是生成的

## 训练过程

两个网络交替训练，形成博弈：

1. **训练判别器**: 固定G，让D学会区分真假
   - 最大化：真实数据判为真 + 生成数据判为假

2. **训练生成器**: 固定D，让G学会骗过D
   - 最小化：D对G(z)判为假的概率

数学形式（minimax博弈）：
```
min_G max_D  E[log D(x)] + E[log(1 - D(G(z)))]
```

理想终态：G生成的数据分布与真实分布完全一致，D对任何输入输出0.5（无法区分）。

## 主要变体

| 变体 | 特点 |
|------|------|
| DCGAN | 使用卷积网络，图像生成的里程碑 |
| WGAN | Wasserstein距离替代JS散度，训练更稳定 |
| StyleGAN | 风格控制的高质量人脸生成 |
| CycleGAN | 无配对数据的图像风格转换 |
| Pix2Pix | 配对数据的图像到图像转换 |

## 训练挑战

- **模式坍塌**: 生成器只学会生成少数几种样本
- **训练不稳定**: G和D之间的均衡难以维持
- **评估困难**: 没有统一指标衡量生成质量
- **梯度消失**: D太强时G的梯度接近零

## 评估指标

- **FID (Fréchet Inception Distance)**: 生成分布与真实分布的距离
- **IS (Inception Score)**: 生成图像的质量和多样性
- **LPIPS**: 感知相似度度量

## 与神经网络和深度学习的关系

GAN建立在深度学习基础之上。生成器和判别器通常是深度卷积网络或Transformer。理解反向传播和网络训练是理解GAN训练过程的前提。

## 历史地位

GAN由Ian Goodfellow于2014年提出，被Yann LeCun称为"机器学习近十年来最有趣的想法"。虽然在图像生成领域逐渐被扩散模型（Diffusion Models）取代，但GAN的对抗训练思想影响深远。
