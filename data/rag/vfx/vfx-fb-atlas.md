---
id: "vfx-fb-atlas"
concept: "图集制作"
domain: "vfx"
subdomain: "flipbook"
subdomain_name: "序列帧特效"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.7
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.419
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---

# 图集制作

## 概述

图集制作（Sprite Sheet / Texture Atlas 制作）是将序列帧动画中的多张独立帧图像按照规则排列拼合为单张纹理文件的过程。与逐帧加载独立图片相比，图集将一个奔跑动作的16帧或一个爆炸动作的32帧压缩进单张 1024×1024 的纹理中，GPU 只需绑定一次纹理对象即可完成整段动画的渲染，显著减少 Draw Call 数量。

图集的概念最早随着2D游戏引擎的普及在1990年代成熟化，TexturePacker 等专用工具在2010年前后成为行业标配，将原本需要手工排列的流程自动化。现代引擎如 Unity 和 Cocos Creator 均内置图集打包功能，但理解其底层排列规则仍然是制作高质量序列帧特效的前提。

图集制作直接决定了显存占用、采样精度与运行时 UV 坐标计算的复杂程度。一张排列混乱、尺寸不规范的图集会导致帧边缘出现"纹理渗色"（Texture Bleeding）瑕疵，或让播放脚本中的 UV 偏移计算产生错位，因此标准化的制作规范是序列帧特效能否正确播放的直接保障。

## 核心原理

### 排列方式：均匀网格 vs 紧凑打包

图集有两种主要排列策略。**均匀网格排列**（Uniform Grid）将每帧分配相同大小的单元格，例如将 16 帧 256×256 的火焰帧排列为 4 列 × 4 行，总图集尺寸为 1024×1024。运行时 UV 偏移公式为：

```
U_offset = (当前帧序号 % 列数) × (1 / 列数)
V_offset = floor(当前帧序号 / 列数) × (1 / 行数)
```

此方案计算简单、适配 Shader 内逐帧播放，是序列帧特效的首选格式。

**紧凑打包**（Bin Packing）由 TexturePacker 等工具实现，每帧按实际像素边界裁切后不规则排列，能节省 20%–40% 的显存，但需要额外的元数据文件（.plist 或 .json）记录每帧的位置与尺寸，播放控制逻辑更复杂。序列帧特效中如无特殊需求，建议优先使用均匀网格以降低运行时开销。

### 尺寸规范：2的幂次与通道布局

图集总尺寸必须为 2 的幂次（Power of Two，简称 POT），如 256、512、1024、2048、4096。这是因为绝大多数 GPU 的纹理采样硬件对 POT 尺寸执行 MIP 映射生成与 Wrap 模式时效率最高，非 POT 纹理在部分移动端 GPU 上甚至无法开启硬件过滤。正方形图集（如 1024×1024）比矩形图集（如 2048×512）在内存对齐上更优，但若帧数较少可用矩形避免浪费。

单帧的像素尺寸也应保持 POT 对齐，且相邻帧之间建议保留 **2–4 像素的边距（Padding）**，防止双线性过滤采样时跨越帧边界产生渗色。部分工具还支持在每帧外扩展"出血区域"（Bleed/Extrude），将边缘像素复制一行以彻底消除接缝。

### 格式选择：PNG、EXR 与压缩纹理

- **PNG（RGBA 8-bit）**：标准序列帧特效的交付格式，支持透明通道，无损压缩，适合火焰、烟雾等需要 Alpha 的效果。一张 1024×1024 RGBA PNG 解压后占 4 MB 显存。
- **EXR（16-bit 半精度浮点）**：用于 HDR 爆炸、光效等需要高动态范围亮度的特效，单张图集显存占用达 8 MB，仅在高端平台使用。
- **ASTC（Adaptive Scalable Texture Compression）**：移动端首选压缩格式，ASTC 6×6 压缩比约为 4.2 bpp，相较未压缩 RGBA 节省约 87.5% 显存，但需在打包阶段由引擎预处理，不能直接以 PNG 形式上传 GPU。

颜色通道复用是进阶技巧：将 Alpha 单独存入灰度通道或借助另一张 RGB 图的 R 通道，可将两张图的信息合并为一张，减少纹理采样次数。

## 实际应用

**制作一个 8 帧爆炸图集的完整流程：**

1. 在 After Effects 或 Houdini 中导出 8 张 512×512 的 PNG 序列（每帧独立文件）。
2. 打开 TexturePacker，设置 Max Size 为 2048×512（均匀网格：8 列 × 1 行），Padding 设为 2px，Algorithm 选择"Basic Grid"。
3. 导出图集文件（explosion_atlas.png）与元数据（explosion_atlas.json），确认总尺寸为 2048×512。
4. 在 Unity Shader 中传入参数 `_TilesX = 8, _TilesY = 1`，用帧序号计算 UV 偏移并在 Update 中按 30 fps 递增帧号。

**移动端优化案例：** 某手机游戏的技能特效原始图集为 1024×1024 RGBA PNG，显存 4 MB。将格式转换为 ASTC 4×4 后降至约 0.5 MB，同时将 Padding 从 4px 缩减至 2px，在 1024 尺寸内多容纳了 4 帧动画，整体特效表现力提升且内存下降 87.5%。

## 常见误区

**误区一：帧数越多越好，填满整张图集**

许多初学者将一张 2048×2048 图集尽量塞满帧数，导致单帧分辨率被压缩到 64×64 以下。序列帧特效的细节质量由单帧分辨率决定，128×128 以下的单帧在全屏特效中会明显模糊。应根据特效显示尺寸反推所需单帧像素数，再决定图集尺寸与帧数的搭配，而非盲目堆砌帧数。

**误区二：非 2 的幂次尺寸"现代引擎已支持"**

虽然 WebGL 2.0 和 Vulkan 从规范层面允许非 POT 纹理，但在 iOS Metal 驱动和部分 Android OpenGL ES 3.0 设备上，非 POT 纹理仍会强制禁用 MIP 映射，导致远景特效出现锯齿或闪烁。除非项目明确限定平台并经过测试，图集尺寸应严格遵守 POT 规则。

**误区三：Padding 设为 0 可以节省空间**

去掉边距能让图集多容纳约 3%–5% 的有效像素，但一旦启用双线性过滤（Bilinear Filtering，几乎所有引擎的默认设置），GPU 在采样帧边缘像素时会混合相邻帧的颜色，产生明显的色带或黑边瑕疵。2px Padding 是可靠的最低标准，高缩放比例特效建议使用 4px。

## 知识关联

**前置概念衔接：** 序列帧概述中介绍了帧的时间序列逻辑，图集制作将这一时间序列转化为空间上的二维排列，需要理解帧序号到 UV 坐标的映射关系；纹理采样的双线性过滤机制直接解释了为何必须设置 Padding，采样原理是 Padding 规范的技术依据。

**后续概念衔接：** 图集制作完成后，播放控制模块负责在运行时以正确的帧率读取图集中的各帧 UV 区间，播放控制脚本的 `_CurrentFrame` 递增逻辑、帧率与 deltaTime 的换算，以及循环/单次播放的状态机，都直接依赖图集制作阶段确定的列数、行数与帧总数参数。