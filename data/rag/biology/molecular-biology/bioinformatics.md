---
id: "bioinformatics"
concept: "生物信息学"
domain: "biology"
subdomain: "molecular-biology"
subdomain_name: "分子生物学"
difficulty: 4
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 37.1
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 0.4
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
---
# 生物信息学

## 概述

生物信息学（Bioinformatics）是一门融合计算机科学、统计学与分子生物学的交叉学科，专门处理、分析和解读大规模生物序列数据。其核心任务包括DNA/RNA序列比对、基因功能注释、蛋白质结构预测，以及维护和查询公共生物数据库。生物信息学不仅是分析工具的集合，更是将海量测序数据转化为生物学知识的方法论体系。

该学科的形成可追溯至1970年代。1970年，Margaret Dayhoff编制了第一部蛋白质序列数据库《蛋白质序列与结构图集》（Atlas of Protein Sequence and Structure），这标志着生物信息学数据库研究的起点。1981年，Smith和Waterman发表了局部序列比对算法（Smith-Waterman算法），为后续所有序列比对工具奠定了数学基础。随着人类基因组计划（Human Genome Project）于2003年完成，每日产生的测序数据呈指数级增长，生物信息学工具成为不可或缺的分析手段。

理解生物信息学对于现代分子生物学研究至关重要，原因在于高通量测序（NGS）每次实验可产生数十亿条短读段（reads），人工逐条分析完全不可行。例如，Illumina NovaSeq 6000单次运行可生成超过6000亿碱基对的数据，必须依靠自动化比对、注释流程才能提取有意义的生物学信息。

---

## 核心原理

### 序列比对：全局比对与局部比对

序列比对的目标是找出两条或多条序列之间的相似区域，以推断同源性或功能相似性。**全局比对**由Needleman-Wunsch算法（1970年）实现，使用动态规划将两条序列从头到尾强制对齐，得分矩阵公式为：

$$F(i, j) = \max\begin{cases}F(i-1,j-1) + s(x_i, y_j)\\F(i-1,j) + d\\F(i,j-1) + d\end{cases}$$

其中 $s(x_i, y_j)$ 为替换得分（来自PAM或BLOSUM矩阵），$d$ 为空位罚分（gap penalty）。**局部比对**则由Smith-Waterman算法实现，在上述矩阵中额外引入 $\max(0, ...)$ 条件，允许矩阵值归零，从而找出最优局部匹配区域。BLAST（Basic Local Alignment Search Tool）是这两类算法的快速启发式实现，通过预构建k-mer索引将搜索速度提升至Smith-Waterman的50倍以上，但以损失部分灵敏度为代价。

BLOSUM62替换矩阵是最常用的氨基酸替换得分矩阵，由1992年Henikoff夫妇统计62%序列一致性的保守蛋白质区块（blocks）而得，矩阵中对角线值（如Trp=11）反映氨基酸自我匹配的保守程度，负值（如Trp-Gly=-3）表示该替换在进化中极少发生。

### 基因注释：从序列到功能

基因注释分为**结构注释**和**功能注释**两个层次。结构注释确定基因的位置、外显子-内含子边界、转录起始位点等，工具如Augustus通过隐马尔可夫模型（HMM）训练物种特异性参数，人类基因组注释准确率可达90%以上。功能注释则将预测的基因序列与已知功能数据库比对，常用数据库包括UniProt/Swiss-Prot（手动审核注释，包含约570,000条高质量蛋白质条目）和Gene Ontology（GO）数据库。GO数据库将基因功能分为三大本体：分子功能（Molecular Function）、生物过程（Biological Process）和细胞组件（Cellular Component），每个GO术语拥有唯一的7位数字编号（如GO:0003677代表DNA结合活性）。

对于真核生物基因组，重复序列屏蔽（repeat masking）是注释前必须完成的步骤——人类基因组中约45%为转座元件，若不屏蔽将严重干扰比对结果，RepeatMasker是最常用的屏蔽工具。

### 生物数据库：存储、格式与查询

主要公共生物数据库包括：
- **GenBank/INSDC**：核酸序列存储，数据库条目采用FASTA或GenBank格式，截至2024年已收录超过2亿条序列。
- **PDB（蛋白质数据库）**：存储三维蛋白质结构，使用.pdb格式，每个条目包含原子坐标（X、Y、Z）和温度因子（B-factor）。
- **Ensembl**：整合基因组注释、变异数据和物种间同源信息，支持REST API查询，提供BioMart工具进行批量数据导出。

数据库中的序列通常以FASTA格式存储，格式为以`>`开头的标题行加序列行；变异数据则用VCF（Variant Call Format）格式记录，每行包含染色体号、位置、参考碱基、替代碱基及质量得分。

---

## 实际应用

**癌症基因组分析**：通过将肿瘤样本测序数据与参考基因组（如GRCh38）比对，使用工具如BWA-MEM进行短读段比对，GATK的HaplotypeCaller检测体细胞突变（SNV和indel）。已鉴定的驱动基因突变（如EGFR L858R点突变）直接指导临床靶向用药方案。

**宏基因组学中的物种鉴定**：无需培养微生物，直接提取环境样本DNA测序，使用Kraken2软件通过k-mer匹配将数百万条reads在数分钟内分类到物种级别，分类数据库包含超过15,000种微生物参考基因组。人类肠道微生物组项目（HMP）的数据分析完全依赖此类生物信息学流程。

**蛋白质功能预测**：通过PSI-BLAST对新发现蛋白质进行迭代搜索，构建位点特异性评分矩阵（PSSM），在远程同源（序列一致性低至20%-30%的"twilight zone"区间）中仍能检测功能相似的蛋白质。AlphaFold2（2021年发布）利用多序列比对（MSA）和注意力机制，将蛋白质结构预测精度提升至接近实验水平（中位TM-score > 0.9）。

---

## 常见误区

**误区一：E-value越小，生物学意义一定越大。**
BLAST搜索结果中的E-value（期望值）衡量的是在随机数据库中偶然得到该比对得分的期望次数。E-value < 1e-5通常被视为可信，但E-value极小（如1e-100）的比对结果若对应的是高度保守的蛋白质结构域（如ATP结合口袋），其功能信息价值并不必然高于中等E-value（如1e-10）的结果。E-value受数据库大小影响——同一比对在大数据库中的E-value会比小数据库中更大，不同数据库的E-value不可直接横向比较。

**误区二：序列相似即功能相同（同源性与相似性混淆）。**
序列相似性（similarity）是可测量的数值，而同源性（homology）是进化关系的定性判断——两序列要么同源要么不同源，不存在"80%同源"的说法。更重要的是，即使序列一致性高达70%，若关键活性位点氨基酸发生突变，蛋白质功能可能完全不同。例如丝氨酸蛋白酶与苏氨酸蛋白酶活性位点残差的细微差异足以改变催化机制。

**误区三：参考基因组代表该物种所有个体。**
以GRCh38为代表的人类参考基因组实际上是多个个体序列的拼接，其中大量基因组区域来自少数几名供体。人群结构变异（structural variants）中约有15%-20%不存在于参考基因组中，这意味着以参考基因组为中心的分析会系统性地低估群体遗传多样性，对非欧裔人群的分析偏差尤为突出。

---

## 知识关联

生物信息学的学习建立在**基因组学**与**蛋白质组学**的概念基础之上。基因组学提供了理解参考基因组构建、基因结构（外显子、内含子、UTR）和变异类型（SNP、indel、CNV）的背景知识，这些知识直接对应到生物信息学中的变异检测流程和基因注释逻辑。蛋白质组学的质谱数据分析（如Mascot、MaxQuant工具）本身就是生物信息学的重要应用分支，蛋白质序列数据库（如UniProt）是蛋白质功能注释的直接资源。

掌握生物信息学的关键指标是能够从原始FASTQ文件出发，完整执行一条分析流程：质控（FastQC）→ 比对（BWA/STAR）→ 后处理（SAMtools）→ 变异检测（GATK）→ 注释（ANNOVAR/SnpEff），并能根据QC报告中的具体指标（如Phred质量值 < 20的碱基比例、GC含量偏差）判断数据质量问题的来源。
