---
id: "anim-facs"
concept: "FACS系统"
domain: "animation"
subdomain: "facial-animation"
subdomain_name: "面部动画"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 42.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.4
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# FACS系统

## 概述

面部动作编码系统（Facial Action Coding System，简称FACS）由心理学家保罗·艾克曼（Paul Ekman）和华莱士·弗里森（Wallace Friesen）于1978年正式发布。该系统通过解剖学分析，将人类面部的所有可观察肌肉运动分解为独立的基本单元，称为"动作单元"（Action Unit，AU）。FACS最初用于心理学研究中的欺骗检测与情绪识别，后来被动画行业广泛采用，成为数字面部动画的标准参考框架。

FACS将面部运动划分为46个核心Action Unit，每个AU对应一块或一组特定面部肌肉的收缩动作。例如AU1对应额肌内侧（Inner Brow Raise），AU6对应颧小肌（Cheek Raiser），AU12对应颧大肌（Lip Corner Puller）。在动画领域，美工师和技术总监通过AU的组合来精确重建目标表情，而不依赖主观描述。

FACS之所以对面部动画至关重要，在于它提供了一套与艺术风格无关的客观肌肉语言。无论是《阿凡达》中的动作捕捉流程，还是游戏引擎中的实时面部混合变形（Blend Shape），都能用相同的AU编号体系进行跨团队沟通和数据标注，极大降低了动画师、程序员与研究人员之间的协作摩擦。

---

## 核心原理

### 46个Action Unit的分类结构

FACS的46个AU按面部区域分为上面部（Upper Face）和下面部（Lower Face）两大类。上面部AU编号集中在AU1至AU7，主要对应眉毛、前额和上眼睑的运动，例如AU2（Outer Brow Raise，外眉上扬）由额肌外侧控制，AU4（Brow Lowerer，眉头下压）由皱眉肌控制，AU5（Upper Lid Raiser，上睑提升）由上睑提肌控制。下面部AU编号跨度较大，从AU9一直延伸至AU28，涵盖鼻子、嘴唇和下颌的各类运动，如AU25（Lips Part，唇部分开）和AU26（Jaw Drop，下颌下落）。

除主要AU外，FACS还定义了若干头部与眼部运动单元（Head Movement Unit，HU；Eye Movement Unit，EU），以及约20个描述面部质地变化的"附加动作描述符"。这些编号帮助动画师记录皮肤起皱、酒窝出现等无法由单一肌肉捕捉的细节。

### 强度分级系统（FACS Intensity Score）

每个AU的激活程度用字母A至E五个等级量化：A表示仅可追踪（Trace，约1/5强度），B表示轻微（Slight），C表示明显（Marked/Pronounced），D表示极度（Extreme），E表示最大化（Maximum）。在Blend Shape驱动的角色装配中，这五个等级直接对应权重值0.2、0.4、0.6、0.8、1.0，方便程序员将FACS数据与变形目标（Morph Target）参数对齐。

### AU组合与表情合成

单一AU无法构成完整表情，FACS表情通过AU的线性叠加描述。以"真诚微笑"（Duchenne Smile）为例，其标准编码为 **AU6 + AU12**——颧小肌提升脸颊同时颧大肌拉扯嘴角，缺少AU6则被识别为社交性微笑而非真实喜悦。愤怒表情的典型编码为 **AU4 + AU5 + AU7 + AU23 + AU24**，分别涉及眉头压低、上睑提升、眼睑收紧、唇部收紧与唇部压合。动画师在制作过程中可将每一帧的表情翻译成AU列表，再驱动对应的Blend Shape权重，实现高度可控的表情设计流程。

---

## 实际应用

**影视VFX中的AU数据管道**：在《本杰明·巴顿奇事》和《猩球崛起》等项目中，表演捕捉演员面部贴有专用标记点，捕捉软件将点的位移数据自动解算为AU激活值，再驱动数字角色的面部装配。技术总监会将装配中每个Blend Shape命名为对应AU编号（如"AU12_L"表示左侧嘴角拉扯），确保解算器输出能直接映射到控制器。

**游戏实时面部系统**：虚幻引擎5的MetaHuman框架内置了基于52个AU扩展集的控制骨骼（包含苹果ARKit的52个Blend Shape，其命名体系与FACS AU直接对应）。开发者通过iPhone TrueDepth摄像头实时捕捉面部，系统以每秒60帧输出每个AU的权重，驱动游戏角色做出同步表情。

**动画师手工K帧参考**：在没有动作捕捉设备的团队中，动画师会对照FACS手册或参考Ekman编写的《情绪的解析》（Emotions Revealed，2003）来分析演员参考视频，识别关键帧上的AU组合，再在软件中逐一调整对应的Blend Shape滑条，这比仅凭感觉调整参数更易于复查和修改。

---

## 常见误区

**误区1：FACS中只有46个AU，记住编号就能制作所有表情**
实际上，46是核心"主AU"的数量，FACS完整系统还包括约20个附加描述符（如A58描述下颌侧移），以及HU和EU系列。仅熟悉AU1至AU46无法描述咬牙、鼻孔扩张等动作的全部细节。此外，左右面部的AU可以独立激活（如单侧AU12_L与AU12_R），完整描述需区分对称与不对称情况。

**误区2：AU的叠加是简单的线性相加，不存在肌肉拮抗**
部分AU之间存在解剖学冲突：AU25（唇部分开）和AU28（唇部吸入）不能同时处于高强度状态；AU6与AU7同时激活时，眼部区域的皮肤变形会出现非线性叠加效果，不能用两个Blend Shape权重直接求和来模拟。忽视这一点会导致角色出现不自然的"橡皮脸"现象。

**误区3：FACS系统直接等同于情绪系统**
FACS本身不含任何情绪判断，它只描述肌肉运动而非情绪状态。"AU6+AU12"只是对特定肌肉组合的中性描述，将其解读为"快乐"需要额外的情感映射层。在动画流程中，情绪数据（如喜怒哀乐的权重）和FACS数据是两个独立层级，情绪系统驱动AU组合，而非情绪系统等于AU系统。

---

## 知识关联

**前置概念——面部动画概述**：面部动画概述建立了Blend Shape、骨骼驱动和动作捕捉等基本工作流程的概念。FACS系统正是这些技术流程中为Blend Shape命名和组织提供标准化依据的编码框架——没有对Blend Shape工作原理的理解，AU强度分级与权重映射的对应关系就失去了落脚点。

**后续概念——口型同步（Lip Sync）**：口型同步中的唇形变化主要由AU20（Lip Stretcher）、AU25、AU26及AU28等下面部AU驱动。掌握FACS后，动画师能够在音素级别精确指定每个口型对应的AU组合，而不是仅凭视觉匹配调整嘴形，从而提升口型同步的解剖学准确度。

**后续概念——情绪表达**：情绪表达是对FACS AU组合的语义解释层。Ekman确定的六种基本情绪（快乐、悲伤、愤怒、恐惧、厌恶、惊讶）均有对应的标准AU编码，例如恐惧对应AU1+AU2+AU4+AU5+AU7+AU20+AU26。学习情绪表达时，FACS为每种情绪提供了可量化的肌肉行为清单，使动画师能系统地检查表情是否传达了预期的情感信号。
