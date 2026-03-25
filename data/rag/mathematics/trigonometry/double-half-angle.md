---
id: "double-half-angle"
concept: "倍角与半角公式"
domain: "mathematics"
subdomain: "trigonometry"
subdomain_name: "三角学"
difficulty: 6
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 42.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.414
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 倍角与半角公式

## 概述

倍角公式与半角公式是三角学中两组紧密相关的恒等式，专门处理角度扩大一倍或缩小一半时三角函数值的计算关系。倍角公式的核心是 $\sin 2\theta$、$\cos 2\theta$、$\tan 2\theta$ 的展开形式，而半角公式则给出 $\sin\frac{\theta}{2}$、$\cos\frac{\theta}{2}$、$\tan\frac{\theta}{2}$ 的根式表达。这两组公式本质上互为逆向操作：已知 $\theta$ 求 $2\theta$ 用倍角公式，已知 $2\theta$ 求 $\theta$ 用半角公式。

这些公式最早可追溯到古希腊天文学家托勒密（约公元 150 年）的弦表计算，他在《天文学大成》中已隐含地使用了相当于倍角公式的弦长关系。在中国，宋代天文历法中也出现了等效计算。进入 17 世纪后，随着欧洲代数符号体系的成熟，这些公式才获得今天教科书中清晰的代数形式。

倍角与半角公式在三角函数积分、傅里叶展开、信号处理以及几何证明中频繁出现。例如，积分 $\int \sin^2 x \, dx$ 无法直接计算，必须先用 $\cos 2x = 1 - 2\sin^2 x$ 降幂后再积分，这一操作完全依赖倍角公式。

---

## 核心原理

### 倍角公式的推导

倍角公式直接由两角和公式令 $\alpha = \beta = \theta$ 导出。

**正弦倍角公式：**
$$\sin 2\theta = \sin(\theta + \theta) = \sin\theta\cos\theta + \cos\theta\sin\theta = 2\sin\theta\cos\theta$$

**余弦倍角公式（三种等价形式）：**
$$\cos 2\theta = \cos^2\theta - \sin^2\theta = 2\cos^2\theta - 1 = 1 - 2\sin^2\theta$$

三种形式中，$\cos 2\theta = \cos^2\theta - \sin^2\theta$ 是最基本的，后两种是利用 $\sin^2\theta + \cos^2\theta = 1$ 代换得到的变形。不同形式适合不同场景：需要消去 $\sin\theta$ 时用第三种，需要消去 $\cos\theta$ 时用第二种。

**正切倍角公式：**
$$\tan 2\theta = \frac{2\tan\theta}{1 - \tan^2\theta} \quad (\tan\theta \neq \pm 1)$$

当 $\tan\theta = \pm 1$，即 $\theta = \pm 45°$ 或 $\theta = \pm 135°$ 等情况时，$\tan 2\theta$ 无意义，这是正切倍角公式独有的限制条件。

### 半角公式的推导

半角公式通过对余弦倍角公式进行变形得到。令 $\varphi = 2\theta$，即 $\theta = \frac{\varphi}{2}$，代入 $\cos\varphi = 1 - 2\sin^2\frac{\varphi}{2}$ 和 $\cos\varphi = 2\cos^2\frac{\varphi}{2} - 1$，解出：

$$\sin\frac{\theta}{2} = \pm\sqrt{\frac{1 - \cos\theta}{2}}$$

$$\cos\frac{\theta}{2} = \pm\sqrt{\frac{1 + \cos\theta}{2}}$$

$$\tan\frac{\theta}{2} = \pm\sqrt{\frac{1 - \cos\theta}{1 + \cos\theta}} = \frac{\sin\theta}{1 + \cos\theta} = \frac{1 - \cos\theta}{\sin\theta}$$

半角公式中的 $\pm$ 符号由 $\frac{\theta}{2}$ 所在象限决定，是半角公式区别于倍角公式的最重要特征。倍角公式没有符号不确定性，而半角公式必须根据具体角度判断正负。正切半角的后两种形式 $\frac{\sin\theta}{1+\cos\theta}$ 和 $\frac{1-\cos\theta}{\sin\theta}$ 则不含根号，也没有 $\pm$ 问题，在积分换元中特别有用。

### 降幂公式与升幂公式

倍角公式的直接应用是三角函数的降幂与升幂变换：

- **降幂（消去平方）：** $\sin^2\theta = \frac{1 - \cos 2\theta}{2}$，$\cos^2\theta = \frac{1 + \cos 2\theta}{2}$
- **升幂（引入平方）：** 将上述公式反向使用，把含 $\cos 2\theta$ 的式子化为 $\sin^2\theta$ 或 $\cos^2\theta$

降幂公式是计算 $\int \sin^n x \, dx$（$n$ 为偶数）的标准步骤，例如 $\int \sin^4 x \, dx$ 需要连续两次降幂。

---

## 实际应用

**例1：已知 $\sin\theta = \frac{3}{5}$，$\theta \in \left(\frac{\pi}{2}, \pi\right)$，求 $\sin 2\theta$ 和 $\cos 2\theta$。**

由 $\theta$ 在第二象限，$\cos\theta = -\frac{4}{5}$。则：
$$\sin 2\theta = 2 \cdot \frac{3}{5} \cdot \left(-\frac{4}{5}\right) = -\frac{24}{25}$$
$$\cos 2\theta = 1 - 2\sin^2\theta = 1 - 2 \cdot \frac{9}{25} = \frac{7}{25}$$

**例2：化简 $\frac{1 - \cos 120°}{\sin 120°}$。**

这正是 $\tan\frac{120°}{2} = \tan 60°$ 的半角正切公式形式，直接得出结果为 $\sqrt{3}$，无需逐步计算。

**例3：证明 $\sin 3\theta = 3\sin\theta - 4\sin^3\theta$（三倍角公式）。**

将 $\sin 3\theta = \sin(2\theta + \theta)$ 展开后，用倍角公式替换 $\sin 2\theta = 2\sin\theta\cos\theta$，再用 $\cos^2\theta = 1 - \sin^2\theta$ 消去余弦，可完整推导出三倍角公式，全程只用倍角公式和平方关系。

**万能公式（半角正切换元）：** 令 $t = \tan\frac{\theta}{2}$，则：
$$\sin\theta = \frac{2t}{1+t^2}, \quad \cos\theta = \frac{1-t^2}{1+t^2}, \quad \tan\theta = \frac{2t}{1-t^2}$$

这一换元法在求解含 $\sin\theta$ 和 $\cos\theta$ 的方程及计算三角有理式的积分（如 $\int \frac{1}{a + b\sin\theta} d\theta$）时将问题转化为有理函数问题。

---

## 常见误区

**误区1：余弦倍角公式只有一种形式。**

许多学生只记住 $\cos 2\theta = \cos^2\theta - \sin^2\theta$，忽略了 $1 - 2\sin^2\theta$ 和 $2\cos^2\theta - 1$ 两种变形。实际上，遇到只含 $\sin\theta$ 的表达式时，必须用 $1 - 2\sin^2\theta$ 形式；遇到只含 $\cos\theta$ 时用 $2\cos^2\theta - 1$ 形式。强行使用第一种形式反而会引入多余变量，增加计算难度。

**误区2：半角公式的 $\pm$ 可以忽略或随意选取。**

例如，$\cos 135° = -\frac{\sqrt{2}}{2}$，若用半角公式计算 $\cos\frac{270°}{2} = \cos 135°$，代入得 $\pm\sqrt{\frac{1 + \cos 270°}{2}} = \pm\sqrt{\frac{1}{2}}$，必须根据 $135°$ 在第二象限（余弦为负）选取负号，得 $-\frac{\sqrt{2}}{2}$。忽略象限判断会得到符号错误的结果。

**误区3：万能公式适用于所有 $\theta$。**

令 $t = \tan\frac{\theta}{2}$ 时，当 $\theta = \pi$（即 $\frac{\theta}{2} = 90°$）时，$\tan\frac{\theta}{2}$ 无意义，万能公式在 $\theta = (2k+1)\pi$ 处失效。在解方程或积分时若 $\theta = \pi$ 是解，必须单独验证，不能仅依赖万能公式换元后的结果。

---

## 知识关联

**前置基础：** 倍角公式完全由两角和差公式（$\sin(\alpha\pm\beta)$、$\cos(\alpha\pm\beta)$）令 $\alpha = \beta$ 特殊化而来，若对和差公式不熟练，倍角公式的推导过程就无法独立完成。而半角公式又依赖倍角公式的余弦形式进行反解，形成了"和差 → 倍角 → 半角"的推导链。

**延伸方向：** 倍角思想可推广至 $n$ 倍角公式，利用棣莫弗定理 $(\cos\theta + i\sin\theta)^n = \cos n\theta + i\sin n\theta$ 可导出任意整数倍