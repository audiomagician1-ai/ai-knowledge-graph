---
id: "input-buffering"
concept: "输入缓冲"
domain: "game-engine"
subdomain: "input-system"
subdomain_name: "输入系统"
difficulty: 3
is_milestone: false
tags: ["格斗"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 输入缓冲

## 概述

输入缓冲（Input Buffer）是格斗游戏与动作游戏中一种专用的输入预存机制：当玩家在当前动作的执行帧期间提前按下下一条指令时，引擎将该指令记录在缓冲队列中，待当前动作进入**可取消窗口（Cancel Window）**或动作结束帧时，自动从队列中读取并执行该指令。其本质是将"精确到单帧的按键时机"扩展为"若干帧的容错时间窗口"。

输入缓冲最早在街机格斗游戏时代被系统化应用。Capcom 于 1991 年发布的《街头霸王 II》（Street Fighter II）引入了结构化的优先级指令队列，允许玩家在出招动画播放期间预录入下一次指令，从而让"连续技"（Combo）成为可稳定执行的技术而非纯粹的偶然。这一设计被后续的《拳皇》《铁拳》《任天堂明星大乱斗》等系列沿用并演进，成为动作类游戏输入系统设计的基础组件之一（参见 Treglia, 《Game Programming Gems 2》，Charles River Media，2001）。

格斗游戏的标准帧率为 60 FPS，每帧时长约 16.67 毫秒。高难度连段要求玩家在 2 至 6 帧（约 33 至 100 毫秒）的窗口内衔接下一个指令，远低于普通人反应时间的下限（约 150 至 200 毫秒）。输入缓冲将这个窗口延展至 3 至 15 帧不等，使高难度技术从"几乎不可能稳定执行"变为"通过练习可以掌握"，是平衡竞技深度与操作可及性的核心工具。

---

## 核心原理

### 缓冲队列的存储结构

输入缓冲在引擎层面通常以**循环数组（Ring Buffer）**实现。设缓冲窗口长度为 $N$ 帧，则分配一个长度为 $N$ 的定长数组，配备写指针 $w$ 与读指针 $r$，两者均以模 $N$ 方式递增：

$$w_{t+1} = (w_t + 1) \bmod N, \quad r_{t+1} = (r_t + 1) \bmod N$$

每一帧，引擎将当前帧的完整输入状态写入 $\text{buffer}[w]$，同时将 $w_{t-N}$ 位置的旧数据标记为过期。每条缓冲记录（InputRecord）通常包含以下字段：

- **ButtonMask**（uint16）：16 个按键的即时状态位掩码，1 表示该帧被按下。
- **DirectionCode**（uint8）：摇杆/方向键的离散化值，通常映射为 1–9 的数字方向（小键盘约定），0 表示无输入。
- **LifeCounter**（int8）：该条记录的剩余有效帧数，初始化为 $N$，每帧递减 1，归零后标记为 `EXPIRED`。
- **ConsumedFlag**（bool）：标记该条记录是否已被某次动作匹配消费，防止同一帧输入被重复触发。

以《街头霸王 V》的 5 帧缓冲为例，环形数组长度为 5，每帧写入一条记录，超出 5 帧的记录自动过期，确保玩家 6 帧前的操作不会在当前状态节点被意外消费。

### 指令匹配与优先级规则

缓冲读取并非逐帧轮询，而是在特定**状态节点（State Node）**触发一次完整的指令匹配扫描。这些节点包括：动作结束帧、Hit 确认帧（攻击命中后的 2–4 帧）、技能取消帧（普通攻击命中后允许接必杀的帧段）。

扫描时遵循严格的优先级顺序：

1. **超级必杀（Super / CA）** > **EX 必杀** > **普通必杀** > **普通攻击** > **移动指令**
2. 同级指令中，**完整序列匹配**（如 ↓↘→ + 拳）优先于**部分序列匹配**（如单独 → + 拳）
3. 时序更近的输入记录（LifeCounter 更大）优先于较早的记录

这套优先级规则解决了**指令子集冲突（Subset Collision）**问题。当玩家输入波动拳序列 ↓↘→ + 拳时，缓冲中同时存在方向 → 和拳键，若不加控制则可能被误判为"→ + 拳"（前冲重拳）。《街头霸王》系列的处理方案是：要求完整的方向序列必须在连续 $M$ 帧内录入（$M$ 通常为 10 至 15 帧），且序列中每个方向输入的间隔不得超过 $K$ 帧（$K \approx 8$），只有满足时序约束的完整序列才触发必杀，否则降级匹配更简单的指令。

### 缓冲窗口长度的设计权衡

缓冲窗口长度 $N$ 直接决定游戏的操作宽松程度，不同游戏有截然不同的取值：

| 游戏 | 缓冲窗口（帧） | 设计意图 |
|---|---|---|
| 《街头霸王 V》 | 3–5 帧 | 竞技向，维持高技术门槛 |
| 《拳皇 XV》 | 4 帧 | 兼顾连段复杂度与可操作性 |
| 《只狼：影逝二度》弹反 | 约 15 帧 | 弹反节奏偏慢，宽容窗口降低挫败感 |
| 《黑暗之魂》系列 | 约 12 帧 | 因过宽曾引发"幽灵翻滚攻击"问题 |
| 《超级任天堂明星大乱斗》 | 6 帧 | 派对向，操作宽松优先 |

窗口过长会产生**意外触发（Accidental Activation）**：玩家在执行翻滚或架势切换时随手按下的攻击键，会在缓冲中"存活"至下一个可取消节点并自动执行，打断玩家预期的防御节奏。《艾尔登法环》（2022 年）对《黑暗之魂》的这一问题进行了修正，缩短了特定动作的缓冲窗口，并引入了 `ConsumedFlag` 机制确保每条缓冲记录在一个取消窗口内最多被消费一次。

---

## 关键算法实现

以下是一个精简的 C++ 伪代码实现，展示循环缓冲区的写入、过期管理与优先级匹配逻辑：

```cpp
// 缓冲记录结构
struct InputRecord {
    uint16_t buttonMask;    // 按键位掩码
    uint8_t  directionCode; // 1-9 数字方向，0=无输入
    int8_t   lifeCounter;   // 剩余有效帧数，初始=BUFFER_SIZE
    bool     consumed;      // 是否已被消费
};

static const int BUFFER_SIZE = 5; // 《街头霸王V》风格：5帧窗口
InputRecord buffer[BUFFER_SIZE];
int writeHead = 0;

// 每帧调用：写入当前帧输入并衰减所有记录的 LifeCounter
void TickBuffer(uint16_t buttons, uint8_t direction) {
    // 写入新记录
    buffer[writeHead] = { buttons, direction, BUFFER_SIZE, false };
    writeHead = (writeHead + 1) % BUFFER_SIZE;

    // 衰减所有记录的存活计数
    for (int i = 0; i < BUFFER_SIZE; ++i) {
        if (buffer[i].lifeCounter > 0)
            buffer[i].lifeCounter--;
    }
}

// 在取消窗口内调用：按优先级扫描缓冲，返回可执行的最高优先级动作ID
ActionID ConsumeBuffer(const PriorityList& actions) {
    for (const auto& action : actions) { // actions 已按优先级降序排列
        for (int i = 0; i < BUFFER_SIZE; ++i) {
            InputRecord& rec = buffer[i];
            if (rec.lifeCounter > 0 && !rec.consumed
                && action.Matches(rec.buttonMask, rec.directionCode)) {
                rec.consumed = true;
                return action.id;
            }
        }
    }
    return ACTION_NONE;
}
```

该实现的时间复杂度为 $O(P \cdot N)$，其中 $P$ 为优先级列表长度，$N$ 为缓冲窗口帧数。由于 $P$ 通常不超过 30，$N$ 不超过 15，单次匹配的开销可忽略不计。

---

## 实际应用

### 格斗游戏的连段辅助

在《街头霸王 V》中，技能取消（Special Cancel）的工作流程如下：玩家按下普通攻击（如 5MP，站立中拳），攻击动画在第 6 帧进入 Hit 确认帧；若在第 3 至 5 帧内已预录入了波动拳序列（↓↘→ + 拳），缓冲中的记录此时 LifeCounter 仍 > 0，系统在 Hit 确认帧触发取消扫描，匹配到波动拳指令并执行，完成"5MP → 波动拳"连段。

若没有输入缓冲，玩家必须在第 6 帧的 16.67 毫秒内完成按键，而人类平均简单反应时间约为 200 毫秒，稳定执行几乎不可能。引入 5 帧缓冲后，有效操作窗口扩展至约 83 毫秒，高水平玩家通过练习可以稳定掌握。

### 动作 RPG 的预输入设计

《只狼：影逝二度》（FromSoftware，2019 年）将弹反（Deflect）的输入缓冲设置为约 15 帧，这一决策基于游戏节奏的特殊性：忍义手格挡动作本身有 8 帧的前摇，玩家需要提前预判敌人攻击，15 帧缓冲恰好覆盖了"预判按键"到"格挡前摇结束"之间的时间差。相比之下，《只狼》的追击跳跃（Mikiri Counter）缓冲窗口仅约 6 帧，因为该动作的视觉反馈更明确，无需过长缓冲。

### 平台跳跃游戏的跳跃缓冲

输入缓冲同样广泛用于平台游戏的跳跃系统。《蔚蓝》（Celeste，2018 年，Maddy Thorson & Noel Berry）实现了两种缓冲机制：
- **跳跃缓冲（Jump Buffer）**：玩家在落地前 6 帧内按下跳跃键，落地瞬间自动起跳，消除"刚好落地时按键偏早"的挫败感。
- **土狼时间（Coyote Time）**：角色离开平台边缘后，在 6 帧内仍可执行跳跃，弥补玩家反应延迟。

这两种机制在代码层面均以输入缓冲的形式实现，本质上与格斗游戏的缓冲队列相同，只是 $N$ 值和匹配条件有所差异。

---

## 常见误区

### 误区一：输入缓冲越长越好

更长的缓冲窗口并不意味着更好的游戏体验。《黑暗之魂》系列的约 12 帧缓冲曾导致玩家反复遇到"翻滚结束后意外触发攻击"的问题——玩家在翻滚过程中下意识按下攻击键以准备反击，但该输入被缓冲保存，在翻滚结束帧自动消费，使角色立刻出招而无法进行第二次翻滚闪避。这一问题在社区中被称为 **"Ghost Input（幽灵输入）"**，是缓冲窗口过长的典型负面案例。

### 误区二：缓冲输入等同于输入延迟（Input Lag）

输入缓冲与输入延迟是两个完全不同的概念。输入延迟是指从玩家按键到屏幕呈现反馈的时间差（通常由显示器刷新率、渲染管线和网络延迟决定），它总是使响应变慢。输入缓冲则是在当前动作无法被打断时暂存指令，在动