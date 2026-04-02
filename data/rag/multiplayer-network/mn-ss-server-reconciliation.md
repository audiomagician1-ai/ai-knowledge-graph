---
id: "mn-ss-server-reconciliation"
concept: "服务器调和"
domain: "multiplayer-network"
subdomain: "state-synchronization"
subdomain_name: "状态同步"
difficulty: 4
is_milestone: true
tags: []

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 服务器调和

## 概述

服务器调和（Server Reconciliation）是客户端预测机制的必要补充，专门解决客户端本地预测状态与服务器权威状态之间产生分歧时的修正问题。当客户端预测到玩家移动并立即渲染，而随后收到服务器发来的确认状态时，客户端必须判断两者是否一致——若不一致，则执行回滚（Rollback）并重放（Replay）之后所有未确认的本地输入，以还原出与服务器权威结果对齐的正确状态。

该技术最早在加布·纽维尔（Gabe Newell）所在的Valve团队于1996年开发《Quake》客户端时被系统性地归纳，后来由Valve在《半条命》（Half-Life）及其多人框架GoldSrc中完善。Gabriel Gambetta在2018年将其整理为广为引用的教学文章，并将服务器调和列为网络游戏客户端架构的四大核心机制之一（另外三个是客户端预测、延迟补偿和插值）。

服务器调和存在的根本原因是网络延迟不对称：客户端输入到达服务器需要一段时间（RTT的一半），服务器确认再返回客户端又需要一段时间。在这段往返时延（RTT通常为50ms–200ms）内，客户端已经在预测的基础上继续产生了多个新的输入帧，若收到不一致的服务器状态后直接覆盖当前状态，会造成明显的位置跳变（Rubber-banding），严重影响操控手感。

## 核心原理

### 输入序列号与未确认缓冲区

实现服务器调和的前提是客户端必须为每一个发送给服务器的输入帧分配一个单调递增的序列号（Sequence Number），例如第1帧输入编号为`seq=1001`，第2帧为`seq=1002`，以此类推。客户端在本地维护一个"未确认输入缓冲区"（Unacknowledged Input Buffer），其中存储所有已发送但尚未收到服务器确认的输入数据（包括输入内容、时间戳、当时的客户端预测状态）。服务器每次回包时，必须在响应报文中携带它最后处理的输入序列号`last_processed_seq`，以便客户端知道哪些输入已被权威处理。

### 回滚与重放算法

当客户端收到服务器的权威状态包时，调和流程分为三步：

1. **比较阶段**：将服务器返回的位置/状态与客户端缓冲区中对应序列号的预测状态进行比对。若误差超过容忍阈值（通常设为0.1–1.0游戏单位，视游戏类型而定），则触发调和。
2. **回滚阶段**：将客户端本地状态强制覆写为服务器权威状态（即以`last_processed_seq`对应的服务器坐标为基准）。
3. **重放阶段**：从未确认输入缓冲区中取出序列号大于`last_processed_seq`的所有输入，按照与服务器相同的物理/移动逻辑逐帧重新模拟，最终得出当前帧的预测位置。

重放阶段的计算量与未确认输入的数量成正比。若RTT为100ms，游戏以60帧/秒运行，则每次调和最多需要重放约6帧（100ms × 60fps ÷ 1000 = 6帧）。这对现代CPU而言几乎无感知，但若RTT升至500ms，重放帧数增至30帧，则需要对重放逻辑进行优化。

### 误差阈值与视觉平滑

并非所有服务器状态与预测状态的偏差都值得触发完整回滚。工程实践中，通常区分两种处理策略：当偏差小于设定阈值（如0.5个单位）时，采用**线性插值平滑**（Lerp）在若干帧内逐渐收敛至服务器状态，避免视觉突变；当偏差大于阈值（如发生了服务器拒绝的非法移动）时，才执行完整的回滚重放。《Overwatch》技术分享（2017年GDC演讲）中提到，他们对位置偏差使用了动态阈值，根据角色速度和网络抖动自动调整容忍范围，从而在激烈战斗场景中减少不必要的重放开销。

## 实际应用

**第一人称射击游戏（FPS）**：在《CS:GO》和《Valorant》中，本地玩家的移动完全由客户端预测驱动，服务器调和确保非法穿墙移动（如被服务端反作弊拒绝的位移）在客户端得到及时纠正。《Valorant》官方技术博客（2020年）明确指出，其服务器以128 tick运行，客户端预测+调和的误差纠正发生在每帧渲染之前，保证了玩家几乎感知不到回滚。

**多人竞速游戏**：在赛车游戏中，服务器调和主要处理碰撞判定后的位置修正。当两辆本地预测的赛车发生碰撞，服务器裁定后的结果可能与客户端预测不同，调和流程会将车辆位置回滚到服务器确认的碰撞结果，再重放后续帧的加速/转向输入。

**代码示意（伪代码）**：
```
// 收到服务器状态包时
function onServerUpdate(serverState, lastProcessedSeq):
    predictedState = inputBuffer.getStateAt(lastProcessedSeq)
    if distance(serverState.position, predictedState.position) > THRESHOLD:
        currentState = serverState  // 回滚
        for input in inputBuffer.after(lastProcessedSeq):
            currentState = simulate(currentState, input)  // 重放
    inputBuffer.removeBefore(lastProcessedSeq)
```

## 常见误区

**误区一：直接用服务器状态覆盖客户端状态**
部分初学者认为"以服务器为准"就意味着每次收到服务器包就直接覆盖本地状态。这实际上废弃了客户端预测的全部收益，导致每次更新都出现明显的位置抖动（Rubber-banding），等同于没有任何延迟隐藏。正确做法必须保留并重放未确认输入。

**误区二：每次调和都丢弃整个输入缓冲区**
服务器调和后，只应丢弃序列号**小于等于**`last_processed_seq`的已确认输入，序列号更大的未确认输入必须继续保留用于重放。若将整个缓冲区清空，则客户端会丢失最近若干帧的输入，造成短暂停顿感。

**误区三：调和只处理位置信息**
实际上，需要调和的状态不仅包括位置坐标，还包括速度向量、角色朝向、动画状态、技能冷却等所有会被输入影响的状态变量。《Rocket League》的物理同步方案中，服务器调和需要同步整个刚体物理状态（位置、旋转四元数、线速度、角速度共13个浮点数），这要求客户端缓冲的状态快照也必须完整记录这些字段。

## 知识关联

服务器调和直接依赖**客户端预测**提供的本地状态模拟能力——没有预测，就不存在需要调和的"分歧"，也不需要重放缓冲区。两者合称"预测-调和"（Predict-Reconcile）循环，是客户端权威感的技术基础。

在服务器调和的基础上，**延迟补偿**（Lag Compensation）进一步解决另一个方向的问题：服务器在处理玩家输入时，需要将游戏世界时钟回拨到该输入被发出时的状态，以公平判定命中检测，这与调和中服务器向客户端的"时间对齐"形成互补——一个是客户端向服务器权威看齐，另一个是服务器向客户端发出时刻看齐。理解服务器调和中回滚重放的思路，有助于直觉性地理解延迟补偿中服务端时间回溯的必要性。