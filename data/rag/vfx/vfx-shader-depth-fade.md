---
id: "vfx-shader-depth-fade"
concept: "深度渐变"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 深度渐变

## 概述

深度渐变（Depth Fade）是一种基于场景深度缓冲（Depth Buffer）信息，让粒子或半透明物体在接近不透明表面时自动产生透明度衰减的Shader技术。其核心目的是消除半透明粒子与实体几何体相交时产生的"硬切割"锯齿边缘——当一个火焰粒子贴着地面时，没有深度渐变会让粒子像被刀割一样突兀截断，而有了深度渐变，粒子边缘会柔和地淡化为透明。

这一技术随可编程GPU着色器的普及而成熟，在Unreal Engine 3（2006年发布）时代已成为粒子系统的标配功能。UE4/5的材质编辑器中专门提供了`DepthFade`节点，Unity的ShaderGraph同样内置了`Scene Depth`节点用于实现相同效果。其重要性在于：现代游戏中水面、烟雾、火焰等特效几乎100%依赖深度渐变来保证视觉连续性，没有它的特效在场景交叉时会立即暴露"假"的感觉。

深度渐变属于屏幕空间（Screen Space）技术，它读取的是当前帧已渲染的不透明几何体深度数据，因此只对渲染队列在不透明物体之后的半透明材质有效——这是理解其适用范围的关键前提。

## 核心原理

### 深度差计算公式

深度渐变的数学核心是计算**场景深度与粒子自身深度之差**，然后将差值映射到 [0, 1] 的透明度区间。标准公式如下：

```
DepthFadeAlpha = saturate( (SceneDepth - PixelDepth) / FadeDistance )
```

- `SceneDepth`：从深度缓冲采样得到的该像素位置处不透明物体的深度值（线性化后，单位为世界空间厘米/单位）
- `PixelDepth`：当前粒子像素自身的深度值
- `FadeDistance`：渐变过渡距离，决定淡化区域的宽窄（通常设置为5~50个世界单位）
- `saturate`：将结果钳制到 [0, 1] 范围

当粒子像素与不透明表面的深度差小于 `FadeDistance` 时，`DepthFadeAlpha` 从 0 渐增至 1，实现交叉区域的平滑淡出。最终透明度 = `OriginalAlpha × DepthFadeAlpha`。

### 深度缓冲的线性化处理

GPU深度缓冲存储的是非线性的裁剪空间深度（NDC Depth），范围为 [0, 1] 但分布不均匀——近处精度高、远处精度低。直接用NDC深度做差会导致远处物体的渐变距离失真膨胀。因此实现深度渐变时必须先将深度值转换为**线性视图空间深度**，转换公式为：

```
LinearDepth = (Near × Far) / (Far - NDCDepth × (Far - Near))
```

其中 `Near` 和 `Far` 是相机的近远裁剪面距离。UE5的 `SceneDepth` 节点已自动完成此线性化，但在自定义GLSL/HLSL中手动实现时必须显式处理，否则在距相机超过100单位处渐变效果会严重偏差。

### 交叉淡出（Cross Fade）的扩展应用

深度渐变的逻辑可延伸至**交叉淡出**场景：两个半透明粒子系统在空间上相互穿插时，利用双向深度比较，让相互穿透的区域双方都产生淡化。具体实现时，需要在双Pass渲染中分别记录前后两层粒子的深度，再对两层深度差做Lerp混合。这在水面与岸边泡沫、云层内部粒子相互叠加等效果中尤为关键，若忽略此步骤，两个半透明层叠加会产生深度排序错误导致的闪烁（Z-fighting表现为透明层的闪烁而非黑色锯齿）。

## 实际应用

**火焰与地面接触**：地面粒子（FadeDistance = 15单位）在接触地面前15个世界单位内开始透明淡出，使火焰根部看起来自然地"燃烧在地面上"而非悬浮于地面之上被地面切断。

**水下气泡浮到水面**：气泡粒子在距水面（不透明水体网格）8单位以内开始淡出，避免气泡在穿越水面时产生突变的消失闪烁。FadeDistance值比火焰更小，因为气泡本身直径只有3~5单位，过大的渐变距离会让气泡在水下就开始半透明。

**体积烟雾贴着建筑物**：烟雾粒子（FadeDistance = 30~80单位，因粒子体积大）在靠近墙面时大范围柔化，解决大型Billboard粒子被建筑物平面截断的视觉破绽。此时FadeDistance需要与粒子Billboard半径匹配，通常设为粒子最大半径的60%~80%。

**Unity HDRP中的具体节点连接**：`Scene Depth (Eye)`节点输出线性深度 → 减去 `Fragment Position (View Space).z的绝对值` → 除以FadeDistance → `Saturate` → 乘入原Alpha通道。

## 常见误区

**误区一：FadeDistance越大效果越好**
FadeDistance过大会使粒子在距离表面很远处就开始变透明，导致粒子"虚浮无力"。以火焰粒子为例，若将FadeDistance设为100单位而粒子本身高度只有20单位，则整个粒子在正常状态下都呈半透明，完全失去实体感。正确做法是将FadeDistance设为粒子与几何体预期交叉深度的1.2~2倍，通常在5~50单位之间针对具体粒子尺寸调整。

**误区二：深度渐变可以解决透明物体之间的排序问题**
深度渐变只能读取不透明几何体的深度缓冲，无法获取其他半透明粒子的深度信息（因为半透明Pass不写入深度缓冲）。因此两个半透明粒子相互穿插时，深度渐变无效，此时需要使用Order-Independent Transparency（OIT）或分层Alpha合成技术。将深度渐变误用于解决半透明粒子间Z-fighting是初学者最常见的实现错误。

**误区三：深度渐变在延迟渲染与前向渲染中行为一致**
在延迟渲染（Deferred Rendering）管线中，深度缓冲在Geometry Pass后立即可用，深度渐变工作正常。但在某些移动端前向渲染配置中，深度缓冲的读取时机与半透明Pass的执行顺序可能导致深度数据滞后一帧，产生一帧延迟的"幽灵轮廓"。Unity URP在低端移动端使用`_CameraDepthTexture`时需要显式开启"Depth Texture"选项，否则该纹理为空，DepthFade节点输出全1（完全不透明），深度渐变完全失效但不报错，极难排查。

## 知识关联

**与遮罩技术的关联**：遮罩技术（Mask）通过美术绘制的贴图硬性定义透明区域，是静态的、与场景几何无关的透明控制；深度渐变则是动态读取运行时深度数据的程序化透明控制。二者可叠乘使用：先用遮罩贴图定义粒子的基础形状Alpha，再乘以DepthFadeAlpha处理与场景的交叉边缘，两套透明信息在最终输出Alpha中相乘合并。

**向极坐标变换的延伸**：掌握深度渐变后，下一步学习极坐标变换（Polar Coordinate Transform）时会遇到类似的"坐标空间转换"思维——深度渐变处理的是视图空间Z轴的深度坐标映射，而极坐标变换处理的是UV平面从笛卡尔坐标到极坐标的映射。两者都涉及将一种坐标表示转换为更适合特定视觉效果的另一种形式，深度渐变中建立的"坐标差值→透明度映射"逻辑，在极坐标变换中会演变为"角度差值→UV扭曲映射"。
