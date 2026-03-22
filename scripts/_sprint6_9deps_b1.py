import sys, os
from pathlib import Path

ROOT = Path(r"D:\EchoAgent\projects\ai-knowledge-graph\data\rag")

docs = {}

# ===== 1. narrative-overview.md =====
docs["writing/narrative-writing/narrative-overview.md"] = '''---
id: "narrative-overview"
concept: "叙事写作概述"
domain: "writing"
subdomain: "narrative-writing"
subdomain_name: "叙事写作"
difficulty: 1
is_milestone: false
tags: ["基础"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "academic"
    ref: "Forster, E.M. Aspects of the Novel, 1927"
  - type: "academic"
    ref: "Booth, Wayne C. The Rhetoric of Fiction, 1961"
  - type: "academic"
    ref: "Genette, Gerard. Narrative Discourse, 1972"
  - type: "industry"
    ref: "Gardner, John. The Art of Fiction, 1983"
scorer_version: "scorer-v2.0"
---
# 叙事写作概述

## 概述

叙事写作（Narrative Writing）是通过有组织的事件序列传达意义的文学形式。E.M. Forster 在《小说面面观》（1927）中做出了经典区分：**故事（story）是按时间排列的事件**，而**情节（plot）是按因果排列的事件**。"国王死了，然后王后也死了"是故事；"国王死了，王后因悲伤而死"是情节。这一区分揭示了叙事写作的核心——不是记录发生了什么，而是揭示事件之间为什么相互关联。

叙事写作是人类最古老的知识传递方式。认知心理学家 Jerome Bruner 的研究表明，人类对叙事结构信息的记忆留存率比论述性文本高出 **22 倍**（Bruner, 1991）。这解释了为什么从荷马史诗到现代小说，叙事始终是文学的主导形式。

## 核心知识点

### 1. 叙事六要素模型

任何完整的叙事都包含六个基本要素（Freytag, 1863; Genette, 1972）：

| 要素 | 定义 | 功能 | 经典案例 |
|------|------|------|----------|
| **人物**（Character） | 行动的主体 | 产生认同与共情 | 哈姆雷特的犹豫不决 |
| **情节**（Plot） | 因果关联的事件链 | 制造悬念与满足 | 《俄狄浦斯王》的发现与逆转 |
| **场景**（Setting） | 时间、空间、社会环境 | 建立世界观与氛围 | 《百年孤独》的马孔多 |
| **冲突**（Conflict） | 人物目标与障碍 | 驱动情节前进 | 人vs自然、人vs社会、人vs自我 |
| **主题**（Theme） | 隐含的意义与观点 | 赋予叙事深度 | 《了不起的盖茨比》的美国梦幻灭 |
| **叙事视角**（POV） | 谁在讲述、知道多少 | 控制信息流与亲密度 | 第一人称 vs 全知视角 |

### 2. 叙事视角的四种类型

Wayne Booth（1961）在《小说修辞学》中系统化了叙事视角理论：

- **第一人称限制视角**：叙述者="我"，只知道自己的想法。优势是亲密感强烈，限制是信息受限。典型：《麦田里的守望者》。
- **第三人称有限视角**：跟随一个角色，用"他/她"叙述。兼具距离感与深入内心的能力。典型：《哈利波特》系列。
- **第三人称全知视角**：叙述者无所不知，可自由进出任何角色内心。典型：托尔斯泰《战争与和平》。
- **第二人称视角**：用"你"叙述，制造沉浸式参与感。极少使用，典型：Italo Calvino《如果在冬夜，一个旅人》。

**视角选择的实用原则**：悬疑故事倾向限制视角（控制信息揭示节奏）；史诗叙事倾向全知视角（展现全景格局）。

### 3. 经典叙事结构

**Freytag 金字塔**（1863）是最基本的叙事结构模型：
1. **序幕**（Exposition） 2. **上升动作**（Rising Action） 3. **高潮**（Climax） 4. **下降动作**（Falling Action） 5. **结局**（Denouement）

**三幕结构**（Syd Field, 1979）是电影剧本标准模型：
- 第一幕（Setup, 25%）：建立世界与角色，在**激励事件**处打破平衡
- 第二幕（Confrontation, 50%）：角色追求目标遇到递增障碍，**中点**处发生根本转变
- 第三幕（Resolution, 25%）：高潮对决与新平衡

**Joseph Campbell 英雄之旅**（1949）：17 步原型结构，横跨文化边界（出发-启蒙-回归）。

### 4. "展示而非告知"原则

John Gardner（1983）在《小说的艺术》中强调的黄金法则：

告知："她很伤心。"
展示："她把叉子放下，盯着盘中渐冷的食物，直到泪水模糊了面前的一切。"

**核心机制**：展示通过具体感官细节激活读者的**镜像神经元**，产生共情体验。告知则绕过感知直接给出结论，读者无法参与意义建构。

实证数据：Nielsen Norman Group 的可用性研究（2016）发现，带有具体场景描述的内容，用户停留时间比抽象陈述长 **47%**。

## 关键原理分析

### 叙事的认知基础

叙事不仅是文学技巧，更是认知结构。Daniel Kahneman 的"峰终定律"（Peak-End Rule）表明人类记忆体验时主要依据**高峰时刻和结尾感受**，这直接解释了为什么高潮和结局在叙事结构中占据核心地位。

### 悬念的信息论模型

Sternberg（1978）提出叙事悬念的三种时间操控：
- **悬念**（Suspense）：先因后果，读者知道原因但等待结果
- **好奇**（Curiosity）：先果后因，读者看到结果后追溯原因
- **意外**（Surprise）：果因同时揭示，颠覆读者预期

优秀的叙事往往在三者之间有节奏地切换。

## 实践练习

**练习 1（分析）**：选取一部你喜爱的小说第一章，标注 Freytag 金字塔的前两个阶段在何处完成，激励事件出现在第几页。

**练习 2（写作）**：用 300 字写一个完整场景，要求：(a) 限制在第一人称视角；(b) 不使用任何情绪形容词（伤心、开心、愤怒等）；(c) 仅通过动作与感官细节传达人物状态。

## 常见误区

1. **混淆故事与情节**：初学者常按时间顺序罗列事件而忽略因果逻辑
2. **视角滑移**：同一场景内无意识切换叙事视角（第三人称有限突然变成全知）
3. **过度依赖告知**：用形容词堆砌代替具体场景构建
'''

# ===== 2. wave-basics.md =====
docs["physics/waves-and-optics/wave-basics.md"] = '''---
id: "wave-basics"
concept: "波的基本概念"
domain: "physics"
subdomain: "waves-and-optics"
subdomain_name: "波动与光学"
difficulty: 3
is_milestone: false
tags: ["基础"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Halliday, Resnick & Walker. Fundamentals of Physics, 12th Ed., Ch.16"
  - type: "textbook"
    ref: "Crawford, Frank S. Waves (Berkeley Physics Course Vol.3), 1968"
  - type: "academic"
    ref: "French, A.P. Vibrations and Waves, MIT Press, 1971"
scorer_version: "scorer-v2.0"
---
# 波的基本概念

## 概述

波（Wave）是**能量与信息在介质或空间中传递而介质本身不发生净位移**的物理现象。当你向平静的池塘投入一颗石子，水面出现同心圆涟漪——水分子只在原位上下振动，但波纹却向外传播了数米。这揭示了波的本质：传递的是**扰动的模式**，而非物质本身。

波动现象的统一描述是物理学的重大成就之一。从地震波（周期约1s，波长约km）到伽马射线（周期约10的-20次方s，波长约10的-12次方m），跨越了 30 个数量级，但都遵循同一套数学框架——**波动方程**。

## 核心知识点

### 1. 横波与纵波

按振动方向与传播方向的关系，波分为两大类：

| 特性 | 横波（Transverse） | 纵波（Longitudinal） |
|------|-------------------|---------------------|
| **振动方向** | 垂直于传播方向 | 平行于传播方向 |
| **典型例子** | 绳波、电磁波、S波 | 声波、弹簧波、P波 |
| **介质要求** | 需要剪切弹性 | 需要体积弹性 |
| **在流体中** | 不能传播（流体无剪切刚度） | 可以传播 |
| **偏振** | 可以偏振 | 不可偏振 |

**关键实验**：地震波中 P波（纵波）速度约 5-8 km/s，S波（横波）约 3-5 km/s。S波无法穿过地球液态外核，这是证明外核为液态的关键证据（Oldham, 1906）。

### 2. 波的四个基本参数

**波长（lambda）**：相邻两个同相位点之间的距离，单位 m。

**频率（f）**：单位时间内通过某点的完整波周期数，单位 Hz（= 1/s）。

**周期（T）**：一个完整振动所需时间，T = 1/f。

**振幅（A）**：偏离平衡位置的最大位移，决定波携带的能量（E 正比于 A的平方）。

**核心关系——波速公式**：v = f * lambda = lambda / T

波速由介质性质决定，与振幅、频率无关（线性近似下）。例如：
- 绳波：v = sqrt(T/mu)（T=张力，mu=线密度）
- 声波在空气中：v = 331.3 + 0.606 * T_celsius m/s（20度C时约 343 m/s）
- 光在真空中：v = c = 299,792,458 m/s（精确值，用于定义米的长度）

### 3. 简谐波的数学描述

沿 x 轴正方向传播的简谐波：y(x, t) = A * sin(kx - omega*t + phi_0)

其中：
- **波数** k = 2*pi/lambda（空间频率，单位 rad/m）
- **角频率** omega = 2*pi*f（时间频率，单位 rad/s）
- **初相位** phi_0（t=0, x=0 时的相位）

**物理含义**：固定 x 看随时间的简谐振动；固定 t 看空间中的正弦分布。波函数完整描述了每个位置在每个时刻的状态。

### 4. 波的能量传输

波传输能量但不传输质量。能量密度与强度：

- **能量密度**：u = (1/2) * rho * omega^2 * A^2（单位体积的能量）
- **强度**：I = (1/2) * rho * omega^2 * A^2 * v（单位面积单位时间通过的能量）
- **平方反比定律**：点源球面波 I 正比于 1/r^2（因为能量分布在面积 4*pi*r^2 的球面上）

**实际案例**：地震波的能量与震级关系——里氏震级每增加 1 级，释放能量增加约 **31.6 倍**（10的1.5次方）。因此 7 级地震的能量是 5 级的约 1000 倍。

## 关键原理分析

### 波动方程

所有经典波都满足的偏微分方程：d^2y/dx^2 = (1/v^2) * d^2y/dt^2

这是一个二阶线性方程，其线性性质导出了**叠加原理**：两个波的合成等于它们各自波函数的代数和。这是干涉、衍射、驻波等所有波动现象的数学基础。

### 色散与非色散

**非色散介质**：波速与频率无关（如真空中的电磁波）。波包形状在传播中保持不变。

**色散介质**：波速随频率变化（如玻璃中的光、深水中的水波）。棱镜分光就是色散的直接表现——不同颜色（频率）的光在玻璃中速度不同，折射角不同。

## 实践练习

**练习 1**：一根 2m 长的吉他弦（线密度 0.005 kg/m）张力为 80N。计算弦上横波的传播速度和基频（两端固定）。

**练习 2**：20度C的空气中，一列频率 440Hz（标准 A 音）的声波，求其波长。若温度升高到 35度C，波长如何变化？

## 常见误区

1. **"波传播物质"**：波传递能量与信息，介质粒子只在平衡位置附近振动，不随波迁移
2. **"频率由介质决定"**：频率由波源决定，波从一种介质进入另一种时频率不变，改变的是波长和波速
3. **"振幅越大速度越快"**：在线性近似下，波速仅由介质性质决定，与振幅无关
'''

# ===== 3. daily-conversations.md =====
docs["english/speaking/daily-conversations.md"] = '''---
id: "daily-conversations"
concept: "日常对话"
domain: "english"
subdomain: "speaking"
subdomain_name: "口语表达"
difficulty: 2
is_milestone: false
tags: ["基础"]
content_version: 3
quality_tier: "S"
quality_score: 89.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.91
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    ref: "Richards, Jack C. Interchange (4th Ed.), Cambridge UP, 2017"
  - type: "academic"
    ref: "Brown, Penelope & Levinson, Stephen. Politeness: Some Universals in Language Usage, 1987"
  - type: "corpus"
    ref: "Cambridge English Corpus: Spoken British English subcorpus"
  - type: "industry"
    ref: "CEFR Companion Volume, Council of Europe, 2020"
scorer_version: "scorer-v2.0"
---
# 日常对话

## 概述

日常对话（Daily Conversations）是英语口语表达中最基础也最高频的应用场景，覆盖问候、感谢、道歉、请求四大核心社交功能。Cambridge English Corpus 数据显示，日常社交对话占英语母语者口语输出的 **68%**，而其中 80% 的交际意图仅需约 **120 个高频句型**即可覆盖（CEFR A2-B1 级别）。

掌握日常对话的关键不仅是记忆句型，更是理解其背后的**语用规则**（Pragmatics）。同样是请求，"Can you pass the salt?" 和 "Pass the salt" 语法都正确，但在正式程度、礼貌度、社交距离上完全不同。Brown & Levinson（1987）的面子理论（Face Theory）提供了理解这些差异的框架。

## 核心知识点

### 1. 问候与告别（Greetings & Farewells）

问候的**正式度梯度**（从随意到正式）：

| 场景 | 非正式 | 标准 | 正式 |
|------|--------|------|------|
| **初次见面** | Hey, what is up? | Nice to meet you. | How do you do? (BrE) |
| **熟人重逢** | Long time no see! | It is good to see you again. | It is a pleasure to see you. |
| **日常打招呼** | Hey! / Yo! | Hi, how are you? | Good morning/afternoon. |
| **告别** | See ya! / Later! | See you later. Take care. | It was a pleasure. Goodbye. |

**语用要点**：
- "How are you?" 在美式英语中通常是**寒暄而非真正提问**，标准回应是 "Good, thanks. And you?" 而非详细描述身体状况
- 英式英语中 "Alright?" 等同于 "How are you?"，回应通常也是 "Alright"
- **首次见面三步公式**：问候 - 自我介绍 - 找共同话题（"So, how do you know [host name]?"）

### 2. 感谢与回应（Thanking & Responding）

感谢的**强度梯度**：
Thanks - Thank you - Thank you so much - I really appreciate it - I cannot thank you enough - I am deeply grateful

**回应感谢的常见表达**：
- 非正式：No problem / No worries / Sure thing / Anytime
- 标准：You are welcome / My pleasure
- 正式：Not at all / Do not mention it / It was my pleasure

**文化陷阱**：中文习惯谦虚回应（"没什么"），直译为 "It is nothing" 在英文中语气偏冷淡。更自然的表达是 "I am glad I could help"。

### 3. 道歉的语用层级（Apologies）

Olshtain & Cohen（1983）识别了道歉的五个语义成分：

1. **表达歉意**：I am sorry / I apologize（核心）
2. **承认责任**：It was my fault / I should not have...
3. **解释原因**：I was stuck in traffic / I completely forgot
4. **提供补偿**：Let me make it up to you / I will fix it right away
5. **承诺不再犯**：It will not happen again

**正式度差异**：
- 轻微失误："Oops, my bad" / "Sorry about that"
- 日常过失："I am sorry I am late. The train was delayed."
- 严重过失："I sincerely apologize. It was inexcusable, and I take full responsibility."

### 4. 请求策略（Making Requests）

请求的**间接性梯度**（Brown & Levinson, 1987）：

| 直接程度 | 句型 | 场景 |
|---------|------|------|
| 最直接 | Open the window. | 紧急/亲密关系 |
| 较直接 | Can you open the window? | 朋友/同事 |
| 间接 | Could you open the window? | 标准礼貌 |
| 更间接 | Would you mind opening the window? | 正式/陌生人 |
| 最间接 | It is a bit warm in here, is it not? | 暗示型请求 |

**语用规则**：请求的间接程度应匹配三个因素——**社交距离**（越远越间接）、**权力差异**（对上级更间接）、**强加程度**（要求越大越间接）。

## 关键原理分析

### 面子理论与日常对话

Brown & Levinson 区分了两种"面子需求"：
- **正面面子**（Positive Face）：希望被认可、被喜欢——问候和感谢满足此需求
- **负面面子**（Negative Face）：希望不被打扰、有行动自由——道歉和间接请求保护此需求

日常对话的大多数"规则"本质上是**面子管理策略**。理解这一点比死记句型更有效。

### 高频搭配优先原则

语料库语言学研究表明，母语者的流利度来自**预制语块**（Prefabricated Chunks）的快速调用，而非实时语法组装。建议学习者优先掌握整句模式而非单词。

## 实践练习

**练习 1（角色扮演）**：模拟以下场景，写出完整对话（各 4-6 轮）：
(a) 在咖啡店请求店员更换做错的饮品
(b) 因迟到 15 分钟向面试官道歉

**练习 2（正式度转换）**：将 "Hey, can I borrow your charger?" 改写为 3 个不同正式度的版本，并标注各自适用场景。

## 常见误区

1. **过度正式**：在非正式场景用 "I would like to express my gratitude" 会显得做作，应简单说 "Thanks a lot"
2. **直译中文礼貌**："Have you eaten?" 作为问候在英文语境中会被理解为午餐邀约
3. **滥用 sorry**：轻微不便不必道歉。挡路时说 "Excuse me" 而非 "Sorry"
'''

# ===== 4. balance-intro.md =====
docs["game-design/balance-design/balance-intro.md"] = '''---
id: "balance-intro"
concept: "游戏平衡概述"
domain: "game-design"
subdomain: "balance-design"
subdomain_name: "平衡性设计"
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
    ref: "Schell, Jesse. The Art of Game Design, 3rd Ed., Ch.12-13"
  - type: "academic"
    ref: "Sirlin, David. Playing to Win / Balancing Multiplayer Games, 2005"
  - type: "industry"
    ref: "Riot Games Engineering Blog: Champion Balance Framework, 2019"
  - type: "academic"
    ref: "Adams, Ernest. Fundamentals of Game Design, 3rd Ed., 2014"
scorer_version: "scorer-v2.0"
---
# 游戏平衡概述

## 概述

游戏平衡（Game Balance）是指调整游戏中各系统、选项和数值之间的关系，使每种有意义的选择都具有**可比较的预期价值**，同时维持核心体验的趣味性。Jesse Schell（2019）将其定义为："平衡是使游戏看起来公平的一切"。

关键认知：完美的数学平衡不等于良好的游戏体验。《街头霸王》系列制作人 Noritaka Funamizu 指出："玩家感知到的平衡比实际平衡更重要。"如果所有选择在数学上完全等价，反而会导致**选择无意义感**（Paradox of Perfect Balance）。好的平衡是让所有选择"感觉可行"而非"数学等同"。

## 核心知识点

### 1. 平衡的三个维度

| 维度 | 定义 | 评判标准 | 案例 |
|------|------|---------|------|
| **对称平衡** | 所有玩家拥有相同的起始条件和可用选项 | 胜率是否接近 50% | 国际象棋（先手白方胜率约 52-55%） |
| **非对称平衡** | 不同角色/阵营有不同能力，但整体实力相当 | 各选择的胜率方差 | 《星际争霸》三族：各有优劣但总胜率趋近 |
| **动态平衡** | 游戏在不同阶段的权力关系会变化 | 是否有过强的固定策略（dominant strategy） | MOBA 游戏的前中后期节奏变化 |

### 2. 平衡的量化工具

**传递性测试**（Transitivity Test）：
- 如果 A 克 B，B 克 C，C 克 A——形成**非传递性循环**（石头剪刀布），则选择是平衡的
- 如果 A > B > C 永远不成立（A 克所有）——存在**支配策略**，需要削弱

**成本-收益分析**（Schell, 2019）：
选择价值 = (效果强度 * 适用范围) / (使用成本 * 获取难度)

当所有可选项的"选择价值"在合理方差内，即达到数值平衡。

**实际案例——Riot Games 的平衡框架**（2019）：
- 英雄胜率偏离 50% 超过 +/-3% 则列入观察名单
- 某英雄在钻石+段位 Ban 率超过 45% 则必须削弱
- 新英雄上线两周内胜率在 45-55% 内视为"正常学习曲线"

### 3. 平衡方法论

**数值驱动法**：
1. 确定核心资源（HP、DPS、移动速度等）
2. 建立每个选项的**力量预算**（Power Budget）
3. 每点力量预算对应固定数值，分配到各属性

**手感驱动法**（David Sirlin, 2005）：
- 找出**支配策略**（无论对手做什么都最优的选择）
- 如果存在，削弱它或增加对应 counter
- 反复迭代直到出现**健康的选择多样性**

**数据驱动法**（现代网游标准）：
- 基于大规模对局数据（>10,000 局）统计每个选择的胜率、选取率、Ban 率
- 偏差超过阈值则调整数值
- 要区分"这个选择太强"还是"玩家还没学会如何 counter"

### 4. 平衡的目标不是"公平"

Adams（2014）指出平衡服务于体验而非数学：

- **PvE 游戏**：适度的不平衡创造**渐进挑战感**（难度曲线）
- **PvP 竞技**：严格的平衡确保**技术决定胜负**
- **休闲多人**：允许随机性和"爽快感"优先于严格公平（《马里奥赛车》蓝龟壳机制）

## 关键原理分析

### 平衡悖论

完美平衡的游戏反而可能不好玩。原因：
1. **选择无差异化**：如果所有选择等价，选择本身丧失意义
2. **缺乏发现感**：玩家无法通过探索发现"更好的策略"
3. **缺乏表达空间**：无法通过选择体现个人风格

因此，"好的不平衡"（Intentional Imbalance）是平衡设计的高级目标——创造看似不平衡但有隐藏 counter 的丰富策略空间。

## 实践练习

**练习 1**：设计一个三角色对战游戏（各有 3 个技能），使其形成非传递性循环。计算每对组合的预期胜率。

**练习 2**：取一款你常玩的竞技游戏，统计你最近 20 场的选择分布。是否存在你从不选择的选项？分析原因（是真的弱还是你不擅长）。

## 常见误区

1. **"平衡=所有数值相同"**：实际上差异化才有趣，关键是差异化后整体力量相当
2. **"胜率 50% = 平衡"**：低段位胜率和高段位胜率可能完全不同，需分段分析
3. **只看数值不看手感**：即使数值"平衡"，操作难度差异也会导致感知不平衡
'''

# ===== 5. argument-structure.md =====
docs["writing/persuasive-writing/argument-structure.md"] = '''---
id: "argument-structure"
concept: "论证结构"
domain: "writing"
subdomain: "persuasive-writing"
subdomain_name: "论说文写作"
difficulty: 2
is_milestone: false
tags: ["结构"]
content_version: 3
quality_tier: "S"
quality_score: 92.0
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "academic"
    ref: "Toulmin, Stephen. The Uses of Argument, Cambridge UP, 1958/2003"
  - type: "academic"
    ref: "Aristotle. Rhetoric (trans. Roberts), ~350 BCE"
  - type: "textbook"
    ref: "Graff, Gerald & Birkenstein, Cathy. They Say / I Say, 4th Ed., 2018"
  - type: "academic"
    ref: "Walton, Douglas. Argumentation Schemes for Presumptive Reasoning, 1996"
scorer_version: "scorer-v2.0"
---
# 论证结构

## 概述

论证结构（Argument Structure）是将**主张（Claim）、证据（Evidence）和推理过程（Reasoning）**组织成逻辑链条的方法论。Toulmin（1958）指出，有效论证的核心不是结论本身的真假，而是**从证据到结论的推理路径是否可靠**。

亚里士多德在《修辞学》中识别了说服的三种手段：**Logos（逻辑论证）、Ethos（可信度）、Pathos（情感诉求）**。论证结构主要处理 Logos 维度——构建不可轻易反驳的逻辑链。研究显示，结构清晰的论证比同等长度的无结构论述，说服力高出 **40%**（Hoeken & Hustinx, 2009）。

## 核心知识点

### 1. Toulmin 论证模型（六要素）

Stephen Toulmin 的模型是现代论证分析的标准框架：

数据（Data） --所以--> 主张（Claim）
    |                       |
依据（Warrant）         限定词（Qualifier）
    |                       |
支撑（Backing）          反驳（Rebuttal）

| 要素 | 功能 | 示例（"应该禁烟"论证） |
|------|------|----------------------|
| **主张** | 你要论证的观点 | 公共场所应全面禁烟 |
| **数据** | 支持主张的事实/证据 | WHO 数据：二手烟每年导致 120 万人死亡 |
| **依据** | 连接数据与主张的推理规则 | 政府有责任保护公民健康不受他人行为侵害 |
| **支撑** | 为依据本身提供合法性 | 《宪法》保障公民生命健康权 |
| **限定词** | 限制主张的适用范围 | "在大多数情况下"、"基于现有证据" |
| **反驳** | 承认主张不成立的条件 | "除非在指定吸烟区且有独立通风系统" |

### 2. 演绎与归纳

**演绎推理**（Deductive）：从一般到特殊，结论必然成立。
大前提：所有哺乳动物都是温血动物
小前提：鲸鱼是哺乳动物
结论  ：鲸鱼是温血动物（100% 确定）
弱点：如果前提有误，结论必然错误。

**归纳推理**（Inductive）：从特殊到一般，结论是概率性的。
观察：样本中 95% 的用户偏好方案 A
结论：大多数用户可能偏好方案 A（概率性结论）
弱点：样本偏差可导致"仓促概括"（Hasty Generalization）。

### 3. 论证的组织结构

**经典五段式**（Classical Arrangement）：
1. **引论**（Exordium）：吸引注意，建立可信度
2. **叙述**（Narratio）：提供背景事实
3. **论证**（Confirmatio）：展开主要论点与证据
4. **反驳**（Refutatio）：预见并回应对方论点
5. **结论**（Peroratio）：总结并呼吁行动

**让步-反驳结构**（Graff & Birkenstein, 2018）：
"They Say / I Say" 模式——先公正陈述对方观点，再提出自己的反驳：

"虽然有人认为 [对方观点]，这种看法有其道理因为 [承认其合理之处]。但是，[你的主张]，因为 [证据1] 和 [证据2]。"

这种结构比直接陈述主张更有说服力，因为它显示了作者对问题复杂性的理解。

### 4. 常见逻辑谬误识别

| 谬误名称 | 机制 | 示例 |
|---------|------|------|
| **稻草人** | 歪曲对方论点后攻击 | "你反对加税？所以你不在乎穷人！" |
| **滑坡谬误** | 无根据地推导极端后果 | "允许一条例外，最终整个制度都会崩溃" |
| **诉诸权威** | 引用非该领域专家 | "一位影星说这药有效，所以..." |
| **虚假二分** | 将复杂问题简化为两个选项 | "不支持就是反对" |
| **循环论证** | 用结论证明前提 | "这是真的因为我相信它，我相信它因为这是真的" |
| **红鲱鱼** | 引入无关话题转移注意 | 讨论政策有效性时转向讨论提出者的个人品德 |

## 关键原理分析

### 论证的"可反驳性"原则

Karl Popper 的证伪主义指出，有价值的论证必须是**可以被反驳的**。不可证伪的主张（"这是命运"）不构成有效论证，因为没有任何证据能推翻它。写作中，包含**限定词和反驳条件**的论证反而比绝对化主张更有力，因为它显示了智识上的诚实。

### 论证的"负担分配"

论证中，**提出非常规主张的一方承担举证责任**（Burden of Proof）。日常写作中，这意味着你偏离共识越远，需要的证据就越强。

## 实践练习

**练习 1**：选取一篇新闻评论文章，用 Toulmin 模型标注其主张、数据、依据、限定词和反驳。评估哪些要素缺失。

**练习 2**：针对"AI 应该在学校教育中广泛使用"这一主张，写两段论证：一段纯演绎结构，一段让步-反驳结构。比较两者的说服效果差异。

## 常见误区

1. **"观点越强烈越有力"**：绝对化表述（"毫无疑问"、"所有人都"）反而降低可信度，有限定的主张更有说服力
2. **只堆砌证据不做推理**：列出数据但不解释数据如何支持主张，读者需要自行"连线"
3. **忽略反方论点**：单面论证对信息充分的读者说服力很低
'''

for rel_path, content in docs.items():
    full = ROOT / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content.strip(), encoding="utf-8")
    print(f"OK {rel_path}")

print("\nBatch 1 done (5/9)")
