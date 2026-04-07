---
id: "free-electron-model"
concept: "自由电子模型"
domain: "physics"
subdomain: "solid-state-physics"
subdomain_name: "固态物理"
difficulty: 6
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 自由电子模型

## 概述

自由电子模型（Free Electron Model）是固态物理中描述金属导电性质的基础理论，其核心假设是将金属中价电子视为在均匀正电荷背景中自由运动的粒子群，完全忽略电子与离子实之间的周期性势场（即"凝胶近似"，jellium approximation）以及电子间的库仑排斥。这一简化虽然粗糙，却以惊人的精度解释了金属的诸多宏观性质。

该模型经历了两个关键历史阶段：1900年Paul Drude基于经典统计力学建立了经典自由电子模型，将导电电子视为满足麦克斯韦-玻尔兹曼分布的理想气体；1928年Arnold Sommerfeld在Drude框架中引入费米-狄拉克量子统计和泡利不相容原理，建立了量子自由电子模型（Sommerfeld模型），彻底解决了经典模型在电子热容预测上的百倍偏差问题。两个模型的对比与融合，构成了从经典物理向量子固体物理过渡的重要里程碑。参考文献：《固体物理学》（黄昆、韩汝琦，1988，高等教育出版社）与 *Solid State Physics*（Ashcroft & Mermin, 1976）对本节内容均有详尽推导。

---

## 核心原理

### Drude经典模型：弛豫时间与碰撞图像

1900年，Paul Drude将气体动理论的碰撞思想移植到金属中，假设电子以平均弛豫时间 $\tau$（典型值约 $10^{-14}$ 秒）与离子实发生随机碰撞，每次碰撞后电子速度完全随机化。在外加电场 $\mathbf{E}$ 下，电子在两次碰撞间受到加速，平均漂移速度为 $v_d = eE\tau/m$，由此推导出直流电导率：

$$\sigma = \frac{ne^2\tau}{m}$$

其中 $n$ 为自由电子数密度，$e$ 为电子基本电荷量 $1.602\times10^{-19}$ C，$m$ 为电子静止质量 $9.109\times10^{-31}$ kg。此式成功给出欧姆定律 $\mathbf{J} = \sigma\mathbf{E}$ 的微观解释。

Drude模型的另一重要成就是推导**维德曼-弗朗兹定律**（Wiedemann-Franz Law）：金属热导率 $\kappa$ 与电导率 $\sigma$ 之比满足：

$$\frac{\kappa}{\sigma} = LT, \quad L = \frac{\pi^2}{3}\left(\frac{k_B}{e}\right)^2 = 2.44\times10^{-8}\ \text{W·Ω·K}^{-2}$$

其中 $L$ 称为**洛伦兹数**（Lorenz number）。室温下铜的实验值 $L_{exp} = 2.23\times10^{-8}\ \text{W·Ω·K}^{-2}$，与理论值吻合在10%以内。然而，Drude模型将电子热容预测为 $C_{el} = \frac{3}{2}Nk_B$（每个电子贡献 $\frac{3}{2}k_B$），比实验值高出约100倍，这一致命缺陷直到Sommerfeld引入量子统计后才得到修正。

### Sommerfeld量子模型：费米能与费米球

Sommerfeld模型将金属中 $N$ 个自由电子置于体积为 $V$ 的三维无限深势阱（势箱）中，用量子力学求解薛定谔方程，得到允许的单粒子能级。对周期性边界条件，允许的波矢 $\mathbf{k}$ 满足 $k_i = 2\pi n_i / L$（$n_i$ 为整数，$L = V^{1/3}$），每个 $\mathbf{k}$ 态可容纳自旋向上和向下各一个电子（泡利不相容原理）。

在绝对零度 $T = 0$ 时，电子按能量从低到高逐一填充，所有被占据态在动量空间中构成半径为 $k_F$ 的球体——**费米球**（Fermi sphere），其表面即**费米面**（Fermi surface）。费米波矢由电子数密度 $n = N/V$ 唯一确定：

$$k_F = (3\pi^2 n)^{1/3}$$

对应的**费米能**（Fermi energy）为：

$$E_F = \frac{\hbar^2 k_F^2}{2m} = \frac{\hbar^2}{2m}(3\pi^2 n)^{2/3}$$

以铜（Cu）为例：$n_{Cu} = 8.49\times10^{28}\ \text{m}^{-3}$，代入计算得：
- $k_F = 1.36\times10^{10}\ \text{m}^{-1}$
- $E_F = 7.04\ \text{eV}$
- 费米温度 $T_F = E_F / k_B = 81{,}600\ \text{K}$
- 费米速度 $v_F = \hbar k_F / m = 1.57\times10^6\ \text{m/s}$（约为光速的0.52%）

$T_F \gg T_{room} = 300\ \text{K}$ 这一事实表明，室温对费米海的扰动极为微弱，经典麦克斯韦-玻尔兹曼统计在此完全失效，必须使用费米-狄拉克统计。

### 态密度与费米-狄拉克分布

单位体积、单位能量间隔内的量子态数称为**态密度**（Density of States, DOS），对三维自由电子：

$$g(\varepsilon) = \frac{1}{2\pi^2}\left(\frac{2m}{\hbar^2}\right)^{3/2} \varepsilon^{1/2}$$

态密度正比于 $\varepsilon^{1/2}$，在费米能处取值 $g(E_F) = \frac{3n}{2E_F}$。在有限温度 $T$ 下，各量子态的平均占据概率由**费米-狄拉克分布函数**给出：

$$f(\varepsilon) = \frac{1}{e^{(\varepsilon - \mu)/k_BT} + 1}$$

其中 $\mu$ 为化学势（在 $T=0$ 时精确等于 $E_F$，在有限温度下 $\mu \approx E_F[1 - \frac{\pi^2}{12}(k_BT/E_F)^2]$）。当 $\varepsilon = \mu$ 时，$f = 1/2$；当 $\varepsilon \ll \mu$ 时，$f \to 1$（全占据）；当 $\varepsilon \gg \mu$ 时，$f \to 0$（全空）。分布从0到1的过渡宽度约为 $4k_BT$，室温下约0.1 eV，远小于 $E_F \sim 7\ \text{eV}$，说明费米面附近仅有比例约 $k_BT/E_F \approx 1/300$ 的电子受热激发。

---

## 关键公式与推导

### 电子热容的线性温度关系

利用态密度和费米-狄拉克分布，电子总内能为：

$$U = \int_0^\infty \varepsilon \cdot g(\varepsilon) \cdot f(\varepsilon)\, d\varepsilon$$

对 $k_BT \ll E_F$ 的条件（金属室温下始终满足此条件），采用Sommerfeld展开，得到电子热容：

$$C_{el} = \frac{\pi^2}{2} \frac{k_BT}{E_F} Nk_B \equiv \gamma T$$

其中**Sommerfeld系数** $\gamma = \frac{\pi^2 Nk_B^2}{2E_F} = \frac{\pi^2}{3}k_B^2 g(E_F)$。

以铜为例，自由电子模型给出 $\gamma_{th} = 0.505\ \text{mJ/(mol·K}^2)$，实验测量值为 $\gamma_{exp} = 0.695\ \text{mJ/(mol·K}^2)$，两者之比定义**有效质量比** $m^*/m = \gamma_{exp}/\gamma_{th} = 1.38$，该偏差源于电子与声子、晶格势的相互作用（将在能带理论中用有效质量 $m^*$ 加以修正）。

低温下金属总热容由电子项和声子项（Debye模型，$C_{ph} \propto T^3$）共同组成：

$$C_{total} = \gamma T + AT^3$$

将实验数据以 $C/T$ 对 $T^2$ 作图，截距即为 $\gamma$，斜率为 $A$。这是实验上从低温比热提取费米能和声子谱信息的标准方法。

### Python 数值计算费米分布

```python
import numpy as np
import matplotlib.pyplot as plt

def fermi_dirac(E, mu, T, kB=8.617e-5):  # eV, K, eV/K
    """费米-狄拉克分布函数"""
    return 1.0 / (np.exp((E - mu) / (kB * T)) + 1)

E = np.linspace(0, 14, 500)       # 能量范围 0~14 eV（铜 E_F ≈ 7.04 eV）
mu = 7.04                          # 铜的费米能，eV

for T in [0.01, 300, 1000, 5000]:  # 温度：近零度、室温、中温、高温
    f = fermi_dirac(E, mu, T)
    plt.plot(E, f, label=f"T = {T} K")

plt.axvline(x=mu, color='gray', linestyle='--', label=f'E_F = {mu} eV')
plt.xlabel("能量 (eV)")
plt.ylabel("占据概率 f(ε)")
plt.title("铜的费米-狄拉克分布随温度变化")
plt.legend()
plt.show()
```

运行此代码可直观观察到：在 $T = 300\ \text{K}$ 时，分布函数在 $E_F = 7.04\ \text{eV}$ 附近的过渡宽度约为 $4k_BT \approx 0.10\ \text{eV}$，与 $T = 5000\ \text{K}$（$\approx 1.72\ \text{eV}$）相比极为陡峭，验证了金属在室温下仍处于"高度简并"费米气体状态。

---

## 实际应用

### 金属电阻率的温度依赖性

结合Drude电导率公式 $\sigma = ne^2\tau/m$ 与声子散射机制，可定性解释纯金属电阻率的温度行为：在德拜温度 $\Theta_D$ 以上（室温通常满足此条件，铜的 $\Theta_D = 343\ \text{K}$），电阻率 $\rho \propto T$（Bloch-Grüneisen高温极限）；在 $T \ll \Theta_D$ 时，$\rho \propto T^5$（Bloch-Grüneisen低温律）。室温下铜的电阻率实验值为 $1.68\times10^{-8}\ \Omega\cdot\text{m}$，对应 $\tau \approx 2.5\times10^{-14}\ \text{s}$，平均自由程 $\ell = v_F\tau \approx 39\ \text{nm}$，远大于铜的晶格常数 $a = 0.361\ \text{nm}$，证实电子在金属中确实能"自由"传播相当长距离。

### 金属的光学性质：等离子体频率

自由电子模型预测金属存在**等离子体频率**（Plasma frequency）：

$$\omega_p = \sqrt{\frac{ne^2}{\varepsilon_0 m}}$$

当入射光频率 $\omega < \omega_p$ 时，金属对光具有高反射率（金属光泽的来源）；当 $\omega > \omega_p$ 时，金属对光透明。铝（Al）的 $n = 1.81\times10^{29}\ \text{m}^{-3}$，计算得 $\omega_p = 2.4\times10^{16}\ \text{rad/s}$，对应紫外波长约79 nm，这正确预测了铝对可见光（380–780 nm）高反射、对远紫外透明的实验观测结果。

### 热电子发射（Richardson-Dushman方程）

金属加热后向真空发射电子的热电子发射电流密度由Richardson-Dushman方程描述：

$$J = A_0 T^2 \exp\left(-\frac{W}{k_BT}\right)$$

其中 $W$ 为金属逸出功，$A_0 = 4\pi emk_B^