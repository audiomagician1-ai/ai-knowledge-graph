---
id: "protists"
concept: "原生生物"
domain: "biology"
subdomain: "microbiology"
subdomain_name: "微生物学"
difficulty: 2
is_milestone: false
tags: ["多样性"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 原生生物

## 概述

原生生物（Protista）是一个高度异质性的真核生物类群，涵盖所有不属于动物、植物或真菌的单细胞或简单多细胞真核生物。该名称由德国生物学家恩斯特·海克尔（Ernst Haeckel）于1866年在其著作《普通形态学》（*Generelle Morphologie der Organismen*）中正式提出，作为他三界系统（原生生物界、植物界、动物界）之一。原生生物的细胞具有完整的膜包被细胞核、线粒体（部分专性胞内寄生种类如微孢子虫已将线粒体退化为"氢化酶体"）以及内质网、高尔基体等细胞器，与原核生物有本质区别。

体型方面，原生生物跨越多个数量级：最小的皮科藻类（picoeukaryotes）直径仅1–2微米；草履虫（*Paramecium caudatum*）体长约150–300微米，肉眼勉强可见；而褐藻门的巨藻（*Macrocystis pyrifera*）最长可达60米，是地球上生长最快的生物之一，日生长量可达30厘米。

现代系统发育基因组学研究（如Adl等人2019年在《Journal of Eukaryotic Microbiology》发表的真核生物分类修订方案）已证明传统"原生生物界"并非单系群，而是至少8个独立超类群的集合，包括囊泡虫类（SAR超类群）、泛植物界（Archaeplastida）、变形虫界（Amoebozoa）等。因此，"原生生物"如今更多作为一个方便使用的非正式标签，而非严格的系统分类单元（Adl et al., 2019）。

## 核心原理

### 细胞运动结构与"9+2"轴丝模型

原生生物演化出了三类截然不同的细胞运动机制：

**伪足运动**：变形虫类（Amoebozoa）的伪足由细胞骨架中的G-肌动蛋白单体快速聚合为F-肌动蛋白丝（约每秒延伸0.1–1微米）驱动，细胞前缘"喷泉流"推进速度约为0.3–3微米/秒，视温度和底物黏附性而定。

**纤毛运动**：草履虫体表覆盖约14,000根纤毛，排列成斜行，相邻纤毛摆动存在约20°的相位差，形成"元波"（metachronal wave），使草履虫游速可达1000微米/秒（约自身体长的4倍/秒）。每根纤毛横切面均为经典的"9+2"轴丝结构：

$$
\text{轴丝} = 9 \times \text{周围二联微管} + 1 \times \text{中央二联微管}
$$

周围二联微管的A管上附着动力蛋白（dynein）臂，通过水解ATP驱动相邻微管间的滑动，摆动频率15–30次/秒，产生约1 pN量级的单根纤毛推力。

**鞭毛运动**：眼虫（*Euglena gracilis*）具1根长约50微米的主鞭毛和1根短鞭毛，轴丝结构与纤毛相同，但通过三维螺旋波动产生螺旋推进，游速约50–100微米/秒。

### 营养方式的全谱系分化

原生生物几乎展现了真核生物所有已知的营养策略：

**光合自养**：不同类群的色素系统反映了叶绿体的多次内共生起源。绿藻（Chlorophyta）叶绿体含叶绿素a和b，吸收峰分别在430 nm和662 nm，与陆地植物同源（初级内共生）；红藻（Rhodophyta）额外含藻红素（phycoerythrin），最大吸收峰约498–568 nm，使其能在水下60米的蓝绿光环境中有效光合；硅藻（Bacillariophyta）叶绿体含岩藻黄素（fucoxanthin），吸收峰约470–540 nm，对水体中占主导的蓝绿光利用效率极高，这是硅藻成为海洋初级生产力主力的光学原因（约贡献海洋初级生产力的40%）。

**吞噬异养**：草履虫通过口沟纤毛驱动水流，每小时摄食约5,000个细菌细胞，细菌被包裹进食物泡后，溶酶体与食物泡融合，pH从7降至约5，蛋白酶、脂肪酶、核酸酶协同消化，残渣由胞肛（cytoproct）排出。

**混合营养（Mixotrophy）**：眼虫在300 μmol photons·m⁻²·s⁻¹以上光强下完全依赖光合作用；低于约5 μmol photons·m⁻²·s⁻¹时转为腐生性吸收溶解有机物；完全遮光超过72小时后，叶绿体褪色并逐渐降解，转为专性异养——这一切换过程体现了原生生物营养方式的高度表型可塑性。

### 繁殖策略与生活史复杂性

**无性生殖**：草履虫在25°C、食物充足条件下，横二分裂周期约8小时，理论上每天可产生3代（2³ = 8倍增长），但实验室观察到种群密度超过约5,000个/mL时因废物积累生长速率显著下降。

**接合生殖（Conjugation）**：饥饿或种群密度过高时，草履虫发生接合生殖：两个亲和型个体以口沟区域相互贴合，各自小核（micronucleus）经减数分裂产生8个单倍体核，其中7个退化，1个再分裂为2个，互相交换后与对方融合，各自获得重组二倍体核，再分裂为数个新个体——全程约12小时，是基因重组但不增加个体数量的特殊有性生殖。

**顶复门的复杂生活史**：恶性疟原虫（*Plasmodium falciparum*）生活史涉及人类和按蚊两个宿主，在人体红细胞内完成48小时裂殖周期，裂殖体破裂时释放热原质（hemozoin）导致周期性高热（每48小时一次）；在按蚊中肠完成有性生殖（配子融合），形成卵囊后释放约1,000个子孢子迁移至唾液腺，平均每只感染按蚊一次叮咬可注入10–100个子孢子。

## 关键公式与定量模型

原生生物种群增长在资源充足的初期符合指数增长模型：

$$
N(t) = N_0 \cdot e^{rt}
$$

其中 $N_0$ 为初始种群密度，$r$ 为内禀增长率（intrinsic rate of increase），$t$ 为时间。草履虫在最适条件下 $r \approx 0.087\ \text{h}^{-1}$（即倍增时间 $t_{1/2} = \ln 2 / r \approx 8\ \text{h}$）。当种群密度接近环境容纳量 $K$ 时，增长转为逻辑斯谛模式：

$$
\frac{dN}{dt} = rN\left(1 - \frac{N}{K}\right)
$$

Gause（1934）在其经典实验中使用草履虫（*P. aurelia* 与 *P. caudatum*）验证了该模型，同时发现两种草履虫共培养时，*P. aurelia* 在约16天内将 *P. caudatum* 完全竞争排除，成为竞争排除原理（Gause's Law）的实验依据（Gause, G.F., *The Struggle for Existence*, 1934, Williams & Wilkins）。

硅藻的光合速率与光强的关系由光响应曲线描述：

$$
P = P_{\max} \cdot \frac{I}{I + K_s} - R_d
$$

其中 $P_{\max}$ 为最大净光合速率，$I$ 为光强（μmol photons·m⁻²·s⁻¹），$K_s$ 为半饱和常数（硅藻约50–150 μmol photons·m⁻²·s⁻¹），$R_d$ 为暗呼吸速率。

以下Python代码可用于模拟草履虫逻辑斯谛增长：

```python
import numpy as np
import matplotlib.pyplot as plt

# 草履虫 P. aurelia 参数 (Gause, 1934)
r = 0.087       # 内禀增长率 (h⁻¹)
K = 450         # 环境容纳量 (个/mL)
N0 = 2          # 初始密度 (个/mL)
t = np.linspace(0, 120, 1000)  # 模拟120小时

# 逻辑斯谛增长解析解
N = K / (1 + ((K - N0) / N0) * np.exp(-r * t))

plt.plot(t, N, 'b-', linewidth=2)
plt.xlabel('时间 (小时)')
plt.ylabel('种群密度 (个/mL)')
plt.title('草履虫 P. aurelia 逻辑斯谛增长 (K=450)')
plt.axhline(y=K, color='r', linestyle='--', label=f'K={K}')
plt.legend()
plt.show()
```

## 实际应用

### 生态系统中的关键作用

硅藻是地球氧气循环的重要参与者：全球约20%的光合固碳量（约每年6.7 Gt C）由海洋硅藻完成，硅藻死亡后细胞沉入海底形成"硅藻土"（diatomite），数百万年积累后形成厚达数百米的地层，如加利福尼亚州Lompoc地区的白垩纪硅藻土矿床，是重要的工业原料（过滤剂、隔热材料、炸药载体）。

甲藻（Dinoflagellata）中的沟腰鞭虫属（*Karenia*）及链状亚历山大藻（*Alexandrium catenella*）等种类能产生saxitoxin（石房蛤毒素），神经毒素半数致死量（LD₅₀）约为263 μg/kg（小鼠腹腔注射），一次赤潮事件中毒素浓度可超过0.8 mg/L，导致麻痹性贝类中毒（Paralytic Shellfish Poisoning, PSP）。2015年美国西海岸赤潮事件造成渔业损失超过1.48亿美元。

### 医学应用

疟原虫的叶绿体同源细胞器"顶质体"（apicoplast）是新型抗疟药物靶标——由于顶质体保留了原核型基因复制机制，四环素类抗生素（如强力霉素100 mg/天）可干扰其DNA复制，用于疟疾预防。弓形虫（*Toxoplasma gondii*）慢性感染据估计影响全球约33%人口，近年研究发现潜伏感染与精神分裂症风险（OR约1.7）及交通事故发生率升高存在统计关联（Flegr et al., 2012, *Schizophrenia Bulletin*）。

### 模式生物价值

盘基网柄菌（*Dictyostelium discoideum*）是研究细胞趋化性和多细胞分化的理想模型：单细胞变形体在饥饿时分泌cAMP（cAMP脉冲峰值约1 μM），通过cAMP梯度趋化聚集，最终约10万个细胞分化为2种细胞类型——约20%成为死亡的柄细胞（stalk cells），80%成为孢子细胞——这一"利他分化"是研究细胞演化的重要体系（Bonner, J.T., *The Social Amoebae*, Princeton University Press, 2009）。

## 常见误区

**误区1："原生生物都是单细胞的"**。实际上，褐藻（如海带*Saccharina japonica*）可长达数米，具有形态分化（叶状体、柄、固着器）和简单的细胞间通讯，但缺乏真正意义上的组织分化，属于简单多细胞原生生物。

**误区2："原生动物就是简单版的动物"**。草履虫、变形虫等"原生动物"与真正的后生动物（Metazoa）亲缘关系并不比与真菌、植物更近——事实上，领鞭毛虫（Choanoflagellatea）才被认为是动物界