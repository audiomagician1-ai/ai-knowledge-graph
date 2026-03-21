---
id: "rotational-dynamics"
concept: "转动动力学"
domain: "physics"
subdomain: "classical-mechanics"
subdomain_name: "经典力学"
difficulty: 5
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 34.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.714
last_scored: "2026-03-21"
sources: []
---
# 转动动力学

## 概述

转动动力学是经典力学中描述刚体转动运动的分支。正如牛顿第二定律 $F=ma$ 描述平动，转动的基本方程是 $\tau = I\alpha$——力矩等于转动惯量乘以角加速度。转动动力学使我们能够分析陀螺、飞轮、行星自转等旋转系统。

## 核心知识点

### 角量与线量的对应

| 线量 | 角量 | 关系 |
|:---|:---|:---|
| 位移 $s$ | 角位移 $\theta$ | $s = r\theta$ |
| 速度 $v$ | 角速度 $\omega$ | $v = r\omega$ |
| 加速度 $a$ | 角加速度 $\alpha$ | $a_t = r\alpha$ |
| 力 $F$ | 力矩 $\tau$ | $\tau = rF\sin\theta$ |
| 质量 $m$ | 转动惯量 $I$ | $I = \sum m_i r_i^2$ |
| $F = ma$ | $\tau = I\alpha$ | — |

### 转动惯量

$$I = \int r^2 dm$$

常见刚体的转动惯量（绕中心轴）：
- 细棒（绕中点）：$I = \frac{1}{12}ML^2$
- 实心圆柱/圆盘：$I = \frac{1}{2}MR^2$
- 实心球：$I = \frac{2}{5}MR^2$
- 薄球壳：$I = \frac{2}{3}MR^2$

**平行轴定理**：$I = I_{cm} + Md^2$（$d$ 是新轴到质心的距离）

### 角动量守恒

角动量 $\vec{L} = I\vec{\omega}$，当合外力矩为零时：

$$I_1\omega_1 = I_2\omega_2$$

经典例子：花样滑冰选手收紧手臂（$I$ 减小），转速 $\omega$ 加快。

### 转动动能

$$K_{\text{rot}} = \frac{1}{2}I\omega^2$$

刚体沿斜面滚动时，总动能 = 平动动能 + 转动动能：$K = \frac{1}{2}mv^2 + \frac{1}{2}I\omega^2$

## 关键要点

1. **转动惯量取决于质量分布和转轴位置**：同一物体绕不同轴转动，转动惯量不同
2. **纯滚动的约束条件**：$v = R\omega$（接触点速度为零）
3. **角动量是矢量**：方向沿转轴，由右手定则确定。陀螺进动就是力矩改变角动量方向的结果

## 常见误区

1. **"质量大转动惯量就大"**：不一定。质量分布在远离转轴处时转动惯量更大（空心圆柱比同质量实心圆柱转动惯量大）
2. **"不滑动的物体没有摩擦力"**：纯滚动时存在静摩擦力，提供角加速度的力矩，但不做功

## 知识衔接

**先修概念**：牛顿第二定律、动量守恒、能量守恒

**后续概念**：陀螺进动、刚体动力学、角动量量子化、天体自转
