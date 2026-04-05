---
id: "cg-texture-atlas"
concept: "纹理图集"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 2
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 纹理图集

## 概述

纹理图集（Texture Atlas）是一种将多张独立纹理图像拼合进单张大型纹理图像的技术方案。每个子纹理在图集中占据一块矩形区域，渲染时通过缩放后的UV坐标范围（通常映射到 [0,1] 子区间）来采样该区域。Unity引擎的Sprite Atlas系统和Unreal Engine的纹理流送机制都以此技术为基础进行批次合并与资产管理。

该技术最早在2000年代初的2D游戏领域被广泛采用，其直接动机是GPU每次切换绑定纹理（`glBindTexture` 调用）都会产生状态切换开销。将100张小贴图合并为1张图集，可将Draw Call中纹理绑定次数从100次降低到1次，显著减少CPU向GPU提交指令的瓶颈。在移动端GPU（如Adreno、Mali架构）上，纹理切换引发的缓存失效尤为昂贵，图集优化收益更为突出。

纹理图集的核心价值在于两点：一是通过减少纹理状态切换实现批次合并（Batching）；二是将碎片化的小纹理整合后，使GPU纹理缓存（L1/L2 Texture Cache）的命中率提升，因为相邻多边形访问同一块内存页的概率更高。然而图集也引入了UV坐标重新计算、图集打包算法选择、边界渗色等新问题，需要系统性地处理。

---

## 核心原理

### 打包算法与空间利用率

图集打包本质上是二维矩形装箱问题（2D Bin Packing），属于NP-Hard问题，工程中常用启发式算法近似求解。最常见的三种策略为：

- **MaxRects算法**：将可用空闲区域维护为一组最大矩形列表，每次放置新矩形后分裂剩余空间。TexturePacker工具默认采用此算法，空间利用率通常可达85%–95%。
- **Shelf算法（货架算法）**：将图集横向分成若干"货架"，按高度降序排列子纹理后逐行填充，实现简单但利用率偏低，约70%–80%。
- **Guillotine算法（切割算法）**：每次放置后用两条垂直切割线分割剩余空间，适合子纹理尺寸差异不大的情况。

图集输出尺寸通常要求为2的幂次（POT，Power of Two），如256×256、1024×1024、2048×2048，这是因为历史上OpenGL ES 2.0要求非POT纹理不支持Mipmap和重复采样。现代API（Vulkan、Metal）已无此限制，但部分移动硬件仍建议使用POT尺寸以保证缓存对齐效率。

### UV坐标的重映射

子纹理在图集中的位置由四个参数描述：偏移量 `(u_offset, v_offset)` 和缩放比 `(u_scale, v_scale)`。设原始UV坐标为 `(u, v)`，则图集UV坐标 `(u', v')` 的计算公式为：

```
u' = u_offset + u × u_scale
v' = v_offset + v × v_scale
```

其中 `u_scale = 子纹理宽度 / 图集总宽度`，`v_scale = 子纹理高度 / 图集总高度`。例如一张128×128的子纹理放入1024×1024图集后，其 `u_scale = v_scale = 0.125`。这一重映射通常在工具链（如Sprite Packer）导出时自动写入网格顶点的UV数据，或在Shader中通过Uniform传入变换矩阵动态计算。

### UV边界渗色（Bleeding）与Padding处理

图集中最常见的视觉缺陷是**UV渗色**（UV Bleeding），即采样时因双线性过滤（Bilinear Filtering）在子纹理边界越界，采样到相邻子纹理的像素颜色，造成贴图边缘出现异色条纹。

解决方案是在每个子纹理四周添加**Padding（内边距）**像素，并对边缘像素进行**边缘扩展（Edge Extrusion / Bleed）**处理——将最外层有效像素的颜色向外复制填充到Padding区域。TexturePacker的默认Extrude值为2像素，在使用Mipmap时建议设置为4–8像素，因为Mipmap的LOD层级会将更大范围的相邻像素混合进采样结果。

对于Mipmap的情况，Padding需求随Mipmap层级增加而成指数增长：若最大Mipmap层级为 `n`，则理论最小Padding为 `2^n` 像素。在1024×1024图集上使用全Mipmap链（10级）时，最外层Mipmap的1像素对应原图512像素，因此对子纹理边界的保护需提前在打包阶段规划。

---

## 实际应用

**2D游戏精灵图集**：Unity的Sprite Atlas（`.spriteatlas`资产）会将同一`SpriteAtlas`中的所有Sprite自动打包，运行时`SpriteRenderer`引用同一图集的多个Sprite可被合并进同一个Draw Call。配合`CanvasRenderer`的动态批次，一个拥有500个UI元素的场景可以从500次Draw Call压缩到个位数。

**3D场景道具合批**：对于场景中大量使用的碎石、植被等资产，将其Albedo/Normal/Roughness贴图分别打包进对应的图集，使多个Mesh可共享同一材质球（Material）。Unreal Engine的Hierarchical Instanced Static Mesh（HISM）与图集配合使用，可在不拆分网格的前提下实现GPU Instancing。

**字体渲染**：字体系统（如FreeType + 自定义渲染器）将字形位图（Glyph Bitmap）动态插入一张灰度图集（通常为R8格式），每个字符对应图集中的一块区域。字形位图尺寸不一，因此运行时动态图集通常采用Shelf算法以降低插入时间复杂度，牺牲部分空间效率换取实时更新速度。

---

## 常见误区

**误区一：Padding越大越好**。增大Padding会消耗图集面积，导致空间利用率下降，迫使图集尺寸升档（如从2048×2048升至4096×4096），反而使内存占用翻四倍。合理的Padding应根据是否启用Mipmap以及最大Mipmap层级来计算，而非无脑设置为16像素或32像素。

**误区二：图集越大越好，应尽量合并所有纹理**。纹理图集的合批效果依赖于同一帧内确实有多个对象同时使用该图集。若某张4096×4096图集在实际场景中只有少数几个对象引用，则该图集会常驻显存（VRAM）但无法实现有效合批，造成显存浪费。移动设备的显存通常为2GB–4GB，单张4K RGBA图集（压缩前）占用64MB，需谨慎规划图集分组策略。

**误区三：使用图集后可以任意设置纹理的Wrap Mode为Repeat**。子纹理在图集中仅占据 [0,1] 的一个子区间，UV坐标如果超出该子区间范围（对应Repeat模式下的平铺），会采样到图集中其他子纹理的区域，而非正确地平铺该子纹理本身。需要平铺的纹理（如地面瓷砖）不适合放入图集，应单独使用独立纹理并设置Wrap Mode为Repeat。

---

## 知识关联

纹理图集建立在**纹理映射概述**的基础之上：UV坐标的含义、双线性过滤的采样方式以及Mipmap的生成原理，是理解图集打包参数和Padding计算的前提。如果不了解GPU如何执行双线性插值，就无法判断为何边界会产生渗色。

纹理图集的下一个发展形态是**UDIM**技术。UDIM将一个完整物体的UV展开分布到多个1×1的UV瓦片（Tile）中，每个瓦片对应一张独立纹理文件（文件名包含瓦片编号如`_1001`、`_1002`），在VFX和影视制作流程中用于高精度角色的超大分辨率贴图管理。与图集不同，UDIM的核心目的是突破单张纹理分辨率限制，而非减少Draw Call；两者在UV坐标超出 [0,1] 范围的处理逻辑上有本质差异，UDIM允许整数偏移寻址不同贴图文件，而图集要求UV始终在子区间内。