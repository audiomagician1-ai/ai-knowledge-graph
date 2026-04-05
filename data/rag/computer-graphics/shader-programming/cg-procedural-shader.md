---
id: "cg-procedural-shader"
concept: "程序化着色器"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 3
is_milestone: false
tags: ["技术"]

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
updated_at: 2026-03-26
---


# 程序化着色器

## 概述

程序化着色器（Procedural Shader）是指在着色器代码中通过数学函数实时计算颜色、纹理和材质细节，而不依赖预先存储的图像文件。这种方式的核心工具是**噪声函数**——特别是Perlin噪声（1983年由Ken Perlin为电影《电子世界争霸战》开发）、Simplex噪声（2001年Perlin改进版）以及Worley噪声（1996年Steven Worley提出）。三种噪声函数各有特性，Perlin噪声产生有机的流动感纹理，Worley噪声生成细胞状或晶体状图案，Simplex噪声则在高维时计算效率显著优于Perlin噪声。

程序化着色器之所以重要，在于它能以极小的存储代价生成理论上无限分辨率的纹理。一张1024×1024的PNG纹理占用约3MB存储空间，而实现相同视觉复杂度的程序噪声代码通常不超过50行GLSL，存储量仅几KB。这一特性使程序化着色器在游戏、电影CGI和实时渲染领域被广泛采用，尤其适合需要无缝平铺、无限细节缩放的场景（如地形、云层、大理石纹理）。

## 核心原理

### Perlin噪声的数学构造

Perlin噪声通过以下步骤生成：首先将空间划分为整数格子，在每个格点上分配一个伪随机梯度向量；然后对查询点与各格点的距离向量和对应梯度向量做点积，得到影响值；最后使用**平滑插值函数** `fade(t) = 6t⁵ - 15t⁴ + 10t³`（即"quintic curve"，取代早期版本的三次曲线以消除二阶导数不连续）对各格点影响值进行插值混合。其中 `t` 是查询点到格点的归一化距离。最终得到的值域约为 [-1, 1]，实际常规范化到 [0, 1] 使用。

在GLSL中，一个2D Perlin噪声的典型调用如下：
```glsl
float n = perlinNoise(uv * 4.0); // 频率4.0倍，控制图案尺度
float color = n * 0.5 + 0.5;     // 重映射到[0,1]
```

### 分形叠加（fBm）

单层噪声往往过于平滑，实际应用中几乎总是使用**分形布朗运动（fBm，Fractal Brownian Motion）**：将多层不同频率和振幅的噪声叠加。标准公式为：

```
fBm(x) = Σ(i=0 to n-1) [ amplitude^i × noise(frequency^i × x) ]
```

其中 `amplitude`（持久度）通常取0.5，`frequency`（拉卡纳里提）通常取2.0，每叠加一层称为一个**倍频程（octave）**。叠加6~8层倍频程可以模拟云层、山脉轮廓等自然界的分形特征。振幅每翻倍频率时缩小一半，确保高频细节不会主导整体形态。

### Worley噪声与细胞纹理

Worley噪声（也称为细胞噪声或Voronoi噪声）的计算逻辑与Perlin截然不同：将空间划分为单元格，在每个单元格内随机放置一个特征点，对空间中任意查询点，计算其与**最近特征点的距离** F1，以及到**第二近特征点的距离** F2。利用 F1、F2 或 F2-F1 可分别生成不同视觉效果——F1产生细胞膜状图案，F2-F1产生网格线状图案，广泛用于模拟生物组织、石砖缝隙、星云结构。

```glsl
// Worley噪声的距离计算核心
float F1 = 8.0;
for (int i = -1; i <= 1; i++) {
    for (int j = -1; j <= 1; j++) {
        vec2 neighbor = vec2(float(i), float(j));
        vec2 point = random2(cell + neighbor); // 单元格内随机特征点
        float d = length(neighbor + point - fract_uv);
        F1 = min(F1, d);
    }
}
```

## 实际应用

**大理石纹理**是程序化着色器的经典案例。将坐标的x分量加上Perlin fBm噪声后输入sin函数：
```glsl
float marble = sin(uv.x * 10.0 + fBm(uv * 3.0) * 8.0);
```
这一行代码即可产生逼真的大理石纹脉，通过调整10.0（条纹密度）和8.0（扭曲强度）控制最终外观。

**云层和体积雾**使用3D fBm噪声，在片元着色器中对光线方向进行多次采样（Ray Marching），每步累积噪声密度值，实现体积云的散射效果。游戏《无人深空》（2016年，Hello Games）的行星大气即大量依赖这类程序化噪声生成。

**地形高度图生成**中，Shadertoy平台上大量地形Demo（如iq的"Elevated"示例）仅用约100行GLSL代码，通过8层fBm噪声驱动的位移贴图生成包含山脉、峡谷、侵蚀细节的完整地形，无需任何外部资源文件。

## 常见误区

**误区一：认为Perlin噪声是真正随机的。** Perlin噪声是**伪随机确定性函数**——相同的输入坐标永远返回相同的输出值，这正是它的设计目标。真正的随机函数（如每帧调用`rand()`）会产生白噪声（雪花屏），完全没有连续性和空间相关性，无法用于纹理生成。Perlin噪声的"随机感"来自梯度向量的哈希映射，而其平滑性来自插值函数。

**误区二：认为噪声函数输出范围是严格的[0,1]或[-1,1]。** Perlin噪声的理论值域约为[-√(N/4), √(N/4)]（N为维度数），在实践中2D Perlin噪声的实际输出约在[-0.7, 0.7]之间，并非恰好±1。直接将输出乘以0.5加0.5进行重映射后，极端值仍然达不到0或1，颜色范围会被压缩。正确做法是记录实测最大最小值后进行精确归一化，或在着色器中使用`clamp()`截断。

**误区三：层数越多效果越好。** fBm的倍频程并非越多越好。超过8层后，高频噪声的贡献振幅已小于0.5⁸≈0.004，在8位颜色精度（256级）下已低于1/256，即人眼不可见，继续叠加只浪费GPU算力。在移动端着色器中，通常限制在4~5层倍频程以平衡画质与性能。

## 知识关联

程序化着色器直接建立在**片元着色器**的执行模型上——每个片元独立运行噪声计算，这正是程序纹理与CPU端程序纹理的本质区别：GPU的并行架构使每像素独立计算数十次噪声采样成为可行。片元着色器中的`gl_FragCoord`或传入的UV坐标为噪声函数提供空间输入参数，材质颜色由噪声输出直接驱动。

在Shadertoy（shadertoy.com）这一实践平台上，程序化噪声是最常见的技术主题，iq（Inigo Quilez）发布的噪声教程和GLSL实现被视为该领域的权威参考。掌握这套工具后，可进一步结合**光线步进（Ray Marching）**实现体积渲染，或结合**域变形（Domain Warping）**技术——即将噪声的坐标输入先经过另一层噪声扭曲——生成更复杂的有机流体状图案，这是程序纹理艺术表达的重要进阶方向。