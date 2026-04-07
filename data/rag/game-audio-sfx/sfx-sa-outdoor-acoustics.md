---
id: "sfx-sa-outdoor-acoustics"
concept: "室外声学"
domain: "game-audio-sfx"
subdomain: "spatial-audio"
subdomain_name: "空间音频"
difficulty: 5
is_milestone: true
tags: []

# Quality Metadata (Schema v2)
content_version: 5
quality_tier: "A"
quality_score: 82.7
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "academic"
    author: "Salomons, E. M."
    title: "Computational Atmospheric Acoustics"
    year: 2001
    publisher: "Kluwer Academic Publishers"
  - type: "standard"
    author: "ISO"
    title: "ISO 9613-2: Acoustics — Attenuation of Sound During Propagation Outdoors"
    year: 1996
    publisher: "International Organization for Standardization"
  - type: "conference"
    author: "Tsingos, N., Funkhouser, T., Ngan, A., & Carlbom, I."
    title: "Modeling Acoustics in Virtual Environments Using the Uniform Theory of Diffraction"
    year: 2001
    publisher: "ACM SIGGRAPH Proceedings"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---

# 室外声学

## 概述

室外声学（Outdoor Acoustics）研究声音在开放空间中的传播规律，与室内声学的核心区别在于：开放环境中几乎不存在封闭边界反射，声波向全方向自由扩散，导致能量随距离呈平方反比衰减。这一特性使得游戏音效设计师必须用完全不同的信号处理链路来模拟户外场景，放弃混响拖尾而转而依赖大气吸收、地面反射和障碍物遮挡等真实物理效应。

室外声学作为独立研究领域，在20世纪60至70年代随机场噪声控制需求而系统化发展。1978年，Maekawa首次以实验数据验证了障碍物衍射遮挡量的近似公式，奠定了工程应用基础；ISO 9613-2标准（1996年正式发布）随后为户外声音衰减预测建立了完整的工程规范，至今仍是建筑声学与噪声评估领域的通用参考（ISO, 1996）。在游戏音频领域，Valve在2004年《半条命2》（Half-Life 2）中引入的环境声系统首次将室外声学原理具体实现为实时计算的遮挡与衰减模型，此后成为业界参考。2013年，Tsingos等人将均匀衍射理论（Uniform Theory of Diffraction, UTD）引入虚拟环境声学建模，显著提升了游戏引擎中绕射计算的精度（Tsingos et al., 2001）。

室外声学在游戏空间音频中的重要性体现在"空旷感"的真实性上：错误的室外混响设置会让开阔战场听起来像停车场，破坏玩家对空间规模的直觉判断。《荒野大镖客：救赎2》（Red Dead Redemption 2, 2018）的音效总监Cody Matthew Johnson在GDC 2019制作访谈中明确指出，他们用地形高度差和植被密度动态调整高频衰减曲线，才使得平原与峡谷的听感截然不同。这一设计理念与Salomons（2001）在计算大气声学领域提出的分层传播模型高度吻合。

**思考问题：** 为什么室外开阔场景不能直接复用室内声学的混响参数？具体来说，哪些物理量在这两种环境中发生了本质性的变化？

## 核心物理原理

### 反平方定律与大气吸收

声压级随距离的基础衰减遵循反平方定律：每当距离翻倍，声压级衰减约6 dB（点声源在自由声场中）。公式为：

$$\Delta L = 20 \times \log_{10}(r_2 / r_1)$$

其中 $r_1$ 为参考距离，$r_2$ 为目标距离，$\Delta L$ 为衰减量（单位 dB）。

例如，一挺机枪在距离1米处测得声压级为140 dB SPL，则在10米处约为120 dB，在100米处约为100 dB，在1000米处约为80 dB——每十倍距离衰减20 dB。这一规律与室内声场的扩散衰减（约3 dB/倍距离）形成鲜明对比。

在此基础上，大气吸收（Atmospheric Absorption）对高频成分额外衰减，其强度与频率的平方成正比、与距离成正比。ISO 9613-1（1996）规定：在温度20°C、相对湿度70%的标准条件下，4000 Hz信号每100米额外衰减约2.1 dB，1000 Hz约为0.4 dB，而250 Hz仅约0.1 dB（ISO, 1996）。这就是为什么远处炮声只剩低频轰鸣——高频能量早已被空气"吸收殆尽"。游戏实现中通常用一个随距离动态收紧的低通滤波器截止频率来模拟这一效应，截止频率 $f_c$ 与声源距离 $d$ 成反比关系，典型映射为：

$$f_c(d) = f_{c,\max} \times e^{-\alpha \cdot d}$$

其中 $\alpha$ 为大气吸收系数，可根据ISO 9613-1查表获得，$f_{c,\max}$ 通常取20000 Hz（近场全频带保留）。

### 地面反射与地面效应

不同于室内的全方向反射，室外声音的主要反射来自地面（Ground Reflection）。当直达声与地面反射声相位差满足半波长条件时，会在特定频率产生梳状滤波（Comb Filtering）陷波，压低200 Hz以下的低频响应——这称为"地面效应"（Ground Effect）。草地、泥土等软质地面对声波有更强的吸收，能量损耗可达硬地面（混凝土、水面）的3至5倍。Salomons（2001）的实测数据表明，草地地面在100 Hz处的声阻抗约为200 kPa·s/m²，而混凝土约为2000 kPa·s/m²，两者相差一个数量级。

在游戏中，地面材质标签（grass/concrete/water）直接映射到地面反射系数，水面的强反射正是湖边声音"更响亮"的物理依据。例如，《孤岛危机3》（Crysis 3, 2013）的地面材质系统定义了12种地面类型，每种类型对应独立的低频增益补偿值，湿地（wetland）设定的低频增益比干燥草地高出约3.5 dB。

### 障碍物遮挡与绕射

室外遮挡不同于室内墙壁的完全隔断，声波会绕过障碍物边缘发生衍射（Diffraction），衍射强度与波长成正比。Maekawa（1978）遮挡衰减公式给出了遮挡量的近似计算：

$$A_{\text{bar}} = 10 \times \log_{10}(3 + 20N)$$

其中 $N$ 为菲涅尔数（Fresnel Number），定义为：

$$N = \frac{2\delta}{\lambda}$$

$\delta$ 为绕射路径比直达路径的额外长度（单位米），$\lambda$ 为声波波长（单位米）。

例如，一道高度为3米的混凝土围墙，声源与听者各在其两侧5米处（$\delta \approx 0.9$ 米），对频率1000 Hz（$\lambda = 0.343$ 米）的遮挡量约为 $A_{\text{bar}} = 10 \times \log_{10}(3 + 20 \times 5.25) \approx 14.3$ dB；而对100 Hz（$\lambda = 3.43$ 米）仅约5.8 dB，差异近9 dB，充分说明低频绕射能力远强于高频。

实际游戏实现中，Wwise（版本2021.1起）和FMOD Studio（版本2.01起）的Occlusion系统均基于此原理，对低频设置更小的遮挡系数（低频绕射能力强），对高频设置更大的遮挡系数（高频更易被遮挡），通常通过频段分离的增益矩阵实现。Tsingos等人（2001）在SIGGRAPH的研究进一步证明，将UTD引入实时引擎可将绕射计算误差从Maekawa近似的±4 dB压缩至±1.5 dB以内。

### 风场效应与多普勒频移

室外环境特有的风场会引入两类音效：环境风噪（Ambient Wind Noise）来自气流扰动麦克风或树叶的摩擦；传播风效（Wind Gradient Effect）则使声波路径弯曲——顺风时声波折向地面，逆风时折向天空，导致顺风可听距离比逆风远30%至50%（Salomons, 2001）。游戏中《孤岛惊魂5》（Far Cry 5, 2018）通过将风向矢量投影到声源-听者连线上，动态修正衰减曲线斜率来近似这一效果，风速超过8 m/s时衰减斜率参数降低约15%以模拟顺风增程效应。

多普勒效应在室外场景中因空间尺度大而更为显著，飞行器或车辆的频率偏移量计算公式为：

$$f' = f \times \frac{v_{\text{sound}} \pm v_{\text{observer}}}{v_{\text{sound}} \mp v_{\text{source}}}$$

游戏引擎通常以343 m/s（20°C干燥空气）作为声速标准值。例如，一架以100 m/s飞行的战斗机（约0.29马赫）在直线掠过听者时，接近阶段的音高相对静止态上升约41%，离开阶段下降约29%，两者合计音调落差约11个半音——在游戏中若不正确实现这一效果，会让音效严重脱离视觉画面的直觉感知。

## 实际应用与工程实践

### 开阔战场的距离分层

《战地》系列（Battlefield，DICE出品）自《战地3》（2011年）起使用"声音层级系统"（Sound LOD System），将武器声分为近距离（0-30米）、中距离（30-150米）、远距离（150米+）三个资产层，分别承载不同的高频保留量和混响状态。远距离枪声素材本身就是经过低通滤波（截止频率约800 Hz）和电平压缩（压缩比约4:1，attack 50ms）处理的版本，而非对近距离素材实时滤波，以保证性能预算。《战地2042》（2021年）进一步将这一系统扩展为5层，在150-400米范围增设了"超远距离层"，截止频率降至500 Hz，并叠加了模拟大气湍流的随机幅度调制（AM，调制频率0.3-2 Hz，调制深度±1.5 dB）。

### 峡谷与山谷的平行反射

两侧峭壁之间会产生"峡谷回声"（Canyon Echo），回声延迟时间计算如下：

$$t_{\text{echo}} = \frac{2W}{v_{\text{sound}}} = \frac{2W}{343}$$

其中 $W$ 为峡谷宽度（单位米）。例如，一个50米宽的峡谷产生约 $t = 100/343 \approx 292$ 毫秒的回声，听感上对应约120 BPM节奏的一个八分音符延迟，这会显著影响玩家对枪声节奏的感知。Wwise中可用单次离散延迟（Delay插件，Feedback量设为-8至-12 dB）来实现衰减的峡谷回声，而非使用标准Reverb插件，后者会产生不真实的扩散混响尾巴。

### 森林密度的高频吸收

茂密森林中树叶和树干对1000 Hz以上频段的散射吸收可达每10米约1至2 dB的额外损耗，这意味着100米外的敌人声音应比空旷地面上额外损失10至20 dB的高频。例如，《幽灵行动：荒野》（Ghost Recon Wildlands, 2017）采用植被密度贴图（Vegetation Density Map，分辨率