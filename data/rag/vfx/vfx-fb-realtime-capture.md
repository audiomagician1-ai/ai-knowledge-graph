---
id: "vfx-fb-realtime-capture"
concept: "实时捕获"
domain: "vfx"
subdomain: "flipbook"
subdomain_name: "序列帧特效"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 实时捕获

## 概述

实时捕获（Runtime Capture）是序列帧特效制作中的一种动态内容生成技术，其核心机制是在游戏运行时通过Render Target将三维场景或动画实时渲染并写入纹理序列，从而生成可供Sprite Sheet使用的动态帧数据。与离线预烘焙的静态序列帧不同，实时捕获的帧内容在每次运行时都可以根据当前场景状态动态生成，因此能够反映实时变化的光照、颜色或几何形变。

该技术在虚幻引擎（Unreal Engine）体系中最早随着Render Target功能的成熟而被特效艺术家广泛采用，尤其在UE4.20之后，Scene Capture 2D组件的性能开销大幅降低，使得每帧捕获多张Render Target成为可行方案。实时捕获的意义在于它打通了三维动画与二维序列帧特效之间的实时数据通道——VAT顶点动画驱动的网格体形变可以在运行时被逐帧"拍摄"下来，转化为轻量的二维纹理序列。

这项技术的核心价值体现在两个方面：第一，它允许基于玩家输入或环境参数生成个性化的序列帧内容，例如根据角色皮肤颜色实时生成对应色调的爆炸特效帧；第二，通过将高成本的粒子模拟或布料模拟提前"烤入"Render Target序列，可以将后续播放的GPU开销降低至单张纹理采样级别。

## 核心原理

### Scene Capture 2D 与 Render Target 写入流程

实时捕获的基础组件是`Scene Capture 2D`，它本质上是一个正交投影或透视投影的虚拟摄像机，将指定Layer的场景内容渲染到一张`Render Target 2D`纹理上。捕获参数中最关键的是`Capture Source`枚举，选择`Final Color (LDR) in RGB`时输出的是经过后处理的8位颜色，而选择`SceneDepth in R`则可以同时捕获深度信息用于后续重建法线。

Render Target的分辨率直接决定单帧的精度，常见的序列帧捕获分辨率为256×256或512×512，捕获完成后通过蓝图节点`Export Render Target`或`Copy Texture`将像素数据写入内存中的Texture2D缓冲。若需在一帧内完成16张序列帧的捕获，需要在`EndOfFrameRendering`回调中串行提交16次捕获指令，每次移动捕获对象到下一个姿态位置后触发一次`Capture Scene`。

### 帧序列的时序控制与姿态驱动

实时捕获最复杂的部分是时序控制逻辑，即如何在有限帧数（通常16帧或32帧）内均匀采样完整动画周期。对于一段时长为`T`秒、目标帧数为`N`的动画，每次捕获前需要将动画时间轴推进`T/N`秒，公式为：

```
采样时间点 t_i = (i / N) × T,  i ∈ [0, N-1]
```

对于VAT顶点动画驱动的网格体，姿态驱动通过修改材质的`TimeOffset`标量参数来精确定位到特定动画帧，无需播放Timeline，可直接跳帧采样，这是实时捕获与传统录屏的本质区别——它是**按需寻址**而非线性录制。

### Render Target 纹理图集的打包策略

单次捕获生成的是独立的Render Target序列，最终需要通过蓝图或C++逻辑将其打包为Sprite Sheet格式的纹理图集（Texture Atlas）。打包时使用`DrawMaterialToRenderTarget`节点将每帧按`floor(i / cols) × frameHeight`的纵向偏移和`(i % cols) × frameWidth`的横向偏移写入目标图集。对于4×4排列的16帧图集，最终输出纹理尺寸为单帧分辨率的4倍，例如单帧256×256则图集为1024×1024。图集打包完成后，原始的16张独立Render Target可立即释放显存，整个序列仅占用一张1024×1024 RGBA8纹理约4MB显存。

## 实际应用

**角色死亡特效的个性化捕获**：在支持自定义外观的RPG游戏中，角色死亡时的溶解特效序列帧需要与角色当前的染色方案匹配。实时捕获方案在角色死亡触发时，将当前穿戴的材质参数传递给Scene Capture的后处理材质，在0.5秒内完成32帧的溶解动画捕获并打包图集，随后以Sprite Sheet形式播放，整体捕获开销约为2个游戏帧（33ms）。

**液体模拟序列帧的运行时烘焙**：Niagara液体模拟在低端设备上实时运行开销极高，但通过实时捕获可以在高端设备上预先将20帧液体翻涌动画捕获为512×512的图集，然后以纹理流方式发送给低端设备实例播放，将GPU开销从约8ms/帧的粒子模拟降低至0.3ms/帧的纹理采样。

**环境光照变化的序列帧同步**：场景昼夜切换时，预烘焙的静态序列帧无法反映光照变化。实时捕获可在昼夜切换完成后的1帧内重新捕获火焰、光晕等特效的序列帧内容，确保序列帧的高光颜色与当前天光方向匹配。

## 常见误区

**误区一：认为实时捕获与录屏（Screen Capture）等价**。实时捕获使用Scene Capture 2D组件针对特定Layer或Actor进行隔离渲染，背景透明，仅捕获目标对象；而录屏是对完整屏幕内容的像素复制。混淆两者会导致捕获结果包含不需要的背景元素，且无法使用Alpha通道进行透明合成。Scene Capture 2D的`Primitive Render Mode`设置为`Use ShowOnly List`可以精确控制哪些Actor参与捕获，这是实时捕获工作流中的必要配置步骤。

**误区二：认为捕获分辨率越高越好**。实时捕获的目标是生成用于Sprite Sheet播放的序列帧，最终显示尺寸受粒子屏幕占比限制。若粒子在屏幕上的最大显示尺寸为128×128像素，使用512×512的捕获分辨率不会带来视觉收益，却会使图集纹理从256KB膨胀至4MB，显存占用增加16倍，并显著增加捕获写入时的带宽压力。正确做法是根据特效的最大屏幕显示分辨率乘以1.5的过采样系数来确定单帧捕获尺寸。

**误区三：认为实时捕获可以在每帧持续运行**。Scene Capture 2D若设置为`Capture Every Frame`，其渲染开销等同于添加了一个完整的额外摄像机渲染Pass，在1080p下约增加4-8ms的GPU帧时间。实时捕获应设计为**一次性触发事件**：在特定条件满足时完成N帧的快速捕获，然后立即禁用组件。将Scene Capture 2D的`Capture Source`与触发逻辑绑定到Game Event而非Tick是性能优化的关键原则。

## 知识关联

实时捕获的上游依赖是**VAT顶点动画**技术：VAT将骨骼动画或物理模拟的顶点位移编码为纹理，提供了可以通过`TimeOffset`参数精确寻址的动画数据。正是由于VAT的按需寻址特性，实时捕获才能实现跨帧跳跃采样，而不需要线性等待动画播放到目标时间点。若目标动画是传统骨骼动画而非VAT，则需要借助动画蓝图的`Montage Jump To Section`配合捕获时序控制，实现等效的帧定位功能，但精度低于VAT的浮点纹理寻址。

实时捕获的下游工具是**Sprite Sheet工具**，其负责解析捕获流程生成的图集纹理，提供帧索引、播放速率、UV偏移计算等功能，并将序列帧数据整合到Niagara粒子系统的Sub UV模块中。实时捕获提供的图集格式（行列数、帧分辨率、Alpha通道约定）必须与Sprite Sheet工具的输入规范精确对齐，否则会出现帧错位或透明度异常。两者之间的数据接口是一张包含帧数元信息的Render Target以及记录行列数的整型参数对`(NumColumns, NumRows)`。