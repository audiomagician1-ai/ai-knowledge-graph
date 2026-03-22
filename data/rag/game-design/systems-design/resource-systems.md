---
id: "resource-systems"
concept: "资源系统"
domain: "game-design"
subdomain: "systems-design"
subdomain_name: "系统设计"
difficulty: 2
is_milestone: false
tags: ["资源", "经济", "系统"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.85
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    name: "Adams & Dormans, Game Mechanics: Advanced Game Design"
  - type: "textbook"
    name: "Schell, The Art of Game Design, 3rd ed."
scorer_version: "scorer-v2.0"
---
# 资源系统

## 定义与核心概念

资源系统（Resource System）是游戏中管理**可量化资产的产出、消耗、储存和流转**的机制框架。Adams & Dormans 在《Game Mechanics: Advanced Game Design》中将其形式化为一个**经济系统**：由源头（Sources）、汇聚（Sinks）、转换器（Converters）和交易机制（Traders）组成的流网络。

所有游戏本质上都是资源管理游戏——从《大富翁》的现金到《魔兽世界》的多层级货币体系，资源系统的设计质量直接决定了游戏经济的健康度和玩家决策的深度。

## Machinations 框架

Adams & Dormans 提出的可视化经济建模语言，核心元素：

| 符号 | 名称 | 功能 | 游戏示例 |
|------|------|------|---------|
| ●→ | **Source（源）** | 产出资源 | 怪物刷新、每日登录 |
| →● | **Sink（汇）** | 消耗资源 | 装备修理、消耗品使用 |
| ○ | **Pool（池）** | 储存资源 | 背包、银行 |
| □ | **Converter（转换器）** | A资源→B资源 | 制造系统、升级 |
| ◇ | **Trader（交易器）** | 双向转换 | 拍卖行、NPC商店 |
| △ | **Gate（门）** | 条件通过 | 等级门槛、任务前置 |

### 四种基本经济模式

```
1. 静态引擎（Static Engine）：
   Source → Pool → Sink
   产出速率固定，消耗速率固定
   例：每日获得100金币，商店物品固定价格

2. 动态引擎（Dynamic Engine）：
   Source → Pool → Converter → Pool → Sink
   产出速率随游戏进度变化
   例：高等级区域产出更多金币，但消耗也更大

3. 正反馈引擎（Positive Feedback）：
   Pool → [修改产出速率] → Source → Pool
   资源越多→获取速度越快（"富者越富"）
   例：投资回报、复利机制

4. 负反馈引擎（Negative Feedback）：
   Pool → [修改产出速率] → Source → Pool（反向）
   资源越多→获取速度越慢（自动平衡）
   例：Mario Kart位次加速、追赶机制
```

## 资源分类体系

### 按功能分类

| 类型 | 定义 | 设计意图 | 示例 |
|------|------|---------|------|
| **硬通货** | 最稀缺、最通用 | 长期目标驱动 | 钻石/水晶（F2P） |
| **软通货** | 主要游戏循环的中介 | 日常决策 | 金币 |
| **能量/体力** | 限制玩家行动频率 | 留存节奏控制 | 体力值、燃料 |
| **材料** | 制造/升级的消耗品 | 目标追踪 | 矿石、草药 |
| **经验值** | 不可交易的进度标记 | 成长感 | EXP |
| **声望/信用** | 社交证明 | 身份认同 | 排名分、成就点 |

### 按经济属性分类

```
可交易 vs 不可交易（绑定）：
  可交易：金币、材料 → 形成玩家间经济
  绑定：任务奖励装备、赛季通行证进度 → 防止RMT

有限 vs 无限：
  有限（Fixed Supply）：限定版物品、NFT → 稀缺性驱动价值
  无限（Faucet）：日常产出的金币 → 需要等量的Sink防止通胀

通胀风险 = Source总产出 - Sink总消耗
  > 0 → 通胀（物价上涨、货币贬值）
  < 0 → 通缩（物价下跌、新玩家获取困难）
  = 0 → 均衡（理想但几乎不可能静态实现）
```

## 经济平衡设计

### 源-汇平衡方程

```
长期均衡条件：
  ΣSource_rate × active_time = ΣSink_rate × active_time + ΔInventory

实际操作：
  日产出（Source）：
    任务奖励：500金/天
    怪物掉落：300金/天
    日常签到：100金/天
    总计：900金/天

  日消耗（Sink）：
    装备修理：150金/天
    消耗品购买：200金/天
    制造材料：100金/天
    税/手续费：50金/天（拍卖行5%抽成）
    总计：500金/天

  净流入：+400金/天 → 通胀！
  
  解决方案：
  - 添加新Sink（时装、坐骑、住宅装饰）
  - 增加税率
  - 添加金币上限
  - 引入"金币重置"机制（赛季制）
```

### 双币模型（F2P标配）

```
免费货币（软通货）：  时间 → 软通货 → 基本功能
付费货币（硬通货）：  真实金钱 → 硬通货 → 加速/装饰

关键设计参数：
  硬通货 ↔ 软通货 兑换比例
  每日免费硬通货产出量（维持免费玩家参与感）
  硬通货的独占消费品（驱动付费）

《原神》案例：
  软通货（摩拉）：日常获取约 120,000-200,000
  硬通货（原石）：免费获取约 60/天（探索+委托）
  160原石=1次祈愿 → 免费玩家约2.7天/抽
  付费：648元=6480原石=40.5抽 → 每抽约16元
```

## 心理学机制

| 机制 | 资源系统应用 | 心理效应 |
|------|------------|---------|
| 损失厌恶 | 装备耐久度下降 | 驱动修理/更换消费 |
| 禀赋效应 | 拾取即绑定 | 物品感知价值上升 |
| 沉没成本 | 升级进度不可逆 | 增加留存 |
| 锚定效应 | 商店原价显示 | 折扣感知放大 |
| 稀缺性偏误 | 限时/限量资源 | FOMO（害怕错过） |

## 参考文献

- Adams, E. & Dormans, J. (2012). *Game Mechanics: Advanced Game Design*. New Riders. ISBN 978-0321820273
- Schell, J. (2019). *The Art of Game Design: A Book of Lenses*, 3rd ed. CRC Press. ISBN 978-1138632059
- Castronova, E. (2005). *Synthetic Worlds: The Business and Culture of Online Games*. University of Chicago Press. ISBN 978-0226096278

## 教学路径

**前置知识**：基础游戏设计概念、基本经济学概念（供需）
**学习建议**：先用 Machinations（machinations.io 在线工具）建模一个简单的 Source→Pool→Sink 系统，观察参数变化如何导致通胀/通缩。然后分析 3 款 F2P 游戏的双币模型。最后设计一个完整的 4 资源类型经济系统并用 Excel 模拟 30 天运行。
**进阶方向**：Agent-based 经济模拟、虚拟经济中的货币政策（如 EVE Online 的经济学家）、行为经济学在内购设计中的应用。
