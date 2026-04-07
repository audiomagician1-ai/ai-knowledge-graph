---
id: "cg-upscaling"
concept: "超分辨率技术"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 88.0
generation_method: "intranet-llm-rewrite-v3"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v3"
  - type: "academic"
    citation: "Tsai, R. Y., & Huang, T. S. (1984). Multiframe image restoration and registration. Advances in Computer Vision and Image Processing, 1, 317–339."
  - type: "academic"
    citation: "Wang, X., Yu, K., Wu, S., et al. (2018). ESRGAN: Enhanced super-resolution generative adversarial networks. Proceedings of the European Conference on Computer Vision Workshops (ECCVW), 63–79."
  - type: "academic"
    citation: "Dong, C., Loy, C. C., He, K., & Tang, X. (2014). Learning a deep convolutional network for image super-resolution. Proceedings of the European Conference on Computer Vision (ECCV), 184–199."
  - type: "academic"
    citation: "Sajjadi, M. S. M., Schölkopf, B., & Hirsch, M. (2017). EnhanceNet: Single image super-resolution through automated texture synthesis. Proceedings of the IEEE International Conference on Computer Vision (ICCV), 4491–4500."
scorer_version: "scorer-v2.1"
quality_method: intranet-llm-rewrite-v3
updated_at: 2026-04-06
---

# 超分辨率技术

## 概述

超分辨率技术（Super-Resolution，SR）是指从低分辨率输入图像重建出高分辨率输出图像的一类算法总称。在图形渲染领域，超分辨率的核心动机是以较低的像素填充率（pixel fill rate）换取更高的最终输出质量——即在内部以较小分辨率渲染场景，再通过算法将其放大至目标分辨率，从而绕过GPU光栅化阶段最耗时的像素着色瓶颈。

超分辨率算法的学术研究可追溯至1984年Tsai与Huang发表的频域重建论文（Tsai & Huang, 1984），该论文首次以严格的信号处理框架证明：若多帧低分辨率图像之间存在亚像素级位移，则可利用频域混叠关系求解原始高分辨率信号，奠定了时间超分辨率的理论基础。此后学界在2014至2016年间相继提出SRCNN（Dong et al., 2014）、VDSR（Kim et al., 2016）等卷积神经网络方案，将PSNR提升约2~3 dB。ESRGAN（Wang et al., 2018）则在感知质量维度进一步突破，通过引入相对论判别器（Relativistic Discriminator）与感知损失函数（Perceptual Loss），使生成纹理细节的主观评分（MOS，Mean Opinion Score）超越传统PSNR优化方法约0.3分（满分5分量表）。真正影响实时渲染工业的转折点是2018年9月NVIDIA在图灵架构（Turing, RTX 20系列）上随《战地5》发布DLSS 1.0，以及AMD于2021年6月发布的开源方案FSR 1.0（FidelityFX Super Resolution）。这两项技术将深度学习超分辨率与传统图像缩放算法分别推向量产GPU，使超分辨率从离线后处理变为每帧实时运行的渲染管线阶段，覆盖游戏、影视及虚拟现实等多个领域。

超分辨率技术之所以在抗锯齿框架下被重点讨论，是因为其放大过程天然承担了重建亚像素信息的职责：一个设计良好的超分辨率算法不仅要填补缺失的高频细节，还要抑制放大过程中的振铃（ringing）与棋盘格（checkerboard）伪影，这与传统MSAA、TAA在亚像素级别抑制混叠的目标高度一致，但实现路径根本不同。

---

## 核心原理

### 空间超分辨率（Spatial SR）

空间超分辨率仅使用**单帧**低分辨率图像作为输入，通过卷积网络或分析性滤波器一次性完成放大。放大因子通常记为 $s$，输出尺寸为 $s \times W$ 乘以 $s \times H$，所需填充的新像素数量为原始像素数的 $s^2 - 1$ 倍。FSR 1.0的EASU（Edge-Adaptive Spatial Upsampling）阶段是典型的空间超分辨率：它在每个输出像素处计算方向性梯度，决定沿边缘方向还是垂直边缘方向做插值，从而在2×放大时将锐利边缘的锯齿明显减少。EASU之后紧随RCAS（Robust Contrast-Adaptive Sharpening）锐化阶段，通过4抽头（4-tap）反锐化掩模（Unsharp Mask）恢复因插值引入的模糊，两阶段合计在RDNA2架构上约耗时0.7毫秒（4K输出，质量模式）。空间超分辨率的根本局限在于信息量受限于单帧，无法重建运动序列中时间维度上积累的亚像素采样。

例如，以FSR 1.0处理一张1920×1080的输入图像，放大至3840×2160时，EASU阶段会在输出分辨率的每个像素处查询12个邻域样本，并根据局部梯度方向动态调整插值核权重：当梯度方向检测为水平边缘时，插值核沿水平方向拉伸，减少垂直方向上的锯齿抖动；在各向同性区域（如天空）则退化为标准Lanczos滤波以保留平滑过渡。整个过程在Radeon RX 6800 XT上约耗时0.7毫秒，具备实用的实时性能。

### 时间超分辨率（Temporal SR）

时间超分辨率利用**多帧历史信息**，通过运动向量将前几帧的像素反投影（back-projection）到当前帧坐标系，从而获得相当于多重亚像素采样的信息量。DLSS 2.x/3.x的核心正是时间超分辨率：每帧使用抖动（jitter）偏移相机投影矩阵，使相邻帧的采样位置在像素网格上形成Halton序列分布，多帧累积后理论亚像素覆盖率随帧数 $n$ 增长，相邻采样间隔精度约为 $1/\sqrt{n}$ 个像素单位。

时间方法的主要挑战是**幽灵（ghosting）**伪影：当遮挡或快速运动使历史帧无效时，若权重未及时衰减，前帧残像会在新几何体边缘滞留。DLSS通过深度神经网络（训练集超过100万张16K参考图像对，包含多种游戏场景与光照条件）隐式学习何时丢弃历史帧，而不依赖显式的像素差阈值裁剪，这正是其相比FSR 2.x在高速运动场景下幽灵抑制更优的核心原因。

### 统一框架：时空联合超分辨率

将两种路径统一描述时，可用如下重建公式：

$$\hat{I}_{high} = f\!\left(\{L_t,\, L_{t-1},\, \ldots,\, L_{t-k}\},\; \{MV_t\},\; \theta\right)$$

其中 $L_t$ 为当前帧低分辨率输入（分辨率为 $W \times H$），$MV_t$ 为像素级运动向量场（维度为 $W \times H \times 2$，分别编码水平与垂直位移），$\theta$ 为网络参数或滤波器核，$k=0$ 退化为纯空间方法，$k>0$ 为时间方法。英特尔XeSS 1.0（2022年10月随Arc A770发布）采用的DP4a（Dot Product of 4 elements, 8-bit integer）指令集加速矩阵乘法，使上述网络推理在非NVIDIA硬件上达到实用帧率，体现了统一框架在不同硬件路径上的实现多样性。

时间帧数 $k$ 的选取是精度与延迟的权衡：DLSS通常累积4~8帧有效历史，而FSR 2.0虽也引入时间信息但依赖显式的颜色夹紧（color clamping）而非神经网络决策。颜色夹紧会将历史帧颜色强制约束在当前帧邻域色彩的包围盒（bounding box）内，可有效消除幽灵，但同时也会抹去部分合法的时间积累细节，在静止场景下导致轻微的时间抖动（temporal flickering）。

### 质量评估指标

超分辨率的质量通常用**PSNR**（峰值信噪比，单位dB）和**SSIM**（结构相似性指数，范围0~1）度量。PSNR定义为：

$$\text{PSNR} = 10 \cdot \log_{10}\!\left(\frac{MAX_I^2}{MSE}\right)$$

其中 $MAX_I$ 为像素最大值（8位图像为255），$MSE$（均方误差）定义为 $\frac{1}{mn}\sum_{i=0}^{m-1}\sum_{j=0}^{n-1}\left[I(i,j)-\hat{I}(i,j)\right]^2$，$m$ 与 $n$ 分别为图像的行数与列数，$I$ 为参考高分辨率图像，$\hat{I}$ 为超分辨率重建结果。一般而言，PSNR超过40 dB视为重建质量优秀，低于30 dB则存在明显视觉失真。

然而，在游戏实时渲染场景中PSNR与主观视觉体验相关性有限，因为人眼对纹理的感知锐度比均方误差更敏感。更有价值的指标是**时间稳定性**（temporal stability），即相邻帧输出之间的L2差分归一化值——DLSS 3.5（2023年8月发布，新增光线重建Ray Reconstruction功能）在此项指标上比FSR 2.2低约15%（NVIDIA内部基准，2023年）。此外，LPIPS（Learned Perceptual Image Patch Similarity，Zhang et al., 2018）作为感知距离指标，通过AlexNet/VGG特征空间中的L2距离衡量感知差异，在离线渲染评估中使用日益广泛。超分辨率放大因子越高（如4×），重建难度呈超线性增长，因为需要填充的高频信息量与 $s^2$ 成正比，4×放大时需重建的像素中有约93.75%为算法生成，对网络容量要求极为苛刻。

---

## 关键公式与数学模型

### 图像退化模型

超分辨率问题的数学本质是求解一个病态逆问题（ill-posed inverse problem）。标准图像退化模型将低分辨率观测 $L$ 表示为高分辨率原始图像 $I_{high}$ 经过模糊、下采样与噪声污染的结果：

$$L = \mathbf{D} \cdot \mathbf{B} \cdot I_{high} + \mathbf{n}$$

其中 $\mathbf{B}$ 为模糊核（通常为高斯核，标准差 $\sigma$ 典型值为1.0~2.0像素），$\mathbf{D}$ 为下采样矩阵（以步长 $s$ 进行均匀下采样），$\mathbf{n}$ 为加性高斯白噪声（方差 $\sigma_n^2$）。超分辨率的目标即为从 $L$ 估计 $\hat{I}_{high}$，使某一损失函数 $\mathcal{L}(\hat{I}_{high}, I_{high})$ 最小化。

### 感知损失函数

ESRGAN（Wang et al., 2018）采用的感知损失函数将像素级L1损失、对抗损失与VGG特征空间损失三项组合：

$$\mathcal{L}_{total} = \lambda_1 \mathcal{L}_{pixel} + \lambda_2 \mathcal{L}_{perceptual} + \lambda_3 \mathcal{L}_{GAN}$$

其中 $\lambda_1 = 0.01$，$\lambda_2 = 1.0$，$\lambda_3 =