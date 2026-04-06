# 分布式信源编码

## 概述

分布式信源编码（Distributed Source Coding, DSC）研究的是这样一个核心问题：多个地理位置分散的编码器，在彼此无法通信的条件下，分别对各自观测的相关信源进行独立压缩，而解码器在接收到所有码流之后能够联合重建这些信源。这一设定与传统联合信源编码（Joint Source Coding）形成鲜明对比——在联合编码中，编码器之间可以共享信息以利用相关性，但在分布式场景下，编码端无法"合作"。

该领域的奠基性成果由 Jack Slepian 和 Jack Wolf 于 1973 年在论文《Noiseless Coding of Correlated Information Sources》（IEEE Transactions on Information Theory, 1973）中正式建立，给出了现称 **Slepian-Wolf 定理** 的无损分布式压缩速率域（rate region）。随后，Aaron Wyner 与 Jacob Ziv 于 1976 年在《The Rate-Distortion Function for Source Coding with Side Information at the Decoder》（IEEE Transactions on Information Theory, 1976）中将这一框架推广至有损压缩场景，提出了 **Wyner-Ziv 编码** 理论。这两项工作构成了分布式信源编码的理论基石，并在此后三十年间随着传感器网络、视频编码等应用的兴起而重新获得工程界的高度关注。

---

## 核心原理

### Slepian-Wolf 定理：分布式无损压缩的速率域

设两个离散无记忆信源 $X$ 和 $Y$ 联合分布为 $p(x, y)$，两个编码器分别以速率 $R_X$ 和 $R_Y$ 独立编码，解码器接收两条码流后联合重建 $(X^n, Y^n)$，则可无损重建的充要条件是速率对 $(R_X, R_Y)$ 满足：

$$
R_X \geq H(X \mid Y), \quad R_Y \geq H(Y \mid X), \quad R_X + R_Y \geq H(X, Y)
$$

这一速率域令人震惊之处在于：**分布式编码的速率和下界 $H(X,Y)$ 与联合编码完全相同**。也就是说，即使两个编码器不能通信，只要解码器能够联合解码，总速率可以低至联合熵 $H(X,Y)$，而不是各自熵之和 $H(X)+H(Y)$。两者之差 $H(X)+H(Y)-H(X,Y) = I(X;Y)$（互信息）正是分布式编码所"节省"的冗余。

值得注意的是，当 $R_X = H(X)$ 时，对 $Y$ 的压缩仅需 $R_Y = H(Y|X)$（条件熵），此时 $X$ 充当解码侧已知的辅助信息（side information）。对称地，若 $R_Y = H(Y)$，则 $R_X = H(X|Y)$。整个可行速率域是一个以 $(H(X|Y), H(Y))$ 和 $(H(X), H(Y|X))$ 为顶点的五边形区域。

### Wyner-Ziv 编码：有损压缩与边信息

当允许重建存在一定失真时，问题转化为：编码器独立压缩 $X$，解码器拥有相关边信息 $Y$（但编码器不知道 $Y$），求在失真约束 $D$ 下的最小速率 $R_{WZ}(D)$。

Wyner 和 Ziv 证明（Wyner & Ziv, 1976），Wyner-Ziv 速率失真函数为：

$$
R_{WZ}(D) = \min_{p(u|x),\, \hat{x}(u,y):\; \mathbb{E}[d(X,\hat{X})] \leq D} I(X; U) - I(Y; U)
$$

其中 $U$ 是满足 $U \to X \to Y$ 马尔可夫链约束的辅助随机变量，$\hat{x}(u,y)$ 是利用 $U$ 与边信息 $Y$ 的重建函数，$d(\cdot,\cdot)$ 为失真度量。

**一个重要的特殊结论**：对于联合高斯分源 $(X,Y)$（均值为零，方差 $\sigma_X^2$，相关系数 $\rho$）以及均方误差（MSE）失真度量，Wyner-Ziv 速率失真函数恰好等于具有完全边信息时的条件速率失真函数：

$$
R_{WZ}(D) = \frac{1}{2} \log \frac{\sigma_X^2 (1-\rho^2)}{D}, \quad 0 < D \leq \sigma_X^2(1-\rho^2)
$$

这意味着对于高斯源，**编码器是否知晓边信息 $Y$ 不影响最优速率**——即 Wyner-Ziv 编码不存在"边信息代价"。但对于非高斯源，一般存在正的 Wyner-Ziv 代价（WZ penalty），即 $R_{WZ}(D) > R(D|Y)$。

### 编码构造：Syndrome 编码与嵌套码

实现 Slepian-Wolf 编码的主流构造方法基于**陪集编码**（coset coding）或称**伴随式编码**（syndrome coding）。设 $X^n$ 可视为某线性码的一个码字，则编码器仅发送该码字所属陪集的标签（syndrome）；解码器利用边信息 $Y^n$ 与收到的 syndrome 联合进行最大后验（MAP）译码，从可能的陪集代表元中选出与 $Y^n$ "最接近"的序列。

对于 Wyner-Ziv 编码，实用构造基于**嵌套码**（nested codes）：将量化（内码）与信道编码（外码）相结合，以 $Y^n$ 作为虚拟信道输入端的"噪声相关"参考。这一思想最早由 Zamir, Shamai 和 Erez（2002）系统地通过嵌套格码（nested lattice codes）加以实现，为实际工程系统设计奠定了基础。

---

## 关键公式与模型

### 多终端信源编码的速率域统一框架

将 Slepian-Wolf 定理推广至 $K$ 个相关信源 $X_1, X_2, \ldots, X_K$，可无损重建的速率区域由以下 $2^K - 1$ 个不等式刻画：对于任意非空子集 $S \subseteq \{1, 2, \ldots, K\}$，

$$
\sum_{i \in S} R_i \geq H(X_S \mid X_{S^c})
$$

其中 $X_S = \{X_i : i \in S\}$，$X_{S^c}$ 为 $S$ 的补集对应的信源。当 $K=2$ 时退化为标准 Slepian-Wolf 三个不等式。

### 条件熵与压缩增益的量化

设 $X$ 与 $Y$ 的相关系数为 $\rho$，对于均值为零的联合高斯信源，条件熵 $H(X|Y)$ 在高斯近似下满足：

$$
H(X|Y) = h(X) - I(X;Y) = \frac{1}{2}\log(2\pi e \sigma_X^2) - \frac{1}{2}\log\frac{1}{1-\rho^2} = \frac{1}{2}\log(2\pi e \sigma_X^2 (1-\rho^2))
$$

当 $\rho \to 1$（两信源高度相关），$H(X|Y) \to -\infty$（差分熵趋于负无穷），说明分布式压缩可获得极大增益。在离散情形，$H(X|Y) \geq 0$，且相关性越强，$H(X|Y)$ 越接近于 $0$，分布式压缩相比独立压缩节省的速率越大。

---

## 实际应用

**传感器网络（Sensor Networks）** 是分布式信源编码最主要的应用场景。在野外部署的温度、湿度传感器网络中，相邻节点采集的数据高度相关。由于无线传输能耗远高于本地计算，各传感器节点通常无法先彼此交换数据再编码；DSC 框架允许每个节点独立以接近 $H(X_i | X_{-i})$ 的速率压缩发送，由基站集中解码，显著降低总传输能耗（Pradhan & Ramchandran, 2003）。

**案例：分布式视频编码（Distributed Video Coding, DVC）**。在多摄像头监控或低功耗无线摄像头场景中，编码端（摄像头）计算资源有限，难以进行运动估计；Wyner-Ziv 编码框架允许将运动补偿等计算复杂度转移至解码端。编码器对关键帧（key frame）进行标准帧内编码，对非关键帧（Wyner-Ziv 帧）仅发送基于 Turbo 码或 LDPC 码的 syndrome 比特；解码器利用相邻帧作为边信息，通过软解码恢复 Wyner-Ziv 帧。代表性系统如斯坦福大学 Bernd Girod 团队开发的 PRISM 系统（2003）和巴塞罗那大学的 DISCOVER 编解码器（2008）。

**基因组数据压缩**：人类基因组序列中，不同个体的基因组相似度高达 99.9%，相邻 SNP 位点具有强连锁不平衡（LD）。利用参考基因组作为解码侧边信息的 Wyner-Ziv 框架，可将个人基因组压缩比提升数倍，具有重要的医学数据库存储意义。

---

## 常见误区

**误区一：认为分布式编码必然比联合编码差。** Slepian-Wolf 定理的核心洞察恰恰相反：在速率和（total rate）意义上，分布式无损编码与联合编码渐近等价。代价仅在于需要联合解码，解码复杂度更高，且需要已知联合分布 $p(x,y)$。

**误区二：将 Wyner-Ziv 代价（WZ penalty）普遍化。** 高斯信源在均方误差失真下 WZ 代价恰好为零，这是一个特殊结论。对于二元对称信源（BSS）在汉明失真下，Wyner-Ziv 代价同样为零（Wyner, 1978）。但对于一般非高斯、非对称信源，WZ 代价可能为正，即编码器不知晓边信息会导致速率损失。

**误区三：混淆"边信息在编码端"与"边信息在解码端"的情形。** 若边信息 $Y$ 在编码端已知，则 $R \geq H(X|Y)$ 是直接可达的（Shannon, 1948）。Wyner-Ziv 的贡献在于证明即使边信息仅在解码端，对于高斯源同样可以达到 $H(X|Y)$ 附近的速率，这一非直观结论是该理论的精髓所在。

**误区四：认为实用 DSC 系统已接近理论极限。** 尽管基于 Turbo 码和 LDPC 码的实用 Slepian-Wolf 编码已能达到接近 $H(X|Y)$ 的速率（Garcia-Frias & Zhao, 2001），但对于一般有损 Wyner-Ziv 编码，实用系统与理论界之间仍存在 1–3 dB 的差距，是当前研究的活跃方向。

---

## 知识关联

**前置概念**：分布式信源编码建立在**信源编码定理**（Shannon, 1948）之上——单一信源的无损编码下界 $H(X)$ 以及速率失真理论（Rate-Distortion Theory）是理解 Slepian-Wolf 和 Wyner-Ziv 定理的必要基础。此外，**联合典型序列**（Jointly Typical Sequences）与**陪集码**（Coset Codes）的基本知识是理解编码证明的关键工具。

**并列概念**：与**多终端信息论**（Multi-Terminal Information Theory）中的多接入信道（MAC）、广播信道（BC）和干扰信道形成对称性——前者处理分布式信源（压缩端分散），后者处理分布式信道（传输端/接收端分散）。

**延伸概念**：**Berger-Tung 定理**（1978）将 Slepian-Wolf 框架推广至有损多终端场景，但一般情形的速率域（rate-distortion region）至今仍是未解决的开放问题，被列为信息论中最重要的开放问题之一（El Gamal & Kim, 2011，《Network Information Theory》）。**