---
id: "3da-uv-channels"
concept: "UV通道"
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
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# UV通道

## 概述

UV通道（UV Channel）是三维模型上存储UV坐标数据的独立插槽。每个通道保存一套完整的UV映射关系，将三维网格的每个顶点对应到二维纹理空间中的(U, V)坐标对。单个模型可以同时持有多个UV通道，不同通道的UV布局彼此独立，互不干扰——第0通道的接缝位置不影响第1通道的展开方式。

这一机制最早在游戏引擎发展初期随多重纹理（Multitexturing）技术一同普及。OpenGL在1.2版本（1998年）引入多重纹理扩展，允许渲染器在同一次绘制调用中采样来自不同UV通道的纹理。现代DCC软件如Maya、Blender、3ds Max通常支持最多8到99个独立UV通道，但实时游戏引擎中常用的通道数量一般不超过4个，因为超出部分会带来显著的顶点数据开销。

理解UV通道的意义在于：不同用途的纹理对UV布局有截然相反的要求。纹理贴图UV允许重叠以节省纹理空间，而光照贴图UV绝对不能重叠，否则烘焙结果会产生错误的阴影叠加。将两者分开存储在不同通道，使同一张网格可以同时满足两种完全矛盾的展开规则。

## 核心原理

### 通道索引与寻址方式

UV通道通过整数索引访问，起始编号因软件而异：Maya从UV0/UV1开始，Blender使用"UV Map"列表（索引0起），Unreal Engine将通道编号定义为Channel 0、Channel 1等。每个顶点在每个通道中各存储一对浮点数(U, V)，取值范围通常为0.0到1.0，超出范围则触发纹理平铺（Tiling）或钳制（Clamp）行为。以一个拥有500个顶点、2个UV通道的模型为例，其UV数据总量为 500 × 2通道 × 2坐标 × 4字节 = 8000字节，额外UV通道直接增加顶点缓冲区大小。

### 纹理UV通道（Channel 0）

纹理UV通道是绑定漫反射贴图、法线贴图、粗糙度贴图等PBR材质纹理所使用的主UV通道。此通道的核心设计目标是最大化纹理利用率，因此**允许**UV岛屿重叠——例如一个对称建筑的左右两侧门窗可以完全堆叠到同一片纹理区域，从而用更小的贴图分辨率实现相同的视觉细节密度。纹理UV通道中每个纹素（Texel）的密度应尽量均匀，常见标准是每米16到32个纹素（Texels Per Meter）用于游戏场景资产。

### 光照图UV通道（Channel 1）

光照图（Lightmap）UV通道专用于烘焙全局光照、环境遮蔽（AO）或阴影贴图等预计算光照信息。此通道有两条硬性规则：**UV岛屿不得重叠**，且每个岛屿之间必须保留足够的间距（Padding），Unreal Engine要求相邻岛屿间距至少为目标光照图分辨率下的2到4个像素，例如128×128分辨率时最小间距约为3.1%的UV空间宽度。违反不重叠规则会导致烘焙时不同面的光照信息互相写入，产生漏光（Light Bleeding）瑕疵。光照图UV通道通常由DCC软件的自动展开工具生成，或由引擎在导入时自动计算（Unreal Engine的"Generate Lightmap UVs"选项）。

### 细节UV通道（Detail UV）

细节UV通道用于驱动高频细节纹理（Detail Texture），这类纹理在近距离观察时叠加到主纹理之上，补充主贴图因分辨率不足而损失的微观细节（如皮肤毛孔、混凝土颗粒）。细节UV通常使用高倍数的UV平铺值，例如将UV坐标乘以8.0使纹理在表面重复8×8次，从而以小尺寸纹理（如256×256）呈现等价于2048×2048主贴图的细节密度。细节UV可以单独存放在第2通道，也可直接在材质着色器中通过数学运算对Channel 0的坐标做缩放来模拟，后者无需额外通道但牺牲了独立控制灵活性。

## 实际应用

在Unreal Engine 5的静态网格体工作流中，Channel 0承载材质纹理，Channel 1强制用于Lumen之前的传统光照贴图烘焙。导入FBX时，若勾选"Generate Lightmap UVs"，引擎会自动为Channel 1生成无重叠展开，开发者无需在Maya中手动处理第二套UV。

在Unity的HDRP管线中，烘焙光照贴图时Lightmap UV同样独占一个通道，通过MeshRenderer组件的"UV Chart"参数控制打包方式。对于地形混合材质，细节纹理的UV平铺倍数通常配置在4到16之间，直接写入材质的Shader Graph节点，而不占用独立UV通道。

在影视级资产管线（如使用Substance Painter制作游戏角色）中，常见的通道分配为：Channel 0放置手工展开的纹理UV，Channel 1由Marmoset Toolbag自动生成AO烘焙UV，二者共存于同一FBX文件内，Substance Painter在烘焙法线贴图时选择Channel 0，烘焙AO时切换至Channel 1。

## 常见误区

**误区一：以为光照图UV只需要"无重叠"就够了，忽略Padding要求。**
许多初学者将光照图UV展开至0到1空间内且无重叠，但岛屿贴边排列、间距为零。低分辨率光照贴图（如64×64）中相邻像素间的双线性过滤会导致颜色从一个岛屿渗透到另一个岛屿，产生边缘漏光。正确做法是根据目标分辨率预留至少2像素的间距边界。

**误区二：以为多UV通道会显著增加Draw Call。**
UV通道数量不直接影响Draw Call数量，但会增加每个顶点的数据量，从而增大顶点缓冲区占用的显存和带宽。额外UV通道的性能代价来自顶点着色器处理更多属性数据，而非渲染批次增加。

**误区三：以为所有软件的通道0和通道1含义相同。**
Blender的UV通道顺序由"UV Map"列表决定，列表中第一个UV Map对应导出FBX时的Channel 0，第二个对应Channel 1，顺序可手动调整。若在Blender中将光照图UV放在列表第一位，导入Unreal Engine后它会占据Channel 0，引擎的自动光照图生成功能默认写入Channel 1，两套UV会发生通道错位，导致渲染结果异常。

## 知识关联

UV通道建立在UV展开概述的基础上——理解UV岛屿、接缝、0到1纹理空间等基本概念后，才能判断哪种展开策略适合某一特定通道的用途。纹理UV通道的质量直接影响后续纹理烘焙（如使用Marmoset或xNormal从高模烘焙法线图）的精度，因为烘焙工具依赖Channel 0的UV布局决定高模信息写入低模贴图的位置。光照图UV通道的布局质量则决定了预计算全局光照的Texel分辨率利用率——UV面积越均匀、浪费空间越少，相同光照图分辨率下烘焙结果越清晰。掌握UV通道分配原则是进入材质制作、光照烘焙以及引擎资产管线配置等进阶主题的必要前提。