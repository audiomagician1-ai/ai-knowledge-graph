---
id: "cg-sdf-texture"
concept: "SDF纹理"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# SDF纹理

## 概述

SDF纹理（Signed Distance Field Texture，有符号距离场纹理）是一种将几何形状编码为距离值的特殊纹理格式。纹理中每个像素存储的不是颜色，而是该像素位置到最近形状边界的有符号距离——正值表示在形状外部，负值表示在形状内部，零值精确对应形状轮廓。这一特性使得一张低分辨率的SDF纹理可以在任意缩放比例下渲染出清晰锐利的边缘。

SDF用于图形渲染的思想可追溯至计算机图形学的隐式曲面研究，但将其系统性地应用于实时文字渲染，是由Chris Green于2007年在SIGGRAPH上发表的论文《Improved Alpha-Tested Magnification for Vector Textures and Special Effects》所确立的。Green在Valve公司工作期间针对游戏《传送门》的HUD文字渲染问题提出此方案，将64×64像素的SDF纹理替代传统位图字体，渲染效果在放大16倍后仍优于普通双线性过滤的位图字体。

SDF纹理在UI和文字渲染领域的重要性体现在其"一次生成，任意缩放"的特质。传统位图字体需要为每种字号预生成一套字形图集，而单张SDF字体纹理即可覆盖从8pt到200pt的全部显示需求，显著降低内存占用并消除缩放时的模糊与锯齿问题。

## 核心原理

### 距离值的编码方式

SDF纹理将浮点距离值映射到0到1的灰度范围内存储。通常以0.5为边界阈值，大于0.5代表形状内部，小于0.5代表形状外部。实际生成时会限定一个最大搜索距离（称为spread值），超出此范围的距离被截断并归一化。例如，若spread设为8像素，则内部8像素处的距离1.0对应归一化值1.0，外部8像素处归一化值为0.0，边界处精确为0.5。

### 渲染时的阈值采样

在片元着色器中，SDF纹理的使用核心是对采样值与阈值的比较。最基本的渲染代码逻辑如下：

```glsl
float dist = texture(sdfTex, uv).r;
float alpha = smoothstep(0.5 - smoothing, 0.5 + smoothing, dist);
```

其中`smoothing`参数控制边缘过渡的宽度，通常取值0.02到0.1之间。通过`smoothstep`而非硬性阈值，可以利用GPU的超采样产生抗锯齿效果。调整阈值本身（例如从0.5改为0.4）可以实现字体描边：阈值减小则轮廓向外扩展，产生膨胀效果；阈值增大则字形收缩。

### 多通道SDF（MSDF）

标准SDF纹理在锐角形状（如字母"W"的尖端）处会因距离场的平滑性而丢失角点细节。2016年，Viktor Chlumský在其硕士论文中提出多通道SDF（Multi-channel SDF，MSDF），利用RGB三个通道分别存储不同方向的距离信息，在解码时取中值（median）进行重建：

```glsl
vec3 msd = texture(msdfTex, uv).rgb;
float sd = max(min(msd.r, msd.g), min(max(msd.r, msd.g), msd.b));
```

MSDF在相同纹理分辨率下能精确重建直角和锐角，使汉字、衬线字体等复杂字形的质量大幅提升，目前已成为高质量文字渲染的行业标准方案。

## 实际应用

**游戏引擎的UI文字系统**：Unity引擎的TextMesh Pro插件（现已并入Unity核心包）正是基于MSDF技术构建，默认生成512×512像素的字体图集，在渲染时通过材质参数动态控制描边宽度、发光效果（Glow）和阴影偏移，全部效果均在单次绘制调用中完成，无需多Pass渲染。

**矢量图标与徽标渲染**：游戏HUD中的方向箭头、血条图标等几何形状UI元素，可预先离线生成为SDF纹理存储在图集中。运行时通过修改片元着色器的阈值，同一张SDF贴图既可渲染实心版本，也可渲染描边版本，减少美术资源数量。

**动态文字特效**：基于SDF的距离信息可轻松实现传统位图字体难以做到的效果。例如，外发光效果通过采样阈值0.3至0.5区间并赋予发光颜色即可实现；内阴影通过对内部距离较小区域（如0.5至0.6区间）叠加深色实现，上述效果的计算量仅需在片元着色器中增加两到三行代码。

## 常见误区

**误区一：SDF纹理分辨率越低越好**。SDF的抗缩放优势容易让人认为分辨率无关紧要。实际上，SDF纹理的分辨率直接决定可捕获的形状细节精度。若字形中存在宽度小于spread值的细笔画，该笔画的内外距离场会互相覆盖，导致细节丢失。对于笔画纤细的汉字，建议SDF单字符分辨率不低于32×32像素，并将spread设为4到6像素。

**误区二：SDF纹理可以完美还原任意曲线**。SDF的重建质量本质上受限于原始纹理的分辨率和spread参数。在极大倍率缩放（如超过原始生成尺寸的10倍）时，仍会出现圆弧变形、角点变圆等失真。这是因为SDF存储的是离散采样的距离值，而非精确的解析几何，其精度上限由纹素密度决定，并非真正等价于矢量图形。

**误区三：SDF阈值0.5对应真实的几何边界**。在实际生成SDF纹理时，若输入的光栅化形状存在抗锯齿（半透明边缘像素），距离场的零点可能并不严格对应视觉轮廓。使用带有抗锯齿的源图像生成SDF时，需先二值化再计算距离场，否则渲染时0.5阈值处的轮廓会产生系统性偏移。

## 知识关联

SDF纹理建立在纹理映射的基础概念之上：它复用了UV坐标系统、双线性过滤和纹理图集打包等标准机制，但将纹素含义从颜色扩展为标量距离值。理解标准纹理的采样插值原理（尤其是双线性过滤对距离值的平滑效果如何贡献抗锯齿）是使用SDF的必要前提。

在图形渲染的更广阔领域中，SDF的思想延伸至三维空间形成体积SDF（Volume SDF），用于光线步进（Ray Marching）渲染隐式曲面，以及碰撞检测中的距离查询。对于专注于UI和文字渲染的应用场景，掌握SDF纹理后可进一步研究子像素渲染（Subpixel Rendering）技术，后者通过利用LCD屏幕RGB子像素排列进一步提升水平方向的文字清晰度，与SDF技术形成互补。