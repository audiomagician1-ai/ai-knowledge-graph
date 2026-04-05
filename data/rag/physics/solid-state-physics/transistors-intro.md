---
id: "transistors-intro"
concept: "晶体管简介"
domain: "physics"
subdomain: "solid-state-physics"
subdomain_name: "固态物理"
difficulty: 5
is_milestone: false
tags: ["应用"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 95.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.983
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 晶体管简介

## 概述

晶体管（Transistor）是利用半导体材料实现电流放大或电子开关功能的三端有源器件，由贝尔实验室的肖克利（William Shockley）、巴丁（John Bardeen）和布拉顿（Walter Brattain）于1947年12月16日发明。布拉顿和巴丁制造了世界上第一个点接触型晶体管，其放大倍数约为18倍，工作频率仅约10kHz——与今日GHz级器件相比不可同日而语，但这一成果彻底终结了真空管时代。三位发明者因此荣获1956年诺贝尔物理学奖。

"Transistor"一词由贝尔实验室工程师约翰·皮尔斯（John R. Pierce）命名，源自"Transfer Resistor"（转移电阻），意指通过输入端小信号控制输出端大信号的特性。1958年，德州仪器的基尔比（Jack Kilby）将晶体管与其他元件集成于单片锗基板，制造了第一块集成电路；此后摩尔定律预测芯片晶体管数量每约18个月翻倍，这一趋势从1970年代延续至今。英特尔Alder Lake（2021年）在单颗封装内集成约100亿个晶体管，台积电3nm工艺节点（2022年量产）的最小栅极长度缩至约3nm，约等于10个硅原子并排的宽度。

晶体管的两大主流类型为**双极结型晶体管（BJT，Bipolar Junction Transistor）**和**金属氧化物半导体场效应晶体管（MOSFET，Metal-Oxide-Semiconductor Field-Effect Transistor）**。前者以电流控制电流，由电子和空穴双载流子参与导电；后者以电压控制电流，栅极与沟道之间的SiO₂绝缘层使输入阻抗极高。两者的物理机制、偏置方式与应用场景均有本质差别，下文逐一展开。

参考教材：《微电子器件》（施敏 著，赵鹤鸣 等译，电子工业出版社，2013年），以及 Neamen, D.A., *Semiconductor Physics and Devices*, 4th ed., McGraw-Hill, 2012。

---

## 核心原理

### BJT（双极结型晶体管）的结构与放大机制

BJT由两个背靠背的PN结构成，共有三个掺杂区域：发射区（Emitter）、基区（Base）和集电区（Collector），对应三个外部电极E、B、C。按掺杂组合分为NPN型（发射区N⁺、基区P、集电区N）和PNP型（发射区P⁺、基区N、集电区P）。

以NPN型为例，各区掺杂浓度存在刻意设计的不对称性：

- **发射区**：高浓度N型掺杂（典型值 $N_E \approx 10^{18}\ \text{cm}^{-3}$），目的是提供充足的电子注入基区；
- **基区**：薄层P型掺杂（典型宽度 $W_B \approx 0.1\text{–}1\ \mu\text{m}$，掺杂浓度 $N_B \approx 10^{17}\ \text{cm}^{-3}$），越薄则载流子复合概率越低，β越高；
- **集电区**：低浓度N型掺杂（$N_C \approx 10^{15}\ \text{cm}^{-3}$），面积最大，承受反偏电压，收集穿越基区的电子。

BJT工作在放大区时，**发射结正偏（$V_{BE} \approx 0.6\text{–}0.7\text{V}$，硅管）、集电结反偏**。发射结正偏使发射区大量电子越过势垒注入基区；基区极薄且掺杂浓度低，电子在其中的少数载流子扩散长度 $L_n \gg W_B$，绝大多数电子穿越基区后被集电结强电场（反偏产生）扫入集电区，仅极少数在基区与空穴复合，形成微小的基极电流 $I_B$。

BJT的**共射极直流电流增益**定义为：

$$\beta = h_{FE} = \frac{I_C}{I_B}$$

由此得到三极电流关系：

$$I_E = I_B + I_C = (1 + \beta)\,I_B$$

典型硅NPN晶体管（如2N2222A）的 $\beta$ 值约为100–300，意味着仅需向基极注入10μA电流，即可驱动1–3mA的集电极电流。BJT之所以称为"双极型"，正是因为电子（多数载流子）与空穴（少数载流子）**同时参与**导电过程。

> 思考：若将基区宽度 $W_B$ 从1μm减小至0.1μm，电流增益 $\beta$ 将如何变化？为什么？

---

### MOSFET的结构与场效应导通机制

MOSFET由栅极（Gate, G）、漏极（Drain, D）、源极（Source, S）和衬底（Body, B）四端构成。以**N沟道增强型MOSFET（NMOS）**为例：

- 衬底为P型硅；
- 源区与漏区为高掺杂N⁺区（$N_D \approx 10^{20}\ \text{cm}^{-3}$），两者之间隔以P型沟道区（长度L即栅极长度）；
- 栅极下方生长一层极薄的热氧化SiO₂绝缘层，台积电7nm工艺的等效氧化层厚度（EOT）约0.9nm，28nm工艺约1.2nm；
- 栅极材料早期为多晶硅，现代高k金属栅工艺（High-k/Metal Gate）改用HfO₂（介电常数 $\kappa\approx25$）替代SiO₂（$\kappa=3.9$）以降低漏电。

MOSFET的导通由**栅源电压 $V_{GS}$** 控制：当 $V_{GS}$ 超过阈值电压 $V_{th}$（典型值0.3–0.7V，随工艺节点降低而下降）时，栅极下方P型衬底表面感应出足够多的电子，形成N型反型层（导电沟道），漏源之间电流得以流通。

**线性区**（$V_{DS} < V_{GS} - V_{th}$）漏极电流：

$$I_{DS} = \mu_n C_{ox} \frac{W}{L} \left[ (V_{GS} - V_{th})\,V_{DS} - \frac{V_{DS}^2}{2} \right]$$

**饱和区**（$V_{DS} \geq V_{GS} - V_{th}$，沟道夹断）漏极电流：

$$I_{DS} = \frac{1}{2}\,\mu_n C_{ox} \frac{W}{L} (V_{GS} - V_{th})^2$$

其中：$\mu_n$ 为电子迁移率（体硅约1400 cm²/V·s，但实际反型层中约200–500 cm²/V·s）；$C_{ox} = \varepsilon_{ox}/t_{ox}$ 为栅氧单位面积电容；$W/L$ 为沟道宽长比，是设计者调整器件驱动能力的核心参数。

由于栅极与沟道之间被SiO₂完全隔断，**MOSFET栅极输入阻抗极高**（$>10^{14}\ \Omega$），静态栅极电流几乎为零（飞安量级），这使MOSFET在数字集成电路和低功耗应用中远优于BJT。

---

### 放大模式与开关模式的工作区划分

BJT和MOSFET均可通过改变偏置条件工作在放大或开关两种模式：

**BJT工作区总结：**

| 工作区 | 发射结 | 集电结 | 特点 |
|--------|--------|--------|------|
| 截止区 | 反偏 | 反偏 | $I_C \approx 0$，相当于断路 |
| 放大区（主动区） | 正偏 | 反偏 | $I_C = \beta I_B$，线性放大 |
| 饱和区 | 正偏 | 正偏 | $V_{CE(sat)} \approx 0.1\text{–}0.3\text{V}$，相当于闭合开关 |

**MOSFET工作区总结：**

| 工作区 | 条件 | 特点 |
|--------|------|------|
| 截止区 | $V_{GS} < V_{th}$ | $I_{DS} \approx 0$ |
| 线性区 | $V_{GS} > V_{th}$，$V_{DS} < V_{GS}-V_{th}$ | 沟道完整，$I_{DS}$ 随 $V_{DS}$ 线性增大 |
| 饱和区 | $V_{GS} > V_{th}$，$V_{DS} \geq V_{GS}-V_{th}$ | 沟道夹断，$I_{DS}$ 受 $V_{GS}$ 控制，用于放大 |

数字逻辑电路中MOSFET在截止区与线性区（对应"关"与"开"）之间切换，导通电阻 $R_{on}$ 越小（典型值数Ω至数百Ω）开关性能越好。

---

## 关键公式与参数

以下代码演示了利用MOSFET饱和区公式计算不同 $V_{GS}$ 下漏极电流（Python 示例，参数取自典型0.18μm工艺NMOS）：

```python
import numpy as np
import matplotlib.pyplot as plt

# 典型 0.18μm NMOS 参数
mu_n = 270e-4       # 电子迁移率 270 cm²/V·s → 转换为 m²/V·s
C_ox = 8.6e-3       # 栅氧电容 8.6 mF/m²（t_ox ≈ 4nm，ε_ox=3.45e-11 F/m）
W = 10e-6           # 沟道宽度 10 μm
L = 0.18e-6         # 沟道长度 0.18 μm
V_th = 0.5          # 阈值电压 0.5 V

V_GS_values = np.arange(0.6, 1.4, 0.2)  # V_GS 从 0.6V 到 1.2V

for V_GS in V_GS_values:
    V_DS_sat = V_GS - V_th
    I_DS_sat = 0.5 * mu_n * C_ox * (W / L) * V_DS_sat**2
    print(f"V_GS = {V_GS:.1f}V, V_DS_sat = {V_DS_sat:.2f}V, "
          f"I_DS(饱和) = {I_DS_sat*1e3:.3f} mA")
```

运行后可得：当 $V_{GS}=0.6\text{V}$ 时 $I_{DS}\approx0.13\text{mA}$，当 $V_{GS}=1.2\text{V}$ 时 $I_{DS}\approx2.16\text{mA}$，体现了MOSFET电流随 $(V_{GS}-V_{th})^2$ 的平方律特性。

BJT的小信号跨导 $g_m$ 是描述放大能力的核心参数：

$$g_m = \frac{\partial I_C}{\partial V_{BE}}\bigg|_{Q} = \frac{I_{CQ}}{V_T}$$

其中 $V_T = kT/q \approx 26\text{mV}$（室温300K下），$I_{CQ}$ 为静态工作点电流。若 $I_{CQ}=1\text{mA}$，则 $g_m \approx 38.5\text{mA/V}$，意味着 $V_{BE}$ 变化1mV即引起约38.5μA的集电极电流变化。

---

## 实际应用场景

### 共射极放大电路（BJT模拟放大）

**例如**，设计一个音频前置放大器时，常采用NPN型BJT（如BC547，$\beta_{\min}=110$）的共射极配置。设 $V_{CC}=12\text{V}$，$R_C=4.7\text{k}\Omega$，静态工作点 $I_{CQ}=1\text{mA}$，则：

- 小信号电压增益：$A_v = -g_m R_C = -(38.5\text{mA/V})(4.7\text{k}\Omega) \approx -181$，即输入10mV正弦信号可得约1.81V输出（反相）；
- 频率响应上限受器件寄生电容（米勒效应）限制，BC547的特征频率 $f_T\approx300\text{MHz}$。

### CMOS