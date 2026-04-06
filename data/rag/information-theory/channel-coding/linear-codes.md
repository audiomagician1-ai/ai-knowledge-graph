# 线性码

## 概述

线性码（Linear Code）是信道编码理论的核心构件，由Richard Hamming于1950年在贝尔实验室的奠基性论文《Error Detecting and Error Correcting Codes》中系统化奠定基础，随后由Marcel Golay、Irving Reed、David Muller等人相继拓展。线性码的"线性"特指码字集合构成有限域 $\mathbb{F}_q$（通常 $q=2$）上的向量子空间：任意两个码字的线性组合仍是码字，即对码字 $\mathbf{c}_1, \mathbf{c}_2 \in \mathcal{C}$ 及域元素 $\alpha, \beta$，有 $\alpha\mathbf{c}_1 + \beta\mathbf{c}_2 \in \mathcal{C}$。这一代数结构使得线性码拥有高效的编码器设计、系统化的错误检测与纠错算法，以及精确的最小距离分析能力，是Turbo码、LDPC码、极化码等现代编码方案的理论前驱。

一个 $[n, k, d]$ 线性码将 $k$ 比特信息映射为 $n$ 比特码字，最小汉明距离为 $d$，冗余度为 $r = n - k$。码率（Code Rate）定义为 $R = k/n$，量化每个码字比特携带的信息量。例如，经典的 $[7, 4, 3]$ Hamming码每7位码字携带4位信息，码率 $R = 4/7 \approx 0.571$，能纠正1个比特错误并检测2个比特错误。

---

## 核心原理

### 生成矩阵（Generator Matrix）

生成矩阵 $G$ 是一个 $k \times n$ 的矩阵，其行向量构成码空间 $\mathcal{C}$ 的一组基。编码过程为：
$$\mathbf{c} = \mathbf{m} G$$
其中 $\mathbf{m} \in \mathbb{F}_2^k$ 是长度为 $k$ 的消息向量，$\mathbf{c} \in \mathbb{F}_2^n$ 是长度为 $n$ 的码字（均为行向量）。$G$ 的 $k$ 行必须线性无关，保证 $\mathcal{C}$ 恰好包含 $2^k$ 个不同码字。

系统形式（Systematic Form）的生成矩阵具有 $G = [I_k \mid P]$ 的结构，其中 $I_k$ 是 $k \times k$ 单位矩阵，$P$ 是 $k \times (n-k)$ 的奇偶校验矩阵。此时码字 $\mathbf{c} = [\mathbf{m} \mid \mathbf{m}P]$，前 $k$ 位直接复制消息比特，后 $r = n-k$ 位为冗余校验位，极大简化了编码电路的实现。

**例如**，$[7,4,3]$ Hamming码的系统生成矩阵为：
$$G = \begin{pmatrix} 1&0&0&0&1&1&0 \\ 0&1&0&0&1&0&1 \\ 0&0&1&0&0&1&1 \\ 0&0&0&1&1&1&1 \end{pmatrix}$$
消息 $\mathbf{m} = (1,0,1,1)$ 编码为 $\mathbf{c} = \mathbf{m}G = (1,0,1,1,0,1,1)$，其中最后三位 $(0,1,1)$ 是校验位。

### 校验矩阵（Parity-Check Matrix）

校验矩阵 $H$ 是 $(n-k) \times n$ 的矩阵，定义了码字必须满足的线性约束。$\mathbf{c}$ 是码字当且仅当：
$$H\mathbf{c}^T = \mathbf{0}$$
即 $\mathcal{C}$ 是 $H$ 的零空间（Null Space）：$\mathcal{C} = \ker(H)$。对于系统生成矩阵 $G = [I_k \mid P]$，对应的校验矩阵为 $H = [-P^T \mid I_{n-k}]$，在二进制域中即 $H = [P^T \mid I_{n-k}]$（因 $-1 \equiv 1 \pmod{2}$）。

**伴随式（Syndrome）**是校验矩阵最重要的应用。接收向量 $\mathbf{r} = \mathbf{c} + \mathbf{e}$（$\mathbf{e}$ 为错误向量）的伴随式定义为：
$$\mathbf{s} = H\mathbf{r}^T = H(\mathbf{c} + \mathbf{e})^T = H\mathbf{e}^T$$
由于 $H\mathbf{c}^T = \mathbf{0}$，伴随式 $\mathbf{s}$ 完全由错误模式 $\mathbf{e}$ 决定，与发送码字无关。这使得伴随式解码成为可能：通过查表（Syndrome Table）将长度为 $n-k$ 的伴随式映射到最可能的错误向量 $\hat{\mathbf{e}}$，再由 $\hat{\mathbf{c}} = \mathbf{r} - \hat{\mathbf{e}}$ 恢复码字。

对于 $[7,4,3]$ Hamming码，校验矩阵 $H$ 的列恰好对应1到7的二进制表示：
$$H = \begin{pmatrix} 0&0&0&1&1&1&1 \\ 0&1&1&0&0&1&1 \\ 1&0&1&0&1&0&1 \end{pmatrix}$$
若第 $i$ 位出错，则伴随式 $\mathbf{s} = H\mathbf{e}_i^T$ 等于 $H$ 的第 $i$ 列，即数字 $i$ 的二进制编码，直接指示出错位置——这正是Hamming码名称中"自指示"设计的精妙之处（Hamming, 1950）。

### 最小汉明距离与纠错能力

线性码最重要的性质之一是其**最小距离等于最小非零码字重量**：
$$d_{\min}(\mathcal{C}) = \min_{\mathbf{c} \in \mathcal{C},\ \mathbf{c} \neq \mathbf{0}} w_H(\mathbf{c})$$
其中 $w_H(\mathbf{c})$ 为码字 $\mathbf{c}$ 的汉明重量（非零分量数量）。这一性质仅对线性码成立（非线性码需逐对比较），使最小距离的计算从 $O(2^{2k})$ 降至 $O(2^k)$。

一个最小距离为 $d$ 的线性码能够：
- **检测** $d-1$ 个错误（$t_{detect} = d-1$）
- **纠正** $\lfloor (d-1)/2 \rfloor$ 个错误（$t_{correct} = \lfloor (d-1)/2 \rfloor$）

Singleton界（Singleton Bound）给出 $d \leq n - k + 1$，达到此界的码称为MDS码（Maximum Distance Separable），Reed-Solomon码是最著名的MDS码族。

---

## 关键公式与模型

### Hamming界（球填充界）

对于一个能纠正 $t$ 个错误的 $[n, k, d]$ 二进制线性码，码字数量 $2^k$ 与以每个码字为中心、半径为 $t$ 的Hamming球之积不能超过总空间 $2^n$：
$$2^k \cdot \sum_{i=0}^{t} \binom{n}{i} \leq 2^n$$
整理得：
$$k \leq n - \log_2\!\left[\sum_{i=0}^{t} \binom{n}{i}\right]$$
恰好达到Hamming界的码称为**完美码（Perfect Code）**。已知的二进制完美码仅有：重复码、$[2^r-1, 2^r-r-1, 3]$ Hamming码族（$r \geq 2$）和 $[23, 12, 7]$ Golay码（Golay, 1949）。Golay码由Marcel Golay在1949年发现，能纠正3个错误，被用于1977年发射的旅行者号探测器的图像传输编码。

### GV界（Gilbert-Varshamov界）

对于给定参数 $(n, k, d)$，当满足：
$$2^{n-k} > \sum_{i=0}^{d-2} \binom{n-1}{i}$$
时，存在一个 $[n, k, d]$ 二进制线性码（Gilbert, 1952; Varshamov, 1957）。GV界从可实现性角度给出了编码参数的下界，是随机线性码渐近性能分析的基础。

---

## 实际应用

**案例1：汉明码在计算机内存中的应用（ECC Memory）**

现代服务器的纠错内存（ECC RAM）普遍使用 $[72, 64, 4]$ 扩展Hamming码：将64位数据扩展为72位（增加8位校验位），可纠正1位错误并检测2位错误（SECDED: Single Error Correction, Double Error Detection）。Intel和AMD的服务器平台从1990年代起广泛采用此方案，相比于非ECC内存可将内存错误导致的服务器宕机率降低约99%（Schroeder et al., 2009, USENIX FAST）。

**案例2：Reed-Solomon码在CD/DVD中的应用**

紧凑光盘（CD）采用CIRC（Cross-Interleaved Reed-Solomon Coding）方案，使用两级Reed-Solomon码：C2级为 $[28, 24, 5]$，C1级为 $[32, 28, 5]$，结合交错技术，可纠正长达4000比特的连续突发错误，对应约2.5毫米的划痕（Hoeve et al., 1982, Philips Technical Review）。

**案例3：低密度奇偶校验码（LDPC）中的稀疏校验矩阵**

Robert Gallager于1960年在MIT博士论文中提出LDPC码，其校验矩阵 $H$ 极度稀疏（每行/列仅有少量1），允许使用置信传播（Belief Propagation）算法在近Shannon容量处高效解码。现代5G NR标准（3GPP Release 15, 2018）对数据信道采用LDPC码，码长最高达8448比特，正是线性码稀疏校验矩阵思想的极致应用。

---

## 常见误区

**误区1："线性码的生成矩阵是唯一的"**
这是错误的。同一个线性码 $\mathcal{C}$ 有无穷多个生成矩阵，只要行向量构成 $\mathcal{C}$ 的基即可。两个生成矩阵 $G$ 和 $G'$ 描述同一个码，当且仅当 $G' = AG$，其中 $A$ 是 $k \times k$ 的满秩矩阵。选择系统形式 $G = [I_k \mid P]$ 只是为了实现方便，并非本质唯一性。

**误区2："最小距离越大，码越好"**
最小距离 $d$ 决定纠错能力，但更大的 $d$ 通常意味着更低的码率 $R = k/n$。例如将每位信息重复5次可得 $d=5$，但码率仅 $R=0.2$，信道利用率极低。实际系统需在 $d$（可靠性）与 $R$（效率）之间权衡，Shannon容量定理给出了可同时实现可靠传输与高效率的理论极限。

**误区3："伴随式解码总能找到正确码字"**
伴随式解码基于最大似然假设，即错误模式权重最小。当实际错误数量超过 $\lfloor(d-1)/2\rfloor$ 时，解码器可能将接收向量纠正到一个错误的码字，造成解码错误而非检测到错误。因此在突发错误信道中，需配合交错（Interleaving）技术使用。

**误区4："线性码的零向量不是有效码字"**
恰恰相反，由于线性码构成向量子空间，**零向量必须是码字**（子空间对零向量封闭）。这意味着全0码字 $\mathbf{0} = (0,0,\ldots,0)$ 始终对应某个消息（通常是全零消息），最小非零码字重量即为最小距离，正是利用了零向量必存在这一性质。

---

## 知识关联

**前序概念：差错检测码（Error-Detecting Codes）**
线性码建立在奇偶校验码（Parity Check Code）的基础上，将单一校验位泛化为多个线性无关的校验约束，用矩阵