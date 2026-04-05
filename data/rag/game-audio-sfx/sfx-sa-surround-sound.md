---
id: "sfx-sa-surround-sound"
concept: "环绕声系统"
domain: "game-audio-sfx"
subdomain: "spatial-audio"
subdomain_name: "空间音频"
difficulty: 1
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 环绕声系统

## 概述

环绕声系统通过在听者周围布置多个物理扬声器，将音频信号分发至不同声道，在水平面乃至三维空间中营造出包围感音场。与双耳音频依赖头相关传输函数（HRTF）模拟空间感不同，环绕声系统利用真实扬声器的物理位置差异产生方向性——声音从实际角度传入耳朵，依靠声波到达时间差（ITD）和声压级差（ILD）而非心理声学欺骗来定位。

环绕声的商业化历史可追溯至1976年杜比实验室推出的 **Dolby Stereo** 四声道矩阵编码方案。1992年，杜比AC-3（Dolby Digital）正式确立5.1声道作为家庭影院与DVD的标准格式；其中"0.1"特指频率范围仅覆盖20–120 Hz的低频效果声道（LFE）。2012年，Dolby Atmos将声道模型升级为**基于对象（Object-based）**的渲染方式，允许最多128个独立音频对象在三维空间实时定位，打破了传统固定声道数量的硬性限制。DTS:X（2015年发布）随后提出竞争方案，同样采用对象渲染，但允许渲染器根据实际扬声器数量自适应输出，无需预设声道格式。

在游戏音频领域，环绕声系统直接影响玩家对敌方位置、环境深度和爆炸方向的感知判断。《使命召唤》系列自2007年起要求混音师为PC平台提供5.1母版，原因是竞技玩家依赖脚步声方向判断敌人位置，环绕声精确性因此与竞技公平性直接挂钩。索尼PlayStation 5于2020年推出Tempest 3D Audio引擎，在缺少物理环绕扬声器的条件下通过HRTF将Atmos信号折算为双耳渲染，体现出环绕声系统与双耳音频之间的技术互补关系（参见 Begault, D.R., *3-D Sound for Virtual Reality and Multimedia*, NASA/TM-2000-209606）。

---

## 核心原理

### 声道布局与扬声器角度标准

5.1系统包含六个声道：前左（L）、前中（C）、前右（R）、后左环绕（Ls）、后右环绕（Rs）以及0.1 LFE。**ITU-R BS.775-3** 标准规定，前左/右扬声器置于±30°，后环绕扬声器置于±110°（部分实现为±120°），中置扬声器置于0°。

7.1系统在5.1基础上增加侧左（Lss）和侧右（Rss）两个声道，分别置于±90°，填补了5.1中±30°至±110°之间约80°的定位空洞，使水平面声像移动更加连续。

Dolby Atmos天空声道最多支持4个顶置扬声器（Top Front Left/Right、Top Back Left/Right），实现从地面到头顶180°垂直覆盖，标准描述格式为 **7.1.4**（底层7.1声道 + 4个高度声道）。更完整的影院配置可达 **9.1.6**，即底层9个全频声道、1个LFE、6个高度声道，合计16路独立输出。

### 声道分配与等功率平移法则

游戏引擎将三维场景坐标映射到多声道输出时，采用**等功率平移法则（Equal-Power Panning Law）**。对于相邻两个扬声器之间的声像移动，左右增益系数须满足：

$$L(\theta) = \cos\!\left(\frac{\pi}{4} + \frac{\theta}{2}\right), \quad R(\theta) = \cos\!\left(\frac{\pi}{4} - \frac{\theta}{2}\right)$$

其中 $\theta \in [-\pi/2,\, \pi/2]$ 为偏移角度，此公式保证 $L^2 + R^2 = 1$，即总功率在声像移动全程保持恒定，避免信号移动到两扬声器正中间时出现-3 dB的功率凹陷（线性平移会出现此问题）。

中置声道承担固定对话和HUD音效的职责，防止听者头部移动导致语音感知位置漂移。游戏中，角色配音和系统提示音通常硬锚定到C声道，仅环境音和音效走L/R/Ls/Rs的动态平移路径。

### LFE声道的频率与增益特性

0.1声道的"0.1"代表带宽仅为全频声道的十分之一（20–120 Hz vs 20–20000 Hz）。Dolby Digital规范中，LFE声道拥有相对于主声道 **+10 dB** 的编码增益优势，专门承载爆炸、引擎轰鸣、低频震动等内容。

游戏混音时，将武器射击或爆炸的次低频分量（20–80 Hz）单独路由至LFE可显著增强震撼感，而不污染用于方向感知的五个全频声道。关键约束：LFE内容**不得**包含方向信息，因为人耳对120 Hz以下频率的方向辨别能力接近于零（波长超过2.8 m，远大于人头间距），任何写入LFE的定向内容都会被听者忽略，只会浪费编码带宽。

---

## 关键公式与实现算法

### VBAP多声道振幅计算

**Vector Base Amplitude Panning（VBAP）** 是适用于任意扬声器布局的多声道平移算法，由Pulkki（1997）在赫尔辛基理工大学提出。算法核心是将目标声源方向向量 $\mathbf{p}$ 表达为最近一对（二维）或三角形（三维）扬声器方向向量的线性组合：

$$\mathbf{p} = g_1 \mathbf{l}_1 + g_2 \mathbf{l}_2 \quad \Rightarrow \quad \begin{bmatrix} g_1 \\ g_2 \end{bmatrix} = \mathbf{p}^T \begin{bmatrix} \mathbf{l}_1 & \mathbf{l}_2 \end{bmatrix}^{-T}$$

求解后对增益归一化：$g_i' = g_i / \sqrt{g_1^2 + g_2^2}$，确保总功率不变。VBAP已被集成进 Wwise（作为"3D Spatialization"后端之一）和 FMOD Studio 的空间化器，支持从5.1到7.1.4的任意声道配置。

### Wwise 路由示例（伪代码）

```python
# Wwise Python SDK 示例：将爆炸音效路由至5.1声道床
import waapi

with waapi.connect() as client:
    # 设置音源的3D空间化模式为 "Position + Orientation"
    client.call("ak.wwise.core.object.setProperty", {
        "object": "\\Actor-Mixer Hierarchy\\SFX\\Explosion_Large",
        "property": "3DSpatialization",
        "value": "Position"
    })
    # 将LFE发送量设为 -6 dBFS，主声道保持 0 dB
    client.call("ak.wwise.core.object.setProperty", {
        "object": "\\Actor-Mixer Hierarchy\\SFX\\Explosion_Large",
        "property": "LFEContribution",
        "value": -6.0  # 单位：dB
    })
```

上述代码将爆炸音效的低频贡献量限制在 -6 dBFS，避免LFE声道过载（Wwise默认LFE总线的限幅器阈值设为 -0.3 dBFS）。

---

## 实际应用

### 游戏引擎中的环绕声配置

Unreal Engine 5 内置 **Quartz** 和 **MetaSounds** 系统，支持直接向 7.1 声道床输出。在 `Project Settings > Audio > Default Surround Sound Quality` 中选择 "7.1 Surround"，引擎将自动激活空间化插件链，并在运行时检测玩家设备的最大声道数：若检测到立体声耳机，则自动降回双耳渲染路径（通过 HRTF 折算）。

Unity 中使用 **Resonance Audio** 插件时，需在 `Audio Mixer` 中将 Master 输出设置为 `8-channel (7.1)`，并为每个 `AudioSource` 绑定 `ResonanceAudioSource` 组件，才能激活基于对象的动态声道分配。若不做此绑定，Unity 默认退回到基于振幅的立体声平移，丧失5.1/7.1的方向精度。

### 竞技游戏的脚步声混音实践

以《Apex Legends》（Respawn Entertainment，2019）为例：游戏混音师将脚步声的200–800 Hz中频段路由至环绕声道（Ls/Rs/Lss/Rss），将80 Hz以下次低频完全切除（而非送入LFE），原因是LFE在竞技场景中会产生"位置掩蔽"——低频方向信息不明确，反而干扰玩家对脚步来源的水平定位判断。竞技类游戏通常还会将脚步声的整体响度抬高至 -12 dBFS LUFS，远高于环境音轨的 -23 dBFS LUFS 标准，以确保方向信息在混响丰富的场景中仍清晰可辨。

---

## 常见误区

**误区1：LFE等同于低音炮音量控制**
LFE是一个独立编码声道，不是低音炮的音量旋钮。家庭影院接收机的"低音管理（Bass Management）"功能会将**所有全频声道**中低于80 Hz的内容重定向至低音炮——这与LFE声道是两条完全独立的信号路径。游戏混音师若误将所有低频都塞入LFE，会导致其余声道缺乏低频基础，在没有开启低音管理的专业监听系统上听起来单薄。

**误区2：声道数越多定位越精确**
从5.1升级到7.1可填补侧向定位空洞，但从7.1升级到9.1的边际效益递减明显。Hollerweger（2006）的主观测试表明，受试者在7.1与9.1之间的水平面定位辨别正确率差异仅约4%，而从5.1到7.1的差异约17%。因此预算有限时，优先保证7.1的扬声器校准精度（±1 dB声压级匹配、±2°角度误差）比增加声道数量更有效。

**误区3：Atmos对象可以无限精确定位**
Dolby Atmos的128个对象在渲染至实体扬声器时，最终仍受限于扬声器的物理位置。"对象"的优势在于**渲染自适应**——同一内容在2.0耳机、5.1家庭影院和64扬声器影院中均可自动重映射，而非空间分辨率本身无限提升。

---

## 知识关联

环绕声系统与**双耳音频**（前置知识）的核心区别在于物理扬声器 vs. HRTF卷积：双耳音频在耳机上效果最佳，但受个体HRTF差异影响较大（约30%的用户出现"颅内化"感知）；环绕声系统定位精度不依赖HRTF，但强制要求正确的物理扬声器摆位。现代系统（如PS5 Tempest、Xbox Spatial Sound）通过**双耳折算（Binaural Downmix）**将环绕声信号在耳机上还原，成为两者的交汇点。

后续概念 **Ambisonics** 是一种与声道无关的空间音频格式：一阶Ambisonics（FOA）使用4个信号分量（W/X/Y/Z）编码全球域声场，高阶Ambisonics（HOA）以球谐函数为基底，N阶需要 $(N+1)^2$ 个分量——三阶HOA需16个分量，可提供约 ±5° 的水平分辨率，远超7.1的离散声道间隔约22°。环绕声系统可视为Ambisonics的**下游渲染目标**：Ambisonics先捕获全域声场，再解码输出至5.1/7.1/Atmos任意格式，这也是游戏引擎中"Ambisonics → 声道床"工作流的核心逻辑。

> **思考问题：** 若一款游戏的目标平台同时包含PC（支持7.1扬声器）和主机（仅有立体声耳机），混音师应在母版阶段做7.1混音还是双耳混音？两种策略在