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
quality_tier: "pending-rescore"
quality_score: 13.8
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.182
last_scored: "2026-03-21"

sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Photosynthesis"
    url: "https://en.wikipedia.org/wiki/Photosynthesis"
  - type: "encyclopedia"
    ref: "Wikipedia - Calvin cycle"
    url: "https://en.wikipedia.org/wiki/Calvin_cycle"
---
# 光合作用

## 概述

光合作用（Photosynthesis）是植物、藻类和蓝细菌利用光能将二氧化碳和水转化为有机物（主要是葡萄糖）并释放氧气的生物化学过程。其总反应方程式为：

**6CO₂ + 6H₂O + 光能 → C₆H₁₂O₆ + 6O₂**

光合作用是地球上几乎所有生命的能量基础。全球光合作用捕获的平均能量约为 **130 太瓦（TW）**，大约是人类文明总能耗的 **8 倍**。光合生物每年将约 **1000-1150 亿吨**碳固定为生物量（Wikipedia: Photosynthesis）。

光合作用于 1779 年由 **Jan Ingenhousz** 发现——他证明植物需要光而不仅是土壤和水。

## 核心知识点

### 光反应（Light-Dependent Reactions）

发生在叶绿体的**类囊体膜**上：

1. **光系统II（PSII）**：吸收 680nm 光（P680），利用光能裂解水分子：2H₂O → O₂ + 4H⁺ + 4e⁻。这是地球大气中**氧气的来源**
2. **电子传递链**：电子经过质体醌（PQ）→ 细胞色素 b6f → 质体蓝素（PC），传递过程中将 H⁺ 泵入类囊体腔
3. **光系统I（PSI）**：吸收 700nm 光（P700），将电子传给铁氧还蛋白，最终由 **NADP⁺还原酶** 将 NADP⁺ 还原为 **NADPH**
4. **ATP合酶**：H⁺ 沿浓度梯度经 ATP 合酶回流，驱动 ADP + Pi → **ATP**（化学渗透假说，Mitchell 1961）

### Calvin 循环（暗反应/碳反应）

发生在叶绿体**基质**中，不直接需要光但需要光反应产物（ATP 和 NADPH）：

1. **碳固定**：RuBisCO 酶催化 CO₂ + RuBP（5C）→ 2 × 3-磷酸甘油酸（3C）。RuBisCO 是地球上**最丰富的蛋白质**
2. **还原**：3-磷酸甘油酸被 ATP 和 NADPH 还原为甘油醛-3-磷酸（G3P）
3. **再生**：每固定 3 个 CO₂，产出 6 个 G3P，其中 5 个用于再生 RuBP，1 个为净产出

**总结**：固定 1 个 CO₂ 需要 3 ATP + 2 NADPH；合成 1 分子葡萄糖需要 6 轮 Calvin 循环（Wikipedia: Calvin cycle）。

### C4 和 CAM 光合途径

**C4 途径**（如玉米、甘蔗）：先在叶肉细胞中由 PEP 羧化酶固定 CO₂ 为 4 碳化合物，再转运到维管束鞘细胞释放 CO₂ 给 Calvin 循环。避免了 RuBisCO 的**光呼吸**问题。

**CAM 途径**（如仙人掌、景天）：夜间开放气孔固定 CO₂，白天关闭气孔进行 Calvin 循环。适应干旱环境。

## 关键要点

1. 光反应在类囊体膜上产生 ATP 和 NADPH；Calvin 循环在基质中用它们固定 CO₂
2. 水的光解（PSII）是大气 O₂ 的来源
3. RuBisCO 是碳固定的关键酶也是地球上最丰富的蛋白质，但效率不高（也催化光呼吸）
4. 全球光合作用捕获约 130 TW 能量 ≈ 人类总能耗的 8 倍
5. C4 和 CAM 途径是对高温/干旱环境中 RuBisCO 光呼吸问题的进化解决方案

## 常见误区

1. **"暗反应在黑暗中进行"**——"暗反应"（Calvin循环）不直接使用光但需要光反应产物ATP和NADPH，因此实际在白天进行
2. **"光合作用只发生在叶子中"**——任何含叶绿体的绿色组织都能光合，包括茎和未成熟果实
3. **"植物白天光合晚上呼吸"**——植物 24 小时都在呼吸，白天光合速率通常大于呼吸速率所以净释放 O₂

## 知识衔接

- **先修**：细胞器结构（叶绿体）、ATP 与能量代谢
- **后续**：细胞呼吸（糖酵解+三羧酸循环）、碳循环生态学


### 实际案例

例如，C4植物（如玉米、甘蔗）进化出了特殊的碳浓缩机制来解决光呼吸问题。在C4植物中，CO2首先在叶肉细胞中被PEP羧化酶固定为四碳化合物（草酰乙酸），然后转运到维管束鞘细胞中释放CO2供Calvin循环使用。这种空间分离机制使C4植物在高温、高光照环境下的光合效率比C3植物高30-40%，这也解释了为什么热带地区的主要粮食作物多为C4植物。

## 思考题

1. 光合作用的光反应和暗反应（Calvin循环）之间如何相互依赖？如果其中一个被抑制会发生什么？
2. C3、C4和CAM三种光合途径分别适应什么环境？为什么进化产生了这些不同策略？
3. 全球变暖如何影响光合作用效率？CO₂浓度升高对不同类型植物的影响相同吗？


## 延伸阅读

- Wikipedia: [Photosynthesis](https://en.wikipedia.org/wiki/Photosynthesis)
