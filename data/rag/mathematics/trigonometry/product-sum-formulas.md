---
id: "product-sum-formulas"
concept: "积化和差公式"
domain: "mathematics"
subdomain: "trigonometry"
subdomain_name: "三角学"
difficulty: 6
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 积化和差公式

## 概述

积化和差公式是三角学中将两个三角函数的乘积转化为三角函数之和或差的一组恒等式。其核心价值在于：三角函数的乘积形式在积分、化简和求极限时往往难以直接处理，而通过积化和差，可将"积"转化为"和差"，使计算大幅简化。例如，∫sinA·cosB dx 在不展开的情况下无法直接积分，而展开后立刻变为两个标准正弦函数的积分。

积化和差公式并非凭空创造，而是直接由和差化积公式（或更准确地说，由两角和差公式）逆向推导而来。其历史根源可追溯至16世纪欧洲天文学家的计算需求——约翰内斯·开普勒时代的天文学家用"prosthaphaeresis"（积化和差法）替代繁琐的乘法运算，在对数发明之前，这是天文计算中处理大数相乘的主要工具。

这组公式共有四个，覆盖了正弦与余弦的所有两两组合（sinsin、coscos、sincos、cossin），是三角恒等变换工具箱中结构最紧凑、应用最直接的一组。

## 核心原理

### 四个公式的推导与表达

积化和差的四个公式如下：

1. **sin A · cos B** = ½[sin(A+B) + sin(A−B)]
2. **cos A · sin B** = ½[sin(A+B) − sin(A−B)]
3. **cos A · cos B** = ½[cos(A+B) + cos(A−B)]
4. **sin A · sin B** = −½[cos(A+B) − cos(A−B)]

其中第4个公式的负号最容易被忽视，推导步骤如下：

由两角和差公式：
- cos(A+B) = cosA·cosB − sinA·sinB
- cos(A−B) = cosA·cosB + sinA·sinB

两式相减得：cos(A−B) − cos(A+B) = 2sinA·sinB

因此 **sinA·sinB = ½[cos(A−B) − cos(A+B)]**，即等于 −½[cos(A+B) − cos(A−B)]。

### 符号规律与记忆方法

四个公式的系数统一为 **½**，这是所有积化和差公式的共同特征。区分"和"还是"差"有一个规律：

- 含 **sinA·cosB 或 cosA·sinB** 时，展开后为 **sin** 函数的和差；
- 含 **cosA·cosB** 时，展开后为 **cos** 函数的 **和加差**；
- 含 **sinA·sinB** 时，展开后为 **cos** 函数的 **差减和**（即小角余弦减大角余弦）。

记忆口诀：**"积化和差，半角变换；同名余弦，异名正弦；sin乘cos用正弦，cos乘cos用余弦加，sin乘sin用余弦减"**。

### 与和差化积公式的对称关系

积化和差与和差化积互为逆运算。以 sinC + sinD 为例，令 A+B=C、A−B=D，则 A=(C+D)/2、B=(C−D)/2，代入积化和差的第1式即得和差化积公式 sinC+sinD = 2sin[(C+D)/2]·cos[(C−D)/2]。这说明两组公式本质上是同一套恒等式的不同方向的运用，变量替换连接了两者。

## 实际应用

### 三角函数积分

计算 ∫sin3x·cos5x dx 时，直接积分无标准公式可用。利用积化和差第1式展开：

sin3x·cos5x = ½[sin(3x+5x) + sin(3x−5x)] = ½[sin8x + sin(−2x)] = ½[sin8x − sin2x]

则 ∫sin3x·cos5x dx = ½∫(sin8x − sin2x)dx = ½[−cos8x/8 + cos2x/2] + C = −cos8x/16 + cos2x/4 + C

若不使用积化和差，此题无法用初等方法直接求解。

### 乘积形式的化简与求值

已知 sin20°·sin40°·sin80°，可分步使用积化和差：

先计算 sin40°·sin80° = ½[cos(40°−80°) − cos(40°+80°)] = ½[cos40° − cos120°] = ½[cos40° + ½]

再乘以 sin20°，继续展开，最终结果为 **√3/8**，这是一个经典竞赛结论，需要连续两次使用 sinA·sinB 的积化和差公式才能得出。

### 物理中的拍频现象

两列频率相近的声波叠加时，物理上的"拍"可用积化和差解释：

cos(ω₁t) · cos(ω₂t) = ½[cos((ω₁+ω₂)t) + cos((ω₁−ω₂)t)]

其中 (ω₁−ω₂) 为低频拍频，(ω₁+ω₂) 为载频，积化和差公式直接对应了拍频的物理原理。

## 常见误区

**误区一：sin A·sin B 公式的符号写错**

很多学生将 sinA·sinB 写成 +½[cos(A+B) − cos(A−B)]，漏掉负号或颠倒减法方向。正确结果是 **½[cos(A−B) − cos(A+B)]**，即 **小角在前、大角在后**。检验方法：令 A=B=0，则左边 sin0·sin0=0，右边 ½[cos0−cos0]=0，符合；再令 A=B=π/2，左边=1，右边=½[cos0−cosπ]=½[1+1]=1，正确。

**误区二：混淆展开后是 sin 还是 cos**

规律是：**同名（sinsin 或 coscos）展开用 cos**，**异名（sincos）展开用 sin**。初学者有时将 cosA·cosB 误展开为 sin 函数之和，这与第1、2式的正弦结果相混淆。可通过特殊值验证：令 A=B=0，cosA·cosB=1，而 ½[cos0+cos0]=1，正确；若错误地套用 sin 公式得 ½[sin0+sin0]=0，明显错误。

**误区三：忘记系数 ½**

积化和差之后乘积变为和差，但系数 **必须是 ½**，不是 1。这来源于两角和差公式相加（或相减）时产生的系数 2，移项后得到 ½。遗漏 ½ 会导致计算结果偏差 2 倍，在积分题中尤为致命。

## 知识关联

**前置知识**：积化和差公式是由**两角和差公式**（sin(A±B)和cos(A±B)）直接加减推导而来，因此必须熟练掌握 sin(A+B)=sinAcosB+cosAsinB 等四个基本公式，才能真正理解积化和差的来源，而不是死记硬背。

**与和差化积的关系**：和差化积公式（如 sinC+sinD=2sin[(C+D)/2]cos[(C−D)/2]）是积化和差的逆变换，两者通过换元 C=A+B、D=A−B 精确对应。在解题中，两组公式经常配合使用：先积化和差降次，再和差化积合并同类项。

**后续应用方向**：积化和差是**三角函数定积分**（尤其是乘积型被积函数）、**傅里叶级数**（将乘积形式分解为频率分量）以及**数列求和**（含三角函数的乘积型通项）的基础工具，在高中竞赛和大学微积分课程中均有直接出现。
