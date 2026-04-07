---
id: "optical-properties-solid"
concept: "固体光学性质"
domain: "physics"
subdomain: "solid-state-physics"
subdomain_name: "固态物理"
difficulty: 6
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 固体光学性质

## 概述

固体光学性质描述固态材料与电磁辐射相互作用时表现出的吸收、反射、透射和色散行为，其微观根源在于固体内部电子（和声子）对入射光子的响应。与孤立原子的光谱不同，固体中的能带结构使光学跃迁形成连续的吸收边（absorption edge），而非分立谱线，这一特征是固体光学区别于原子光学的本质。

历史上，Paul Drude 于 1900 年提出自由电子模型，首次给出金属介电函数的解析表达式，奠定了金属光学的理论基础。此后 Felix Bloch 的能带理论（1928年）将半导体和绝缘体的光学吸收边与禁带宽度 $E_g$ 直接联系起来，使固体光学从现象描述进入定量预测阶段。研究固体光学性质对半导体器件（光电探测器、LED、太阳能电池）、金属薄膜镀层及透明导电材料的设计具有直接工程意义。

## 核心原理

### 复介电函数与光学常数

固体对光的响应由复介电函数 $\tilde{\varepsilon}(\omega) = \varepsilon_1(\omega) + i\varepsilon_2(\omega)$ 完整描述，也可等价写成复折射率 $\tilde{n} = n + i\kappa$，其中 $\varepsilon_1 = n^2 - \kappa^2$，$\varepsilon_2 = 2n\kappa$。实部 $\varepsilon_1$ 决定相速度和色散，虚部 $\varepsilon_2$（或消光系数 $\kappa$）决定吸收。光强在介质中沿传播方向的衰减遵从 Beer-Lambert 定律：

$$I(x) = I_0 \, e^{-\alpha x}$$

吸收系数 $\alpha = 2\omega\kappa/c$，单位为 cm⁻¹。对典型半导体 GaAs，在其带隙能量（约 1.42 eV，对应波长 873 nm）之上，$\alpha$ 可迅速上升至 $10^4$–$10^5$ cm⁻¹ 量级。

### Drude 模型与等离子体频率

对于自由电子浓度为 $n$ 的金属或重掺杂半导体，Drude 模型给出介电函数：

$$\varepsilon_1(\omega) = 1 - \frac{\omega_p^2}{\omega^2 + \gamma^2}$$

其中等离子体频率（plasma frequency）定义为：

$$\omega_p = \sqrt{\frac{ne^2}{m^* \varepsilon_0}}$$

$m^*$ 为电子有效质量，$e$ 为元电荷，$\varepsilon_0$ 为真空介电常量，$\gamma$ 为阻尼系数（与电子散射率相关）。在 $\omega > \omega_p$ 时，$\varepsilon_1 > 0$，金属变为透明；在 $\omega < \omega_p$ 时，$\varepsilon_1 < 0$，入射光被强烈反射。铝的等离子体频率对应光子能量约为 15.8 eV（真空紫外区），因此铝对可见光呈高反射率，但在极紫外波段透明。重掺杂 n 型 InSb（载流子浓度 $\sim 10^{18}$ cm⁻³）的 $\omega_p$ 落在中红外区，是研究等离子体响应的经典体系。

### 带间跃迁与吸收边

半导体和绝缘体的光吸收主要来自带间跃迁（interband transition）。直接带隙半导体（如 GaAs）的吸收系数在带边附近满足：

$$\alpha(\hbar\omega) \propto (\hbar\omega - E_g)^{1/2}$$

间接带隙半导体（如 Si，$E_g \approx 1.12$ eV）的跃迁必须同时伴随声子的发射或吸收以满足动量守恒，吸收系数变为：

$$\alpha \propto (\hbar\omega - E_g \pm \hbar\Omega)^2$$

其中 $\hbar\Omega$ 是参与跃迁的声子能量（Si 的 TO 声子约为 56 meV）。这一区别导致 Si 的吸收边比 GaAs 更加平缓，这是 Si 作为太阳能材料效率受限的物理根源之一。

### 反射率与 Kramers-Kronig 关系

垂直入射时固体表面的反射率为：

$$R = \left|\frac{\tilde{n}-1}{\tilde{n}+1}\right|^2 = \frac{(n-1)^2 + \kappa^2}{(n+1)^2 + \kappa^2}$$

实验上常通过测量宽频反射谱，再利用 Kramers-Kronig 关系（一对积分变换）从 $R(\omega)$ 同时提取 $n(\omega)$ 和 $\kappa(\omega)$，从而无需透射测量即可获得完整光学常数。这一方法是固体光学实验分析的标准手段，广泛用于测量强吸收材料（如过渡金属氧化物）的光学性质。

## 实际应用

**太阳能电池材料选择**：直接带隙的 GaAs（$E_g = 1.42$ eV）和 CdTe（$E_g = 1.45$ eV）的吸收系数比 Si 高 1–2 个数量级，因此只需约 1 μm 厚度即可吸收绝大部分太阳光，而 Si 太阳能电池需要约 100–200 μm 的吸收层。

**低辐射（Low-E）玻璃**：在玻璃上镀厚度约 10–20 nm 的 Ag 薄膜，利用银的等离子体频率（$\omega_p$ 对应约 3.8 eV）使其对可见光透明而对近红外热辐射高度反射，实现建筑节能。

**椭偏测量（Ellipsometry）**：通过测量斜入射后反射光的偏振态变化角 $\Psi$ 和 $\Delta$，结合上述光学模型，可非破坏性地同时确定薄膜厚度（精度达 0.1 nm）和复折射率，是半导体工艺中不可或缺的表征手段。

## 常见误区

**误区一：金属在所有频率下都不透明。** 实际上，当入射光频率超过等离子体频率 $\omega_p$ 时，金属的 $\varepsilon_1 > 0$，将变为透明。碱金属（如钠，$\omega_p$ 对应约 5.9 eV）在紫外区即出现透明窗口，这一现象已被实验直接证实。混淆这一点往往源于将 Drude 模型结论的适用频率范围忽略。

**误区二：带隙越大，材料越透明。** 这一说法仅对直接带隙材料在带隙以下频率成立。对于间接带隙材料，即使光子能量低于直接带隙，声子辅助的间接跃迁仍会产生可观的带尾吸收（Urbach tail），使透射窗口并非严格的阶跃函数。此外，自由载流子的 Drude 吸收在红外区会独立存在，与带隙大小无关。

**误区三：反射率高等价于吸收弱。** 由菲涅耳公式可知，高反射率意味着大的消光系数 $\kappa$，而 $\kappa$ 大正对应强吸收。金属在可见光区高反射的原因恰恰是其 $\kappa \gg 1$，光虽进不去，但并不意味着材料对光"不敏感"——金属的强吸收只是发生在极短的趋肤深度（$\delta = c/(\omega\kappa)$，对铜在 600 nm 处约为 25 nm）之内。

## 知识关联

固体光学性质直接建立在**能带理论**之上：带间跃迁的选择定则（跃迁矩阵元）和吸收边形状均由导带与价带的色散关系及对称性决定；等离子体频率中的有效质量 $m^*$ 同样来自能带曲率 $m^* = \hbar^2(\partial^2 E/\partial k^2)^{-1}$。掌握自由电子 Drude 模型、Bloch 定理和直接/间接带隙的概念是理解本节所有公式的必要前提。在实验技术层面，固体光学性质的测量（反射谱、透射谱、椭偏仪）是表征未知材料能带结构和载流子浓度的重要手段，与输运测量（霍尔效应）互为补充，共同构成固态物理实验表征的核心工具集。