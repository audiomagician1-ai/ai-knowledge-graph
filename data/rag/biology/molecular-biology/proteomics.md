---
id: "proteomics"
concept: "蛋白质组学"
domain: "biology"
subdomain: "molecular-biology"
subdomain_name: "分子生物学"
difficulty: 4
is_milestone: false
tags: ["组学"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 40.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-23"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 蛋白质组学

## 概述

蛋白质组学（Proteomics）由澳大利亚科学家Marc Wilkins于1994年首次提出，用于描述某一基因组所表达的全套蛋白质。与基因组学研究静态的DNA序列不同，蛋白质组具有高度动态性——同一细胞在不同生理状态、不同时间点所表达的蛋白质种类和丰度可能天壤之别。人类基因组约编码2万个基因，但由于选择性剪接、翻译后修饰（PTM）等机制，人类蛋白质组的实际成员估计超过100万种，远超基因数量[Wilkins et al., 1996]。

蛋白质组学之所以不可替代，在于中心法则的信息传递并非完全线性：mRNA水平并不能准确预测蛋白质丰度。研究表明，mRNA表达量与蛋白质表达量的相关系数（Pearson $r$）通常仅为0.4～0.6，这意味着超过一半的蛋白质丰度变化无法从转录组数据中推断[Gygi et al., Science, 1999]。因此，直接测量蛋白质组是理解细胞功能、疾病机制和药物靶点的必要手段。

## 核心原理

### 质谱技术：蛋白质组学的核心检测手段

现代蛋白质组学的核心技术是串联质谱（LC-MS/MS）。实验流程通常为：将蛋白质混合物用胰蛋白酶（Trypsin）在赖氨酸（K）和精氨酸（R）的羧基端切割，生成长度6～20个氨基酸的肽段；经液相色谱（LC）分离后进入质谱仪，第一级质谱（MS1）记录肽段的母离子质荷比 $m/z$，第二级质谱（MS2）对母离子碎裂，产生b离子和y离子系列，用于序列鉴定。肽段的理论质量可由下式计算：

$$M = \sum_{i=1}^{n} m_{aa_i} + m_{H_2O}$$

其中 $m_{aa_i}$ 为第 $i$ 个氨基酸残基的单同位素质量，$m_{H_2O} = 18.0106\ \text{Da}$。目前主流仪器如Thermo Orbitrap Fusion可实现质量分辨率 $>500{,}000$，质量精度优于5 ppm，能在单次实验中鉴定超过10,000种蛋白质。

### 定量蛋白质组学方法

蛋白质组学不仅要鉴定"是什么"，还要精确测量"有多少"。主要定量策略分为标记定量和非标记定量两大类：

**同位素标记定量（SILAC）**：通过在细胞培养基中加入含重同位素（$^{13}C_6$-赖氨酸、$^{13}C_6{,}^{15}N_4$-精氨酸）的氨基酸，使"重"标记细胞蛋白质与正常"轻"细胞蛋白质混合后，在MS1图谱中形成质量差固定的同位素对（赖氨酸标记产生 $\Delta m = 6.0201\ \text{Da}$）。两个峰的面积之比即为相对丰度比[Ong et al., Molecular & Cellular Proteomics, 2002]。

**串联质量标签（TMT）**：允许在单次实验中同时比较最多18个样品，适用于大规模临床队列研究。TMT试剂与肽段氨基末端及赖氨酸侧链反应，在MS2碎裂时释放126～134 Da的报告离子，报告离子强度比即代表各样品的蛋白质相对丰度。

**非标记定量（Label-Free Quantification, LFQ）**：不使用同位素或化学标记，直接比较不同运行之间MS1的肽段峰面积，通过MaxLFQ算法在MaxQuant软件中实现，适合处理临床样本（无法进行代谢标记）的大规模比较。

### 翻译后修饰（PTM）蛋白质组学

细胞信号转导的动态调控主要通过PTM实现。磷酸化蛋白质组学（Phosphoproteomics）是研究最广泛的PTM方向：磷酸化在丝氨酸（Ser）、苏氨酸（Thr）和酪氨酸（Tyr）上发生，分别占总磷酸化位点的约90%、10%和0.05%。由于磷酸化肽段丰度极低，需要通过固相金属亲和色谱（IMAC）或TiO₂富集后再进行质谱分析。

一个完整的磷酸化蛋白质组学数据分析流程示例（使用Python/pandas处理MaxQuant输出）：

```python
import pandas as pd
import numpy as np

# 读取MaxQuant Phospho(STY)Sites.txt输出文件
phospho = pd.read_csv("Phospho (STY)Sites.txt", sep="\t", low_memory=False)

# 筛选定位概率 >= 0.75 的高可信磷酸化位点
high_conf = phospho[phospho["Localization prob"] >= 0.75].copy()

# 提取LFQ强度列并进行log2转换
lfq_cols = [col for col in high_conf.columns if col.startswith("Intensity ")]
high_conf[lfq_cols] = high_conf[lfq_cols].replace(0, np.nan)
high_conf[lfq_cols] = np.log2(high_conf[lfq_cols])

# 计算各位点在条件A（3重复）与条件B（3重复）之间的平均差
high_conf["log2FC"] = (high_conf[lfq_cols[:3]].mean(axis=1) - 
                       high_conf[lfq_cols[3:6]].mean(axis=1))

print(f"高可信磷酸化位点数：{len(high_conf)}")
print(high_conf[["Proteins","Amino acid","Position","log2FC"]].head())
```

## 实际应用

**癌症生物标志物发现**：2020年，美国国家癌症研究所（NCI）主导的临床蛋白质组肿瘤分析联盟（CPTAC）发表了对284例肺腺癌患者肿瘤组织的深度蛋白质组学分析，鉴定了超过11,000种蛋白质，发现STK11突变患者中蛋白激酶MARK1/2显著低表达，为该亚型的靶向治疗提供了新依据（Gillette et al., Cell, 2020）。

**新冠病毒感染机制研究**：2020年，Bojkova等人（Nature, 2020）对SARS-CoV-2感染Caco-2细胞进行时间分辨蛋白质组和磷酸化蛋白质组分析，在感染后2、6、10、24小时分别鉴定蛋白质组变化，发现病毒感染激活翻译机制同时抑制核糖体蛋白磷酸化，进而证明蛋白翻译抑制剂（如Zotatifin）可在体外抑制病毒复制，直接将蛋白质组学数据转化为药物重定向策略。

**临床血浆蛋白质组学**：人类血浆蛋白质组动态范围极宽，白蛋白浓度约35–50 mg/mL，而一些低丰度疾病标志物（如PSA前列腺癌标志物）浓度仅为ng/mL量级，动态范围跨越约10个数量级（$10^{10}$）。通过高丰度蛋白质去除（如IgY14免疫耗竭）结合深度蛋白质组学，已在人类血浆中检测到近4,600种蛋白质，构建了人类血浆蛋白质组图谱（Human Plasma Proteome Project, HPPP）。

## 常见误区

**误区一：蛋白质组学就是把所有蛋白质都测一遍**。实际上，由于动态范围、翻译后修饰异构体和样本制备偏差等限制，任何单一实验方案都只能覆盖蛋白质组的一个子集。"鸟枪法"（Shotgun proteomics）偏向检测高丰度蛋白，低丰度信号通路蛋白（如转录因子FOXO1，细胞内拷贝数约1,000个/细胞）在全蛋白质组实验中往往检测不到，需要靶向方法（如PRM/SRM）专门验证。

**误区二：检测到的肽段就等于检测到了对应蛋白质**。质谱鉴定的最小单元是肽段，同一蛋白质的不同肽段可能检测到的数量差异悬殊，且某些肽段序列被多个蛋白质共享（简并肽），直接导致蛋白质推断的歧义性。国际蛋白质组学数据报告标准（MIAPE，Minimum Information About a Proteomics Experiment）要求每个蛋白质报告至少需1条唯一肽段（unique peptide），以此降低假阳性推断。

**误区三：蛋白质组学数据无需统计校正**。由于同时检测数千种蛋白质，多重比较问题极为严重。若使用 $p < 0.05$ 而不校正，在5,000个蛋白质中预期产生约250个假阳性。标准分析应采用Benjamini-Hochberg假发现率（FDR）校正，将FDR控制在1%或5%，相应调整后阈值远低于名义显著性水平。

## 思考题

1. 在SILAC实验中，如果研究者将"重"标记细胞（$^{13}C_6$-赖氨酸处理）与"轻"标记细胞按照1:1混合后进行LC-MS/MS分析，但在MS1图谱中观察到某蛋白质的重/轻峰面积比为3:1，这说明该蛋白质在实验条件下发生了什么变化？请结合 $\log_2(\text{ratio}) = \log_2(3) \approx 1.58$ 解释其生物学含义。

2. 在磷酸化蛋白质组学研究中，两种激酶抑制剂处理后共同下调了100个磷酸化位点，但其中60个位点所在蛋白质的总蛋白质丰度也发生了变化。如何设计分析流程，区分"磷酸化水平真正降低"与"蛋白质本身减少导致磷酸化信号减弱"这两种情况？

3. 人类血浆蛋白质组的检测动态范围约为 $10^{10}$，而目前最先进的Orbitrap质谱仪的单次扫描动态范围约为 $10^4$。请解释研究人员是通过哪些技术手段（至少列举两种）来弥补这一巨大差距，并分析每种方法的局限性。
