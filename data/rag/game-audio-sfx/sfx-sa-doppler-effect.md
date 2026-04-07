---
id: "sfx-sa-doppler-effect"
concept: "多普勒效应"
domain: "game-audio-sfx"
subdomain: "spatial-audio"
subdomain_name: "空间音频"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 82.5
generation_method: "intranet-llm-rewrite-v3"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v3"
  - type: "academic"
    author: "Bregman, A. S."
    year: 1990
    title: "Auditory Scene Analysis: The Perceptual Organization of Sound"
    publisher: "MIT Press"
  - type: "academic"
    author: "Härmä, A., Jakka, J., Tikander, M., Karjalainen, M., Lokki, T., Hiipakka, J., & Lorho, G."
    year: 2004
    title: "Augmented Reality Audio for Mobile and Wearable Appliances"
    journal: "Journal of the Audio Engineering Society"
    volume: "52"
    issue: "6"
    pages: "618–639"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v3
updated_at: 2026-04-06
---

# 多普勒效应

## 概述

多普勒效应是指当声源与听者之间存在相对运动时，听者感知到的声音频率与声源实际发出的频率产生偏差的物理现象。当声源朝向听者靠近时，感知频率升高（音调变尖）；当声源远离听者时，感知频率降低（音调变沉）。这一规律由奥地利物理学家克里斯蒂安·多普勒（Christian Andreas Doppler，1803–1853）于1842年在其论文《论双星及某些天体的彩色光》（Über das farbige Licht der Doppelsterne）中首次提出，并于1845年由荷兰气象学家白贝罗（Christophorus Buys Ballot）在铁路实验中首次用声学实验加以验证——他让一列满载号手的火车以不同速度行驶，由站台乐手判断音调偏移，实验结果与多普勒公式高度吻合（Bregman, 1990）。

在游戏音效领域，多普勒效应是赋予运动声源真实感的关键机制。一辆赛车在玩家面前飞驰而过，其引擎声从高音调急速滑落至低音调，这种频率变化是玩家判断物体速度和运动方向的重要听觉线索。若缺失多普勒效应，高速运动物体的音效会显得呆板且不真实，严重削弱沉浸感。游戏引擎（如Unity 2022 LTS和Unreal Engine 5.3）均内置了多普勒效应模拟，开发者可通过调节多普勒系数（Doppler Factor）在0到5之间精确控制效果强度，0表示完全禁用，1表示物理真实值，更高数值则产生夸张的戏剧化效果。音频中间件FMOD Studio 2.02及Wwise 2023.1同样提供专用的Doppler节点，支持在参数化混音图中对频率偏移进行二次处理。

## 核心原理

### 多普勒频率公式

多普勒效应的感知频率由以下公式精确计算：

$$f' = f \times \frac{v + v_{\text{listener}}}{v + v_{\text{source}}}$$

- $f'$：听者感知到的频率（Hz）
- $f$：声源发出的原始频率（Hz）
- $v$：声音在空气中的传播速度（20°C常温下约为343 m/s，0°C时约为331 m/s）
- $v_{\text{listener}}$：听者相对于声音传播介质的速度（靠近声源为正值，远离为负值）
- $v_{\text{source}}$：声源相对于介质的速度（远离听者为正值，靠近为负值）

**例如**，一辆时速120 km/h（约33.3 m/s）的赛车发出1000 Hz的引擎基频声：赛车迎面驶来时，感知频率约为 $1000 \times \frac{343}{343 - 33.3} \approx 1109$ Hz；赛车驶离后，感知频率降至约 $1000 \times \frac{343}{343 + 33.3} \approx 912$ Hz，总变化幅度接近197 Hz，听觉上相当于约3个半音（semitone）的音高差异，人耳对此变化极为敏感，识别阈值通常仅需1个半音（约6%的频率差）。

频率偏移量与相对速度的关系还可以用近似线性公式表达，当 $v_{\text{source}} \ll v$ 时：

$$\Delta f \approx f \times \frac{v_{\text{radial}}}{v}$$

其中 $v_{\text{radial}}$ 为声源与听者之间沿连线方向的相对速度分量（径向速度）。

### 游戏引擎中的实时模拟方法

游戏引擎并非每帧都执行完整物理公式，而是通过计算声源与听者之间的相对径向速度（即沿两者连线方向的速度分量）来近似模拟多普勒效应。每帧记录声源和听者在世界空间中的位置，用位移差除以帧时间得到速度向量，再将速度向量投影到声源-听者单位方向向量上，仅取径向分量代入公式。横向运动（声源从侧面经过）不产生频率变化，这与真实物理完全一致。

Unity的`AudioSource`组件中，`dopplerLevel`属性默认值为1.0，直接乘以物理计算出的频率偏移比例。将该值设为0.5可获得较为柔和的效果，适合写实类游戏；设为3.0以上则适合科幻或卡通风格，产生夸张的音调滑动。Unreal Engine 5中则在`UAudioComponent`的`DopplerIntensity`参数中实现等效逻辑，默认值同为1.0，取值范围建议限制在0到2.0之间以避免极端的音高跳变（Härmä et al., 2004）。

### 频率偏移与音频重采样

在实际音频处理管线中，多普勒频率偏移通过**实时变速重采样（pitch shifting via resampling）**实现：当感知频率应升高时，音频引擎以更快的速率读取音频缓冲区中的采样点，等效于提高播放音调；反之降低读取速率。这种方法不改变音频资源本身，仅修改播放速率，因此对CPU消耗极低，可在数千个并发声源上实时运行。

在44100 Hz采样率下，频率偏移10%（约1.73个半音）意味着实际读取速率变为48510 Hz或39690 Hz。需要注意的是，变速重采样会同时改变声音的持续时间，但由于运动声源通常是循环播放的（如引擎声、子弹飞行声），这一副作用几乎不可察觉。高质量实现中可采用Sinc插值重采样以减少混叠失真，FMOD Studio内部默认即使用此方案。

## 实际应用案例

**赛车游戏**：《极品飞车》（Need for Speed）系列中，NPC赛车超车时的引擎音调变化直接通过多普勒系数驱动，据Criterion Games（2012年《极品飞车：最高通缉》）的音频团队GDC演讲披露，其Doppler Factor通常设为1.2至1.5，略高于物理真实值，以补偿玩家在较慢的游戏帧率（30 fps）下对速度感知不足的问题。

**FPS射击游戏**：子弹飞行音效是多普勒效应的典型应用场景。一颗速度约900 m/s的步枪子弹（超过音速343 m/s），其多普勒公式中 $v_{\text{source}}$ 超过 $v$，会导致公式分母为负或趋近于零，物理上对应音爆（Sonic Boom）现象，引擎需对此做特殊处理。《战地》（Battlefield）系列的DICE音频团队采用的方案是将 $v_{\text{source}}$ 限制在 $0.9v$（约308 m/s）以下用于多普勒计算，同时触发独立的音爆资源（通常为预录制的"whip crack"音效），两者混合以还原超音速弹道的真实听觉体验。

**飞行模拟器**：战斗机俯冲时的音调下滑是多普勒效应与距离衰减模型的组合效果。Wwise 2023.1提供专用的Doppler RTPC（Real-Time Parameter Control）节点，允许将频率偏移值路由到参数均衡器（Parametric EQ）而非单纯变速，从而在保持时长不变的同时模拟频率变化，声音质感更为丰富，避免了纯变速方案在极速飞行中造成的音调"颤抖"瑕疵。

**太空题材游戏**：真实太空中声音无法传播，但《星际公民》（Star Citizen）等游戏为增强临场感仍应用了多普勒效应，并通过将 $v$ 设为虚构的"游戏内音速"（约700 m/s）来匹配宇宙飞船的飞行速度范围，同时保持公式结构不变，实现了物理公式与艺术需求的平衡。

## 常见误区与调试建议

**误区一：多普勒效应影响所有运动方向**。实际上，只有声源与听者之间的径向速度（连线方向的分量）才会引起频率变化。一个在听者正侧方做匀速直线运动的声源，在经过最近点的瞬间，径向速度为零，此时感知频率等于原始频率，既没有升高也没有降低。不少开发者误以为只要声源在运动就应施加多普勒效果，从而对侧向飞过的物体错误地添加了音调变化，导致违和感。

**误区二：多普勒效应可以用来模拟声源速度超过音速的情况**。当声源速度等于或超过343 m/s时，经典多普勒公式失效（分母趋近于零或变为负数）。游戏中将子弹或超音速飞机的 $v_{\text{source}}$ 直接代入标准公式，会产生极端频率值甚至导致浮点数溢出崩溃。正确做法是在代码中检测 $v_{\text{source}} \geq v$ 的边界条件，触发独立的音爆逻辑，而非依赖标准多普勒公式。

**误区三：提高多普勒系数总能提升真实感**。高多普勒系数（如5.0）会使慢速运动的物体（如人物慢跑，速度约1.5 m/s）也产生明显的音调滑动，听起来极为怪异。在真实物理下，1.5 m/s产生的频率偏移不足0.5%（约8.7音分，cents），人耳察觉阈限约为5音分，因此实际上人耳几乎无法察觉步行引起的多普勒偏移，此时系数应设为0或极小值。

**调试建议**：在Unity中可使用`AudioSource.velocityUpdateMode`设为`AudioVelocityUpdateMode.Fixed`，避免因物理帧率不稳定导致的速度估算误差，从而消除多普勒音调的不规则抖动。FMOD中则建议在Programmer Sound机制中手动传入速度向量，而非依赖自动位置差分，以获得更稳定的帧间速度估算。

## 参数调优策略

在实际项目中，多普勒效应的参数调优需结合游戏类型、目标平台与美术风格综合考量。以下为针对不同场景的建议参数范围：

| 游戏类型 | 推荐 Doppler Factor | 说明 |
|---|---|---|
| 写实赛车 | 1.0 – 1.3 | 接近物理真实，保留玩家速度感知线索 |
| 卡通/动漫风 | 2.0 – 3.5 | 夸张效果强化喜剧感或动作张力 |
| FPS/军事 | 0.8 – 1.2 | 接近真实但需对超音速弹道单独处理 |
| 太空/科幻 | 0.5 – 1.5 | 虚构物理规则，以美术感受为主导 |
| 步行/NPC