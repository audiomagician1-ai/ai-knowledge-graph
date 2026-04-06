# Turbo码与LDPC码

## 概述

Turbo码与LDPC码是20世纪末信道编码领域的两项革命性突破，二者均能以迭代译码方式逼近Shannon于1948年在《通信的数学理论》中证明的信道容量极限。Shannon极限指出，对于加性高斯白噪声（AWGN）信道，当码率 $R < C$（信道容量）时，理论上存在误码率任意小的编码方案，但Shannon本人并未给出构造性方法。此后近半个世纪，工程界与理论界一直在追寻能够接近这一极限的实用编码。1993年，法国学者Berrou、Glavieux与Thitimajshima在IEEE国际通信会议（ICC）上发表论文《Near Shannon Limit Error-Correcting Coding and Decoding: Turbo Codes》，正式宣告Turbo码的诞生，在码率 $R=1/2$、帧长65536比特的条件下，仅需 $E_b/N_0 = 0.7\,\mathrm{dB}$ 即可达到误码率 $10^{-5}$，距Shannon极限仅差约0.5 dB，震惊了整个通信领域。而LDPC码（低密度奇偶校验码）虽然由Gallager早在1962年博士论文中提出，却因计算条件限制沉寂三十年，直至1996年MacKay与Neal重新发现并证明其逼近Shannon极限的性能，才重新进入工程实践。

## 核心原理

### Turbo码的编码结构

Turbo码的编码器由两个（或多个）并联的**递归系统卷积码**（Recursive Systematic Convolutional Code, RSCC）和一个**交织器**（Interleaver）组成。以最典型的率 $1/2$ 并行级联结构为例，输入信息比特序列 $\mathbf{u}$ 同时送入分量编码器1（产生校验位 $\mathbf{p}_1$）和经过交织器打乱顺序后的编码器2（产生校验位 $\mathbf{p}_2$）。系统位 $\mathbf{u}$ 直接传输，总码率为 $1/3$（通过删余puncturing可提升至 $1/2$）。

递归系统卷积码的关键在于反馈结构。对于一个生成多项式为 $(1, g_1/g_0)$ 的RSCC，其反馈使编码器具有无限冲激响应，能将输入比特的影响扩散到整个码字，这是获得大自由距离（free distance）的基础。交织器的作用是打破两个分量码之间的相关性，使整个Turbo码的最小汉明距离随帧长 $N$ 的增大而增大，从而获得高编码增益。理论分析表明，交织增益约为 $O(\sqrt{N})$。

### LDPC码的Tanner图表示

LDPC码由一个稀疏奇偶校验矩阵 $H$（维度 $M \times N$，$M < N$）定义，码率 $R = 1 - M/N$。矩阵 $H$ 中每行（校验节点）的非零元素数称为**校验节点度** $d_c$，每列（变量节点）的非零元素数称为**变量节点度** $d_v$。当 $d_v$ 和 $d_c$ 均远小于矩阵维度时，称为低密度。

Gallager在1962年定义的规则LDPC码要求所有行、列的度数分别固定为 $d_c$ 和 $d_v$。1996年MacKay引入非规则LDPC码，允许度数分布不均匀，大幅提升了性能。Tanner于1981年将LDPC码的奇偶校验矩阵映射为**二部图**（Bipartite Graph），即Tanner图：左侧 $N$ 个变量节点（variable nodes）对应码字比特，右侧 $M$ 个校验节点（check nodes）对应奇偶校验方程，$H_{ij}=1$ 时在变量节点 $i$ 与校验节点 $j$ 之间连边。Tanner图中的环（cycle）长度（称为围长 girth）对译码性能至关重要——围长越大，置信传播译码的近似精度越高。

### 迭代置信传播译码

Turbo码与LDPC码共用的核心译码思想是**置信传播**（Belief Propagation, BP），也称消息传递算法。

**Turbo码的BCJR算法**：每个分量码译码器使用Bahl-Cocke-Jelinek-Raviv（BCJR）算法计算各比特的**外部信息**（extrinsic information）——即不依赖本分量码自身系统位直接观测的后验概率比值（对数似然比 LLR）。两个分量译码器交替将各自产生的外部信息 $L_e$ 作为对方的先验信息 $L_a$ 进行迭代：

$$L_e^{(1)}(\hat{u}_k) = \log \frac{\sum_{(s',s): u_k=+1} \alpha_{k-1}(s') \gamma_k(s',s) \beta_k(s)}{\sum_{(s',s): u_k=-1} \alpha_{k-1}(s') \gamma_k(s',s) \beta_k(s)} - L_c y_k - L_a(u_k)$$

其中 $\alpha_k(s)$ 为前向状态度量，$\beta_k(s)$ 为后向状态度量，$\gamma_k(s',s)$ 为分支度量，$L_c = 4R E_b/N_0$ 为信道可靠性因子。

**LDPC码的和积算法**：在Tanner图上，变量节点 $v_i$ 向校验节点 $c_j$ 发送消息 $\mu_{v_i \to c_j}$，校验节点利用来自所有邻居变量节点（除 $v_i$ 外）的消息更新并反馈。校验节点到变量节点的消息更新规则为：

$$\mu_{c_j \to v_i} = 2 \tanh^{-1} \left( \prod_{i' \in \mathcal{N}(c_j) \setminus \{i\}} \tanh\left(\frac{\mu_{v_{i'} \to c_j}}{2}\right) \right)$$

经过若干轮迭代后，各变量节点汇总所有邻居校验节点的消息计算后验LLR并作硬判决。理论上，若Tanner图中无环（即为树形图），BP算法能给出精确的最大后验概率估计；实际有环图中，BP是近似算法，但围长足够大时近似误差可接受。

## 关键公式与性能界

### 密度演化分析

Richardson与Urbanke于2001年发展了**密度演化**（Density Evolution）方法，可精确预测不规则LDPC码在迭代译码下的性能门限。对于二进制删除信道（BEC），密度演化退化为简单的递推方程：

$$p^{(l)} = \varepsilon \cdot \lambda\!\left(1 - \rho(1 - p^{(l-1)})\right)$$

其中 $p^{(l)}$ 是第 $l$ 次迭代后变量节点消息为删除符号的概率，$\varepsilon$ 为删除概率，$\lambda(x) = \sum_i \lambda_i x^{i-1}$ 和 $\rho(x) = \sum_j \rho_j x^{j-1}$ 分别为变量节点与校验节点的度分布多项式（从边角度定义）。设计最优度分布等价于求解使迭代收敛的最大 $\varepsilon$（即容量逼近问题）。

### EXIT图分析

Brink于2001年提出**外部信息转移图**（EXIT Chart）方法，通过追踪互信息 $I_A \to I_E$ 的转移特性分析Turbo/LDPC码的迭代收敛行为。两个分量码译码器的EXIT曲线在图中形成隧道（tunnel），隧道宽度越大收敛越快，隧道在 $I_A = I_E = 1$ 处交汇意味着理论上可达无误差译码。

## 实际应用

Turbo码最早被3GPP采纳于**UMTS/WCDMA（3G）**标准（1999年），后续被LTE（4G）沿用，负责用户数据信道（DL-SCH、UL-SCH）的编码。实现中使用的是码率 $1/3$、约束长度4的并行级联卷积码，配合内部交织器（QPP交织器，由Sun与Takeshita于2005年提出）保证良好的最小距离性质。

LDPC码则被IEEE 802.11n/ac/ax（Wi-Fi）、IEEE 802.16（WiMAX）以及**5G NR**（新空口）采用。5G NR中，LDPC码负责数据信道编码，而极化码（Polar Code）负责控制信道。5G NR的LDPC基矩阵（base graph）有两种：BG1适用于码块大小 $K > 307$ 比特或码率 $R > 0.67$ 的场景，BG2适用于较小码块或低码率场景，通过提升（lifting）操作从基矩阵扩展为实际校验矩阵。

**深空通信**中，NASA喷气推进实验室（JPL）自2003年起在火星探测项目中使用了串行级联Turbo码，并在Consultative Committee for Space Data Systems（CCSDS）标准中规范了多种Turbo码与LDPC码的参数配置，支持从数百比特到数万比特的帧长范围。

## 常见误区

**误区1：迭代次数越多性能越好**。实际上，Turbo码与LDPC码均存在"误码平台"（error floor）现象：在低信噪比区域，迭代次数增加显著降低误码率；但在高信噪比区域，性能曲线趋于平坦。这一现象与码的最小距离分布（weight enumerator）和Tanner图中的"陷阱集"（trapping set）密切相关。增加迭代次数不能消除误码平台，需通过优化码的最小距离或消除有害陷阱集来解决。

**误区2：LDPC码总优于Turbo码**。这一判断过于简化。在短码长（$N < 1000$）条件下，精心设计的Turbo码（如3GPP标准码）往往优于同等码率的LDPC码，因为LDPC码的密度演化设计在短码中有限长效应（finite-length effects）明显。在长码长（$N > 10000$）条件下，优化度分布的LDPC码可在瀑布区（waterfall region）逼近Shannon极限至0.1 dB以内。

**误区3：外部信息与系统位LLR可以叠加**。Turbo码迭代中必须严格区分外部信息（extrinsic LLR）和系统信道观测（channel LLR）。若将同一信息重复计入，等效于过度计数，导致迭代发散（double-counting问题）。正确做法是分量译码器输出的总后验LLR减去自身输入的先验LLR，才得到可传递给对方的外部信息。

**误区4：极化码已经取代Turbo码与LDPC码**。5G NR采用极化码仅针对控制信道（因为控制信道码块较短，极化码在短码CRC辅助列表译码下表现优秀），数据信道仍使用LDPC码。三类编码各有其适用场景，并非简单替代关系。

## 知识关联

**与卷积码的关系**：Turbo码的每个分量编码器本质上是约束长度 $\nu$（通常为3或4）的递归系统卷积码，BCJR算法是Viterbi算法的软输出推广。理解Viterbi算法的网格图（trellis）结构是理解BCJR前向-后向递推的前提。

**与Shannon信息论的关系**：LDPC码与Turbo码从不同角度"构造性地"逼近Shannon于1948年证明的信道编码定理。密度演化方法从理论上证明了特定度分布的LDPC码序列在码长趋于无穷时能达到BEC的信道容量（Richardson & Urbanke, 2001），而Turbo码的性能分析则借助重量枚举函数（weight enumerating function）与联合界（union bound）。

**与极化码的关系**：Arıkan于2009年提出的极化码（Polar Code）是第一类被严格证明在任意对称二进制无记忆信道上渐近达到信道容量的构造性编码方案，与Turbo码、LDPC码共同构成现代信道编码的三大支柱。极化码的逐次消除（SC）译码复杂度为 $O(N \log N)$，而LDPC码的BP译码复杂度为 $O(N \cdot d_v \cdot I_{max})$（$I