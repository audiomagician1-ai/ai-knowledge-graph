---
id: "rna-interference"
concept: "RNA干扰"
domain: "biology"
subdomain: "molecular-biology"
subdomain_name: "分子生物学"
difficulty: 4
is_milestone: false
tags: ["调控"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# RNA干扰

## 概述

RNA干扰（RNA interference，RNAi）是一种由双链RNA（dsRNA）触发的序列特异性基因沉默机制，通过降解互补mRNA或抑制其翻译来下调特定基因的表达。1998年，Andrew Fire和Craig Mello在线虫（*Caenorhabditis elegans*）中注射dsRNA时意外发现：正义链RNA与反义链RNA单独注射的效果远弱于两者同时注射，且注射量极少的dsRNA即可引发强烈的基因沉默效应。这一发现推翻了此前对反义RNA机制的解释，Fire和Mello因此于2006年获得诺贝尔生理学或医学奖。

RNA干扰在生物学上承担着多重天然功能：抵御外源病毒RNA的入侵、抑制转座子在基因组中的跳跃、以及通过微小RNA（miRNA）调控发育过程中数百个靶基因的时序表达。在技术层面，RNAi已成为基因功能研究的标准工具，并在遗传疾病和肿瘤治疗中展现出显著的临床潜力——2018年美国FDA批准的Patisiran（Onpattro）是首个基于siRNA的获批药物，用于治疗遗传性甲状腺素转运蛋白淀粉样变性。

## 核心原理

### Dicer酶的切割与RISC的组装

RNAi的启动依赖于RNase III家族的Dicer酶。当细胞内出现长dsRNA（通常>30 bp）或含有发夹结构的前体miRNA（pre-miRNA）时，Dicer识别并切割这些RNA，产生长度约为21-23个核苷酸的小RNA双链，其3'端各有2个核苷酸的悬突（overhang）——这种结构特征是判断Dicer产物的分子标志。

切割产生的小RNA双链随后被加载到RNA诱导沉默复合物（RNA-induced silencing complex，RISC）中。RISC的核心催化组分是Argonaute（AGO）蛋白家族。在RISC组装时，小RNA双链的两条链中，热力学上5'端较不稳定的那条链（称为"引导链"guide strand）优先保留在AGO蛋白中，另一条"过客链"（passenger strand）被降解。人类基因组编码4种AGO蛋白（AGO1-4），其中AGO2具有"切割酶"（slicer）活性，能直接切割与引导链完全互补的靶mRNA。

### siRNA与miRNA的作用机制差异

siRNA（小干扰RNA）通常来源于外源dsRNA或人工导入，与靶mRNA的互补程度接近100%，由AGO2介导的RISC在与靶mRNA完全互补配对后，于引导链5'端第10-11位核苷酸之间切割靶mRNA磷酸二酯骨架，导致mRNA迅速降解。这种精准的一对一靶向关系意味着一种siRNA通常只沉默一个特定基因。

miRNA（微小RNA）由内源基因转录为初级转录本pri-miRNA，经核内Drosha/DGCR8复合物切割成约60-70 nt的前体pre-miRNA，出核后再被Dicer进一步切割成成熟miRNA双链。成熟miRNA与靶mRNA通常为不完全互补配对，主要通过"种子序列"（seed sequence，位于miRNA 5'端第2-8位核苷酸）识别靶mRNA 3'非翻译区（3'UTR）。不完全互补配对导致RISC不切割靶mRNA，而是通过抑制核糖体翻译或促进mRNA去帽和去腺苷酸化降解来下调蛋白表达。一个miRNA可调控数百个下游靶基因，例如miR-21在多种肿瘤中高表达，已知靶基因包括*PTEN*、*PDCD4*等肿瘤抑制因子。

### 信号扩增机制

在线虫等生物中，RNA依赖的RNA聚合酶（RdRP）可以靶mRNA为模板合成新的dsRNA，从而生成更多siRNA，产生信号放大效应，使极微量的初始dsRNA即可维持长期的基因沉默。哺乳动物细胞中缺乏功能性RdRP，因此RNAi效果会随细胞分裂而稀释，这也是siRNA在哺乳动物细胞中通常只能维持数天到一周效果的分子原因。

## 实际应用

**全基因组功能筛选**：利用siRNA文库对人类所有约20,000个基因逐一敲低，可系统鉴定特定表型（如病毒感染抵抗、药物敏感性）的遗传决定因素。例如，通过全基因组siRNA筛选鉴定出HDAC1是流感病毒复制的宿主因子。

**疾病治疗**：siRNA药物Inclisiran靶向PCSK9基因的mRNA，单次皮下注射可将低密度脂蛋白（LDL）胆固醇水平降低约50%，效果维持6个月以上，于2020年获欧洲药品管理局（EMA）批准用于高胆固醇血症治疗。其长效性依赖于GalNAc（N-乙酰半乳糖胺）化学修饰使siRNA靶向肝细胞递送。

**农业应用**：通过在转基因植物中表达dsRNA，沉默害虫摄食后体内的必需基因。玉米根虫（*Diabrotica virgifera*）摄入靶向其*Snf7*基因的dsRNA后，幼虫死亡率显著提高，孟山都公司已将此策略用于SmartStax Pro玉米品系的研发。

## 常见误区

**误区一：认为siRNA和miRNA仅在序列长度上有差异。** 两者的根本区别在于生物发生途径、与靶mRNA的互补程度及沉默机制：siRNA来自外源或人工dsRNA，需要100%互补才能切割靶标；miRNA来自内源发夹结构基因，通过不完全互补的种子序列识别靶标，主要抑制翻译。同一个小RNA在不同互补程度下实际上可以兼具两种功能，例如人工导入的siRNA如果与非靶基因3'UTR存在种子序列匹配，就会产生脱靶效应，模仿miRNA的翻译抑制模式。

**误区二：认为RNA干扰效果是永久性的基因敲除。** RNAi沉默的是mRNA水平，并不改变基因组DNA序列。siRNA本身会被细胞内核酸酶降解，效果通常仅持续数天；而且在哺乳动物细胞中缺乏RdRP扩增机制，沉默效果会随细胞分裂稀释。这与CRISPR-Cas9等基因组编辑工具造成的永久性突变有本质区别。若需长期沉默，需使用慢病毒等载体持续表达shRNA（短发夹RNA）。

**误区三：认为dsRNA在所有生物中都能高效触发RNAi。** 哺乳动物体细胞中，长dsRNA（>30 bp）会激活干扰素（interferon）先天免疫通路，激活PKR激酶和OAS酶，导致全局性蛋白翻译抑制和细胞凋亡，而非特异性基因沉默。因此在哺乳动物细胞中必须使用21-23 nt的短siRNA以规避免疫激活，而线虫、果蝇、植物等生物可直接使用长dsRNA。

## 知识关联

RNA干扰建立在**基因调控**的基础之上——RNAi是转录后调控的典型机制，与启动子甲基化（转录水平调控）形成互补的调控层级。miRNA的靶点预测需要了解mRNA的5'UTR、编码区和3'UTR的功能差异，以及碱基配对的热力学原理。

理解RNAi中RISC的组装和AGO蛋白的功能，需要以**RNA类型**的知识为基础，区分mRNA、rRNA、tRNA和各类非编码小RNA的结构特征。RISC识别靶mRNA的过程本质上依赖Watson-Crick碱基配对规则，但种子序列的不完全配对还涉及G-U摇摆配对和核苷酸堆积能量等物理化学因素。

RNAi与表观遗传调控存在交叉：在某些情境下，RISC可被招募到细胞核，引导组蛋白H3第9位赖氨酸的三甲基化（H3K9me3）和DNA甲基化，实现转录水平的沉默，这一机制在裂殖酵母着丝粒异染色质形成中已有详细描述，展示了RNA介导的表观遗传修饰路径。