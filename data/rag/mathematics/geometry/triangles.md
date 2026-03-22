---
id: "triangles"
concept: "三角形"
domain: "mathematics"
subdomain: "geometry"
subdomain_name: "几何"
difficulty: 3
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 32.2
generation_method: "llm-rewrite-v2"
unique_content_ratio: 0.344
last_scored: "2026-03-22"
sources:
  - type: "encyclopedia"
    ref: "Wikipedia - Triangle"
    url: "https://en.wikipedia.org/wiki/Triangle"
  - type: "textbook-reference"
    ref: "Euclid. Elements, Book I"
scorer_version: "scorer-v2.0"
---
# 三角形

## 概述

三角形（Triangle）是由三条线段首尾相连构成的最简单多边形，也是欧几里得几何中最基本的图形。三角形的研究可追溯到古埃及和古巴比伦时期（约公元前2000年），而系统化的三角形理论由欧几里得在《几何原本》（*Elements*，约公元前300年）的第一卷中建立。

三角形有三个顶点、三条边和三个内角，内角和恒为 $180°$（即 $\pi$ 弧度）。这一定理是欧几里得几何的标志性结论，在非欧几何中不成立——球面三角形的内角和大于180°，双曲面三角形的内角和小于180°。

## 核心原理

### 分类体系

**按角分类**：
| 类型 | 定义 | 特征 |
|------|------|------|
| 锐角三角形 | 三个角均 < 90° | 外接圆圆心在三角形内部 |
| 直角三角形 | 有一个角 = 90° | 满足勾股定理 $a^2 + b^2 = c^2$ |
| 钝角三角形 | 有一个角 > 90° | 外接圆圆心在三角形外部 |

**按边分类**：
- **等边三角形**（equilateral）：三边相等，三角均为60°
- **等腰三角形**（isosceles）：至少两边相等，底角相等
- **不等边三角形**（scalene）：三边互不相等

### 核心定理

**勾股定理**（Pythagorean Theorem）：直角三角形中，$a^2 + b^2 = c^2$，其中 $c$ 为斜边。该定理至少有370种已知证明方法。最早的严格证明出现在欧几里得《原本》命题I.47。勾股数的例子：$(3,4,5)$、$(5,12,13)$、$(8,15,17)$。

**正弦定理**：$\frac{a}{\sin A} = \frac{b}{\sin B} = \frac{c}{\sin C} = 2R$，其中 $R$ 为外接圆半径。

**余弦定理**：$c^2 = a^2 + b^2 - 2ab\cos C$，这是勾股定理的推广——当 $C = 90°$ 时，$\cos C = 0$，退化为勾股定理。

### 面积公式

三角形面积有多种计算方式：

1. **基本公式**：$S = \frac{1}{2} \times \text{底} \times \text{高}$
2. **两边夹角**：$S = \frac{1}{2}ab\sin C$
3. **海伦公式**（Heron's Formula，约公元60年）：$S = \sqrt{s(s-a)(s-b)(s-c)}$，其中 $s = \frac{a+b+c}{2}$ 为半周长
4. **坐标公式**：给定三顶点 $(x_1,y_1), (x_2,y_2), (x_3,y_3)$，$S = \frac{1}{2}|x_1(y_2-y_3) + x_2(y_3-y_1) + x_3(y_1-y_2)|$

### 特殊点与线

- **重心**（centroid）：三条中线交点，坐标为三顶点坐标的算术平均
- **外心**（circumcenter）：三条中垂线交点，到三顶点等距
- **内心**（incenter）：三条角平分线交点，到三边等距
- **垂心**（orthocenter）：三条高线交点

**欧拉线**（Euler Line, 1767年）：任意三角形的重心、外心和垂心共线，且重心将外心到垂心的线段分为 $1:2$。等边三角形中四心重合，无欧拉线。

## 实际应用

1. **三角测量法**：测量难以直接到达的距离。例如，通过在地面两点测量山顶的仰角，结合两点间距，用正弦定理计算山高。

2. **计算机图形学**：所有3D模型的表面由三角形网格（triangle mesh）组成，因为三角形是唯一保证共面的多边形。现代GPU每秒可渲染数十亿个三角形。

3. **结构工程**：三角形是唯一具有**刚性**的多边形——给定三边长度，三角形的形状唯一确定。桥梁和屋架大量使用三角形桁架结构。

## 常见误区

1. **"三角形内角和在任何情况下都是180°"**：仅在欧几里得平面几何中成立。球面上三角形内角和为 $180° + \frac{S}{R^2} \times \frac{180°}{\pi}$（$S$为球面三角形面积，$R$为球半径）。

2. **"勾股定理的逆定理不成立"**：实际上逆定理成立——若 $a^2 + b^2 = c^2$，则三角形必为直角三角形（欧几里得《原本》命题I.48）。

3. **"任意三条线段都能构成三角形"**：必须满足**三角不等式**：任意两边之和大于第三边。即 $a + b > c$，$a + c > b$，$b + c > a$。

## 知识关联

**先修概念**：角的度量、线段长度、面积概念、勾股定理（初步了解）。

**后续发展**：三角形理论通向三角函数（正弦、余弦的几何定义）、向量几何（用向量表示三角形运算）、以及计算几何（凸包算法的基础构件）。在拓扑学中，三角剖分（triangulation）是研究曲面的核心方法。

## 参考来源

- [Triangle - Wikipedia](https://en.wikipedia.org/wiki/Triangle)
- Euclid. *Elements*, Book I (c. 300 BC), Propositions I.47-I.48.
- Coxeter, H.S.M. & Greitzer, S.L. *Geometry Revisited*, MAA (1967).
