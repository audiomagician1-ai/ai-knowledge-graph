---
id: "cg-mipmap"
concept: "Mipmap"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 79.6
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

# Mipmap（多级渐远纹理）

## 概述

Mipmap 是一种将同一张纹理预先生成为一系列分辨率逐级减半的图像集合的技术，由 Lance Williams 于 1983 年在论文 *Pyramidal Parametrics* 中正式提出。"Mip" 来源于拉丁语 *multum in parvo*，意为"小空间中的多样性"，形象地描述了这项技术将多个精度层级压缩在一个纹理集合中的特点。

在不使用 Mipmap 的情况下，当一个覆盖大量像素的纹理被渲染到屏幕上很小的区域时，GPU 在采样时会跳过纹素，导致走样（aliasing）和闪烁（shimmering）问题。Mipmap 通过预计算低分辨率版本，使 GPU 能在合适的细节级别（Level of Detail，LOD）上进行采样，从根本上解决了纹理的缩小（minification）走样问题。

存储一套完整的 Mipmap 链（mipmap chain）所需的额外内存约为原始纹理的 1/3，因为 1/4 + 1/16 + 1/64 + … 是一个收敛于 1/3 的等比级数。这意味着一张 1024×1024 的纹理附加完整 Mipmap 后，总内存占用约为原始纹理的 4/3 倍。

---

## 核心原理

### LOD 层级的计算

每一个 Mipmap 层级称为一个 **mip level**，编号从 0 开始：level 0 是原始分辨率，level 1 是宽高各减半（即面积缩减为 1/4），以此类推。对于一张 256×256 的纹理，完整的 Mipmap 链包含 level 0（256×256）、level 1（128×128）、…、level 8（1×1），共 9 个层级，层级数 = log₂(max(width, height)) + 1。

GPU 自动选择 mip level 的依据是纹理坐标 (u, v) 在屏幕空间中的变化率，即偏导数 ∂u/∂x、∂u/∂y、∂v/∂x、∂v/∂y。OpenGL 和 Direct3D 均通过以下公式计算 LOD 值：

> **λ = log₂(ρ)**，其中 ρ = max(√((∂u/∂x)² + (∂v/∂x)²), √((∂u/∂y)² + (∂v/∂y)²))

λ 越大表示纹理在屏幕上被压缩得越厉害，GPU 会选取编号更高（分辨率更低）的 mip level 进行采样。

### 过滤模式对 Mipmap 的影响

仅有 LOD 计算还不够，GPU 需要进一步决定如何在层级之间过渡：

- **GL_NEAREST_MIPMAP_NEAREST**：选取最接近 λ 的整数层级，并在该层级内使用最近邻采样。速度最快，但层级切换时会产生明显的跳变边界。
- **GL_LINEAR_MIPMAP_NEAREST**：选取最近整数层级，层级内使用双线性过滤，是早期游戏的常用选项。
- **GL_LINEAR_MIPMAP_LINEAR（三线性过滤）**：在相邻两个 mip level 分别进行双线性采样，再对两个结果按 λ 的小数部分做线性插值。这是目前最常用的 Mipmap 过滤模式，代价是每次纹理采样需要 8 个纹素读取（每层 4 个，共 2 层）。

### LOD 偏移（LOD Bias）

着色器和 API 均支持手动调整 λ 的偏移量，称为 **LOD bias**。在 GLSL 中，`texture(sampler, uv, bias)` 的第三个参数即为 LOD bias；在 OpenGL 全局状态中可通过 `GL_TEXTURE_LOD_BIAS` 设置默认偏移。

- **负偏移**（如 -1.0）：强制使用更精细的层级，图像显得更清晰，但可能引入更多锯齿。
- **正偏移**（如 +1.0）：强制使用更模糊的层级，可用于故意软化纹理或减少纹理缓存压力。

部分驱动程序会限制 LOD bias 的可设置范围，例如将其限制在 [-2.0, 2.0] 之间，以防止玩家通过极端负偏移获得竞争优势（在射击游戏中使墙面纹理变锐从而透视敌人）。

### Mipmap 的生成算法

最基础的生成方式是 **Box Filter（盒式滤波）**：将 2×2 纹素的均值作为下一级的单个纹素值。更高质量的方案包括使用 Kaiser 滤波器或 Lanczos 滤波器进行降采样，能更好地保留高频细节同时抑制振铃效应。对于法线贴图（normal map），不能直接对 RGB 值取平均，必须对法线向量归一化后再存储，否则低 mip 层级的法线长度会缩短，导致光照计算错误。

---

## 实际应用

**游戏地形渲染**：在 Unreal Engine 中，地形系统默认为所有地形纹理生成完整 Mipmap 链。当摄像机在高空俯视时，地面纹理自动采用高编号 mip level，避免远处地面出现高频噪声闪烁。

**UI 纹理的反例**：2D UI 元素（如血条、按钮图标）通常固定在屏幕像素位置，其纹理坐标偏导数几乎为零，强制使用 level 0。此时为 UI 纹理生成 Mipmap 是多余的内存浪费，Unity 和 Unreal 均在 UI 图集导入设置中默认关闭 Mipmap 生成。

**立方体贴图（Cubemap）的 Mipmap**：环境反射探针通常以粗糙度参数索引 Mipmap 层级，这是基于物理的渲染（PBR）中预过滤环境贴图（Pre-Filtered Environment Map，PFEM）的核心机制——粗糙度越高，采用编号越大的 mip level，实现不同光泽度的反射效果。

---

## 常见误区

**误区一：Mipmap 解决了所有纹理走样问题**
Mipmap 对各向同性（isotropic）缩小走样效果优秀，但对**各向异性**情况效果有限。当表面以倾斜角度呈现时（如向远处延伸的地板），沿 u 方向的纹素密度与沿 v 方向差异可达 8 倍以上，此时 Mipmap 为了覆盖较长的那个方向不得不选取更高的 LOD，导致纹理在较短方向上过度模糊。解决这个问题需要各向异性过滤（Anisotropic Filtering）技术。

**误区二：非 2 的幂次纹理无法使用 Mipmap**
OpenGL 2.0 之前的规范确实要求纹理尺寸必须是 2 的幂次（Power of Two，POT）才能生成 Mipmap，但自 OpenGL 2.0 起已支持非 2 的幂次（NPOT）纹理的 Mipmap 生成，Direct3D 9 及以上版本同样支持。现代 GPU 对 NPOT Mipmap 的处理方式是向下取整，例如 100×100 的纹理，level 1 为 50×50，level 2 为 25×25，level 3 为 12×12。

**误区三：LOD bias 负值总能提升视觉质量**
将 LOD bias 设为较大负值（如 -3.0）会强制采样原始分辨率纹理，虽然纹理看起来"更清晰"，但当纹素与屏幕像素比例失调时反而会重新引入高频走样，并且会增加纹理缓存缺失（cache miss）率，降低渲染性能。

---

## 知识关联

**前置概念——纹理映射概述**：理解 Mipmap 需要先掌握 UV 坐标系统与纹素采样的基本流程；Mipmap 的 LOD 计算本质上是对纹理坐标偏导数的扩展应用，而偏导数概念正来自双线性过滤对相邻像素 UV 差值的分析。

**后续概念——各向异性过滤**：各向异性过滤在 Mipmap 的基础上引入了方向性采样，通过沿最大变化方向进行多次采样（各向异性级别 N 表示最多采样 N 个不同位置），弥补了 Mipmap 在斜视角场景中的模糊缺陷。二者在 GPU 硬件中通常协同工作。

**后续概念——纹理流式加载**：在大型开放世界游戏中，Mipmap 链的分层结构天然适合流式加载：远处物体只需低分辨率的高 mip level，近处物体才需要 level 0 的完整分辨率。Unreal Engine 的纹理流式系统正是以单个 mip level 为单位进行 GPU 内存的动态加载与卸载。