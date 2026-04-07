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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
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

实时捕获（Runtime Capture）是一种在游戏运行时通过 Render Target 将动态3D场景或骨骼动画实时渲染并保存为序列帧纹理的技术流程。与离线烘焙序列帧不同，实时捕获的所有帧数据均在运行时逐帧写入 Render Target 的像素缓冲区，最终形成可供 Sprite Sheet 系统驱动的动态纹理图集。这一技术的核心意义在于：角色的表情变化、布料模拟、程序化动画等无法预先烘焙的动态效果，可以被即时转化为轻量的序列帧特效，从而在低端设备或大批量实例化场景中以极低的 Draw Call 代价播放。

该技术方案最早在 Unreal Engine 4.20 版本引入的 Scene Capture Component 2D 的基础上形成工程实践，开发者利用 `USceneCaptureComponent2D` 每帧向指定 `UTextureRenderTarget2D` 写入渲染结果，再通过 Blueprint 或 C++ 调度捕获节奏。在虚幻引擎的移动端项目中，这一方案常被用于将复杂的骨骼动画角色批量转换为粒子特效，使单场景同屏角色数量从 50 提升至数百甚至数千。

## 核心原理

### Render Target 帧写入机制

实时捕获的基础单元是 `UTextureRenderTarget2D`，其格式通常设置为 `RTF_RGBA8` 或 `RTF_RGBA16f`，分别对应 4 字节和 8 字节每像素的存储精度。每次捕获触发时，引擎调用 `SceneCaptureComponent2D::CaptureScene()`，将当前帧的场景投影写入该 Render Target。捕获分辨率与序列帧列数之间存在固定关系：若目标 Sprite Sheet 为 8×8 布局（共64帧），且每帧分辨率为 128×128，则 Render Target 的总尺寸需为 1024×1024，即满足公式：

```
RT_Width  = Frame_Width  × Columns
RT_Height = Frame_Height × Rows
```

开发者必须在捕获前精确计算 UV 偏移量 `(col/Columns, row/Rows)`，否则相邻帧之间会产生像素渗色（Bleeding）。

### 捕获调度与时序控制

实时捕获不能简单地在每个 `Tick` 均执行 `CaptureScene()`，因为这会导致 GPU 在单帧内承受 N 次完整的场景渲染代价。标准做法是利用 **逐帧分时捕获（Per-Frame Staggered Capture）**：在一次完整捕获周期内，每个引擎 Tick 仅捕获一帧画面，同时将目标对象的动画时间推进 `1/TargetFPS` 秒。例如，捕获一段 30 帧、每秒 24fps 的跑步动画，完整捕获周期为 `30 / 24 ≈ 1.25` 秒的游戏时间。此期间需要暂停主逻辑更新或将捕获对象隔离至独立子关卡（Sublevel），以避免场景中其他元素进入捕获视野并污染序列帧内容。

### 动画状态与摄像机的精确对齐

捕获用的正交摄像机（Orthographic Camera）需与目标对象的包围盒（Bounding Box）严格对齐。`OrthoWidth` 参数设置为对象最大帧包围盒宽度的 1.05 倍（预留 5% 边距防裁切），摄像机位置锁定在对象中心点的正前方固定距离处。若捕获的是 VAT 顶点动画驱动的网格体，还需在捕获前通过 `SetScalarParameterValue` 将材质的 `AnimationTime` 参数手动推进至对应帧时间，而不依赖引擎自动的材质时间轴，确保帧与帧之间的动画状态精确可控、完全可复现。

### Alpha 通道与背景隔离

序列帧特效要求捕获结果具备有效的透明度信息。实时捕获时必须将背景设置为纯黑 `(0,0,0,0)` 并开启 `bCaptureEveryFrame = false`，同时将 Scene Capture 的 `CaptureSource` 设为 `SCS_FinalColorHDR` 或 `SCS_SceneColorHDR`。捕获用的材质须在 Blend Mode 设为 `Masked` 或 `Translucent`，并将 Opacity Mask 输出到 Alpha 通道，否则运行时合成时对象边缘会出现黑边（Premultiplied Alpha 误差）。

## 实际应用

**移动端大规模 NPC 特效化**：在某开放世界手游项目中，开发团队对 12 种 NPC 角色的行走、奔跑、攻击共 36 段骨骼动画执行实时捕获，每段动画输出为 8×8 的 512×512 PNG 序列帧图集。捕获完成后，这些 NPC 由 GPU Particle System 驱动，单次 Draw Call 即可渲染 800 个实例，相比原始骨骼动画方案节省约 94% 的渲染耗时。

**程序化布料的序列帧化**：布料模拟结果具有随机性，无法离线预烘焙，实时捕获是唯一可行的序列帧化方案。具体做法是在捕获开始前固定物理模拟的随机种子（`FMath::SRandInit(42)`），保证每次捕获的布料形态完全一致，再按上述分时调度逐帧写入 Render Target。

**爆炸特效的动态变体生成**：Niagara 粒子驱动的爆炸效果可借助实时捕获在运行时生成多份外观差异化的序列帧，每份仅改变粒子系统的随机种子参数。游戏中随机选取其中一份序列帧播放，视觉上完全消除了重复感，而内存代价远低于存储多套骨骼动画资产。

## 常见误区

**误区一：认为实时捕获可以替代离线烘焙**。实时捕获在运行时占用 GPU 渲染带宽，每次捕获周期会造成游戏帧率下降。标准流程是在关卡加载阶段或专用的预捕获场景中完成捕获，将结果持久化为纹理资产后再用于正式游戏逻辑，而非在战斗过程中实时执行捕获写入。若在高负载帧中触发捕获，GPU 渲染耗时可能飙升 3～5 倍。

**误区二：忽略 sRGB 与 Linear 色彩空间不一致问题**。Render Target 的 `bSRGB` 标志与序列帧材质的采样方式必须匹配。若 Render Target 以 sRGB 格式写入但材质以 Linear 空间读取（或反之），序列帧播放时颜色会出现明显偏暗或偏亮的色差，这一问题在暗部细节丰富的角色皮肤捕获中尤为明显，但开发者往往误认为是光照设置错误。

**误区三：将捕获帧率等同于播放帧率**。捕获阶段以每引擎帧写入一帧序列帧数据，实际捕获帧率受 `TargetFrameRate` 限制；而播放阶段的帧率由 Sprite Sheet 材质中的 `FlipBook` 节点的 `FramesPerSecond` 参数独立控制。两者解耦意味着可以用 12fps 的捕获数据以 24fps 播放（产生补帧效果），也可以反向慢放，但必须在设计阶段明确区分这两个参数的含义。

## 知识关联

实时捕获建立在 **VAT 顶点动画** 技术之上：VAT 将顶点位移信息烘焙为纹理驱动网格体变形，而实时捕获则将这种已由材质驱动的动态网格体的最终渲染结果再次"拍照"写入新的纹理序列。两者的组合使得 GPU 端的顶点形变既能保留物理真实感，又能以最低代价批量复用。掌握 VAT 材质中 `AnimationTime` 参数的手动推进方式，是实时捕获时序控制的前置技能。

实时捕获的产出物——序列帧图集——直接输入 **Sprite Sheet 工具**进行后处理：图集的 UV 分区信息、列数行数、每帧持续时间等元数据均需在 Sprite Sheet 工具中注册并生成对应的 `FlipBook` 材质实例。因此实时捕获阶段输出的纹理命名规范（如 `T_Char_Run_8x8_512`）须与 Sprite Sheet 工具的导入格式约定保持一致，否则自动解析列数与行数时会出现帧序错乱。