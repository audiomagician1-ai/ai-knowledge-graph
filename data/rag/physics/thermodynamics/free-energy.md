---
id: "free-energy"
concept: "自由能"
domain: "physics"
subdomain: "thermodynamics"
subdomain_name: "热力学"
difficulty: 6
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 43.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 自由能

## 概述

自由能是热力学中描述系统在特定约束条件下能够对外做功的最大能量的状态函数。与内能或焓不同，自由能将熵的贡献纳入考量，因此可以直接判断过程的自发性。历史上，亥姆霍兹（Hermann von Helmholtz）于1882年正式引入了以其名字命名的亥姆霍兹自由能 $A$（也写作 $F$），而吉布斯（Josiah Willard Gibbs）则在19世纪70年代的奠基性论文《论非均相物质的平衡》中系统阐述了吉布斯自由能 $G$，这两种函数各自适用于不同的实验约束条件。

自由能之所以在热力学中具有核心地位，是因为它将第一定律（能量守恒）与第二定律（熵增原理）整合为单一的判据。在等温等容条件下，系统自发过程必须满足 $\Delta A \leq 0$；在等温等压条件下，必须满足 $\Delta G \leq 0$。这一判据在化学反应、相变分析和生物化学过程中被广泛应用。

## 核心原理

### 亥姆霍兹自由能

亥姆霍兹自由能定义为：

$$A = U - TS$$

其中 $U$ 是系统内能，$T$ 是绝对温度（单位开尔文），$S$ 是熵。对该定义式取全微分，结合热力学第一定律 $\mathrm{d}U = T\mathrm{d}S - p\mathrm{d}V$，得到：

$$\mathrm{d}A = -S\mathrm{d}T - p\mathrm{d}V$$

这意味着 $A$ 的自然变量是 $(T, V)$，即亥姆霍兹自由能在等温等容过程中是最合适的热力学势。在等温条件下，系统对外做的最大功等于 $-\Delta A$，"自由能"名称正源于此——$A$ 中扣除了"束缚"于熵的部分 $TS$，剩余的才是可自由转化为功的能量。

### 吉布斯自由能

吉布斯自由能定义为：

$$G = H - TS = U + pV - TS$$

其中 $H = U + pV$ 是焓。对 $G$ 取全微分得：

$$\mathrm{d}G = -S\mathrm{d}T + V\mathrm{d}p$$

因此 $G$ 的自然变量是 $(T, p)$，适用于等温等压过程。实验室中大多数化学反应在大气压下进行，使得 $G$ 比 $A$ 更为常用。等温等压条件下系统可对外做的最大非体积功（如电功）等于 $-\Delta G$，这是燃料电池和电化学电池理论分析的基础。

吉布斯自由能与化学反应平衡直接挂钩：标准摩尔吉布斯自由能变 $\Delta_r G^\circ$ 与平衡常数 $K$ 的关系为：

$$\Delta_r G^\circ = -RT \ln K$$

其中 $R = 8.314\ \mathrm{J\ mol^{-1}\ K^{-1}}$。当 $\Delta_r G^\circ < 0$ 时，平衡常数 $K > 1$，反应正向自发进行。

### 亥姆霍兹自由能与吉布斯自由能的关系

两者通过勒让德变换相互联系。从 $A(T,V)$ 出发，引入压强 $p = -(\partial A/\partial V)_T$，对变量 $V$ 做勒让德变换即得 $G = A + pV$。这种变换在形式上将自然变量从 $(T,V)$ 切换到 $(T,p)$，反映的是从固定体积约束转变为固定压力约束的物理情景。事实上，内能 $U$、焓 $H$、亥姆霍兹自由能 $A$ 和吉布斯自由能 $G$ 构成四种经典热力学势，彼此通过对 $S$、$V$ 两个广延量做勒让德变换互相转化。

## 实际应用

**化学反应自发性判断**：在298 K、标准大气压下，葡萄糖完全氧化反应的 $\Delta_r G^\circ \approx -2870\ \mathrm{kJ\ mol^{-1}}$，负值表明该反应强烈自发，生物体通过ATP合成将部分吉布斯自由能转化为化学能储存起来。

**相变临界点**：在液-气相变的临界点（例如水的临界点为 $T_c = 647.1\ \mathrm{K}$，$p_c = 22.06\ \mathrm{MPa}$），两相的摩尔吉布斯自由能相等，$G_{\text{液}} = G_{\text{气}}$。这一等式是确定相图上相边界的核心条件，也是克劳修斯-克拉珀龙方程的出发点。

**蛋白质折叠**：蛋白质从伸展态到折叠态时，$\Delta G$ 通常仅为 $-20\ \text{至}\ -60\ \mathrm{kJ\ mol^{-1}}$，远小于葡萄糖氧化，这说明蛋白质折叠状态的稳定性相当脆弱，轻微的温度升高即可通过 $-T\Delta S$ 项的增大而使 $\Delta G$ 变正，导致蛋白质变性。

## 常见误区

**误区一：自由能等同于"可用能"，损失的部分就是热量**。实际上，$A$ 与最大功之间的差额来自不可逆过程中的熵产生，而非直接等于耗散热。对可逆等温过程，系统从环境吸收的热量恰好等于 $T\Delta S$；对不可逆过程，实际做功 $|W_{\text{实际}}| < |\Delta A|$，差值 $|\Delta A| - |W_{\text{实际}}|$ 才与熵产生对应。混淆"最大功"与"实际功"会导致对效率的错误估计。

**误区二：$\Delta G < 0$ 意味着反应一定快速发生**。吉布斯自由能变只判断热力学自发性，完全不涉及反应速率。氢气在常温空气中 $\Delta_r G^\circ \ll 0$，但若无催化剂或点火，反应速率极低。动力学（活化能）与热力学（自由能）是两套独立的分析框架，不可混用。

**误区三：亥姆霍兹自由能 $A$ 与吉布斯自由能 $G$ 数值差异微小，可以互换**。对凝聚态（固体、液体）在常压下，$pV$ 项确实很小，两者数值接近；但对气相系统，$pV = nRT$ 可达数千焦每摩尔量级，两者差异显著。在处理高压气体或气相化学平衡时，必须明确区分等容与等压条件，选用对应的自由能函数。

## 知识关联

自由能是在熵的基础上建立的。若未掌握熵的统计诠释（$S = k_B \ln \Omega$）和克劳修斯不等式（$\mathrm{d}S \geq \delta Q/T$），就无法理解为何 $\Delta A \leq 0$ 或 $\Delta G \leq 0$ 能作为自发性判据——这些不等式本质上是第二定律对等温等容或等温等压过程的特殊表述。

掌握自由能的全微分表达式（$\mathrm{d}A = -S\mathrm{d}T - p\mathrm{d}V$ 与 $\mathrm{d}G = -S\mathrm{d}T + V\mathrm{d}p$）后，可以直接推导麦克斯韦关系。以 $A$ 为例，由混合偏导数相等 $\partial^2 A / \partial T \partial V = \partial^2 A / \partial V \partial T$，立即得到：

$$\left(\frac{\partial S}{\partial V}\right)_T = \left(\frac{\partial p}{\partial T}\right)_V$$

类似地，从 $G$ 出发可得 $(\partial S/\partial p)_T = -(\partial V/\partial T)_p$。这四个麦克斯韦关系是将难以直接测量的量（如 $(\partial S/\partial V)_T$）转化为可测量量（如热膨胀系数）的桥梁，而这一推导完全依赖于自由能作为热力学势的精确数学结构。