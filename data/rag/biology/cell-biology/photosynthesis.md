---
id: "photosynthesis"
concept: "光合作用"
domain: "biology"
subdomain: "cell-biology"
subdomain_name: "细胞生物学"
difficulty: 3
is_milestone: false
tags: ["代谢"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 95.9
generation_method: "research-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Photosynthesis"
    url: "https://en.wikipedia.org/wiki/Photosynthesis"
  - type: "encyclopedia"
    ref: "Wikipedia - Calvin cycle"
    url: "https://en.wikipedia.org/wiki/Calvin_cycle"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---




# 光合作用

## 概述

光合作用是植物、藻类和部分细菌利用光能将二氧化碳和水转化为葡萄糖和氧气的过程。其总反应方程式为：

$$6CO_2 + 6H_2O + 光能 \rightarrow C_6H_{12}O_6 + 6O_2 \quad \Delta G = +2870 \text{ kJ/mol}$$

这一过程发生在叶绿体中，分为依赖光的**光反应**阶段（定位于类囊体薄膜）和不直接依赖光的**暗反应（Calvin循环）**阶段（定位于叶绿体基质）。

光合作用的研究历史跨越三个世纪。1771年，英国化学家约瑟夫·普里斯特利（Joseph Priestley）发现植物能"净化"被蜡烛燃烧污染的空气，首次揭示植物释放氧气的现象。1845年，德国医生罗伯特·迈尔（Robert Mayer）提出植物将光能转化为化学能的假说。1862年，Julius von Sachs用碘液染色法证明淀粉是光合作用的直接产物，且只在受光照的叶片区域积累。20世纪40至50年代，梅尔文·卡尔文（Melvin Calvin）与安德鲁·本森（Andrew Benson）、詹姆斯·巴沙姆（James Bassham）利用放射性同位素¹⁴C示踪技术与纸层析法，历时约10年完整描绘了暗反应的碳固定路径，卡尔文于1961年独获诺贝尔化学奖。

全球绿色植物每年通过光合作用固定约$1.2 \times 10^{14}$千克碳，维持大气中氧气浓度约21%。若光合作用骤然停止，大气氧气约在200万年后降至无法支持大型动物生存的水平（参见《植物生理学》第6版，Taiz & Zeiger，2015，Sinauer Associates）。

---

## 核心原理

### 光反应：类囊体薄膜上的能量转换

光反应发生在叶绿体**类囊体（thylakoid）薄膜**上，核心结构是光系统II（PSII）和光系统I（PSI）两个超分子蛋白质复合体，二者通过电子传递链串联。

**第一步：水的光解（Water Splitting）**

PSII中的核心色素叶绿素P680（吸收峰680 nm）吸收光子后进入激发态，将电子传递给脱镁叶绿素（Pheophytin），自身成为强氧化剂。PSII通过其锰簇（Mn₄CaO₅催化中心）催化水的氧化：

$$2H_2O \rightarrow 4H^+ + 4e^- + O_2$$

释放的O₂全部逸散入大气，是地球大气氧的主要来源。4个H⁺留在类囊体腔内，参与质子梯度的建立。

**第二步：电子传递链与ATP合成**

高能电子从P680出发，依次经质体醌（PQ）、细胞色素b₆f复合体（Cytb₆f）、质体蓝素（PC）传递，每步均释放能量。Cytb₆f利用电子传递能量，将额外的H⁺从基质泵入类囊体腔（类比线粒体呼吸链），使类囊体腔H⁺浓度远高于基质，形成**质子动力势（pmf）**。ATP合酶（CF₀CF₁复合体）利用H⁺顺浓度梯度回流产生的驱动力合成ATP，此过程称为**光合磷酸化**（光驱化学渗透）。

**第三步：PSI与NADPH生成**

电子传递至PSI的核心色素P700（吸收峰700 nm），再次被光子激发后经铁氧还蛋白（Fd）最终将NADP⁺还原：

$$NADP^+ + 2e^- + H^+ \rightarrow NADPH$$

光反应的净产物为**ATP**、**NADPH**和**O₂**，前两者作为"同化力"直接驱动暗反应。

### 暗反应：Calvin循环的三个阶段

Calvin循环在叶绿体**基质（stroma）**中进行，每循环一次固定1个CO₂，需运行3次才能净产生1个三碳骨架（G3P）。

**阶段一：碳固定（Carbon Fixation）**

CO₂与五碳受体**1,5-二磷酸核酮糖（RuBP）**在关键酶**RuBisCO**（核酮糖-1,5-二磷酸羧化酶/加氧酶）催化下结合，生成2分子**3-磷酸甘油酸（3-PGA）**：

$$CO_2 + RuBP \xrightarrow{RuBisCO} 2 \times 3\text{-PGA}$$

RuBisCO是地球上含量最丰富的蛋白质，每片成熟叶片每平方厘米含有约4 μg RuBisCO，但其催化效率极低——每个活性位点每秒仅催化约3个CO₂分子（kcat ≈ 3 s⁻¹），且对O₂存在竞争性结合（导致光呼吸，详见误区部分）。

**阶段二：3-PGA的还原**

每分子3-PGA先消耗1个ATP磷酸化为1,3-二磷酸甘油酸（1,3-BPG），再消耗1个NADPH还原为**甘油醛-3-磷酸（G3P）**：

$$3\text{-PGA} \xrightarrow{ATP} 1,3\text{-BPG} \xrightarrow{NADPH} G3P$$

G3P是光合作用输出有机碳的核心形式，可用于合成葡萄糖、蔗糖、淀粉、脂肪酸及氨基酸前体。

**阶段三：RuBP的再生**

每固定3个CO₂，产生6个G3P分子；其中5个G3P经一系列消耗ATP的磷酸化和异构化反应（涉及磷酸戊糖通路中间体）重新合成3个RuBP，使循环得以持续。仅剩的**1个G3P为净产出**，输出到细胞质用于合成其他有机物。

**Calvin循环的化学计量**（固定3个CO₂，净产1个G3P）：

$$\text{消耗：} 9 \text{ ATP} + 6 \text{ NADPH} + 3 \text{ CO}_2 \rightarrow 1 \text{ G3P} + 9 \text{ ADP} + 8 \text{ Pi} + 6 \text{ NADP}^+$$

合成1分子葡萄糖（6碳）需运行6次碳固定（2个完整循环统计单元），共消耗**18个ATP**和**12个NADPH**。

### 光合色素的吸收光谱与能量传递

叶绿体中存在多种光合色素，分工明确：

| 色素 | 吸收峰（nm） | 功能 |
|------|-------------|------|
| 叶绿素a | 430、680 | 光系统反应中心，直接参与光化学反应 |
| 叶绿素b | 453、642 | 捕光天线色素，将能量传递给叶绿素a |
| β-胡萝卜素 | 451、480 | 捕光辅助，保护色素防止光氧化损伤 |
| 叶黄素 | 445、475 | 捕光辅助，参与非光化学猝灭（NPQ）保护 |

天线色素吸收光能后，通过**荧光共振能量转移（FRET）**以飞秒（$10^{-15}$ s）级速度将激发能传递至反应中心叶绿素，能量传递效率高达95%以上（Fleming et al., 2007, *Nature*）。

---

## 关键公式与能量效率计算

光合作用的**理论最大光能利用率**可通过以下方式估算：

合成1 mol葡萄糖需吸收最少**48个光子**（光反应每产生1个O₂需吸收8个光子，共产生6个O₂）。每个700 nm光子能量为：

$$E = \frac{hc}{\lambda} = \frac{6.626 \times 10^{-34} \times 3 \times 10^8}{700 \times 10^{-9}} \approx 2.84 \times 10^{-19} \text{ J}$$

48个光子总能量约为 $48 \times N_A \times 2.84 \times 10^{-19} \approx 8210 \text{ kJ/mol}$，而葡萄糖燃烧热为2870 kJ/mol，故理论最大效率约为 $2870/8210 \approx 35\%$。实际田间作物的年均光能利用率通常仅为**1%–3%**，主要损耗来自非光合有效辐射（约50%）、反射与透射（约10%）、热耗散及光呼吸等（Zhu et al., 2010, *Current Opinion in Biotechnology*）。

---

## 实际应用

### C₄植物与CAM植物对光合作用的改造

在高温、强光、干旱环境下，普通C₃植物（如水稻、小麦）因RuBisCO的加氧酶活性增强而产生大量**光呼吸**，浪费已固定的碳。C₄植物（如玉米、甘蔗）通过空间分离进化出"CO₂浓缩机制"：叶肉细胞用**PEP羧化酶**（对CO₂亲和力约为RuBisCO的60倍）将CO₂固定为四碳酸（草酰乙酸），再转运到维管束鞘细胞脱羧，将局部CO₂浓度提升至正常的3–6倍，使RuBisCO几乎不发生加氧反应。这使玉米的光合速率可达水稻的1.5倍以上，水分利用效率也显著更高。

景天酸代谢（CAM）植物（如仙人掌、菠萝）则通过**时间分离**：夜间气孔开放固定CO₂储存为苹果酸，白天气孔关闭将苹果酸脱羧后进入Calvin循环，极端减少水分散失，适应沙漠环境。

### 人工光合作用与碳捕获

例如，2022年中国科学院天津工业生物技术研究所团队在体外重建了由11种酶组成的**CETCH循环**（基于丙烯酰辅酶A）的仿生光合固碳路径，CO₂固定速率比天然Calvin循环高约3倍（Schwander et al., *Science*, 2016 首次报道CETCH循环原型；Wang et al., *Science*, 2021 报道人工合成淀粉）。这为利用太阳能直接合成燃料和食品提供了新思路。

---

## 常见误区

**误区1："暗反应不需要光"**——暗反应（Calvin循环）本身的酶促反应不直接需要光，但实际上**光照调控多种Calvin循环酶的活性**。例如，RuBisCO活化酶（RuBisCO activase）需要ATP（由光反应提供）来激活RuBisCO；磷酸甘油醛脱氢酶和FBPase通过**硫氧还蛋白（thioredoxin）**依赖光还原来激活。黑暗中Calvin循环很快停止，因此"暗反应可在黑暗中无限持续"的说法是错误的。

**误区2："光合作用释放的O₂来自CO₂"**——O₂全部来自**水的光解**，而非CO₂。1941年，鲁宾（Samuel Ruben）和卡门（Martin Kamen）用重氧同位素¹⁸O标记H₂¹⁸O和C¹⁸O₂，证明释放的¹⁸O₂仅在¹⁸O标记水时出现，彻底澄清了这一误解。

**误区3："RuBisCO只固定CO₂"**——RuBisCO存在竞争性**加氧酶活性**，在O₂浓度高或CO₂浓度低时（高温加剧）催化RuBP与O₂反应产生磷酸乙醇酸，触发**光呼吸**，消耗已固定碳的约25%–30%。这是限制C₃作物产量的重要因素，也是当前基因工程提升作物光合效率的核心靶标。

思考：**若将大气CO₂浓度从目前的约420 ppm提升