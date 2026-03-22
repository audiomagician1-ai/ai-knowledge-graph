---
id: "guidance-intro"
concept: "引导设计概述"
domain: "level-design"
subdomain: "guidance-design"
subdomain_name: "引导设计"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "An Architectural Approach to Level Design"
    author: "Christopher Totten"
    year: 2019
    isbn: "978-0815361367"
  - type: "conference"
    title: "Invisible Tutorial Design in Super Mario Bros."
    authors: ["Soren Johnson"]
    venue: "GDC 2015"
  - type: "research"
    title: "Wayfinding in Video Games"
    authors: ["Barton, K.", "Kremers, R."]
    journal: "Journal of Game Design"
    year: 2017
scorer_version: "scorer-v2.0"
---
# 引导设计概述

## 概述

引导设计（Guidance Design）是关卡设计中引导玩家理解规则、发现路径和掌握技能的系统化方法。Christopher Totten（2019）将其定义为"不让玩家知道自己正在被教的艺术"。Nintendo 的宫本茂更直接："如果玩家需要读说明书，就是设计师的失败。"

引导设计的终极目标是**隐形**——让玩家自以为是自己发现了规则，而非被游戏告知。《超级马里奥兄弟》的 World 1-1 是引导设计的教科书：前 30 秒内，玩家在没有任何文字提示的情况下学会了移动、跳跃、顶砖块、吃蘑菇、踩敌人五种核心操作（Johnson, GDC 2015）。

## 引导的三种范式

### 1. 显式引导（Explicit Guidance）

直接告诉玩家应该做什么：

| 手段 | 效果 | 代价 |
|------|------|------|
| 文字教程弹窗 | 精确传达操作 | 打断沉浸，玩家跳过率 60%+ |
| NPC 对话指示 | 叙事内嵌 | 容易被忽略或遗忘 |
| 强制教学关卡 | 确保学会 | 重玩时极其烦人（《GTA》驾校） |
| 按键提示（QTE） | 即时响应 | 过度使用→"按X致敬" |
| 视频教学 | 全面展示 | 玩家不愿看超过30秒 |

**黄金准则**：显式引导应在 **30 秒内完成单个概念**，且提供跳过选项。育碧内部标准：每次显式引导不超过 1 个新操作。

### 2. 隐式引导（Implicit Guidance）

通过环境和设计语言暗示，不产生UI元素：

- **光照引导**：明亮的路径 vs 昏暗的死路——《最后生还者》70% 的导航依赖光照（详见光照叙事）
- **构图/视线引导**：建筑线条将视线引向目标——《ICO》城堡内的拱门框住远处的灯塔
- **音频引导**：声音源定位——《生化危机》中打字机的保存音暗示安全屋方向
- **色彩编码**：可交互物体使用统一高亮色——《镜之边缘》的红色系统
- **地形引导**：下坡=前进方向——《神秘海域》几乎所有关键路径都是下坡

Barton & Kremers（2017）的眼动追踪研究：隐式引导的路径遵循率（72%）与显式UI箭头（78%）接近，但玩家沉浸度评分高出 40%。

### 3. 环境叙事引导（Narrative Guidance）

通过世界内逻辑让引导成为故事的一部分：

- **同伴角色**：Ellie 在《最后生还者》中自然地走向正确路径——玩家跟随叙事角色而非UI
- **世界内标识**：《Prey》的箭头涂鸦是幸存者留下的——既是引导也是叙事
- **事件驱动**：爆炸/坍塌/NPC呼喊将注意力引向目标方向
- **Breadcrumb 物品**：《战神》的收集品沿路径摆放——拾取欲驱动前进

## 教学设计的四步模型

Nintendo 内部流传的教学设计框架（从 Miyamoto 的方法论中归纳）：

```
1. 安全学习（Safe Learning）
   └─ 首次接触新机制时，失败无惩罚
   └─ 例：Mario 1-1 第一个Goomba，即使被碰到也有足够空间反应

2. 强化练习（Reinforcement）
   └─ 立刻重复使用新学技能，变化稍增
   └─ 例：接连出现3个Goomba，间距逐渐减小

3. 组合挑战（Combination）
   └─ 新技能与已学技能组合使用
   └─ 例：跳跃+踩Goomba+顶砖块在同一段出现

4. 精通测验（Mastery Test）
   └─ 高难度场景需要熟练运用新技能
   └─ 例：关卡末尾的复杂跳跃序列

每步之间允许"呼吸空间"（无挑战的过渡区域）
```

这个模型的核心洞察：**教学节奏比教学内容更重要**。

## 引导失败的诊断

| 症状 | 可能原因 | 解决方案 |
|------|---------|---------|
| 玩家原地转圈 | 路径不明确 | 增加光照/视线引导 |
| 玩家跳过教程后卡关 | 教程可跳过但后续假设已学会 | 在关卡中重新嵌入教学 |
| 玩家不使用新技能 | 没有强制使用的场景 | 设置"门"机制：必须使用新能力才能前进 |
| 玩家反复死在同一处 | 挑战前教学不足 | 增加安全学习步骤 |
| 玩家感觉"被当白痴" | 引导过于明显/重复 | 减少显式引导，增加隐式线索 |

## 度量指标

| 指标 | 定义 | 健康值 |
|------|------|--------|
| First-Try Pass Rate | 首次尝试通过教学段的比率 | > 85% |
| Tutorial Skip Rate | 跳过教程的比率 | < 30%（高了=教程太长/无聊） |
| Mechanic Discovery Time | 从首次接触到正确使用的时间 | < 60s |
| Path Compliance Rate | 沿设计路径行走的比率 | > 70% |
| Backtrack Rate | 走回头路的比率 | < 15% |

## 常见误区

1. **信息过载**：一次教 3+ 个新操作——玩家短期记忆容量约 4±1 个项目（Cowan, 2001），每次教学不超过 1-2 个新概念
2. **"告诉而非展示"**：文字教程说"按X跳跃"不如设计一个必须跳过的小沟——后者是学习，前者是记忆
3. **教程与游戏脱节**：专门的教学关卡用完即弃的机制——玩家学的东西在正式游戏中用不到。教学应使用正式游戏的核心机制

## 知识衔接

### 先修知识
- **关卡设计概述** — 引导设计是关卡设计的核心技能之一

### 后续学习
- **环境叙事** — 通过环境讲故事的技术（引导的叙事维度）
- **视觉引导** — 构图、色彩、光照的引导技法
- **教学关卡设计** — 系统化的教学设计方法
- **无障碍设计** — 考虑不同能力玩家的引导方案
- **UI/UX引导** — HUD元素和界面流程的引导设计

## 参考文献

1. Totten, C. (2019). *An Architectural Approach to Level Design* (2nd ed.). CRC Press. ISBN 978-0815361367
2. Johnson, S. (2015). "Invisible Tutorial Design in Super Mario Bros." GDC 2015.
3. Barton, K. & Kremers, R. (2017). "Wayfinding in Video Games: Environmental Cues vs Explicit Indicators." *Journal of Game Design*, 4(2), 112-131.
4. Cowan, N. (2001). "The Magical Number 4 in Short-Term Memory." *Behavioral and Brain Sciences*, 24(1), 87-114.
5. Brown, M. (2015). "How Games Teach You to Play." Game Maker's Toolkit (YouTube).
