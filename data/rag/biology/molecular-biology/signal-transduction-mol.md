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
quality_tier: "B"
quality_score: 49.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 分子信号通路

## 概述

分子信号通路是细胞内一系列蛋白质和小分子按照特定顺序依次激活的级联反应链，将来自细胞表面受体的外部信号转化为基因表达改变或代谢调控响应。与细胞信号转导的宏观框架不同，分子信号通路关注的是具体的蛋白质分子——如激酶、GTP酶、转录因子——之间的物理互作与化学修饰，尤其以磷酸化（serine/threonine/tyrosine位点）为核心传递手段。

经典分子信号通路的系统研究始于20世纪80年代，Martin Rodbell和Alfred Gilman因发现G蛋白在信号传递中的作用而于1994年获得诺贝尔生理学或医学奖。随后MAPK通路（1993年完整阐明其三级激酶级联结构）、PI3K/Akt通路和Wnt/β-catenin通路相继被解析，形成了今日分子肿瘤学和发育生物学的基础框架。

这三条通路的临床意义在于：约30%的人类癌症携带RAS基因点突变（MAPK通路核心节点），20%以上携带PIK3CA突变（PI3K通路），而Wnt通路异常则见于超过90%的结直肠癌。靶向这些通路的药物已成为精准医疗的主体，理解其分子机制是研发新型靶向药物的前提。

---

## 核心原理

### MAPK信号通路：三级激酶级联

MAPK（丝裂原激活蛋白激酶）通路的核心结构是三层串联激酶：MAP3K（如RAF）→ MAP2K（如MEK1/2）→ MAPK（如ERK1/2）。信号起始时，生长因子（如EGF）结合受体酪氨酸激酶，触发RAS-GTP的形成；活化的RAS招募并磷酸化RAF（在Ser338位点），RAF再磷酸化MEK（在Ser217/Ser221双位点），MEK最终在Thr202/Tyr204双位点磷酸化ERK。活化的ERK既可在胞质中磷酸化底物（如RSK激酶），也可转位入核磷酸化转录因子ELK1，驱动细胞周期蛋白D1（Cyclin D1）等促增殖基因的表达。

信号终止依赖双特异性磷酸酶（DUSPs），其中DUSP6对ERK具有高度选择性，形成负反馈回路。KRAS G12D突变使RAS蛋白丧失GTP酶活性，导致通路持续活化，是胰腺癌中最常见的驱动突变。

### PI3K/Akt/mTOR通路：代谢与生存的枢纽

PI3K（磷脂酰肌醇-3-激酶）被招募至活化受体后，将质膜上的PIP₂（磷脂酰肌醇-4,5-二磷酸）磷酸化为PIP₃（磷脂酰肌醇-3,4,5-三磷酸）。PIP₃作为第二信使，结合PDK1与Akt的PH结构域，使PDK1在Thr308位点磷酸化Akt，mTORC2复合体则在Ser473位点完成Akt的完全激活。

激活的Akt通过磷酸化超过100种底物发挥作用：磷酸化并抑制TSC1/TSC2复合体，解除对mTORC1的抑制，从而促进4E-BP1和S6K1磷酸化，上调蛋白质合成；磷酸化并抑制FOXO转录因子的核入，抑制凋亡基因。关键的肿瘤抑制因子PTEN是PIP₃的磷酸酶，是该通路的天然制动器，其基因在子宫内膜癌中约有50%的突变率。

### Wnt/β-catenin通路：发育与干细胞维持

Wnt通路在无信号状态下，由APC（腺瘤性结肠息肉蛋白）、Axin、GSK-3β和CK1α组成的"破坏复合体"持续磷酸化β-catenin（在Ser33/Ser37/Thr41/Ser45四个位点），被β-TrCP识别后经蛋白酶体降解。

当Wnt配体与细胞表面Frizzled受体及共受体LRP5/6结合后，Dishevelled蛋白被激活，散布复合体中的Axin被招募至受体，GSK-3β活性受到抑制，β-catenin磷酸化减少并在胞质积累，随后转位入核，置换TCF/LEF转录因子上的抑制性辅助因子Groucho，激活靶基因如MYC、CCND1（编码Cyclin D1）和AXIN2。APC蛋白截断突变见于约80%的散发性结直肠癌，导致β-catenin降解障碍。

---

## 实际应用

**靶向治疗药物开发**：MAPK通路中，RAF抑制剂维莫非尼（Vemurafenib）专门靶向BRAF V600E突变（苯丙氨酸被谷氨酸替代），2011年获FDA批准用于黑色素瘤，客观缓解率达48%，远超化疗的5%。然而单药使用会通过CRAF旁路激活引发耐药，催生了MEK抑制剂（曲美替尼/Trametinib）的联合用药策略。

**糖尿病与胰岛素抵抗**：胰岛素信号通过IR→IRS-1→PI3K→Akt→GLUT4转位促进葡萄糖摄取。2型糖尿病患者常表现为Ser/Thr位点的抑制性磷酸化（由JNK或IKKβ执行）阻断IRS-1正常功能，即MAPK通路的"旁路干扰"。二甲双胍通过激活AMPK间接抑制mTORC1，从而部分恢复胰岛素敏感性。

**结直肠癌筛查与诊断**：Wnt通路基因（APC、CTNNB1、AXIN2）的突变状态现被纳入结直肠癌的分子分型，直接影响免疫治疗和靶向治疗方案的选择。对粪便DNA中APC突变的检测是非侵入性癌症早筛的技术基础之一。

---

## 常见误区

**误区一：MAPK通路只调控增殖**。实际上，同一ERK通路在不同细胞类型和信号强度下产生截然相反的效果。在PC12嗜铬细胞瘤细胞中，短暂的EGF刺激激活ERK引发增殖，而持续的NGF刺激同样激活ERK却诱导神经元分化。差别在于信号的持续时间和空间定位（内体上的ERK信号与质膜上的ERK信号功能不同），而非通路本身的"增殖专属性"。

**误区二：抑制一条通路足以杀死肿瘤细胞**。三条通路之间存在大量交叉激活（cross-talk）：Akt可磷酸化RAF的Ser259位点并抑制其活性，而RAS在激活RAF的同时也激活PI3K，MAPK通路的RSK可磷酸化并激活mTOR。单独使用PI3K抑制剂往往会因RAS→RAF→MEK→ERK通路代偿上调而失效，这是临床试验中大量PI3K抑制剂单药疗效不佳的机制原因。

**误区三：Wnt通路只在胚胎发育中起作用**。成体组织中的肠道隐窝干细胞、造血干细胞和毛囊干细胞的自我更新均持续依赖Wnt信号。组织工程领域利用GSK-3β抑制剂（如CHIR99021）激活Wnt通路，是体外扩增干细胞和诱导特定细胞分化（如类器官培养）的标准操作步骤。

---

## 知识关联

理解分子信号通路需要以**细胞信号转导**为基础，特别是受体酪氨酸激酶的自磷酸化机制、G蛋白偶联受体的第二信使系统以及蛋白激酶的催化机理（ATP的γ-磷酸基团转移至底物Ser/Thr/Tyr残基的反应）。若对磷酸化修饰的可逆性理解不足，将难以把握激酶-磷酸酶动态平衡对通路开关状态的调控。

MAPK通路与细胞周期调控紧密相连——ERK激活导致Cyclin D1累积，推动CDK4/6复合体磷酸化Rb蛋白，释放E2F转录因子，是G1/S期过渡的关键节点。PI3K/Akt通路与细胞代谢（尤其是Warburg效应和氨基酸感应）高度整合，其下游mTORC1是代谢重编程研究的核心靶点。Wnt通路的研究则与表观遗传学（β-catenin招募p300/CBP组蛋白乙酰转移酶）和RNA剪接调控形成新兴交叉领域。这三条通路共同构成肿瘤学中**合成致死（synthetic lethality）**策略设计的分子基础。