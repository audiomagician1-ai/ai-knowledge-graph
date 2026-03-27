---
id: "cell-membrane"
concept: "细胞膜"
domain: "biology"
subdomain: "cell-biology"
subdomain_name: "细胞生物学"
difficulty: 2
is_milestone: false
tags: ["结构"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 89.3
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-03-22"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Fluid mosaic model"
    url: "https://en.wikipedia.org/wiki/Fluid_mosaic_model"
  - type: "textbook-online"
    ref: "Alberts et al. Molecular Biology of the Cell, 4th ed. Ch.11 - NCBI Bookshelf"
    url: "https://www.ncbi.nlm.nih.gov/books/NBK26815/"
  - type: "educational"
    ref: "Khan Academy (中文版) - 细胞膜的结构"
    url: "https://zh.khanacademy.org/science/biology/membranes-and-transport/the-plasma-membrane/a/structure-of-the-plasma-membrane"
  - type: "textbook-online"
    ref: "LibreTexts Biology - Fluid Mosaic Model (OpenStax/Boundless)"
    url: "https://bio.libretexts.org/Bookshelves/Introductory_and_General_Biology/General_Biology_(Boundless)/05%3A_Structure_and_Function_of_Plasma_Membranes/5.02%3A_Components_and_Structure_-_Fluid_Mosaic_Model"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 细胞膜

## 概述

细胞膜（cell membrane），又称质膜（plasma membrane），是包裹细胞内容物、将细胞与外界环境分隔开来的脂质-蛋白质复合薄膜，厚度约为7～10纳米。其化学组成以磷脂和蛋白质为主，同时含有少量糖类（以糖脂和糖蛋白形式存在）。细胞膜并非简单的物理屏障，而是具有高度选择透过性的动态结构，能够精确调控细胞内外物质、能量与信息的交流。

细胞膜研究的历史可追溯至19世纪末。1895年，Ernst Overton通过观察不同化学性质的物质进出细胞的速度，提出细胞表面存在脂质层的假说。1925年，Gorter和Grendel从人红细胞中提取磷脂，展开后测量面积约为细胞表面积的两倍，首次提出**磷脂双分子层**模型。1972年，Singer和Nicolson在大量实验证据基础上提出了著名的**流动镶嵌模型**（fluid mosaic model），成为现代细胞膜结构的经典描述框架，该模型至今仍是理解细胞膜功能的核心参照。

细胞膜的重要性体现在：它维持细胞内稳态（homeostasis），参与细胞识别、信号转导、免疫应答以及能量代谢等几乎所有生命活动。许多遗传性疾病（如囊性纤维化）和病毒感染机制都直接涉及细胞膜蛋白的功能异常。

---

## 核心原理

### 1. 磷脂双分子层的两亲性结构

磷脂分子是构成细胞膜骨架的基本单元，每个磷脂分子由**亲水性磷酸头部**（含甘油、磷酸和胆碱等极性基团）和**疏水性脂肪酸尾部**（两条非极性烃链）组成，这种结构称为两亲分子（amphipathic molecule）。

在水溶液中，磷脂分子自发排列为双分子层：两层磷脂分子的疏水尾部相向内折，远离水环境；亲水头部分别朝向细胞内侧（面向细胞质）和外侧（面向胞外液），形成厚约5纳米的疏水核心区。这一排列方式由热力学原理驱动——减少疏水基团与水分子的接触面积可降低系统自由能，是自发过程，无需消耗ATP。

磷脂尾部的**饱和度**直接影响膜的流动性：含不饱和脂肪酸（如亚油酸，含一个或多个双键）的磷脂尾部呈弯折形态，使双分子层排列疏松，流动性增大；而含饱和脂肪酸的磷脂尾部笔直，排列紧密，流动性较低。细胞可通过调节磷脂脂肪酸的饱和度来适应温度变化。

### 2. 流动镶嵌模型的三大特征

Singer和Nicolson于1972年提出的流动镶嵌模型包含三个关键特征：

- **流动性（fluidity）**：磷脂分子在同一单层内可自由横向扩散，侧向扩散速率约为每秒移动数微米；而从一层翻转至另一层（翻转运动，flip-flop）则极少发生（半衰期可达数小时至数天），需要翻转酶（flippase）催化。膜的流动性受温度、磷脂组成及**胆固醇含量**影响——胆固醇插入磷脂双层中，在高温时限制磷脂分子运动（降低流动性），在低温时阻止磷脂有序排列（防止膜固化），起到"缓冲剂"作用。动物细胞膜中胆固醇约占膜脂质总量的30%～40%。

- **镶嵌性（mosaic）**：蛋白质以不同方式与双分子层结合。**整合膜蛋白**（integral membrane protein）部分或全部嵌入脂质双层，其中跨膜蛋白（transmembrane protein）贯穿整个双层，具有跨膜α螺旋结构域（通常含约20个疏水氨基酸）；**外周膜蛋白**（peripheral membrane protein）通过非共价键附着于膜的内侧或外侧表面，可相对容易地被盐溶液洗脱。

- **不对称性（asymmetry）**：细胞膜两侧的磷脂组成和蛋白质种类均不对称。例如，磷脂酰丝氨酸（PS）正常情况下几乎全部分布于膜内叶（细胞质侧）；当细胞发生凋亡时，PS翻转至外叶，成为凋亡信号，被吞噬细胞识别。糖脂和糖蛋白的糖链则仅分布于膜外表面，共同构成**糖萼**（glycocalyx），参与细胞识别与免疫应答。

### 3. 细胞膜的选择透过性与物质转运

细胞膜的选择透过性使得不同物质以不同机制通过细胞膜：

- **自由扩散**：无需蛋白质协助，物质顺浓度梯度穿越膜。脂溶性小分子（O₂、CO₂、乙醇）及小的非极性分子可直接透过疏水核心；水分子虽是极性分子，亦可缓慢自由扩散，但主要通过**水通道蛋白**（aquaporin，AQP）快速转运，Peter Agre因发现水通道蛋白而获2003年诺贝尔化学奖。

- **协助扩散**：需要转运蛋白（载体蛋白或通道蛋白）协助，但顺浓度梯度进行，不消耗ATP。葡萄糖通过GLUT载体蛋白进入红细胞即属此类。

- **主动运输**：逆浓度梯度转运，必须消耗能量（通常为ATP）。典型例子是Na⁺-K⁺泵（Na⁺/K⁺-ATPase），每水解1个ATP，将3个Na⁺泵出细胞、2个K⁺泵入细胞，维持细胞内外的离子浓度差和膜电位（静息膜电位约为-70 mV）。

---

## 实际应用

**药物靶点设计**：许多药物直接作用于细胞膜上的跨膜蛋白。例如，β受体阻滞剂（如普萘洛尔）通过结合心肌细胞膜上的β-肾上腺素能受体（跨膜G蛋白偶联受体），阻断肾上腺素信号，用于治疗高血压和心律失常。

**渗透作用与医疗实践**：红细胞置于低渗溶液中会因水分大量内渗而膨胀溶血；置于高渗溶液中则皱缩。临床上静脉输液使用0.9% NaCl（生理盐水）或5%葡萄糖溶液，正是为维持与血浆等渗的环境，保护细胞膜完整性。

**囊性纤维化（CF）**：该病由编码CFTR蛋白（囊性纤维化跨膜转导调节蛋白）的基因突变引起。CFTR是细胞膜上的Cl⁻通道，突变导致Cl⁻无法正常分泌至呼吸道黏膜，水分随之减少，黏液变稠，引发严重肺部感染。

---

## 常见误区

**误区一：细胞膜是静态的固体结构**
许多初学者将细胞膜想象为固定不动的硬壳。实际上，在37°C体温条件下，细胞膜具有类似液晶的流动状态，磷脂分子每秒可横向移动约1～2微米，蛋白质也可在膜平面内扩散（部分蛋白质除外，因细胞骨架锚定而受限）。流动性对于膜融合、胞吞、胞吐等过程不可缺少。

**误区二：所有物质都能自由通过细胞膜**
细胞膜的选择透过性常被误解为"半透膜只允许水通过"或"小分子都能自由通过"。实际上，带电的离子（Na⁺、K⁺、Cl⁻）即使分子量极小，也因其亲水性和电荷而无法直接穿越疏水核心，必须经由离子通道或载体蛋白转运。氨基酸、核苷酸等极性分子同样需要专门的转运蛋白。

**误区三：细胞膜两侧完全相同（对称性假设）**
流动镶嵌模型强调膜的不对称性，但学生常忽视这一点。膜脂的不对称分布（如PS分布于内叶）和糖基化修饰仅在外叶的特点，对细胞功能至关重要。磷脂酰丝氨酸从内叶翻转至外叶是细胞凋亡的早期标志，血小板激活时PS外露还能促进凝血因子结合，启动凝血级联反应。

---

## 知识关联

**前置知识——真核细胞**：真核细胞的学习已建立"膜系统"概念，细胞膜