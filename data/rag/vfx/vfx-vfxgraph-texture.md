---
id: "vfx-vfxgraph-texture"
concept: "纹理采样"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 3
is_milestone: false
tags: ["进阶"]

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


# 纹理采样

## 概述

纹理采样（Texture Sampling）是VFX Graph中从二维图像获取颜色或数据信息的核心操作，其本质是通过UV坐标索引纹理像素（texel），将静态图像转化为粒子系统的动态视觉输入。在VFX Graph的节点网络中，`Sample Texture 2D`节点接收一张纹理资产和一对UV坐标（范围通常为0到1），输出该坐标位置的RGBA四通道浮点数值。

该技术的GPU实现基于双线性插值（Bilinear Interpolation）算法：当UV坐标落在两个纹理像素之间时，GPU会对周围4个相邻像素进行加权平均，从而产生平滑的过渡效果。Unity VFX Graph从2018年随Unity 2018.3版本正式引入Package形式，其纹理采样流程完全运行在GPU的Compute Shader和Visual Effect Shader管线中，与CPU侧的粒子数据解耦。

纹理采样在粒子特效中的价值在于，它将单一粒子的颜色从纯色扩展为具有空间变化的图像信息，一张512×512的噪声纹理可以为数万个粒子提供差异化的透明度、颜色或速度偏移，从而以极低的带宽开销实现高度复杂的视觉结果。

## 核心原理

### Sample Texture 2D节点的工作机制

VFX Graph中的`Sample Texture 2D`节点包含三个主要输入端口：`Texture`（纹理资产引用）、`UV`（二维坐标Vector2）和`Mip Level`（可选的Mip层级偏移）。节点输出`RGBA`四通道以及独立的`R`、`G`、`B`、`A`浮点通道，便于下游节点单独引用某一通道。UV坐标默认使用粒子自身的纹理坐标，但也可以由`Position`或随机种子派生，实现与位置绑定的纹理查找。

采样模式方面，纹理资产本身需要在Unity Inspector中预先设置Filter Mode（Point/Bilinear/Trilinear）和Wrap Mode（Repeat/Clamp/Mirror）。Repeat模式下UV超出0-1范围会自动平铺，适合制作无缝循环纹理；Clamp模式则将边界值锁定，用于需要明确边缘的粒子贴图。

### Flipbook动画采样

Flipbook是将多帧序列动画平铺排列在一张纹理中的技术，例如一张2048×2048的爆炸序列图集可以容纳8×8共64帧动画。VFX Graph提供了专用的`Flipbook Player`模块（位于Output Context的Render属性区），需要设置`Flip Book Size`参数为Vector2，例如(8,8)表示横向8列、纵向8行。系统内部自动将粒子年龄（Age/Lifetime）映射为UV偏移公式：

$$UV_{frame} = \left(\frac{col + UV.x}{cols},\ \frac{row + UV.y}{rows}\right)$$

其中`col`和`row`由当前帧索引（`floor(age/lifetime * totalFrames)`）取模和整除得到。若需要帧间混合（Motion Blur-style Blending），可在`Flipbook Player`中启用`Blend Frames`选项，系统会对相邻两帧按比例混合采样，代价是每粒子多执行一次纹理采样指令。

### 法线贴图采样与切线空间

在VFX Graph中为粒子使用法线贴图，需要在Output Particle Lit Quad或Output Particle Lit Mesh节点中开启`Normal Map`插槽，并将贴图类型设置为`Normal Map`（Unity会自动将RGB通道重映射为-1到+1范围的法线向量）。采样公式为：

$$N_{tangent} = RGB \times 2 - 1$$

即将[0,1]的颜色值解码为[-1,+1]的切线空间法线向量。VFX Graph的粒子面片默认法线朝向摄像机（Billboard模式），法线贴图叠加后能够在Lit渲染模式下对HDRP或URP的实时光照产生响应，使粒子表面呈现凹凸质感。需注意：法线贴图采样仅在Output中支持光照计算的节点（如`Output Particle Lit Quad`）中生效，在`Unlit`系列Output节点中法线信息会被忽略。

### UV扰动与数据纹理

纹理采样在VFX Graph中不限于颜色信息，还可以读取编码为纹理的向量场数据。将流体模拟烘焙成RG双通道纹理（R通道存X方向速度，G通道存Y方向速度），通过`Sample Texture 2D`读取后连接至`Velocity`属性，可驱动数万粒子跟随预烘焙的流场运动，其运算开销仅为一次纹理采样。

## 实际应用

**火焰粒子**：使用一张4×4共16帧的Flipbook火焰序列图，设置`Flip Book Size`为(4,4)，粒子生命周期1.2秒内完整播放16帧，配合Alpha通道的黑白蒙版实现边缘柔化。将`Sample Texture 2D`的A通道输出接入`Alpha`端口，R通道接入`Color`端口与HDR颜色相乘，产生自发光效果。

**流体溶解特效**：采样一张Perlin噪声灰度纹理（通常使用128×128或256×256分辨率平衡精度与显存），将R通道值与粒子年龄进行比较（`age/lifetime > noiseValue`），将满足条件的粒子Alpha设为0，形成随机溶解消隐动画。

**岩浆地面贴花**：通过粒子的世界坐标XZ分量除以地面尺寸得到UV坐标，采样一张法线贴图，在Output Lit Quad中叠加实时光照计算，使贴花粒子根据场景主光源方向动态呈现凹凸感。

## 常见误区

**误区一：将sRGB纹理直接用于数据采样**
颜色纹理通常以sRGB格式存储，GPU读取时会自动执行gamma解码（约2.2次幂校正）。若将sRGB格式的噪声纹理用于控制粒子速度或位置，解码误差会导致数值偏差，应在Unity导入设置中将该纹理的`sRGB (Color Texture)`选项取消勾选，保持线性数据。

**误区二：Flipbook的UV坐标方向问题**
Unity纹理坐标V轴（垂直方向）原点在左下角，但序列帧图集通常按照从左到右、从上到下的阅读顺序排列，导致播放顺序与预期相反。解决方案是在图集导出时垂直翻转整张图，或在VFX Graph的`Flipbook Player`中启用`Flip UV Y`选项，该选项将V坐标转换为`1 - V`以匹配图集实际布局。

**误区三：在Update Context中过量使用高分辨率纹理采样**
Update Context在每帧对每个存活粒子执行一次，若粒子数量为50万且采样一张2048×2048纹理，GPU纹理缓存压力会显著上升。对于仅需低频变化的颜色驱动，应将纹理分辨率降低至64×64或128×128，或将采样操作移至Initialize Context（仅在粒子出生时采样一次），用`Attribute`存储结果供后续帧引用。

## 知识关联

**前置概念**：SubGraph复用技术使得纹理采样的节点组合（如"采样+通道分离+HDR颜色相乘"）可以封装为可复用的SubGraph模板，在多个VFX效果中共享同一套采样逻辑，避免重复连线。SubGraph的参数暴露机制也允许将`Texture`和`Flip Book Size`作为外部参数提供，方便美术人员在Inspector中快速替换素材。

**后续概念**：噪声函数（Noise Function）是纹理采样的程序化替代方案，`VFX Graph Noise`节点在GPU上实时生成Perlin、Cellular等噪声值，省去了噪声纹理的导入和显存占用，但计算成本高于纹理采样。理解纹理采样的UV映射原理后，图集制作（Atlas Creation）会进一步规范化Flipbook纹理的尺寸约束（必须为2的幂次方，如256×256、512×512、1024×1024），以及多种序列帧的打包工具（如TexturePacker与Unity Sprite Atlas）的使用流程。