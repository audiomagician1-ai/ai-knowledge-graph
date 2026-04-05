---
id: "membrane-transport"
concept: "膜转运"
domain: "biology"
subdomain: "cell-biology"
subdomain_name: "细胞生物学"
difficulty: 2
is_milestone: false
tags: ["功能"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 膜转运

## 概述

膜转运（Membrane Transport）是指物质穿越细胞膜进出细胞的过程，涵盖离子（Na⁺、K⁺、Ca²⁺、Cl⁻）、极性小分子（葡萄糖、氨基酸）、水分子，乃至分子量超过数万道尔顿的大分子蛋白质和多糖的跨膜移动。细胞膜由磷脂双分子层构成，厚度约为7–10 nm，其疏水内核对带电荷或强极性分子构成能垒（energy barrier），导致不同化学性质的分子必须借助截然不同的转运机制才能穿越。

膜转运研究的重大里程碑集中于20世纪中下叶。1952年，Alan Hodgkin 与 Bernard Katz 提出钠离子渗透性变化模型，首次从定量角度描述动作电位中离子流动规律；1957年，丹麦生化学家 Jens Christian Skou 发现 Na⁺/K⁺-ATPase，并于1997年凭此荣获诺贝尔化学奖；2003年，Peter Agre 因发现水通道蛋白（Aquaporin，AQP）获得诺贝尔化学奖，揭示红细胞和肾小管上皮细胞每秒可借助 AQP1 通道转运约 3×10⁹ 个水分子的惊人速率。根据物质大小、极性及细胞能量投入的差异，膜转运被划分为**被动运输**、**主动运输**和**囊泡转运**三大类别。

参考文献：《细胞生物学》（Alberts et al.，*Molecular Biology of the Cell*, 7th ed., W.W. Norton, 2022）对上述三类机制均有系统阐述。

---

## 核心原理

### 被动运输：顺浓度梯度的自发移动

被动运输（Passive Transport）不消耗ATP，物质沿浓度梯度（或电化学梯度）从高浓度侧自发向低浓度侧扩散，系统自由能变化 ΔG < 0，符合热力学自发过程的判据。被动运输进一步细分为两种机制：

**自由扩散（Simple Diffusion）**：非极性小分子（O₂、CO₂、N₂）和脂溶性分子（乙醇、类固醇激素）可直接溶入磷脂双分子层自由穿越。其扩散通量遵循菲克定律（Fick's First Law）：

$$J = -D \cdot A \cdot \frac{\Delta C}{\Delta x}$$

其中，$J$ 为单位时间通量（mol/s），$D$ 为扩散系数（m²/s），$A$ 为膜有效面积（m²），$\Delta C / \Delta x$ 为浓度梯度（mol/m⁴）。O₂ 在脂质双分子层中的扩散系数约为 $5 \times 10^{-10}\ \text{m}^2/\text{s}$，远高于水溶液中的 $2 \times 10^{-9}\ \text{m}^2/\text{s}$，说明气体分子"更偏爱"经脂质相扩散。

**协助扩散（Facilitated Diffusion）**：葡萄糖、氨基酸等极性分子及 Na⁺、K⁺、Cl⁻ 等离子虽同样顺梯度运动，却须借助两类膜蛋白完成转运：
- **载体蛋白（Carrier Protein）**：通过构象变化携带特定底物，具有饱和动力学（类似酶的 Michaelis-Menten 模型）。红细胞膜上的葡萄糖转运蛋白 GLUT1 是典型代表，其 $K_m$ 约为 1.5 mM，与血糖正常浓度（4–6 mM）相匹配，确保持续的葡萄糖摄取。
- **通道蛋白（Channel Protein）**：形成亲水孔道供离子单向或双向通过。电压门控钠通道（Nav）开放持续时间约 1 ms，单通道电导约 20 pS，每次开放可允许约 10⁷ 个 Na⁺/s 通过。

### 主动运输：逆浓度梯度的耗能泵送

主动运输（Active Transport）消耗代谢能（ATP 水解或离子梯度势能），将物质从低浓度侧逆电化学梯度泵送至高浓度侧，ΔG > 0，必须与放能反应（ATP 水解释放 −30.5 kJ/mol）偶联才能自发进行。

**原发性主动运输（Primary Active Transport）**：直接由 ATP 水解驱动。Na⁺/K⁺-ATPase 是教科书级经典：每水解 1 个 ATP 分子（消耗能量约 50 kJ/mol，在实际细胞条件下），将 **3 个 Na⁺ 泵出**细胞，同时将 **2 个 K⁺ 泵入**细胞，从而维持：
- 细胞内 K⁺ ≈ 140 mM，细胞外 K⁺ ≈ 5 mM（浓度比约 28:1）
- 细胞外 Na⁺ ≈ 145 mM，细胞内 Na⁺ ≈ 12 mM（浓度比约 12:1）

这一不对称离子分布产生约 −70 mV 的静息膜电位，是神经冲动、肌肉收缩和心脏节律的分子基础。估算表明，神经元在静息状态下约有 1/3 的 ATP 消耗用于维持 Na⁺/K⁺-ATPase 的运转。

**继发性主动运输（Secondary Active Transport）**：不直接使用 ATP，而是利用原发性主动运输建立的离子梯度作为驱动力。小肠上皮细胞刷状缘膜上的 **SGLT1**（钠-葡萄糖协同转运体 1）利用 Na⁺ 内流驱动葡萄糖逆浓度梯度进入细胞：每转运 1 个葡萄糖分子，同时转运 **2 个 Na⁺**。这属于**同向转运（Symport）**。与之相反，**逆向转运（Antiport）** 的典型案例是红细胞膜上的 AE1 阴离子交换蛋白，将 HCO₃⁻ 转出细胞的同时将 Cl⁻ 转入，实现 CO₂ 运输而不改变膜电位。

### 囊泡转运：大分子的膜包被运输

囊泡转运（Vesicular Transport）专门负责蛋白质、多糖、病毒颗粒等大分子物质的跨膜转运，通过质膜的出芽（budding）与融合（fusion）实现，消耗 ATP 和 GTP。

**内吞作用（Endocytosis）** 分为三类：
1. **受体介导内吞（Receptor-mediated Endocytosis）**：低密度脂蛋白（LDL）与 LDL 受体结合后，受体-配体复合物聚集于网格蛋白包被小窝（Clathrin-coated pit）；每个包被小窝直径约 150–200 nm，含约 150 个网格蛋白（Clathrin）三脚架分子，出芽形成内吞囊泡后网格蛋白脱落，囊泡与早期内体（early endosome）融合，pH 降至约 6.0 时 LDL 与受体解离。
2. **吞噬作用（Phagocytosis）**：巨噬细胞和中性粒细胞通过伪足包裹摄入直径超过 500 nm 的颗粒（细菌、凋亡细胞），形成吞噬体（phagosome），随后与溶酶体融合，溶酶体内 pH ≈ 4.5，含超过 50 种酸性水解酶。
3. **胞饮作用（Pinocytosis）**：非特异性摄入细胞外液及其中溶质，囊泡直径通常仅 60–120 nm。

**胞吐作用（Exocytosis）** 将胞内分泌囊泡与质膜融合，向胞外释放内容物。神经末梢突触小泡（直径约 40 nm）储存乙酰胆碱（每个小泡约含 5000–10000 个分子），动作电位触发 Ca²⁺ 内流后，SNARE 蛋白复合物驱动囊泡与突触前膜融合，全程仅需约 0.2 ms，体现了囊泡转运在神经信号传递中的极端精确性。

---

## 关键公式与定量参数

菲克定律描述被动扩散通量（见上文），而跨膜离子平衡电位可由 **Nernst 方程**计算：

$$E_{ion} = \frac{RT}{zF} \ln\frac{[Ion]_{out}}{[Ion]_{in}}$$

其中，$R = 8.314\ \text{J/(mol·K)}$，$T$ 为绝对温度（37°C 时 $T = 310\ \text{K}$），$z$ 为离子化合价，$F = 96485\ \text{C/mol}$（法拉第常数）。

例如，以 K⁺ 为例（$z = +1$，$[\text{K}^+]_{in} = 140\ \text{mM}$，$[\text{K}^+]_{out} = 5\ \text{mM}$）：

$$E_{K^+} = \frac{8.314 \times 310}{1 \times 96485} \ln\frac{5}{140} \approx 0.02676 \times (-3.332) \approx -89\ \text{mV}$$

该值与典型神经元静息膜电位（−70 mV）接近，说明 K⁺ 外流是建立静息膜电位的主要驱动力。

---

## 实际应用

**案例 1——肾脏水重吸收**：肾近端小管和集合管上皮细胞高度表达 AQP1 和 AQP2 水通道蛋白。AQP2 的膜定位受抗利尿激素（ADH/AVP）调控：ADH 与 V2 受体结合后，cAMP 升高驱动 AQP2 从胞质内体向顶膜转移，使集合管水渗透性提高约 10 倍，每天约 178 L 滤液中的 99% 以上水分得以重吸收回血液。AQP2 基因突变导致肾源性尿崩症，患者每日尿量可超过 10 L。

**案例 2——药物作用靶点**：洋地黄（Digoxin）是治疗心力衰竭的经典药物，其作用机制是特异性抑制心肌细胞膜上的 Na⁺/K⁺-ATPase，使细胞内 Na⁺ 升高，继而通过 Na⁺/Ca²⁺ 交换体（NCX，一种继发性主动运输的逆向转运体）减少 Ca²⁺ 外排，最终使心肌收缩力增强。治疗剂量仅需抑制约 20–30% 的 Na⁺/K⁺-ATPase 活性。

**案例 3——囊性纤维化（CF）**：CF 是由 CFTR 基因突变引起的遗传病，CFTR 蛋白本质上是一个 ATP 门控的 Cl⁻ 通道（属于协助扩散）。最常见的突变 ΔF508 导致 CFTR 蛋白在高尔基体中折叠错误，无法运输到细胞膜，致使气道黏液脱水变稠，影响约 1/3000 的欧洲裔新生儿。

---

## 常见误区

**误区 1：主动运输一定直接消耗 ATP。**
实际上，继发性主动运输（如 SGLT1 转运葡萄糖）不直接水解 ATP，而是"借用"Na⁺/K⁺-ATPase 事先建立的离子梯度中储存的势能。因此从整体看它仍是耗能的主动过程，但局部机制不涉及 ATP 水解。

**误区 2：协助扩散速率可以无限增大。**
载体蛋白介导的协助扩散具有饱和性：当膜上所有 GLUT1 分子均被葡萄糖占据时，增加胞外葡萄糖浓度不再提升转运速率，最大速率 $V_{max}$ 由膜上载体蛋白的密度决定。这与自由扩散的线性关系（无饱和点）有本质区别。