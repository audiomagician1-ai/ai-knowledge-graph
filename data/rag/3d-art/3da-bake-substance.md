---
id: "3da-bake-substance"
concept: "Substance烘焙"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: true
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# Substance 烘焙

## 概述

Substance Painter 内置烘焙器是 Adobe（前 Allegorithmic）公司集成于 Substance Painter 软件中的专属烘焙模块，自 Substance Painter 1.x 版本起便作为软件的核心工作流程存在，并在 2.x 版本后逐步完善了多贴图同步烘焙能力。与 xNormal、Marmoset Toolbag 等外部烘焙工具不同，Substance 烘焙器的最大优势在于：烘焙结果可以直接被软件内的所有智能材质、锚点（Anchor Point）和填充图层实时读取，无需导入导出操作。

Substance 烘焙器最核心的功能是"一键式多图烘焙"——在同一次烘焙操作中，用户可以同时生成法线贴图（Normal Map）、环境光遮蔽（AO）、曲率图（Curvature）、位置图（Position）、厚度图（Thickness）、世界空间法线（World Space Normal）等多达十余种贴图，这些贴图统称为 Mesh Maps（网格贴图），它们共同构成智能材质识别几何体特征的数据基础。

在 3D 美术制作中，Substance 烘焙器的价值不仅是减少软件切换成本。更重要的是，曲率图和位置图这两种 Substance 特有的烘焙输出，是 Substance Painter 智能材质系统的专用输入信号，若使用外部工具烘焙则很难获得格式完全匹配的版本，导致智能材质效果失效或异常。

---

## 核心原理

### 烘焙设置面板与关键参数

在 Substance Painter 中，通过菜单 **Texture Set Settings → Bake Mesh Maps** 打开烘焙面板。其中最关键的参数包括：

- **Output Size（输出尺寸）**：决定所有 Mesh Maps 的分辨率，通常选择 2048×2048 或 4096×4096，与贴图集（Texture Set）分辨率保持一致。
- **Dilation Width（扩张宽度）**：默认值为 16 像素，用于填充 UV 边界外的颜色溢出区域，防止贴图接缝在实时渲染中出现黑边。
- **Max Frontal Distance / Max Rear Distance**：定义高模投射到低模的前后搜索距离，其功能等同于 xNormal 中的 Ray Distance，控制烘焙笼（Cage）的范围。
- **High Definition Meshes（高精度网格）**：这是 Substance 烘焙器的特有选项，用户可以在此槽位中直接拖入高模 FBX 文件，无需提前将高低模合并，软件会在烘焙时自动做名称匹配（Name Matching）。

### 名称匹配（Name Matching）机制

Substance 烘焙器通过网格名称前缀或后缀来自动配对高低模。默认规则是：低模网格命名为 `Mesh_low`，高模网格命名为 `Mesh_high`，软件识别 `_low` 和 `_high` 后缀后自动对应烘焙，避免多个物件相互干扰产生烘焙污染（Baking Pollution）。除内置规则外，用户可在 **Edit → Settings → Baking** 中自定义后缀关键字。这一机制在处理包含数十个子部件的角色或载具模型时尤为重要。

### 曲率图与厚度图的独特算法

曲率图（Curvature Map）并非由高模直接投射生成，而是由 Substance 烘焙器对低模本身的网格曲率进行计算，输出一张以灰度表示凸起（白色）和凹陷（黑色）的贴图，中性灰（128, 128, 128）代表平面区域。该图在智能材质中用于给边缘添加磨损效果，若曲率图烘焙质量差，边缘破损效果将完全失真。

厚度图（Thickness Map）则从网格内部向外发射射线，计算表面到对面内壁的距离，输出白色（薄处）到黑色（厚处）的渐变。它专门用于驱动次表面散射（SSS）材质中的透光效果，例如耳廓、手指在背光时呈现的透射感。

### Anti-aliasing（抗锯齿）与 Supersampling

Substance 烘焙器在 **Antialiasing** 下拉菜单中提供 None、Subsampling 2×2、Subsampling 4×4 三个选项。选择 4×4 时，软件实际以目标分辨率的 4 倍进行内部采样后再降采样输出，可以显著减少法线贴图在斜面区域出现的锯齿状走样，代价是烘焙时间增加约 3～5 倍。

---

## 实际应用

**角色武器的完整 Mesh Maps 烘焙流程**：以一把游戏低模步枪（约 8000 三角面）为例，将高模（约 200 万面）和低模同时载入 Substance Painter，在 Bake 面板中勾选全部 Mesh Map 类型，设置 Output Size 为 2048，Dilation Width 为 16，Subsampling 4×4，单次烘焙即可获得法线、AO、曲率、位置、厚度、世界空间法线共 6 张贴图。随后在图层面板中应用"Metal Edge Wear"智能材质，该材质会自动调用曲率图识别枪管和枪托的棱角位置，无需任何手动遮罩绘制即可生成真实的磨损痕迹。

**多 Texture Set 批量烘焙**：当角色模型拥有身体、头部、服装三个独立 UV 集（Texture Set）时，Substance Painter 支持通过 **Bake All Texture Sets** 功能一次性烘焙全部 UV 集，避免逐一切换操作，显著提升大型项目的迭代效率。

---

## 常见误区

**误区一：认为 Substance 烘焙法线质量不如 xNormal**
这一观点在 Substance Painter 早期版本（1.x）时曾部分成立，但自 2.6 版本引入改进的切线空间算法并支持 MikkTSpace 切线空间计算后，Substance 烘焙器输出的法线贴图与主流游戏引擎（Unreal Engine、Unity）的切线空间计算完全对齐，实际上比在 xNormal 中烘焙后再导入更不容易出现接缝问题。

**误区二：曲率图可以用手绘遮罩代替**
曲率图是基于网格几何信息精确计算的数学结果，记录了每个像素点的曲率方向和强度。手绘遮罩只能粗略模拟磨损区域的位置，无法重现曲率图在 0.5～5 像素级别边缘上的精确梯度信息，用于驱动智能材质时效果差异显著，尤其在复杂机械零件的倒角处更为明显。

**误区三：烘焙后修改 UV 无影响**
由于 Mesh Maps 是基于烘焙时的 UV 布局生成的，若在烘焙完成后修改模型 UV，所有 Mesh Maps 将与新 UV 错位，导致法线贴图扭曲、AO 位置偏移。正确做法是在最终确认 UV 展开后再进行烘焙，需要修改 UV 时必须重新执行全部烘焙流程。

---

## 知识关联

学习 Substance 烘焙之前，需要掌握**法线烘焙**的基础知识，包括切线空间法线的物理含义、高低模的准备标准以及 UV 展开规范，这些前置知识直接决定烘焙参数（如 Max Distance）的合理设置方式。

Substance 烘焙器输出的 Mesh Maps 是 Substance Painter 内所有**智能材质**（Smart Material）和**智能遮罩**（Smart Mask）的驱动数据源。理解哪些 Mesh Maps 控制哪些材质效果——例如 AO 驱动污垢积累、Position 驱动渐变过渡、Thickness 驱动透光——是进阶使用 Substance Painter 智能材质系统的直接前提。此外，Position Map 的 Y 轴分量还常被用于驱动角色从脚底（黑色）到头顶（白色）的垂直方向颜色渐变，是 Substance 特有的应用技巧。