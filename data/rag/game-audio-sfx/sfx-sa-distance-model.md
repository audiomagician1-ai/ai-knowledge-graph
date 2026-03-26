---
id: "sfx-sa-distance-model"
concept: "距离模型"
domain: "game-audio-sfx"
subdomain: "spatial-audio"
subdomain_name: "空间音频"
difficulty: 2
is_milestone: false
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 48.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 距离模型

## 概述

距离模型（Distance Model）描述声音强度随声源与听者之间物理距离变化而衰减的数学规律，是游戏引擎空间音频系统将真实声学物理现象转化为可实时计算的参数化模型的核心机制。最基础的物理原理来自**平方反比定律**（Inverse Square Law）：在无障碍物的自由空间中，声压级（SPL）随距离加倍而下降约6 dB，即音量与距离的平方成反比，公式为 $I \propto 1/r^2$，其中 $I$ 为声音强度，$r$ 为距离。

距离模型的工程化应用可追溯至20世纪90年代初期的3D音频API标准化工作。1996年，Creative Labs与Intel联合推出的**DirectSound3D**率先将距离衰减参数（最小距离、最大距离、衰减因子）封装为可编程接口；随后1998年的**OpenAL 1.0**规范进一步将距离模型分类化，定义了至今仍被广泛沿用的六种标准模型。游戏音频开发者需要正确选择和配置距离模型，才能让枪声、脚步声、环境音等在三维空间中呈现出符合玩家直觉的位置感。

## 核心原理

### OpenAL 定义的六种标准距离模型

OpenAL 1.1规范明确列出以下六种距离模型，每种均有对应的增益计算公式：

1. **AL_INVERSE_DISTANCE**（反比距离）：
   $G = \dfrac{RefDist}{RefDist + RolloffFactor \cdot (r - RefDist)}$
   
2. **AL_INVERSE_DISTANCE_CLAMPED**（钳位反比距离）：在上式基础上将 $r$ 钳位至 $[RefDist,\ MaxDist]$ 区间，超出最大距离的声源增益固定为0。

3. **AL_LINEAR_DISTANCE**（线性距离）：
   $G = 1 - RolloffFactor \cdot \dfrac{r - RefDist}{MaxDist - RefDist}$

4. **AL_LINEAR_DISTANCE_CLAMPED**（钳位线性距离）：与钳位反比类似，加入距离区间限制。

5. **AL_EXPONENT_DISTANCE**（指数距离）：
   $G = \left(\dfrac{r}{RefDist}\right)^{-RolloffFactor}$

6. **AL_EXPONENT_DISTANCE_CLAMPED**（钳位指数距离）：加入区间钳位。

其中 **RolloffFactor**（衰减因子）为1.0时模拟真实物理空间；游戏中常将其设为0到10之间的浮点数，室外开阔场景通常用1.0，室内小空间可调至2.0以强调距离感。

### 三个关键距离参数

所有主流游戏引擎（Unity、Unreal Engine 5、FMOD、Wwise）的距离模型都围绕三个参数构建：

- **最小距离（Min Distance / Reference Distance）**：在此距离以内声音以满音量播放，不再继续增大。Unity的AudioSource默认值为1米，Wwise的默认值同样为1单位距离。
- **最大距离（Max Distance）**：声音可被感知的极限距离，超过此值增益归零（钳位模型）或趋近于零。Wwise允许将其单独设置为"不截断"模式。
- **衰减因子（Rolloff Factor）**：控制衰减速率的乘数，相当于对物理模型的夸张或收缩。

### 对数感知与感知矫正

人耳对响度的感知遵循**韦伯-费希纳定律**，以对数形式而非线性形式响应强度变化。纯粹的物理平方反比衰减（$1/r^2$）在游戏中常常显得声音"消失过快"，因为玩家在距声源5米处就感知到音量大幅下滑。为此，许多游戏会故意将线性衰减模型（AL_LINEAR_DISTANCE）与较小的RolloffFactor（如0.5）配合使用，牺牲物理真实性以换取更好的游戏体验。《守望先锋》团队在2016年GDC演讲中公开提到，他们对所有武器音效采用了经美术主导调整的自定义衰减曲线，而非默认的物理模型。

## 实际应用

**第一人称射击游戏中的枪声距离感**：以Wwise实现为例，远距离枪声（>50米）通常使用指数衰减模型（RolloffFactor = 1.5），并配合高通滤波器模拟空气对高频的吸收（Air Absorption），使玩家能通过音色变化而非仅凭音量判断敌人距离。

**开放世界环境音铺设**：《荒野大镖客：救赎2》等开放世界游戏对不同类别的声源使用不同距离模型：河流水声采用线性钳位模型（MaxDist = 80米），鸟鸣采用反比钳位模型（MinDist = 5米，MaxDist = 30米），确保玩家在不同速度移动时过渡平滑。

**Unity AudioSource配置示例**：将Spatial Blend设为1.0（纯3D），Volume Rolloff选择"Logarithmic Rolloff"，Min Distance = 2，Max Distance = 50。这一组合对室外场景中小型道具碰撞音效效果最佳。

## 常见误区

**误区一：RolloffFactor = 1.0 等于物理真实**
许多开发者认为将衰减因子设为1.0即可还原现实声学。事实上，OpenAL的反比公式在 $r = RefDist$ 时才等于真实物理的平方反比，而且游戏引擎普遍省略了空气吸收、反射叠加等次级效应，单凭距离模型无法完整还原真实声学环境。

**误区二：线性衰减"不真实"就不该用**
物理上声音确实不以线性方式衰减，但线性距离模型在某些场景下反而听感更自然。原因在于游戏摄像机的FOV缩放、音效的混音压缩等流程会改变听者的响度基准，此时线性模型的可预测性便于混音师精确控制不同距离声层的相对关系。

**误区三：最大距离设得越远越好**
将MaxDist设置为500米以上看似增加了细节，实则带来两个问题：一是大量声源被激活进入计算，增加CPU/DSP开销；二是过远距离的细小音量差异在最终混音中被Limiter压缩掉，玩家毫无察觉。实际项目中，人声对话的MaxDist极少超过25米，爆炸音效通常不超过150米。

## 知识关联

距离模型以**衰减曲线**为直接前驱：衰减曲线是距离模型在游戏引擎编辑器中的可视化与编辑形式，Wwise的Attenuation编辑器将距离模型的数学公式绘制为可手动调节的样条曲线，开发者通过拖拽曲线实质上就是在修改RolloffFactor和距离参数。距离模型计算出的增益值作为基础响度输入，被Ambisonics编码器在生成球谐函数（Spherical Harmonics）表示时用于设定声源权重，距离越远的声源其Ambisonics编码中的高阶分量会被额外衰减以模拟距离模糊感。

距离模型的输出结果直接影响**多普勒效应**的感知显著性：当声源正在靠近监听者时，距离模型让音量持续增大，这与多普勒音调上移产生协同增强效果，使高速移动的声源（赛车、炮弹）产生更强烈的空间动感；反之，若距离模型的MaxDist设置过小导致声源在触发多普勒前就已消音，则整个多普勒效果将被截断而听不到完整的音调变化过程。