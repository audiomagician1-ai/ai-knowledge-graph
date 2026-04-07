---
id: "phylogenetics"
concept: "系统发育"
domain: "biology"
subdomain: "evolution"
subdomain_name: "进化生物学"
difficulty: 4
is_milestone: false
tags: ["方法"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 系统发育

## 概述

系统发育（phylogeny）是研究生物物种或基因之间进化关系的科学，其核心成果是"系统发育树"（phylogenetic tree），一种用分支图表示物种或序列共同祖先关系的拓扑结构。系统发育分析不仅回答"哪两个物种亲缘关系更近"，还能定量估算分歧时间和进化速率，从而重建数亿年前的生命历史。

系统发育学的现代奠基人是德国昆虫学家威利·亨尼希（Willi Hennig），他于1950年出版《系统发育系统学》（*Grundzüge einer Theorie der Phylogenetischen Systematik*），提出以"共同衍征"（synapomorphy）——即来自共同祖先的衍生性状——作为划分自然类群的唯一依据，由此建立了支序系统学（cladistics）框架。1960年代以后，DNA测序技术的出现使系统发育分析从形态学特征转向核酸和蛋白质序列，诞生了分子系统学（molecular phylogenetics）。

分子系统发育分析的实际意义远超学术分类。病毒溯源（如2019年SARS-CoV-2祖先追踪至蝙蝠冠状病毒）、法医DNA鉴定、濒危物种保护单元的划定，以及抗生素耐药性的传播路径重建，都依赖系统发育树提供结构化的进化证据。

---

## 核心原理

### 序列比对与信息位点

系统发育分析的第一步是多序列比对（multiple sequence alignment, MSA），常用工具为MUSCLE或MAFFT。比对后，并非所有位点都含有进化信息——**信息位点**（parsimony-informative site）要求该位点至少有两种碱基状态，且每种状态出现在至少两条序列中。以4条序列为例，若某列碱基为A、A、G、G，则它支持两种不同的树拓扑，属于信息位点；若为A、A、A、G，则无论树形如何，该位点的解释成本相同，不具备区分能力。信息位点的数量和质量直接影响建树结果的可靠性。

### 建树方法：距离法、最简约法与最大似然法

**距离法**（distance-based method）先将序列相似度转换为进化距离矩阵，再用邻接法（Neighbor-Joining, NJ）聚类成树。NJ算法在1987年由斋藤成也（Nei & Saitou）提出，时间复杂度为O(n³)，适合大数据集的快速分析。

**最大简约法**（Maximum Parsimony, MP）寻找需要最少进化变化步骤的树拓扑，本质上是离散优化问题，对于n条序列存在 (2n-3)!! 种可能的有根二叉树，当n>10时穷举不可行，需启发式搜索。

**最大似然法**（Maximum Likelihood, ML）是目前最主流的方法，代表软件为RAxML和IQ-TREE。ML在给定替换模型下，最大化观测序列数据出现的概率：

$$\mathcal{L}(\mathcal{T}, \theta \mid D) = P(D \mid \mathcal{T}, \theta)$$

其中 $\mathcal{T}$ 为树拓扑及枝长，$\theta$ 为替换模型参数，$D$ 为比对序列矩阵。GTR+Γ模型（广义时间可逆模型+位点速率Gamma分布）是核苷酸分析中最常用的替换模型，共有6个替换率参数和4个碱基频率参数。

**贝叶斯推断法**（Bayesian Inference, BI）通过MCMC采样后验概率分布，软件MrBayes和BEAST广泛用于时间树（time-calibrated tree）的构建，可将化石校准点整合进分析，直接输出分歧时间的概率分布。

### 树的可靠性评估：Bootstrap与后验概率

Bootstrap重采样（自举检验）由Felsenstein于1985年引入系统发育领域：对原始比对数据有放回地随机抽取等长列，重复建树100或1000次，统计目标分支出现的频率作为支持值。通常认为Bootstrap值≥70%的节点具有一定可信度，≥95%为强支持。贝叶斯后验概率（posterior probability, PP）≥0.95通常对应更高的统计置信度，但两者不可直接数值等价比较。

---

## 实际应用

**病毒进化与溯源**：2020年，张永振团队将SARS-CoV-2与RaTG13（云南蝙蝠冠状病毒）的全基因组系统发育分析显示两者序列相似度达96.2%，据ML建树估算其共同祖先约在40-70年前分歧。这一结论直接为疫情溯源提供了分子证据框架。

**物种分类修订**：传统形态学将大熊猫（*Ailuropoda melanoleuca*）长期归入熊猫科，20世纪80年代线粒体DNA的系统发育分析将其明确归入熊科（Ursidae），与其最近亲眼镜熊约在1800万年前分歧，彻底解决了长达百年的分类争议。

**水平基因转移（HGT）检测**：在细菌和古菌中，不同基因的系统发育树拓扑往往彼此矛盾，反映了基因通过质粒或噬菌体在非亲缘物种间转移的历史。通过比较16S rRNA树与抗性基因树的拓扑冲突，可精确定位耐药基因的转移事件。

---

## 常见误区

**误区一：树的根代表"最原始"的物种**。系统发育树的根仅表示所有内群（ingroup）的最近共同祖先（MRCA），根的位置需要外群（outgroup）来确定，并不意味着靠近根的物种在其当代形式上更"原始"。现存的变形虫和现存的人类在各自谱系上经历了同样长时间的进化，都不是"更原始"的生物。

**误区二：Bootstrap值高等于树的拓扑正确**。Bootstrap值反映数据对特定分支的支持强度，但若所用替换模型选择错误，或比对质量低，即使Bootstrap=100%的节点也可能代表错误的进化关系（模型错误导致的系统误差，如长枝吸引现象LBA）。长枝吸引（Long Branch Attraction）是MP法中两条进化速率高的枝因平行突变而被错误聚类的典型伪像。

**误区三：分子钟假设普遍适用**。严格分子钟假设所有谱系进化速率相同，但不同物种代时、种群大小、DNA修复效率差异导致速率高度异质。现代分析普遍采用松弛分子钟模型（relaxed molecular clock），允许各枝速率独立变化，否则强行使用严格分子钟会导致分歧时间估算严重偏差。

---

## 知识关联

系统发育分析直接依赖**分子进化**提供的理论工具：核苷酸替换模型（如Jukes-Cantor、Kimura 2-parameter）定义了序列距离的计算方式，选择压力（dN/dS比值）分析则帮助识别功能保守区域，这些区域在建树时往往提供更稳定的系统发育信号。没有替换模型，序列比较就无法转化为进化距离。

在系统发育框架之上，**人类进化**研究是其最重要的应用方向之一。线粒体DNA和Y染色体单倍群系统发育树被用于追踪现代人走出非洲的迁徙路线，古DNA（如尼安德特人基因组，2010年由帕博团队发表于*Science*）与现代人的系统发育整合分析，揭示了智人与已灭绝古人类之间的基因流事件。系统发育分析为理解人类起源与种群结构提供了不可替代的时间与拓扑坐标。