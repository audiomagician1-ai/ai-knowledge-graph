---
id: "3da-uv-padding-bleeding"
concept: "Padding与Bleeding"
domain: "3d-art"
subdomain: "uv-unwrapping"
subdomain_name: "UV展开"
difficulty: 2
is_milestone: false
tags: ["核心"]

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
updated_at: 2026-04-01
---


# Padding与Bleeding

## 概述

在UV打包完成后，每个UV岛（UV Island）之间必须保留一定的像素间距，这个间距被称为**Padding**（填充间距）。Bleeding（纹理出血）则是将UV岛边缘的像素颜色向外扩展复制，填充到Padding区域内。这两个概念共同解决了一个实际问题：当GPU对纹理进行Mipmap采样时，相邻UV岛之间会互相"污染"颜色，导致模型边缘出现颜色条纹或错误的颜色渗透。

Padding的概念随着实时渲染对Mipmap的广泛使用而变得不可忽视。Mipmap技术由Lance Williams于1983年提出，GPU在远距离渲染时会自动切换到更低分辨率的Mipmap层级（如从1024×1024降至512×512或256×256）。每下降一个Mipmap级别，纹理分辨率减半，相邻UV岛之间的间距也随之缩小。如果原始贴图中两个UV岛之间只有2像素的间距，那么在第二级Mipmap（分辨率变为1/4）中这个间距就会收缩到不足1像素，两个岛的颜色就会混合在一起，产生可见的接缝瑕疵。

Bleeding本质上是Padding的"内容填充方案"。空白的Padding区域在Mipmap降采样时仍会参与颜色混合计算，如果这些区域是黑色或透明（alpha=0），降采样后边缘就会变暗或产生半透明边框。正确的做法是将UV岛边缘像素的颜色复制扩展到Padding区域，确保Mipmap采样时获得正确的边缘颜色。

---

## 核心原理

### Padding像素数量的计算标准

Padding的最小安全值取决于纹理分辨率和目标Mipmap层级数。通用公式为：

**最小Padding = 2^n 像素**（其中n为目标最低Mipmap层级数）

对于一张2048×2048的贴图，如果需要支持到第5级Mipmap（分辨率降至64×64），最小安全Padding为2^5 = **32像素**。在行业实践中，大多数游戏引擎（如Unreal Engine 5）默认推荐的Padding值为**4到8像素**，适用于目标平台Mipmap层级不超过第4级的情况。移动平台由于渲染距离和纹理内存限制，通常贴图上限为1024×1024，此时8像素的Padding已能覆盖到第4级Mipmap（1024降至64）。

如果制作的是光照贴图（Lightmap），Padding要求更严格。Unreal Engine的Lightmap默认最小Padding为4像素，但包含阴影渐变的岛建议使用8像素，以防止漏光（Light Bleeding）现象。

### Bleeding的生成方式

Bleeding并非手动绘制，而是由烘焙软件或后处理步骤自动生成。主流工作流中有两种生成方式：

**烘焙时扩展（Bake-time Dilation）**：Marmoset Toolbag、Substance Painter等工具在烘焙法线贴图、AO贴图时，会在烘焙设置中提供"Dilation"（扩张）选项，数值直接以像素为单位输入，例如设置16像素的Dilation即可生成16像素宽度的Bleeding区域。

**后处理扩展（Post-process Dilation）**：使用Photoshop的"填充→内容识别"或专用工具如xNormal的"Dilate"滤镜，对已烘焙完成的贴图边缘进行外扩处理。这种方式适用于修复Bleeding不足的现有贴图。

Bleeding的本质操作是：取UV岛最外层像素的颜色，向外重复复制N次，N值等于所需Padding像素数。复制后的颜色与原始UV岛数据完全相同，确保Mipmap降采样时边缘颜色不会偏移。

### Mipmap降采样对Padding消耗的计算

每升高一个Mipmap级别，纹理像素间距缩小为原来的1/2。具体计算示例：

- 原始贴图：2048×2048，Padding = 8像素
- Mipmap Level 1（1024×1024）：Padding缩小为4像素
- Mipmap Level 2（512×512）：Padding缩小为2像素
- Mipmap Level 3（256×256）：Padding缩小为1像素
- Mipmap Level 4（128×128）：Padding缩小为0.5像素（不足1像素，开始产生颜色混合）

由此可见，8像素的Padding在2048分辨率的贴图中仅能保护到Mipmap Level 3。如果游戏场景中该模型会出现在较远距离（触发Level 4及以上的Mipmap），就需要增加Padding到16像素。

---

## 实际应用

**角色贴图（Character Texture）**：人物角色通常使用2048×2048的贴图，脸部、手部等细节区域的UV岛会被放大排列，相邻岛之间建议保持8像素Padding。皮肤UV岛的Bleeding必须用皮肤颜色填充，否则在远距离渲染时发际线、眼眶边缘会出现黑边，这在CG电影和写实游戏中是不可接受的瑕疵。

**地形与建筑（Tileable + Unique合并贴图）**：当一张Unique贴图中同时包含与Tiling贴图混合使用的UV岛时，不同材质区域的UV岛之间若Padding不足，在低Mipmap级别下会发生石材颜色渗入金属区域的情况。实际项目中，《地平线：零之曙光》的美术规范要求建筑模块贴图中所有UV岛间距不低于4像素（基于1024分辨率贴图）。

**透明贴图（Alpha贴图）**：树叶、栅栏等使用Alpha通道实现镂空效果的模型，透明区域周围的UV岛若Bleeding颜色不正确（例如背景色为黑色），Mipmap降采样后叶片边缘会出现黑色轮廓。正确做法是确保Alpha遮罩外的颜色通道填充与叶片相近的颜色（如绿色），即使Alpha为0，RGB颜色也应当是叶片色。

---

## 常见误区

**误区一：Padding越大越好**
增大Padding会直接压缩UV岛可用面积，导致贴图分辨率利用率下降。例如一张1024×1024的贴图中有20个UV岛，如果每个岛四周各增加16像素的Padding，浪费的像素面积可能占总面积的15%以上，相当于有效贴图分辨率从1024降至约960。在手机游戏中，这种浪费会直接影响资产包体大小和渲染清晰度的平衡。合理的Padding应根据贴图分辨率和最低可视Mipmap级别精确计算，而不是盲目调大。

**误区二：Bleeding宽度等于Padding宽度就已足够**
许多美术同学认为Bleeding填充到与Padding等宽即可，但实际上Bleeding应当**略大于Padding**，建议多出2-4像素作为安全冗余。这是因为UV打包算法并非总能精确保证所有岛之间的间距完全一致，部分打包工具会在优化面积利用率时压缩个别岛之间的间距，而Bleeding的额外冗余能覆盖这类误差。

**误区三：法线贴图不需要Bleeding**
颜色贴图需要Bleeding容易理解，但法线贴图（Normal Map）同样需要。法线贴图存储的是表面朝向向量，如果UV岛边缘的法线方向向量（RGB值为特定方向如(0,0,1)对应蓝色）在Mipmap降采样时与空白区域的默认值混合，会导致模型边缘产生错误的光照反射高光，在金属材质上尤为明显。烘焙法线贴图时Dilation设置与颜色贴图应使用相同的像素扩展值。

---

## 知识关联

Padding与Bleeding是UV打包（UV Packing）步骤完成后的质量保障环节。在UV打包阶段，美术人员已经决定了每个UV岛的大小比例和排列位置；Padding参数通常可以直接在RizomUV、Maya的UV工具包或Blender的UV打包插件（如UV Packmaster 3）中设置，软件会在自动排列时自动预留对应像素数的间距，前提是需要正确输入目标贴图分辨率（如2048）和所需间距像素数（如8）。

理解Mipmap的降采样机制是正确设置Padding数值的必要前提——具体来说，需要了解目标游戏引擎（Unity或Unreal Engine）的Mipmap生成策略、模型在场景中的最远可视距离，以及该距离下GPU会激活第几级Mipmap，才能推算出贴图中Padding的最小安全像素数。Bleeding的生成则与法线贴图烘焙、AO贴图烘焙等烘焙流程直接关联，是完整纹理烘焙管线中的最后一道质量检查步骤。