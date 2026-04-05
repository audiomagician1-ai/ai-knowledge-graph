---
id: "ta-lod-crowd"
concept: "人群LOD"
domain: "technical-art"
subdomain: "lod-strategy"
subdomain_name: "LOD策略"
difficulty: 3
is_milestone: false
tags: ["进阶"]

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
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-31
---

# 人群LOD

## 概述

人群LOD（Crowd Level of Detail）是一种专门针对游戏场景中大量NPC同时存在时的综合性渐进简化技术。与单个角色的LOD不同，人群LOD必须同时协调**骨骼层级数量、材质批次合并、动画系统切换**三个维度的降级策略，因为单独优化任何一个维度都无法解决成百上千个动态角色带来的性能瓶颈。

该技术在2000年代中期随着《刺客信条》《战锤：维京战争》等需要展示大规模战场的游戏兴起而系统化。传统单角色LOD在100个以上NPC并存时会因DrawCall爆炸式增长（每个角色独立骨骼动画产生独立绘制调用）而失效，人群LOD通过引入GPU Instancing与骨骼纹理采样（Vertex Texture Fetch）将这一瓶颈从CPU侧转移至GPU侧。

在现代开放世界游戏中，一个城市广场场景可能需要同时渲染300-500个NPC，若全部使用标准骨骼动画，仅动画更新的CPU消耗就会超出帧预算。人群LOD将这个问题拆解为可分级管理的子问题，使同屏NPC数量提升10倍以上成为可能。

---

## 核心原理

### 骨骼简化策略：从全骨骼到伪骨骼

标准人形角色骨骼通常包含50-80根骨骼（含手指、面部骨骼），人群LOD将其划分为典型的三个等级：
- **LOD0（0-15米）**：完整骨骼，启用IK（Inverse Kinematics），约50根骨骼
- **LOD1（15-40米）**：精简骨骼，移除手指/面部/武器辅助骨骼，约20根骨骼，禁用IK计算
- **LOD2（40米以上）**：极简骨骼或直接切换为**骨骼动画纹理（BAT，Bone Animation Texture）**，仅保留根骨骼+4个肢体关节

BAT技术将每帧的骨骼变换矩阵预烘焙进一张RGBA32浮点纹理，每行存储一帧数据，每列对应一根骨骼的变换四元数。运行时顶点着色器通过`tex2Dlod()`采样该纹理重建蒙皮，完全绕过CPU侧的骨骼运算。

### 材质与DrawCall合并：GPU Instancing的限制突破

人群LOD中最关键的材质策略是将所有NPC的颜色变体打包进**颜色变化图集（Color Variation Atlas）**，并通过Instance ID索引不同的色调偏移量。这使得同一材质球的NPC可以被合并为单次GPU Instancing调用，将300个NPC的DrawCall从300次压缩至3-5次（按材质类型分组）。

Unity的Hybrid Renderer V2和Unreal的HLOD系统均实现了这一策略，但上限不同：Unity GPU Instancing单批次上限为1023个实例，Unreal的Crowd Manager默认分批大小为512。超出上限后会自动分批，因此在设计NPC材质时应尽量控制材质种类数量（建议不超过8种变体材质）以减少分批次数。

### 动画系统的三级切换

动画系统的降级是人群LOD中延迟最敏感的部分：

1. **近距离（<15米）**：完整AnimGraph，支持状态机、混合树、动态IK，每帧CPU更新骨骼Transform
2. **中距离（15-40米）**：切换为**AnimationBudgetAllocator**模式，将动画更新频率从60Hz降至15-20Hz，并在帧间进行线性插值补偿
3. **远距离（>40米）**：切换为预烘焙BAT动画，动画播放完全在GPU顶点着色器中完成，CPU端仅维护一个播放时间戳（float），内存消耗从每个角色约200字节的骨骼Transform数组降至单个float

距离阈值切换时需要添加0.5-1米的滞后区间（Hysteresis Band）防止LOD在边界反复横跳产生闪烁，具体实现为：进入下一级LOD的距离 > 退出该级LOD的距离，差值约为最大视距的2-3%。

---

## 实际应用

### 战场场景：《全战三国》中的万人同屏

《全战三国》使用了分层人群LOD方案：前排士兵（<30米）使用标准骨骼动画，中排（30-80米）使用12骨骼简化版本+2帧间插值，后排（>80米）全部替换为GPU粒子模拟的"伪NPC"——仅渲染一个带有动态纹理的Billboard，纹理内容是预渲染的奔跑动画序列（8帧循环）。这种三层方案使10000人场景的帧率从无法运行提升至目标60fps。

### 城市人群：Atlas系统与社交动画剔除

在城市场景中，NPC除移动外还需要交谈、坐下、使用道具等"社交动画"。人群LOD在此场景中会额外添加**社交动画距离门控**：距摄像机25米以外的NPC，所有包含手臂次级运动（二次动力学）的动画层被整体Mask掉，仅保留根运动（Root Motion）和主躯干动画，节省约30%的动画混合计算量。

---

## 常见误区

### 误区一：LOD切换距离使用固定世界空间阈值

很多实现直接以米为单位设置固定阈值（如40米切换到LOD2），但正确做法应基于**屏幕空间投影面积**。一个距摄像机40米的NPC在FOV 90°时占屏幕面积约0.8%，但在使用长焦镜头（FOV 30°）时同样距离会占到约7%，此时切换到极简骨骼会产生明显可见的质量劣化。正确公式为：`Screen Size = (Character Height * ProjectionMatrix[1][1]) / DistanceToCam`，当Screen Size < 0.05时切换LOD2更为准确。

### 误区二：BAT动画与骨骼动画可以无缝融合

BAT动画完全运行在GPU着色器中，无法在运行时接收程序化动画修改（如AI驾动的避障倾斜、受击反馈）。一些开发者在NPC进入BAT范围后仍尝试通过CPU修改骨骼Transform，导致CPU数据与GPU采样结果冲突，出现角色"分裂"的画面错误。BAT适合循环类型动画（行走、待机），但受击、死亡等需要物理响应的动画必须在切换回骨骼动画后才能正确播放。

### 误区三：人群LOD等同于静态网格体LOD的NPC版本

静态网格体LOD仅需要降低顶点数，而人群LOD的性能瓶颈主要在**动画更新的CPU消耗**和**DrawCall数量**，而非顶点数本身。一个仅削减顶点数但保留完整骨骼动画的"人群LOD"方案，对性能的实际提升几乎可以忽略不计。测试数据表明，将NPC从5000三角面降至500三角面（GPU几何消耗减少90%）带来的帧时间改善，远小于将骨骼从50根降至5根（CPU动画消耗减少约85%）所带来的改善。

---

## 知识关联

人群LOD直接依赖**LOD动画简化**中建立的骨骼压缩与AnimGraph分层概念——后者解决的是单个角色的动画LOD问题，而人群LOD在此基础上引入了**实例化批次管理**和**骨骼动画纹理烘焙**两个人群专属问题。理解AnimBudgetAllocator的时间分片机制是实现人群LOD中级方案的前提，因为该机制决定了每帧可以完整更新多少个骨骼动画实例的上限（通常为CPU线程每帧0.5-1ms骨骼更新预算）。

人群LOD也与**GPU Instancing**和**纹理图集策略**紧密相关：材质合批是人群LOD从DrawCall层面降低CPU压力的核心手段，而骨骼动画纹理本质上是将动画数据的存储和计算范式从CPU内存+Transform运算转向GPU纹理采样，这与静态网格体的Mesh Shader管线改造思路一脉相承。