---
id: "epigenetics"
concept: "表观遗传学"
domain: "biology"
subdomain: "molecular-biology"
subdomain_name: "分子生物学"
difficulty: 4
is_milestone: false
tags: ["前沿"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 表观遗传学

## 概述

表观遗传学（Epigenetics）研究在DNA序列不发生改变的前提下，基因表达模式的可遗传性变化。这一术语由英国发育生物学家Conrad Waddington于1942年正式提出，他在《现代遗传学导论》中以"表观遗传景观"（epigenetic landscape）这一地形比喻，描述细胞发育中命运选择的不可逆性——如同小球滚入山谷沟壑，细胞一旦分化便难以逆行。1975年，Holliday与Pugh，以及Riggs分别独立提出DNA甲基化的体细胞遗传模型，奠定了分子机制研究的基础。进入21世纪，高通量测序技术（如全基因组亚硫酸氢盐测序，WGBS）使单碱基精度的甲基化图谱成为可能，人类表观基因组学由此进入系统研究阶段（参见《表观遗传学》Allis等主编，CSH Press，2015年第二版）。

现代表观遗传学公认的三大核心机制是：**DNA甲基化**、**组蛋白修饰**和**染色质重塑**，三者协同构成基因组之上的调控层级。表观遗传修饰的关键特性在于其**可逆性**与**可遗传性**：与基因突变不同，DNA甲基化等标记在细胞分裂时可被DNA甲基转移酶忠实复制至子代细胞，但也可在特定发育阶段或病理条件下被主动去除。表观遗传标记还可跨代遗传——荷兰1944至1945年饥荒（Hongerwinter）幸存者的流行病学追踪研究显示，饥荒期间受孕的胎儿，其成年后IGF2基因的甲基化水平显著低于同性别未受影响的兄弟姐妹（Heijmans et al., 2008, *PNAS*），提示环境压力可将表观遗传印记传递至后代。

携带完全相同基因组的肝细胞与神经元之所以形态与功能迥异，正是因为两种细胞在分化过程中积累了截然不同的表观遗传修饰谱——这是理解细胞分化机制的核心切入点。

---

## 核心原理

### DNA甲基化

DNA甲基化是在DNA甲基转移酶（DNMT）催化下，将S-腺苷甲硫氨酸（SAM）提供的甲基基团共价添加到胞嘧啶第5位碳原子上，形成5-甲基胞嘧啶（5mC）的化学反应。该反应在哺乳动物中几乎专一发生在**CpG二核苷酸**位点（即5'—CG—3'序列）上。人类基因组约含2800万个CpG位点，其中**70%～80%**处于甲基化状态，主要分布于重复序列和基因间区，用于抑制转座子活性。

基因启动子区的**CpG岛**（CpG island，定义标准：长度≥200 bp、GC含量≥50%、CpG观测值/期望值≥0.6）通常保持低甲基化，对应基因活跃转录。当CpG岛发生超甲基化时，甲基化CpG结合蛋白（如MeCP2）募集HDAC复合体，压缩染色质并阻断转录因子结合，导致基因沉默。结直肠癌中，错配修复基因*MLH1*的CpG岛超甲基化检出率高达**40%**，是导致微卫星不稳定性的主要表观遗传事件（Herman & Baylin, 2003, *NEJM*）。

**三种DNMT的功能分工明确**：
- **DNMT1**：复制型甲基转移酶，在DNA复制后识别半甲基化CpG位点，将新合成链甲基化，维持亲代甲基化模式的代际传递。
- **DNMT3A / DNMT3B**：从头甲基转移酶（de novo methylation），在胚胎着床前后建立全新的甲基化模式，DNMT3A突变是急性髓系白血病（AML）最常见的体细胞突变之一（检出率约20%）。
- **TET1/2/3酶**：将5mC氧化为5-羟甲基胞嘧啶（5hmC），介导主动去甲基化，逆转基因沉默。

---

### 组蛋白修饰与"组蛋白密码"

核小体（nucleosome）是染色质的基本重复单元：约147 bp的DNA双链缠绕在由H2A、H2B、H3、H4各两分子组成的组蛋白八聚体上，相邻核小体由约20 bp的连接DNA（linker DNA）及组蛋白H1连接。组蛋白N端尾部富含赖氨酸和精氨酸残基，突出于核小体颗粒外，是发生翻译后修饰（PTM）的主要位点。

常见修饰及其生物学意义：

| 修饰类型 | 代表位点 | 功能意义 |
|---|---|---|
| 三甲基化 | H3K4me3 | 活跃基因启动子标记（由SETD1A/B催化） |
| 三甲基化 | H3K27me3 | 多梳沉默标记（由PRC2复合体EZH2催化） |
| 三甲基化 | H3K9me3 | 组成型异染色质标记（由SUV39H1/2催化） |
| 乙酰化 | H3K27ac | 增强子活跃状态标记 |
| 磷酸化 | H2A.XS139ph (γH2AX) | DNA双链断裂损伤应答的早期信号 |
| 单泛素化 | H2BK120ub1 | 促进H3K4甲基化，协同激活转录 |

"**组蛋白密码假说**"（histone code hypothesis，Strahl & Allis, 2000, *Nature*）指出：单一修饰位点的生物学输出取决于周围其他修饰的组合状态，多种修饰的协同或拮抗决定染色质区域的最终转录状态。例如，H3K4me3与H3K27me3同时存在于同一核小体上，构成"**二价域**"（bivalent domain），这种状态在胚胎干细胞的发育调控基因处高度富集，维持基因处于低表达但可快速激活的"待命"状态（Bernstein et al., 2006, *Cell*）。

---

### 染色质重塑

染色质重塑复合体利用ATP水解的能量，通过**滑动**（sliding）、**弹出**（ejection）或**替换**（histone variant exchange）核小体，改变转录因子对DNA的可及性。主要家族如下：

- **SWI/SNF家族**（人类中称BAF/PBAF复合体）：核心催化亚基为SMARCA4（BRG1）或SMARCA2（BRM），通过滑动或剥离核小体暴露启动子区域。BAF复合体亚基突变在超过**20%**的人类癌症中可被检出，使其成为肿瘤抑制因子（Kadoch & Crabtree, 2015, *Science*）。
- **ISWI家族**（如NURF、CHRAC复合体）：主要将核小体规则排列，创造或消除核小体自由区（NFR），调控转录起始。
- **CHD家族**（如CHD7）：利用染色质域（chromodomain）读取H3K4me1/2，在增强子激活中发挥关键作用；CHD7突变导致CHARGE综合征（多器官发育缺陷）。

---

## 关键公式与量化分析

在表观遗传学研究中，DNA甲基化水平通常以**甲基化率**（β值或M值）表示。在Illumina甲基化芯片（450K/EPIC芯片）分析中：

$$\beta = \frac{I_{methylated}}{I_{methylated} + I_{unmethylated} + 100}$$

其中 $I_{methylated}$ 与 $I_{unmethylated}$ 分别为甲基化探针与非甲基化探针的荧光强度，$\beta$ 值范围为 $[0, 1]$，0代表完全未甲基化，1代表完全甲基化。在差异甲基化分析中，通常将 $|\Delta\beta| \geq 0.2$ 且调整后 $p < 0.05$ 作为显著差异甲基化位点（DMR）的筛选标准。

以下为利用R语言中`minfi`包计算β值矩阵并进行差异甲基化分析的核心代码片段：

```r
library(minfi)

# 读取IDAT原始数据并进行归一化
RGset <- read.metharray.exp(base = "idat_directory")
Mset  <- preprocessQuantile(RGset)         # 分位数归一化

# 提取beta值矩阵 (CpG位点 × 样本)
beta_matrix <- getBeta(Mset)

# 差异甲基化分析（肿瘤 vs 正常）
library(limma)
design <- model.matrix(~ group)            # group: "tumor" / "normal"
fit    <- lmFit(logit(beta_matrix), design)
fit    <- eBayes(fit)
DMPs   <- topTable(fit, coef = 2, number = Inf,
                   adjust = "BH", p.value = 0.05)

# 筛选 |Δβ| ≥ 0.2 的位点
DMPs_filtered <- DMPs[abs(DMPs$logFC) >= logit(0.7) - logit(0.5), ]
```

---

## 实际应用

### 肿瘤诊断与液体活检

表观遗传学改变早于形态学变化出现，使其成为早期癌症诊断的理想生物标志物。游离DNA（cfDNA）的甲基化谱分析可用于多癌种早筛：Grail公司开发的Galleri检测基于血浆cfDNA甲基化，对50种癌症联合检测的特异性达**99.5%**（Klein et al., 2021, *Annals of Oncology*）。

### 表观遗传药物

表观遗传修饰的可逆性使其成为药物靶点：
- **DNMT抑制剂**：5-氮杂胞苷（Azacitidine，地西他滨）整合至DNA后不可逆结合DNMT1，导致复制后去甲基化，重激活沉默的抑癌基因；已获FDA批准用于骨髓增生异常综合征（MDS）治疗。
- **HDAC抑制剂**：伏立诺他（Vorinostat，SAHA）抑制HDAC I/II类，导致组蛋白高乙酰化，激活凋亡相关基因；2006年获FDA批准用于皮肤T细胞淋巴瘤（CTCL）。
- **EZH2抑制剂**：他泽司他（Tazemetostat）靶向PRC2复合体催化亚基EZH2，抑制H3K27me3积累，用于EZH2突变型滤泡淋巴瘤治疗（2020年FDA批准）。

### 发育生物学：基因组印记

基因组印记（genomic imprinting）是表观遗传单亲特异性表达的典型案例：*IGF2*基因仅来自父方的等位基因表达，*H19*仅来自母方等位基因表达，两者由同一差异甲基化区域（ICR）控制。父方ICR甲基化→阻断CTCF绝缘子结合→增强子激活*IGF2*；母方ICR未甲基化→CTCF结合→增强子转向激活*H19*。这一精密的顺式调控回路说明**5 kb以内的甲基化差异即可决定Mb级别基因组区域的转录命运**。

---

## 常见误区

**误区1：表观遗传 = 基因表达调控**
表观遗传修饰是基因调控的机制之一，但并非所有基因调控都属于表观遗传学范畴。表观遗传的界定标准是：**在细胞分裂过程中可被遗传**，而转录因子的瞬时结合仅属于顺式/反式调控，不具有分裂后的遗传稳定性。

**误区2：DNA甲基化总是抑制基因表达**
启动子CpG岛甲基化确实与基因沉默相关，但基因体（gene body）内的CpG甲基化与活跃转录**正相关**——基因体甲基化可能抑制隐性启动子的激活并防止转录延伸中的错误起始。*DNMT3B*敲除实验证实基因体甲基化缺失导