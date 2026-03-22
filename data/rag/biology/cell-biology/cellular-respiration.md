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
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.91
last_scored: "2026-03-22"
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
---
# 细胞呼吸

## 概述

细胞呼吸是将有机分子（主要是葡萄糖）中储存的化学能转化为细胞通用能量货币 ATP 的过程。总反应方程式为：

$C_6H_{12}O_6 + 6O_2 \rightarrow 6CO_2 + 6H_2O + \text{~30-32 ATP}$

这个反应释放的自由能为 $\Delta G°' = -2870$ kJ/mol（Nelson & Cox, *Lehninger*, 8th ed.），但细胞并不是一步释放——而是通过三个精密耦合的阶段逐步提取能量，每一步都将电子传递给载体分子（NAD+ 和 FAD），最终在氧化磷酸化中一次性将电子能量转化为 ATP。这种分步策略使能量提取效率达到约 34%，远高于大多数人造发动机。

## 核心知识点

### 1. 糖酵解（Glycolysis）

糖酵解发生在**细胞质**中（不在线粒体内），是所有生物共有的最古老的代谢通路——从厌氧细菌到人类细胞都使用它。

**十步反应分两个阶段**：

**投资阶段**（步骤 1-5）：消耗 2 ATP，将葡萄糖（6C）裂解为 2 分子甘油醛-3-磷酸（G3P，3C）。关键步骤包括磷酸果糖激酶-1（PFK-1）催化的第3步——这是糖酵解的**主要调控点**。

**收获阶段**（步骤 6-10）：每分子 G3P 产生 2 ATP + 1 NADH，两分子 G3P 共产生 4 ATP + 2 NADH。

**净产量**（每分子葡萄糖）：
- **2 ATP**（产生4 - 消耗2 = 净2）
- **2 NADH**
- **2 丙酮酸**（3C）

**调控机制**：PFK-1 是变构酶，被 ATP 和柠檬酸抑制（能量充足时减速），被 AMP 和果糖-2,6-二磷酸激活（能量不足时加速）。这是一个经典的负反馈调控示例。

### 2. 丙酮酸氧化（过渡反应）

丙酮酸通过线粒体膜上的丙酮酸转运蛋白进入**线粒体基质**，被丙酮酸脱氢酶复合物（PDC）氧化脱羧：

**丙酮酸(3C) + CoA + NAD+ → 乙酰-CoA(2C) + CO2 + NADH**

每分子葡萄糖产生 2 乙酰-CoA + 2 CO2 + 2 NADH。

PDC 是一个由三种酶（E1, E2, E3）和五种辅酶（TPP, 硫辛酸, CoA, FAD, NAD+）组成的巨型复合物（分子量约 5×10⁶ Da），受到产物抑制和共价修饰的双重调控。

### 3. 柠檬酸循环（TCA/Krebs Cycle）

Hans Krebs 于1937年阐明了这个循环通路（获1953年诺贝尔奖）。在**线粒体基质**中进行：

**8步反应的关键节点**：

| 步骤 | 反应 | 产物 | 意义 |
|------|------|------|------|
| 1 | 乙酰-CoA + 草酰乙酸 → 柠檬酸 | 柠檬酸(6C) | 循环入口，柠檬酸合酶催化 |
| 3 | 异柠檬酸 → α-酮戊二酸 | NADH + CO2 | 第一次氧化脱羧 |
| 4 | α-酮戊二酸 → 琥珀酰-CoA | NADH + CO2 | 第二次氧化脱羧 |
| 5 | 琥珀酰-CoA → 琥珀酸 | GTP(≡ATP) | 底物水平磷酸化 |
| 6 | 琥珀酸 → 延胡索酸 | FADH2 | 复合物 II 也在此步 |
| 8 | 苹果酸 → 草酰乙酸 | NADH | 循环回到起点 |

**每轮循环净产量**：3 NADH + 1 FADH2 + 1 GTP + 2 CO2

**每分子葡萄糖**（2轮）：6 NADH + 2 FADH2 + 2 GTP + 4 CO2

> 思考题：为什么说 TCA 循环是"两用通路"？（提示：它不仅分解有机物产能，还为氨基酸、脂肪酸、核苷酸合成提供碳骨架中间产物。）

### 4. 氧化磷酸化（Oxidative Phosphorylation）

这是 ATP 产量最大的阶段，发生在**线粒体内膜**上。

**电子传递链（ETC）**将 NADH 和 FADH2 中的电子逐步传递给 $O_2$，释放的能量用于将 $H^+$ 泵出基质：

- 1 NADH → 复合物 I → 辅酶Q → 复合物 III → 细胞色素 c → 复合物 IV → $H_2O$（泵出 ~10 $H^+$）
- 1 FADH2 → 复合物 II → 辅酶Q → ... →（泵出 ~6 $H^+$）

**化学渗透学说**（Peter Mitchell, 1961, 获1978年诺贝尔奖）：$H^+$ 梯度驱动 ATP 合酶合成 ATP。约 3-4 个 $H^+$ 回流合成 1 个 ATP。

**ATP 产量计算**：

| 来源 | NADH | FADH2 | ATP(直接) | ATP(通过ETC) |
|------|------|-------|-----------|-------------|
| 糖酵解 | 2 | - | 2 | ~3-5* |
| 丙酮酸氧化 | 2 | - | - | ~5 |
| TCA循环 | 6 | 2 | 2 (GTP) | ~17 |
| **总计** | **10** | **2** | **4** | **~25-28** |

*注：细胞质 NADH 通过苹果酸-天冬氨酸穿梭产生 ~2.5 ATP/NADH，通过甘油磷酸穿梭仅产生 ~1.5 ATP/NADH。

**总 ATP 产量：约 30-32 ATP/葡萄糖**（旧教科书的 36-38 未考虑穿梭消耗和质子泄漏）。

### 5. 无氧呼吸与发酵

当 $O_2$ 缺乏时，电子传递链无法运行，NADH 无法被氧化回 NAD+。为维持糖酵解继续运转，细胞通过**发酵**再生 NAD+：

- **乳酸发酵**：丙酮酸 + NADH → 乳酸 + NAD+（人类肌肉剧烈运动时）
- **酒精发酵**：丙酮酸 → 乙醛 + CO2；乙醛 + NADH → 乙醇 + NAD+（酵母菌）

发酵效率极低：仅 2 ATP/葡萄糖（vs 有氧的 30-32），这就是为什么厌氧环境中的生物生长缓慢。

### 6. 代谢通路的整合调控

细胞呼吸不是孤立运行的，它与脂肪酸氧化、氨基酸代谢等通路深度整合：

- **脂肪酸 β-氧化**：在线粒体基质中将脂肪酸切割为乙酰-CoA，直接进入 TCA 循环。一分子棕榈酸（16C）可产生 ~106 ATP——这就是脂肪热量远高于糖类的原因（9 kcal/g vs 4 kcal/g）。
- **氨基酸**：脱氨后碳骨架可在多个节点进入 TCA 循环（例如谷氨酸 → α-酮戊二酸）。
- **AMP激酶（AMPK）**：细胞的"能量感受器"，当 AMP/ATP 比值上升时激活，促进分解代谢、抑制合成代谢。

## 关键要点

1. 细胞呼吸分三阶段：**糖酵解**（细胞质，2 ATP）→ **TCA循环**（基质，2 GTP + 电子载体）→ **氧化磷酸化**（内膜，~25-28 ATP）
2. 总 ATP 产量约 **30-32/葡萄糖**，能量转化效率约 34%
3. $O_2$ 是电子传递链的**最终电子受体**——没有它，整条链停转
4. 化学渗透学说（Mitchell, 1961）：$H^+$ 梯度驱动 ATP 合酶是核心产能机制
5. 糖酵解是最古老的代谢通路，发酵是无氧条件下维持 NAD+ 再生的应急方案

## 常见误区

1. **"细胞呼吸 = 呼吸（breathing）"**：呼吸是肺部的气体交换过程。细胞呼吸是发生在每个细胞内的生化反应。虽然 $O_2$ 的供给依赖呼吸系统，但两者是不同层次的概念。
2. **"ATP 全部在线粒体中产生"**：糖酵解在细胞质中产生 2 ATP，不需要线粒体。红细胞没有线粒体，完全依赖糖酵解供能。
3. **"每分子葡萄糖产生 36 或 38 ATP"**：这是过时的教科书数值。考虑穿梭消耗和质子泄漏后，现代计算为 **30-32 ATP**。
4. **"TCA 循环直接产生大量 ATP"**：TCA 循环每轮只直接产生 1 GTP。它的主要"产品"是 NADH 和 FADH2——这些电子载体才是氧化磷酸化中产生 ATP 的真正"燃料"。

## 知识衔接

### 先修知识
- **线粒体** — 细胞呼吸的主要场所（TCA循环和氧化磷酸化都在线粒体中进行）
- **酶** — 理解酶催化和变构调控是掌握代谢通路调控的基础

### 后续学习
- **代谢概览** — 将细胞呼吸置于全细胞代谢网络的背景中理解
- **光合作用** — 细胞呼吸的"逆过程"——利用光能将 CO2 和 H2O 合成葡萄糖

## 参考文献

1. Nelson, D.L. & Cox, M.M. (2021). *Lehninger Principles of Biochemistry* (8th ed.). W.H. Freeman. ISBN 978-1319228002. Ch.14-19.
2. Alberts, B. et al. (2022). *Molecular Biology of the Cell* (7th ed.). W.W. Norton. ISBN 978-0393884821. Ch.2, 14.
3. Krebs, H.A. & Johnson, W.A. (1937). The role of citric acid in intermediate metabolism. *Enzymologia*, 4, 148-156.
4. Mitchell, P. (1961). Coupling of phosphorylation to electron and hydrogen transfer by a chemi-osmotic mechanism. *Nature*, 191, 144-148.
