---
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
last_scored: "2026-03-22"
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
