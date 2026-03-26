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
quality_tier: "B"
quality_score: 48.7
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.419
last_scored: "2026-03-22"
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

纹理采样（Texture Sampling）是VFX Graph中粒子系统从二维图像中读取颜色、法线或遮罩数据的核心机制。与普通Shader中的UV采样不同，VFX Graph的纹理采样发生在粒子的Compute着色器阶段或Output阶段，允许每一个粒子独立地访问纹理的不同区域，从而产生外观各异的粒子群体效果。

纹理采样在VFX Graph中由`Sample Texture 2D`节点实现，该节点接受一个`Texture2D`资产引用和一个`UV`坐标作为输入，输出`RGBA`颜色值和Alpha通道。Unity VFX Graph在2019.3版本后将此节点整合进了Output粒子块（Output Particle Quad/Mesh），使得采样操作可以直接绑定到粒子的渲染步骤，而无需手动传递中间属性。

纹理采样之所以在特效制作中不可或缺，是因为它允许美术师用一张256×256甚至64×64的贴图赋予成千上万粒子视觉细节，而非通过几何体堆叠。火焰、烟雾、魔法光效等视觉元素几乎完全依赖纹理采样来实现其外观多样性和动态感。

---

## 核心原理

### UV坐标与粒子属性绑定

VFX Graph中的UV坐标是一个二维向量，取值范围通常为`(0,0)`到`(1,1)`，分别对应纹理的左下角和右上角。在`Sample Texture 2D`节点中，UV输入端可以直接连接粒子属性，例如将粒子的归一化年龄（`Age/Lifetime`，值域0→1）映射为U轴偏移，实现粒子生命周期内颜色从左到右的渐变采样。这种绑定方式每个粒子独立计算，GPU并行效率极高。

### Flipbook动画帧序列采样

Flipbook是VFX Graph中实现逐帧纹理动画的标准方法。它将多帧动画水平和垂直排列在一张图集中，例如一张`512×512`的Flipbook图集可以容纳`8×8=64`帧动画，每帧大小为`64×64`像素。VFX Graph提供`Flipbook Player`属性块，内部自动计算当前帧对应的UV偏移量，公式为：

```
UV_offset = (float2(column, row)) / float2(flipbookColumns, flipbookRows)
```

其中`column`和`row`由粒子的`TexIndex`属性（整数帧索引）求余和整除得到。勾选Output节点中的`Use Flipbook`选项后，VFX Graph会自动在`_TexColumns`和`_TexRows`着色器属性中注入行列数，无需手动编写帧计算逻辑。

Flipbook还支持**帧插值（Frame Blending）**，即同时采样当前帧和下一帧并按小数部分线性混合，避免动画切换时的跳帧感。这一选项在Output节点的`Flipbook Blend Frames`处启用，会额外增加一次纹理采样调用，性能代价约为原来的1.7倍，需根据粒子数量权衡。

### 法线贴图采样与粒子光照

VFX Graph支持在Output粒子四边形（Quad）上应用法线贴图，使粒子表面响应场景光照方向，产生体积感。法线贴图采样使用`Sample Texture 2D`节点，输出的RGB值需经过`Unpack Normal`节点处理，将存储在`[0,1]`范围内的法线数据还原为`[-1,1]`的切线空间向量：

```
Normal = RGB * 2.0 - 1.0
```

在Lit Output（如`Output Particle Lit Quad`）中，解包后的法线会与粒子的朝向矩阵（Billboard矩阵）结合，计算漫反射和高光照明。注意法线贴图仅在**Lit渲染模式**下生效，在`Unlit`输出节点中此采样结果对最终颜色无影响。

### 遮罩贴图与Alpha控制

纹理的Alpha通道常被用作粒子的形状遮罩（Shape Mask），决定粒子透明区域的边缘羽化程度。VFX Graph可将`Sample Texture 2D`节点输出的`A`端口直接连接到Output节点的`Alpha`输入，实现软边粒子效果。若需要更复杂的遮罩逻辑，可以将R、G、B、A四个通道分别存储不同遮罩（如R=烟雾形状，G=发光边缘，B=扰动遮罩），在一次纹理采样中同时获取多种控制信息，减少采样次数。

---

## 实际应用

**火焰Flipbook特效**：制作一张`8×8`帧的火焰动画图集，在VFX Graph中将粒子`Age/Lifetime`乘以64得到`TexIndex`，配合Flipbook Player呈现完整的火焰燃烧动画。每个粒子可设置随机初始帧（`Random.Range(0, 64)`），避免所有粒子同步播放的"整齐感"。

**烟雾法线贴图**：为烟雾粒子绑定一张切线空间法线贴图，在带有方向光的场景中，烟雾粒子的受光面和背光面会产生明暗差异，相比纯Unlit贴图，体积感提升明显。Unity官方的VFX Graph示例项目（2020.2版本后附带）中的`Smoke_Lit`效果即采用此方案。

**RGBA通道分离采样**：在爆炸特效中，用一张纹理的R通道作为火球遮罩，G通道作为碎片遮罩，B通道驱动UV扰动偏移，仅用一次`Sample Texture 2D`调用同时控制三种视觉元素，降低GPU带宽消耗。

---

## 常见误区

**误区1：认为Flipbook帧数越多越好**
Flipbook图集的纹理尺寸受GPU纹理缓存限制。一张`2048×2048`的Flipbook（容纳`32×32=1024`帧）在移动端GPU上会导致严重的缓存未命中，采样延迟显著增加。实际项目中，PC端通常不超过`8×8=64`帧，移动端建议控制在`4×4=16`帧以内，保证纹理能驻留在L2缓存中。

**误区2：法线贴图在Billboard粒子上等同于Mesh粒子**
Billboard粒子的法线贴图始终面向摄像机，意味着粒子旋转时切线空间跟随旋转，光照计算正确。但若将粒子的Orient模式设为`Fixed Axis`（固定轴），法线与世界空间的对应关系会发生错位，出现光照方向与视觉不符的问题。需在使用法线贴图时确认Orient设置为`Face Camera Position`。

**误区3：在Update阶段采样纹理用于逻辑计算性能无影响**
在Update（Compute）阶段调用`Sample Texture 2D`会触发GPU的随机纹理读取，如果粒子数量超过10万，每帧数十万次随机采样会导致显存带宽瓶颈。建议将需要纹理数据驱动粒子运动的逻辑改为使用`Texture2D.GetPixel`预计算后存入缓冲区，或改用噪声函数在着色器内部生成，避免在Compute阶段高频采样大型纹理。

---

## 知识关联

**前置概念——SubGraph复用**：纹理采样逻辑（如Flipbook UV计算、法线解包流程）往往在多个VFX Graph资产中重复出现，将这些节点组合封装为SubGraph可显著减少重复工作。例如将`TexIndex → Flipbook UV → Sample Texture 2D → Unpack Normal`的完整链路打包为`SampleFlipbookNormal`子图，在不同特效中直接复用。

**后续概念——噪声函数**：纹理采样获得的UV坐标可被噪声函数扰动，产生水波纹、热浪扭曲等效果。Perlin噪声或Simplex噪声的输出值作为UV偏移量叠加在原始坐标上，使静态贴图呈现动态流动感，这是从纹理采样进阶到程序化特效的关键步骤。

**后续概念——图集制作**：理解了Flipbook的行列数公式和通道复用策略后，图集制作阶段需要提前规划每张纹理的帧数、通道分配和分辨率，确保最终图集能被VFX Graph的采样节点高效读取。纹理采样的参数（列数、行数、通道语义）直接决定了图集的制作规格。