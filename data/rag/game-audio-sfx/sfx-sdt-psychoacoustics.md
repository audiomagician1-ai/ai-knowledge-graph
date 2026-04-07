---
id: "sfx-sdt-psychoacoustics"
concept: "声音心理学"
domain: "game-audio-sfx"
subdomain: "sound-design-theory"
subdomain_name: "音效设计理论"
difficulty: 1
is_milestone: false
tags: []

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
  - type: "academic"
    citation: "Fletcher, H., & Munson, W. A. (1933). Loudness, its definition, measurement and calculation. Journal of the Acoustical Society of America, 5(2), 82–108."
  - type: "academic"
    citation: "Zwicker, E., & Fastl, H. (1999). Psychoacoustics: Facts and Models (2nd ed.). Springer-Verlag Berlin Heidelberg."
  - type: "standard"
    citation: "International Organization for Standardization. (2003). ISO 226:2003 — Acoustics: Normal equal-loudness-level contours."
  - type: "academic"
    citation: "Moore, B. C. J. (2012). An Introduction to the Psychology of Hearing (6th ed.). Brill Academic Publishers."
  - type: "book"
    citation: "Collins, K. (2008). Game Sound: An Introduction to the History, Theory, and Practice of Video Game Music and Sound Design. MIT Press."
  - type: "academic"
    citation: "Blauert, J. (1997). Spatial Hearing: The Psychophysics of Human Sound Localization (revised ed.). MIT Press."
  - type: "standard"
    citation: "International Telecommunication Union. (2011). ITU-R BS.1770-3 — Algorithms to measure audio programme loudness and true-peak audio level."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 声音心理学

## 概述

声音心理学（Psychoacoustics）是研究人类听觉系统如何感知、处理和解读声音信号的科学分支。它聚焦于物理声波与人类主观听觉体验之间的映射关系——同样强度的声音，在不同频率下，人耳会产生截然不同的响度感受。这一学科融合了心理学、神经科学与声学工程，专门解释"声音的物理属性"与"人的感知结果"为什么常常不一致。

该学科的奠基性研究可追溯至1933年，美国贝尔实验室的哈维·弗莱彻（Harvey Fletcher）与威尔顿·曼森（Wilton Munson）在《美国声学学会期刊》第5卷第2期发布了著名的"等响曲线"（Fletcher-Munson Curves），首次系统量化了人耳在不同频率下的灵敏度差异（Fletcher & Munson, 1933）。这份测量数据涵盖了从20 Hz到16 kHz、从听觉阈值到痛觉阈值的完整响度等级，后来被国际标准化组织（ISO）在2003年修订为ISO 226:2003标准，基于更严格的跨国实验室数据对原始曲线进行了校正，特别是在低频段（低于200 Hz）有显著修正幅度。德国亚琛工业大学声学家埃里希·兹维克（Erich Zwicker）等人进一步将等响曲线整合进完整的心理声学模型，提出了24个临界频带的"巴克尺度"理论（Zwicker & Fastl, 1999），成为现代音频工程的参照基准。英国剑桥大学心理声学家布莱恩·摩尔（Brian C. J. Moore）于2012年出版的《听觉心理学导论》第六版，系统整合了临界频带、听觉滤波器组、听觉场景分析等现代理论，是该领域公认的权威教材（Moore, 2012）。空间听觉领域的奠基性著作则来自德国波鸿鲁尔大学的约恩斯·布劳尔特（Jens Blauert），其1997年修订版专著《空间听觉：人类声源定位心理物理学》系统建立了HRTF理论框架（Blauert, 1997）。

在游戏音效设计领域，声音心理学的价值在于它能指导设计师有意识地塑造玩家的听觉体验。一个爆炸音效不需要在物理上准确还原真实爆炸的声压级（真实爆炸近场声压级可超过180 dB SPL，足以造成永久性听力损伤），只需通过精心设计的低频冲击（通常集中在40–80 Hz）、中频"噼啪"质感（2–5 kHz）和高频瞬态（8–12 kHz）的组合，触发玩家大脑中与"冲击力"和"危险"相关联的神经反应即可。理解听觉感知机制，是制作出令人信服的游戏音效的前提条件。游戏音频研究者凯伦·柯林斯（Karen Collins）在其2008年的专著《游戏声音》中指出，游戏音效设计从本质上是对玩家感知的主动管理，而非对现实声音的被动复制（Collins, 2008）。

**思考**：为什么同一个声音文件，在游戏中用小音箱播放与用耳机播放时，玩家对其"重量感"的判断会截然不同？这背后涉及哪些声音心理学原理——等响曲线补偿导致的低频感知损失、掩蔽阈值随总体声压级变化，还是HRTF空间定位机制在耳机与扬声器之间的根本性差异？如果你是游戏音效设计师，你会如何在单一音频资源中同时兼顾这两种播放场景？

---

## 核心原理一：频率敏感度与等响曲线

### 人耳灵敏度的分布特征

人耳对不同频率的声音敏感程度差异巨大。人类听觉的频率范围约为20 Hz至20,000 Hz，但灵敏度峰值集中在2,000 Hz至5,000 Hz区间——这与人类语音中辅音（如"s"、"f"、"t"）的关键频段高度重合，是数百万年进化选择的结果，也与人类外耳道的共振频率（约3,400 Hz）相吻合。根据ISO 226:2003等响曲线，要让一个100 Hz的低频声音听起来与1,000 Hz的声音同等响亮（均处于40方响度级），前者的声压级需要额外提高约20 dB。换言之，一个在物理测量上与枪声等声压级的低沉轰鸣，在玩家主观感受中会显得明显"更轻"，这直接决定了游戏低频音效必须做补偿性增益处理的技术逻辑。

等响曲线还揭示了一个反直觉的现象：当整体播放音量降低时，人耳对低频和高频的灵敏度损失远比中频更大——这一现象在响度级低于40方时尤为显著。这就是为什么游戏音效在低音量监听环境下（如手机扬声器最大声压级通常低于80 dB SPL）听起来"单薄"——低频物理上仍在，但已跌至听觉感知阈值以下。专业的游戏音效设计师在制作时会用多种播放设备（头戴耳机、桌面音箱、笔记本内置扬声器、手机扬声器）反复比对，确保在不同收听条件下音效的感知平衡保持一致。

### 响度感知的数学关系

响度感知遵循**韦伯-费希纳定律（Weber-Fechner Law）**的非线性特性，更精确的描述则采用斯蒂文斯幂律（Stevens' Power Law，1957年由哈佛大学心理学家斯坦利·史密斯·史蒂文斯提出）。声压级每增加10 dB，主观响度大约翻倍，其基于宋-方关系的换算可表达为：

$$L_{phon} = 40 \cdot \log_2\left(\frac{S}{S_0}\right) + 40$$

其中 $L_{phon}$ 为响度级（单位：方，Phon，定义为与被测声音等响的1,000 Hz纯音的声压级分贝数），$S$ 为实测响度（宋，Sone，1宋定义为1,000 Hz纯音在40 dB SPL条件下的主观响度），$S_0 = 1$ 宋为参考值。由此可知：2宋对应50方，4宋对应60方，16宋对应80方——每增加1倍的宋值，对应10方（即10 dB）的变化。这一公式说明响度感知是对数而非线性的，直接决定了游戏混音中各层次声音的电平分配策略：武器音效、角色语音、环境音、背景音乐之间的电平层级必须按照主观感知比例而非物理比例来规划。

此外，现代游戏音频行业广泛使用**响度单位LUFS（Loudness Units relative to Full Scale）**作为混音标准。LUFS基于ITU-R BS.1770标准（国际电信联盟，2006年首次发布，2011年更新为BS.1770-3版本），通过K加权滤波器（K-weighting filter，在高频段预加重约+4 dB、低频段引入约-4 dB的滚降）模拟人耳对不同频段的感知权重，比简单的dB峰值测量更贴近实际听感（ITU, 2011）。主流游戏平台的响度标准差异显著：Steam游戏通常建议整体响度在 $-14$ LUFS左右，PlayStation平台建议 $-18$ LUFS，而手机游戏则因播放环境噪声更高，常将动态范围压缩至 $-12$ LUFS附近。

**例如**：在《使命召唤》系列的混音实践中，武器射击音效的峰值通常设置在 $-3$ 至 $-1$ dBFS（True Peak），而背景环境音的整合响度维持在 $-30$ LUFS左右，两者之间存在超过15 dB的主观响度差距。根据宋-方换算，这约相当于主观感知上2.8倍的响度差——确保武器音效在密集交战环境中依然具有无可置疑的主导地位，同时背景声维持环境沉浸感而不被完全掩盖。若不做等响曲线的频率补偿，低频武器音效（如大口径步枪的低频炮口爆破声，基频约在80–120 Hz）即便峰值电平相同，在玩家耳中依然会显得"发虚"，缺乏令人信服的物理存在感。

---

## 核心原理二：听觉掩蔽效应

### 掩蔽效应的分类

当两个声音同时出现时，频率相近或强度更高的声音会"遮盖"另一个声音，使其变得难以察觉，这种现象称为听觉掩蔽（Auditory Masking）。掩蔽效应分为以下两大类：

- **同时掩蔽（Simultaneous Masking）**：两声音同时发生，强者压制弱者，掩蔽量与频率差和强度差直接相关。同时掩蔽的影响范围向高频方向的扩展明显强于向低频方向（即"向上扩展掩蔽"，Upward Spread of Masking），这一不对称性在游戏混音中具有重要的实践意义——低频强声（如爆炸声的40–120 Hz能量）对中高频弱声（如800 Hz–3 kHz的脚步声）的掩蔽作用远比反过来更强，这也解释了为何爆炸发生后玩家暂时难以分辨环境中的脚步声。
- **时间掩蔽（Temporal Masking）**：分为前向掩蔽（Forward Masking）和后向掩蔽（Backward Masking）。一个强声结束后约100–200毫秒内，仍会抑制对后续弱声的感知（前向掩蔽），这一效应由耳蜗毛细胞在强刺激后的"恢复期"决定；一个强声到来前约5–20毫秒，也能逆向抑制对先前弱声的回溯感知（后向掩蔽），机制更为复杂，涉及中枢听觉系统的处理延迟。前向掩蔽的持续时长与掩蔽音的强度正相关，强度每增加10 dB，前向掩蔽时长约延长2–3毫秒（Moore, 2012）。

### 临界频