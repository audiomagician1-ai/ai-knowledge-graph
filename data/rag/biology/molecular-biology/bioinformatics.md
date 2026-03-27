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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 生物信息学

## 概述

生物信息学（Bioinformatics）是将计算机科学、统计学与分子生物学相结合的交叉学科，专门处理DNA序列、RNA转录本和蛋白质结构等大规模生物数据。其核心任务包括三项：序列比对（sequence alignment）、基因注释（gene annotation）和生物数据库的构建与查询。与一般数据科学不同，生物信息学的分析对象具有特殊的生物意义——4个碱基字母或20种氨基酸组成的线性序列承载着生命遗传信息。

该领域的奠基性工作可追溯至1970年，Smith–Waterman局部序列比对算法发表，以及1981年同名论文正式提出的动态规划矩阵方案。1990年美国国立卫生研究院（NIH）启动人类基因组计划（HGP），产生的海量测序数据直接推动了GenBank、EMBL和DDBJ三大国际核酸序列数据库的协作共建，使生物信息学从辅助工具演变为独立的核心学科。如今，仅GenBank每18个月就翻一番的数据量，已超过5000亿个碱基对，任何不依赖计算方法的生物学分析都无法处理这一量级的数据。

## 核心原理

### 序列比对与打分矩阵

序列比对的数学基础是**动态规划**，其全局比对由Needleman–Wunsch算法（1970）实现，局部比对由Smith–Waterman算法实现。核心计算公式为递推矩阵：

$$H(i,j) = \max\begin{cases} H(i-1,j-1) + s(a_i, b_j) \\ H(i-1,j) - d \\ H(i,j-1) - d \\ 0 \end{cases}$$

其中 $s(a_i, b_j)$ 是替换打分矩阵中两个残基之间的得分，$d$ 是间隙罚分（gap penalty）。对于蛋白质序列，常用的替换矩阵是**BLOSUM62**，其数值由250个进化距离在62%以内的蛋白质家族统计得出，矩阵中色氨酸（W）与色氨酸的自比对得分为+11，而与半胱氨酸（C）的替换得分为-3，体现了氨基酸物理化学性质的相似程度。

实际高通量比对中，精确动态规划算法因O(mn)时间复杂度代价过高，BLAST（Basic Local Alignment Search Tool）通过"词查找（word hit）+ 延伸"的启发式策略将速度提升了约50倍，其E值（Expect value）表示在随机数据库中期望出现相同或更高得分比对的次数，E值 < 0.001通常被视为显著匹配的统计阈值。

### 基因注释

基因注释分为**结构注释**和**功能注释**两个层次。结构注释识别基因组序列中编码区（CDS）、启动子、剪接位点等元件，常用工具包括Augustus和GenScan，它们基于隐马尔可夫模型（HMM）预测外显子–内含子边界；功能注释则将预测出的基因产物与已知蛋白质数据库（如UniProt/Swiss-Prot，含超过568,000条人工审核条目）进行比对，推断其分子功能和参与的生物学过程（GO terms）。

基因注释质量由"证据权重"决定：经过实验验证的mRNA和EST序列比同源性预测更可靠，而同源性预测又比纯粹的从头（ab initio）预测更准确。人类参考基因组GRCh38注释显示约20,000–25,000个蛋白质编码基因，但仅其中约14,000个拥有充分的实验证据支持，其余均依赖计算预测。

### 生物数据库体系

生物数据库按数据类型分为核酸数据库（GenBank/EMBL/DDBJ）、蛋白质序列数据库（UniProt）、蛋白质结构数据库（PDB，截至2024年收录超过210,000个结构）和功能/通路数据库（KEGG、Reactome）。它们通过交叉引用（cross-reference）形成网络：一个UniProt条目可同时链接到PDB三维结构、KEGG通路编号、OMIM疾病关联和对应的Ensembl基因ID。

NCBI的RefSeq数据库与GenBank的区别在于：GenBank收录所有提交的原始序列（含冗余），而RefSeq仅保留非冗余、经过人工审核的参考序列，每条记录以NM_（mRNA）、NP_（蛋白质）或NC_（染色体）为前缀，是注释流程中的标准参照源。

## 实际应用

**新冠病毒溯源与变异追踪**：SARS-CoV-2基因组全长约29,900个碱基对，2020年1月11日中国科学家将首个完整序列上传至GISAID数据库后，全球研究者立即通过多序列比对（MUSCLE、MAFFT工具）构建系统发育树，在数周内确认了Omicron变体S蛋白上超过32个突变位点，这一速度在没有生物信息学方法的时代需要数年才能完成。

**癌症基因组学**：TCGA（The Cancer Genome Atlas）项目对33种癌症类型的超过11,000例样本进行了WGS/WES分析，通过变异注释流程（Variant Annotation Pipeline）将体细胞突变位点与ClinVar数据库比对，识别出如TP53、KRAS、EGFR等驱动突变基因。这些数据直接支撑了EGFR突变阳性肺腺癌患者使用厄洛替尼靶向治疗的临床决策。

**蛋白质功能预测**：当一个基因产物序列无法在Swiss-Prot中找到同源蛋白时，可用InterProScan扫描其包含的结构域（domain）和功能位点（motif），如识别出Pfam数据库中PF00069（蛋白激酶催化域），即可推断其可能具有激酶功能。

## 常见误区

**误区一：E值越小越好，0就是完美匹配**。许多初学者认为BLAST搜索结果E值为0意味着序列完全相同。实际上，E值为0只代表该匹配得分极高以至于数值超出浮点数表示范围（通常得分>200 bits），而非两序列百分之百一致——即使99%的序列相似度也可能产生E=0。比较序列相似度必须同时查看"Percent Identity"列。

**误区二：序列相似 = 功能相同**。两个蛋白质序列具有40%以上的氨基酸同一性（identity）通常被视为具有相同折叠和相近功能的安全阈值，但低于30%的区域进入"twilight zone"，此时序列相似性不再可靠地预测功能。更关键的是，即便整体序列高度相似，活性位点处的单个残基替换也可能彻底改变催化功能，如酶活性位点的Ser→Ala突变可导致丝氨酸蛋白酶完全失活。

**误区三：数据库序列均经过实验验证**。UniProt分为Swiss-Prot（人工审核，~568,000条）和TrEMBL（自动注释，超过2.5亿条）两个子库。TrEMBL条目的注释大多由计算方法自动转移，存在"注释传播错误"——如果一个错误注释的原始序列被大量引用，该错误可能在整个数据库中扩散传播，导致下游分析结论失效。使用数据库时应优先引用Swiss-Prot中带"Reviewed"标签的条目。

## 知识关联

生物信息学直接依赖**基因组学**提供的参考基因组序列和**蛋白质组学**提供的质谱数据作为分析输入。基因组学提供了染色体物理坐标系统（如GRCh38的坐标体系），使变异注释能精确定位到外显子第几位碱基；蛋白质组学的LC-MS/MS数据则需要比对至蛋白质序列数据库（如UniProt）才能完成肽段鉴定，即谱图–序列匹配过程依赖Mascot或MaxQuant等生物信息学工具。

学习生物信息学需要掌握Linux命令行操作（因为BLAST、BWA、GATK等工具均为命令行程序）以及至少一种脚本语言（Python的Biopython库或R的Bioconductor包），这些是使用主流分析工具的实际技术门槛，而非可选能力。对动态规划算法原理的理解有助于判断比对参数（如gap open penalty与gap extension penalty的差异设置）对特定分析场景的影响。