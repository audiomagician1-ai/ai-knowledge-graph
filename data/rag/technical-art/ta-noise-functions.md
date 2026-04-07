---
id: "ta-noise-functions"
concept: "噪声函数"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 3
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# 噪声函数

## 概述

噪声函数（Noise Function）是一类能够生成视觉上随机、但在数学上连续且可重复的伪随机函数。与真正的随机数不同，噪声函数的输出在空间上是平滑过渡的——相邻位置的采样值差距不会突然跳变。这种"有序的混乱"特性使它成为程序化生成云、火焰、地形、木纹等自然纹理的基础工具。

噪声函数的历史可以追溯到1983年，Ken Perlin在参与电影《电子世界争霸战》（Tron）的视觉效果制作时，为了解决计算机生成图像过于机械的问题，发明了以他名字命名的Perlin噪声（Perlin Noise）。这项发明在1997年为他赢得了奥斯卡技术成就奖。2001年，Perlin又发布了改进版本Simplex噪声，将N维噪声的计算复杂度从O(2ᴺ)降低到O(N²)，在高维情况下性能提升显著。Worley噪声（又称细胞噪声/Voronoi噪声）则由Steven Worley在1996年提出，通过寻找最近特征点来生成截然不同的有机感图案。

在Shader开发中，噪声函数运行在GPU着色器程序里，每帧对数百万像素并行求值。理解三种主要噪声的数学原理和GLSL/HLSL实现方式，是制作程序化材质、流体模拟、地形渲染等效果的必要技能。

## 核心原理

### Perlin 噪声的梯度插值机制

Perlin噪声的核心思路是：将空间划分为整数网格，在每个网格顶点处分配一个伪随机的**梯度向量**，然后对查询点到各顶点的贡献进行加权插值。

以2D为例，对坐标点 `(x, y)` 求值时：
1. 计算所在整数格子的四个顶角坐标 `(i, j)`；
2. 用置换表（Permutation Table，通常是预先打乱的0~255整数数组）为每个顶角查找梯度向量；
3. 计算从顶角到查询点的**偏移向量**，与梯度向量做点积；
4. 使用缓动函数（Fade Function）`f(t) = 6t⁵ - 15t⁴ + 10t³`（Improved Perlin Noise版本）对四个点积结果进行双线性插值。

该缓动函数的一阶和二阶导数在 t=0 和 t=1 处均为0，确保了网格边界处的连续性，避免了早期版本 `f(t) = 3t² - 2t³` 存在的二阶不连续瑕疵。

GLSL实现片段：
```glsl
float fade(float t) { return t * t * t * (t * (t * 6.0 - 15.0) + 10.0); }
float grad(int hash, float x, float y) {
    int h = hash & 3;
    float u = h < 2 ? x : y;
    float v = h < 2 ? y : x;
    return ((h & 1) == 0 ? u : -u) + ((h & 2) == 0 ? v : -v);
}
```

### Simplex 噪声的单纯形格子

Simplex噪声抛弃了正方形网格，改用**单纯形（Simplex）**——2D中是三角形，3D中是四面体，N维中是N+1个顶点的多胞体。这样每次只需对 `N+1` 个顶角求梯度贡献，而非 Perlin 噪声的 `2ᴺ` 个。

2D Simplex噪声的倾斜变换（Skew Transform）系数为 `F = (√3 - 1) / 2 ≈ 0.366`，逆变换系数为 `G = (3 - √3) / 6 ≈ 0.211`。通过这对系数，可以将正方形坐标系和三角形坐标系相互转换，从而快速确定查询点落在哪个三角形单纯形内。Simplex噪声还有一个视觉优势：没有 Perlin 噪声那种明显的轴对齐方向性伪影。

### Worley 噪声的特征点距离场

Worley噪声的算法完全不同：在空间中随机散布**特征点（Feature Points）**，对于查询点 P，计算它到最近特征点的距离 F₁，以及到第二近特征点的距离 F₂。常见变体：

- `F₁`：产生细胞状图案，适合生成龟裂皮肤、泡沫
- `F₂ - F₁`：产生网格线效果，适合蜘蛛网、叶脉
- `F₁ * F₂`：产生更复杂的有机纹理

实现时关键的优化：将空间分成边长为1的网格单元，每格内放置一个特征点（坐标 = 格子整数坐标 + hash(格子坐标) 得到的随机偏移）。查询时只需检查当前格和周围 `3×3=9` 个（2D）或 `3×3×3=27` 个（3D）邻格，而不必遍历全部特征点。

### 分形布朗运动（fBm）叠加

单层噪声往往过于平滑。分形布朗运动（Fractional Brownian Motion，fBm）通过叠加多层不同频率和振幅的噪声来模拟自然界的多尺度细节：

```
fBm(p) = Σ amplitude * noise(p * frequency)
         frequency *= lacunarity  (常用值 2.0)
         amplitude *= gain        (常用值 0.5)
```

这里 `lacunarity`（间隙度）控制每层频率倍增比，`gain`（增益，又称persistence持续度）控制每层振幅衰减比。叠加的层数称为**倍频程（Octaves）**，通常取4~8层。

## 实际应用

**云和体积雾**：使用4~6层fBm叠加Perlin噪声，以世界空间XYZ坐标加上时间偏移采样，实现动态流动云层。Unity的VolumetricClouds就使用了这种方案。

**地形高度图**：以地表XZ坐标输入2D fBm，输出Y轴高度，配合侵蚀算法后处理，能生成山地、平原的多尺度地形特征。

**程序化木纹**：将 `sin(x * 10 + Perlin(x, y) * 5)` 形式的公式中，用Perlin噪声对正弦波的相位施加扰动，产生弯曲的年轮纹路。

**火焰和岩浆**：对UV坐标用随时间变化的噪声进行偏移扭曲，然后映射到颜色渐变（Gradient），即可得到动态火焰效果。HLSL中实现一般需要2~3次噪声采样：一次驱动整体形态，一次添加细节扰动。

**Worley噪声应用**：将F₁距离值取反后做色调映射，可产生蜡质皮肤的次表面散射细胞图案；用于法线贴图扰动可模拟鳞片、蜂窝表面。

## 常见误区

**误区一：噪声函数等于随机函数**
很多初学者把 `rand()` 和噪声函数混用。`rand(uv)` 之类的哈希函数在相邻像素间完全无关，结果是纯噪点（白噪声）。而Perlin/Simplex噪声保证了空间连续性，频率可控，这才是程序化纹理可用的本质原因。在Shader中，高频白噪声会在摄像机移动时产生严重的时域闪烁（Temporal Aliasing），而噪声函数则不会。

**误区二：直接用世界坐标采样导致纹理漂移**
如果将网格的世界空间UV直接传入噪声函数，当物体移动时纹理图案会相对于物体表面滑动。正确做法是使用模型的本地空间（Object Space）坐标作为噪声输入，这样纹理随物体一起运动，像是"印"在表面上的真实材质。

**误区三：fBm倍频程越多越好**
受奈奎斯特采样定理约束，当噪声频率超过纹理分辨率的一半时，高频细节无法被正确显示，反而引入摩尔纹和锯齿。对于实时渲染，fBm层数一般不超过6层，超过后视觉收益接近零但GPU计算开销线性增加。屏幕像素尺寸对应的世界空间频率是选择最大倍频数的实用依据。

## 知识关联

**前置概念**：Shader数学基础中的向量点积直接用于Perlin噪声的梯度计算；插值函数（Lerp/Smoothstep）是噪声内部插值的具体实现；UV坐标变换（缩放、平移）决定了噪声的采样频率和世界对应关系。

**后续应用——SDF着色器**：噪声函数常被用于扰动SDF（有向距离场）的边界，使圆形SDF的边缘变得粗糙不规则，从而模拟云朵、火焰轮廓或生物细胞边界。`sdf_circle(p + noise(p) * 0.3)` 这种组合是SDF有机感的标准技法。

**后续应用——程序化材质**：在Substance Designer和材质Graph中，