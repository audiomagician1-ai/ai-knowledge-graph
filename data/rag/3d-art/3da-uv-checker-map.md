---
id: "3da-uv-checker-map"
concept: "棋盘格检查"
domain: "3d-art"
subdomain: "uv-unwrapping"
subdomain_name: "UV展开"
difficulty: 1
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 棋盘格检查

## 概述

棋盘格检查（Checkerboard Check）是UV展开流程中用于诊断贴图质量的标准验证方法。具体做法是将一张黑白交替的正方形格子贴图（通常为8×8、16×16或32×32的等大方块）指定给模型材质，通过观察这些方块在模型表面的形变情况，直观判断UV坐标是否存在拉伸、压缩或密度不均的问题。

该方法借鉴自传统纺织品和印刷行业检验图案变形的手段，进入3D行业后成为UV质检的基本步骤，最迟在2000年代初随着Maya 4.0和3ds Max 5.0内置程序化棋盘格纹理节点而普及。在Maya中该节点名为"Checker"，在Blender中称为"Checker Texture"，在3ds Max中以"Checker"贴图形式存在于程序贴图库，均无需外部导入即可直接使用。

棋盘格检查之所以有效，是因为人眼对等比例方块的形变极为敏感——心理学研究表明，人眼能够识别出低至约5%的长宽比偏差（参见《Digital Texturing and Painting》，Ken Musgrave等，2002，Morgan Kaufmann出版社）。当UV正确展开且比例均匀时，所有方块应呈现接近完美的正方形；一旦出现长方形、梯形或大小不一的方块，即可精确定位UV问题所在的面或UV岛。这比直接贴最终纹理更容易发现细微瑕疵，能将问题前置修复，避免后期返工。

---

## 核心原理

### 拉伸检测：方块形状与UV变形的数学对应关系

棋盘格方块的形状直接对应UV坐标的拉伸比例。若某个面在U轴方向的UV跨度为0.1，而在V轴方向的UV跨度仅为0.067，则该面上显示的棋盘格方块宽高比约为 $1.5:1$，即出现横向拉伸50%的变形。反之，若V轴跨度大于U轴跨度，方块变为竖向长方形。

用公式表示拉伸比（Stretch Ratio）为：

$$S = \frac{\Delta U / W_{mesh}}{\Delta V / H_{mesh}}$$

其中 $\Delta U$ 和 $\Delta V$ 分别是UV岛在U轴和V轴的跨度，$W_{mesh}$ 和 $H_{mesh}$ 是对应三维模型边在世界空间的长度。当 $S = 1$ 时，UV各向同性，无拉伸；当 $S > 1$ 时，U方向拉伸；当 $S < 1$ 时，V方向拉伸。

行业通行标准允许 $S$ 值在 $0.9$ 至 $1.1$ 之间（即不超过±10%的形变容忍度）。对于写实角色皮肤、砖墙等对各向同性有严格要求的材质，容忍度收紧至 $S \in [0.95, 1.05]$，即±5%以内；若超出此范围，贴上纹理后细节方向性将肉眼可见。

### 密度检测：Texel Density的视觉化表达

棋盘格方块在屏幕上显示的物理尺寸，是Texel Density（像素密度，单位：texels/meter）的直观体现。Texel Density的计算公式为：

$$TD = \frac{T \times U_{span}}{L_{world}}$$

其中 $T$ 为贴图分辨率（如2048），$U_{span}$ 为该UV岛在U方向占UV空间的比例（0到1之间），$L_{world}$ 为对应三维模型边在世界空间的实际长度（单位：米）。

游戏美术中常见的统一密度基准：
- **次时代写实游戏（AAA）**：512–1024 texels/meter，对应2K贴图（2048×2048）
- **手机游戏**：128–256 texels/meter，通常使用1K贴图（1024×1024）
- **影视VFX**：2048–4096 texels/meter，常使用4K–8K贴图

当棋盘格Scale设为10（即10×10网格）时，若2K贴图下某区域每格对应模型表面约10cm见方，则该区域Texel Density约为 $\frac{2048 \times (1/10)}{0.1} \approx 2048$ texels/meter，远超游戏标准，应适当缩小该UV岛。

### 接缝与镜像检查：格子连续性的视觉判断

在UV接缝处，相邻UV岛的棋盘格应实现"视觉对齐"——格子图案跨接缝后能自然延续，不出现黑白跳格。若接缝两侧格子大小相同但颜色错位（黑对黑或白对白），说明UV岛存在奇数格偏移，在后期烘焙法线贴图时可能产生可见接缝。

使用镜像UV技术（Mirror UV）时，两侧的棋盘格会呈左右镜像，格子走向相反——这属于正常现象，不能误判为拉伸错误。但需注意：若角色脸部使用镜像UV，烘焙法线贴图后镜像侧凹凸高光方向会与真实方向相反，此情况需在镜像侧单独处理UV或接受该限制。

---

## 关键操作步骤与代码示例

以Blender Python API为例，可通过脚本自动为选中物体赋予棋盘格检查材质，Scale值设为10以获得足够密度的参考网格：

```python
import bpy

def apply_checker_material(obj, scale=10.0):
    """为目标物体创建并赋予棋盘格检查材质"""
    mat = bpy.data.materials.new(name="UV_Checker_Debug")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # 清除默认节点
    nodes.clear()

    # 创建节点
    tex_coord = nodes.new("ShaderNodeTexCoord")
    checker   = nodes.new("ShaderNodeTexChecker")
    output    = nodes.new("ShaderNodeOutputMaterial")

    # 设置棋盘格密度（Scale=10 → 10×10方格）
    checker.inputs["Scale"].default_value = scale

    # 连接节点：UV坐标 → 棋盘格 → 材质输出
    links.new(tex_coord.outputs["UV"], checker.inputs["Vector"])
    links.new(checker.outputs["Color"], output.inputs["Surface"])

    # 赋予材质
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

# 使用示例：对当前选中物体应用Scale=10的棋盘格检查
apply_checker_material(bpy.context.active_object, scale=10.0)
```

执行后在3D视口按下 `Z` → 选择"材质预览"模式，即可在实体着色模式下直接观察棋盘格变形情况，无需进入渲染模式，节省预览时间。检查完毕后直接删除该材质并换回正式材质节点，UV数据不受影响。

---

## 实际应用案例

**案例一：角色头部UV检查**

将棋盘格贴图（Scale=8）赋予角色头部模型后，重点检查鼻翼、眼角和嘴角等曲率变化大的区域。这些位置因多边形密度高，UV容易堆积，导致格子偏小（密度过高，约为其他区域的2–3倍）；而耳后、颈部等相对平坦的区域则容易出现格子偏大（密度不足）。通过在UV编辑器中按 `S` 缩放各UV岛，将各区域格子尺寸统一到与面部主体相差不超过±15%的范围。

例如，若面部主体格子边长约对应模型表面8mm，而耳廓区域格子边长对应约18mm，则需将耳廓UV岛放大约 $18/8 = 2.25$ 倍，方可达到密度一致。

**案例二：建筑墙面UV检查**

对一块3米×2米的砖墙面板做棋盘格检查（Scale=10），理想状态下应呈现10列×6.67行（比例3:2）的正方形格子。若实际观察到10列×10行（显示为正方形布局），说明V轴方向UV被拉伸了 $10/6.67 \approx 1.5$ 倍，贴上砖块纹理后砖块会呈现比实际高约50%的竖长方形。修复方法是在UV编辑器中沿V轴方向将该UV岛压缩至原来的 $6.67/10 = 0.667$ 倍，直到格子还原为与网格比例一致的3:2布局。

**案例三：硬表面武器密度统一**

为一把游戏用写实步枪（全长约90cm）制作UV时，目标Texel Density设为512 texels/meter（使用2K贴图）。枪管UV岛的实际长度约占UV空间U方向30%，对应世界空间60cm枪管，则当前密度为 $2048 \times 0.3 / 0.6 \approx 1024$ texels/meter，是目标值的2倍。需将枪管UV岛整体缩放至50%，使其U方向跨度降至约15%，棋盘格方格尺寸随之增大一倍，与其他部件格子尺寸对齐。

---

## 常见误区与错误判断

**误区一：认为接缝处格子对齐就代表UV无问题**

接缝处两侧格子颜色和大小匹配，只能说明接缝两侧密度一致、无奇数格偏移，但不能排除整体UV仍存在拉伸。例如两侧UV岛同样在U方向拉伸了30%，格子外观一致地呈现横向长方形，看起来"对齐"，但两侧均已存在拉伸问题。必须以方块是否接近正方形作为拉伸判断依据，而非仅看接缝对称性。

**误区二：棋盘格Scale值影响检查结论**

Scale值（格子密度）的高低不影响拉伸检查的结论——无论Scale设为5还是50，若UV存在30%的U轴拉伸，所有方块都会以相同比例呈横向长方形。Scale值仅影响密度对比的精度：Scale越高，不同区域之间格子尺寸的相对差异越容易目视对比。通常推荐Scale=8或Scale=10作为检查起点。

**误区三：混淆镜像UV的棋盘格方向与拉伸**

使用镜像UV时，镜像侧的棋盘格走向与原始侧相反，视觉上容易被误读为某种扭曲。判断方法：单独观察镜像侧的单个方块，若该方块本身形状接近正方形，则无拉伸问题；格子走向相反是镜像的正常结果，不属于UV错误。

**误区四：棋盘格检查可以替代最终纹理验证**

棋盘格只能检查几何层面的拉伸与密度，无法预测最终纹理在该UV布局下的视觉效果。例如，砖缝纹理的走向是否与模型的建筑方向匹配、是否需要旋转UV岛，必须将最终纹理赋予模型后才能确认。棋盘格检查是必要的第一步，但不能省略最终纹理的视觉确认。

---

## 知识关联

**前置概念——UV展开概述**：棋盘格检查的前提是已完成基础UV展开，理解UV岛（UV Island）、UV空间（0–1 UV Space）、接缝（Seam）等基础概念。若UV尚未展开，棋盘格会以混乱的方式映射到默认UV坐标，检查无意义。

**后续工作流衔接**：
- **Texel Density工具**：Maya的"Texel Density"插件（如Texel Density Checker by Ivan Vostrikov，2018）和Blender的"TexTools"插件可在棋盘格目视检查的基础上提供精确数值化的密度测量与批量统一，是棋盘格检查的数字化辅助。
- **UV烘焙（Baking）**：棋盘格检查通过后，才应开始法线贴图、AO贴图等的烘焙操作。若带着拉伸UV进行烘焙，烘焙结果中高光、阴影的方向会随UV拉伸方向失真，且该问题在烘焙后极难修复。
- **UV打包（UV Packing）**：棋盘格检查中发现密度不