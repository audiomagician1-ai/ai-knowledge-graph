---
id: "anim-hit-pause"
concept: "Hit Pause"
domain: "animation"
subdomain: "keyframe-animation"
subdomain_name: "关键帧动画"
difficulty: 3
is_milestone: false
tags: ["游戏"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
  - type: "book"
    citation: "Swink, S. (2008). Game Feel: A Game Designer's Guide to Virtual Sensation. Morgan Kaufmann Publishers."
  - type: "book"
    citation: "Totten, C. W. (2014). An Architectural Approach to Level Design. CRC Press / A K Peters."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Hit Pause（命中停顿）

## 概述

Hit Pause，又称"命中帧冻结"或"Hitstop"，是动画与游戏设计中一种专门用于强化攻击命中瞬间打击感的技术手段。其核心操作是：当攻击判定接触目标的那一帧触发时，暂停或极度减慢动画播放约2至12帧（在60fps标准下，约相当于0.033秒至0.200秒），随后恢复正常速度。这段极短的"时间静止"会让玩家或观众的大脑感知到"这一击打实了"。

该技术在日本格斗游戏文化中被系统化运用，早在1991年Capcom发行的《街头霸王II》便已将Hit Pause作为设计标准写入开发规范。《街头霸王II》的"冻结帧"时长约为4帧（60fps），轻攻击与重攻击的冻结时长被刻意区分，重拳的Hit Pause明显长于轻拳，从而在手感上传达出力量层级差异。这一设计传统由制作人西山隆志（Nishiyama Takashi）团队奠定，此后成为格斗游戏工业事实标准。

Hit Pause之所以重要，在于它解决了视觉动画固有的"轻飘感"问题。无论角色动作的位移速度有多快、特效有多炫，如果缺乏命中瞬间的帧冻结，攻击往往感觉"穿透而过"而非"砸中"。Hit Pause通过操控时间感知，将生理上的"疼痛反射停顿"这一现实规律移植到动画逻辑中。神经科学研究表明，人体在受到强烈冲击时会产生约80～150毫秒的反射性肌肉僵直，Hit Pause正是这一生理现象的视觉模拟。

> **思考问题**：如果一款游戏的所有攻击——无论是普通拳击还是终结必杀——都使用完全相同时长的Hit Pause，玩家的打击感体验会发生什么变化？力量层级的感知依赖于什么？

---

## 核心原理

### 帧冻结的时长区间与力量分级

Hit Pause的时长直接对应攻击力量的等级感知。通常设计规范如下：
- **轻攻击**：2～4帧冻结（约0.033～0.067秒）
- **中攻击**：5～8帧冻结（约0.083～0.133秒）
- **重攻击/必杀技**：9～16帧冻结（约0.150～0.267秒）
- **超必杀/终结技**：16～22帧冻结（约0.267～0.367秒，需配合特殊演出补偿节奏损失）

超过20帧的冻结会开始让玩家感到"卡顿"而非"震撼"，因此16帧通常被视为单次普通攻击的上限。《猎天使魔女》（Bayonetta，2009年，PlatinumGames）的"Torture Attack"触发时冻结时长约达18帧，但配合镜头推拉和音效层，仍维持了节奏感。Steve Swink在其2008年著作《Game Feel》中将Hit Pause列为"虚拟感觉（Virtual Sensation）"设计的核心工具之一，并指出其有效性的物理上限约为人类视觉系统对"瞬间"的感知阈值——约200毫秒（即12帧@60fps）。

### 关键公式：Hit Pause时长与伤害值的映射关系

在程序化生成Hit Pause时长的系统中，常见的线性映射公式为：

$$H = H_{\min} + \left(\frac{D - D_{\min}}{D_{\max} - D_{\min}}\right) \times (H_{\max} - H_{\min})$$

其中：
- $H$：本次攻击的Hit Pause帧数
- $H_{\min}$：系统设定的最小冻结帧数（通常为2帧）
- $H_{\max}$：系统设定的最大冻结帧数（通常为12～16帧）
- $D$：本次攻击的实际伤害值
- $D_{\min}$：游戏中最小单次伤害值
- $D_{\max}$：游戏中最大单次伤害值

例如，假设某游戏伤害区间为 $D_{\min}=10$，$D_{\max}=100$，Hit Pause帧数区间为 $H_{\min}=2$，$H_{\max}=14$。当某次攻击造成55点伤害时，代入公式：

$$H = 2 + \frac{55 - 10}{100 - 10} \times (14 - 2) = 2 + \frac{45}{90} \times 12 = 2 + 6 = 8 \text{ 帧}$$

该攻击将触发8帧的Hit Pause，对应约0.133秒的命中冻结，与"中攻击"的感知区间吻合。这种公式驱动的方案避免了为每个攻击动作单独手工标注冻结帧数的繁琐工作，在攻击种类超过50种的大型动作游戏中尤为实用。

### 攻击方与受击方的差异化处理

Hit Pause并非对所有对象一视同仁地冻结。专业实现方案中，攻击方角色与受击方角色会接收不同的处理：

- **攻击方**：完全冻结或保留极小幅度的震颤动画（2～3像素的随机位移抖动，频率约为每帧随机化一次）
- **受击方**：冻结在受击动作（Hit Stun动画）的第1帧，同时叠加颜色闪白（Flash White）效果持续1～2帧

这种差异化处理使画面不会显得"完全静止"，而是保留了一丝动态张力。《黑暗之魂》系列（FromSoftware，2011年）中，受击方冻结时长比攻击方多1～2帧，制造出"力量传递有延迟"的物理真实感——这模拟了现实中冲击波从碰撞点传递到受害者全身的微小时差。

### 与Hit Stun及Hitstop的区别

Hit Pause（或Hitstop）专指**帧冻结本身**，而Hit Stun是指冻结结束后受击方进入无法操作状态的持续帧数。两者在时间轴上是连续但独立的阶段：

```
攻击帧触发 → [Hit Pause: 4帧冻结] → [Hit Stun: 12帧硬直] → 恢复可操作
```

许多初学者将两者混淆，但它们服务于不同目的：Hit Pause强化"命中感知"，Hit Stun控制"攻防节奏"。在《街头霸王V》的帧数数据库（Frame Data）中，两个参数被分列在不同字段，设计师可独立调整，互不干扰。

### 慢放变体（Slow Motion Hit Pause）

除完全冻结外，部分游戏与动画采用**局部慢放**替代硬停顿，将命中后2～8帧的时间尺度缩放为0.1～0.3倍速（即正常速度的10%～30%）。《茶杯头》（Cuphead，Studio MDHR，2017年）某些Boss受击动画采用0.2倍速持续4帧的慢放方案，比硬冻结更流畅但同样有效。这种变体在强调"流动感"的动作游戏（如《空洞骑士》）中更常见，因为完全冻结会破坏其流体运动的美学一致性。

---

## 关键公式与数据模型

### 感知有效性阈值

根据Swink（2008）的实验数据，Hit Pause的感知有效性并非线性分布。在60fps环境下，人类视觉对帧冻结的感知呈现如下特征：

- **0～1帧**（0～16.7ms）：低于视觉感知阈值，玩家无法察觉，等同于无Hit Pause
- **2～4帧**（33～67ms）：边界感知区，需配合音效才能有效传达命中感
- **5～12帧**（83～200ms）：最佳有效区间，打击感与节奏感平衡最优
- **13～20帧**（217～333ms）：强调区间，适用于高权重攻击，但需演出补偿
- **20帧以上**（>333ms）：进入"卡顿感知"区域，负面反馈增加

这一分布可用分段函数建模：

$$\text{PerceivedImpact}(H) = \begin{cases} 0 & H \leq 1 \\ \alpha \cdot H & 2 \leq H \leq 12 \\ \alpha \cdot 12 - \beta \cdot (H - 12) & H > 12 \end{cases}$$

其中 $\alpha$ 为正向感知增益系数，$\beta$ 为超限后的负向惩罚系数，具体数值依游戏类型校准。

### 帧率换算与跨平台一致性

当游戏支持多帧率（30fps、60fps、120fps）时，Hit Pause的帧数必须以**时间（秒）为基准**进行换算，而非直接复用帧数值：

$$H_{\text{target}} = \text{round}\left(H_{\text{base}} \times \frac{FPS_{\text{target}}}{FPS_{\text{base}}}\right)$$

例如，基准帧率60fps下的8帧Hit Pause，在30fps平台应换算为4帧，在120fps平台应换算为16帧，以确保玩家感知到的冻结时长（约0.133秒）保持一致。

---

## 实际应用

### 2D格斗游戏中的标准实现

在Unity或Godot中实现Hit Pause的最简方案是操控`Time.timeScale`（Unity）或`Engine.time_scale`（Godot），在命中帧将全局时间缩放设为0或接近0的值，持续目标帧数后恢复为1.0。需要注意的是，如果Hit Pause冻结了整个游戏时间，粒子特效、音效触发器也会受影响，因此通常需要为特效系统单独设定不受timeScale影响的独立时间轴。

**案例**：独立游戏《Skullgirls》（Lab Zero Games，2012年）的开源代码中，Hit Pause实现采用了"双时间轴"架构：游戏逻辑时间轴（受timeScale控制）与视觉特效时间轴（固定为实时）分离，命中帧闪光和粒子爆发在Hit Pause期间仍然正常播放，避免了"画面完全静止"的廉价感。该实现方案被许多独立格斗游戏开发者作为参考范本引用。

### 动作游戏中的镜头配合

《猎天使魔女》《鬼泣5》（Devil May Cry 5，Capcom，2019年）等作品将Hit Pause与镜头Zoom-In（向命中点推进约5%～8%的视野缩放）绑定，两者在同一帧触发。这使得命中瞬间同时获得时间与空间两个维度的"强调"，打击感倍增。单独使用Hit Pause而不配合镜头震动，在大场面中视觉冲击会减弱约30%～40%（根据Swink，2008年测试数据）。

### 逐帧动画中的手工处理

在传统逐帧动画（如格斗游戏手绘序列帧）中，Hit Pause通过**重复绘制同一张命中帧**来实现：将命中瞬间的那一张赛璐珞画格在时间轴上延展2～6格，无需编程介入。《街头霸王III：三度冲击》（Street Fighter III: 3rd Strike，Capcom，1999年）的拳击命中帧便采用