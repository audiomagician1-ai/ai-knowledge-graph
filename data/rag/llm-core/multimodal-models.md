# 多模态大模型

## 概述

多模态大模型（Multimodal Large Language Model，MLLM）是指能够在单一统一架构中同时处理文本、图像、音频、视频等两种或以上异质信息模态的大规模神经网络。其本质挑战在于：不同模态的原始信号具有根本不同的统计结构——文本是离散符号序列，图像是连续像素网格，音频是时域波形——如何将这些异质信号投影到同一语义表示空间并实现有效交叉推理，是多模态大模型的核心技术问题。

2021年OpenAI发布的CLIP（Contrastive Language-Image Pre-training）奠定了现代多模态大模型的基础范式（Radford et al., 2021）。CLIP使用4亿对从互联网抓取的图文对进行对比学习预训练，其核心贡献是证明视觉语义与语言语义可以在同一$d=512$维或$d=768$维向量空间中对齐，且这种对齐具有跨任务的零样本迁移能力。2023年，GPT-4V的闭源发布与LLaVA系列的开源发布共同推动多模态大模型进入规模化应用阶段；同年11月Google发布Gemini 1.0，首次在单一Transformer架构中原生支持文本、图像、音频、视频四种模态的联合训练，而非依赖外挂编码器的拼接方案（Team et al., 2023）。

现实世界的信息天然是多模态的：医学CT影像须结合病历文字才能诊断，工业视觉质检需要图文对照知识库，机器人操控需要融合摄像头语义与力觉反馈。单纯文本大模型在这些场景下存在信息输入通道的根本缺失，多模态架构填补了AI系统与物理世界之间的感知鸿沟。

## 核心原理

### 视觉编码器：从CNN到Vision Transformer

早期多模态系统使用卷积神经网络（ResNet-50/101）提取图像特征，输出空间特征图后展平为固定长度向量。这种方式丢失了精确的位置信息，且无法处理可变分辨率输入。

现代主流方案基于Vision Transformer（ViT）的Patch Embedding机制（Dosovitskiy et al., 2021）：将$H \times W$的输入图像划分为$N = \frac{H \cdot W}{P^2}$个大小为$P \times P$像素的非重叠图块，每个图块线性投影为$d$维嵌入向量，加上可学习位置编码后送入标准Transformer编码器。LLaVA-1.5采用CLIP的ViT-L/14@336px，将$336 \times 336$图像编码为$\left(\frac{336}{14}\right)^2 = 576$个视觉token，每个token携带1024维特征（Liu et al., 2023）。

$$N_{tokens} = \left\lfloor \frac{H}{P} \right\rfloor \times \left\lfloor \frac{W}{P} \right\rfloor$$

视觉token数量直接决定细粒度理解能力与推理显存开销之间的权衡：InternVL2采用动态分辨率策略，将高分辨率图像分割为多个子图分别编码再拼接，在OCR和图表理解任务上显著优于固定分辨率方案。

### 跨模态对齐：投影层的三种设计范式

视觉编码器的输出维度（如CLIP ViT-L输出1024维）与语言模型词嵌入维度（如LLaMA-2-7B的4096维、LLaMA-3-70B的8192维）之间存在语义空间不匹配，必须通过投影层（Projection Layer）弥合。

**线性投影**：单层矩阵变换 $\mathbf{z}_{lang} = \mathbf{W} \cdot \mathbf{z}_{vis} + \mathbf{b}$，参数量仅为 $d_{vis} \times d_{lang}$（约400万参数）。LLaVA-1.0采用此方案，实现简单但表达能力受限，难以处理视觉特征的非线性分布。

**MLP投影**：两层带GELU激活的全连接网络：
$$\mathbf{z}_{lang} = \mathbf{W}_2 \cdot \text{GELU}(\mathbf{W}_1 \cdot \mathbf{z}_{vis} + \mathbf{b}_1) + \mathbf{b}_2$$
LLaVA-1.5将线性投影换为MLP后，在MMBench基准上从36.2%提升至68.2%，提升幅度超过30个百分点，证明投影层的非线性表达能力对视觉语言对齐质量有决定性影响。

**Q-Former（Query Transformer）**：BLIP-2提出的交叉注意力查询机制（Li et al., 2023）。定义32个可学习的查询向量 $\mathbf{Q} \in \mathbb{R}^{32 \times d_q}$，通过交叉注意力从视觉特征序列中动态聚合信息：
$$\text{Attention}(\mathbf{Q}, \mathbf{K}_{vis}, \mathbf{V}_{vis}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}_{vis}^T}{\sqrt{d_k}}\right)\mathbf{V}_{vis}$$
Q-Former将576个视觉token压缩为固定32个输出token，大幅降低语言模型侧的计算开销，但固定token数可能丢失空间细节，在需要精确定位的任务（如Visual Grounding）上表现弱于MLP方案。

### 训练流程：两阶段或三阶段策略

多模态大模型的训练必须分阶段以防止灾难性遗忘（Catastrophic Forgetting）破坏预训练语言能力。

**第一阶段（模态对齐预训练）**：冻结视觉编码器与语言模型的全部参数，仅训练投影层。使用规模在500K–5M量级的图文描述对（如LAION-CC-SBU-595K），损失函数为标准语言模型的自回归交叉熵：
$$\mathcal{L}_{align} = -\sum_{t=1}^{T} \log P_\theta(x_t \mid x_{<t}, \mathbf{z}_{vis})$$
此阶段目标是让投影层将视觉特征"翻译"为语言模型已有词汇空间中的近邻表示，通常需要数小时至数天在8×A100上完成。

**第二阶段（视觉指令微调）**：解冻投影层与语言模型（视觉编码器通常仍冻结），使用高质量的视觉问答指令数据（如LLaVA-Instruct-665K）进行端到端微调，使模型学会遵循多轮对话中的视觉推理指令。

**第三阶段（RLHF对齐，可选）**：部分商业模型（如GPT-4V、Gemini Ultra）额外进行基于人类反馈的强化学习，针对视觉安全拒绝、幻觉抑制进行专项对齐，此阶段在公开文献中披露细节极少。

### 对比学习目标：CLIP的InfoNCE损失

CLIP训练使用InfoNCE（Info Noise-Contrastive Estimation）对比损失，对于批量大小$N$的图文对，将匹配的图文对视为正样本，其余$N-1$对视为负样本：

$$\mathcal{L}_{CLIP} = -\frac{1}{2N}\sum_{i=1}^{N}\left[\log\frac{\exp(\text{sim}(\mathbf{z}_i^I, \mathbf{z}_i^T)/\tau)}{\sum_{j=1}^{N}\exp(\text{sim}(\mathbf{z}_i^I, \mathbf{z}_j^T)/\tau)} + \log\frac{\exp(\text{sim}(\mathbf{z}_i^T, \mathbf{z}_i^I)/\tau)}{\sum_{j=1}^{N}\exp(\text{sim}(\mathbf{z}_j^I, \mathbf{z}_i^T)/\tau)}\right]$$

其中$\tau$为可学习温度参数（CLIP论文初始值0.07），$\text{sim}(\cdot)$为余弦相似度。批量大小对CLIP训练极为关键——原论文使用批量大小32768，远大于常规分类训练的256，以确保每个样本有足够多的负样本进行区分。

## 关键评测基准与能力维度

多模态大模型的能力需通过专项基准分维度评测，而非单一总分：

**感知理解类**：MMBench（覆盖30个视觉能力维度，总计3217道选择题）评测基础视觉感知；POPE（Polling-based Object Probing Evaluation）专项评测物体存在性幻觉，使用Adversarial/Popular/Random三种采样策略，模型在Adversarial子集上的F1分数揭示其幻觉脆弱性。

**知识推理类**：ScienceQA（科学多选题，12726道，覆盖自然科学/语言/社会三大领域）测试科学知识的多模态推理能力；MathVista专项评测数学图形理解，GPT-4V在该基准上早期版本仅达49.9%，远低于人类的60.3%。

**细粒度理解类**：TextVQA（从图像中识别文字后回答问题）、DocVQA（文档图像理解）、ChartQA（图表数据提取与推理）三类基准评测OCR与结构化视觉信息理解，InternVL2-26B在DocVQA上达到91.6%，接近人类水准。

**视频理解类**：MVBench（含20种时序理解任务）、Video-MME（含6大类、256个视频的综合评测）评测模型对时序依赖的多帧理解能力。

## 实际应用案例

**案例1：医学影像辅助诊断**  
LLaVA-Med（Li et al., 2024）基于LLaVA框架，使用从PubMed抓取的60万生物医学图文对进行领域自适应微调，可回答"图中X光片显示的是什么类型的骨折？"此类需要专科知识与视觉定位的复合问题。实验显示，LLaVA-Med在VQA-RAD（放射学视觉问答数据集）上达到73.6%的准确率，在开放式问题上超越此前的专用医疗VQA模型。

**案例2：工业视觉质检**  
例如，将产品缺陷图像与质检标准文档同时输入多模态模型，模型需对照文档描述定位图像中的异常区域并输出结构化缺陷报告。与传统计算机视觉流水线相比，多模态大模型无需针对每种缺陷类型单独训练分类器，可通过自然语言指令动态调整检测策略，使缺陷类型扩展的工程成本从数周降低至数小时。

**案例3：多模态RAG（检索增强生成）**  
将图像与文本统一编码为向量，存储于多模态向量数据库（如使用CLIP嵌入索引的Qdrant实例），查询时以文本或图像为检索键召回相关多模态文档，再由多模态大模型综合生成答案。这一架构在企业知识库问答场景中实现了对PDF、图表、产品手册等混合格式内容的统一检索与理解。

## 常见误区

**误区1：视觉token越多，理解能力越强**  
视觉token数量与理解质量之间并非线性正相关。过多视觉token会占据语言模型的上下文窗口（如576个视觉token在4096 token窗口中占比14%），压缩了文本推理空间，并导致推理延迟线性增加。InternVL2的动态分辨率策略与MiniCPM-V的自适应切片机制均致力于在token数量与图像细节之间寻找Pareto最优点，而非一味提升token数。

**误区2：多模态大模型不会产生幻觉**  
视觉幻觉（Visual Hallucination）是多模态大模型特有的系统性缺陷，且比纯文本幻觉更难检测。模型可能自信地描述图中并不存在的物体（Object Hallucination），这是因为语言模型先验（"草地上通常有树"）强烈干扰了视觉编码器的实际输出。POPE基准的设计初衷正是量化这一现象——当被问到"图中有没有X？"时，部分模型在高频物体上的误报率超过20%。

**误区3：冻结视觉编码器不影响性能**  
早期研究为节省计算成本而固定CLIP视觉编码器权重