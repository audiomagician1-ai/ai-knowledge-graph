---
id: "se-game-loop"
concept: "游戏循环"
domain: "software-engineering"
subdomain: "game-programming-patterns"
subdomain_name: "游戏编程模式"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 游戏循环

## 概述

游戏循环（Game Loop）是游戏程序持续运行的核心驱动机制，其本质是一个在游戏运行期间反复执行"处理输入→更新状态→渲染画面"三步骤的无限循环结构。与普通事件驱动程序不同，游戏循环不等待用户输入，而是主动以尽可能快的速度或以固定节拍推进游戏世界的时间。

游戏循环的概念随着早期电子游戏的诞生而出现。1962年的《太空战争！》（Spacewar!）已经隐含了类似结构，而1980年代街机硬件通常依靠垂直消隐中断（VBlank Interrupt）强制以60Hz锁帧更新，这是游戏循环的硬件对应物。随着PC游戏在1990年代普及，软件层面的游戏循环才被显式设计和讨论，Chris Crawford在1982年的《电子游戏设计的艺术》中率先对此结构进行了系统描述。

游戏循环的设计直接决定游戏的物理模拟精度、帧率稳定性与跨平台一致性。一款物理引擎如果以可变帧率更新碰撞检测，在低帧率机器上子弹可能"穿墙"——这是游戏循环时间步长设计失误造成的具体后果。

## 核心原理

### 固定时间步长（Fixed Timestep）

固定时间步长模式下，每次循环迭代的逻辑更新量 `dt` 为常量，通常设为 `1/60` 秒（约16.67ms）或 `1/50` 秒。其伪代码结构为：

```
while (running) {
    processInput();
    update(FIXED_DT);   // FIXED_DT = 1.0/60.0
    render();
}
```

优点是物理模拟结果具有确定性（Determinism），相同输入序列在任何机器上产生完全相同的游戏状态，这对联机同步（如RTS游戏的帧同步方案）至关重要。缺点是渲染帧率与逻辑帧率强制绑定：若渲染耗时超过16.67ms，游戏会整体变慢，产生"慢动作"效果而非丢帧。

### 可变时间步长（Variable Timestep）

可变时间步长将上一帧实际经过的真实时间作为 `dt` 传入更新函数：

```
double lastTime = getCurrentTime();
while (running) {
    double now = getCurrentTime();
    double dt = now - lastTime;
    lastTime = now;
    processInput();
    update(dt);
    render();
}
```

这使游戏在不同性能设备上都能以"真实时间"推进，60fps机器和30fps机器上角色移动的物理距离相同。然而当 `dt` 过大时（例如调试时打断点导致 `dt` = 5秒），游戏对象可能瞬移或穿越碰撞体。通常需要加入 `dt = min(dt, MAX_DT)` 的截断保护，`MAX_DT` 常设为 `0.25` 秒。

### 半固定时间步长（Semi-Fixed / Decoupled Timestep）

半固定时间步长由Glenn Fiedler在2004年的文章《Fix Your Timestep!》中系统提出，是目前专业引擎（如Unity的物理子系统、Godot的`_physics_process`）的主流方案。其核心思想是将逻辑更新帧率与渲染帧率解耦：

```
double accumulator = 0.0;
const double FIXED_DT = 1.0 / 60.0;

while (running) {
    double frameTime = getRealDeltaTime();
    accumulator += frameTime;
    
    while (accumulator >= FIXED_DT) {
        update(FIXED_DT);      // 以固定步长多次或不执行
        accumulator -= FIXED_DT;
    }
    
    double alpha = accumulator / FIXED_DT;  // 渲染插值因子
    renderWithInterpolation(alpha);
}
```

变量 `alpha`（范围0到1）用于在当前帧状态与上一帧状态之间做线性插值，使渲染画面在逻辑帧之间保持流畅，彻底分离了"游戏逻辑更新频率"与"画面刷新频率"两个维度。

## 实际应用

**Unity引擎的双循环设计**：Unity将游戏循环拆分为`Update()`（可变dt，处理输入和游戏逻辑）与`FixedUpdate()`（固定50Hz，即`Time.fixedDeltaTime = 0.02s`，处理物理）。`FixedUpdate`的底层实现正是半固定时间步长的accumulator模式，因此Rigidbody的移动必须写在`FixedUpdate`中，否则在高帧率下会出现不稳定的力累积。

**《Minecraft》的游戏刻（Game Tick）**：Minecraft将逻辑更新频率固定为20TPS（Tick Per Second），即每个游戏刻为50ms，完全采用固定时间步长。红石电路、生物AI、方块更新全部以游戏刻为单位，这是Minecraft红石计时精度刚好是50ms整数倍的根本原因。

**网络对战游戏的帧同步**：格斗游戏（如《街头霸王》系列）使用固定时间步长以确保本地与远程客户端状态完全一致。《街头霸王V》的逻辑帧率为60fps，每帧输入通过网络同步，输入延迟以"帧"（约16.67ms）为最小单位。

## 常见误区

**误区一：`dt` 越小物理模拟越精确**
将 `FIXED_DT` 从 `1/60` 缩小到 `1/240` 并不总是提升精度，反而会使每帧需要执行更多次物理迭代，CPU开销成倍增加。积分误差与时间步长的关系取决于所用积分方法（欧拉法误差为O(dt)，Verlet法为O(dt²)），盲目缩小步长不如改进积分算法。

**误区二：可变时间步长对所有游戏都适用**
RPG或横版动作游戏使用可变时间步长通常没有问题，但涉及精确物理的赛车游戏或网络同步的竞技游戏中，可变 `dt` 会导致不同帧率的玩家弹射力度计算不一致，产生公平性问题。《火箭联盟》（Rocket League）明确采用固定物理步长来保证复现性。

**误区三：游戏循环只有一个**
现代游戏引擎中，渲染循环、物理循环、音频循环通常运行在不同线程，各自拥有独立的时间步长和调度频率。Unity的主线程游戏循环与渲染线程并非同一循环，混淆这一点会导致在渲染回调中访问游戏对象状态时发生数据竞争。

## 知识关联

**前置概念**：了解游戏编程模式概述后，游戏循环是理解所有运行时模式的起点——它定义了"每帧发生什么"的基本框架，后续所有模式都在这个框架内运作。

**后续概念——更新方法（Update Method）**：游戏循环的 `update(dt)` 步骤需要遍历所有游戏实体并调用其更新逻辑，如何组织这些实体的更新调用顺序与接口，正是更新方法模式所解决的问题。游戏循环提供"何时更新"，更新方法提供"更新什么"。

**后续概念——游戏多线程架构**：单线程游戏循环的性能瓶颈（CPU单核利用率100%而其他核心闲置）推动了多线程架构的需求。将渲染、物理、AI分离到不同线程后，原有的单一 `while(running)` 循环演变为带有同步屏障（Barrier）的多线程协作结构，其时间步长管理复杂度大幅上升。