---
id: "bacterial-genetics"
concept: "细菌遗传"
domain: "biology"
subdomain: "microbiology"
subdomain_name: "微生物学"
difficulty: 3
is_milestone: false
tags: ["细菌"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 细菌遗传

## 概述

细菌遗传是指细菌在世代传递和种群间传播遗传信息的全部机制，包括垂直遗传（亲代到子代的染色体复制）和水平基因转移（HGT，Horizontal Gene Transfer）。细菌基因组通常是单条环状双链DNA分子，大小在0.5～10 Mb之间（大肠杆菌 *E. coli* K-12的基因组约4.6 Mb，编码约4300个基因），不同于真核生物的线性染色体，且缺乏核膜包裹，转录与翻译可同步发生于细胞质中。

细菌水平基因转移的概念在20世纪中期逐步建立：1928年格里菲斯（Frederick Griffith）首次报道肺炎链球菌（*Streptococcus pneumoniae*）R型菌与热杀死S型菌混合注射小鼠后出现转化现象；1944年艾弗里（Oswald Avery）、麦克劳德（Colin MacLeod）与麦卡蒂（Maclyn McCarty）团队用DNA酶特异性消除转化活性，证明转化物质为DNA；1952年莱德伯格（Joshua Lederberg）和津德尔（Norton Zinder）在鼠伤寒沙门菌（*Salmonella typhimurium*）中发现转导；而接合则由莱德伯格与塔特姆（Edward Tatum）于1946年在大肠杆菌K-12株中首次记录，莱德伯格于1958年因此获诺贝尔生理学或医学奖。

上述三种水平基因转移机制对临床医学具有直接冲击：携带β-内酰胺酶基因（*bla*）的质粒可在数小时内通过接合在不同菌种间扩散，使原本对氨苄西林敏感的菌株获得耐药性，最小抑菌浓度（MIC）可从≤2 μg/mL骤升至≥256 μg/mL。参考文献：《微生物学》（沈萍、陈向东主编，高等教育出版社，2016年）第7章对上述机制有系统阐述；英文经典教材《Molecular Biology of the Gene》（Watson et al., 2014, Cold Spring Harbor Laboratory Press）第12章亦提供了详细分子机制说明。

---

## 核心原理

### 转化（Transformation）

转化是细菌直接摄取胞外裸露DNA片段并整合至基因组的过程。能够自然进行转化的细菌称为处于"感受态"（competence），如肺炎链球菌、枯草芽孢杆菌（*Bacillus subtilis*）和嗜血流感杆菌（*Haemophilus influenzae*）等。感受态的建立受胞外信号肽（competence stimulating peptide，CSP）调控：当细胞密度升高时，CSP浓度超过阈值，激活ComD/ComE双组分系统，进而诱导约100个感受态相关基因表达（Claverys et al., 2006, *Annual Review of Microbiology*）。

转化效率受DNA片段大小影响显著：片段小于500 bp时难以稳定整合；超过20 kb时摄取效率大幅下降。外源双链DNA被膜表面核酸酶降解为单链后，由RecA蛋白（长丝状核蛋白酶）介导与同源染色体序列发生链侵入重组，最终以错配修复方式整合。在实验室中，通过电穿孔（电场强度通常为12.5 kV/cm，脉冲时间约4～5 ms）可人工诱导非自然感受态菌株（如大肠杆菌DH5α）进行转化，转化效率可达10⁸～10¹⁰ cfu/μg超螺旋质粒DNA。

### 转导（Transduction）

转导以噬菌体（bacteriophage）为媒介，将宿主细菌DNA片段携带至另一宿主细菌，分为**普遍性转导**（generalized transduction）和**特异性转导**（specialized transduction）。

普遍性转导发生于裂解性噬菌体感染过程中：噬菌体在裂解宿主时偶然将宿主DNA片段包入衣壳，形成转导颗粒。以P1噬菌体为例，其头部可容纳约90 kb的DNA，每次裂解产生的转导颗粒比例约为10⁻⁶～10⁻⁸，可转导大肠杆菌基因组上任意约2%的区段，是构建精细遗传图谱的经典工具。

特异性转导仅见于溶原性噬菌体，以λ噬菌体为代表：λ噬菌体整合于大肠杆菌染色体的 *attB* 位点（位于 *bio* 和 *gal* 操纵子之间，基因组坐标约17 min处），诱导切除时若发生不精确切除，可携带相邻的 *gal*（半乳糖利用基因）或 *bio*（生物素合成基因），形成λ*dgal*或λ*dbio*缺陷转导噬菌体。被转导基因范围固定，仅限于整合位点左右两侧约10 kb以内的序列。

### 接合（Conjugation）

接合是通过细菌间直接物理接触、由菌毛（pilus）介导将DNA从供体（donor，F⁺菌）转移至受体（recipient，F⁻菌）的过程。大肠杆菌F质粒（Fertility factor）约100 kb，携带长约33 kb的 *tra*（transfer）操纵子，编码F菌毛合成蛋白（TraA为菌毛结构蛋白，每根菌毛约由1000个TraA亚基组装而成）、通道蛋白TraD及启动转移的TraI松弛酶共约40种蛋白。

接合转移以单链形式通过IV型分泌系统（T4SS）通道进行，起始于质粒上的 *oriT*（转移起点）位点：TraI松弛酶在 *nic* 位点切割单链，共价结合于5'端，启动滚环复制（rolling circle replication）。完整质粒转移至受体后，在供体与受体各自合成互补链，完成双链再生。接合频率在F⁺×F⁻组合中约为每细胞每小时1～5次，而当F质粒整合于染色体形成Hfr（High frequency recombination）菌株时，可高频率转移染色体基因，但因完整染色体转移需约100分钟而配对常提前中断，转移基因顺序呈线性，可用于构建中断接合实验（interrupted mating）遗传图。

---

## 关键公式与计算

### 转化效率公式

实验室中评价转化实验结果的核心指标为**转化效率**（Transformation Efficiency，TE），定义如下：

$$TE = \frac{\text{菌落形成单位数 (cfu)}}{\text{所用DNA质量 (μg)}}$$

例如：使用0.1 ng质粒DNA转化大肠杆菌，铺板后计数得到500个菌落，则：

$$TE = \frac{500}{0.0001\ \mu g} = 5 \times 10^6 \ \text{cfu/μg}$$

一般认为TE ≥ 10⁶ cfu/μg适用于普通克隆实验，文库构建则需TE ≥ 10⁸ cfu/μg。

### 中断接合实验与遗传图距

中断接合实验（Wollman & Jacob, 1958）通过记录各基因进入受体的时间（分钟）确定其在染色体上的相对位置，图距单位为"分钟（min）"。大肠杆菌K-12染色体全长约100 min，常用参考位点如 *thr*（苏氨酸合成，0 min）、*lac*（乳糖利用，8 min）、*trp*（色氨酸合成，28 min）、*his*（组氨酸合成，44 min）。

```python
# 简单示例：根据中断接合实验数据绘制基因进入时间图
import matplotlib.pyplot as plt

genes = ['thr', 'lac', 'trp', 'his', 'arg']
entry_time_min = [0, 8, 28, 44, 70]  # 各基因进入受体的时间（分钟）

plt.figure(figsize=(8, 2))
plt.scatter(entry_time_min, [1]*len(genes), s=100, color='steelblue', zorder=5)
for i, gene in enumerate(genes):
    plt.annotate(gene, (entry_time_min[i], 1), textcoords="offset points",
                 xytext=(0, 10), ha='center', fontsize=11)
plt.plot(entry_time_min, [1]*len(genes), color='gray', linewidth=1)
plt.xlim(-5, 105)
plt.yticks([])
plt.xlabel('进入时间（分钟）')
plt.title('大肠杆菌K-12 Hfr菌株中断接合遗传图')
plt.tight_layout()
plt.savefig('conjugation_map.png', dpi=150)
plt.show()
```

---

## 实际应用

### 基因工程与质粒载体构建

转化技术是重组DNA技术的核心操作步骤。将目的基因连接至pUC19（2686 bp）、pET系列等质粒载体后，通过CaCl₂化学法或电穿孔法转化大肠杆菌宿主（如DH5α用于扩增，BL21(DE3)用于蛋白表达），筛选阳性克隆后进行蛋白表达纯化或基因功能研究。目前CRISPR-Cas9系统的递送也常通过质粒转化完成。

### 抗生素耐药性的水平扩散

携带耐药基因的可接合质粒（conjugative resistance plasmid）是临床多重耐药菌（MDR）形成的主要驱动力。

例如，编码NDM-1（新德里金属β-内酰胺酶，New Delhi Metallo-β-lactamase-1）的 *bla*NDM-1 基因位于可接合质粒上，自2008年首次在印度被报道（Yong et al., 2009, *Antimicrobial Agents and Chemotherapy*）后，通过接合在肺炎克雷伯菌、大肠杆菌、鲍曼不动杆菌等之间迅速扩散，目前已在全球逾60个国家检出。NDM-1能水解几乎所有β-内酰胺类抗生素，包括碳青霉烯类（亚胺培南、美罗培南），使对应菌株MIC常超过32 μg/mL（EUCAST耐药折点）。

### 噬菌体转导在噬菌体治疗中的双刃剑效应

噬菌体治疗（phage therapy）利用噬菌体裂解耐药菌，但需警惕转导现象：溶原性噬菌体可能将耐药基因或毒力基因从一株细菌转导至另一株，例如志贺毒素基因（*stx*）即通过λ样噬菌体整合于大肠杆菌O157:H7染色体。因此，临床应用噬菌体时需筛选严格裂解性（strictly lytic）噬菌体，排除具有溶原性整合能力者。

---

## 常见误区

**误区1：转化需要噬菌体参与**
转化是细菌直接摄取裸露DNA的过程，完全不依赖噬菌体；转导才是以噬菌体为媒介。混淆两者的根源在于对"媒介"角色的理解不清晰。

**误区2：接合仅限于同种细菌之间**
接合的宿主范围（host range）取决于质粒 *tra* 系统的表面识别蛋白特异性。宽宿主范围质粒（如IncP类质粒，如RK2，60 kb）可在革兰阴性菌之间跨属甚至跨纲接合转移，部分质粒甚至可以在革兰阴性菌与革兰阳性菌之间、或细菌与植物细胞之间转移（如农杆菌 *Ti* 质粒向植物细胞转移T-DNA）。

**误区3：Hfr菌株接合可以将完整质粒高效转移至F⁻菌**
Hfr菌株中F质粒已整合至染色体，*oriT* 被置于染色体序列中，接合转移时先行转移的是染色体基因，而F质粒本身最后转移。由于完整染色体转移需约100分钟，配对通常提前中断，受体极少获得完整F因子，因此Hfr×F⁻后代多为F⁻而非F⁺。

**误区4：转导可以转移