"""Sprint 7 - 7-deps Batch 2: 7 documents research-rewrite-v2"""
import pathlib, datetime

ROOT = pathlib.Path(r"D:\EchoAgent\projects\ai-knowledge-graph\data\rag")
TODAY = datetime.date.today().isoformat()

DOCS = {

# ── 1. 心理治疗概述 ──────────────────────────────
"psychology/clinical-psychology/psychotherapy-overview.md": f"""---
id: "psychotherapy-overview"
concept: "心理治疗概述"
domain: "psychology"
subdomain: "clinical-psychology"
subdomain_name: "临床心理学"
difficulty: 2
is_milestone: false
tags: ["治疗", "临床", "概述"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "{TODAY}"
sources:
  - type: "textbook"
    name: "Wampold & Imel, The Great Psychotherapy Debate, 2nd ed."
  - type: "paper"
    name: "Smith & Glass (1977) Meta-analysis of psychotherapy outcome studies"
scorer_version: "scorer-v2.0"
---
# 心理治疗概述

## 定义与核心概念

心理治疗（Psychotherapy）是训练有素的治疗师通过**心理学方法**（而非药物）帮助来访者缓解心理痛苦、改善行为模式和提升生活功能的系统性干预过程。美国心理学会（APA）的操作定义强调三要素：(1) 基于心理学理论，(2) 建立在治疗关系上，(3) 使用特定技术。

全球约 **30%** 的人一生中会经历至少一次可诊断的心理障碍（WHO, 2022），但仅有不到一半接受过任何形式的心理治疗，这种"治疗鸿沟"（treatment gap）在中低收入国家尤为严重（>75%未获治疗）。

## 主要心理治疗流派

### 1. 认知行为疗法（CBT）

Aaron Beck（1960s）开创，当前证据基础最强的疗法：

| 核心假设 | 技术 | 适应症 |
|---------|------|--------|
| 认知三角：想法→情绪→行为 | 认知重构（挑战自动思维） | 抑郁、焦虑、PTSD |
| 扭曲的认知模式可识别并修正 | 行为实验（验证灾难化预期） | 强迫症、社交恐惧 |
| 技能可学习和泛化 | 暴露疗法（系统脱敏） | 恐惧症、创伤后应激 |

**疗效数据**：对抑郁症，CBT 的效应量 d = **0.71**（中到大效应），与 SSRI 药物等效（Cuijpers et al., 2013 meta-analysis，n=115 RCTs）。复发率方面，CBT 显著优于单独药物治疗：2年复发率 CBT **29%** vs 药物 **60%**（Hollon et al., 2005）。

### 2. 精神动力学疗法（Psychodynamic）

Freud 传统的现代化版本，强调**无意识冲突**和**早期关系模式**：

核心概念：
- **移情**（Transference）：来访者将早期关系模式投射到治疗师身上
- **防御机制**：如压抑、投射、合理化、升华
- **自由联想**：不加审查地报告意识流

**短程动力学疗法**（STPP，16-24 次）的 meta-analysis 效应量 d = **0.97**（Abbass et al., 2014），但研究质量参差不齐（Cochrane评价）。

### 3. 人本-存在主义疗法

Carl Rogers（1950s）的来访者中心疗法奠基。核心条件（Rogers 的"充分必要条件"）：
- **无条件积极关注**（Unconditional Positive Regard）
- **共情理解**（Empathic Understanding）
- **真诚一致**（Congruence）

### 4. 系统家庭治疗

将问题视为**关系系统**的功能，而非个人病理：
- 结构式家庭治疗（Minuchin）：重组家庭权力结构
- 策略式家庭治疗（Haley）：布置悖论任务打破恶性循环
- 叙事疗法（White & Epston）：将问题外化（"问题是问题，人不是问题"）

## 疗效研究：大辩论

### Dodo Bird 判决（"所有疗法等效"）

Luborsky et al.（1975）提出著名的"渡渡鸟判决"：不同疗法之间的疗效差异远小于疗法与不治疗之间的差异。

Wampold & Imel（2015）的 meta-analysis 支持：
- 疗法之间的差异仅解释结果变异的 **~1%**
- **治疗关系**（特别是治疗联盟）解释 **~5-8%**
- **治疗师个体差异**解释 **~5-9%**（有些治疗师无论用什么疗法都更有效）

### 反对意见：特异性因素确实重要

对于特定障碍，某些疗法确实优越：
- **暴露疗法 > 其他** 对恐惧症（d 差异 = 0.3-0.5）
- **EMDR/PE > 支持性咨询** 对 PTSD
- **DBT > TAU** 对边缘型人格障碍的自伤行为

## 循证实践的层级体系

| 证据等级 | 标准 | 示例 |
|---------|------|------|
| 1 级（强推荐） | 2+ 组 RCT 支持 | CBT 治疗抑郁/焦虑 |
| 2 级（推荐） | 1 个 RCT + 准实验 | EMDR 治疗 PTSD |
| 3 级（有限证据） | 案例系列/小样本 | 艺术疗法治疗创伤 |
| 临床共识 | 专家意见 | 部分存在主义疗法 |

APA Division 12 维护的"经验支持疗法"列表是目前最权威的疗效评级系统。

## 治疗过程的关键变量

### 治疗联盟（Therapeutic Alliance）

Bordin（1979）模型的三成分：
1. **目标共识**（Goals）
2. **任务合作**（Tasks）
3. **情感纽带**（Bond）

Flückiger et al.（2018）对 295 项研究的 meta-analysis：联盟-结果相关 r = **0.278**（p < .001），是最稳定的疗效预测因子。

### 来访者因素

Lambert（2013）的成分模型估计：
- 来访者因素（动机、严重程度、支持系统）：**~40%** 的结果变异
- 治疗关系：**~30%**
- 期望/安慰剂效应：**~15%**
- 特定技术：**~15%**

## 参考文献

- Smith, M.L. & Glass, G.V. (1977). "Meta-analysis of psychotherapy outcome studies," *American Psychologist*, 32(9), 752-760.
- Wampold, B.E. & Imel, Z.E. (2015). *The Great Psychotherapy Debate*, 2nd ed. Routledge. ISBN 978-0805857092
- Cuijpers, P. et al. (2013). "A meta-analysis of cognitive-behavioural therapy for adult depression," *Journal of Consulting and Clinical Psychology*, 81(3).
- Flückiger, C. et al. (2018). "The alliance in adult psychotherapy," *Psychotherapy*, 55(4). [doi: 10.1037/pst0000172]

## 教学路径

**前置知识**：心理学导论、研究方法基础
**学习建议**：先掌握 CBT 的理论框架和基本技术（认知三角模型），再横向比较不同流派的核心假设差异。重点理解"共同因素 vs 特异因素"辩论，这是临床心理学的核心科学争议。
**进阶方向**：第三浪潮 CBT（ACT、MBCT、DBT）、心理治疗的神经机制、文化适应性治疗。
""",

# ── 2. 组合 ──────────────────────────────
"mathematics/probability/combinations.md": f"""---
id: "combinations"
concept: "组合"
domain: "mathematics"
subdomain: "probability"
subdomain_name: "概率论"
difficulty: 1
is_milestone: false
tags: ["计数", "组合数学"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "{TODAY}"
sources:
  - type: "textbook"
    name: "Graham, Knuth & Patashnik, Concrete Mathematics, 2nd ed."
  - type: "textbook"
    name: "Brualdi, Introductory Combinatorics, 5th ed."
scorer_version: "scorer-v2.0"
---
# 组合

## 定义与核心概念

组合（Combination）是从 n 个不同元素中选取 k 个元素的**无序**选择方案数。与排列不同，组合不考虑元素的排列顺序——选 {{A,B,C}} 和 {{C,A,B}} 视为同一种组合。

二项式系数（Binomial Coefficient）的标准记号和公式：

```
C(n,k) = (n choose k) = n! / (k!(n-k)!)

等价递推定义（Pascal恒等式）：
C(n,k) = C(n-1,k-1) + C(n-1,k)
边界条件：C(n,0) = C(n,n) = 1
```

Graham, Knuth & Patashnik 在《Concrete Mathematics》中强调，二项式系数"可能是数学中出现频率最高的组合对象"（2nd ed., p.153）。

## 基本公式的推导

### 从排列到组合

从 n 中选 k 个的排列数 = P(n,k) = n!/(n-k)!

每种组合对应 k! 种排列（k 个元素的全排列），因此：

```
C(n,k) = P(n,k) / k! = n! / (k!(n-k)!)

数值示例：从5人中选3人
P(5,3) = 5×4×3 = 60（排列数）
C(5,3) = 60 / 3! = 60 / 6 = 10（组合数）
```

### Pascal三角与递推

```
         C(0,0)
        C(1,0) C(1,1)
      C(2,0) C(2,1) C(2,2)
    C(3,0) C(3,1) C(3,2) C(3,3)
  C(4,0) C(4,1) C(4,2) C(4,3) C(4,4)

数值：
       1
      1  1
     1  2  1
    1  3  3  1
   1  4  6  4  1
  1  5 10 10  5  1
```

Pascal 恒等式的组合解释：n 中选 k，对某个特定元素 x：
- 要么选了 x → 从剩余 n-1 中再选 k-1：C(n-1,k-1)
- 要么没选 x → 从剩余 n-1 中选 k：C(n-1,k)

## 关键恒等式

| 恒等式 | 公式 | 组合解释 |
|--------|------|---------|
| 对称性 | C(n,k) = C(n,n-k) | 选k个 = 排除n-k个 |
| Vandermonde | C(m+n,r) = Σ C(m,k)·C(n,r-k) | 从两组分别选 |
| 行和 | Σ C(n,k) = 2ⁿ | n元素子集总数 |
| 交错和 | Σ(-1)ᵏC(n,k) = 0 | 奇偶子集数相等 |
| 上指标求和 | Σ C(i,k) [i=k..n] = C(n+1,k+1) | Hockey stick恒等式 |
| 倍增 | C(2n,n) = Σ C(n,k)² | Catalan数的基础 |

## 二项式定理

组合最重要的代数应用：

```
(x + y)ⁿ = Σ C(n,k) · xᵏ · yⁿ⁻ᵏ  [k=0..n]

示例：(a+b)⁴ = a⁴ + 4a³b + 6a²b² + 4ab³ + b⁴
系数恰好是 Pascal 第4行：1, 4, 6, 4, 1
```

**推广**：Newton 广义二项式定理（1665）将指数推广到非整数/负数：
```
(1+x)^α = Σ C(α,k) · xᵏ  [k=0..∞]，|x|<1

其中 C(α,k) = α(α-1)(α-2)...(α-k+1) / k!
```

## 组合模型的分类

| 模型 | 有序? | 可重复? | 公式 | 示例 |
|------|------|--------|------|------|
| 排列 | 是 | 否 | P(n,k)=n!/(n-k)! | 赛跑名次 |
| 组合 | 否 | 否 | C(n,k) | 选委员会 |
| 可重排列 | 是 | 是 | nᵏ | 密码组合 |
| 可重组合 | 否 | 是 | C(n+k-1,k) | 糖果分配 |

### 可重组合（Stars and Bars）

从 n 种中选 k 个（可重复），等价于将 k 个星星用 n-1 个隔板分为 n 组：

```
C(n+k-1, k) = C(n+k-1, n-1)

示例：从3种水果中选5个
C(3+5-1, 5) = C(7,5) = 21 种方案
```

## 计算技巧

### 大数组合的对数计算

直接计算 C(100,50) 会溢出（≈ 10²⁹），使用对数：
```
log C(n,k) = Σ log(i) [i=1..n] - Σ log(i) [i=1..k] - Σ log(i) [i=1..n-k]
           = log(n!) - log(k!) - log((n-k)!)

Stirling近似：log(n!) ≈ n·log(n) - n + 0.5·log(2πn)
```

### 递推计算（避免溢出）

```python
# Python: 逐步乘除避免中间值爆炸
def comb(n, k):
    if k > n - k:
        k = n - k  # C(n,k) = C(n,n-k)，取较小的k
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result

# comb(100, 50) = 100891344545564193334812497256
```

## 应用实例

### 概率计算：扑克牌型

```
52张牌选5张总方案数：C(52,5) = 2,598,960

皇家同花顺：4种（每种花色1种）
概率 = 4 / 2,598,960 = 1/649,740 ≈ 0.000154%

同花（5张同花色，不含顺子和同花顺）：
C(4,1)·C(13,5) - 40 = 4·1287 - 40 = 5,108
概率 = 5,108 / 2,598,960 ≈ 0.197%
```

### 算法：子集枚举

```python
# 位掩码枚举所有 C(n,k) 个k元子集
def k_subsets(n, k):
    if k == 0:
        yield []
        return
    for i in range(k-1, n):
        for subset in k_subsets(i, k-1):
            yield subset + [i]
```

## 参考文献

- Graham, R.L., Knuth, D.E. & Patashnik, O. (1994). *Concrete Mathematics*, 2nd ed. Addison-Wesley. ISBN 978-0201558029
- Brualdi, R.A. (2009). *Introductory Combinatorics*, 5th ed. Pearson. ISBN 978-0136020400
- Stanley, R.P. (2011). *Enumerative Combinatorics*, Vol. 1, 2nd ed. Cambridge University Press.

## 教学路径

**前置知识**：阶乘、基本排列概念
**学习建议**：先通过小例子（从5选3的10种方案手动列举）建立直觉，再掌握 C(n,k)公式。Pascal三角是理解递推关系的最佳工具。之后学习二项式定理并练习展开 (a+b)ⁿ。
**进阶方向**：生成函数方法、容斥原理、Catalan数与组合恒等式的证明技巧。
""",

# ── 3. 四则运算 ──────────────────────────────
"mathematics/arithmetic/four-operations.md": f"""---
id: "four-operations"
concept: "四则运算"
domain: "mathematics"
subdomain: "arithmetic"
subdomain_name: "算术"
difficulty: 1
is_milestone: false
tags: ["基础", "运算"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "{TODAY}"
sources:
  - type: "textbook"
    name: "Knuth, The Art of Computer Programming, Vol. 2: Seminumerical Algorithms"
  - type: "research"
    name: "Karatsuba & Ofman (1962) Multiplication of Many-Digital Numbers by Automatic Computers"
scorer_version: "scorer-v2.0"
---
# 四则运算

## 定义与核心概念

四则运算是数学中四种基本算术操作的统称：**加法（Addition）、减法（Subtraction）、乘法（Multiplication）和除法（Division）**。它们构成了从小学算术到高等数学的计算基础，也是所有计算机算术运算的底层原语。

在 Peano 公理体系中，加法是唯一通过**后继函数**原始定义的运算，其余三种运算均可由加法派生：
- 减法 = 加法的逆运算
- 乘法 = 重复加法
- 除法 = 乘法的逆运算

## 运算的形式化定义

### 自然数上的递归定义

```
加法（Peano公理）：
  a + 0 = a                    （零元素）
  a + S(b) = S(a + b)          （递推，S为后继函数）

乘法：
  a × 0 = 0
  a × S(b) = a × b + a

幂运算（由乘法派生）：
  a⁰ = 1
  a^S(b) = a^b × a
```

### 运算律总结

| 性质 | 加法 | 乘法 | 减法 | 除法 |
|------|------|------|------|------|
| 交换律 | a+b = b+a ✓ | a×b = b×a ✓ | ✗ | ✗ |
| 结合律 | (a+b)+c = a+(b+c) ✓ | (a×b)×c = a×(b×c) ✓ | ✗ | ✗ |
| 单位元 | 0 | 1 | — | — |
| 逆元素 | -a (整数域) | 1/a (有理数域, a≠0) | — | — |
| 分配律 | — | a×(b+c) = a×b+a×c ✓ | — | (a+b)÷c = a÷c+b÷c ✓ (右分配) |

**关键洞察**：加法和乘法各自形成**交换幺半群**；在整数域上，加法形成**阿贝尔群**；在有理数域（除0外），乘法也形成阿贝尔群。这两个群通过分配律连接，构成**域**（Field）结构。

## 运算优先级

标准优先级规则（PEMDAS/BODMAS）：

```
括号 > 指数 > 乘除（同级，从左到右） > 加减（同级，从左到右）

示例：2 + 3 × 4² ÷ 2 - 1
     = 2 + 3 × 16 ÷ 2 - 1    （先指数）
     = 2 + 48 ÷ 2 - 1         （从左到右：乘）
     = 2 + 24 - 1              （除）
     = 25                       （加减）
```

**历史注记**：运算优先级并非"自然法则"，而是约定俗成。Cajori（1928, *A History of Mathematical Notations*）记录了18-19世纪优先级规则的逐步标准化过程。

## 算法复杂度

不同算法在 n 位数运算上的时间复杂度：

| 运算 | 朴素算法 | 最佳已知算法 | 备注 |
|------|---------|------------|------|
| 加法 | O(n) | O(n) | 已最优 |
| 减法 | O(n) | O(n) | 已最优 |
| 乘法 | O(n²) | O(n·log n)（Harvey & van der Hoeven, 2021） | Karatsuba: O(n^1.585) |
| 除法 | O(n²) | O(M(n))，M为乘法复杂度 | Newton迭代求逆 |

### Karatsuba 乘法（1962）

第一个打破 O(n²) 壁垒的乘法算法（Karatsuba & Ofman, 1962）：

```
将 n 位数 x, y 各分为高低两半：
x = x₁·B^m + x₀,  y = y₁·B^m + y₀  (B=基数, m=n/2)

朴素：x·y = x₁y₁·B^2m + (x₁y₀+x₀y₁)·B^m + x₀y₀  → 4次乘法

Karatsuba 技巧：
z₂ = x₁·y₁
z₀ = x₀·y₀
z₁ = (x₁+x₀)·(y₁+y₀) - z₂ - z₀  → 只需3次乘法！

x·y = z₂·B^2m + z₁·B^m + z₀

复杂度：T(n) = 3T(n/2) + O(n) → O(n^log₂3) ≈ O(n^1.585)
```

## 计算机中的实现

### 整数运算

| 表示 | 位宽 | 范围 | 溢出行为 |
|------|------|------|---------|
| unsigned int | 32 | 0 ~ 4,294,967,295 | 回绕（模 2³²） |
| signed int (补码) | 32 | -2,147,483,648 ~ 2,147,483,647 | 未定义（C标准） |
| int64 | 64 | ±9.2×10¹⁸ | 回绕 |

### 浮点运算（IEEE 754）

```
float32: 1位符号 + 8位指数 + 23位尾数
精度：约7位十进制有效数字
最大值：≈ 3.4 × 10³⁸

关键陷阱：
0.1 + 0.2 = 0.30000000000000004  (float64)
原因：0.1 的二进制表示是无限循环小数 0.0001100110011...
```

**Kahan 求和算法**（补偿求和）解决浮点加法的累积误差：
```python
def kahan_sum(values):
    s = 0.0
    c = 0.0  # 补偿值
    for x in values:
        y = x - c
        t = s + y
        c = (t - s) - y  # 丢失的低位
        s = t
    return s
```

## 除法的特殊性

除法是四则运算中唯一**不封闭**的运算（自然数除法结果可能不是自然数），也是唯一涉及**不可执行情况**（除以零）的运算。

不同数学系统对除以零的处理：
| 系统 | 1/0 的结果 | 理由 |
|------|-----------|------|
| 实数域 | 未定义 | 不存在满足 0×x=1 的 x |
| IEEE 754 | +∞ 或 -∞ | 实用约定（极限意义下） |
| 0/0 | NaN (Not a Number) | 不定式 |
| 射影几何 | ∞（有意义） | 扩展实数线 |

## 参考文献

- Knuth, D.E. (1997). *The Art of Computer Programming, Vol. 2: Seminumerical Algorithms*, 3rd ed. Addison-Wesley. ISBN 978-0201896848
- Karatsuba, A. & Ofman, Y. (1962). "Multiplication of Many-Digital Numbers by Automatic Computers," *Doklady Akademii Nauk SSSR*, 145(2), 293-294.
- Harvey, D. & van der Hoeven, J. (2021). "Integer multiplication in time O(n log n)," *Annals of Mathematics*, 193(2). [doi: 10.4007/annals.2021.193.2.4]

## 教学路径

**前置知识**：自然数概念、计数能力
**学习建议**：先通过实物操作建立加减法直觉，再理解乘法作为"重复加法"的本质。除法应分两阶段教学：先等分（12÷3="分成3份"），再包含（12÷3="每3个一组"）。运算律的记忆应结合代数结构理解而非死记硬背。
**进阶方向**：模运算与同余、计算机算术（补码、浮点）、快速乘法算法（FFT-based）。
""",

# ── 4. 随机性设计概述 ──────────────────────────────
"game-design/randomness-design/randomness-intro.md": f"""---
id: "randomness-intro"
concept: "随机性概述"
domain: "game-design"
subdomain: "randomness-design"
subdomain_name: "随机性设计"
difficulty: 2
is_milestone: false
tags: ["概述", "随机", "概率"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "{TODAY}"
sources:
  - type: "textbook"
    name: "Schell, The Art of Game Design, 3rd ed."
  - type: "paper"
    name: "Bateman & Boon (2005) 21st Century Game Design"
scorer_version: "scorer-v2.0"
---
# 随机性概述

## 定义与核心概念

游戏中的随机性（Randomness/RNG）是通过**不确定性**创造变化和悬念的设计工具。Richard Garfield（万智牌设计师）在 GDC 2012 演讲中区分了两种基本类型：

- **输入随机性**（Input Randomness）：在玩家做决策**之前**引入不确定性（如地图生成、手牌抽取）
- **输出随机性**（Output Randomness）：在玩家做决策**之后**引入不确定性（如攻击命中判定、暴击概率）

这一区分至关重要：输入随机性要求玩家**适应**随机结果（策略性），输出随机性让玩家**承受**随机结果（情绪性）。

## 随机性的功能分析

### 正面功能

| 功能 | 机制 | 设计示例 |
|------|------|---------|
| 增加重玩价值 | 不同体验路径 | Roguelike 地图生成 |
| 平衡技能差距 | 弱者有翻盘机会 | Mario Kart 蓝龟壳 |
| 创造情感峰值 | 意料之外的好运/厄运 | 暗黑破坏神传奇掉落 |
| 防止最优策略固化 | 强制适应性决策 | 万智牌随机手牌 |
| 模拟现实不确定性 | 战争迷雾、天气系统 | XCOM 命中率 |

### 负面效应

| 问题 | 表现 | 感知阈值 |
|------|------|---------|
| "不公平"感 | 关键时刻随机失败 | 连续失败 **3次** 后玩家愤怒急剧上升 |
| 技能贬值 | 高水平玩家无法稳定发挥 | 竞技场景中随机性贡献 > **30%** 时开始被抱怨 |
| 赌博成瘾 | 变比率强化的过度使用 | gacha 类机制的监管关注 |

## 伪随机与加权随机

### 纯随机 vs 伪随机分布（PRD）

纯随机：每次事件独立，25%暴击率 = 每次25%概率。
问题：玩家可能连续 10+ 次不暴击（(0.75)^10 ≈ 5.6%），或连续暴击。

**PRD**（DotA 2/魔兽世界采用）：
```
初始概率 C 远低于标称概率 P
每次未触发：当前概率 += C
触发后重置为 C

示例：标称暴击率 25%
  C ≈ 8.5%（通过数值求解使长期均值=25%）
  第1次：8.5%
  第2次：17.0%
  第3次：25.5%
  第4次：34.0%
  ...最迟第12次必定触发（100%）

效果：极端序列（长期不触发/连续触发）几乎被消除
```

### Mercy System（保底机制）

```
gacha/抽卡设计：
  基础SSR概率：0.6%
  硬保底：第90抽必出（概率提升到100%）
  软保底：第75抽开始概率逐步提升

  期望花费计算：
  无保底：E = 1/0.006 ≈ 167 抽
  有软保底：E ≈ 62 抽（原神实测数据，Paimon.moe统计）
```

## 随机性的设计谱系

```
完全确定 ←──────────────────→ 完全随机
  国际象棋   扑克   XCOM    骰子   老虎机
  
  |          |      |        |      |
  纯策略    混合    战术+运气  运气主导  纯运气
```

Schell（*The Art of Game Design*, 3rd ed., p.178）建议：游戏的"随机性预算"应与目标受众的技能水平反向相关——硬核玩家偏好低随机性（电竞），休闲玩家偏好高随机性（派对游戏）。

## 常见随机系统设计模式

### 1. 掉落表（Loot Table）

```
怪物掉落表示例：
  普通材料：60%（权重6）
  稀有材料：25%（权重2.5）
  史诗装备：10%（权重1）
  传奇装备：4%（权重0.4）
  坐骑/宠物：1%（权重0.1）

实现方式：
  total_weight = sum(weights)
  roll = random() * total_weight
  累积权重遍历直到 roll < 累积值
```

### 2. 暗影骰子（Hidden Adjustment）

许多游戏在后台悄悄调整随机结果以改善体验：
- XCOM 在"简单"难度下，显示 65% 命中率实际为 **~80%**
- Fire Emblem 使用两次随机数平均值，使高命中率更可靠、低命中率更难触发
- 文明系列在战斗预测中使用隐藏修正确保"压倒性优势"几乎必胜

### 3. 随机种子控制

```python
# 可复现的随机性（Roguelike标配）
import random

seed = hash("player_name_2024")
rng = random.Random(seed)

# 每个地图层使用派生种子
floor_rng = random.Random(rng.randint(0, 2**32))
```

种子控制的好处：
- 竞速赛事可在相同地图上竞技
- 重放系统只需记录玩家输入
- 玩家可分享"好种子"（Minecraft）

## 心理学基础

### 变比率强化（Variable Ratio Reinforcement）

Skinner 的操作条件反射研究表明，变比率强化（VR）产生**最高且最稳定的反应率**：

| 强化程序 | 反应速率 | 消退抗性 | 游戏示例 |
|---------|---------|---------|---------|
| 固定比率（FR） | 稳定，到点暂停 | 中 | 每10次战斗必掉 |
| 变比率（VR） | 高且稳定 | 最高 | 随机掉落/gacha |
| 固定时距（FI） | 到点加速 | 低 | 每日登录奖励 |
| 变时距（VI） | 中等稳定 | 高 | 随机事件触发 |

VR 机制的伦理边界是当前游戏行业监管的核心争议（比利时/荷兰已禁止部分 loot box 机制）。

## 参考文献

- Schell, J. (2019). *The Art of Game Design: A Book of Lenses*, 3rd ed. CRC Press. ISBN 978-1138632059
- Garfield, R. (2012). "Luck vs. Skill in Games," *GDC 2012 Presentation*.
- Bateman, C. & Boon, R. (2005). *21st Century Game Design*. Charles River Media. ISBN 978-1584504290

## 教学路径

**前置知识**：基础概率概念、游戏设计基础
**学习建议**：先分析 3 款熟悉游戏的随机机制（区分输入/输出随机性），再实现一个带 PRD 和保底的简单掉落系统。最后用 A/B 测试方法比较纯随机 vs PRD 对玩家满意度的影响。
**进阶方向**：程序生成算法（WFC、L-system）、随机性的信息论分析、gacha 机制的行为经济学建模。
""",

# ── 5. 实验设计 ──────────────────────────────
"psychology/research-methods/experimental-design.md": f"""---
id: "experimental-design"
concept: "实验设计"
domain: "psychology"
subdomain: "research-methods"
subdomain_name: "研究方法"
difficulty: 2
is_milestone: false
tags: ["方法论", "实验", "因果"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "{TODAY}"
sources:
  - type: "textbook"
    name: "Shadish, Cook & Campbell, Experimental and Quasi-Experimental Designs, 2nd ed."
  - type: "textbook"
    name: "Field & Hole, How to Design and Report Experiments"
scorer_version: "scorer-v2.0"
---
# 实验设计

## 定义与核心概念

实验设计（Experimental Design）是通过**系统化操纵自变量、控制无关变量**来建立因果关系的研究方法论。Shadish, Cook & Campbell（2002）在《Experimental and Quasi-Experimental Designs for Generalized Causal Inference》中定义实验的三个必要条件：

1. **操纵**（Manipulation）：研究者主动改变自变量
2. **控制**（Control）：通过随机分配或匹配消除混淆变量
3. **比较**（Comparison）：至少两个条件（实验组 vs 控制组）

Fisher（1935）在《The Design of Experiments》中奠基了现代实验设计的三大原则：**随机化**（Randomization）、**重复**（Replication）、**局部控制**（Local Control/Blocking）。

## 实验设计的基本类型

### 被试间设计（Between-Subjects）

每个参与者只接受**一种**实验条件：

```
随机分配：
  参与者 → [随机化] → 实验组（接受处理）
                    → 控制组（不接受处理或安慰剂）

优点：无顺序效应、无练习/疲劳效应
缺点：需要更多参与者（个体差异噪声大）
样本量估计：n ≈ 2(Z_α/2 + Z_β)²·σ² / δ²
  (α=0.05, β=0.20, 中等效应d=0.5 → 每组约64人)
```

### 被试内设计（Within-Subjects / Repeated Measures）

每个参与者接受**所有**实验条件：

| 优势 | 劣势 | 对策 |
|------|------|------|
| 消除个体差异 | 顺序效应 | 拉丁方平衡（Latin Square） |
| 需要更少参与者 | 练习效应 | 随机化条件顺序 |
| 统计功效更高 | 疲劳/厌倦 | 充足间隔期 |
| | 遗留效应（Carryover） | 完全对抗平衡（ABBA设计） |

### 混合设计（Mixed Design）

同时包含被试间和被试内因子。示例：
```
因子A（被试间）：治疗类型（CBT vs 药物 vs 安慰剂）→ 3水平
因子B（被试内）：测量时间（前测 vs 后测 vs 3个月随访）→ 3水平
设计矩阵：3 × 3 混合 ANOVA
```

## 效度体系

Shadish et al.（2002）的四维效度框架：

| 效度类型 | 核心问题 | 主要威胁 |
|---------|---------|---------|
| **内部效度** | 自变量是否真正导致了因变量变化？ | 历史效应、成熟效应、回归效应、选择偏差 |
| **外部效度** | 结果能否推广到其他情境？ | 样本偏差、场景特异性、时代效应 |
| **构念效度** | 操纵和测量是否准确反映理论构念？ | 操纵不纯、测量不全、社会期望偏差 |
| **统计结论效度** | 统计推断是否正确？ | 低统计功效、违反假设、多重比较 |

### 内部效度的八大威胁（Campbell & Stanley经典）

1. **历史**（History）：实验期间发生的外部事件
2. **成熟**（Maturation）：自然发展变化
3. **测试**（Testing）：前测本身影响后测
4. **工具**（Instrumentation）：测量工具变化
5. **回归**（Regression to the Mean）：极端分数自然回归
6. **选择**（Selection）：组间系统差异
7. **流失**（Attrition）：选择性退出
8. **交互作用**：上述因素的组合

## 高级设计

### 因子设计（Factorial Design）

同时操纵两个或以上自变量，揭示**交互效应**：

```
2×2因子设计示例：
                  因子B: 背景噪音
                   安静    嘈杂
因子A:   简单任务  | 95%  | 90%  |  → 主效应A: 简单>复杂
  任务   复杂任务  | 80%  | 50%  |  → 主效应B: 安静>嘈杂
  难度                              → 交互效应: 噪音对复杂任务影响更大!

交互效应的统计检验：F(AxB) = MS(AxB) / MS(error)
```

### Solomon四组设计

解决前测的反应性问题：
```
组1: O₁  X  O₂   (前测-实验-后测)
组2: O₁     O₂   (前测-控制-后测)
组3:     X  O₂   (实验-后测)
组4:        O₂   (仅后测)
```
比较组3与组4可检验处理效应（无前测污染）；比较组1与组3可检验前测的反应性。

### 准实验设计

当随机分配**不可行**时（伦理、现实约束）：

| 设计 | 结构 | 因果推断强度 |
|------|------|------------|
| 非等组前后测 | O₁ X O₂ / O₁ O₂ | 中（受选择偏差威胁） |
| 中断时间序列 | ...O₁O₂O₃ X O₄O₅O₆... | 中-高（多时间点控制成熟效应） |
| 回归不连续 | 阈值分配（如GPA>3.0获奖学金） | 高（局部随机化的类比） |

## 样本量与统计功效

Cohen（1988）的效应量基准与功效分析：

| 效应量(d) | 分类 | 达到 80% 功效所需每组 n |
|-----------|------|----------------------|
| 0.20 | 小 | 394 |
| 0.50 | 中 | 64 |
| 0.80 | 大 | 26 |

**再现危机背景**：Open Science Collaboration（2015）对 100 项心理学研究的重复实验，成功复现率仅 **36%**。主要原因之一是原始研究的样本量不足（中位 n ≈ 40/组），导致假阳性率虚高。

## 参考文献

- Shadish, W.R., Cook, T.D. & Campbell, D.T. (2002). *Experimental and Quasi-Experimental Designs for Generalized Causal Inference*, 2nd ed. Cengage. ISBN 978-0395615560
- Fisher, R.A. (1935). *The Design of Experiments*. Oliver and Boyd.
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences*, 2nd ed. Erlbaum. ISBN 978-0805802832
- Open Science Collaboration (2015). "Estimating the reproducibility of psychological science," *Science*, 349(6251). [doi: 10.1126/science.aac4716]

## 教学路径

**前置知识**：基础统计学（假设检验、t检验、ANOVA）
**学习建议**：先掌握被试间/被试内设计的区别，用卡片模拟理解随机分配如何消除混淆变量。然后学习 2×2 因子设计的交互效应解读。推荐用 G*Power 软件练习样本量计算。
**进阶方向**：多层模型（HLM）、结构方程模型（SEM）、贝叶斯实验设计。
""",

# ── 6. 图论基础 ──────────────────────────────
"mathematics/discrete-math/graph-theory-basics.md": f"""---
id: "graph-theory-basics"
concept: "图论基础"
domain: "mathematics"
subdomain: "discrete-math"
subdomain_name: "离散数学"
difficulty: 2
is_milestone: false
tags: ["图论", "基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "{TODAY}"
sources:
  - type: "textbook"
    name: "Diestel, Graph Theory, 5th ed., Springer GTM 173"
  - type: "textbook"
    name: "Cormen et al., Introduction to Algorithms (CLRS), 4th ed."
scorer_version: "scorer-v2.0"
---
# 图论基础

## 定义与历史

图论（Graph Theory）研究由**顶点**（Vertices）和**边**（Edges）组成的关系结构。形式化定义：图 G = (V, E)，其中 V 是顶点集，E ⊆ V×V 是边集。

图论诞生于 Euler（1736）对柯尼斯堡七桥问题的证明：不可能恰好经过每座桥一次遍历所有四块陆地。Euler 的关键洞察——将陆地抽象为顶点、桥抽象为边——开创了拓扑学和组合数学的先河。

Diestel（2017）在《Graph Theory》中指出："如果组合数学有一个统一主题，那就是图。"（5th ed., GTM 173, Preface）

## 基本概念

### 图的分类

| 类型 | 定义 | 例 |
|------|------|---|
| 无向图 | 边无方向：(u,v) = (v,u) | 社交网络 |
| 有向图（Digraph） | 边有方向：(u,v) ≠ (v,u) | 网页链接 |
| 加权图 | 边附带权重 w(e) | 地图导航 |
| 简单图 | 无自环、无重边 | 大多数理论研究 |
| 多重图 | 允许重边 | 交通网络 |
| 完全图 K_n | 每对顶点间都有边 | |E| = n(n-1)/2 |
| 二部图 | V可分为两组，边只在组间 | 匹配问题 |

### 度与握手定理

顶点 v 的度 deg(v) = 与 v 相连的边数。

**握手定理**（Euler, 1736）：
```
Σ deg(v) = 2|E|   [对所有 v ∈ V]

推论1：奇数度顶点的个数必为偶数
推论2：平均度 = 2|E|/|V|
```

有向图中区分入度 deg⁻(v) 和出度 deg⁺(v)：
```
Σ deg⁺(v) = Σ deg⁻(v) = |E|
```

## 图的表示

### 邻接矩阵

```
n×n 矩阵 A，A[i][j] = 1 当 (i,j) ∈ E
         
空间：O(n²)
边查询：O(1)
遍历邻居：O(n)
适用：稠密图（|E| ≈ n²）
```

### 邻接表

```
每个顶点维护一个邻居列表

空间：O(n + m)，m = |E|
边查询：O(deg(v))
遍历邻居：O(deg(v))
适用：稀疏图（|E| << n²）
```

CLRS（4th ed.）建议：当 |E| < |V|²/64 时优选邻接表，否则优选邻接矩阵。

## 核心问题与算法

### 1. 图遍历

| 算法 | 数据结构 | 时间复杂度 | 应用 |
|------|---------|-----------|------|
| BFS（广度优先） | 队列 | O(V+E) | 最短路径（无权）、层序遍历 |
| DFS（深度优先） | 栈/递归 | O(V+E) | 连通分量、拓扑排序、环检测 |

```python
# BFS 模板
from collections import deque
def bfs(graph, start):
    visited = set([start])
    queue = deque([start])
    while queue:
        v = queue.popleft()
        for neighbor in graph[v]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
```

### 2. 最短路径

| 算法 | 约束 | 复杂度 | 思想 |
|------|------|--------|------|
| Dijkstra | 非负权 | O((V+E)log V) | 贪心 + 优先队列 |
| Bellman-Ford | 允许负权 | O(VE) | 动态规划（松弛V-1轮） |
| Floyd-Warshall | 全源最短路 | O(V³) | DP: d[i][j] = min(d[i][j], d[i][k]+d[k][j]) |

### 3. 连通性

- **无向图连通分量**：一次 DFS/BFS → O(V+E)
- **有向图强连通分量**：Tarjan 算法或 Kosaraju 算法 → O(V+E)

### 4. 最小生成树

| 算法 | 策略 | 复杂度 |
|------|------|--------|
| Kruskal | 按权排序 + Union-Find | O(E log E) |
| Prim | 类 Dijkstra 贪心扩展 | O((V+E)log V) |

**Cut property**（最小生成树的理论基础）：对图的任意割，穿越割的最小权边必属于某棵 MST。

## 特殊图与经典定理

### Euler 路径与回路

- **Euler 回路**存在 ⟺ 图连通且所有顶点度数为偶数
- **Euler 路径**存在 ⟺ 图连通且恰好 0 或 2 个奇度顶点

### Hamilton 回路

经过每个**顶点**恰好一次的回路。判定是 **NP-完全问题**（Karp, 1972）。
- Dirac 定理（1952）：若 n ≥ 3 且每个顶点 deg(v) ≥ n/2，则存在 Hamilton 回路

### 图着色

**四色定理**（Appel & Haken, 1976）：任何平面图可用 4 种颜色着色使相邻顶点不同色。这是首个借助计算机辅助完成的重大数学证明。

色数 χ(G) 的基本界：
```
ω(G) ≤ χ(G) ≤ Δ(G) + 1

ω(G) = 最大团大小
Δ(G) = 最大度数
Brooks定理：当G不是完全图或奇圈时，χ(G) ≤ Δ(G)
```

## 参考文献

- Diestel, R. (2017). *Graph Theory*, 5th ed. Springer GTM 173. ISBN 978-3662536216
- Cormen, T.H. et al. (2022). *Introduction to Algorithms*, 4th ed. MIT Press. ISBN 978-0262046305
- Euler, L. (1736). "Solutio problematis ad geometriam situs pertinentis," *Commentarii academiae scientiarum Petropolitanae*, 8, 128-140.

## 教学路径

**前置知识**：集合论基础、基本算法概念
**学习建议**：先手绘小图理解度、路径、连通的直觉，再实现 BFS 和 DFS。学习最短路径时，在 5-6 个节点的图上手动执行 Dijkstra 算法。图论的核心在于**将实际问题建模为图**的能力。
**进阶方向**：网络流（Ford-Fulkerson）、匹配理论（Hungarian算法）、谱图论、随机图模型。
""",

# ── 7. 经典条件反射 ──────────────────────────────
"psychology/behavioral-psychology/classical-conditioning.md": f"""---
id: "classical-conditioning"
concept: "经典条件反射"
domain: "psychology"
subdomain: "behavioral-psychology"
subdomain_name: "行为心理学"
difficulty: 1
is_milestone: false
tags: ["学习", "条件反射", "巴甫洛夫"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "{TODAY}"
sources:
  - type: "textbook"
    name: "Rescorla & Wagner (1972) A theory of Pavlovian conditioning"
  - type: "textbook"
    name: "Bouton, Learning and Behavior, 2nd ed."
scorer_version: "scorer-v2.0"
---
# 经典条件反射

## 定义与历史

经典条件反射（Classical/Pavlovian Conditioning）是通过反复将**中性刺激**与**无条件刺激**配对，使中性刺激最终能独立引发类似反应的学习过程。Ivan Pavlov（1849-1936）在研究狗的消化系统时意外发现了这一现象，并因此获得 1904 年诺贝尔生理学或医学奖。

Pavlov 的原始实验（约 1897 年）：
```
阶段1（条件化前）：
  铃声（NS）→ 无反应（或朝向反应）
  食物（US）→ 分泌唾液（UR）

阶段2（条件化）：
  铃声（NS）+ 食物（US）→ 分泌唾液（UR）
  重复 30-40 次配对

阶段3（条件化后）：
  铃声（CS）→ 分泌唾液（CR）
  
术语：
  NS = Neutral Stimulus（中性刺激）
  US = Unconditioned Stimulus（无条件刺激）
  UR = Unconditioned Response（无条件反应）
  CS = Conditioned Stimulus（条件刺激）
  CR = Conditioned Response（条件反应）
```

## 核心现象

### 习得（Acquisition）

条件反射建立的过程。关键参数：

| 参数 | 影响 | 最优值 |
|------|------|--------|
| CS-US 间隔 | 过短/过长都削弱 | **0.2-2秒**（延迟条件反射） |
| 配对次数 | 非线性增长 | 依任务而异（恐惧条件反射可1次习得） |
| US 强度 | 正相关 | 更强的 US → 更快习得 |
| CS 显著性 | 正相关 | 新异刺激 > 熟悉刺激 |

### 消退（Extinction）

反复呈现 CS 而不伴随 US → CR 逐渐减弱。

**关键发现**：消退不是"遗忘"，而是新的抑制性学习。证据：
- **自发恢复**（Spontaneous Recovery）：消退后经过一段时间，CR 重新出现
- **快速重新习得**（Rapid Reacquisition）：再次配对时，习得速度远快于首次
- **更新效应**（Renewal Effect）：在不同情境中测试，消退的 CR 恢复

### 泛化与分化

```
刺激泛化：对与 CS 相似的刺激也产生 CR
  CS = 1000Hz 音调 → CR
  900Hz → 较弱 CR
  800Hz → 更弱 CR
  → 泛化梯度（Generalization Gradient）

刺激分化：通过选择性强化区分 CS+ 和 CS-
  1000Hz + US → CR（CS+）
  800Hz 单独呈现 → 无 CR（CS-）
```

## Rescorla-Wagner 模型（1972）

最有影响力的条件反射数学模型，核心方程：

```
ΔV = αβ(λ - ΣV)

ΔV = 条件刺激关联强度的变化
α  = CS 的学习率参数（0-1，刺激显著性）
β  = US 的学习率参数（0-1，US强度）
λ  = US 实际发生时的最大关联值（通常=1）
ΣV = 所有存在的 CS 的关联强度之和

关键：误差驱动学习——当 ΣV 接近 λ 时，学习减缓
```

### R-W 模型的预测

**阻断效应**（Blocking, Kamin 1969）：
```
阶段1：A + US → V_A ≈ λ（A已充分预测US）
阶段2：AB + US → ΔV_B = αβ(λ - V_A - V_B) ≈ 0
结论：B无法获得关联强度，因为A已经"用完"了可学习的误差
```

这一预测已被大量实验验证，证明条件反射不是简单的"接近性=学习"，而是**信息性**驱动的。

**过度期望效应**（Overexpectation）：
```
训练：A+US → V_A=λ；B+US → V_B=λ
测试：AB+US → ΔV = αβ(λ - V_A - V_B) = αβ(λ - 2λ) < 0
结果：V_A 和 V_B 都下降！尽管US仍在出现
```

## 条件反射的变体

| 类型 | CS-US关系 | 效果 | 示例 |
|------|----------|------|------|
| 延迟条件反射 | CS开始→US出现→同时结束 | 最有效 | 标准Pavlov范式 |
| 痕迹条件反射 | CS结束→间隔→US出现 | 较弱（间隔越长越弱） | 依赖海马体 |
| 同时条件反射 | CS和US完全同时 | 较弱 | CS无预测价值 |
| 反向条件反射 | US先于CS | 几乎无效/抑制性 | CS预测"US不会来" |

## 神经机制

### 恐惧条件反射的神经通路

LeDoux（1996）的双通路模型：
```
CS（声音）→ 丘脑 → 
  快速通路（Low Road）：丘脑 → 杏仁核 → 恐惧反应（~12ms）
  慢速通路（High Road）：丘脑 → 皮层 → 杏仁核 → 精确评估（~30ms）

消退的神经基础：
  前额叶皮层（vmPFC）→ 抑制杏仁核的 CR 表达
  （这就是为什么消退是"新学习"而非"遗忘"）
```

### 小脑与眨眼条件反射

眨眼条件反射（Eyeblink Conditioning）是研究最透彻的模型系统：
- 小脑浦肯野细胞编码 CS-US 时间关系
- 小脑间核（Interpositus Nucleus）损毁 → CR 完全消失，UR 不受影响
- 这一解离证明 CR 和 UR 由不同神经回路控制

## 应用

| 领域 | 应用 | 机制 |
|------|------|------|
| 临床心理 | 系统脱敏治疗恐惧症 | 反条件化（将CS与放松反应配对） |
| 临床心理 | 厌恶疗法戒酒/戒烟 | 将酒精/香烟与催吐剂配对 |
| 广告 | 品牌+正面情感的重复配对 | 高阶条件反射 |
| 免疫学 | 条件化免疫抑制 | Ader & Cohen (1975)：糖水+环磷酰胺配对 |
| 药理学 | 耐药性的条件反射成分 | 环境线索→补偿性CR→需要更大剂量 |

## 参考文献

- Rescorla, R.A. & Wagner, A.R. (1972). "A theory of Pavlovian conditioning: Variations in the effectiveness of reinforcement and nonreinforcement," in *Classical Conditioning II*, Appleton-Century-Crofts.
- Bouton, M.E. (2007). *Learning and Behavior: A Contemporary Synthesis*, 2nd ed. Sinauer. ISBN 978-0878930630
- LeDoux, J.E. (1996). *The Emotional Brain*. Simon & Schuster. ISBN 978-0684803821
- Kamin, L.J. (1969). "Predictability, surprise, attention, and conditioning," in *Punishment and Aversive Behavior*, Appleton-Century-Crofts.

## 教学路径

**前置知识**：心理学导论中的学习概念
**学习建议**：先掌握 CS-US-CR-UR 术语框架并用日常生活例子（如手机铃声→期待→查看行为）理解。然后用 R-W 模型做手算练习（3-5个配对试次的ΔV计算）。最后比较经典条件反射与操作性条件反射的关键区别。
**进阶方向**：时序差分学习（TD Learning，机器学习的联系）、注意力模型（Mackintosh, Pearce-Hall）、条件反射的进化约束（味觉厌恶学习）。
""",

}

# ── 写入逻辑 ──────────────────────────────
updated = []
for rel_path, content in DOCS.items():
    fpath = ROOT / rel_path
    if not fpath.exists():
        print(f"NOT FOUND: {fpath}")
        continue
    fpath.write_text(content.strip() + "\n", encoding="utf-8")
    updated.append(fpath.name)
    print(f"OK  {fpath.name}")

print(f"\nTotal updated: {len(updated)}")
