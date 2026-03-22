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
---
# DNA复制

## 概述

DNA复制（DNA Replication）是细胞精确复制其DNA分子的过程，发生在细胞周期的**S期**（合成期）。这一过程对于生物遗传、细胞分裂和损伤组织修复至关重要——它确保每个新产生的子细胞都获得一份完整的DNA拷贝（Wikipedia: DNA replication）。

DNA复制是**半保留复制**（semiconservative replication）：双螺旋的两条链分别作为模板，各自合成一条新的互补链。因此每个子代DNA分子都包含一条来自亲代的原始链和一条新合成的链。这一机制由 Meselson 和 Stahl 在 1958 年通过同位素密度梯度离心实验证实（Khan Academy）。

## 核心知识点

### DNA结构基础

DNA由两条反向平行的核苷酸链组成双螺旋结构。四种碱基通过氢键配对：**腺嘌呤(A)-胸腺嘧啶(T)**（2个氢键）、**鸟嘌呤(G)-胞嘧啶(C)**（3个氢键）。每条链有方向性：5'端和3'端，两条链反向平行排列（Wikipedia: DNA replication）。

### 复制机器——关键酶和蛋白质

**解旋酶（Helicase）**：在复制起始位点（origin of replication）解开双螺旋，形成**复制叉**（replication fork），复制叉向两个方向双向延伸。

**DNA聚合酶（DNA Polymerase）**：核心复制酶，按5'→3'方向合成新链，具有**校对功能**（proofreading，3'→5'外切核酸酶活性）。原核生物中 DNA Pol III 是主要复制酶，真核生物中 DNA Pol ε（前导链）和 DNA Pol δ（滞后链）执行主要合成（NCBI Bookshelf）。

**引物酶（Primase）**：合成短的RNA引物（约10个核苷酸），为DNA聚合酶提供3'-OH起始点——因为DNA聚合酶**不能从头合成**，只能延伸已有的链。

**拓扑异构酶（Topoisomerase）**：缓解解旋产生的超螺旋张力。

### 前导链 vs 滞后链

由于DNA聚合酶只能5'→3'合成：
- **前导链（Leading strand）**：朝向复制叉方向连续合成，仅需一个引物
- **滞后链（Lagging strand）**：远离复制叉方向不连续合成，产生多个短片段——**冈崎片段**（Okazaki fragments），原核生物约1000-2000核苷酸/片段，真核生物约100-200核苷酸/片段
- **DNA连接酶（Ligase）**：将冈崎片段连接成完整链

### 复制保真性

DNA复制的错误率极低：约 10⁻⁹ ~ 10⁻¹⁰ 每碱基对每次复制。保真机制包括：
1. **碱基选择**：聚合酶活性位点的几何约束（错误率 ~10⁻⁴）
2. **校对**：3'→5'外切核酸酶立即纠正错配（降低 ~100倍）
3. **错配修复（MMR）**：复制后修复系统检测并纠正残余错误（再降低 ~100倍）

## 关键要点

1. DNA复制是半保留的——每个子代分子含一条旧链和一条新链（Meselson-Stahl 1958）
2. DNA聚合酶只能 5'→3' 合成，导致前导链连续合成、滞后链不连续合成（冈崎片段）
3. 复制起始于特定位点（origin），双向进行形成复制叉
4. 引物酶合成RNA引物是必须的——DNA聚合酶不能从头起始
5. 三重保真机制使错误率达到约 10⁻⁹ ~ 10⁻¹⁰/碱基对/复制

## 常见误区

1. **"DNA聚合酶可以双向合成"**——聚合酶只能 5'→3' 方向添加核苷酸，这是滞后链必须不连续合成的根本原因
2. **"复制从DNA任意位置开始"**——复制起始于特定的起始位点（大肠杆菌有1个，人类细胞有约30,000-50,000个）
3. **"RNA引物会留在DNA中"**——引物在合成后被DNA聚合酶I（原核）或RNase H（真核）去除，空隙由DNA填补

## 知识衔接

- **先修**：DNA结构、碱基配对规则
- **后续**：基因表达（转录和翻译）、DNA修复机制、PCR技术
