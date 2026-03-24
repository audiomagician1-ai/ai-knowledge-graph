---
id: "vfx-shader-noise-gen"
concept: "噪声生成"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 噪声生成

## 概述

噪声生成是指在Shader程序内部通过数学函数实时计算出具有自然随机特征的连续值场，无需采样外部贴图。Shader中最常用的三种噪声算法是Perlin噪声、Voronoi噪声和Worley噪声，它们各自产生截然不同的视觉特征：Perlin噪声输出平滑的云雾状纹理，Voronoi噪声产生多边形细胞分割图案，Worley噪声（本质上与Voronoi是同族算法）生成类似石材或皮肤组织的颗粒状网格。

Perlin噪声由Ken Perlin于1983年为电影《创：战纪》（Tron）开发，并因此获得1997年技术类奥斯卡奖。其核心思想是将空间划分为网格，在每个整数坐标处存储随机梯度向量，然后通过插值将相邻格点的梯度混合成连续平滑的标量场。Voronoi噪声则由数学家Georgy Voronoi于1908年提出，在Shader中的实现通常涉及将空间划分为若干Tile，在每个Tile中随机放置一个特征点，输出当前像素到最近特征点的距离。

在实时Shader中自行生成噪声而非采样贴图，好处在于可以对噪声参数（频率、相位、种子）进行动态修改，制作出随时间演变的火焰、水面、云层等效果，并且完全避免了贴图重复平铺的问题。

## 核心原理

### Perlin噪声的梯度插值

Perlin噪声的GLSL实现依赖一个伪随机哈希函数和平滑插值曲线。标准实现中常用的平滑步函数为 **fade(t) = 6t⁵ - 15t⁴ + 10t³**，这是Ken Perlin在2002年"Improved Noise"版本中将早期的 **3t² - 2t³** 替换后的结果，目的是使插值在端点处的二阶导数为零，从而消除早期版本在网格边界上出现的高频瑕疵。

在Shader中，整数坐标处的梯度向量通常由哈希函数近似：先取坐标的点积与常数（如`dot(p, vec2(127.1, 311.7))`），再通过`fract(sin(x) * 43758.5453)`生成伪随机值。最终的噪声值是当前像素位置相对于四个（2D情况）或八个（3D情况）邻近格点的偏移向量与梯度向量的点积，经过fade插值后的加权平均。

### Voronoi噪声的特征点搜索

Voronoi噪声的计算核心是"最近邻搜索"。标准做法是将UV空间划分为边长为1的Tile，对于每个片元，搜索其所在Tile及周围8个相邻Tile（共9格），在每格内用哈希函数生成一个随机特征点坐标，计算片元到该特征点的欧式距离，取最小值作为输出。

输出值可以是：
- **F1**：到最近特征点的距离，产生亮度随距离渐变的平滑圆形区域；
- **F2 - F1**：到第二近与最近特征点距离之差，产生清晰的细胞边界线条；
- **F1 / F2**：归一化比值，常用于石材纹理。

距离度量不必使用欧式距离，改用曼哈顿距离（`|dx| + |dy|`）会产生菱形细胞，改用切比雪夫距离（`max(|dx|, |dy|)`）会产生方形细胞。

### FBM分形布朗运动叠加

单层噪声过于规则，实际应用中几乎总是将多个频率倍增的噪声层叠加，称为分形布朗运动（Fractal Brownian Motion，FBM）。标准公式为：

**FBM(p) = Σ(amplitude × noise(p × frequency))**

其中每次迭代将`frequency`乘以2（即lacunarity=2），将`amplitude`乘以0.5（即gain=0.5）。叠加6至8个octave后，结果的Hurst指数H≈0.5，视觉上与自然地形高度场高度相似。在Shader中，通常每加一个octave会增加若干指令数（ALU cost），需要在精度与性能之间权衡，移动端项目常将octave数限制在4以内。

## 实际应用

**火焰效果**：以`time`参数驱动Perlin FBM的UV偏移，沿Y轴方向累积运动，同时用噪声值驱动颜色梯度从红→橙→黄→白的过渡，噪声的垂直拉伸（Y轴scale放大2~3倍）模拟火舌细长的形状。

**溶解描边**：将Voronoi F2-F1的细胞边界线与一个从0到1的`dissolveThreshold`参数比较，当像素的噪声值小于阈值时discard，边界附近（距离阈值差值在0.05内）着发光描边颜色，制作出魔法溶解边缘的效果。

**水面法线扰动**：用两层Perlin噪声（方向相反的UV偏移）生成法线扰动向量，叠加后对环境贴图坐标进行扰动采样，产生轻微波纹。两层偏移速度比约为1:1.3，避免出现明显的周期感。

**云层生成**：在UV空间直接用FBM生成密度场，将密度阈值以下的区域设为透明（alpha=0），阈值以上用smoothstep映射至白色，并在密度中等区域叠加一层更高频的噪声增加细节卷曲感。

## 常见误区

**误区一：认为`fract(sin(dot(...)) * 43758.5)`是真随机**。这个公式在GPU上是纯确定性的哈希函数，对相同输入永远返回相同输出。它利用sin函数在大参数下的混沌行为模拟随机性，但部分GPU（尤其是低精度模式下的移动端GPU）会因为浮点精度不足导致哈希函数出现明显条纹或重复块，解决方案是改用整数位运算哈希（如xxHash）或将精度指定为`highp`。

**误区二：Worley噪声与Voronoi噪声是两种完全不同的算法**。Steven Worley在1996年发表的论文《A cellular texture basis function》中描述的算法与Voronoi图的距离场本质上是同一类，区别仅在于Worley论文中使用的是泊松圆盘分布的特征点而非Tile哈希，以及引入了F1、F2、F2-F1的组合表达方式。现代Shader教程中的"Voronoi噪声"往往已经包含了Worley的距离组合思想。

**误区三：octave越多效果越好**。在fragment shader中，每增加一个octave意味着约增加1次哈希计算和2次纹理坐标变换，超过8个octave后人眼在屏幕分辨率下已无法区分细节差异，但GPU的ALU开销依然线性增加；更严重的是，当噪声的最高频率分量在屏幕空间下超过1像素/周期时，会产生摩尔纹或走样，此时应当截断octave而非继续叠加。

## 知识关联

**前置概念——极坐标变换**：在极坐标系中对Perlin或Voronoi噪声的输入UV进行变换，可以将线性噪声弯曲成环形纹理（如涡旋火焰、行星云带），具体做法是将`vec2(atan(y, x), length(p))`作为噪声函数的输入，atan分量决定角度方向的频率，length分量决定径向频率。理解极坐标的角度-半径映射关系，是控制环形噪声拉伸比例的前提。

**后续概念——边缘光（Rim Light）**：噪声生成在边缘光效果中的典型用途是打破均匀边缘的单调感。将视线方向与法线的点积（经典rim因子）与一层Perlin FBM相乘，可以产生忽明忽暗、不规则发光的能量护盾效果；也可以用Voronoi F2-F1在边缘区域叠加细胞纹理，模拟熔岩冷却后的裂纹发光边缘。噪声的频率与边缘光衰减宽度的匹配，直接决定边缘细节的粗细程度。
