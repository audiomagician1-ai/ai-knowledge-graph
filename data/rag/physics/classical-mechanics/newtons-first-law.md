---
id: "newtons-first-law"
concept: "牛顿第一定律"
domain: "physics"
subdomain: "classical-mechanics"
subdomain_name: "经典力学"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 40.6
generation_method: "llm-rewrite-v2"
unique_content_ratio: 0.407
last_scored: "2026-03-22"
sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Newton's laws of motion"
    url: "https://en.wikipedia.org/wiki/Newton%27s_laws_of_motion"
  - type: "textbook-reference"
    ref: "Halliday, Resnick & Walker. Fundamentals of Physics, 10th ed. Ch.5"
scorer_version: "scorer-v2.0"
---
# 牛顿第一定律

## 概述

牛顿第一定律（Newton's First Law of Motion），又称惯性定律（Law of Inertia），由艾萨克·牛顿于1687年在《自然哲学的数学原理》（*Principia Mathematica*）中正式表述。其原始拉丁文表述为："Corpus omne perseverare in statu suo quiescendi vel movendi uniformiter in directum, nisi quatenus a viribus impressis cogitur statum illum mutare。"

现代标准表述：**一个物体，如果不受外力作用（或所受合力为零），将保持静止状态或匀速直线运动状态不变。** 数学表达为：当 $\sum \vec{F} = 0$ 时，$\vec{v} = \text{const}$（含 $\vec{v} = 0$ 的特殊情况）。

这一定律并非牛顿独创。早在公元前4世纪，亚里士多德认为"物体的自然状态是静止"，需要持续施力才能维持运动。1632年，伽利略通过著名的斜面实验（inclined plane experiment）推翻了这一观点：他发现光滑斜面上的小球会沿对面斜面上升到近乎相同的高度，由此推断在完全光滑的水平面上物体将永远运动下去。笛卡尔在1644年进一步将这一思想推广为直线运动的守恒。牛顿的贡献在于将其精确数学化，并将它作为整个力学体系的第一公理。

## 核心原理

### 惯性（Inertia）

惯性是物体抵抗运动状态改变的固有属性。惯性的大小由物体的**质量**（mass）唯一决定——质量越大，惯性越大，改变其运动状态所需的力就越大。

日常体验中：推动一辆空购物车比推满载购物车容易得多——满载车质量更大，惯性更大。在太空中（微重力环境），宇航员推动一个质量为100 kg的设备箱，尽管设备箱"没有重量"，但由于惯性仍然需要施加可观的力才能改变其运动状态。

**关键区分**：惯性是标量属性，与运动方向无关。质量是惯性的度量，单位为千克（kg）。重量（$W = mg$）是引力作用的结果，随位置而变，而惯性（质量）不变。

### 惯性参考系（Inertial Reference Frame）

牛顿第一定律同时定义了**惯性参考系**的概念：在该参考系中，不受力的物体保持匀速直线运动或静止。换言之，第一定律成立的参考系就是惯性参考系。

地球表面近似为惯性参考系（忽略自转效应，地球自转引起的向心加速度在赤道约为 $0.034 \, \text{m/s}^2$，远小于 $g = 9.8 \, \text{m/s}^2$）。而旋转的旋转木马、加速的汽车内部则不是惯性参考系——在这些参考系中会出现"虚拟力"（如离心力、科里奥利力）。

### 合力为零 ≠ 没有力

第一定律的条件是"合力为零"而非"没有力"。一本放在桌上的书同时受到重力 $mg$（向下）和桌面支持力 $N$（向上），二者大小相等方向相反，合力为零，因此书保持静止。匀速行驶的汽车，发动机牵引力与空气阻力+摩擦力平衡，合力为零。

## 实际应用

1. **安全带设计**：急刹车时，车身减速但乘客因惯性继续前冲。安全带提供使乘客减速的力。现代三点式安全带由Volvo工程师Nils Bohlin于1959年发明，正是基于对惯性效应的工程应对。

2. **航天器姿态控制**：在太空真空中，航天器一旦获得速度就会永远以该速度运动（无摩擦力）。这就是为什么"旅行者1号"探测器在1977年发射后无需持续推进仍在飞行，目前距地球超过240亿公里。

3. **魔术中的桌布抽取**：快速抽走桌布时，桌上的餐具因惯性"倾向于"保持静止状态（前提是桌布与餐具间摩擦力作用时间极短，不足以显著改变餐具的运动状态）。

## 常见误区

1. **"力是维持运动的原因"**：这是亚里士多德力学的核心错误。事实上，力是**改变**运动状态的原因，不是维持运动的原因。在冰面上滑动的冰球之所以最终停下，不是因为"缺乏推力"，而是因为冰面摩擦力（虽小但非零）持续使它减速。

2. **"静止的物体没有惯性"**：静止和匀速运动在第一定律中地位完全平等。质量为1000 kg的静止汽车和以100 km/h匀速行驶的汽车具有相同的惯性（相同的质量）。

3. **"牛顿第一定律是第二定律的特例"**：从数学形式看，当 $F=0$ 时 $F=ma$ 给出 $a=0$，似乎第一定律多余。但第一定律的核心价值在于**定义了惯性参考系的存在**，没有这个前提，第二定律 $F=ma$ 中的加速度 $a$ 将无法被正确测量。

## 知识关联

**先修概念**：理解牛顿第一定律需要掌握一维运动学中位移、速度、加速度的定义，以及匀速直线运动与变速运动的区别。

**后续发展**：牛顿第一定律为第二定律（$\vec{F} = m\vec{a}$）和第三定律（作用力与反作用力）提供了概念基础。在更高级的框架中，爱因斯坦的广义相对论（1915年）重新定义了惯性参考系：在弯曲时空中，自由落体的参考系才是局域惯性参考系（等效原理）。

## 参考来源

- [Newton's laws of motion - Wikipedia](https://en.wikipedia.org/wiki/Newton%27s_laws_of_motion)
- Halliday, D., Resnick, R., & Walker, J. *Fundamentals of Physics*, 10th ed., Chapter 5.
- Feynman, R. *The Feynman Lectures on Physics*, Vol. I, Ch. 9: Newton's Laws of Dynamics.
