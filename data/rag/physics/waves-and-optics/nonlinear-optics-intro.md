---
id: "nonlinear-optics-intro"
concept: "非线性光学简介"
domain: "physics"
subdomain: "waves-and-optics"
subdomain_name: "波动与光学"
difficulty: 6
is_milestone: false
tags: ["拓展"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 92.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 非线性光学简介

## 概述

非线性光学是研究强光场与介质相互作用时，介质极化强度对光场呈非线性响应的物理分支。在普通光强条件下，介质极化强度 **P** 与电场强度 **E** 成正比：$P = \varepsilon_0 \chi^{(1)} E$，其中 $\chi^{(1)}$ 为线性电极化率，典型值约为 $10^{-1}$ 量级（无量纲SI制）。而当光场强度接近或超过原子内部电场（约 $10^{8}$ V/m 量级，对应激光峰值功率密度约 $10^{13}$ W/cm²）时，必须引入高阶极化项：

$$P = \varepsilon_0\bigl(\chi^{(1)}E + \chi^{(2)}E^2 + \chi^{(3)}E^3 + \cdots\bigr)$$

其中 $\chi^{(2)}$ 的典型值约为 $10^{-12}$ m/V（如 LiNbO₃ 的 $d_{33} \approx 27$ pm/V），$\chi^{(3)}$ 约为 $10^{-22}$ m²/V²，正是这些高阶项催生了倍频、自聚焦、光学参量振荡等独特现象。

非线性光学的实验基础建立于1961年——激光器诞生仅一年后。Peter Franken 及其同事将红宝石激光（波长 694.3 nm，脉冲能量约 3 mJ）聚焦到石英晶体，首次观测到二次谐波输出（347.15 nm）。该论文发表于 *Physical Review Letters* 第7卷，但最初投稿时编辑误将倍频光点当作底片污点而删除，成为学术史上著名的乌龙事件（Franken et al., 1961）。此后，Nicolaas Bloembergen 与 P. S. Pershan 于1962年在 *Physical Review* 第128卷建立了系统的非线性光学边界条件理论，Bloembergen 因在非线性光学领域的奠基性贡献于1981年与 Arthur Schawlow 共同获得诺贝尔物理学奖。

非线性光学的工业意义极为具体：现代绿色激光笔（532 nm）全部依赖1064 nm Nd:YAG 激光在 KTP 晶体中倍频实现；深紫外光源（266 nm、213 nm）由此延伸的四倍频、五倍频方案支撑了半导体光刻与材料表征；光学参量振荡器（OPO）则提供了从 350 nm 至 5000 nm 的连续可调谐波长，是光谱学不可或缺的光源。

---

## 核心原理

### 二次谐波产生（倍频，SHG）

二次谐波产生（Second Harmonic Generation，SHG）源于二阶非线性极化率 $\chi^{(2)}$。设基频光电场为 $E = E_0 \cos(\omega t - kz)$，则二阶极化项为：

$$P^{(2)} = \varepsilon_0 \chi^{(2)} E_0^2 \cos^2(\omega t - kz) = \frac{\varepsilon_0 \chi^{(2)} E_0^2}{2}\bigl[1 + \cos(2\omega t - 2kz)\bigr]$$

其中直流项（光整流效应）产生静电场，振荡项 $\cos(2\omega t)$ 辐射频率为 $2\omega$（波长减半）的倍频光。注意，$\chi^{(2)}$ 在具有中心对称性的介质（液体、非晶玻璃、中心对称晶体）中因对称性要求**严格为零**，因此 SHG 仅发生于非中心对称材料，常见的有：磷酸二氢钾（KDP，$d_{36} = 0.39$ pm/V）、铌酸锂（LiNbO₃，$d_{33} = 27$ pm/V）、β-偏硼酸钡（BBO，$d_{22} = 2.2$ pm/V，透射窗口延伸至 189 nm）和磷酸氧钛钾（KTP，$d_{33} = 13.7$ pm/V）。

高效 SHG 的决定因素是**相位匹配条件**：

$$\Delta k = k(2\omega) - 2k(\omega) = \frac{2\omega}{c}\bigl[n(2\omega) - n(\omega)\bigr] = 0$$

由于正常色散导致 $n(2\omega) > n(\omega)$，$\Delta k \neq 0$ 时转换效率随相互作用长度 $L$ 呈 $\text{sinc}^2(\Delta k \cdot L/2)$ 振荡，相干长度 $L_c = \pi/\Delta k$ 仅约数微米至数十微米，转换效率极低（$<0.01\%$）。实验上最常用**Ⅰ类双折射相位匹配**：选取特定切割角 $\theta_m$ 使寻常光 $n_o(\omega)$ 等于非寻常光 $n_e(2\omega, \theta_m)$，从而 $\Delta k = 0$，转换效率可从接近 0 提升至 80% 以上。对于 BBO 晶体，实现 1064 nm → 532 nm 倍频的相位匹配角为 $\theta_m \approx 22.8°$。

另一种重要技术是**准相位匹配（QPM）**，由 Armstrong 等人于1962年提出，通过周期性极化（如周期极化铌酸锂，PPLN，周期约 $6\text{–}30\,\mu\text{m}$）补偿相位失配，可利用最大非线性系数分量（$d_{33}$），转换效率比传统双折射相位匹配提高约一个数量级。

### 自聚焦与光克尔效应

自聚焦源于三阶非线性极化率 $\chi^{(3)}$ 产生的**光克尔效应**：介质折射率随局部光强线性变化：

$$n = n_0 + n_2 I, \quad n_2 = \frac{3\chi^{(3)}}{4\varepsilon_0 c n_0^2}$$

其中 $n_0$ 为线性折射率，$n_2$ 为非线性折射率系数（石英光纤中 $n_2 \approx 2.6 \times 10^{-20}$ m²/W，CS₂ 液体中 $n_2 \approx 3 \times 10^{-18}$ m²/W），$I$ 为光强。由于高斯光束横截面中心光强（$I_0$）远大于边缘光强，中心区折射率更高，等效形成一个正透镜，光束向轴线汇聚——即自聚焦。

当光功率超过**临界自聚焦功率**时，自聚焦效应将战胜衍射扩散：

$$P_{cr} = \frac{3.77\lambda^2}{8\pi n_0 n_2}$$

对于波长 800 nm 的飞秒激光在空气中，$P_{cr} \approx 3\text{–}5$ GW。超过此功率后，光束发生灾难性坍缩，导致介质损伤或激发产生从紫外到近红外覆盖的**超连续谱**（白光激光）。飞秒激光在大气中传输时，自聚焦与由此产生的等离子体散焦形成动态平衡，可维持跨越数百米甚至数公里的"光丝"，已被用于大气遥感（探测 CO₂、O₃ 浓度）和远程激光雷达。

### 光学参量效应（OPA/OPO）

光学参量效应同样基于 $\chi^{(2)}$，但能量流向与 SHG 相反：一个泵浦光子（频率 $\omega_p$）在晶体中分裂为两个低频光子，同时满足：

$$\omega_p = \omega_s + \omega_i \quad \text{（能量守恒）}$$
$$\vec{k}_p = \vec{k}_s + \vec{k}_i \quad \text{（动量守恒，相位匹配）}$$

其中 $\omega_s$（信号光）和 $\omega_i$（闲频光）的频率由相位匹配条件决定，可通过旋转晶体角度或改变温度连续调节。以 BBO 晶体为例，用 355 nm 泵浦的光学参量振荡器（OPO）可在 410–700 nm（信号光）和 710–2500 nm（闲频光）范围内连续调谐，覆盖跨度超过 2 微米。

将参量放大腔搭配谐振腔构成**光学参量振荡器（OPO）**，其阈值泵浦强度约为数 MW/cm²，商业化产品的波长调谐精度可达 0.1 cm⁻¹，是中红外（3–5 μm）化学分子指纹区光谱分析的标准光源。

---

## 关键公式汇总

| 效应 | 核心公式 | 关键参数 |
|------|----------|----------|
| 二阶极化 | $P^{(2)} = \varepsilon_0 \chi^{(2)} E^2$ | $\chi^{(2)} \sim 10^{-12}$ m/V |
| SHG转换效率 | $\eta \propto \text{sinc}^2(\Delta k \cdot L/2)$ | 相干长度 $L_c = \pi/\Delta k$ |
| 光克尔折射率 | $n = n_0 + n_2 I$ | 石英：$n_2 = 2.6\times10^{-20}$ m²/W |
| 自聚焦临界功率 | $P_{cr} = 3.77\lambda^2/(8\pi n_0 n_2)$ | 空气800 nm：$P_{cr}\approx 3$ GW |
| OPO能量守恒 | $\omega_p = \omega_s + \omega_i$ | 可调谐范围 410–2500 nm |

以下 Python 代码演示 SHG 转换效率随相位失配量 $\Delta k$ 的变化关系：

```python
import numpy as np
import matplotlib.pyplot as plt

L = 1e-2          # 晶体长度 1 cm
delta_k = np.linspace(-3e4, 3e4, 1000)  # 相位失配量 (m⁻¹)

# SHG强度正比于 sinc²(ΔkL/2)
efficiency = (np.sinc(delta_k * L / (2 * np.pi)))**2

plt.plot(delta_k * 1e-3, efficiency)
plt.xlabel('Δk (mm⁻¹)')
plt.ylabel('相对转换效率')
plt.title('SHG效率 vs 相位失配量（L = 1 cm）')
plt.axvline(x=0, color='r', linestyle='--', label='完美相位匹配 Δk=0')
plt.legend()
plt.show()
# Δk=0 时效率最大，相干长度 Lc = π/Δk 决定有效作用区间
```

---

## 实际应用

**工业激光倍频**：全球每年出货量超过千万支的绿色激光笔（532 nm）均采用 Nd:YAG（或 Nd:YVO₄）1064 nm 激光在 KTP 晶体（尺寸约 1 mm × 1 mm × 3 mm）中进行 Ⅱ 类相位匹配倍频，KTP 的损伤阈值约为 500 MW/cm²，适合纳秒脉冲操作。

**超快激光与超连续谱**：将800 nm、100 fs 的钛宝石激光（能量约 1 nJ）耦合入直径 2 μm 的光子晶体光纤，自相位调制（基于 $\chi^{(3)}$）产生覆盖 400–1400 nm 的超连续谱，频率梳技术由此发展，Hänsch 与 Hall 因此获得2005年诺贝尔物理学奖。

**量子纠缠光子对产生**：利用 BBO 晶体中的**自发参量下转换（SPDC）**，可产生纠缠光子对，是量子密钥分发（QKD）和量子计算实验的基础光源。典型实验中，405 nm 泵浦 BBO 产生810 nm 的纠缠光子对，符合计数率约 $10^4$–$10^6$ 对/秒。

**医疗与材料加工**：266 nm 四倍频 Nd:YAG 激光（1064 nm → 532 nm → 266 nm，两次倍频）用于视网膜光凝和 DNA 损伤研究；213 nm 五倍频激光用于熔融石英和蓝宝石的精密刻蚀，因光子能量（5.8 eV）超过许多聚合物的化