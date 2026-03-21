---
id: "amperes-law"
concept: "安培定律"
domain: "physics"
subdomain: "electromagnetism"
subdomain_name: "电磁学"
difficulty: 5
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 35.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.714
last_scored: "2026-03-21"
sources: []
---
# 安培定律

## 概述

安培定律（Ampere's Law）描述了电流与磁场的关系：**沿闭合路径的磁场环路积分等于该路径所围面积内穿过的电流之和乘以真空磁导率**。它是麦克斯韦方程组的第四个方程（安培-麦克斯韦定律）在静态情况下的特殊形式。

## 核心知识点

### 数学表述

$$\oint \vec{B} \cdot d\vec{l} = \mu_0 I_{\text{enc}}$$

其中 $\mu_0 = 4\pi \times 10^{-7}$ T·m/A，$I_{\text{enc}}$ 是穿过安培环路所围面积的总电流。

### 对称性应用

| 电流分布 | 安培环路 | 磁场结果 |
|:---|:---|:---|
| 无限长直导线 | 同心圆 | $B = \frac{\mu_0 I}{2\pi r}$ |
| 密绕螺线管内部 | 矩形环路 | $B = \mu_0 nI$（均匀） |
| 密绕螺线管外部 | — | $B \approx 0$ |
| 环形线圈（toroid） | 内部同心圆 | $B = \frac{\mu_0 NI}{2\pi r}$ |

### 安培-麦克斯韦修正

麦克斯韦发现原始安培定律在时变场中不自洽，添加了位移电流项：

$$\oint \vec{B} \cdot d\vec{l} = \mu_0 I_{\text{enc}} + \mu_0\varepsilon_0\frac{d\Phi_E}{dt}$$

这一修正预言了电磁波的存在。

## 关键要点

1. **磁场线是闭合的**：电流产生的磁场环绕电流，没有起点和终点（无磁荷）
2. **只有穿过安培环路的电流才贡献**：环路外的电流对环路积分无贡献
3. **安培定律是右手定则**：四指沿电流方向弯曲，拇指指向磁场环绕方向

## 常见误区

1. **"安培定律只对直导线有效"**：对任何闭合路径和任何电流分布都成立，只是非对称时无法简化
2. **"螺线管外部磁场严格为零"**：对有限长螺线管，外部有弱漏磁。$B=0$ 只在理想无限长螺线管近似下成立

## 知识衔接

**先修概念**：磁场、毕奥-萨伐尔定律、洛伦兹力

**后续概念**：麦克斯韦方程组、电磁波、电感器
