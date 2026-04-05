---
id: "3da-uv-rizom-workflow"
concept: "RizomUV工作流"
domain: "3d-art"
subdomain: "uv-unwrapping"
subdomain_name: "UV展开"
difficulty: 2
is_milestone: false
tags: ["工具"]

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


# RizomUV工作流

## 概述

RizomUV是由法国公司Rizom-Lab开发的专业UV展开软件，自2017年以独立产品形式发布以来，逐渐成为游戏和影视行业中处理复杂UV任务的首选工具之一。它的前身是Unfold3D，后者曾作为Maya和3ds Max的插件存在，RizomUV继承并大幅扩展了其自动展开算法，使得单独处理数万面的网格不再是瓶颈。

RizomUV的核心价值在于其虚拟切割（Virtual Cuts）与自动展开（Auto Unwrap）算法的组合速度。对于同一个角色头部模型，在Maya中手动展开可能需要30到60分钟，而在RizomUV中通过脚本化工作流完成同等质量的展开通常只需5分钟以内。这种效率差距来自RizomUV内置的LSCM（最小二乘共形映射）和ABF（基于角度的展开）两种算法的协同工作，并非简单的自动化工具。

理解RizomUV工作流的意义在于：UV质量直接影响纹理拉伸率、光照烘培精度和贴图空间利用率，而RizomUV提供了可量化的拉伸可视化（Stretch Map）和像素密度均匀化工具，让美术师能够以数据为依据做决策，而不是凭肉眼判断。

## 核心原理

### 导入与切割线设置

RizomUV接受FBX和OBJ两种主要格式，推荐使用FBX以保留材质组信息（Polygroup），因为RizomUV可以根据材质边界自动生成初始切割线，节省手动标记接缝的时间。导入后，第一步是在"Select"模式下使用鼠标右键激活"Edge Selection"，将需要隐藏的接缝（如角色腋下、裤裆内侧）手动标记为红色"Cut"线。

切割线规划遵循一个核心原则：**最大化平整度，最小化接缝可见性**。RizomUV提供"Protect"标签，可以锁定不希望被自动算法修改的切割线，这在处理硬表面模型时尤为重要——例如将一个机械面板的四条硬边全部标记为Protected Cut，确保展开后该面板始终呈现为一个矩形UV岛。

### 自动展开参数配置

RizomUV的主展开命令通过Lua脚本界面调用，核心命令格式如下：

```
ZomUnfold({PreferedGroup=1, Iterations=1, StopIfSubdivided=true, RoomSpace=0})
```

其中`Iterations`控制优化迭代次数，数值1到5之间；`RoomSpace`控制UV岛之间的间隔像素数，设置为0表示紧密排列，打包阶段再统一设置间距。实际工作中，对于游戏角色（通常使用2048×2048贴图），推荐将最终打包时的`RoomSpace`设置为4到8像素，以防止相邻UV岛在Mip贴图缩小时产生颜色渗透（Bleeding）。

ABF算法在处理有机物体（人脸、布料）时拉伸更小，LSCM在处理平坦或接近平坦的硬表面时收敛更快。RizomUV的"Unfold"按钮默认组合使用两者：先用LSCM获得初始展开结果，再用ABF进行局部优化，这一过程对于10,000面的网格通常在3秒内完成。

### 打包（Pack）工作流

UV打包是将所有UV岛排列进0到1的UV空间内，RizomUV的打包算法基于其专有的"Mosaic"引擎，相比Maya的自动排列能将UV空间利用率提升10%到25%。打包前必须完成两件事：一是统一像素密度（Texel Density），在RizomUV的TD（Texel Density）面板中设置目标密度值（如10.24 texel/cm，对应2048分辨率下约1cm网格对应10.24个像素）；二是锁定（Lock）已经手动调整好位置的特殊UV岛（如面部），避免打包算法将其移到角落造成采样精度下降。

执行打包的Lua命令：

```
ZomPack({Rotate=true, Translate=true, HomogeneousSpaces=true, RoomSpace=4})
```

`Rotate`为true时允许算法旋转UV岛以获得更高空间利用率，对于需要保持水平对齐的花纹布料贴图，应将此项设为false，否则纹理方向会随UV旋转而倾斜。

## 实际应用

**游戏角色制作管线**：在实际的游戏美术管线中，RizomUV通过与3ds Max或Blender的桥接插件（Bridge Plugin）实现往返传输。美术师在3ds Max中完成建模后，一键发送至RizomUV，完成展开和打包后再一键返回，整个过程无需手动导出导入OBJ文件，节省约10到15分钟的重复操作。

**硬表面载具UV**：以一辆游戏载具为例，车身面板、车轮、玻璃需要分配不同的像素密度——车身主体设置为10 texel/cm，轮胎设置为8 texel/cm（因轮胎细节较少），驾驶舱玻璃设置为6 texel/cm。RizomUV的TD面板支持按UV岛独立设置密度值并批量应用，这种分级密度管理在Maya的UV编辑器中需要手动缩放每个UV岛才能实现。

**烘培准备的UV整理**：在Substance Painter或Marmoset Toolbag中进行法线烘培之前，所有UV岛不得相互重叠，且岛间距必须至少为烘培分辨率的1/512（即2048分辨率下至少4像素）。RizomUV的"Overlap Check"功能以红色高亮显示重叠UV岛，"Island Spacing"检测工具则标记出间距不足的区域，两项检查可在打包完成后30秒内完成全模型审查。

## 常见误区

**误区一：认为自动展开等同于高质量展开**。RizomUV的一键自动展开会最小化全局拉伸，但不会考虑接缝的美观位置。例如在角色面部，算法可能将切割线放在脸颊中央（拉伸最小处），而正确做法是手动指定切割线走耳轮和发际线边缘，这需要在"Auto Cut"之前先手动标记Protected边。

**误区二：忽略像素密度统一步骤直接打包**。跳过TD均匀化直接执行Pack命令，RizomUV会按照各UV岛现有的大小进行排列。结果是：身体主干UV岛占据贴图80%面积而手指UV岛只有0.5%面积，导致手部纹理模糊而身体纹理浪费大量分辨率。正确流程是先Select All，在TD面板输入统一目标值后点击Apply，再执行Pack。

**误区三：将RoomSpace设置为0进行最终交付**。部分美术师为了追求极致的空间利用率将岛间距设为0，在2048分辨率下看起来没有问题，但当引擎自动生成Mip贴图（缩小至512或256分辨率时），相邻UV岛的边缘颜色会相互渗透，在材质边界处产生明显的黑边或色带。行业标准是在最终交付贴图分辨率下保留至少4像素的岛间距。

## 知识关联

RizomUV工作流建立在对UV展开工具基础操作的理解之上——如果不了解什么是UV岛、接缝（Seam）、以及LSCM算法的基本原理，将无法判断自动展开结果的质量优劣，也无法合理规划切割线位置。具体而言，在进入RizomUV之前，需要掌握"拉伸（Stretch）是展开角度误差的体现，而非缩放误差"这一概念，因为RizomUV的拉伸色图（绿色=无拉伸，红色=高拉伸）的读取方式与Maya的UV失真显示逻辑相同。

RizomUV工作流完成后，所得到的UV布局将直接进入纹理绘制阶段（Substance Painter）或烘培阶段（Marmoset Toolbag），因此打包质量、像素密度分布和岛间距的设置都会对下游环节的最终效果产生直接影响。掌握这一工作流后，美术师能够在UV质量和制作效率之间做出有依据的权衡，而不是在两者之间无谓地反复修改。