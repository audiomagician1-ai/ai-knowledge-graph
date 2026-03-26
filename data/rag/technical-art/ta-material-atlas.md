---
id: "ta-material-atlas"
concept: "材质图集"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 2
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.8
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


# 材质图集

## 概述

材质图集（Material Atlas，也称 Texture Atlas 或 Sprite Atlas）是一种将多个独立材质的纹理图像拼合到同一张大纹理贴图中的技术。GPU 每次切换纹理时需要重新绑定资源，而材质图集让多个不同外观的物体共享同一张纹理，从而使它们可以被合并进同一个 Draw Call，大幅降低 CPU 向 GPU 提交渲染命令的次数。

材质图集的概念在早期街机游戏时代就已出现，当时硬件内存极为有限，开发者将多个精灵图像拼合在一张 256×256 的图块表（Tile Sheet）上以节省显存。现代游戏引擎如 Unity 和 Unreal Engine 均内置了图集打包工具（如 Unity 的 Sprite Atlas 系统，SpriteAtlasV2 在 Unity 2022 正式发布），将原本分散的纹理文件自动排布到一张 2048×2048 或更大的图集纹理上。

材质图集的核心价值在于 Draw Call 合并（Batching）。以移动端为例，主流优化目标是将每帧 Draw Call 控制在 100 次以内，而未经图集化的 UI 界面往往因为每个图标使用独立纹理导致 Draw Call 数量超过 300 次。通过将同一 UI 界面的所有图标打包进一张图集，可以将这部分渲染开销降低 60%～80%。

---

## 核心原理

### UV 坐标重映射

图集的本质是将每张子纹理的 UV 坐标从 [0, 1] 的全纹理空间重映射到图集内的一个矩形子区域。若一张子纹理在 2048×2048 的图集中占据从像素坐标 (256, 512) 到 (512, 768) 的区域，则其 UV 偏移量（Offset）为 (256/2048, 512/2048) = (0.125, 0.25)，缩放量（Scale）为 (256/2048, 256/2048) = (0.125, 0.125)。实际采样时 UV 变换公式为：

**UV_atlas = UV_local × Scale + Offset**

其中 UV_local 是物体原始的本地 UV 坐标，UV_atlas 是最终传入采样器的坐标。引擎在打包时会自动计算并写入每个精灵的这两个参数。

### 排布算法与填充率

图集打包器需要将若干尺寸不一的矩形子纹理高效排列在一张大纹理中，常用算法包括**最大矩形法（MaxRects）**和**货架装箱法（Shelf-First）**。MaxRects 算法能达到 90%以上的填充率，而 Shelf-First 算法速度更快但填充率通常在 70%～85% 之间。Unity 的 Sprite Atlas 默认使用 MaxRects 变体，可配置 Padding（子纹理间距，默认值为 2 像素）来防止纹理过滤时相邻子纹理的颜色渗出（Bleeding）。

### 与 Batching 的关系

GPU 合批（Static/Dynamic Batching）要求参与合批的所有网格使用**完全相同的材质实例**，即指向同一个材质对象和同一张纹理。当两个不同外观的物体分别使用纹理 A 和纹理 B 时，即使材质 Shader 相同，GPU 也必须发出两次 Draw Call。将 A 和 B 合并进同一张图集后，两个物体均引用同一材质实例，渲染管线可以将它们的顶点数据合并为一次提交，Draw Call 从 2 次变为 1 次。这一机制在 UI 系统（UGUI、UI Toolkit）中尤为显著，同一 Canvas 下引用同一图集的所有 Image 组件会被自动合批。

---

## 实际应用

**移动端 UI 优化**：一款典型手游的主界面可能包含 40～60 个独立图标（背包格子、技能按钮、货币图标等）。将它们全部打包进一张 1024×1024 的 UI 图集后，这部分 UI 在每帧只产生 1～3 次 Draw Call（视动态元素数量而定），比未图集化时节省约 40 次 Draw Call。Unity 中只需在 Project 窗口创建 Sprite Atlas Asset，将相关 Sprite 拖入打包列表，勾选 Include in Build，运行时引擎自动完成纹理替换。

**地形 Tile 地图**：2D Tile 地图游戏将草地、泥土、石板等几十种地块纹理打包进一张 Tileset 图集（通常为 512×512，每格 16×16 像素，可容纳 1024 块不同地块）。Tilemap 渲染器在绘制整张地图时只需绑定一张纹理，渲染数千个地块仅用数次 Draw Call。

**角色换装系统**：多套服装的漫反射纹理、法线贴图和 Mask 贴图分别打包成三张图集，角色换装时只需更换 UV offset/scale 参数而无需切换材质实例，维持合批状态。这一做法常见于支持大量玩家同时显示的 MMORPG 服务器场景优化。

---

## 常见误区

**误区一：图集越大越好**。将所有纹理打进一张 4096×4096 图集看似减少了 Draw Call，但会导致该图集常驻显存（移动端常见显存上限为 2GB），而实际上同一帧可能只用到其中 10% 的子纹理。正确做法是按**界面功能模块**分组打包，每张图集控制在 1024×1024 或 2048×2048，仅在需要该模块时加载对应图集。

**误区二：图集可以跨 Canvas 合批**。在 Unity UGUI 中，不同 Canvas 组件下的元素即使引用同一张图集纹理，也不会被合并进同一次 Draw Call，因为 Canvas 本身是一个独立的渲染批次边界。跨 Canvas 引用同一图集只能减少纹理绑定切换，而无法消除 Canvas 切换带来的额外 Draw Call。

**误区三：图集打包后无需再关注 Padding**。若将 Padding 设为 0 并启用双线性过滤（Bilinear Filtering），GPU 在采样子纹理边界像素时会混合相邻子纹理的颜色，产生肉眼可见的彩色边缘（Color Bleeding）。标准做法是保留至少 2 像素 Padding，或在子纹理边缘额外扩展 1 像素的颜色（Extrude Edges），以保证在任何 Mip 级别下采样结果都不会越界。

---

## 知识关联

材质图集直接建立在**纹理通道打包**的基础之上：通道打包将多种属性数据（如粗糙度、金属度、AO）合并进同一张纹理的 RGBA 四个通道，减少纹理采样次数；而材质图集在空间维度上将多张独立纹理合并到一张贴图的 UV 区域内，减少纹理绑定切换和 Draw Call 次数。两者都是减少 GPU 资源切换开销的手段，但作用层面不同：通道打包压缩的是每个材质的纹理数量，图集压缩的是整个场景的材质数量。在实际项目中，两种技术通常叠加使用——先用通道打包将每套材质的贴图数量从 5 张压缩到 2 张，再用图集将多套材质的同类贴图合并，最终实现渲染性能的双重提升。