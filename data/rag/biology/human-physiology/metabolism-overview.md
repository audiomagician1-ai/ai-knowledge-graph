---
id: "metabolism-overview"
concept: "代谢概览"
domain: "biology"
subdomain: "human-physiology"
subdomain_name: "人体生理学"
difficulty: 2
is_milestone: false
tags: ["代谢"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 82.7
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "academic"
    citation: "Berg, J. M., Tymoczko, J. L., & Stryer, L. (2015). Biochemistry (8th ed.). W. H. Freeman."
  - type: "academic"
    citation: "Hardie, D. G., Ross, F. A., & Hawley, S. A. (2012). AMPK: a nutrient and energy sensor that maintains energy homeostasis. Nature Reviews Molecular Cell Biology, 13(4), 251–262."
  - type: "academic"
    citation: "Roza, A. M., & Shizgal, H. M. (1984). The Harris Benedict equation reevaluated: resting energy requirements and the body cell mass. American Journal of Clinical Nutrition, 40(1), 168–182."
  - type: "academic"
    citation: "Cahill, G. F. (2006). Fuel metabolism in starvation. Annual Review of Nutrition, 26, 1–22."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# 代谢概览

## 概述

代谢（Metabolism）是指生物体内所有化学反应的总和，这些反应使生命体能够维持结构、生长、繁殖并对环境做出响应。代谢可以划分为两大相互对立又协调运作的过程：**合成代谢**（Anabolism）和**分解代谢**（Catabolism）。合成代谢将小分子构建成大分子（如将氨基酸聚合为蛋白质），需要输入能量；分解代谢则将大分子拆解为小分子（如将葡萄糖氧化为CO₂和水），并在此过程中释放可用能量。

代谢研究的历史可追溯至17世纪，荷兰科学家 Santorio Sanctorius（1561—1636）最早通过长达30年的自身实验，系统测量体重、食物摄入与排泄物来量化人体的物质转化，被认为是代谢研究的先驱。进入20世纪，德国生物化学家 Otto Warburg 于1931年因发现细胞呼吸酶的性质和作用方式获得诺贝尔生理学或医学奖。1937年，英国科学家 Hans Krebs 提出三羧酸循环（TCA循环，又称克雷布斯循环）的完整通路，并于1953年获得诺贝尔生理学或医学奖——这一发现奠定了现代代谢生化的核心框架（Berg et al., 2015）。

代谢速率对人体健康具有直接影响。成年人在完全静息状态下，每天基础代谢率（BMR）约为1500—2000千卡，约占总能量消耗的60%—75%。当合成与分解代谢失衡时，会导致肥胖、肌肉萎缩、糖尿病等代谢性疾病，因此理解代谢全貌对临床医学和营养学均具有重要意义。

> **关键问题**：如果一个细胞内ATP/AMP比值突然大幅下降，细胞会优先激活合成代谢还是分解代谢？这种调节是通过哪种关键激酶实现的？

---

## 核心原理

### 合成代谢：能量驱动的分子构建

合成代谢反应以ATP（三磷酸腺苷）作为直接能量货币，将小分子前体合成为复杂生物大分子。典型例子包括：利用葡萄糖-6-磷酸合成糖原（糖原合成），以及利用乙酰CoA合成脂肪酸（脂肪合成）。每合成1分子糖原链需消耗1个UDP-葡萄糖分子并释放焦磷酸，该过程是不可逆的放能驱动反应。

合成代谢还依赖**还原力**，主要以NADPH（还原型烟酰胺腺嘌呤二核苷酸磷酸）的形式提供氢原子，用于将前体分子还原成复杂结构。磷酸戊糖途径（Pentose Phosphate Pathway）是细胞产生NADPH的主要来源，每氧化1分子葡萄糖-6-磷酸可产生2个NADPH分子。

例如，脂肪酸的从头合成（De novo synthesis）每延伸2个碳单位（即加入1个乙酰CoA）需消耗1个ATP和2个NADPH，合成1分子软脂酸（C₁₆:0，棕榈酸）共需消耗7个ATP和14个NADPH，这充分说明合成代谢对还原力的高度依赖。值得注意的是，合成代谢与分解代谢在空间上也存在分隔：脂肪酸合成发生在细胞质基质（胞浆），而脂肪酸β-氧化在线粒体基质中进行，这种区室化设计使两个方向的代谢通路可以同时独立调控，避免"无效循环"（Futile Cycle）造成不必要的能量浪费。

### 分解代谢：能量的逐级释放

分解代谢通过三个主要阶段逐步降解营养物质：

1. **消化/水解阶段**：多糖→单糖、蛋白质→氨基酸、脂肪→甘油+脂肪酸；
2. **中间代谢阶段**：各类单体进入糖酵解（Glycolysis）或β-氧化，转化为乙酰CoA；
3. **终末氧化阶段**：乙酰CoA经三羧酸循环彻底氧化，电子通过氧化磷酸化生成ATP。

以葡萄糖的完全氧化为例，理论上1分子葡萄糖（C₆H₁₂O₆）可净生成约30—32个ATP分子（现代修正值，旧版教材常标注38个），化学总方程式为：

$$C_6H_{12}O_6 + 6O_2 \rightarrow 6CO_2 + 6H_2O \quad \Delta G^{\circ'} = -2870\ \text{kJ/mol}$$

其中实际可捕获用于ATP合成的能量约为 $30 \times 30.5\ \text{kJ/mol} = 915\ \text{kJ/mol}$，热力学效率约为：

$$\eta = \frac{915}{2870} \approx 31.9\%$$

这意味着约68%的化学能以热量形式散失，这正是人体维持37°C体温的重要热量来源之一。相比之下，脂肪酸的能量密度远高于葡萄糖：以软脂酸（C₁₆:0）为例，1分子软脂酸完全氧化可净生成约106个ATP，对应能量密度约为9千卡/克，而碳水化合物仅为约4千卡/克，这也是为何脂肪是长期能量储存的首选形式。

### ATP：合成与分解代谢的能量联结

ATP分子中高能磷酸键水解可释放约 $\Delta G^{\circ'} = -30.5\ \text{kJ/mol}$ 的标准自由能（在细胞实际条件下，由于底物浓度效应，实际自由能释放可高达 $-50\ \text{kJ/mol}$），连接了合成代谢对能量的需求和分解代谢对能量的供给。细胞内ATP的浓度通常维持在1—10 mmol/L，而AMP/ATP比值是感知细胞能量状态的关键信号分子。当该比值升高时，AMPK（AMP激活蛋白激酶）被激活，抑制合成代谢、促进分解代谢，从而使细胞恢复能量平衡（Hardie et al., 2012）。

例如，剧烈运动后肌肉细胞内AMP/ATP比值可在数秒内上升10倍以上，AMPK随即被磷酸化激活（在Thr172位点），迅速启动脂肪酸β-氧化并抑制脂肪酸合成酶（Fatty Acid Synthase, FAS）及乙酰CoA羧化酶（ACC），这是运动促进脂肪消耗的核心分子机制之一。AMPK的这一特性也成为2型糖尿病药物二甲双胍（Metformin）的部分作用靶点——二甲双胍通过抑制线粒体复合体I，间接激活AMPK，促进外周组织对葡萄糖的摄取与氧化分解。

### 代谢率与影响因素

人体的代谢速率受多种因素调控，可用以下关系式近似描述基础代谢率（Harris-Benedict公式，1919年由 J. A. Harris 和 F. G. Benedict 首次发表，1984年由 Roza 和 Shizgal 基于更大样本量修订，Roza & Shizgal, 1984）：

**男性BMR（千卡/天）**：
$$BMR = 88.362 + 13.397 \times W + 4.799 \times H - 5.677 \times A$$

**女性BMR（千卡/天）**：
$$BMR = 447.593 + 9.247 \times W + 3.098 \times H - 4.330 \times A$$

其中 $W$ 为体重（kg），$H$ 为身高（cm），$A$ 为年龄（岁）。

案例：一名30岁女性，身高165 cm，体重60 kg，代入公式：$BMR = 447.593 + 9.247 \times 60 + 3.098 \times 165 - 4.330 \times 30 = 447.593 + 554.82 + 511.17 - 129.9 \approx 1383.7$ 千卡/天。若其日常活动系数为1.55（轻度活跃），则每日总能量消耗约为 $1383.7 \times 1.55 \approx 2145$ 千卡。

此外，甲状腺激素（T₃/T₄）水平对代谢速率影响显著：甲亢患者BMR可比正常值高出50%—100%，而甲减患者BMR可降低30%—40%。体温每升高1°C，代谢速率约提高10%（Van't Hoff经验法则在生理温度范围的近似应用）；骨骼肌是静息状态下最大的单一能量消耗组织，占BMR的约20%—30%；随年龄增长，每10年BMR约下降2%—3%，主要原因是肌肉量（去脂体重）的逐渐减少。

---

## 关键公式与模型

### 呼吸商（RQ）：判断底物利用的定量工具

呼吸商（Respiratory Quotient, RQ）定义为单位时间内机体产生的CO₂体积与消耗的O₂体积之比，是判断机体当前以何种底物为主要燃料的重要指标：

$$RQ = \frac{\dot{V}_{CO_2}}{\dot{V}_{O_2}}$$

纯葡萄糖氧化时：$C_6H_{12}O_6 + 6O_2 \rightarrow 6CO_2 + 6H_2O$，故 $RQ = 6/6 = 1.0$；纯脂肪酸（以软脂酸为例）氧化时：$C_{16}H_{32}O_2 + 23O_2 \rightarrow 16CO_2 + 16H_2O$，故 $RQ = 16/23 \approx 0.70$；纯蛋白质氧化的 $RQ \approx 0.82$。

例如，马拉松运动员在比赛初期（糖原充足阶段）测得 $RQ \approx 0.95$，而在比赛后半程（脂肪动员阶段）$RQ$ 可下降至约 $0.75$，直观反映了底物利用的动态转变。临床上，RQ < 0.70 提示可能存在酮体合成（脂肪酸不完全氧化），可作为糖尿病酮症早期监测的辅助指标。

> **思考问题**：若某人连续3天高脂低碳饮食（脂肪供能比＞70%），预期其静息状态下的RQ值会如何变化？这种变化对运动表现有何影响？研究表明，即使脂肪适应（Fat Adaptation）发生后，