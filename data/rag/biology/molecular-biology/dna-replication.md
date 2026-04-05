---
id: "dna-replication"
concept: "DNA复制"
domain: "biology"
subdomain: "molecular-biology"
subdomain_name: "分子生物学"
difficulty: 3
is_milestone: false
tags: ["核酸"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - DNA replication"
    url: "https://en.wikipedia.org/wiki/DNA_replication"
  - type: "textbook-online"
    ref: "NCBI Bookshelf - DNA Replication Mechanisms"
    url: "https://www.ncbi.nlm.nih.gov/books/NBK26850/"
  - type: "educational"
    ref: "Khan Academy - Molecular mechanism of DNA replication"
    url: "https://www.khanacademy.org/science/ap-biology/gene-expression-and-regulation/replication/a/molecular-mechanism-of-dna-replication"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---



# DNA复制

## 概述

DNA复制是指细胞在分裂之前，以亲代双链DNA为模板，合成两条与亲代序列完全相同的子代DNA分子的过程。这一过程发生在细胞周期的S期（DNA合成期），真核生物的DNA复制在细胞核内进行，而原核生物则在拟核区域完成。DNA复制保证了遗传信息从亲代细胞准确传递到子代细胞。

1953年，Watson和Crick在提出DNA双螺旋模型时即预测，碱基互补配对规则（A-T、G-C）天然地为复制提供了模板机制。1958年，Matthew Meselson和Franklin Stahl利用氮同位素（¹⁴N和¹⁵N）标记大肠杆菌DNA，通过密度梯度离心实验，直接证明了DNA复制遵循**半保留复制**方式——每个子代DNA分子中，一条链来自亲代，另一条链是新合成的。

DNA复制的高保真性至关重要：大肠杆菌每复制约10⁹个碱基对才出现约1个错误，真核生物的错误率更低。这种精确性依赖于碱基互补配对的选择性、DNA聚合酶的校对功能，以及复制后的错配修复系统共同保障。

## 核心原理

### 半保留复制机制

半保留复制意味着亲代双链DNA的两条链在复制过程中彼此分离，各自作为模板指导新链合成。复制完成后产生的两个子代DNA分子，每个都含有一条旧链（模板链）和一条新合成链。Meselson-Stahl实验中，第一代子代菌落的DNA密度恰好介于纯¹⁴N和纯¹⁵N之间，第二代出现两种密度的分子，与半保留模型精确吻合，排除了全保留复制和弥散复制模型。

### 复制起点与复制叉

DNA复制并非从双链的任意位置开始，而是从特定的**复制起点（Origin of Replication，ori）**出发。大肠杆菌只有1个复制起点（oriC，约245 bp），复制是双向的，形成两个向相反方向移动的**复制叉**，最终在终止区域相遇。人类细胞基因组约含30亿个碱基对，拥有数万个复制起点，多个复制叉同时工作，将S期时间压缩至约8小时。每两个相邻复制起点之间的复制单位称为**复制子（replicon）**。

复制叉上，亲代双链因**解旋酶（helicase）**的作用被解开，每次解旋都会在前方产生正超螺旋张力，由**拓扑异构酶Ⅱ（topoisomerase II）**切断双链并重接来消除该张力。**单链结合蛋白（SSB）**则稳定已解链的单链模板，防止其重新碱基配对。

### DNA聚合酶与链合成方向

DNA聚合酶只能以5'→3'方向延伸新链，即沿模板链的3'→5'方向读取模板，将脱氧核苷三磷酸（dNTP）连接到已有链的3'-OH末端，同时释放焦磷酸（PPi）。反应的化学本质是：

> dNMP + (dNMP)ₙ → (dNMP)ₙ₊₁ + PPi

由于两条模板链方向相反，**前导链（leading strand）**沿复制叉移动方向连续合成；**滞后链（lagging strand）**则只能间断地合成一系列约100–200 nt（真核）或1000–2000 nt（原核）的**冈崎片段（Okazaki fragments）**，随后由DNA连接酶将片段连接。

DNA聚合酶自身无法从头开始合成新链，必须依赖**引发酶（primase）**先合成一小段RNA引物（约5–10 nt），提供3'-OH起点。在大肠杆菌中，负责延伸的主要酶是**DNA聚合酶Ⅲ（Pol Ⅲ）**，它的错误率约为10⁻⁵，经3'→5'外切酶校对后降至10⁻⁷，再经错配修复后综合错误率达10⁻⁹~10⁻¹⁰量级。

## 实际应用

**PCR技术的设计基础**：PCR（聚合酶链反应）正是模拟DNA复制原理，通过变性-退火-延伸三步循环，在体外扩增目标DNA片段。Taq聚合酶在95°C高温下仍保持活性，正是因为理解了DNA聚合酶的催化机制才得以筛选开发。

**抗病毒药物靶点**：核苷类似物（如治疗HIV的叠氮胸苷AZT）结构上与正常dNTP相似，但其3'位无羟基，一旦掺入新链即终止延伸，从而抑制病毒DNA复制而不影响宿主细胞（有一定选择性）。这一设计直接针对DNA聚合酶的延伸反应。

**DNA复制错误与癌变**：若碱基错配修复基因（如MLH1、MSH2）发生突变，DNA复制错误积累，导致微卫星不稳定，是林奇综合征（遗传性非息肉性结直肠癌）的主要分子机制之一。

## 常见误区

**误区一：DNA聚合酶可以直接起始合成新链**
事实上所有已知的DNA聚合酶都无法从头合成新链，必须有引物存在才能延伸。引物在复制完成后被DNA聚合酶Ⅰ（原核）替换为DNA，并由DNA连接酶封口。忽略引物的必要性会导致对PCR体系设计和端粒缩短问题的误解。

**误区二：前导链和滞后链的合成速度相同**
滞后链因需要反复合成冈崎片段、切除RNA引物、填补缺口并连接，整体效率低于前导链。两条链在同一复制叉协调进行，但滞后链的合成模式（不连续合成）是区分两者的本质特征，而非速度差异导致复制叉不对称。

**误区三：半保留复制意味着每次复制旧链都"消耗"掉**
半保留复制中旧链并未降解，而是保留在子代DNA中。经过n次复制后，含有亲代链的DNA分子始终只有2个（其中各含1条原始链），其余全部是新合成的双链。Meselson-Stahl实验中第三代¹⁵N重链完全消失正是此规律的体现。

## 知识关联

学习DNA复制需要先掌握**DNA双螺旋结构**：碱基互补配对（A=T双氢键、G≡C三氢键）是模板机制的化学基础，3'→5'方向性决定了聚合酶的合成方向，反平行结构解释了前导链与滞后链差异的根本原因。

DNA复制直接衔接**PCR技术**：PCR将体内DNA复制的核心要素——热变性代替解旋酶、人工引物代替引发酶、耐热Taq聚合酶——转移到体外可控体系，理解DNA复制的每个步骤有助于掌握PCR的引物设计原则（如引物不能与自身形成发卡结构）和循环参数设置逻辑。此外，DNA复制中的错误修复机制与**基因突变**和**肿瘤分子生物学**密切相关，复制后修复缺陷是多种遗传病的分子基础。