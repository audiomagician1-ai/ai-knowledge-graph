---
id: "cellular-respiration"
concept: "细胞呼吸"
domain: "biology"
subdomain: "cell-biology"
subdomain_name: "细胞生物学"
difficulty: 3
is_milestone: false
tags: ["代谢"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "textbook"
    title: "Lehninger Principles of Biochemistry (8th ed.)"
    author: "David L. Nelson, Michael M. Cox"
    isbn: "978-1319228002"
  - type: "textbook"
    title: "Molecular Biology of the Cell (7th ed.)"
    author: "Bruce Alberts et al."
    isbn: "978-0393884821"
  - type: "textbook"
    title: "Campbell Biology (12th ed.)"
    author: "Lisa A. Urry et al."
    isbn: "978-0135188743"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---




# 细胞呼吸

## 概述

细胞呼吸（cellular respiration）是细胞将有机物（主要是葡萄糖）中储存的化学能逐步转化为ATP的核心代谢过程。1 mol葡萄糖（180 g）完全氧化释放约2870 kJ自由能，细胞通过耦合反应捕获其中约40%，合成约30–32 mol ATP（真核细胞，考虑线粒体内膜H⁺泄漏等实际损耗；经典教材曾引用38 mol，现代精确测定已修订）。这种逐步释放的方式使每一步能量降落都控制在酶可处理的范围内，避免了葡萄糖直接燃烧时能量以热形式骤散。

细胞呼吸的三条主干途径由20世纪上半叶三代生物化学家相继阐明：糖酵解由古斯塔夫·恩布登（Gustav Embden）、奥托·迈耶霍夫（Otto Meyerhof）和雅各布·帕纳斯（Jakub Parnas）于1930年代完整描述，合称"EMP途径"；柠檬酸循环由汉斯·克雷布斯（Hans Krebs）于1937年提出，获1953年诺贝尔生理学或医学奖；氧化磷酸化的化学渗透机制由彼得·米切尔（Peter Mitchell）于1961年发表于《自然》杂志，获1978年诺贝尔化学奖。权威参考文献见《生物化学》（Lehninger Principles of Biochemistry，Nelson & Cox，W.H. Freeman，第8版，2021）第19–21章。

## 核心原理

### 第一阶段：糖酵解（Glycolysis）

糖酵解在**细胞质基质**中进行，不需要O₂，是所有已知生命（原核与真核）共有的最古老代谢路径。一分子葡萄糖（6碳，C₆H₁₂O₆）经过**10步酶促反应**被裂解为两分子丙酮酸（3碳，C₃H₄O₃⁻）。

整个过程分为两个阶段：

- **投资阶段（第1–5步）**：消耗2个ATP，将葡萄糖磷酸化为1,6-二磷酸果糖（F1,6BP），然后裂解为磷酸二羟丙酮（DHAP）和3-磷酸甘油醛（G3P）。
- **收益阶段（第6–10步）**：每分子三碳中间体产生2 ATP（底物水平磷酸化）和1 NADH，两分子合计产生4 ATP和2 NADH。

**净反应方程式：**

$$\text{C}_6\text{H}_{12}\text{O}_6 + 2\text{NAD}^+ + 2\text{ADP} + 2\text{P}_i \rightarrow 2\text{丙酮酸} + 2\text{NADH} + 2\text{H}^+ + 2\text{ATP} + 2\text{H}_2\text{O}$$

关键限速酶是第3步的**磷酸果糖激酶-1（PFK-1）**：当ATP浓度高（能量充足）时，ATP的别构位点被占据，PFK-1活性降低；当AMP/ADP升高（能量匮乏）时，PFK-1被激活。柠檬酸（TCA循环中间体）也可别构抑制PFK-1，将糖酵解速率与TCA循环通量直接耦合。

**例如：** 肌肉剧烈运动时，ATP迅速水解为ADP与AMP，AMP浓度在数秒内可上升10倍，PFK-1活性随之急剧提高，糖酵解速率可增加至静息状态的100倍以上，以满足短时高强度供能需求。

### 第二阶段：丙酮酸氧化与柠檬酸循环（Pyruvate Oxidation & Krebs Cycle）

**丙酮酸氧化（过渡反应）**

丙酮酸穿过线粒体内膜进入**线粒体基质**后，由**丙酮酸脱氢酶复合体（PDC）**催化氧化脱羧：

$$\text{丙酮酸} + \text{CoA} + \text{NAD}^+ \rightarrow \text{乙酰CoA} + \text{CO}_2 + \text{NADH}$$

PDC由3种酶（E1、E2、E3）和5种辅因子（TPP、硫辛酸、FAD、NAD⁺、CoA）组成，分子量约为9.5 MDa，是细胞中最大的多酶复合体之一。每分子丙酮酸生成1个乙酰CoA、1个CO₂和1个NADH；两分子丙酮酸共贡献2 NADH。

**柠檬酸循环（TCA循环/克雷布斯循环）**

乙酰CoA（2碳乙酰基）与草酰乙酸（OAA，4碳）缩合，生成柠檬酸（6碳），由此启动8步循环反应，最终重新生成草酰乙酸。

每轮循环（对应1分子乙酰CoA）产物：

| 产物 | 数量 | 产生步骤 |
|------|------|----------|
| NADH | 3 | 异柠檬酸脱氢酶、α-酮戊二酸脱氢酶、苹果酸脱氢酶 |
| FADH₂ | 1 | 琥珀酸脱氢酶（复合体Ⅱ） |
| GTP（≈ATP） | 1 | 底物水平磷酸化（琥珀酰CoA合成酶） |
| CO₂ | 2 | 两次氧化脱羧 |

1分子葡萄糖经过**两轮**TCA循环，共产生：6 NADH、2 FADH₂、2 GTP，并将碳原子完全氧化为CO₂排出。

限速酶包括**柠檬酸合酶**（受草酰乙酸浓度制约）、**异柠檬酸脱氢酶**（受ATP/NADH别构抑制）和**α-酮戊二酸脱氢酶**（受琥珀酰CoA和NADH抑制），三处调控共同保证TCA循环与细胞能量状态精确匹配。

### 第三阶段：氧化磷酸化（Oxidative Phosphorylation）

氧化磷酸化发生在**线粒体内膜**上，由电子传递链（ETC，复合体Ⅰ–Ⅳ）和ATP合酶（复合体Ⅴ）共同完成，是全程产ATP最多的阶段。

**电子传递链**

- **复合体Ⅰ（NADH脱氢酶）**：接受NADH的2个电子，将其传递给辅酶Q（CoQ/泛醌），同时将**4个H⁺**从基质泵入膜间隙。
- **复合体Ⅱ（琥珀酸脱氢酶）**：接受FADH₂的电子，传给CoQ，**不泵H⁺**（这正是FADH₂产ATP少于NADH的根本原因）。
- **复合体Ⅲ（细胞色素bc₁复合体）**：经Q循环将电子从CoQH₂传给细胞色素c，泵出**4个H⁺**。
- **复合体Ⅳ（细胞色素c氧化酶）**：将4个电子传给1个O₂，生成2分子H₂O，泵出**2个H⁺**（基质侧消耗4个H⁺参与水形成，净效果相当于跨膜2个H⁺）。

**质子动力势（Proton Motive Force，pmf）**

米切尔（Mitchell, 1961）的化学渗透理论指出，H⁺梯度以两种形式储存能量：

$$\Delta p = \Delta\psi - \frac{2.303RT}{F}\Delta\text{pH}$$

其中 $\Delta\psi$ 为线粒体内膜膜电位（约−180 mV，内负外正），$\Delta\text{pH}$ 约为0.5–1个单位（基质偏碱），两者合计pmf约为−200 mV。

**ATP合酶的旋转催化**

H⁺沿浓度梯度通过ATP合酶F₀亚基的c环回流，驱动c环旋转，带动γ亚单位旋转，每旋转120°合成1个ATP。人线粒体ATP合酶的c环含**8个c亚单位**，故每合成1个ATP需要**8/3 ≈ 2.7个H⁺**通过（Paul Boyer与John Walker因解析ATP合酶旋转催化机制共获1997年诺贝尔化学奖）。

**ATP产量计算**

综合三个阶段，每分子葡萄糖理论产ATP数量如下：

```
阶段               NADH    FADH₂   直接ATP
糖酵解（胞质）       2       0       2
丙酮酸氧化           2       0       0
柠檬酸循环           6       2       2（GTP）
----------------------------------------------
合计                10       2       4

换算（每NADH ≈ 2.5 ATP；每FADH₂ ≈ 1.5 ATP）：
10 × 2.5 + 2 × 1.5 + 4 = 25 + 3 + 4 = 32 ATP
（注：胞质NADH因跨膜转运方式不同，有效产ATP约1.5–2.5，
 此处采用苹果酸-天冬氨酸穿梭计算值2.5）
```

## 关键公式汇总

葡萄糖有氧氧化的总反应方程式：

$$\text{C}_6\text{H}_{12}\text{O}_6 + 6\text{O}_2 + 30\sim32\text{ADP} + 30\sim32\text{P}_i \rightarrow 6\text{CO}_2 + 6\text{H}_2\text{O} + 30\sim32\text{ATP}$$

细胞呼吸商（RQ，Respiratory Quotient）——用于判断燃料类型：

$$RQ = \frac{\text{释放CO}_2\text{的物质的量}}{\text{消耗O}_2\text{的物质的量}}$$

葡萄糖完全氧化时 $RQ = 6/6 = 1.0$；脂肪（以软脂酸为例）氧化时 $RQ ≈ 0.7$；蛋白质氧化时 $RQ ≈ 0.8$。临床上测定患者RQ可间接判断其主要能量底物来源。

## 实际应用

**1. 运动医学与乳酸阈值**

无氧糖酵解速率超过TCA循环与ETC处理能力时，丙酮酸在乳酸脱氢酶催化下还原为乳酸，同时再生NAD⁺以维持糖酵解继续运转。血乳酸浓度超过4 mmol/L时即为"乳酸阈值"，是评估运动强度和有氧耐力的核心指标。马拉松运动员系统训练的目标之一，就是将乳酸阈值对应的跑速从约12 km/h提升至16 km/h以上。

**2. 瓦博格效应（Warburg Effect）与肿瘤代谢**

1924年，奥托·瓦博格（Otto Warburg）发现肿瘤细胞即使在氧气充足条件下也优先使用有氧糖酵解（aerobic glycolysis），产生大量乳酸。这种现象被称为"瓦博格效应"。其机制涉及HIF-1α转录因子上调糖酵解酶表达、线粒体功能受损以及合成代谢对碳骨架的大量需求。PET扫描（正电子发射断层扫描）正是利用肿瘤细胞对¹⁸F-脱氧葡萄糖的高摄取来定位肿瘤病灶，是这一代谢特征最直接的临床应用。

**3. 二甲双胍与糖尿病治疗**

二甲双胍（Metformin）是全球最广泛使用的2型糖尿病药物，其主要作用靶点是**复合体Ⅰ**——轻度抑制复合体Ⅰ活性，降低线粒体ATP产出，激活AMPK（腺苷酸活化蛋白激酶），进而抑制肝糖异生，降低血糖。这一机制直接关联细胞呼吸的氧化磷酸化阶段。

## 常见误区

**误区1："细胞呼吸产生38个ATP"**

38个