---
id: "sfx-sa-underwater-audio"
concept: "水下音效"
domain: "game-audio-sfx"
subdomain: "spatial-audio"
subdomain_name: "空间音频"
difficulty: 5
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 水下音效

## 概述

水下音效（Underwater Audio Effects）是指对水下环境独特声学特性的模拟与重现技术，涵盖声音在水介质中的传播方式、频率响应变化以及玩家角色潜入水面时的主观听觉感知变化。声音在水中的传播速度约为 1480 m/s（25°C 淡水），是空气中（343 m/s，20°C）的 4.31 倍；海水因盐度（约 35‰）和压力影响，传播速度可进一步升至 1520–1540 m/s。这一物理差异从根本上决定了水下音效的设计逻辑：波长更长、高频吸收更剧烈、混响模式与任何陆地空间截然不同。

水下声学的系统性研究起源于二战期间的军事声呐需求。1943 年，美国海军水下声学实验室（USNUSL）开始系统测量不同深度、盐度、温度条件下的声音吸收系数，这些数据奠定了后续游戏音频实现的物理基础。游戏领域对水下音效的早期尝试出现在 1998 年前后的三维动作游戏（如《古墓丽影 III》），彼时实现方式仅为预烘焙的低通滤波混音切换；而现代游戏引擎（Unreal Engine 5 的 MetaSounds 系统、FMOD Studio 2.x 的实时 DSP 链）已能在运行时根据摄像机水深、水体类型、底质材质动态混合多层参数化水下效果。

水下音效的核心挑战在于两点：其一，物理精确性与计算预算的平衡（实时卷积混响的 CPU 开销可能高达 5–8%，需优化为参数化算法混响）；其二，过渡体验的连续性——玩家角色从水面进入水下的那 0.3–0.8 秒是听觉沉浸感的关键窗口。

## 核心原理

### 频率响应与低通滤波

水对声波的吸收遵循频率平方规律（Thorp 公式，1967）。在游戏音频实现中，通常对全局 Submix 总线施加截止频率约为 800–1200 Hz 的低通滤波器（Low-Pass Filter），典型衰减斜率选用 -12 dB/oct（二阶 Butterworth）或 -24 dB/oct（四阶）。具体参数随水深动态调整：

| 水深区间 | 截止频率（LPF） | 衰减斜率 |
|---------|--------------|---------|
| 0–3 m（浅水） | 1200–1500 Hz | -12 dB/oct |
| 3–20 m（中层） | 800–1000 Hz | -18 dB/oct |
| 20 m 以下（深水） | 400–600 Hz | -24 dB/oct |

在 FMOD Studio 中，可通过 Built-In Effect → Three-EQ 的高频段增益参数（High Gain）与截止频率（High Crossover）驱动此动态变化，将水深 Game Parameter 直接映射至 EQ 自动化曲线。

### 混响特性与水体谐振

水下混响不同于任何 ITU-R BS.1116 定义的陆地声学空间类型。硬质底质（岩石、混凝土水底）产生高反射率、低吸收系数的混响，Pre-Delay 约为 5–20 ms，RT60 在封闭水下空间（如游泳池、水下洞穴）可达 2–5 秒；泥沙底质和水草则大量吸收声能，RT60 缩短至 0.3–0.8 秒。

水面作为声学阻抗突变边界，会对水下传播的声波产生接近全反射（反射系数约 0.9995），并形成明显的**梳状滤波效应（Comb Filtering）**，其成因是直达声与水面反射声之间固定路径差 $\Delta d$ 导致的周期性相消干涉。梳状滤波的第 $n$ 个峰谷频率为：

$$f_n = \frac{(2n-1) \cdot c}{2 \Delta d}, \quad n = 1, 2, 3, \ldots$$

其中 $c$ 为水中声速（约 1480 m/s），$\Delta d$ 为直达声与反射声的路径差（米）。在游戏中，可用短延迟（约 2–8 ms）的 Chorus 或 Flanger 效果器近似模拟此效应，湿干比（Wet/Dry）设置为 30–50%。

### 水面过渡层的动态混合

玩家摄像机位于水线附近（±0.5 m 垂直范围）时，单纯的二态切换会产生明显的听觉跳变。专业实现方案使用"水深偏移量"参数 $d$（摄像机位置相对水面的有符号垂直距离，向下为正），在 $d \in [-0.5\text{ m},\ +0.5\text{ m}]$ 区间内以 S 型曲线（Sigmoid）对水上/水下混音做加权插值：

$$\alpha(d) = \frac{1}{1 + e^{-k(d - d_0)}}$$

其中 $k$ 控制曲线陡峭程度（推荐 $k = 8$），$d_0$ 为过渡中心点（通常为 0，即水面处）。$\alpha = 0$ 时完全为水上混音，$\alpha = 1$ 时完全为水下混音，中间态则同时触发水面涟漪声、气泡声等过渡专属音效资产。

在 Wwise 中，可用 **RTPC（Real-Time Parameter Control）** 将 $d$ 映射至水下 Aux Send 的发送量（Send Volume），配合 Blend Track 在 Game Synth 层混合两套环境总线（Environmental Bus）。

### 骨传导与第一人称自发声处理

人在水中通过骨骼振动（骨传导，Bone Conduction）感知自身声音，颅骨腔体谐振峰集中在 200–800 Hz，使得呼吸声、心跳声听起来更低沉且共鸣感强烈。游戏中通常将第一人称自发声（First-Person Body Sounds，包括呼吸循环、心跳、移动摩擦）从主 Submix 总线移出，单独施加以下处理链：

```
FP_Body_Sounds_Bus
  ├─ HighPass Filter: Cutoff = 80 Hz（滤除次声干扰）
  ├─ Parametric EQ: +4 dB @ 300 Hz, Q=1.2（模拟颅腔共鸣）
  ├─ Parametric EQ: -8 dB @ 3000 Hz（削减气导高频）
  ├─ Reverb (Short Room): RT60 = 0.15 s, PreDelay = 0 ms
  └─ Volume: +3 dB（水下骨传导感知响度补偿）
```

这一设计参考了 Larsson & Vastfjall（2011）在《Journal of the Audio Engineering Society》中关于水下听觉感知的心理声学测量结果：受试者在水下对 250–500 Hz 频段声音的响度感知比空气中高约 5–7 dB（相同声压级条件下），证实骨传导路径在低频段具有显著增益优势。

## 关键公式与实现算法

### Thorp 吸收系数公式

Thorp（1967）给出海水中声波吸收系数 $\alpha_T$（单位：dB/km）的经验公式：

$$\alpha_T(f) = \frac{0.11 f^2}{1 + f^2} + \frac{44 f^2}{4100 + f^2} + 3 \times 10^{-4} f^2$$

其中 $f$ 为频率（kHz）。代入 $f = 1$ kHz 得 $\alpha_T \approx 0.055$ dB/km，代入 $f = 10$ kHz 得 $\alpha_T \approx 3.3$ dB/km——这量化地解释了为何水下 10 kHz 以上的高频成分在传播数十米后即衰减殆尽，而 100 Hz 以下的低频可传播数百公里（鲸歌远距离传播的物理基础）。

在游戏音频中，精确应用 Thorp 公式的开销过高，通常简化为分段线性 EQ 曲线，按水深每增加 5 m 将 4 kHz 以上频段额外衰减约 1.5 dB。

### 实时水下 DSP 链示例（FMOD Studio 伪代码）

```lua
-- FMOD Studio Script: 根据水深动态更新水下总线参数
-- 每帧调用，depth 为摄像机水深（米，负值表示水面以上）

function updateUnderwaterBus(depth)
    local alpha = sigmoid(depth, k=8, d0=0)  -- 过渡权重 0~1

    -- 低通滤波截止频率插值（对数空间）
    local fcAbove = 20000  -- Hz（水上，不滤波）
    local fcBelow = lerp(1200, 500, clamp01(depth / 20.0))  -- 随深度降低
    local fc = logLerp(fcAbove, fcBelow, alpha)
    UnderwaterBus:setParameterByName("LPF_Cutoff", fc)

    -- 混响湿量随深度增加
    local reverbWet = lerp(0.0, 0.75, alpha)
    UnderwaterBus:setParameterByName("Reverb_Wet", reverbWet)

    -- 整体增益补偿（水下感知响度轻微下降）
    local gainComp = lerp(0.0, -2.0, alpha)  -- dB
    UnderwaterBus:setFaderLevel(gainComp)
end
```

## 实际应用

**《深海迷onautica》（Subnautica，Unknown Worlds，2018）** 使用分层环境音效架构表现不同深度的水下声学变化：表层（0–200 m）采用较宽的混响与可辨别的海洋生物环境声；午夜区（200–1000 m）将整体 Submix 电平降低约 8 dB、截止频率压至 600 Hz 并叠加 0.3 Hz 的调制颤抖（模拟深水压力感）；深渊区（1000 m+）几乎仅保留 200 Hz 以下的低频成分与 -4 秒 RT60 的长尾混响，营造极度压迫的听觉密闭感。

**《光环：无限》（Halo Infinite，343 Industries，2021）** 的水下区域在 Xbox Series X 平台上利用硬件加速的空间音频（Microsoft Spatial Sound），为水下场景单独配置了一套 HRTF 滤波参数集，使水下声源定位从标准的头相关传输函数切换为模拟水中骨传导方向感知的简化双耳模型，令玩家在水下感知到声源方向信息的模糊化（真实水下骨传导方向辨别误差约为 ±15°，远高于空气中的 ±2°）。

**《荒野大镖客：救赎 2》（Red Dead Redemption 2，Rockstar，2018）** 的河流涉水系统将水深划分为 6 个离散区段（膝盖/腰部/胸部/颈部/水面/完全水下），每个区段对应不同截止频率与 Aux Send 量，同时在颈部至水面区段触发专属的"水面涌入"声效样本（录制自真实泳者入水瞬间的双耳麦克风录音），平均样本时长为 0.6 秒，触发后淡入时间为 80 ms。

## 常见误区

**误区一：将截止频率固定为 800 Hz 并视为"标准水下音效"。**  
实际上 800 Hz 仅适用于中等深度（5–10 m）的淡水环境。浅水区（1–3 m）截止频率应提高至 1200–1500 Hz；咸水（盐度 35‰）因离子弛豫吸收机制，对 1–10 kHz 频段的吸收系数是淡水的 2–4 倍，截止频率应相应下调 200–400 Hz。忽视水体类型差异会导致游泳池与深海场景听感相同。

**误区二：对所有声源使用同一套水下 DSP 链。**  
水下声学中，声源与听者的相对位置决定了传播路径长度，进而决定高频衰减量。距离为 2 m 的声源与距离为 30 m 的声源在水下听感差异巨大——前者仍保有 2 kHz 以上成分，后者几乎仅余低频轰鸣。正确实现方式是在每个声源的 Distance Attenuation 曲线之外，额外附加一条随距离增大而降低截止频率的