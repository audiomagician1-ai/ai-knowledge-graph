---
id: "anim-notify"
concept: "动画通知"
domain: "game-engine"
subdomain: "animation-system"
subdomain_name: "动画系统"
difficulty: 2
is_milestone: false
tags: ["事件"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 动画通知

## 概述

动画通知（Animation Notify）是Unreal Engine动画系统中嵌入在动画序列时间轴上的事件触发机制，允许开发者在动画播放到特定帧时执行自定义逻辑。它以两种形式存在：瞬时触发的 **Notify**（单点事件）和具有持续时间的 **NotifyState**（区间事件），两者均可附加在AnimSequence、AnimMontage或BlendSpace的时间轴上。

动画通知的概念在Unreal Engine 3时代的UE2.5中已有雏形，彼时称为AnimNotify，以C++纯虚函数形式实现。UE4重构了整套动画蓝图系统后，Notify在4.0版本正式支持蓝图派生类，使美术和设计师无需编写C++即可扩展逻辑。UE5则将Notify的触发精度与动画评估管线深度整合，确保通知在正确的线程阶段被调用。

动画通知在游戏开发中解决了"动画与游戏逻辑时序耦合"的核心问题。例如，角色挥剑动作的碰撞检测应当精确地在剑身划过轨迹的帧段内开启和关闭，而不是依赖定时器猜测帧序，这正是NotifyState区间机制的典型用途。

---

## 核心原理

### Notify 与 NotifyState 的结构差异

**Notify** 继承自 `UAnimNotify`，仅实现一个回调函数：
```
virtual void Notify(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation);
```
它在动画时间轴经过放置点的**瞬间**触发一次，没有持续时长，适合播放音效、生成粒子特效等一次性事件。

**NotifyState** 继承自 `UAnimNotifyState`，实现三个回调：
```
NotifyBegin()  // 区间开始帧
NotifyTick()   // 区间内每帧调用，参数含 float DeltaTime
NotifyEnd()    // 区间结束帧
```
NotifyState 在时间轴上占据一段可拖拽调整的橙色矩形区域，`NotifyTick` 会在整个区间内每帧执行，`DeltaTime` 参数反映真实帧间隔，这使得区间内的累积逻辑（如伤害值随动作深度递增）得以精确计算。

### 触发时序与动画评估管线

动画通知的触发发生在 **Worker Thread** 的动画图评估阶段，具体在 `FAnimInstanceProxy::UpdateAnimation()` 之后、骨骼变换写回游戏线程之前。这意味着Notify回调虽在Worker Thread中被"记录"，但实际分发给蓝图的时机是下一帧游戏线程的 `DispatchAnimEvents()`。开发者若在Notify中访问物理或碰撞组件，必须注意线程安全，直接操作Actor属性应通过 `UAnimNotify::bIsNativeBranchingPoint` 标记为分支点以强制在游戏线程执行。

### 蒙太奇中的通知与队列机制

在Montage系统中，当Montage被中断（例如调用 `StopAllMontages`）时，若当前帧有NotifyState正在激活区间内，引擎会**强制调用一次 `NotifyEnd()`** 以确保区间状态被正确清理，避免碰撞盒永久开启等逻辑泄漏。此行为由 `FAnimNotifyEvent::bTriggerOnDedicated` 标志控制，默认为 `true`。Montage的通知还支持 **Notify Track** 分层管理，一条Montage时间轴最多可添加**无限条**轨道，便于按功能分类（音效轨、特效轨、逻辑轨）组织通知。

### 蓝图派生通知

在蓝图中创建继承自 `AnimNotify` 或 `AnimNotifyState` 的子类后，编辑器会自动在动画序列的 **Notifies** 面板中列出该类，可直接拖入时间轴。蓝图版Notify通过重写 `Received_Notify` 事件节点实现逻辑，传入参数包括 `MeshComponent` 和 `Animation` 引用，可通过 `MeshComponent` 向上访问 `OwningActor`，进而调用角色的任意接口函数。

---

## 实际应用

### 脚步音效与地面材质联动

在奔跑动画的左脚和右脚落地帧各放置一个 `Notify_Footstep`，在回调中对角色脚部骨骼做**LineTrace**检测地面物理材质，根据材质类型（石头、泥土、木板）播放对应音效。相比在角色蓝图中写定时轮询逻辑，这种方式将触发时机精确绑定到动画帧，避免因帧率波动导致音效提前或滞后。

### 近战武器伤害区间检测

为攻击动画添加 `NotifyState_MeleeAttack`，在 `NotifyBegin` 中开启武器的碰撞盒（`SetCollisionEnabled(QueryOnly)`），在 `NotifyTick` 中执行重叠检测并将受击目标记录入已命中列表（防止同一次挥击重复伤害），在 `NotifyEnd` 中关闭碰撞盒并清空命中列表。这一模式在《仁王》式动作游戏中极为常见，确保伤害窗口与动画画面完全同步。

### Montage中的技能特效时机控制

在技能施放Montage的蓄力阶段放置 `NotifyState_ChargeEffect`，`NotifyBegin` 时在角色手部骨骼 `Attach` 粒子系统，`NotifyEnd` 时 `Detach` 并触发技能释放逻辑。若玩家在蓄力期间取消操作导致Montage被中断，引擎自动调用的 `NotifyEnd` 会确保粒子被正确清除，无需额外的取消逻辑分支。

---

## 常见误区

### 误区一：Notify 触发时机绑定到具体帧号

许多开发者误以为在第15帧放置Notify就会在第15帧精确触发。实际上，Notify的触发依赖**时间轴采样区间**：若帧率降低导致单帧时间跨度超过Notify所在时刻，引擎仍会检测到区间内存在Notify并触发它，但不会补发跳过帧之间的多个Notify。对于NotifyState，若单帧时间跨越整个NotifyState区间，则 `NotifyBegin`、`NotifyTick`、`NotifyEnd` 会在**同一帧内依次全部触发**。

### 误区二：在 NotifyTick 中直接修改 Actor Transform

`NotifyTick` 在Worker Thread记录阶段被调用（非原生分支点时），直接写入 `Actor->SetActorLocation()` 会导致线程竞争，产生难以复现的随机崩溃。正确做法是在Notify数据中缓存需要传递的信息，通过 `AnimInstance->AddCurve` 或游戏线程消息队列在安全时机应用变换。若必须在Notify中操作游戏对象，应将该Notify的 `bIsNativeBranchingPoint` 设为 `true` 强制同步到游戏线程。

### 误区三：NotifyState 的 NotifyEnd 不会在 Montage 中断时调用

部分开发者在Montage被Stop后发现碰撞盒未关闭，错误地认为NotifyEnd未被调用，转而在 `OnMontageEnded` 委托中手动重置状态。这种双重清理会导致逻辑重复执行。事实上引擎**保证** Montage中断时调用 `NotifyEnd`，问题通常出在开发者自行管理的状态变量与Notify逻辑的执行顺序冲突上，应检查 `OnMontageEnded` 和 `NotifyEnd` 的调用先后关系（NotifyEnd先于OnMontageEnded触发）。

---

## 知识关联

**与Montage系统的关系**：动画通知依附于AnimSequence时间轴，而Montage系统将多段AnimSequence组织为可程序控制的片段。Montage为Notify引入了额外的中断保证（强制NotifyEnd）和多轨道管理能力，理解Montage的片段跳转逻辑有助于预判Notify在Section切换时的触发行为——当Montage跳转到非相邻Section时，跳过的时间区间内的Notify不会被触发。

**与AnimInstance的关系**：Notify最终将事件分发到 `AnimInstance`，蓝图AnimInstance可重写 `AnimNotify_[名称]` 事件节点直接捕获特定名称的Notify，无需创建独立的Notify蓝图类。这种"命名事件"机制（Native Notify）在Notify逻辑简单时可减少资产数量，但会将通知处理逻辑分散到AnimInstance蓝图中，需权衡可维护性。

**与状态机的关系**：动画状态机中的过渡动画同样支持嵌入Notify，但过渡动画时长通常短于0.3秒，放置在过渡动画中的NotifyState若区间过长会因动画播放未完成就过渡完毕而触发强制NotifyEnd，这是状态机动画中使用NotifyState时需要特别注意的边界情况。