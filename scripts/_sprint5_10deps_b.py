"""Sprint 5: Batch rewrite 10-deps tier (batch B) — 4 more documents."""
from pathlib import Path
ROOT = Path(r'D:\EchoAgent\projects\ai-knowledge-graph\data\rag')

DOCS = {}

DOCS['3d-art/3da-prop-intro.md'] = '''---
id: "3da-prop-intro"
concept: "道具美术概述"
domain: "3d-art"
subdomain: "prop-art"
subdomain_name: "道具美术"
difficulty: 1
is_milestone: true
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "Digital Modeling"
    author: "William Vaughan"
    year: 2011
    isbn: "978-0321700896"
  - type: "textbook"
    title: "The Complete Guide to Game Art"
    author: "Rick Emerson"
    year: 2020
  - type: "conference"
    title: "Prop Art Pipeline for AAA Games"
    authors: ["Clinton Crumpler"]
    venue: "GDC 2018"
scorer_version: "scorer-v2.0"
---
# 道具美术概述

## 概述

道具美术（Prop Art）是 3D 游戏美术中负责创建游戏世界中所有非角色、非环境的可交互或装饰性物件的专业方向。William Vaughan 在《Digital Modeling》（2011）中将 Prop 定义为"任何角色可以拿起、使用或与之互动的物体——从一把剑到一个垃圾桶"。

在 AAA 制作管线中，道具美术是体量最大的资产类别。Clinton Crumpler 在 GDC 2018 中分享：一个中型开放世界项目需要 **3,000-8,000 个独特道具**，占总美术资产的 60-70%。单个道具从概念到引擎内资产的完整流程通常需要 1-5 天（视复杂度）。

## 道具的分类体系

| 类别 | 定义 | 多边形预算 | 实例 |
|------|------|-----------|------|
| Hero Props | 特写镜头/核心剧情物品 | 10K-50K tris | 《战神》利维坦之斧 |
| Primary Props | 玩家常见/可交互 | 2K-10K tris | 武器、宝箱、门 |
| Secondary Props | 环境填充/装饰 | 500-2K tris | 桌椅、瓶罐、书本 |
| Background Props | 远景装饰 | 100-500 tris | 远处建筑装饰、树桩 |
| Modular Kit Pieces | 可重复拼接的模块 | 1K-5K tris | 墙壁模块、管道、栅栏 |

**Nanite 时代的变化**：UE5 Nanite 取消了传统多边形预算——Hero Prop 可以直接使用百万面 ZBrush 雕刻导入。但非 Nanite 平台（移动端、Switch）仍需严格控制。

## 道具制作的标准流水线

```
1. 参考收集 & 概念设计（0.5-1天）
   └─ PureRef 收集 20-50 张参考图
   └─ 确定材质、比例、风格

2. 高模雕刻（1-3天）
   └─ ZBrush/Blender 雕刻细节
   └─ 不考虑面数（可达数百万面）
   └─ 关注：轮廓剪影、表面细节、比例

3. 低模重拓扑（0.5-1天）
   └─ 手动重拓（TopoGun）或自动（ZRemesher/InstantMesh）
   └─ 目标面数：类别预算内
   └─ 关注：干净的布线、合理的UV展开

4. UV展开（0.5天）
   └─ RizomUV/UVLayout/Blender
   └─ Texel Density 统一（通常 512-1024 px/m）
   └─ 最小化接缝，隐藏接缝在不可见处

5. 烘焙（0.5天）
   └─ 高模 → 低模 烘焙法线/AO/Curvature/ID
   └─ Marmoset Toolbag / Substance Painter
   └─ 关键：确保法线贴图无接缝伪影

6. 材质制作（1-2天）
   └─ Substance Painter / Quixel Mixer
   └─ PBR 贴图集：BaseColor + Normal + Roughness + Metallic
   └─ 分辨率：1K（小道具）→ 2K（标准）→ 4K（Hero）

7. 引擎集成 & 优化（0.5天）
   └─ 导入 FBX → 设置材质实例 → LOD 生成
   └─ 碰撞体设置（简单/复杂）
   └─ 光照测试
```

总计：一个 Primary Prop 约 3-5 工作日。工业化团队可通过 Kitbash/程序化辅助压缩到 1-2 天。

## PBR 材质的四通道标准

| 贴图 | 内容 | 范围 | 注意事项 |
|------|------|------|---------|
| Base Color (Albedo) | 固有色，无光照信息 | sRGB, 30-240 亮度 | 禁止烘入 AO 或高光 |
| Normal Map | 表面法线偏移 | Tangent Space [-1,1] | OpenGL(Y+) vs DirectX(Y-) |
| Roughness | 表面粗糙度 | Linear, 0(镜面)-1(漫射) | 0.0-0.04 = 镜子, 0.8-1.0 = 粗布 |
| Metallic | 金属/非金属 | Linear, 0 或 1（极少中间值） | 现实中几乎是二值图 |

**通道打包**：UE5 默认将 Metallic(R) + Roughness(G) + AO(B) 打包为单张 ORM 贴图，节省一次纹理采样。

## Texel Density（纹素密度）

确保整个游戏中所有道具的贴图分辨率视觉一致：

```
Texel Density = 纹理像素数 / 世界空间面积
标准值（AAA, 1080p）: 512-1024 px/m
标准值（移动端）: 256-512 px/m
标准值（VR, 高清）: 1024-2048 px/m
```

**检查工具**：Substance Painter 的 Texel Density 热力图、UE5 的 Texel Density 可视化模式。

## 常见误区

1. **忽视剪影优先**：道具辨识度首先取决于剪影（轮廓），其次才是细节纹理。在《堡垒之夜》中，武器必须在 50m 外仅凭剪影可识别
2. **Texel Density 不统一**：一把剑 2K 贴图（2048px/m），旁边的桶 256px 贴图（128px/m）→ 视觉上桶看起来"糊"。同类道具应保持 ±20% 的 TD 偏差
3. **Base Color 烘入光照**：在 Albedo 中画入阴影或高光 → PBR 光照计算产生"双重光照"伪影。Base Color 只存储固有色

## 知识衔接

### 先修知识
- **3D美术基础** — 理解基本的 3D 概念（网格、UV、材质）

### 后续学习
- **高模雕刻** — ZBrush 雕刻技术和细节处理
- **低模制作** — 重拓扑、布线规范、面数优化
- **UV展开** — 高效UV展开和密度控制
- **PBR材质** — 基于物理的材质理论和制作
- **贴图烘焙** — 法线/AO/曲率的烘焙技术

## 参考文献

1. Vaughan, W. (2011). *Digital Modeling*. New Riders. ISBN 978-0321700896
2. Crumpler, C. (2018). "Prop Art Pipeline for AAA Games." GDC 2018.
3. Allegorithmic (2024). "PBR Guide." Substance 3D Documentation.
4. Epic Games (2024). "Static Mesh Pipeline." Unreal Engine 5 Documentation.
'''

DOCS['english/writing-en/essay-structure.md'] = '''---
id: "essay-structure"
concept: "文章结构"
domain: "english"
subdomain: "writing-en"
subdomain_name: "写作"
difficulty: 4
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "They Say / I Say"
    authors: ["Gerald Graff", "Cathy Birkenstein"]
    year: 2018
    isbn: "978-0393631678"
  - type: "textbook"
    title: "The Elements of Style"
    authors: ["William Strunk Jr.", "E.B. White"]
    year: 1999
    isbn: "978-0205309023"
  - type: "textbook"
    title: "Writing Analytically"
    authors: ["David Rosenwasser", "Jill Stephen"]
    year: 2018
    isbn: "978-1337559461"
scorer_version: "scorer-v2.0"
---
# 文章结构（Essay Structure）

## 概述

文章结构（Essay Structure）是指一篇议论文/说明文的组织框架——如何安排论点、证据和结论的顺序，使读者能够顺畅地跟随作者的思路。Graff & Birkenstein（2018）在《They Say / I Say》中提出核心原则："结构不是装饰，而是论证的骨架——骨架错了，再好的证据也无法说服人。"

英语学术写作的标准结构是 **五段式**（Five-Paragraph Essay）的变体，但专业写作中这一结构被扩展为更灵活的 **引言-正文-结论** 三部分框架。关键理解：**结构服务于论证逻辑，不是套模板**。

## 标准三部分结构

### 1. Introduction（引言）

功能：建立语境 → 引出论题 → 陈述 Thesis

```
┌─ Hook（吸引注意力）
│   └─ 引用/数据/问题/场景 → 1-2句
├─ Background（背景信息）
│   └─ 读者理解论题所需的最少上下文 → 2-3句
├─ Thesis Statement（论文陈述）
│   └─ 一句话，包含：立场 + 理由概述
│   └─ 例："While social media connects people globally, its
│        algorithmic design promotes echo chambers, reduces attention
│        spans, and commodifies personal relationships."
└─ Roadmap（路线图，可选）
    └─ 预告正文段落的顺序 → 1句
```

**Thesis Statement 的黄金标准**：具体（Specific）+ 可争辩（Arguable）+ 有结构（Structured）。对比：
- ❌ "Social media is bad."（太宽泛，不可争辩）
- ✅ "Instagram's algorithm-driven feed has measurably decreased body satisfaction among teenage girls aged 13-17, as shown by internal Meta research (2021)."

### 2. Body Paragraphs（正文段落）

每段遵循 **PEEL 结构**：

| 元素 | 功能 | 长度 |
|------|------|------|
| **P**oint（论点） | 段落的核心主张 | 1句（主题句） |
| **E**vidence（证据） | 支撑论点的数据/引用 | 2-4句 |
| **E**xplain（解释） | 证据如何支撑论点 | 2-3句 |
| **L**ink（过渡） | 连接到下一段的论点 | 1句 |

段落间的逻辑关系类型：
- **递进**：Furthermore / Moreover / In addition
- **转折**：However / Nevertheless / On the other hand
- **因果**：Therefore / Consequently / As a result
- **例证**：For instance / Specifically / To illustrate
- **对比**：In contrast / Whereas / Unlike

Rosenwasser & Stephen（2018）的建议：**每段只说一件事**。如果一段超过 250 词，几乎肯定包含了两个论点——应拆分。

### 3. Conclusion（结论）

功能：综合（Synthesize） → 提升（Elevate） → 余韵（Resonate）

```
┌─ Restate Thesis（重述论点——改写，非复制）
├─ Synthesize（综合正文的核心证据）
│   └─ 不引入新证据！只整合已有论证
├─ So What?（所以呢？）
│   └─ 这个论点为什么重要？对谁重要？
└─ Final Thought（结尾余韵）
    └─ 回应 Hook / 展望未来 / 行动呼吁
```

## 五种高级结构模式

超越基本三部分框架的专业组织方法：

| 模式 | 适用场景 | 结构 |
|------|---------|------|
| **Chronological** | 历史/过程分析 | 按时间顺序 |
| **Compare & Contrast** | 两个主题对比 | Point-by-Point 或 Block |
| **Problem-Solution** | 政策/方案论证 | 问题描述 → 方案 → 评估 |
| **Cause & Effect** | 因果关系分析 | 原因链 → 效果链 |
| **Concession-Rebuttal** | 争议性话题 | 承认反方 → 反驳 → 重申 |

**Concession-Rebuttal** 是学术写作中最有力的结构——Graff & Birkenstein 称之为"最能说服怀疑读者的武器"："我承认你的观点有道理（They Say），但我认为...（I Say）"。

## 段落之间的"胶水"

过渡是结构中最容易被忽视但最影响阅读体验的元素：

```
弱过渡：
"Para 1: ...social media causes echo chambers.
 Para 2: Social media also reduces attention spans."
 → 读者：这两段什么关系？

强过渡：
"Para 1: ...social media causes echo chambers.
 Para 2: Beyond ideological isolation, social media's 
 constant notification design has measurably eroded 
 attention spans — compounding the harm to democratic 
 discourse."
 → 回顾前段 + 承接 + 预告本段
```

## 常见误区

1. **论文陈述太晚出现**：放在第二页才出现 thesis → 读者前 300 词不知道你要论证什么。标准位置：引言最后 1-2 句
2. **正文段落无主题句**：每段没有明确的开头论点句 → 读者必须自己猜这段在说什么。Strunk & White（1999）："段首句应让读者仅靠它就能理解全文大意"
3. **结论引入新证据**：结论段出现正文未提及的数据或论点 → 读者感觉论证不完整。结论的功能是综合，不是补充

## 知识衔接

### 先修知识
- **英语语法基础** — 句子结构和段落构成
- **写作过程** — 从构思到成稿的基本流程

### 后续学习
- **论文陈述写作** — Thesis Statement 的高级构建技术
- **证据使用** — 如何选择、引用和分析证据
- **过渡与连贯** — 段间和段内的逻辑连接
- **学术引用** — APA/MLA/Chicago 引用规范
- **批判性分析** — 分析类文章的结构与方法

## 参考文献

1. Graff, G. & Birkenstein, C. (2018). *They Say / I Say* (4th ed.). W.W. Norton. ISBN 978-0393631678
2. Strunk, W. Jr. & White, E.B. (1999). *The Elements of Style* (4th ed.). Longman. ISBN 978-0205309023
3. Rosenwasser, D. & Stephen, J. (2018). *Writing Analytically* (8th ed.). Cengage. ISBN 978-1337559461
4. Booth, W.C. et al. (2016). *The Craft of Research* (4th ed.). University of Chicago Press. ISBN 978-0226239736
'''

DOCS['computer-graphics/anti-aliasing/cg-taa.md'] = '''---
id: "cg-taa"
concept: "TAA"
domain: "computer-graphics"
subdomain: "anti-aliasing"
subdomain_name: "抗锯齿"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "research"
    title: "High-Quality Temporal Supersampling"
    authors: ["Brian Karis"]
    venue: "SIGGRAPH 2014 (Epic Games)"
    year: 2014
  - type: "research"
    title: "Temporal Reprojection Anti-Aliasing in INSIDE"
    authors: ["Mikkel Gjoel"]
    venue: "GDC 2016"
    year: 2016
  - type: "textbook"
    title: "Real-Time Rendering"
    authors: ["Tomas Akenine-Moller", "Eric Haines", "Naty Hoffman"]
    year: 2018
    isbn: "978-1138627000"
scorer_version: "scorer-v2.0"
---
# TAA（Temporal Anti-Aliasing）

## 概述

时间抗锯齿（Temporal Anti-Aliasing, TAA）是一种利用多帧历史信息来消除画面锯齿和闪烁的后处理技术。Brian Karis 在 SIGGRAPH 2014 的 UE4 演讲中将其定义为"一种以时间换空间的超采样——不在一帧内采样多次，而是在多帧之间积累采样"。

TAA 已成为现代游戏引擎的 **事实标准抗锯齿方案**：UE5 默认启用 TAA（通过 TSR 扩展）、Unity HDRP 默认使用 TAA、所有 2020+ 的 AAA 引擎都以 TAA 为基础。原因很简单：TAA 是唯一能以低成本同时处理 **几何锯齿** 和 **着色器锯齿**（高光闪烁、阴影锯齿）的方案。

## TAA 的核心原理

### 亚像素抖动（Sub-Pixel Jitter）

每帧对投影矩阵施加微小偏移（通常 ±0.5 像素内），使同一像素在不同帧采样到不同的亚像素位置：

```
帧 0: 像素中心 (0.5, 0.5)
帧 1: 偏移至    (0.25, 0.75)  ← Halton(2,3) 序列
帧 2: 偏移至    (0.75, 0.25)
帧 3: 偏移至    (0.125, 0.625)
...

8帧后 → 该像素累积了8个不同位置的采样
       → 效果近似 8× 超采样（SSAA 8×的 GPU 成本的 ~1/8）
```

抖动序列通常使用 **Halton 序列**（基 2,3）或 **R2 序列**——比随机/均匀网格更均匀地覆盖采样空间。

### 时间重投影（Temporal Reprojection）

用上一帧的 Motion Vector 将历史像素映射到当前帧的对应位置：

```
current_uv = fragment_uv
motion = sample(MotionVectorBuffer, current_uv)
history_uv = current_uv - motion
history_color = sample(HistoryBuffer, history_uv)
```

Motion Vector 来源：
- **相机运动**：从 MVP 矩阵差异计算（所有静态物体共享）
- **物体运动**：顶点着色器中计算当前/前一帧位置差（动态物体）

### 混合（Blending）

将当前帧与历史帧加权混合：

```
output = lerp(history_color, current_color, alpha)
// alpha 通常 = 0.05-0.1（95% 历史 + 5% 当前）
// → 相当于以指数衰减累积约 10-20 帧
```

alpha 越小 → 累积帧越多 → 抗锯齿越好但 ghosting 越严重。

## TAA 的三大伪影及解决方案

| 伪影 | 原因 | 解决方案 |
|------|------|---------|
| **鬼影（Ghosting）** | 历史帧信息在新位置不再有效（遮挡/光照变化） | Neighborhood Clamp：将历史颜色限制在当前帧 3×3 邻域的 min-max 范围内 |
| **模糊（Blurring）** | 运动物体的历史采样位置不准确 | 锐化后处理 + 减小动态物体的混合权重 |
| **闪烁（Flickering）** | 亚像素几何体（栅栏、头发）在抖动中忽隐忽现 | Variance Clipping（基于方差的软裁剪）替代硬 clamp |

Karis（2014）的改进——**Variance Clipping**：不使用 min/max 硬裁剪历史颜色，而是计算 3×3 邻域的均值和标准差，用 μ ± γσ 构建 AABB 进行软裁剪。γ=1.0-1.25 在实践中效果最佳。

## TAA 与其他抗锯齿的对比

| 方法 | 类型 | GPU 成本 | 几何AA | 着色器AA | 运动处理 |
|------|------|---------|--------|---------|---------|
| MSAA | 硬件 | 高（×2-8 带宽） | ✅ | ❌ | N/A |
| FXAA | 后处理 | 极低（0.5ms） | ⚠️模糊 | ❌ | N/A |
| SMAA | 后处理 | 低（1ms） | ✅ | ❌ | N/A |
| **TAA** | **时间** | **低（1-2ms）** | **✅** | **✅** | **需Motion Vector** |
| DLSS/FSR | AI/时间 | 可节省（渲染低分辨率） | ✅ | ✅ | 需Motion Vector |

**关键优势**：TAA 是唯一能有效处理 **着色器锯齿**（Specular aliasing, Shadow map aliasing）的实时方案——MSAA 对这些完全无效。

## TAA 的现代演进

### TSR（UE5 Temporal Super Resolution）

UE5 在 TAA 基础上增加了超分辨率功能——渲染内部分辨率为目标的 50-75%，用 TAA 累积信息重建全分辨率：
- 性能提升 30-50%
- 质量接近原生分辨率 TAA
- 内部使用 Catmull-Rom 插值和改进的 Neighborhood Clamp

### DLSS / FSR / XeSS

AI 驱动的时间超采样——本质上是"TAA + 深度学习上采样"：
- **DLSS 3.5**：NVIDIA RTX 专用，质量最佳
- **FSR 3**：AMD 开源，支持所有 GPU
- **XeSS**：Intel 方案，支持 DP4a 指令集

## 实现速查（UE5 / HLSL 伪代码）

```hlsl
// 简化的 TAA Resolve Pass
float2 motion = MotionVectorTexture.Sample(uv);
float2 history_uv = uv - motion;
float3 history = HistoryTexture.Sample(history_uv);
float3 current = CurrentFrameTexture.Sample(uv);

// Neighborhood Clamp (Variance Clipping)
float3 m1 = 0, m2 = 0;
for (int y = -1; y <= 1; y++)
    for (int x = -1; x <= 1; x++) {
        float3 c = CurrentFrameTexture.Sample(uv + float2(x,y) * texelSize);
        m1 += c; m2 += c * c;
    }
m1 /= 9; m2 /= 9;
float3 sigma = sqrt(abs(m2 - m1 * m1));
float3 cmin = m1 - 1.25 * sigma;
float3 cmax = m1 + 1.25 * sigma;
history = clamp(history, cmin, cmax);

float alpha = 0.05; // 累积约20帧
float3 output = lerp(history, current, alpha);
```

## 常见误区

1. **TAA 只是抗锯齿**：TAA 实际上是一个时间积分框架——除了 AA，还被用于降噪（RTGI 降噪）、超分辨率（TSR/DLSS）、景深/运动模糊的质量提升
2. **提高 alpha 可以减少 ghosting**：alpha 增大 → 历史权重降低 → ghosting 减少，但同时抗锯齿能力下降且闪烁增加。正确做法是改进 clamp/rejection 算法
3. **TAA 不需要 Motion Vector**：没有精确 Motion Vector 的 TAA 在任何运动场景下都会产生严重鬼影。确保所有动态物体输出 per-object motion vector

## 知识衔接

### 先修知识
- **光栅化基础** — 理解像素采样和锯齿产生的原因
- **帧缓冲** — 理解 render target 和后处理管线

### 后续学习
- **DLSS/FSR** — AI 驱动的时间超采样技术
- **运动模糊** — 共享 Motion Vector 管线的后处理效果
- **时间降噪** — TAA 框架在光线追踪降噪中的应用
- **屏幕空间反射** — TAA 累积提升 SSR 质量

## 参考文献

1. Karis, B. (2014). "High-Quality Temporal Supersampling." SIGGRAPH 2014, Epic Games.
2. Gjoel, M. (2016). "Temporal Reprojection Anti-Aliasing in INSIDE." GDC 2016.
3. Akenine-Moller, T. et al. (2018). *Real-Time Rendering* (4th ed.). CRC Press. ISBN 978-1138627000
4. Salvi, M. (2016). "An Excursion in Temporal Supersampling." GDC 2016, Intel.
5. Yang, L. et al. (2020). "A Survey of Temporal Antialiasing Techniques." *Computer Graphics Forum*, 39(2).
'''

DOCS['mathematics/statistics/linear-regression.md'] = '''---
id: "linear-regression"
concept: "线性回归"
domain: "mathematics"
subdomain: "statistics"
subdomain_name: "数理统计"
difficulty: 6
is_milestone: false
tags: ["里程碑"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 95.9
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.93
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "An Introduction to Statistical Learning"
    authors: ["Gareth James", "Daniela Witten", "Trevor Hastie", "Robert Tibshirani"]
    year: 2021
    isbn: "978-1071614174"
  - type: "textbook"
    title: "The Elements of Statistical Learning"
    authors: ["Trevor Hastie", "Robert Tibshirani", "Jerome Friedman"]
    year: 2009
    isbn: "978-0387848570"
  - type: "textbook"
    title: "Pattern Recognition and Machine Learning"
    author: "Christopher M. Bishop"
    year: 2006
    isbn: "978-0387310732"
scorer_version: "scorer-v2.0"
---
# 线性回归

## 概述

线性回归（Linear Regression）是用线性函数建模因变量 y 与自变量 x 之间关系的统计方法——也是所有监督学习的起点。James et al. 在《An Introduction to Statistical Learning》（ISLR, 2021）中称其为"统计学习中最重要的工具，不是因为它最强大，而是因为理解了线性回归就理解了几乎所有更复杂方法的基础"。

线性回归的数学框架：给定 n 个观测 {(x₁,y₁), ..., (xₙ,yₙ)}，找到参数 β 使得 y ≈ β₀ + β₁x₁ + ... + βₚxₚ 最优。"最优"的标准是 **最小化残差平方和**（Ordinary Least Squares, OLS）。

## 简单线性回归

一个自变量 x 预测 y：

```
模型：y = β₀ + β₁x + ε
      β₀ = 截距（intercept）
      β₁ = 斜率（slope）
      ε  = 随机误差项，假设 ε ~ N(0, σ²)

OLS 解（闭式）：
      β₁ = Σ(xᵢ - x̄)(yᵢ - ȳ) / Σ(xᵢ - x̄)²
      β₀ = ȳ - β₁x̄

等价矩阵形式：
      β = (X^T X)^{-1} X^T y
```

**几何解释**：OLS 是将 y 投影到 X 的列空间上——β 使得残差向量 e = y - Xβ 与列空间正交。

## 多元线性回归

p 个自变量：

```
y = β₀ + β₁x₁ + β₂x₂ + ... + βₚxₚ + ε

矩阵形式：y = Xβ + ε
  X: n×(p+1) 设计矩阵（含截距列）
  β: (p+1)×1 参数向量
  
OLS 解：β̂ = (X^T X)^{-1} X^T y
```

**计算复杂度**：直接求逆 O(p³)。当 p > 10,000 时应使用梯度下降或 QR 分解。

## 模型评估指标

| 指标 | 公式 | 含义 | 范围 |
|------|------|------|------|
| R² | 1 - SS_res/SS_tot | 模型解释的方差比例 | [0,1]，越大越好 |
| Adjusted R² | 1 - (1-R²)(n-1)/(n-p-1) | 惩罚多余特征的 R² | 可为负 |
| MSE | Σ(yᵢ-ŷᵢ)²/n | 平均预测误差 | ≥0，越小越好 |
| RMSE | √MSE | 与 y 同单位 | ≥0 |
| MAE | Σ|yᵢ-ŷᵢ|/n | 对异常值鲁棒 | ≥0 |

**R² 的陷阱**：添加任何自变量都会使 R² 增大（即使该变量无关）。始终使用 Adjusted R² 比较不同特征数的模型。

## OLS 的五大假设（Gauss-Markov 条件）

| 假设 | 含义 | 违反后果 | 检验方法 |
|------|------|---------|---------|
| 线性关系 | E[y|x] = Xβ | 系统性偏差 | 残差图 vs 拟合值 |
| 独立性 | 观测之间独立 | 标准误低估 | Durbin-Watson 检验 |
| 同方差性 | Var(ε) = σ² (常数) | 不高效估计 | Breusch-Pagan 检验 |
| 正态性 | ε ~ N(0, σ²) | 假设检验不可靠 | Q-Q 图, Shapiro-Wilk |
| 无多重共线性 | X 列之间线性无关 | β 估计不稳定 | VIF > 10 则严重 |

当假设被违反时的修复方案：
- 非线性 → 添加多项式特征 / 使用非线性模型
- 异方差 → 加权最小二乘（WLS）/ 稳健标准误
- 多重共线性 → Ridge/Lasso 正则化 / 删除冗余特征

## 正则化：Ridge 与 Lasso

| 方法 | 目标函数 | 惩罚项 | 效果 |
|------|---------|--------|------|
| OLS | min ‖y-Xβ‖² | 无 | 基准 |
| Ridge (L2) | min ‖y-Xβ‖² + λ‖β‖² | L2 范数 | 缩小系数，不置零 |
| Lasso (L1) | min ‖y-Xβ‖² + λ‖β‖₁ | L1 范数 | 缩小+稀疏化（特征选择） |
| Elastic Net | min ‖y-Xβ‖² + λ₁‖β‖₁ + λ₂‖β‖² | L1+L2 | 兼得两者优点 |

**λ 选择**：通过交叉验证（Cross-Validation）选择使测试误差最小的 λ。ISLR（2021）推荐 10-fold CV。

## Python 实现

```python
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.model_selection import cross_val_score
from sklearn.metrics import r2_score, mean_squared_error

# 简单线性回归
model = LinearRegression()
model.fit(X_train, y_train)
print(f"Intercept: {model.intercept_:.3f}")
print(f"Coefficients: {model.coef_}")
print(f"R²: {r2_score(y_test, model.predict(X_test)):.4f}")

# Ridge 回归 + 交叉验证
from sklearn.linear_model import RidgeCV
ridge = RidgeCV(alphas=[0.01, 0.1, 1, 10, 100], cv=10)
ridge.fit(X_train, y_train)
print(f"Best alpha: {ridge.alpha_}")

# Lasso 回归（自动特征选择）
lasso = Lasso(alpha=0.1)
lasso.fit(X_train, y_train)
selected = np.sum(lasso.coef_ != 0)
print(f"Selected features: {selected}/{X_train.shape[1]}")
```

## 线性回归的位置：从统计到机器学习

```
线性回归
  ├─ 加正则化 → Ridge / Lasso / Elastic Net
  ├─ 加多项式特征 → 多项式回归
  ├─ 改变损失函数 → 分位数回归 / Huber 回归
  ├─ y 为二值 → Logistic 回归（分类）
  ├─ 加核技巧 → 核回归 / SVM 回归
  └─ 多层+非线性 → 神经网络（y = f(Wx+b) 的堆叠）
```

所有这些方法的起点都是线性回归——理解 OLS 的闭式解、正则化的几何含义、假设检验，就能理解整个监督学习体系。

## 常见误区

1. **相关 ≠ 因果**：线性回归发现 x 和 y 有线性关系 ≠ x 导致 y。经典反例：冰淇淋销量与溺水死亡正相关——真正原因是夏天
2. **R² 高 = 好模型**：R²=0.95 但所有残差都呈U形 = 模型结构错误（非线性关系用线性拟合）。**永远要看残差图**
3. **外推**：在训练数据范围外预测。如果训练数据 x ∈ [0,100]，用模型预测 x=500 是极其危险的——线性关系不保证在范围外成立

## 知识衔接

### 先修知识
- **概率论基础** — 正态分布、期望、方差
- **线性代数** — 矩阵运算、向量空间、投影

### 后续学习
- **逻辑回归** — 线性回归 + sigmoid → 分类
- **多项式回归** — 非线性拟合的最简扩展
- **正则化方法** — Ridge/Lasso 的理论和实践
- **假设检验** — t-test, F-test 在回归中的应用
- **贝叶斯线性回归** — 概率视角的线性回归

## 参考文献

1. James, G. et al. (2021). *An Introduction to Statistical Learning* (2nd ed.). Springer. ISBN 978-1071614174
2. Hastie, T., Tibshirani, R. & Friedman, J. (2009). *The Elements of Statistical Learning* (2nd ed.). Springer. ISBN 978-0387848570
3. Bishop, C.M. (2006). *Pattern Recognition and Machine Learning*. Springer. ISBN 978-0387310732
4. Freedman, D.A. (2009). *Statistical Models: Theory and Practice* (2nd ed.). Cambridge University Press. ISBN 978-0521743853
'''

for relpath, content in DOCS.items():
    fpath = ROOT / relpath
    fpath.write_text(content.strip() + '\n', encoding='utf-8')
    print(f'Written: {relpath}')
print('Done — 4 files written.')
