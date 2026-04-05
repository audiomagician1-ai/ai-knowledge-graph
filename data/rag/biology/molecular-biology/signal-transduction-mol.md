---
id: "signal-transduction-mol"
concept: "分子信号通路"
domain: "biology"
subdomain: "molecular-biology"
subdomain_name: "分子生物学"
difficulty: 4
is_milestone: false
tags: ["信号"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 92.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 分子信号通路

## 概述

分子信号通路是细胞内一系列蛋白质和小分子按照特定顺序依次激活的级联反应链，将来自细胞表面受体的外部信号转化为基因表达改变或代谢调控响应。与细胞信号转导的宏观框架不同，分子信号通路聚焦于具体蛋白质分子——激酶、GTP酶、泛素连接酶、转录因子——之间的物理互作与化学修饰，尤以丝氨酸/苏氨酸/酪氨酸位点的磷酸化为核心传递手段，单个磷酸化事件可在毫秒至秒的量级内将信号放大逾千倍。

经典分子信号通路的系统研究始于20世纪80年代。Martin Rodbell与Alfred Gilman因阐明G蛋白在受体-效应器耦联中的核心角色而于1994年共同荣获诺贝尔生理学或医学奖。此后，MAPK三级激酶级联结构于1993年由David Robbins等人完整阐明，PI3K于1992年由Michael Waterfield实验室克隆鉴定，Wnt/β-catenin信号轴的"破坏复合体"机制则由Roel Nusse与Harold Varmus自1982年起历经十余年逐步解析完成（参见《Molecular Biology of the Cell》第7版，Alberts et al., 2022，Garland Science）。

三条通路的临床意义极为突出：约30%的人类实体肿瘤携带RAS基因点突变（MAPK通路核心节点），约20%携带PIK3CA激活突变（PI3K通路），而Wnt通路异常则见于超过90%的散发性结直肠癌。全球已批准上市的靶向这三条通路的药物超过40种，深入掌握其分子机制是理解精准肿瘤学的基础。

---

## 核心原理

### MAPK信号通路：三级激酶级联放大

MAPK（丝裂原激活蛋白激酶，Mitogen-Activated Protein Kinase）通路的核心架构为三层串联激酶模块：**MAP3K**（如ARAF/BRAF/CRAF）→ **MAP2K**（如MEK1/MEK2）→ **MAPK**（如ERK1/ERK2）。信号起始时，表皮生长因子（EGF）等配体结合受体酪氨酸激酶（RTK），诱导受体二聚化与自磷酸化，招募衔接蛋白GRB2/SOS，催化RAS-GDP转换为RAS-GTP（半衰期正常约10秒，KRAS突变后延长至数分钟）。活化的RAS-GTP招募BRAF至质膜内侧，在Ser338位点磷酸化后激活RAF；RAF继而在Ser217与Ser221双位点磷酸化MEK1/2；MEK作为双特异性激酶，最终在Thr202/Tyr204（ERK1对应Thr185/Tyr187）双位点磷酸化ERK1/2。

活化ERK的靶底物超过200种：在胞质中磷酸化并激活RSK1/2/3（调控核糖体蛋白S6及CREB）；转位入核后磷酸化ETS家族转录因子ELK1（Ser383/Ser389），驱动细胞周期蛋白D1（*CCND1*）及*MYC*等基因转录上调。信号终止主要依赖双特异性磷酸酶DUSP6（对ERK2具有纳摩尔级亲和力，$K_d \approx 4\ \text{nM}$），构成典型的负反馈环路。

**关键突变**：KRAS G12D（甘氨酸→天冬氨酸）突变消除GTP酶活性，通路持续激活，是胰腺导管腺癌（PDAC）中约90%的驱动突变；BRAF V600E（缬氨酸→谷氨酸）突变使BRAF在单体状态下即持续活化，存在于约60%的黑色素瘤中，靶向药物维莫非尼（Vemurafenib）对此突变型患者中位无进展生存期从1.6个月延长至5.3个月（Chapman et al., 2011, *N Engl J Med*）。

### PI3K/Akt/mTOR通路：代谢与细胞存活的枢纽

PI3K（磷脂酰肌醇-3-激酶）被活化RTK或GPCR招募至细胞膜后，将质膜内侧的PIP₂（磷脂酰肌醇-4,5-二磷酸）的3'-羟基磷酸化，生成第二信使PIP₃（磷脂酰肌醇-3,4,5-三磷酸）。PIP₃通过结合含PH结构域的PDK1与Akt，将两者同时锚定至细胞膜，使PDK1可在Thr308位点磷酸化Akt的激活环；mTORC2复合体则在Akt的疏水基序Ser473位点完成第二步磷酸化，实现Akt完全激活（仅Thr308磷酸化时活性仅为双磷酸化的约10%）。

激活的Akt通过磷酸化逾100种底物发挥多效功能：

- 磷酸化TSC2（Thr1462）→ 抑制TSC1/TSC2复合体对Rheb的GAP活性 → Rheb-GTP积累 → mTORC1激活 → 磷酸化4E-BP1（解除对eIF4E的抑制）和S6K1（Thr389）→ 上调蛋白质合成与核糖体生物发生；
- 磷酸化FOXO1/3/4转录因子（Thr24/Ser256/Ser319）→ 促进其出核并与14-3-3蛋白结合 → 抑制*FASL*、*BIM*等促凋亡基因转录；
- 磷酸化MDM2（Ser166/Ser186）→ 增强其入核及对p53的泛素化降解。

天然制动器**PTEN**（第10号染色体缺失的磷酸酶和张力蛋白同源物）特异性去磷酸化PIP₃的3'-磷酸基团，将其还原为PIP₂，是该通路最重要的负调控因子；PTEN基因在子宫内膜癌中突变率约50%，在胶质母细胞瘤中约36%。

### Wnt/β-catenin通路：发育与干细胞维持

在**无Wnt信号**状态下，由APC（腺瘤性结肠息肉蛋白，约310 kDa）、Axin1/2、GSK-3β与CK1α（酪蛋白激酶1α）组成的"破坏复合体"（destruction complex）持续运作：CK1α首先在β-catenin Ser45位点进行初始磷酸化，随后GSK-3β依次在Thr41、Ser37、Ser33位点（N端降解盒内）磷酸化β-catenin；三磷酸化的β-catenin被E3泛素连接酶受体β-TrCP识别，经蛋白酶体26S快速降解，胞质中游离β-catenin水平维持在极低水平（约$10^{-9}\ \text{mol/L}$量级）。

**当Wnt配体（如Wnt3a）存在时**，Wnt与Frizzled（卷曲蛋白，7次跨膜受体）及共受体LRP5/6同时结合，形成三元复合体；Dishevelled（Dvl）蛋白多聚化激活，招募Axin至磷酸化的LRP5/6胞内段，解散破坏复合体；GSK-3β活性被抑制，β-catenin磷酸化终止，胞质中游离β-catenin迅速积累并转位入核。入核后的β-catenin替换转录共抑制因子Groucho，与TCF/LEF家族转录因子结合，激活*AXIN2*（反馈靶点）、*MYC*（c-Myc）、*CCND1*等靶基因转录。

**关键突变**：APC基因截断突变（导致β-catenin降解障碍）见于约85%的家族性腺瘤性息肉病（FAP）及80%以上的散发性结直肠癌；β-catenin自身N端降解盒（CTNNB1 Ser33/Ser37/Thr41/Ser45）点突变则见于肝母细胞瘤（约70%）及子宫内膜癌（约25%），使其逃避破坏复合体的识别。

---

## 关键公式与定量分析

信号通路中，激酶对底物的磷酸化速率遵循Michaelis-Menten动力学。对于ERK磷酸化其底物（如RSK1）的反应，酶促动力学公式为：

$$v = \frac{V_{\max} \cdot [S]}{K_m + [S]}$$

其中 $v$ 为磷酸化速率（nmol·mg⁻¹·min⁻¹），$[S]$ 为底物浓度，$K_m$ 为米氏常数（ERK2对RSK1的 $K_m \approx 50\ \mu\text{M}$），$V_{\max}$ 为最大反应速率。在信号通路的数学建模中，常用常微分方程组（ODE）描述各组分的时间动态。以最简化的MAPK级联为例：

$$\frac{d[\text{ERK}^*]}{dt} = k_{\text{on}} \cdot [\text{MEK}^*] \cdot [\text{ERK}] - k_{\text{off}} \cdot [\text{DUSP6}] \cdot [\text{ERK}^*]$$

其中 $[\text{ERK}^*]$ 为活化ERK浓度，$k_{\text{on}}$ 为MEK对ERK的磷酸化速率常数，$k_{\text{off}}$ 为DUSP6对ERK的去磷酸化速率常数。Huang与Ferrell（1996，*PNAS*）的建模工作揭示了MAPK三级级联可产生**超灵敏（ultrasensitivity）**响应，Hill系数可高达$n \approx 4.9$，赋予通路类似"开关"的全或无特性。

---

## 实际应用：靶向治疗与生物标志物

### MAPK通路靶向药物

以BRAF V600E突变型黑色素瘤为例，FDA于2011年批准BRAF抑制剂维莫非尼（Vemurafenib），2013年批准MEK抑制剂曲美替尼（Trametinib），两者联合（"达拉非尼+曲美替尼"方案）将转移性黑色素瘤的中位总生存期从未靶向治疗的约8个月提升至约25个月（Long et al., 2017, *Lancet Oncol*）。值得注意的是，BRAF V600E突变存在于结直肠癌中时（约10%），单用BRAF抑制剂效果极差，因为结肠癌细胞通过EGFR的快速反馈激活旁路绕过BRAF抑制，需三联阻断（BRAF + MEK + EGFR）才能获得临床疗效，揭示了同一突变在不同组织背景下信号网络重连方式的差异。

### PI3K/Akt通路抑制剂

阿培利司（Alpelisib）是首个获FDA批准（2019年）的α特异性PI3K抑制剂，专门用于携带*PIK3CA*激活突变（最常见为E545K和H1047R）的HR+/HER2−晚期乳腺癌患者，联合氟维司群使无进展生存期从5.7个月延长至11.0个月（André et al., 2019, *N Engl J Med*）。伴随诊断工具为基于循环肿瘤DNA（ctDNA）检测的Foundation One CDx平台，可在血液样本中以超过1%的等位基因频率检出*PIK3CA*突变。

### Wnt通路抑制策略

Wnt通路的靶向难度较高，因其广泛参与正常组织稳态（肠道隐窝干细胞每5天完全更新一次依赖Wnt信号）。Porcupine抑制剂（如WNT-974）通过阻断Wnt配体的棕榈酰化修饰（该修饰由PORCN酶催化，Ser209位点，为Wnt与Frizzled结合所必需）来抑制所有Wnt亚型的分泌，目前处于AXIN2突变型结直肠癌的Ⅰ/Ⅱ期临床试验阶段。

---

## 常见误区

**误区1：三