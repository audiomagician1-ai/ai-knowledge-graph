---
id: "schrodinger-equation"
name: "薛定谔方程"
subdomain: "quantum-mechanics"
subdomain_name: "量子力学"
difficulty: 6
is_milestone: true
tags: ["里程碑"]
generated_at: "2026-03-19T09:45:51"
---

# 薛定谔方程

## 核心内容

**薛定谔方程**是量子力学的核心方程，描述量子态的时间演化。

**含时薛定谔方程**：
$$i\hbar\frac{\partial}{\partial t}\Psi(\vec{r},t) = \hat{H}\Psi(\vec{r},t)$$

其中 $\hat{H}$ 是哈密顿算符：
$$\hat{H} = -\frac{\hbar^2}{2m}\nabla^2 + V(\vec{r},t)$$

**定态薛定谔方程**（当势能不显含时间时）：
$$\hat{H}\psi(\vec{r}) = E\psi(\vec{r})$$

**关键概念**：
- $|\Psi(\vec{r},t)|^2$ 是概率密度
- 波函数必须**归一化**：$\int|\Psi|^2 d^3r = 1$
- 能量 $E$ 是哈密顿算符的**本征值**
