---
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
last_scored: "2026-03-22"
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
