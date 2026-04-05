---
id: "cg-atlas-batching"
concept: "图集批处理"
domain: "computer-graphics"
subdomain: "render-optimization"
subdomain_name: "渲染优化"
difficulty: 2
is_milestone: false
tags: ["实践"]

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
updated_at: 2026-03-27
---


# 图集批处理

## 概述

图集批处理（Atlas Batching）是一种将多张独立小纹理合并为单张大纹理图集（Texture Atlas），并在渲染时让多个使用同一图集的网格对象合并成单个 Draw Call 的优化技术。其核心逻辑是：GPU 切换纹理绑定是昂贵操作，若多个对象引用不同纹理，渲染管线必须多次中断并重新绑定，而将纹理打包到同一张图集后，这些对象的材质状态完全一致，可被批合并为一次绘制调用。

该技术最早在 2D 游戏精灵渲染领域得到广泛应用，Unity 的 Sprite Atlas（2018 年随 Unity 2018.1 正式取代旧版 Sprite Packer）和 Cocos Creator 的 Auto Atlas 系统都是典型实现。在 3D 渲染场景中，图集批处理则常以"纹理合图 + 材质合批"的形式出现于 UI 系统和粒子系统优化中。理解这一技术对于将项目 Draw Call 从数百次降低到几十次具有直接的量化价值。

## 核心原理

### UV 重映射与图集坐标变换

当多张原始纹理被打包进一张图集时，每张子纹理在图集中占据一个矩形区域，由归一化的 `(u_offset, v_offset, u_scale, v_scale)` 四个参数描述。渲染器在提交顶点数据前，需要将原始 UV 坐标 `(u, v)` 变换为图集 UV：

```
u_atlas = u_offset + u * u_scale
v_atlas = v_offset + v * v_scale
```

Unity 的 Sprite Renderer 自动完成这一变换，但自定义 Shader 若直接采样 `_MainTex` 而未读取 `_MainTex_ST` 的 xy（scale）和 zw（offset）分量，则会采样到错误区域。这是图集批处理中最高频的 Bug 来源。

### 批合并的触发条件

渲染器将相邻渲染对象合并为同一批次（Batch）需同时满足以下条件：
1. **相同材质实例**：必须是同一个 Material 对象（引用相等），而非仅参数相同；
2. **相同纹理对象**：所有对象的 `_MainTex` 指向同一个图集文件；
3. **相同渲染状态**：混合模式（Blend Mode）、深度写入开关、模板参数均一致；
4. **连续渲染队列**：中间没有插入使用不同材质的其他对象。

Unity Profiler 的 Frame Debugger 可以精确显示每个批次的打断原因（如 `Different materials` 或 `Different textures`），这是诊断图集批处理失效的第一工具。

### 图集打包策略与尺寸限制

主流图集打包算法采用**最大矩形面积填充（MaxRects）**算法，能达到约 85%–95% 的面积利用率。图集尺寸必须是 2 的幂次（如 512×512、1024×1024、2048×2048），移动端 GPU 通常支持的最大纹理尺寸为 4096×4096（部分旧设备上限为 2048×2048）。若子纹理数量过多，需拆分为多个图集页（Page），此时跨页对象依然无法合批，因此图集的分组策略（按 UI 界面、按功能模块）直接影响最终批次数量。

Unity Sprite Atlas 默认开启 **Tight Packing**，依据精灵的非透明像素轮廓而非矩形边框排布，可节省约 10%–30% 的图集面积，但会增加离线打包时间。

## 实际应用

**Unity 2D UI 批处理优化**：将同一界面中所有 UI 精灵（按钮图标、背景图片、装饰元素）打入同一张 1024×1024 图集，并确保 Canvas 下所有图片引用同一 Sprite Atlas 资产。优化前 Draw Call 可能达到 40–60 次，优化后通常可压缩至 3–8 次。关键操作是在 Unity Editor 中将 Sprite Atlas 设置为 `Type: Master`，并在 Late Binding 模式下通过 `SpriteAtlasManager.atlasRequested` 事件动态加载，避免图集随首场景一次性全量加载到内存。

**Cocos Creator 自动图集**：Cocos 的 Auto Atlas 工具在构建时自动扫描指定文件夹内的 PNG，生成图集并更新所有引用该精灵的组件的 UV 数据，无需手动设置 UV 偏移。其限制是单张图集不超过 2048×2048，且同一图集内的精灵必须使用相同的混合模式，否则会强制拆分。

**3D 场景中的植被批处理**：将草、灌木、小石块等多种植被的漫反射贴图合并为一张 2048×2048 图集，配合 GPU Instancing，可在单帧内用 1–2 次 Draw Call 渲染数千个植被实例，相较于每种植被独立材质需要数十次 Draw Call 的方案，帧耗时可降低 30%–60%。

## 常见误区

**误区一：图集越大越好**

将所有纹理打入一张超大图集看似能最大化合批效果，但会导致两个问题：首先，即使当前帧只显示图集中 10% 的精灵，整张图集依然驻留显存，导致显存占用远超实际需求；其次，图集尺寸超过 GPU 纹理缓存（L1 缓存通常为 16–64 KB）的有效工作集时，缓存命中率下降，采样性能反而劣化。正确做法是按功能界面或同屏共现频率分组打包。

**误区二：只要在同一图集就一定能合批**

即使两个对象引用同一张图集纹理，若它们使用了不同的材质实例（例如一个被 `material.SetColor` 修改过颜色，从而创建了材质实例副本），仍无法合批。Unity 中访问 `renderer.material`（小写 m）会自动创建材质实例并打断批次，而访问 `renderer.sharedMaterial` 则不会。这一细节是批处理失效的第二大原因。

**误区三：图集批处理适用于所有纹理类型**

法线贴图、光照贴图（Lightmap）和阴影贴图不应打入颜色图集。法线贴图在 DXT5/BC5 压缩格式下有特殊的通道存储方式，混入图集会破坏其压缩结构；光照贴图由 Unity 烘焙系统独立管理，无法手动合图。图集批处理的适用范围主要是漫反射/颜色纹理（Albedo）和 UI 精灵纹理。

## 知识关联

图集批处理直接建立在 **Draw Call 优化**的基础之上：理解 Draw Call 的 CPU 提交开销（在移动端每次 Draw Call 约消耗 0.1–0.3 ms CPU 时间）是明白为何要减少 Draw Call 的前提，而图集批处理正是通过统一纹理状态来使 Dynamic Batching 或 Static Batching 得以成功触发的关键手段。两者的关系是：Draw Call 优化提出"合批"目标，图集批处理解决"纹理状态不一致"这一最常见的合批障碍。

在技术路径上，图集批处理与 **GPU Instancing** 互补：Instancing 解决相同网格大量重复绘制的问题，图集批处理解决不同网格但需统一材质状态的问题；两者结合（相同网格 + 同一图集材质）可达到最优的批处理效果，这是现代移动游戏渲染优化的标准做法。