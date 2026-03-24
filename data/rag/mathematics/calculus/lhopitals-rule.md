---
id: "lhopitals-rule"
concept: "洛必达法则"
domain: "mathematics"
subdomain: "calculus"
subdomain_name: "微积分"
difficulty: 6
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 洛必达法则

## 概述

洛必达法则（L'Hôpital's Rule）是处理 $\frac{0}{0}$ 型和 $\frac{\infty}{\infty}$ 型不定式极限的系统性方法：若 $\lim_{x \to a} f(x) = \lim_{x \to a} g(x) = 0$（或同为 $\infty$），且 $g'(x) \neq 0$，则 $\lim_{x \to a} \frac{f(x)}{g(x)} = \lim_{x \to a} \frac{f'(x)}{g'(x)}$。其本质是用分子分母各自求导之后的比值来替代原极限，而**不是**对整个分式使用商的求导法则。

该法则以法国数学家纪尧姆·德·洛必达（Guillaume de l'Hôpital，1661–1704）命名，但实际上由约翰·伯努利（Johann Bernoulli）于1694年左右发现，并通过付费协议转让给洛必达，后者在1696年出版的《无穷小分析》（*Analyse des Infiniment Petits*）中将其公开发表——这是历史上第一本微积分教材。

洛必达法则之所以重要，在于自然对数、三角函数、指数函数在特定点处构成的极限（如 $\lim_{x \to 0} \frac{\sin x}{x}$、$\lim_{x \to \infty} \frac{x^n}{e^x}$）用代数化简难以直接处理，而该法则将极限问题转化为导数计算，系统地解决了整类问题。

---

## 核心原理

### 适用条件的精确表述

洛必达法则有三个必须同时满足的前提条件：**第一**，极限形式必须是 $\frac{0}{0}$ 或 $\frac{\infty}{\infty}$（其他形式需先变形）；**第二**，$f(x)$ 和 $g(x)$ 在点 $a$ 的某去心邻域内均可导；**第三**，$g'(x)$ 在该邻域内不为零。其理论依据是柯西中值定理：存在 $c \in (a, x)$ 使得 $\frac{f(x) - f(a)}{g(x) - g(a)} = \frac{f'(c)}{g'(c)}$，当 $f(a) = g(a) = 0$ 时直接得到法则形式。该法则对 $x \to a$、$x \to a^+$、$x \to \infty$ 等各种极限过程均成立。

### 七种不定式的化简路径

除 $\frac{0}{0}$ 和 $\frac{\infty}{\infty}$ 外，另外五种不定式需先代数变形，再应用洛必达法则：

- **$0 \cdot \infty$ 型**：将其中一个因子取倒数移至分母，化为 $\frac{0}{1/\infty} = \frac{0}{0}$ 型。例如 $\lim_{x \to 0^+} x \ln x = \lim_{x \to 0^+} \frac{\ln x}{1/x}$，转化为 $\frac{\infty}{\infty}$ 型后求导得 $\lim_{x \to 0^+} \frac{1/x}{-1/x^2} = \lim_{x \to 0^+}(-x) = 0$。
- **$\infty - \infty$ 型**：通分化为分式。
- **$1^\infty$、$0^0$、$\infty^0$ 型**：取对数 $\ln y = g(x) \ln f(x)$，转化为 $0 \cdot \infty$ 型处理。

### 法则的迭代使用与失效情形

洛必达法则可以连续使用：若求导后仍为不定式，可再次求导。典型例子是 $\lim_{x \to \infty} \frac{x^n}{e^x}$，需对分子连续求导 $n$ 次，最终分子变为常数 $n!$，分母仍为 $e^x \to \infty$，故极限为 $0$。这说明**指数函数比任意多项式增长更快**。

但法则并非万能：若 $\lim_{x \to \infty} \frac{f'(x)}{g'(x)}$ 本身不存在，不能反推原极限不存在。例如 $\lim_{x \to \infty} \frac{x + \sin x}{x}$，直接化简为 $1 + \lim_{x \to \infty} \frac{\sin x}{x} = 1$，但若强行用洛必达法则则得 $\frac{1 + \cos x}{1}$，该极限不存在，给出错误结论。

---

## 实际应用

**例1（$\frac{0}{0}$ 型标准应用）**：求 $\lim_{x \to 0} \frac{e^x - 1 - x}{x^2}$。分子分母在 $x=0$ 处均为 $0$，第一次求导得 $\lim_{x \to 0} \frac{e^x - 1}{2x}$，仍为 $\frac{0}{0}$ 型，第二次求导得 $\lim_{x \to 0} \frac{e^x}{2} = \frac{1}{2}$。此结果与泰勒展开 $e^x = 1 + x + \frac{x^2}{2} + \cdots$ 完全吻合。

**例2（$\frac{\infty}{\infty}$ 型与对数）**：求 $\lim_{x \to +\infty} \frac{\ln x}{x^{0.001}}$。求导后得 $\lim_{x \to +\infty} \frac{1/x}{0.001 x^{-0.999}} = \lim_{x \to +\infty} \frac{1000}{x^{0.001}} = 0$，说明对数函数比任意正幂次增长更慢，即使幂次仅有 $0.001$。

**例3（$1^\infty$ 型）**：求 $\lim_{x \to 0} (1 + \sin x)^{1/x}$。令 $y = (1 + \sin x)^{1/x}$，则 $\ln y = \frac{\ln(1 + \sin x)}{x}$，这是 $\frac{0}{0}$ 型，求导得 $\lim_{x \to 0} \frac{\cos x / (1 + \sin x)}{1} = 1$，故原极限为 $e^1 = e$。

---

## 常见误区

**误区一：把"商的求导法则"与洛必达法则混淆。** 洛必达法则是对分子 $f(x)$ 和分母 $g(x)$ **分别求导**，即 $\frac{f'(x)}{g'(x)}$，而不是对整个分式 $\frac{f(x)}{g(x)}$ 求导所得的 $\frac{f'(x)g(x) - f(x)g'(x)}{[g(x)]^2}$。两者结果截然不同，混淆是初学者最高频的计算错误。

**误区二：在非不定式情况下滥用法则。** 若极限形式不是 $\frac{0}{0}$ 或 $\frac{\infty}{\infty}$，直接使用洛必达法则会得出错误答案。例如 $\lim_{x \to 0} \frac{x + 1}{x + 2}$ 可以直接代入得 $\frac{1}{2}$，若误用法则对分子分母求导则得 $\frac{1}{1} = 1$，完全错误。

**误区三：忽略法则的可导性前提，盲目连续套用。** 对于 $\lim_{x \to 0} \frac{|x|}{x}$，分子在 $x=0$ 处不可导，洛必达法则不适用；此极限本身不存在（左右极限分别为 $-1$ 和 $1$）。当函数含绝对值或分段定义时，必须先验证可导性。

---

## 知识关联

洛必达法则的合法性完全依赖**柯西中值定理**，后者是比拉格朗日中值定理更一般的形式，因此不理解柯西中值定理就无法真正证明洛必达法则成立。同时，法则的每一步计算都要求准确掌握**导数运算规则**——链式法则、对数求导、指数函数和三角函数的导数公式直接决定化简是否正确。

从应用的角度看，洛必达法则与**泰勒展开**解决同类问题：泰勒展开通过级数展开消去零因子，洛必达法则通过逐次求导实现同样目标，两种方法在处理高阶不定式时往往可以互相验证。对于 $\frac{0}{0}$ 型，等价无穷小替换（如 $\sin x \sim x$，$\ln(1+x) \sim x$）是比洛必达法则更快的工具，但只适用于乘除结构，洛必达法则则适用于更复杂的加减混合结构。
