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
---
# 线粒体

## 概述

线粒体是真核细胞中负责有氧呼吸和 ATP 合成的双层膜细胞器，常被称为"细胞的发电厂"。一个典型的人类细胞含有约 1,000-2,000 个线粒体，占细胞体积的 10-20%（Alberts et al., *Molecular Biology of the Cell*, 7th ed.）。心肌细胞和肝细胞中线粒体数量更多，反映了这些组织极高的能量需求。线粒体的独特之处在于它拥有自己的 DNA 和核糖体——这一事实是内共生学说的关键证据。

## 核心知识点

### 1. 线粒体的结构

线粒体具有独特的**双膜结构**，形成了四个功能区隔：

**外膜（Outer Membrane）**
- 厚约 6-7 nm，含大量孔蛋白（porin/VDAC），允许分子量 < 5000 Da 的小分子自由通过
- 与内质网膜存在物理接触点（MAM, Mitochondria-Associated ER Membrane），参与钙信号传递和脂质交换

**膜间隙（Intermembrane Space）**
- 宽约 10-20 nm，pH 约 7.0（比基质低约 0.7 个单位）
- 电子传递链将 $H^+$ 泵入此空间，建立用于 ATP 合成的质子梯度
- 含细胞色素 c（电子传递链关键载体）

**内膜（Inner Membrane）**
- 高度折叠形成**嵴（cristae）**，极大增加表面积（展开后面积可达外膜的 5 倍）
- 不含孔蛋白，对离子高度不通透——这对维持质子梯度至关重要
- 富含心磷脂（cardiolipin，约占脂质的 20%），这种脂质在细菌膜中也大量存在（内共生的痕迹）
- 嵌有电子传递链复合物 I-IV 和 ATP 合酶

**基质（Matrix）**
- 内膜包围的内部空间，pH 约 7.7-8.0
- 含三羧酸循环（TCA/Krebs cycle）的全部酶、脂肪酸氧化酶系
- 含 mtDNA（人类为 16,569 bp 的环状双链 DNA）、线粒体核糖体（55S，小于细胞质的 80S）

### 2. 氧化磷酸化：ATP 的生产线

线粒体内膜上的**电子传递链（ETC）**和 **ATP 合酶**协同完成 ATP 合成：

**电子传递链**由四个蛋白复合物组成：

| 复合物 | 名称 | 功能 | 泵出 $H^+$ 数 |
|--------|------|------|---------------|
| I | NADH 脱氢酶 | NADH 氧化，将电子传给辅酶Q | 4 |
| II | 琥珀酸脱氢酶 | FADH2 氧化（TCA 循环酶） | 0 |
| III | 细胞色素 bc1 | 电子从辅酶Q传给细胞色素 c | 4 |
| IV | 细胞色素 c 氧化酶 | 电子最终传给 $O_2$，生成 $H_2O$ | 2 |

每对电子从 NADH 传递到 $O_2$ 共泵出约 10 个 $H^+$，建立约 150-200 mV 的跨膜电位差（$\Delta\psi$）。

**ATP 合酶（复合物 V）**是一个分子旋转马达：$H^+$ 顺浓度梯度回流驱动 $F_0$ 亚基旋转，带动 $F_1$ 亚基催化 ADP + Pi -> ATP。每旋转 360 度合成约 3 个 ATP。实验测量表明，$F_0$ 转子转速可达约 130 转/秒（Yoshida et al., 2001）。

**总产量**：一分子葡萄糖完全氧化的理论产量约 **30-32 ATP**（旧教科书常写 36-38，已被修正为考虑了质子泄漏和转运消耗后的更准确值）。

### 3. 线粒体 DNA 与内共生起源

1967年，Lynn Margulis 提出**内共生学说**：线粒体起源于约 20 亿年前一个被古核细胞吞噬但未被消化的 $\alpha$-变形菌。

支持内共生学说的证据：

| 特征 | 线粒体 | 细菌 | 真核细胞质 |
|------|--------|------|-----------|
| DNA 形状 | 环状 | 环状 | 线状 |
| 核糖体 | 55S | 70S | 80S |
| 膜脂质 | 含心磷脂 | 含心磷脂 | 不含 |
| 分裂方式 | 二分裂 | 二分裂 | 有丝分裂 |
| 抗生素敏感性 | 对氯霉素敏感 | 对氯霉素敏感 | 不敏感 |

人类 mtDNA 仅编码 37 个基因（13 个蛋白质、22 个 tRNA、2 个 rRNA），而线粒体约需 1,500 种蛋白质——其余基因在进化中转移到了细胞核。mtDNA 遵循**母系遗传**（精子线粒体在受精后被降解），这使得 mtDNA 成为追踪人类迁徙的重要工具（例如"线粒体夏娃"研究）。

### 4. 线粒体的动态行为

线粒体不是静态的"豆子形"细胞器，而是高度动态的网络：

- **融合（fusion）**：由 Mfn1/Mfn2（外膜）和 OPA1（内膜）介导。融合允许损伤线粒体共享健康的 mtDNA 和蛋白质。
- **分裂（fission）**：由 Drp1 介导。分裂产生小的线粒体，便于沿细胞骨架运输到高能需部位（例如神经元突触末梢）。
- **自噬（mitophagy）**：PINK1/Parkin 通路标记损伤的线粒体进行降解。PINK1 或 Parkin 基因突变导致损伤线粒体积累，与**帕金森病**密切相关（Kitada et al., 1998）。

### 5. 线粒体与疾病

线粒体功能障碍与多种疾病相关：

- **线粒体遗传病**：mtDNA 突变导致的疾病（如 Leber 遗传性视神经病变、MELAS 综合征），因母系遗传而有独特的家系模式
- **神经退行性疾病**：帕金森病（PINK1/Parkin）、阿尔茨海默病（线粒体碎片化增加）
- **衰老**：mtDNA 突变随年龄积累，氧化损伤加剧，ATP 产量下降——"线粒体衰老假说"
- **癌症**：Warburg 效应——肿瘤细胞即使在有氧条件下也偏好糖酵解而非氧化磷酸化（可能与线粒体信号异常有关）

## 关键要点

1. 双膜四区隔结构：外膜（通透）、膜间隙（$H^+$富集）、内膜（嵴，ETC + ATP合酶）、基质（TCA循环 + mtDNA）
2. 氧化磷酸化：电子传递链建立质子梯度，ATP 合酶利用梯度合成 **30-32 ATP/葡萄糖**
3. 内共生起源：线粒体源自 $\alpha$-变形菌，保留环状 DNA、55S 核糖体、二分裂等细菌特征
4. 高度动态：融合/分裂/自噬维持线粒体质量控制，PINK1/Parkin 缺陷与帕金森病相关
5. mtDNA 母系遗传，仅编码 37 个基因，是人类群体遗传学的重要工具

## 常见误区

1. **"线粒体是细胞唯一的 ATP 来源"**：错。糖酵解在细胞质中也产生 ATP（每分子葡萄糖 2 ATP），且红细胞没有线粒体，完全依赖糖酵解供能。
2. **"线粒体只负责产能"**：线粒体还参与钙离子调节、脂肪酸氧化、血红素合成、铁硫簇组装、细胞凋亡（释放细胞色素 c 激活 caspase 级联）等多种功能。
3. **"每分子葡萄糖产 36 或 38 个 ATP"**：这是过时的教科书数值。考虑质子泄漏和 NADH/FADH2 的转运消耗后，更准确的值为 **30-32 ATP**（Nelson & Cox, *Lehninger*, 8th ed.）。
4. **"线粒体 DNA 只来自母亲所以和父亲无关"**：虽然 mtDNA 确实母系遗传，但线粒体的绝大多数蛋白质（~1500种）是由核基因编码的，这些基因遵循双亲遗传。

## 知识衔接

### 先修知识
- **真核细胞** — 理解真核细胞的膜性区隔化特征是学习线粒体结构的前提
- **细胞膜** — 膜的选择通透性原理是理解线粒体内膜质子梯度的基础

### 后续学习
- **细胞呼吸** — 糖酵解、TCA 循环、氧化磷酸化的完整代谢通路
- **内共生学说** — 线粒体和叶绿体共同支持的真核细胞演化理论

## 参考文献

1. Alberts, B. et al. (2022). *Molecular Biology of the Cell* (7th ed.). W.W. Norton. ISBN 978-0393884821. Ch.14.
2. Nelson, D.L. & Cox, M.M. (2021). *Lehninger Principles of Biochemistry* (8th ed.). W.H. Freeman. ISBN 978-1319228002. Ch.19.
3. Margulis, L. (1967). On the Origin of Mitosing Cells. *Journal of Theoretical Biology*, 14(3), 225-274.
4. Kitada, T. et al. (1998). Mutations in the parkin gene cause autosomal recessive juvenile parkinsonism. *Nature*, 392, 605-608.
