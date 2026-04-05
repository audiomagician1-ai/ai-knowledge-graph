---
id: "gene-editing"
concept: "基因编辑"
domain: "biology"
subdomain: "molecular-biology"
subdomain_name: "分子生物学"
difficulty: 4
is_milestone: false
tags: ["前沿"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 基因编辑

## 概述

基因编辑（Gene Editing）是指对生物体基因组的特定位点进行精准的碱基增添、删除或替换操作的技术。与早期的随机诱变育种不同，现代基因编辑可以在数十亿碱基对的基因组中精确定位并修改单个核苷酸。2012年，Jennifer Doudna 和 Emmanuelle Charpentier 在《Science》杂志发表论文，证明了 CRISPR-Cas9 系统可作为可编程的基因组编辑工具，两人因此于2020年获得诺贝尔化学奖。

CRISPR-Cas9 技术革命性地将基因编辑成本从早期锌指核酸酶（ZFN）时代的数万美元压缩至数百美元，所需时间从数月缩短至数周。这种效率的跃升使全球几乎所有分子生物学实验室都能开展基因编辑实验，推动了从农业育种到遗传病治疗的广泛应用。

## 核心原理

### CRISPR-Cas9 的分子机制

CRISPR（Clustered Regularly Interspaced Short Palindromic Repeats，成簇规律间隔短回文重复序列）最初发现于细菌的适应性免疫系统。Cas9 是一种来源于化脓性链球菌（*Streptococcus pyogenes*）的 RNA 引导核酸内切酶，其分子量约为158 kDa。

整个系统的工作依赖一条**向导RNA（sgRNA）**，其结构分为两部分：
- **crRNA 区域**：约20个核苷酸，与靶DNA互补配对，决定切割位点的特异性。
- **tracrRNA 区域**：形成发夹结构，与 Cas9 蛋白结合，维持酶的活性构象。

Cas9 识别靶位点还需要一个关键的**PAM序列（Protospacer Adjacent Motif）**，对于 SpCas9，PAM 序列为 5'-NGG-3'，位于靶序列的3'端。切割发生在 PAM 上游第3个碱基处，产生平末端双链断裂（DSB）。

### 两种主要修复途径与编辑结果

细胞修复 DSB 的方式直接决定了编辑结果：

**1. 非同源末端连接（NHEJ）**：这是细胞默认的快速修复机制，但容易在断口处引入随机的插入或缺失（InDel）突变，常导致移码突变，从而**敲除**目标基因的功能。效率高，但精确度低。

**2. 同源定向修复（HDR）**：当同时提供含有目标序列的供体模板DNA时，细胞可利用该模板进行精确修复，实现特定碱基的**替换**或外源基因的**敲入**。效率相对较低（通常为1%~10%），且主要发生在细胞周期的 S/G2 期。

### 第二代与第三代编辑工具

为克服 Cas9 产生 DSB 带来的风险，衍生工具相继问世：

- **碱基编辑器（Base Editor）**：由 David Liu 团队于2016年开发，使用切口酶版 Cas9（nCas9）融合脱氨酶，可在不产生双链断裂的情况下将 C·G 直接转换为 T·A（胞嘧啶碱基编辑器 CBE）或 A·T 转换为 G·C（腺嘌呤碱基编辑器 ABE）。
- **先导编辑（Prime Editing）**：2019年发布，使用 pegRNA（先导编辑向导RNA）和逆转录酶融合蛋白，理论上可实现全部12种碱基置换及小片段的精确插入和缺失，被称为"搜索并替换"式基因编辑。

## 实际应用

**遗传性疾病治疗**：镰刀型细胞贫血症和 β-地中海贫血的根本原因是 HBB 基因突变。研究者利用 CRISPR 重新激活患者红细胞中的 BCL11A 增强子或胎儿血红蛋白（HbF）表达。2023年11月，FDA 批准了首个基于 CRISPR 的药物 Casgevy（exa-cel），用于治疗12岁以上镰刀型细胞贫血症患者。

**农业育种**：利用 CRISPR 敲除水稻 OsSWEET13 基因可增强白叶枯病抗性；在番茄中编辑 SP5G 基因可缩短日照依赖性，使番茄在任何纬度高效生长。由于不引入外源DNA，部分 CRISPR 编辑作物已在美国、日本获得免监管豁免。

**功能基因组学研究**：CRISPR 文库筛选（如全基因组敲除文库）使研究者能系统性地评估数千个基因对特定表型（如癌细胞药物敏感性）的贡献，这在 ZFN 时代几乎无法实现。

## 常见误区

**误区一：CRISPR 编辑只有 Cas9 一种酶**。实际上，已开发的 Cas 蛋白家族包括 Cas12a（可识别 T-rich PAM 序列、产生黏性末端）、Cas13（靶向 RNA 而非 DNA）和 CasΦ（来源于噬菌体、体积极小，约70 kDa，更易递送进细胞）等，不同 Cas 蛋白适用于截然不同的应用场景。

**误区二：脱靶效应已不再是问题**。尽管高保真 Cas9 变体（如 eSpCas9、HiFi Cas9）显著降低了脱靶率，但在临床应用中仍需进行全基因组脱靶检测（如 GUIDE-seq 或 CIRCLE-seq）。20nt 的 sgRNA 序列在人类基因组中可能存在与靶序列差2~3个碱基的非预期结合位点，若脱靶切割发生在原癌基因附近，后果严重。

**误区三：基因编辑等同于转基因**。CRISPR 编辑若仅引入 InDel 或单碱基替换而不整合外源 DNA，其最终产品与自然突变在分子层面无法区分，这是多国监管机构对其豁免 GMO 审查的依据之一。

## 知识关联

**依赖先修知识**：理解 sgRNA 的设计原理需要掌握**基因调控**中转录因子与 DNA 结合的序列特异性原理，sgRNA 与靶 DNA 的碱基互补配对本质上与基因调控中反义 RNA 的机制相同。**重组 DNA 技术**中的限制酶识别特异序列并切割的概念，是理解 CRISPR 系统"可编程切割"逻辑的概念铺垫；此外，HDR 修复途径需要供体模板的构建，直接应用了重组 DNA 技术中质粒载体的操作技能。

**延伸至后续概念**：基因编辑是**遗传工程**的核心使能技术。遗传工程在动植物育种、基因治疗、代谢工程中的应用，都以精确的基因组修改能力为前提——CRISPR 将这一能力从少数专业实验室扩展至整个生命科学领域，是从分子机制研究走向系统层面遗传改造的关键技术节点。