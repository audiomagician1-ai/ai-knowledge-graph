---
id: "sfx-aam-delivery-spec"
concept: "交付规格"
domain: "game-audio-sfx"
subdomain: "audio-asset-management"
subdomain_name: "声音资源管理"
difficulty: 5
is_milestone: true
tags: []

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 46.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.414
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 交付规格

## 概述

交付规格（Delivery Specification）是音效团队向游戏集成团队移交音频资产时必须遵守的技术标准集合，通常以检查表（Checklist）或规格文档（Spec Sheet）形式存在。它规定了音频文件的采样率、位深、格式、命名规则、文件夹结构、响度标准和元数据要求等全部维度的验收条件。不符合交付规格的音效文件将被退回，直接影响游戏的里程碑进度节点。

交付规格的概念起源于电影后期制作行业。1990年代，Dolby Digital标准强制要求音频素材以48kHz/24bit交付，这一惯例逐渐被游戏行业借鉴。进入2000年代，随着游戏主机跨平台发布需求增加，各平台（PS、Xbox、PC）的音频压缩格式差异导致单一交付规格已无法满足需求，多平台差异化规格体系随之出现。

交付规格在音效资源管理流程中的价值体现在两个具体环节：其一，它是音频QA测试的执行依据——测试工程师依据规格表逐项核查文件属性；其二，它决定了自动化构建管线（如Wwise或FMOD的批处理导入）能否无错执行，因为格式不匹配会导致构建脚本抛出异常并中断整个音频集成流程。

---

## 核心原理

### 技术参数标准

交付规格中最基础的技术参数组合通常为：**44100Hz或48000Hz采样率，16bit或24bit位深，WAV格式（未压缩）**。主机平台（PS5、Xbox Series X）普遍要求48kHz/24bit作为原始素材交付标准，移动平台则接受44.1kHz/16bit以控制包体大小。位深直接影响动态范围：16bit提供约96dB动态范围，24bit提供约144dB动态范围。规格文档需明确说明交付的是原始源文件（Source）还是经过响度处理后的母版文件（Master），这两者在位深选择上标准不同。

### 响度规范

现代游戏交付规格通常引用**ITU-R BS.1770-4**标准，要求音效文件的峰值电平不超过**-1 dBTP（True Peak）**，以防止数字限幅失真。对话类音效一般要求整合响度（Integrated Loudness）落在**-23 LUFS ± 1LU**范围内。单次音效（one-shot）文件如武器声、脚步声则不强制要求整合响度，但必须满足峰值限制。规格检查表中需要列明测量工具（如iZotope RX Loudness Control或Nugen VisLM）和测量范围（完整文件或去掉头尾静音后测量），不同测量范围会产生2-4 LU的差异。

### 命名规则与文件夹结构

交付规格必须包含文件命名约定（Naming Convention）的精确定义。一个典型的游戏音效命名规则示例为：`[项目代码]_[类别]_[描述]_[变体编号]_[版本号].wav`，例如`PRJ_WPN_RifleShot_01_v003.wav`。命名中禁止使用空格、中文字符、特殊符号（除下划线外），文件名总长度通常限制在64个字符以内（部分引擎路径长度有限制）。文件夹层级结构需与游戏引擎内的事件层级对应，例如Wwise项目中`\SFX\Weapons\Firearms\`这一层级结构应在交付文件夹中完整还原，否则自动导入脚本无法正确映射资产路径。

### 元数据与版本标识

交付规格中的元数据要求包括WAV文件BWAV（Broadcast Wave）头信息的填写规范，具体字段包括：Description（描述）、Originator（创作者）、OriginationDate（创作日期，格式YYYY-MM-DD）和TimeReference（时间参考，以采样数表示）。版本标识规则要求每次修改后版本号递增（v001→v002），而非覆盖同名文件。交付包中还需附带一份**交付清单（Delivery Manifest）**，通常为CSV格式，列出文件名、时长（秒）、采样率、位深、MD5校验值，供接收方自动校验文件完整性。

---

## 实际应用

**案例一：《XX战场》PC与主机双平台交付**
该项目音频总监在规格文档中定义了两套并行标准：PC版交付OGG Vorbis压缩格式（质量等级Q7，对应约192kbps），主机版交付原始WAV 48kHz/24bit。音效师在每批次交付时需在文件夹结构中区分`\Delivery_PC\`和`\Delivery_Console\`两个根目录，并分别附带独立的Manifest CSV文件。构建服务器收到文件后，CI/CD脚本自动读取Manifest，用ffprobe逐文件校验采样率与位深，不匹配项自动生成拒收报告。

**案例二：移动端游戏的包体优先规格**
某移动游戏项目规格要求所有环境音（Ambience）文件强制转换为单声道（Mono）、44.1kHz、16bit，因为立体声移动环境音在移动设备扬声器上几乎无法区分，但会增加100%的文件体积。规格检查表将此作为硬性拒收条件（Hard Fail），区别于采样率偏差1Hz这类软性警告（Soft Warning）。这种Hard Fail / Soft Warning双层判定机制使音频QA效率提升约40%。

---

## 常见误区

**误区一：认为交付规格等同于引擎内部编码设置**
交付规格规定的是源文件的技术参数，游戏引擎（如Wwise）会在导入后对文件进行二次转码（如转为Vorbis或ADPCM）。将引擎导出格式与交付规格混淆，会导致音效师错误地交付已压缩的MP3或OGG文件作为源素材，这类有损压缩文件经引擎二次压缩后音质损失呈乘积效应，俗称"代际损失"（Generation Loss）。

**误区二：认为文件通过响度检测即表示符合规格**
响度合规仅是交付规格中的一项指标。许多团队仅检查LUFS值便标记文件为"通过"，忽略了True Peak超限（常见于采样率转换后产生的过冲）、立体声相位对齐（Phase Correlation应不低于-0.5）和文件头信息缺失等问题。完整的交付规格检查表通常包含12-20个独立检查项，响度只是其中2-3项。

**误区三：版本迭代时复用旧文件名**
当音效师修改了一个文件但保留原文件名时，接收方的Manifest校验会因MD5不匹配而拒收，同时旧版本文件可能已被引擎缓存。规范的做法是将版本号追加到文件名末尾，并在交付清单中标注`REPLACES: PRJ_WPN_RifleShot_01_v002.wav`字段，使版本追溯链完整。

---

## 知识关联

交付规格与**备份与归档**直接衔接：归档系统中保存的源文件版本必须与交付规格中的版本号体系一致，否则当需要从归档中提取特定版本重新交付时，会因命名规则不统一导致无法定位。具体来说，归档时记录的MD5校验值应当与交付Manifest中的MD5完全对应，形成从创作到交付的完整哈希链。

向后连接**平台特定处理**：交付规格定义的是平台无关的源文件标准，而平台特定处理（Platform-Specific Processing）则是在符合交付规格的源文件基础上，针对PS5 Tempest引擎、Xbox Spatial Sound或iOS Core Audio的差异化编码处理。只有源文件严格符合交付规格（特别是采样率和位深），平台特定处理的批量转码工作流才能以可预期的方式执行，避免因输入文件参数不一致导致的平台版本音质差异。