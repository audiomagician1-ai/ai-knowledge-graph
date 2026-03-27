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
last_scored: "2026-03-22"

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
updated_at: 2026-03-27
---


# DNA复制

## 概述

DNA复制是细胞在分裂前将遗传信息精确复制一份的分子过程，使每个子细胞都能获得与亲代细胞完全相同的DNA分子。这一过程遵循**半保留复制**原则：每条新合成的DNA双链由一条亲代旧链和一条新合成链组成，而非全部分解后重新组装。这意味着亲代DNA的两条链分别充当模板，各自引导一条互补新链的合成。

半保留复制原则于1958年由**马修·梅塞尔森（Matthew Meselson）与富兰克林·斯塔尔（Franklin Stahl）**用氮同位素标记实验证实。他们将大肠杆菌在含¹⁵N（重氮）的培养基中培养数代，再转入含¹⁴N（轻氮）的培养基中，通过氯化铯密度梯度离心检测DNA，发现第一代全为中间密度、第二代出现中间密度与轻密度各半的两条带，与半保留复制的预测完全吻合。

DNA复制的忠实度极高，大肠杆菌每复制约**10⁹个碱基对**才发生一次未经纠正的错误，这种精确性由DNA聚合酶的校对功能和错配修复机制共同保障，是遗传信息跨代传递稳定性的物质基础。

---

## 核心原理

### 复制起始与复制叉的形成

DNA复制并非从链的任意位置启动，而是从特定序列——**复制起始点（origin of replication，ori）**开始。大肠杆菌只有**一个**复制起始点，称为 *oriC*，长约245 bp，富含AT碱基对（因AT间仅有2个氢键，熔解温度较低，易于解链）。真核细胞基因组庞大，则拥有**数千个**复制起始点，以便在有限的S期（约6~8小时）内完成全基因组复制。

解旋酶（helicase）在ATP水解驱动下沿复制叉方向移动，持续打开亲代双链，形成向两侧延伸的**Y形复制叉（replication fork）**。解旋造成的扭转张力由**拓扑异构酶II（topoisomerase II）**切断、旋转并重新连接双链来释放，防止链缠绕打结。单链结合蛋白（SSB）随即覆盖已解开的单链，防止其重新形成双链或被核酸酶降解。

### DNA聚合酶的工作机制

DNA聚合酶是复制的核心催化酶，但它有两个重要限制：
1. **只能以5'→3'方向延伸链**，不能反向合成；
2. **不能从头起始合成**，必须在已有3'-OH末端的基础上延伸。

为满足第二个条件，**引发酶（primase）**先合成一段约10个核糖核苷酸的**RNA引物**，提供3'-OH末端。大肠杆菌中主要负责复制的酶是**DNA聚合酶III（Pol III）**，其核心酶包含α（聚合）、ε（3'→5'外切酶校对）、θ三个亚基，β滑动夹（β-clamp）将全酶固定在模板上，大幅提升持续合成能力（processivity），可在不脱落的情况下合成数千个碱基。

### 前导链与滞后链的不对称合成

由于两条模板链极性相反（一条3'→5'，一条5'→3'），而聚合酶只能5'→3'延伸，导致两条新链的合成方式截然不同：

- **前导链（leading strand）**：以3'→5'的模板链为基础，可在一条引物引导下**连续合成**，方向与复制叉推进方向相同。
- **滞后链（lagging strand）**：以5'→3'的模板链为基础，必须周期性地**反向合成**一系列约1000~2000 bp（原核）或100~200 bp（真核）的**冈崎片段（Okazaki fragments）**，每段均需一个RNA引物。

冈崎片段合成完毕后，**DNA聚合酶I（Pol I）**利用其5'→3'外切酶活性切除RNA引物并以DNA填补缺口，最后由**DNA连接酶（ligase）**消耗NAD⁺（原核）或ATP（真核）将相邻片段共价连接，形成完整的滞后链。

---

## 实际应用

**PCR技术的热循环原理**直接借鉴了DNA复制的链解离与聚合步骤：高温变性模拟解链，退火步骤对应引物与模板结合，延伸阶段由耐热的*Taq* DNA聚合酶（来自嗜热菌 *Thermus aquaticus*）完成5'→3'方向的新链合成。PCR每循环约30分钟，经30个循环可将目标片段扩增约10⁹倍。

**抗肿瘤与抗病毒药物**利用了DNA聚合酶对底物的高选择性。氟达拉滨（fludarabine）、阿昔洛韦（acyclovir）等核苷类似物缺少3'-OH，一旦掺入新链即终止延伸，从而抑制癌细胞或病毒的DNA复制，而对宿主正常细胞的影响相对较小。

**端粒酶（telomerase）**解决了线性DNA复制时两端逐渐缩短的"末端复制问题"——每次复制滞后链末端的RNA引物去除后留下的缺口无法填补，导致端粒每次缩短约50~200 bp。端粒酶携带自身RNA模板，能逆转录延长端粒序列，在干细胞和癌细胞中高度活跃。

---

## 常见误区

**误区一：半保留复制等于"保留半条链"**
半保留中的"半"指的是保留**一整条亲代链**，而非一段。每个子代DNA分子中，一条链完全来自亲代（旧链），另一条完全是新合成的，两条链各占一半，绝非亲代链被切碎后分散保留。

**误区二：DNA聚合酶直接从头启动复制**
许多初学者认为DNA聚合酶可以独自开始合成。实际上，Pol III必须依赖引发酶先合成RNA引物才能工作。若没有3'-OH，聚合酶无法催化第一个磷酸二酯键的形成，这也是体外PCR必须添加人工合成引物的原因。

**误区三：复制叉上两条新链都是连续合成的**
复制叉推进时，滞后链因合成方向与解链方向相反，必然以冈崎片段方式不连续合成。认为两条链均连续合成忽略了DNA聚合酶方向性的约束，也无法解释RNA引物的周期性出现和DNA连接酶在复制中的必要性。

---

## 知识关联

**前置知识——DNA结构**：理解DNA复制需要知道双螺旋中碱基互补配对规则（A-T、G-C）以及两条链3'→5'和5'→3'的反向平行关系，这直接决定了为何需要前导链与滞后链两种不同的合成模式。链的极性也解释了为何聚合酶只能单向延伸。

**后续概念——PCR技术**：PCR技术在试管中人工模拟了DNA复制的核心步骤，但用热变性替代解旋酶、用人工引物替代引发酶，并选用耐热聚合酶循环操作。掌握DNA复制中引物功能、聚合酶方向性和链延伸机制，是理解PCR引物设计（为何需要正反两条引物）和扩增特异性的直接基础。