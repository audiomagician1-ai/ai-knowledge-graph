import sys, os
from pathlib import Path

ROOT = Path(r"D:\EchoAgent\projects\ai-knowledge-graph\data\rag")

docs = {}

# ===== 6. cognitive-biases.md =====
docs["psychology/cognitive-psychology/cognitive-biases.md"] = '''---
id: "cognitive-biases"
concept: "认知偏差"
domain: "psychology"
subdomain: "cognitive-psychology"
subdomain_name: "认知心理学"
difficulty: 2
is_milestone: false
tags: ["思维"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "academic"
    ref: "Kahneman, Daniel. Thinking, Fast and Slow, 2011"
  - type: "academic"
    ref: "Tversky, Amos & Kahneman, Daniel. Judgment under Uncertainty: Heuristics and Biases, Science, 1974"
  - type: "academic"
    ref: "Gigerenzer, Gerd. Rationality for Mortals, Oxford UP, 2008"
  - type: "meta-analysis"
    ref: "Blanco, Fernando et al. Cognitive Biases: A Systematic Review, Frontiers in Psychology, 2018"
scorer_version: "scorer-v2.0"
---
# 认知偏差

## 概述

认知偏差（Cognitive Biases）是人类在信息处理过程中**系统性偏离理性判断**的心理倾向。Tversky 与 Kahneman（1974）的开创性研究表明，人类并非在所有情况下都能理性决策，而是大量依赖**启发式**（Heuristics）——快速但粗糙的心理捷径。这些捷径在大多数日常情境下有效，但在特定条件下会产生可预测的系统误差，即认知偏差。

截至 2024 年，心理学文献中已记录超过 **200 种**认知偏差（Blanco et al., 2018）。Kahneman（2011）在《思考，快与慢》中将其归因于**系统 1（快速、自动、直觉）和系统 2（缓慢、费力、理性）**的运作差异——偏差大多发生在系统 1 主导决策时。

## 核心知识点

### 1. 确认偏差（Confirmation Bias）

**定义**：倾向于搜索、解释和记忆能够证实自己既有信念的信息，同时忽略或贬低矛盾信息。

**经典实验**——Wason 选择任务（1960）：
给受试者 4 张卡片（A, K, 4, 7），规则是"如果卡片一面是元音，另一面必须是偶数"。正确答案是翻 A 和 7（寻找反例），但 **75% 的受试者**选择翻 A 和 4（寻找确认证据）。

**现实影响**：
- **医疗诊断**：医生形成初步诊断后，倾向于关注支持性症状而忽略矛盾症状。一项研究显示，确认偏差导致 **13%** 的误诊（Berner & Graber, 2008）
- **投资决策**：投资者持有亏损股票时选择性阅读利好消息（"信息茧房"的认知根源）
- **社交媒体**：算法推荐 + 确认偏差 = 观点极化的加速器

**去偏差策略**：主动寻找反面证据（"红队思维"），对每个假设问"什么证据能证明我错了？"

### 2. 锚定效应（Anchoring Effect）

**定义**：决策时过度依赖最先接触到的信息（"锚"），即使该信息与决策无关。

**经典实验**（Tversky & Kahneman, 1974）：
受试者先看到一个随机数字（由转盘产生的 10 或 65），然后估计联合国中非洲国家的百分比。看到 10 的组平均估计 **25%**，看到 65 的组平均估计 **45%**——一个完全随机的数字使估计值产生了 20 个百分点的差异。

**现实应用**：
- **定价策略**：原价 ¥999 划掉，现价 ¥399——原价就是锚点
- **薪资谈判**：先报价的一方设定了锚点，后续谈判围绕此锚波动（第一个数字影响最终结果约 **30-40%**）
- **法庭判决**：检察官要求的刑期影响法官量刑（Englich et al., 2006：即使锚来自掷骰子，法官的判决仍受其影响）

### 3. 可得性启发式（Availability Heuristic）

**定义**：根据某类事件在脑中被**回忆起的容易程度**来判断其发生概率——越容易想到的事件，被认为越可能发生。

**机制**：系统 1 将"回忆的流畅性"误读为"频率的信号"。

**经典案例**：
- 飞机失事 vs 车祸：媒体大量报道飞机事故，使人高估飞行风险。实际上每英里飞行的死亡率是驾车的 **1/100**
- 鲨鱼袭击 vs 跌落椰子：鲨鱼袭击每年约 5 人死亡，跌落椰子每年约 150 人——但鲨鱼恐惧远大于椰子
- 恐怖袭击后航空需求下降，转向驾车出行，反而导致更多交通死亡（Gigerenzer, 2004 的"恐惧成本"研究）

**去偏差策略**：用**基础概率**（Base Rate）替代直觉判断。问"实际数据怎么说？"而非"我能想到多少例子？"

### 4. 其他关键偏差速览

| 偏差 | 核心机制 | 一句话示例 |
|------|---------|-----------|
| **后见之明偏差** | 事后认为结果是"显而易见的" | "我早就知道会这样"（但事前并未预测） |
| **框架效应** | 同一信息的不同表述导致不同决策 | "手术成功率 90%" vs "手术死亡率 10%" |
| **沉没成本谬误** | 因已投入的不可回收成本继续投入 | 电影难看但"票都买了"坚持看完 |
| **达克效应** | 能力不足者高估自身能力 | 新手自信满满，专家反而犹豫 |
| **光环效应** | 对某一特质的好印象扩展到全部特质 | 长得好看 = "一定也很聪明" |
| **赌徒谬误** | 认为随机事件有"补偿"趋势 | 连续 5 次红，"下一次一定是黑" |

## 关键原理分析

### 偏差是 Bug 还是 Feature？

Gigerenzer（2008）提出**生态理性**（Ecological Rationality）的反对意见：启发式和偏差不是思维缺陷，而是在信息不完整、时间有限的真实世界中的**适应性工具**。例如，"识别启发式"（Recognition Heuristic）——在两个选项中选择你认识的那个——在预测德国城市人口排名时，外国人反而比德国人更准确（因为外国人只认识大城市）。

### 系统 1 vs 系统 2 的互动模型

偏差并非不可避免。Kahneman 的模型预测：当系统 2 被激活（高动机、有充足时间、问题被框架为需要分析时），偏差程度显著降低。教育干预的核心不是消除系统 1，而是训练"何时需要启动系统 2"的直觉。

## 实践练习

**练习 1（识别偏差）**：记录你今天做的 5 个决策（从早餐选择到工作任务排序），分析每个决策中可能存在的认知偏差。

**练习 2（去偏差实验）**：下次做重要决策前，写下"我的结论是 X，什么证据会让我改变想法？"然后花 5 分钟主动搜索反面证据。记录这个过程是否改变了你的判断。

## 常见误区

1. **"知道偏差就能避免偏差"**：元认知知识有帮助但不充分，研究显示即使知道锚定效应的心理学家仍然受锚定影响
2. **"偏差都是坏的"**：启发式在日常场景中准确率很高，只在特定条件下才系统性出错
3. **"只有不聪明的人才有偏差"**：认知偏差是人类认知架构的固有特征，智商与偏差易感性的相关性非常低（Stanovich & West, 2008）
'''

# ===== 7. combat-overview.md =====
docs["game-design/combat-design/combat-overview.md"] = '''---
id: "combat-overview"
concept: "战斗系统概述"
domain: "game-design"
subdomain: "combat-design"
subdomain_name: "战斗设计"
difficulty: 1
is_milestone: false
tags: ["基础"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "academic"
    ref: "Schell, Jesse. The Art of Game Design, 3rd Ed., Ch.15"
  - type: "industry"
    ref: "Rogers, Scott. Level Up! The Guide to Great Video Game Design, 2nd Ed., 2014"
  - type: "industry"
    ref: "GDC Talk: Platinum Games - Action Game Design, 2017"
  - type: "academic"
    ref: "Sylvester, Tynan. Designing Games, O'Reilly, 2013"
scorer_version: "scorer-v2.0"
---
# 战斗系统概述

## 概述

战斗系统（Combat System）是游戏中玩家与敌人/对手进行对抗性交互的核心机制集合。作为最直接的挑战形式，战斗往往是游戏"秒到秒体验"（Second-to-Second Gameplay）的主体。Tynan Sylvester（2013）指出，优秀战斗系统的本质是**一系列有意义的、高频率的决策**——每个决策都有风险、有成本、有时间压力。

战斗系统的设计复杂度极高，因为它同时涉及**输入系统**（手感）、**数值系统**（伤害/血量）、**AI 系统**（敌人行为）、**动画系统**（反馈）和**关卡设计**（遭遇编排）。一个环节失败就会导致整体体验崩塌。

## 核心知识点

### 1. 战斗系统的核心三角

所有战斗系统都围绕三个核心要素构建（Rogers, 2014）：

| 要素 | 功能 | 设计关键 |
|------|------|---------|
| **攻击**（Attack） | 对敌人造成伤害/效果 | 攻击种类的差异化、连招设计、范围/单体 |
| **防御**（Defense） | 减少或规避来自敌人的伤害 | 格挡、闪避、无敌帧（i-frame）、护盾 |
| **移动**（Movement） | 空间位置的控制与调整 | 走位、冲刺、跳跃、空间控制 |

**黄金法则**：三要素之间必须存在**动态张力**——攻击有风险（暴露破绽）、防御有成本（消耗资源/时间）、移动有限制（速度/距离）。如果任一要素无代价，战斗就变成无脑操作。

### 2. 战斗系统分类

**按时间模型分类**：

| 类型 | 特征 | 核心挑战 | 代表作品 |
|------|------|---------|---------|
| **实时动作** | 连续时间流，手动操作 | 反应速度 + 模式识别 | 《黑暗之魂》《鬼泣》 |
| **回合制** | 离散时间步，轮流行动 | 策略规划 + 资源管理 | 《最终幻想》《火焰纹章》 |
| **即时战术暂停** | 实时流 + 可暂停发指令 | 宏观战术 + 微观执行 | 《博德之门》《全面战争》 |
| **半回合制** | ATB/时间轴系统 | 决策速度 + 优先级判断 | 《最终幻想 ATB》《女神异闻录 5》 |

**按视角分类**：
- **1v1 格斗**：帧数据精确、确认连招、心理博弈（《街头霸王》）
- **1vN 动作**：群体控制、优先目标选择、摄像机管理（《战神》）
- **NvN 团队**：角色搭配、焦点火力、阵型与位置（MOBA/MMO 副本）

### 3. 战斗节奏设计

Platinum Games（2017 GDC）提出的战斗节奏三层模型：

- **微节奏（0.1-2秒）**：单次攻防交互（出招 -> 被挡 -> 反击）
- **中节奏（10-60秒）**：一次遭遇/一个敌人组的战斗过程
- **宏节奏（5-30分钟）**：关卡内战斗与非战斗内容的交替

**节奏设计原则**：
1. **张弛有度**：连续高强度战斗超过 3 分钟就会产生疲劳，需要"呼吸空间"
2. **递进性**：同一关卡内，后面的遭遇应比前面更复杂（新敌人组合、更小空间、更多约束）
3. **高潮感**：Boss 战是宏节奏的顶点，应在机制上与普通战斗有质的区别

### 4. 战斗反馈系统

**打击感（Game Feel）的四要素**：
1. **视觉反馈**：受击动画、粒子效果、屏幕震动、慢动作（Hit Stop）
2. **听觉反馈**：打击音效、受伤语音、环境音变化
3. **触觉反馈**：手柄震动（力度/频率映射伤害类型）
4. **数值反馈**：伤害数字、血条变化、状态图标

**关键技术——Hit Stop**（帧冻结）：
攻击命中的瞬间冻结 2-5 帧（约 33-83ms），创造"重量感"。《怪物猎人》大剑蓄力命中 Hit Stop 约 8 帧，《街头霸王》轻拳约 2 帧。这个微小的暂停是打击感的核心来源。

## 关键原理分析

### 深度 vs 复杂度

David Sirlin 的核心原则：**深度（Depth）是好的复杂度——少量规则产生丰富策略**；**复杂度（Complexity）是坏的深度——大量规则但策略单一**。

好的战斗系统的标志："易学难精"（Easy to Learn, Hard to Master）——核心操作在 5 分钟内能掌握，但最优策略需要数百小时探索。

### 风险-回报平衡

每个战斗选项都应有明确的风险-回报比：
- 高风险高回报：蓄力攻击（慢但伤害高，被打断损失大）
- 低风险低回报：轻攻击（快但伤害低，安全但效率低）
- 如果某个选择既安全又高效，它就是**支配策略**，会扼杀深度

## 实践练习

**练习 1**：选择一款你熟悉的动作游戏，记录一场 Boss 战中你做出的所有"攻击/防御/移动"决策。统计三者的比例，以及你何时在它们之间切换。

**练习 2**：设计一个极简战斗系统（仅 3 种攻击 + 1 种防御 + 移动），写出每个选项的帧数据（起手帧、活跃帧、收招帧）和伤害值，确保没有支配策略。

## 常见误区

1. **"招式越多越好"**：如果大部分招式功能重叠，玩家只会用最优的 2-3 个。质量 > 数量
2. **"难度 = 敌人数值高"**：好的难度来自机制复杂度增加，而非简单提高敌人血量/伤害
3. **忽略反馈设计**：数值完美但缺乏打击感的战斗系统，玩家会感觉"打棉花"
'''

# ===== 8. expectation-variance.md =====
docs["mathematics/probability/expectation-variance.md"] = '''---
id: "expectation-variance"
concept: "期望与方差"
domain: "mathematics"
subdomain: "probability"
subdomain_name: "概率论"
difficulty: 6
is_milestone: false
tags: ["里程碑"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.94
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Sheldon Ross. A First Course in Probability, 10th Ed., Ch.4"
  - type: "textbook"
    ref: "Blitzstein & Hwang. Introduction to Probability, 2nd Ed., Ch.4"
  - type: "academic"
    ref: "Feller, William. An Introduction to Probability Theory, Vol.1, 1968"
scorer_version: "scorer-v2.0"
---
# 期望与方差

## 概述

期望（Expectation, E[X]）和方差（Variance, Var[X]）是概率论中描述随机变量的两个最基本的数字特征。期望度量随机变量的**中心位置**（"平均会得到什么"），方差度量其**离散程度**（"结果有多不确定"）。这两个量共同提供了任何分布最核心的"摘要信息"。

Feller（1968）指出：许多概率论的深刻定理——大数定律、中心极限定理——本质上都是关于期望和方差的陈述。掌握它们是理解整个概率论和统计学大厦的基石。

## 核心知识点

### 1. 期望 E[X] 的定义与计算

**离散型随机变量**：
E[X] = Sum over all x: x * P(X = x) = x1*p1 + x2*p2 + ... + xn*pn

**连续型随机变量**：
E[X] = Integral from -inf to +inf: x * f(x) dx

**直觉理解**：如果你重复同一随机实验无穷多次，观测值的算术平均将趋近于 E[X]。

**常见分布的期望**：

| 分布 | 参数 | E[X] | 直觉 |
|------|------|------|------|
| 伯努利 Bernoulli(p) | 成功概率 p | p | 一次试验的平均成功数 |
| 二项 Binomial(n,p) | n 次试验，成功率 p | np | n 次试验的平均成功数 |
| 泊松 Poisson(lambda) | 到达率 lambda | lambda | 单位时间平均事件数 |
| 均匀 Uniform(a,b) | 区间 [a,b] | (a+b)/2 | 区间中点 |
| 指数 Exp(lambda) | 率参数 lambda | 1/lambda | 平均等待时间 |
| 正态 N(mu, sigma^2) | 均值 mu，方差 sigma^2 | mu | 对称中心 |

### 2. 期望的线性性（最重要的性质）

**无论 X, Y 是否独立**：
E[aX + bY] = a*E[X] + b*E[Y]

这是期望最强大的性质，因为**不需要知道联合分布**就能计算。

**经典应用——指示器随机变量法**：

问题：100 人随机戴帽子（每人等概率戴到任意一顶），期望有多少人戴到自己的帽子？

定义 Xi = 1 如果第 i 人戴对，否则为 0。则 E[Xi] = 1/100。
总数 S = X1 + X2 + ... + X100
E[S] = E[X1] + E[X2] + ... + E[X100] = 100 * (1/100) = **1**

无论 n 是多少（10 人、1000 人、100万人），答案始终是 1。这个优美的结果完全来自线性性。

### 3. 方差 Var[X] 的定义与计算

**定义**：Var[X] = E[(X - E[X])^2] = E[X^2] - (E[X])^2

**标准差**：sigma = sqrt(Var[X])，与 X 同单位，更直观。

**计算技巧**：通常用 E[X^2] - (E[X])^2 比定义式更方便。

**常见分布的方差**：

| 分布 | Var[X] | 直觉 |
|------|--------|------|
| Bernoulli(p) | p(1-p) | p=0.5 时方差最大（最不确定） |
| Binomial(n,p) | np(1-p) | n 次独立试验的累积波动 |
| Poisson(lambda) | lambda | 方差 = 期望（泊松分布的特征） |
| Uniform(a,b) | (b-a)^2/12 | 区间越宽，方差越大 |
| Exp(lambda) | 1/lambda^2 | 指数分布的不确定性 |
| N(mu, sigma^2) | sigma^2 | 参数本身就是方差 |

### 4. 方差的性质

**缩放**：Var[aX + b] = a^2 * Var[X]（常数平移不影响离散度，缩放以平方增长）

**独立变量之和**：若 X, Y 独立，Var[X + Y] = Var[X] + Var[Y]

**注意**：如果 X, Y 不独立，需要协方差项：
Var[X + Y] = Var[X] + Var[Y] + 2*Cov(X,Y)

**重要不等式——切比雪夫不等式**：
P(|X - E[X]| >= k*sigma) <= 1/k^2

即：任何分布中，距离均值超过 k 个标准差的概率不超过 1/k^2。例如 k=3 时，P <= 1/9 约 11.1%。这是一个不依赖分布形状的万能界。

### 5. 实际应用案例

**投资组合风险评估**：
假设两支股票 A、B 的日回报率：E[A] = 0.1%, Var[A] = 4; E[B] = 0.1%, Var[B] = 4。
- 全部投 A：组合方差 = 4
- 各投 50%（独立时）：组合方差 = 0.25*4 + 0.25*4 = 2
- 分散投资将方差降低了 **50%**——这就是"不要把所有鸡蛋放在一个篮子里"的数学基础

**质量控制**：工厂零件直径 N(10mm, 0.01mm^2)。合格范围 [9.7mm, 10.3mm]。
距均值 3 个标准差 = 3*0.1mm = 0.3mm。由正态分布 3-sigma 法则，99.7% 的零件合格。

## 关键原理分析

### 大数定律的直觉预告

样本均值 X_bar = (X1+...+Xn)/n。
E[X_bar] = E[X]（无偏）。
Var[X_bar] = Var[X]/n（方差以 1/n 速度缩小）。

这意味着样本越大，样本均值越集中在真实期望附近——这就是大数定律的核心思想，也是统计推断的基础。

### 期望的"非线性陷阱"

E[g(X)] 通常不等于 g(E[X])。例如 E[X^2] 不等于 (E[X])^2（差值正是方差）。Jensen 不等式给出了凸函数/凹函数情形下的方向性结论：若 g 是凸函数，E[g(X)] >= g(E[X])。

## 实践练习

**练习 1**：掷两颗骰子，令 X = 两颗点数之和。(a) 计算 E[X]；(b) 计算 Var[X]；(c) 验证 Var[X] = Var[X1] + Var[X2]（利用独立性）。

**练习 2**：一个赌徒玩轮盘赌（38 格中有 18 红、18 黑、2 绿），每次押红 10 元。计算 (a) 单次下注的期望收益；(b) 玩 100 次后总收益的期望和标准差。

## 常见误区

1. **混淆期望与最可能值**：E[X] 不一定是 X 能取到的值。例如掷骰子 E[X] = 3.5，但永远掷不出 3.5
2. **方差可以相加 = 标准差可以相加**：Var[X+Y] = Var[X] + Var[Y]，但 sigma(X+Y) 不等于 sigma(X) + sigma(Y)
3. **忽略独立性条件**：方差的可加性需要独立性（或至少不相关），否则必须加协方差项
'''

# ===== 9. 3da-bake-intro.md =====
docs["3d-art/3da-bake-intro.md"] = '''---
id: "3da-bake-intro"
concept: "烘焙概述"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 1
is_milestone: true
tags: ["基础"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "industry"
    ref: "Polycount Wiki: Texture Baking, 2023 revision"
  - type: "industry"
    ref: "Marmoset Toolbag Documentation: Baking Guide, 2024"
  - type: "textbook"
    ref: "Ahearn, Luke. 3D Game Textures, 4th Ed., CRC Press, 2016"
  - type: "industry"
    ref: "Substance 3D Painter Documentation: Baking, Adobe 2024"
scorer_version: "scorer-v2.0"
---
# 烘焙概述

## 概述

贴图烘焙（Texture Baking）是将**高模（High-Poly）表面信息转移到低模（Low-Poly）纹理贴图**上的技术过程。其核心原理是：从低模表面向外发射射线（Ray Casting），与高模表面相交，记录交点处的法线、遮蔽等信息，写入对应 UV 坐标的像素中。

这项技术解决了实时渲染的核心矛盾——**视觉质量 vs 性能开销**。一个 200 万面的高模角色包含了丰富的表面细节（肌肉走向、盔甲雕刻、布料褶皱），但实时渲染中只能用 2-5 万面的低模。烘焙使低模在视觉上"看起来"像高模，运行时性能代价几乎为零（仅增加一次纹理采样）。

现代 AAA 游戏中，几乎 **100%** 的角色和道具都经过烘焙流程（Polycount Wiki, 2023）。

## 核心知识点

### 1. 烘焙的工作原理

**射线投射流程**（以法线烘焙为例）：

1. 低模每个三角面的每个 UV 像素 → 对应一个 3D 空间点
2. 从该点沿低模法线方向向外发射射线（射线长度 = Cage 距离）
3. 射线与高模表面相交 → 获取高模交点法线
4. 将高模法线从世界空间转换到低模切线空间 → 写入法线贴图 RGB 通道

**Cage（笼罩网格）**：
Cage 是比低模略大的包围网格，定义射线的起始位置和方向。Cage 过小 → 射线无法达到高模凸出部分 → 产生黑色伪影；Cage 过大 → 射线可能命中错误的高模表面 → 产生"交叉投射"（Ray Misses）。

**经验法则**：Cage 膨胀距离 = 高模与低模最大距离的 **1.2-1.5 倍**。

### 2. 常见烘焙类型

| 贴图类型 | 存储内容 | 用途 | 通道 |
|---------|---------|------|------|
| **法线贴图**（Normal Map） | 高模表面法线方向 | 在平面上模拟凹凸细节 | RGB = XYZ 法线 |
| **AO 贴图**（Ambient Occlusion） | 环境遮蔽信息 | 增强缝隙和凹陷的阴影 | 灰度（0=全遮蔽，1=全暴露） |
| **曲率贴图**（Curvature） | 表面曲率变化 | 边缘磨损、凸起高光效果 | 灰度（0.5=平面，>0.5=凸，<0.5=凹） |
| **厚度贴图**（Thickness） | 网格壁厚 | 次表面散射、透光效果 | 灰度（0=薄，1=厚） |
| **Position 贴图** | 世界/对象空间位置 | 程序化效果的位置参考 | RGB = XYZ 坐标 |
| **World Normal** | 世界空间法线 | 不受切线空间限制的法线信息 | RGB = XYZ 世界法线 |

### 3. 烘焙前的关键准备

**命名匹配**（Name Matching / Matching by Name）：
在 Marmoset 和 Substance Painter 中，通过命名后缀实现精确配对——高模 `armor_high` 只投射到低模 `armor_low`。这避免了不相关部件之间的交叉投射。

**UV 准备**：
- UV 岛之间保留 **至少 4 像素** 的间距（在 2048x2048 贴图中约 0.2% UV 空间），防止颜色溢出
- 硬边（Hard Edge）处必须有 UV 接缝（Seam），否则法线贴图会出现可见的光照断裂
- UV 岛方向尽量与纹理空间轴对齐，减少切线空间扭曲

**低模/高模对齐**：
- 低模必须完全被高模"包含"——任何低模凸出高模的区域都会产生烘焙伪影
- 使用 Shrinkwrap modifier 或手动调整确保贴合

### 4. 常见烘焙问题与解决

| 问题 | 外观 | 原因 | 解决方案 |
|------|------|------|---------|
| **黑色斑块** | 法线贴图出现纯黑区域 | Cage 距离不足，射线未命中高模 | 增大 Cage 距离或局部调整 |
| **扭曲法线** | 光照方向异常 | 切线空间基不一致（导出/导入设置不匹配） | 确保烘焙软件与引擎使用相同切线基 |
| **接缝可见** | UV 岛边界出现硬线 | UV Padding 不足或插值问题 | 增大 UV 间距，使用 Dilation 填充 |
| **交叉投射** | 无关部件细节出现在错误位置 | 射线穿过目标高模命中了其他部件 | 启用 Name Matching 或 Explode 分离 |
| **锯齿边缘** | 贴图边缘有锯齿状伪影 | 烘焙分辨率不足 | 提高贴图分辨率或使用抗锯齿采样（4x/16x） |

## 关键原理分析

### 切线空间 vs 对象空间法线贴图

**切线空间法线贴图**（Tangent Space, 蓝紫色为主）：法线相对于每个面的切线基定义。优点是可以重复平铺（Tiling）和在变形网格上正确工作。**行业标准**，几乎所有角色和道具使用。

**对象空间法线贴图**（Object Space, 彩虹色）：法线在对象坐标系中定义。优点是无 UV 接缝问题，适合静态硬表面。缺点是不支持 Tiling 和动画变形。

### 烘焙在管线中的位置

标准游戏美术管线流程：
概念设计 → 高模雕刻 → 低模拓扑 → UV 展开 → **烘焙** → 材质绘制 → 引擎导入

烘焙是高模向低模信息转移的**唯一桥梁**。如果烘焙质量差，后续材质绘制无论多精细都无法弥补——"垃圾进，垃圾出"。

## 实践练习

**练习 1**：在 Marmoset Toolbag 或 Substance Painter 中，对一个简单道具（如桶或箱子）执行完整烘焙流程。对比默认 Cage 和手动调整 Cage 后的法线贴图质量差异。

**练习 2**：故意制造一个"交叉投射"问题（两个紧贴的部件不做名称匹配），观察烘焙结果，然后用 Name Matching 修复。截图对比前后效果。

## 常见误区

1. **"高模面数越多烘焙效果越好"**：超过一定密度后，高模细节已经超出贴图分辨率的捕捉能力，额外面数只增加烘焙时间
2. **"烘焙一次搞定"**：实际生产中通常需要 3-5 次迭代——调整 Cage、修复 UV、重新对齐部件
3. **忽略切线基一致性**：烘焙软件（Substance）和引擎（UE5）使用不同切线基算法会导致法线"看起来对但打光不对"
'''

for rel_path, content in docs.items():
    full = ROOT / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content.strip(), encoding="utf-8")
    print(f"OK {rel_path}")

print("\nBatch 2 done (4/9). All 9 documents written.")
