---
id: "mitochondria"
concept: "线粒体"
domain: "biology"
subdomain: "cell-biology"
subdomain_name: "细胞生物学"
difficulty: 2
is_milestone: false
tags: ["细胞器"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 88.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.90
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "Molecular Biology of the Cell (7th ed.)"
    author: "Bruce Alberts et al."
    isbn: "978-0393884821"
  - type: "textbook"
    title: "Lehninger Principles of Biochemistry (8th ed.)"
    author: "David L. Nelson, Michael M. Cox"
    isbn: "978-1319228002"
  - type: "primary"
    title: "On the Origin of Mitosing Cells"
    author: "Lynn Margulis"
    journal: "Journal of Theoretical Biology"
    year: 1967
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 线粒体

## 概述

线粒体（Mitochondria）是真核细胞中进行有氧呼吸、合成ATP的双膜细胞器，被称为细胞的"动力工厂"。其直径约为0.5–10微米，长度可达数微米，在不同细胞中数量差异极大：肝细胞中约含1000–2000个线粒体，而人类成熟红细胞则完全不含线粒体。线粒体的独特之处在于拥有自身的环状DNA（mtDNA）和核糖体，能够独立合成部分蛋白质。

线粒体最早于1857年由瑞士生理学家鲁道夫·冯·科里克尔（Rudolf von Kölliker）在肌肉细胞中观察到，1898年卡尔·本达（Carl Benda）正式命名为"Mitochondria"，源自希腊语"mitos"（线）和"chondros"（颗粒）。20世纪中叶，彼得·米切尔（Peter Mitchell）于1961年提出化学渗透假说（Chemiosmotic Hypothesis），解释了线粒体内膜如何利用质子梯度驱动ATP合成，他因此获得1978年诺贝尔化学奖。

线粒体对细胞生存至关重要，因为通过有氧呼吸合成的ATP数量远超无氧糖酵解。一分子葡萄糖经糖酵解仅净产生2个ATP，而经线粒体完整有氧氧化可合成约30–32个ATP。因此，心肌细胞、骨骼肌细胞等高能耗细胞中线粒体数量特别丰富。

---

## 核心原理

### 线粒体的双膜结构

线粒体由外膜（Outer Membrane）、内膜（Inner Membrane）、膜间隙（Intermembrane Space）和基质（Matrix）四部分构成。外膜平整光滑，含有大量孔蛋白（Porin），允许分子量小于5000道尔顿的小分子自由通过。内膜则形成大量向内折叠的嵴（Cristae），显著增大了内膜的表面积——嵴上密布着ATP合酶（ATP Synthase，即复合体V）和呼吸链的各种蛋白质复合体（复合体I至IV）。内膜对离子和大多数分子具有高度不通透性，这一特性是建立质子浓度梯度的结构基础。基质中含有参与三羧酸循环（TCA Cycle）的全套酶系、线粒体DNA及70S核糖体。

### 有氧呼吸的三个阶段与线粒体的角色

有氧呼吸分三个阶段，线粒体直接参与其中两个阶段。

**第一阶段**（糖酵解）发生在细胞质基质中，与线粒体无关，1分子葡萄糖分解为2分子丙酮酸，净产生2个ATP和2个NADH。

**第二阶段**（丙酮酸氧化 + 三羧酸循环）在线粒体基质中进行。丙酮酸经丙酮酸脱氢酶复合体转化为乙酰CoA（同时产生CO₂和NADH），乙酰CoA进入TCA循环，每轮循环产生3个NADH、1个FADH₂、1个GTP（等价于1个ATP），并释放2个CO₂。

**第三阶段**（氧化磷酸化）在线粒体内膜上进行。NADH和FADH₂上的电子经呼吸链（复合体I→III→IV）逐级传递给最终电子受体O₂，此过程将H⁺从基质泵入膜间隙，形成质子动力势（Proton Motive Force）。根据米切尔的化学渗透公式：**ΔG = -nFΔΨ + 2.3RT·ΔpH**（n为质子数，F为法拉第常数，ΔΨ为跨膜电位差），质子顺浓度梯度通过ATP合酶回流至基质时，驱动ADP + Pᵢ → ATP。NADH通过呼吸链可驱动约2.5个ATP的合成，FADH₂约驱动1.5个ATP。

### 线粒体DNA与半自主性

人类线粒体DNA（mtDNA）为长度约16,569个碱基对的闭合环状双链分子，编码13种呼吸链蛋白、22种tRNA和2种rRNA。mtDNA缺乏组蛋白保护且修复机制较弱，突变率是核DNA的10–17倍。线粒体虽能自主复制和转录，但仍需核基因组编码的约1500种蛋白质输入才能正常运作，因此称为"半自主性细胞器"。

---

## 实际应用

**法医与母系遗传追踪**：mtDNA严格母系遗传（精子进入卵细胞后，父系线粒体通常被降解），无重组，因此法医可利用mtDNA比对无核DNA组织（如头发、骨骼）的来源，也用于追踪人类母系迁徙路径。"线粒体夏娃"假说正是基于此，推算出现代人类共同母系祖先生活于约15–20万年前的非洲。

**线粒体病与医学**：线粒体功能障碍引起的疾病称线粒体病，如Leber遗传性视神经病（LHON），由mtDNA第11778位点G→A突变导致复合体I功能缺陷，主要影响视网膜神经节细胞，男性发病率高于女性约5倍。

**细胞凋亡**：线粒体在程序性细胞死亡中扮演关键角色。当细胞受损时，Bcl-2家族蛋白调控线粒体外膜通透性，细胞色素c（Cytochrome c）从膜间隙释放入细胞质，触发Caspase级联反应，启动凋亡程序。

---

## 常见误区

**误区一：线粒体是细胞唯一产ATP的场所**
糖酵解在细胞质基质中即可产生ATP，无氧条件下酵母菌和肌肉细胞也能通过底物磷酸化获得能量。线粒体的贡献在于通过氧化磷酸化大幅提升ATP产量，但并非ATP合成的唯一位点。叶绿体的光合磷酸化同样可合成ATP，只是发生在植物和藻类中。

**误区二：线粒体内膜的质子梯度主要靠pH差维持**
实际上，线粒体内膜两侧的质子动力势由两部分构成：电位差（ΔΨ，约-180 mV）和pH差（ΔpH，约0.5–1个单位），在哺乳动物线粒体中**电位差贡献约占总质子动力势的80%以上**，而非pH差为主。忽略电位差会低估驱动ATP合酶的实际能量。

**误区三：线粒体数量固定不变**
线粒体可通过分裂（Fission，由Drp1蛋白介导）和融合（Fusion，由Mfn1/2和OPA1蛋白介导）动态调节形态与数量，形成连续变化的线粒体网络，并通过线粒体自噬（Mitophagy）清除受损个体。这一动态平衡对细胞适应能量需求变化至关重要。

---

## 知识关联

学习线粒体需要先理解**真核细胞**的基本结构，特别是膜系统的概念——正是双层膜结构使线粒体能够建立区室化的代谢环境。若无对膜通透性和磷脂双分子层的认识，难以理解内膜为何能维持质子梯度。

掌握线粒体结构与功能后，可进一步学习**细胞呼吸**的完整代谢通路，包括糖酵解、TCA循环和电子传递链的酶促反应细节，以及在缺氧状态下乳酸发酵和酒精发酵如何代偿ATP的产生。

线粒体拥有自身DNA和70S核糖体这一特征，直接引出**内共生学说**——该学说由林恩·马古利斯（Lynn Margulis）于1967年系统提出，认为线粒体起源于被原始真核细胞吞噬的α-变形菌，两者形成了互利共生关系。线粒体的外膜（对应原始宿主的吞噬体膜）与内膜（对应祖先细菌的细胞膜）起源不同，这一结构特征正是内共生假说的重要佐证。