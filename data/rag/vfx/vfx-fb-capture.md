---
id: "vfx-fb-capture"
concept: "序列帧捕获"
domain: "vfx"
subdomain: "flipbook"
subdomain_name: "序列帧特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 序列帧捕获

## 概述

序列帧捕获是指将3D软件（如Houdini、Blender）或合成软件（如After Effects）中的动态模拟结果，按照固定时间间隔逐帧渲染并导出为连续编号图像文件的工作流程。与实时渲染不同，序列帧捕获允许每帧独立计算，不受播放帧率限制，可输出高达32位浮点精度的EXR格式图像，保留完整的HDR信息供后续游戏引擎采样使用。

该技术在游戏特效领域兴起于2010年代初，随着Unity和Unreal Engine对图集纹理（Sprite Sheet / Flipbook Texture）支持的完善而逐渐标准化。2016年前后，Epic Games在官方文档中明确推荐使用512×512至2048×2048像素的Flipbook图集来表现粒子特效，序列帧捕获工作流因此成为特效美术的基础技能之一。

序列帧捕获的质量直接影响游戏中粒子效果的真实感上限。离线渲染可以使用体积散射、路径追踪等实时无法承担的算法，烟雾、火焰、水花等效果通过序列帧捕获后，用极低的运行时开销还原出接近物理真实的视觉表现。

---

## 核心原理

### 帧率与时间步长设置

捕获前必须在Houdini（或AE）中将输出帧率与目标播放帧率对齐。常见游戏特效Flipbook采用24fps或30fps，但Houdini模拟的子步数（Substeps）通常设为2~4，意味着内部计算频率可达96fps甚至更高，最终只输出与目标帧率对齐的帧。若模拟帧率（$f_{sim}$）与捕获帧率（$f_{cap}$）不匹配，每帧图像会包含时间伪影（Temporal Artifact），导致Flipbook播放时出现跳帧感。计算关系为：

$$N_{output} = \frac{T_{duration} \times f_{sim}}{step\_interval}$$

其中 $T_{duration}$ 为动画总时长（秒），$step\_interval$ 为输出步进间隔（通常为1）。

### 分辨率与图集布局

序列帧图集要求总图像分辨率为2的幂次（Power of Two），因为GPU纹理采样在非POT尺寸下会触发额外的填充计算。常见布局为8×8（64帧）或8×4（32帧），单格分辨率与总图集分辨率的关系为：

$$单格分辨率 = \frac{图集总分辨率}{列数或行数}$$

例如2048×2048的8×8图集，每格仅有256×256像素。特效美术需要在帧数与单帧清晰度之间做出权衡：烟雾类效果因边缘模糊可用64帧；火花类高频运动效果建议不少于32帧以避免明显跳跃。

### 通道打包与Alpha处理

序列帧捕获不仅输出RGB颜色，还需同步捕获以下数据并写入特定通道：

- **Alpha通道**：存储透明度遮罩，直接嵌入PNG或EXR的第4通道
- **运动矢量（Motion Vector）**：存于独立的RG两通道图像，记录相邻帧之间像素的位移方向与距离，供引擎在帧间插值时使用
- **法线信息（可选）**：存于独立贴图的RGB通道，用于支持光照响应的Lit粒子

Houdini的`Karma`或`Mantra`渲染器通过输出驱动（Output Driver）的"Extra Image Planes"功能，可在单次渲染中同时输出上述所有通道，避免多次重复渲染模拟。

---

## 实际应用

**Houdini火焰捕获实例**：在Houdini中完成PyroFX火焰模拟后，新建`Mantra`节点，将Render Range设为第1帧至第48帧，输出格式选择`OpenEXR 16-bit Half Float`。渲染完成后，使用Houdini内置的`SequenceCopy`或外部工具`ffmpeg`，将48张独立EXR合并为一张2048×1024的6×8图集（即Flipbook）。此格式可直接导入Unreal Engine的Niagara粒子系统，并在材质中用`FlipBook`节点驱动UV偏移动画。

**After Effects捕获工作流**：在AE中完成光效合成后，执行"合成 > 添加到渲染队列"，输出模块设置为PNG序列，文件命名规则必须包含帧编号占位符（如`smoke_[####].png`），确保后续合并工具能按顺序识别文件。帧率锁定为项目帧率（通常24或30fps），渲染范围精确设置到工作区入出点，避免输出多余的首尾空帧造成图集布局错位。

---

## 常见误区

**误区一：认为捕获帧数越多效果越好**  
实际上，图集总分辨率固定（如2048×2048）的前提下，帧数从32帧增加到64帧会使单帧分辨率从256×256降至256×128（若行列比不变则每格更小），烟雾细节反而因分辨率不足而损失。正确做法是根据特效运动速度选择最低够用的帧数，为单帧留出足够像素预算。

**误区二：直接用PNG序列替代EXR序列捕获高动态范围效果**  
PNG格式为8位整数（每通道0~255），无法表示亮度超过1.0的火焰核心或曝光过曝区域。若在Houdini中捕获火焰并用PNG输出，亮部会被硬截断（Clamp），导致最终在游戏中出现"亮部死白"而缺乏层次的现象。必须使用EXR 16-bit Half或32-bit Float格式保留超亮信息，待合并图集后再在引擎材质中通过色调映射（Tone Mapping）控制最终亮度表现。

**误区三：忽略首尾帧的循环对齐**  
若需要Flipbook无缝循环播放（如持续燃烧的火堆），捕获时最后一帧与第一帧之间的模拟状态必须视觉连续。Houdini中的常见做法是将模拟总帧数设为捕获帧数+1（如捕获32帧则模拟33帧），并丢弃第33帧，同时在模拟初始化时注入与结尾状态相近的初始条件，这需要在`DOP Network`中额外配置循环边界约束，而非简单截取任意一段时间范围。

---

## 知识关联

序列帧捕获的前置概念**运动矢量**直接决定了捕获时是否需要额外输出MV通道。运动矢量记录的是相邻两帧之间每个像素的屏幕空间位移（单位通常为像素/帧或NDC比例），序列帧捕获工作流需要在渲染阶段同步生成这张MV贴图，并将其与RGB图集打包到同一份文件组中，才能在引擎端实现帧间插值（Sub-frame Interpolation），大幅降低Flipbook所需的帧数同时维持流畅感。

完成序列帧捕获后，下一步工作流**Houdini烘焙**将在此基础上进一步处理：将捕获的EXR序列经过颜色空间转换（Linear转sRGB）、通道重映射（将MV从世界空间转换为UV空间）以及图集拼合（Atlas Packing）等操作，生成可直接导入Unreal Engine或Unity的最终Flipbook贴图资产。Houdini烘焙阶段的`COPs`（Compositing Operator）网络会引用序列帧捕获的原始EXR文件夹路径作为输入，因此捕获阶段的命名规范和目录结构对后续自动化烘焙流程至关重要。