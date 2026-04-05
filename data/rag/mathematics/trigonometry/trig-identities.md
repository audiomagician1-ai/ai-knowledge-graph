---
id: "trig-identities"
concept: "三角恒等式"
domain: "mathematics"
subdomain: "trigonometry"
subdomain_name: "三角学"
difficulty: 5
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 三角恒等式

## 概述

三角恒等式是指对定义域内**所有**角度值都成立的三角函数等式，与仅在特定角度成立的三角方程有本质区别。最根本的三角恒等式来源于单位圆的几何定义：在半径为1的圆上，角度 θ 对应的点坐标为 (cos θ, sin θ)，由勾股定理直接推导出 sin²θ + cos²θ = 1，这一等式对任意实数 θ 均成立，无需求解，无需验证特例。

三角恒等式的系统化研究可追溯至公元9至10世纪的伊斯兰数学家。波斯数学家阿布·瓦法（Abu al-Wafa，940–998年）在天文计算中首次将正弦、余弦、正切作为独立函数处理，并推导出多个基本关系式。欧洲数学家在16世纪翻译阿拉伯文献后，将这些恒等式整合进对数与球面三角学的框架中，形成现代三角学体系。

三角恒等式的重要性体现在：它将六个三角函数（sin、cos、tan、cot、sec、csc）之间的代数关系固定下来，使得任何三角表达式都可以仅用 sin 和 cos 来表示，为积分、微分方程求解和信号处理中的化简运算提供了不可替代的工具。

---

## 核心原理

### 毕达哥拉斯恒等式（Pythagorean Identities）

毕达哥拉斯恒等式是所有三角恒等式中最基础的一组，共有三个，全部由 sin²θ + cos²θ = 1 衍生：

**第一式：**
$$\sin^2\theta + \cos^2\theta = 1$$

其中 θ 为任意实数。将两边除以 cos²θ（θ ≠ π/2 + nπ），得：

**第二式：**
$$\tan^2\theta + 1 = \sec^2\theta$$

将两边除以 sin²θ（θ ≠ nπ），得：

**第三式：**
$$1 + \cot^2\theta = \csc^2\theta$$

这三个恒等式的几何意义清晰：第一式描述单位圆上的点到原点距离恒为1；第二式对应以 cos θ 为底边的直角三角形中斜边与底边的关系；第三式对应以 sin θ 为底边的情形。

### 倒数恒等式与商恒等式

六个三角函数之间存在三对倒数关系：

$$\sin\theta \cdot \csc\theta = 1, \quad \cos\theta \cdot \sec\theta = 1, \quad \tan\theta \cdot \cot\theta = 1$$

以及两个商恒等式：

$$\tan\theta = \frac{\sin\theta}{\cos\theta}, \quad \cot\theta = \frac{\cos\theta}{\sin\theta}$$

这六个关系式将 tan、cot、sec、csc 完全归约为 sin 和 cos 的表达式，意味着理论上只需掌握 sin 和 cos 的性质，即可推导其他四个函数的所有行为。

### 奇偶性恒等式与余角恒等式

奇偶性恒等式描述负角与正角之间的关系：

$$\sin(-\theta) = -\sin\theta \quad (\text{sin为奇函数})$$
$$\cos(-\theta) = \cos\theta \quad (\text{cos为偶函数})$$
$$\tan(-\theta) = -\tan\theta$$

余角恒等式（co-function identities）指出，名字带"co"前缀的函数与不带"co"的函数之间存在 π/2 的互补关系：

$$\sin\theta = \cos\!\left(\frac{\pi}{2} - \theta\right), \quad \tan\theta = \cot\!\left(\frac{\pi}{2} - \theta\right), \quad \sec\theta = \csc\!\left(\frac{\pi}{2} - \theta\right)$$

"co"这一前缀本身即来源于"complementary（余角）"，这一命名规律可帮助记忆六个余角恒等式。

---

## 实际应用

**化简三角表达式：** 在微积分中计算 ∫ sin²x dx 时，需先用第一毕达哥拉斯恒等式将 sin²x 改写为 (1 - cos 2x)/2（结合半角公式），才能完成积分。若直接积分 sin²x 而不化简，则无法得到初等函数形式的结果。

**验证恒等式的标准步骤：** 证明 (1 - cos²θ)/sin θ = sin θ 时，左侧分子用第一毕达哥拉斯恒等式替换为 sin²θ，得 sin²θ/sin θ = sin θ，右侧相等，证毕。注意：恒等式的证明必须从一侧出发，逐步变形到另一侧，不能两边同时操作（否则可能隐藏除以零等错误）。

**电路分析中的应用：** 交流电中电压 v(t) = V₀ sin(ωt + φ) 与电流 i(t) = I₀ cos(ωt) 的功率计算涉及乘积 sin·cos，必须用积化和差（由毕达哥拉斯恒等式衍生的和角公式推导）将其化为单一频率项，才能提取有效功率（实功率）。

---

## 常见误区

**误区一：将 sin²θ 误写为 sin(θ²)**
sin²θ 是 (sin θ)² 的缩写，表示先求正弦值再平方；而 sin(θ²) 表示对 θ² 取正弦，两者数值完全不同。例如当 θ = π/4 时，sin²(π/4) = (√2/2)² = 1/2，而 sin((π/4)²) = sin(π²/16) ≈ 0.581，差异明显。毕达哥拉斯恒等式中的 sin²θ 只适用于前者这种解释。

**误区二：认为 √(sin²θ + cos²θ) = sin θ + cos θ**
由毕达哥拉斯恒等式知 sin²θ + cos²θ = 1，故 √(sin²θ + cos²θ) = 1。但学生常错误地类比代数中 √(a² + b²) = a + b（这本身也是错误的），将其化为 sin θ + cos θ。实际上 sin θ + cos θ = √2 · sin(θ + π/4)，最大值为 √2，而非恒等于1。

**误区三：在除法化简时忽略定义域限制**
将 sin²θ + cos²θ = 1 两边除以 cos²θ 得到 tan²θ + 1 = sec²θ 时，必须排除 cos θ = 0 的情况，即 θ ≠ π/2 + nπ（n 为整数）。若在解题中不注明此条件，严格来说是不完整的证明，在高等数学中可能导致推导错误。

---

## 知识关联

**前置概念——单位圆：** 毕达哥拉斯恒等式 sin²θ + cos²θ = 1 本质上就是单位圆方程 x² + y² = 1 的直接重述，其中 x = cos θ，y = sin θ。没有单位圆的定义，这个恒等式只能被当作公式死记，无法理解其几何必然性。

**后续概念——和差化积公式：** sin(α ± β) 和 cos(α ± β) 的展开公式（如 cos(α - β) = cos α cos β + sin α sin β）可由单位圆上两点距离公式结合毕达哥拉斯恒等式推导而来；反过来，和差化积公式又可以推出倍角公式 sin 2θ = 2 sin θ cos θ，形成完整的恒等式体系。

**后续概念——三角方程：** 三角恒等式是求解三角方程的核心工具，例如将方程 2sin²θ - cos θ - 1 = 0 中的 sin²θ 用 1 - cos²θ 替换，转化为关于 cos θ 的二次方程 2cos²θ + cos θ - 1 = 0 再求解。

**后续概念——双曲函数：** 双曲函数 cosh x 和 sinh x 满足恒等式 cosh²x - sinh²x = 1，符号上与毕达哥拉斯恒等式 cos²θ + sin²θ = 1 仅差一个负号，这一差异源于双曲函数基于双曲线（x² - y² = 1）而非圆（x² + y² = 1），体现了欧氏几何与双曲几何中"距离"定义的根本不同。