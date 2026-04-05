---
id: "guiux-tech-atlas-batching"
concept: "图集与合批"
domain: "game-ui-ux"
subdomain: "ui-tech"
subdomain_name: "UI技术实现"
difficulty: 3
is_milestone: false
tags: ["ui-tech", "图集与合批"]

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
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 图集与合批

## 概述

图集（Sprite Atlas）是将多张独立小图合并为一张大纹理（通常为 2048×2048 或 4096×4096 像素）的打包策略，其核心目标是减少 GPU 渲染时的 Draw Call 数量。Unity 的 Sprite Atlas 系统会在运行时将同一图集内的所有精灵共享同一个材质实例，从而让引擎将它们合并为一次批处理提交，而非逐图发起独立的渲染命令。

图集技术最早在 2D 游戏开发中以"Texture Packing"形式出现，工具如 TexturePacker 和早期 cocos2d 的 `.plist` 格式将其规范化。Unity 在 5.6 版本引入了 Sprite Atlas（取代旧版 Sprite Packer），并在 Unity 2020 引入 Sprite Atlas V2，新增对文件夹打包和依赖追踪的支持。对于移动端 UI，一个场景存在数百张独立图片时 Draw Call 可能超过 200+，而合理使用图集后可压缩至 10～20 次，直接影响帧率和设备发热。

图集不只是节省 Draw Call 的工具，它同时影响内存布局、资源加载粒度和 AB 包拆分策略。一张未被图集收录的 64×64 小图，GPU 仍需为其分配独立的纹理采样单元，而图集将数十张同类图标共享一次纹理上传，显著降低显存带宽压力。

## 核心原理

### Draw Call 合批的触发条件

Unity UI（uGUI）的合批发生在 Canvas 重建阶段，由 `CanvasRenderer` 收集同 Canvas 下所有 UI 元素，按照**材质相同、纹理相同、不被其他元素遮挡打断**三条规则合并为 Batch。图集的作用正是让原本纹理不同的多个 Image 组件共享同一张大纹理，从而满足"纹理相同"这一条件。若两张图片分别来自 `AtlasA` 和 `AtlasB`，即使材质相同，也无法合批，Draw Call 至少为 2。

合批被打断的最常见原因是**层级穿插**：若渲染顺序为 图A（Atlas1）→ 图B（Atlas2）→ 图C（Atlas1），图C 无法与图A 合并，因为中间有来自 Atlas2 的图B 打断了连续性。这一现象在 Frame Debugger 中表现为同一图集的元素出现在多个不连续的 Batch 中，可通过调整 Hierarchy 顺序修复。

### 图集打包算法与 UV 映射

Sprite Atlas 内部使用**矩形装箱算法（Bin Packing）**，默认采用 MaxRects 策略将不同尺寸的精灵以最小浪费率塞入目标纹理。打包完成后，每个精灵的 UV 坐标被重映射为图集纹理上的子区域：若一张 128×128 的图标被放置在 2048×2048 图集的左上角，其 UV 范围为 `(0, 0)` 到 `(128/2048, 128/2048)` ≈ `(0.0625, 0.0625)`。这一 UV 偏移由 Unity 在 Sprite 的 `textureRect` 属性中自动维护，开发者无需手动处理。

图集支持设置 **Padding**（精灵间距，建议 2～4 像素）以防止纹理过滤时相邻图片像素渗入（Bleeding），这在使用双线性过滤的 UI 图标上尤为重要。过小的 Padding 会导致图标边缘出现相邻图片的颜色条纹。

### 动态图集（Dynamic Atlas）

动态图集指在运行时动态将纹理插入一张预分配大图的技术，Unity 的 UGUI 内部对字体即采用此机制（`Font Texture`）。对于游戏内动态加载的头像、皮肤图标等，第三方方案如 **Dynamic Bone Atlas** 或自实现的 `RenderTexture` 拼接可在运行时构建图集。动态图集的核心代码逻辑是维护一棵**空闲矩形树**，每次插入新图时通过 BFS 找到最小适配空格。动态图集需处理图集碎片化（Fragmentation）问题：频繁插入和删除后，空闲区域变得零散，可通过**定期重新整理（Defragmentation）**或设置最大生命周期来管理。

## 实际应用

**战斗 UI 图标合批**：手游战斗界面中，技能图标、血条装饰、状态 Buff 图标数量可达 30～50 张。将同属"战斗 HUD"分类的图标打入一张 2048×2048 图集后，这 50 次独立 Draw Call 合并为 1～3 次（取决于层级穿插），在中低端 Android 设备（如 骁龙 665）上可将战斗界面帧率从 45fps 稳定至 60fps。

**分图集策略**：按**使用频率和生命周期**而非按视觉主题拆分图集是正确实践。常驻 UI（主界面按钮、通用弹框底图）放入 `Common.spriteatlas`，活动专属图标放入 `EventActivity.spriteatlas`，后者可随活动结束卸载，避免常驻内存。若将全部图标塞入单一图集，一张 4096×4096 RGBA32 图集占用显存达 **64MB**（4096×4096×4 字节），远超按模块拆分的合理上限 16MB。

**AssetBundle 与图集引用**：图集与引用它的 Prefab 必须打入同一个 AB 包，或图集单独成包并设置为依赖包。若图集与 Prefab 分包但未正确设置依赖，Unity 会为每个引用该图集的 AB 包各自冗余一份图集纹理，导致内存翻倍。

## 常见误区

**误区一：图集越大越好**。开发者有时将所有 UI 图标塞入单张 4096×4096 图集以"一劳永逸"减少 Draw Call，但这忽视了内存成本和加载粒度。一张 4096×4096 RGBA32 纹理不压缩时占用 64MB 显存，而 iOS 的 PVRTC 和 Android 的 ETC2 压缩格式要求纹理尺寸为 2 的幂次方且 PVRTC 要求宽高相等，不满足时 Unity 会自动扩容导致额外浪费。合理上限为单图集 2048×2048，通过多图集配合按需加载实现平衡。

**误区二：图集内所有图自动合批**。图集只解决了"纹理相同"这一条件，合批还依赖 Canvas 层级连续性。许多开发者添加图集后发现 Frame Debugger 中 Draw Call 未减少，原因在于不同图集的元素在 Hierarchy 中交替排列。图集是合批的必要条件而非充分条件，需配合 UI 层级管理才能发挥效果。

**误区三：Sprite Atlas V1 与 V2 可互换**。Unity 2020 引入的 Sprite Atlas V2 改变了依赖解析方式：V1 在编辑器中会将未被图集收录的 Sprite 的引用自动重定向，而 V2 要求 Sprite 必须显式加入图集才生效。从 V1 迁移到 V2 时，原先隐式收录的精灵可能重新变为独立纹理，需在升级后重新审查图集配置。

## 知识关联

学习图集与合批需要先掌握 **UI 渲染管线**中 Canvas 批处理的工作原理——只有理解 CanvasRenderer 如何收集和排序网格，才能预判哪些层级结构会打断合批。同时，**图标图集管理**提供了资源组织的实践背景，使开发者在面对数百张 UI 资源时能制定合理的分组策略，而不是随意拼合。

掌握图集与合批后，进入**事件系统**学习时会遇到 `GraphicRaycaster` 的射线检测与 Canvas 层级的关系问题——事件系统同样依赖 Canvas 的层级结构，与合批的 Hierarchy 优化目标有时产生冲突，需要在交互精度和渲染性能之间取得平衡。