---
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
last_scored: "2026-03-22"
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
