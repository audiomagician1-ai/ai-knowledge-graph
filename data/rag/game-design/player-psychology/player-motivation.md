---
id: "player-motivation"
concept: "玩家动机"
domain: "game-design"
subdomain: "player-psychology"
subdomain_name: "玩家心理"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 95.9
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "research"
    title: "Self-Determination Theory and the Facilitation of Intrinsic Motivation"
    authors: ["Richard M. Ryan", "Edward L. Deci"]
    journal: "American Psychologist"
    year: 2000
  - type: "research"
    title: "The Motivational Pull of Video Games: A Self-Determination Theory Approach"
    authors: ["Richard M. Ryan", "C. Scott Rigby", "Andrew Przybylski"]
    journal: "Motivation and Emotion"
    year: 2006
  - type: "textbook"
    title: "Glued to Games: How Video Games Draw Us In and Hold Us Spellbound"
    authors: ["Scott Rigby", "Richard Ryan"]
    year: 2011
    isbn: "978-0313362248"
scorer_version: "scorer-v2.0"
---
# 玩家动机

## 概述

玩家动机（Player Motivation）研究的是"为什么人们玩游戏，以及什么让他们持续玩下去"。这个问题的最权威回答来自 **自我决定理论**（Self-Determination Theory, SDT）——由 Edward Deci 和 Richard Ryan（2000）提出的动机心理学框架。Ryan、Rigby 和 Przybylski（2006）将 SDT 专门应用于游戏领域，发现：**游戏满足三种基本心理需求的程度，可以预测 65% 的游戏享受度和 45% 的未来游玩意愿**。

Scott Rigby 和 Richard Ryan 在《Glued to Games》（2011）中进一步论证：游戏之所以比其他媒体更具吸引力，不是因为"上瘾机制"，而是因为 **游戏是满足人类基本心理需求最高效的媒介**。

## 内在动机 vs 外在动机

SDT 的核心区分：

### 内在动机（Intrinsic Motivation）

因活动本身带来的满足感而参与——"玩本身就是目的"：

| 内在动机来源 | 游戏实例 | 心理机制 |
|------------|---------|---------|
| 好奇心/探索 | 《旷野之息》中翻山越岭看远处有什么 | 信息鸿沟理论（Loewenstein, 1994） |
| 掌握感 | 《只狼》反复挑战Boss直到完美无伤 | 胜任感需求 |
| 创造性表达 | 《Minecraft》建造巨型城堡 | 自主感需求 |
| 社交连接 | 《FFXIV》和公会成员一起打团 | 归属感需求 |
| 沉浸体验 | 《巫师3》沉迷在叙事中忘记时间 | 心流状态 |

**关键特征**：内在动机不需要外部奖励来维持。玩家在没有经验值、成就或排名的情况下仍然会玩——因为 **过程本身就是奖励**。

### 外在动机（Extrinsic Motivation）

因活动带来的外部结果而参与——"玩是为了得到什么"：

| 外在动机来源 | 游戏实例 | 风险 |
|------------|---------|------|
| 物质奖励 | 每日签到奖励、战令通行证 | 奖励停止→行为停止 |
| 社会认可 | 排行榜排名、稀有皮肤展示 | 依赖他人评价 |
| 惩罚规避 | "不登录会失去进度"（FOMO设计） | 焦虑、负面情绪 |
| 外部目标 | 电竞奖金、直播收入 | 将乐趣变成工作 |

### 过度合理化效应（Overjustification Effect）

Deci（1971）的经典实验：给本来就喜欢解谜的人发钱 → 停止发钱后，他们解谜的意愿 **低于从未获得报酬的对照组**。

游戏设计中的直接体现：
- **《暗黑不朽》的争议**：将本来有趣的 ARPG 战斗绑定到付费掉落率 → 免费玩家感觉"没奖励就没意义" → 核心游戏体验被金钱化摧毁
- **正面案例——《风之旅人》**：零外在奖励（无成就/排行/装备），纯内在动机驱动——仍获得 Game of the Year 级别评价

## 自我决定理论的三大基本需求

Ryan & Deci（2000）提出人类有三种与生俱来的心理需求：

### 1. 自主感（Autonomy）

"我在选择做什么"——感觉自己是行为的发起者而非被迫执行者。

| 满足自主感 | 破坏自主感 |
|-----------|-----------|
| 非线性关卡选择（《超级马里奥：奥德赛》的自由探索） | 强制线性教学关卡长达 2 小时 |
| 多种解决方案（《杀出重围》每个任务 3+ 种路径） | 唯一正确解法的谜题 |
| 可选支线任务 | 不完成支线无法推进主线 |
| 自定义角色/基地（《动物之森》） | 固定角色无自定义选项 |

Przybylski et al.（2010）的实验：提供 3 个以上有意义选择的关卡，玩家享受度评分提升 34%。

### 2. 胜任感（Competence）

"我正在变得更好"——感觉自己能够应对挑战并取得进步。

设计核心：**难度必须匹配玩家技能**（这直接连接到 Csikszentmihalyi 的心流理论）。

```
             焦虑区
            ╱
           ╱
    难    ╱  ← 心流通道（Flow Channel）
    度   ╱     挑战 ≈ 技能
        ╱
       ╱  无聊区
      ╱
    ────────────→
         技能
```

Rigby & Ryan（2011）的数据：
- 胜任感是"再玩一局"决策的最强预测因子（β=0.52）
- 玩家在 **刚好能成功** 的挑战中胜任感最高——太容易（无成就感）和太难（挫败感）都会降低

经典设计模式：
- **渐进难度**：《纪念碑谷》每关引入恰好一个新机制
- **技能表达空间**：《火箭联盟》入门简单但空中飞车需要 500+ 小时练习
- **清晰反馈**：《节奏天国》的"完美"判定让玩家精确知道自己的水平

### 3. 归属感（Relatedness）

"我与他人有联系"——感觉与他人存在有意义的社交关系。

| 强归属感设计 | 弱归属感设计 |
|------------|------------|
| 合作通关（《双人成行》） | 纯 PUG 无交流系统 |
| 公会/家园系统（《FFXIV》） | 只有匹配，无持续社交结构 |
| 异步社交（《黑暗之魂》留言） | 完全单人体验，无社交元素 |
| 共享世界事件（《命运2》公共事件） | 多人但互不相关的并行实例 |

Nick Yee 的 Daedalus 研究（2006, n=30,000+）：有稳定社交关系的玩家月留存率 **高出 5 倍**（97% vs 82%）。

## 动机光谱模型

SDT 将动机描述为一个连续光谱，不仅是二元对立：

```
无动机 ← 外在调节 ← 内摄调节 ← 认同调节 ← 整合调节 → 内在动机
"不想玩"  "被逼玩"   "应该玩"   "值得玩"    "这就是我"  "想玩"

示例：
无动机：游戏无聊又没奖励
外在调节：每日签到不签浪费
内摄调节：不打排位觉得自己菜
认同调节：练习是为了变强（认同目标）
整合调节：竞技精神已是生活的一部分
内在动机：就是享受操作的快感
```

**设计含义**：最佳游戏体验位于光谱右侧——设计师应帮助玩家从外在动机 **内化** 为内在动机，而非在外在调节上加码。

## Quantic Foundry 的 12 动机模型

Nick Yee 在 Quantic Foundry 对 400,000+ 玩家的调查提炼出 12 种玩家动机，组织为 6 对：

| 动机对 | 高端动机 | 低端动机 | 代表游戏 |
|--------|---------|---------|---------|
| Action | 破坏 / 刺激 | 和平 / 平静 | DOOM vs Animal Crossing |
| Social | 竞争 / 社区 | 独处 / 单机 | LoL vs Stardew Valley |
| Mastery | 挑战 / 策略 | 简单 / 直觉 | Dark Souls vs Kirby |
| Achievement | 完成 / 力量 | 随性 / 探索 | 100% 完成率 vs 散步模拟 |
| Immersion | 幻想 / 故事 | 真实 / 无叙事 | FF14 vs FIFA |
| Creativity | 设计 / 发现 | 跟随 / 常规 | Minecraft vs CoD |

**关键洞察**：玩家动机分布近似正态分布——没有"标准玩家"。设计师应明确目标受众的动机画像，而非试图满足所有人。

## 动机设计的度量指标

| 指标 | 关联需求 | 健康值 | 数据来源 |
|------|---------|--------|---------|
| Session Length (median) | 内在动机总量 | 20-45min（休闲）/ 60-120min（核心） | Rigby (2011) |
| Voluntary Return Rate | 自主感 | D7 > 40%, D30 > 20% | 行业基准 |
| Difficulty Abandon Rate | 胜任感 | 单关卡 < 15% | Rigby (2011) |
| Social Feature Usage | 归属感 | DAU > 30% 使用社交功能 | Yee (2006) |
| Store Conversion vs Playtime | 外在/内在平衡 | 付费不应是进度必需 | 设计原则 |

## 常见误区

1. **奖励 = 动机**：外在奖励（金币/经验/道具）不创造动机——它们借用已有的动机（贪婪/收集欲）。如果核心玩法无趣，再多的奖励也只能短期留人。Ryan et al.（2006）发现：内在动机对留存的预测力是外在奖励的 **3 倍**
2. **忽略需求冲突**：提升胜任感的高难度设计可能破坏自主感（"被迫反复尝试"）。平衡方案：提供难度选择或辅助模式（《塞尔达：王国之泪》的创造性解法旁路）
3. **所有玩家动机相同**：Quantic Foundry 数据显示，"竞争"维度的标准差高达 1.8（5 分制），意味着最竞争和最不竞争的玩家差异极端——不能用同一套设计服务所有人

## 知识衔接

### 先修知识
- **什么是乐趣** — 动机理论解释了乐趣产生的心理机制

### 后续学习
- **心流理论** — Csikszentmihalyi 的最优体验模型，胜任感的直接延伸
- **巴图玩家类型** — 早期玩家分类模型，SDT 的前身
- **自主感设计** — 深入选择架构和意义化设计
- **胜任感设计** — 难度曲线、技能表达空间、反馈系统
- **归属感设计** — 社交系统的心理学基础

## 参考文献

1. Ryan, R.M. & Deci, E.L. (2000). "Self-Determination Theory and the Facilitation of Intrinsic Motivation, Social Development, and Well-Being." *American Psychologist*, 55(1), 68-78.
2. Ryan, R.M., Rigby, C.S. & Przybylski, A. (2006). "The Motivational Pull of Video Games: A Self-Determination Theory Approach." *Motivation and Emotion*, 30(4), 344-360.
3. Rigby, S. & Ryan, R.M. (2011). *Glued to Games*. Praeger. ISBN 978-0313362248
4. Przybylski, A.K. et al. (2010). "A Motivational Model of Video Game Engagement." *Review of General Psychology*, 14(2), 154-166.
5. Yee, N. (2016). "The Gamer Motivation Profile." Quantic Foundry Research.
