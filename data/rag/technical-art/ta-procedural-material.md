---
id: "ta-procedural-material"
concept: "程序化材质"
domain: "technical-art"
subdomain: "material-system"
subdomain_name: "材质系统"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.2
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-25
---

# 程序化材质

## 概述

程序化材质（Procedural Material）是指完全通过数学函数和算法在着色器内部实时计算生成外观效果的材质系统，不依赖任何预先烘焙的位图贴图（Bitmap Texture）。其视觉细节——包括颜色、粗糙度、法线扰动、遮蔽等——全部由 GPU 在每帧渲染时动态推导。这与传统的纹理采样材质有本质区别：传统材质通过 `texture2D(sampler, uv)` 从存储的像素数据中读取颜色，而程序化材质通过 `f(x, y, z, t)` 这样的纯函数计算颜色，输入是世界坐标或 UV 坐标，输出是材质属性。

程序化材质的理论基础可追溯至 1985 年 Ken Perlin 为电影《电子世界争霸战》续集开发 Perlin Noise 的工作，以及同年 Ken Musgrave 对分形布朗运动（fBm）的程序化纹理研究。Pixar 在其 RenderMan 着色语言中将程序化纹理列为核心特性，使其在离线渲染领域得到广泛普及。实时领域则随着可编程着色器（Shader Model 2.0，2002 年）的出现逐步实用化。

程序化材质的核心价值在于无限分辨率与无缝平铺：因为是数学函数，在任何缩放级别下都能以屏幕像素的精度生成细节，不存在传统贴图在近距离产生的像素化问题。同时，通过调整参数可以即时变更整个材质的外观，一套程序化木纹着色器通过修改纹路方向角度、年轮间距等参数可以生成数百种木材变体。

## 核心原理

### 噪声函数的程序化组合

程序化材质的最基础构建块是各类噪声函数。最常用的是 Simplex Noise 和 Value Noise，其输出范围均为 `[-1, 1]` 或 `[0, 1]`。单层噪声只能生成平滑的低频变化，无法表达真实材质的多尺度细节。因此几乎所有程序化材质都采用**分形布朗运动（fBm）**叠加多倍频：

```
fBm(p) = Σ(i=0 to N) amplitude_i × noise(p × frequency_i)
```

其中每一层的 `frequency_i = lacunarity^i`（lacunarity 通常取 2.0），`amplitude_i = gain^i`（gain 通常取 0.5）。叠加 6~8 个倍频后，可以模拟出云层、大理石纹、山地地形等具有自相似结构的自然材质。沃罗诺伊噪声（Worley/Cellular Noise）则通过计算点到最近特征点的距离 `F1 = min_i(distance(p, cell_i))`，专门生成细胞状、鹅卵石状的有机图案，是程序化皮肤、石材材质的常用基础。

### 域扭曲技术（Domain Warping）

域扭曲是程序化材质中产生复杂有机感外观的关键技术，由 Inigo Quilez 在其 Shadertoy 作品中系统化推广。其原理是用一个噪声函数的输出来偏移另一个噪声函数的输入坐标：

```glsl
vec2 q = vec2(fbm(p + vec2(0.0, 0.0)),
              fbm(p + vec2(5.2, 1.3)));
float result = fbm(p + 4.0 * q);
```

通过两次甚至三次嵌套扭曲（称为 second-order 和 third-order domain warping），可以生成极为复杂的涡旋状、流体状图案，是程序化岩浆、烟雾、水面材质的核心手段。关键参数是扭曲强度系数（上例中的 `4.0`），数值越大扭曲越剧烈，过高会导致图案失去结构。

### 数学图案构造

除噪声外，程序化材质大量使用确定性数学函数直接构造规则图案。棋盘格通过 `fract(p * scale)` 的整数奇偶性判断，砖墙纹理通过对 UV 按行偏移半个单元再取模得到，木纹年轮通过 `sin(distance(p, center) * rings_per_unit + fbm(p) * distortion)` 生成。这些确定性图案与噪声叠加时，`smoothstep(edge0, edge1, x)` 函数用于控制过渡区域的软硬度，是避免程序化材质出现锯齿的关键。色彩映射则通常通过将 `[0,1]` 的噪声值输入调色曲线（Gradient Ramp）或使用余弦色彩调色板公式 `color = a + b × cos(2π(c×t + d))` 实现丰富的颜色变化。

## 实际应用

**游戏引擎中的程序化材质**：Unreal Engine 的材质编辑器内置了 `MF_Noise`、`Voronoi`、`MakeMaterialAttributes` 等节点，允许美术师无需编写 GLSL 即可搭建程序化材质图。Substance Designer 则是目前技术美术领域最主流的程序化材质创作工具，其输出的 `.sbsar` 格式文件本质上是一个打包的着色器函数网络，在游戏引擎运行时通过 Substance Runtime 动态计算贴图。典型的程序化混凝土材质在 Substance Designer 中包含约 20~40 个节点。

**无限地形的材质混合**：开放世界游戏（如《荒野大镖客2》的地形系统）使用程序化材质根据世界坐标的高度、坡度、曲率等参数自动混合多种地表材质。其混合权重完全由程序化函数实时计算，避免了手工绘制权重贴图的工作量，并且在任意地形尺度下都能保持细节一致性。

**运行时参数动画**：程序化材质可以将时间 `t` 作为输入参数，实现无缝的动态材质效果。熔岩材质通过 `p += vec3(0, t * lava_speed, 0)` 将域扭曲后的噪声以恒定速度偏移，产生流动感；护盾击中特效通过将冲击点坐标和 `t` 输入程序化涟漪函数，生成向外扩散的波纹高光。这类效果若用传统贴图序列实现，内存开销将高出数十倍。

## 常见误区

**误区一：程序化材质总是比贴图材质性能差**。实际上，一次 `texture2D` 采样在移动端 GPU 上约耗费 4~8 个算术逻辑单元（ALU）周期，而中等复杂度的 fBm（4 倍频 Perlin Noise）约耗费 60~120 个 ALU 周期。程序化材质在高倍频数时确实比单次贴图采样昂贵，但与需要采样多张贴图（Albedo + Normal + Roughness + AO = 4次采样 + 混合计算）的复杂 PBR 材质相比，性能差距大幅缩小。对于大量平铺使用的地面材质，程序化方案可以减少纹理内存带宽压力，在内存带宽受限的场景中反而有性能优势。

**误区二：程序化材质只能生成"自然有机"图案，不能做硬表面材质**。这是对程序化材质应用范围的严重低估。金属拉丝纹理可通过沿 U 方向的高频 Value Noise + 低频 Perlin Noise 叠加精确模拟；划痕可通过沃罗诺伊噪声的 F1-F2 差值结合方向阈值生成；电路板走线图案可通过曼哈顿距离场（Manhattan Distance Field）构造。Substance Designer 的内置预设中有超过 30 种专门针对硬表面工业材质的程序化方案。

**误区三：程序化材质等同于"无需美术介入的自动材质"**。程序化材质降低了重复劳动，但并未消除美术创作判断。一个高质量的程序化大理石材质需要美术师精确理解大理石的纹路走向规律、矿物颜色分布特征，并将这些知识转化为正确的噪声类型选择、叠加策略和色彩映射曲线。程序化材质的参数调整本身就是高度依赖审美经验的创作过程，并非填入参数即可自动生成令人满意的结果。

## 知识关联

程序化材质直接建立在噪声函数知识之上：Perlin Noise、Simplex Noise、Worley Noise 的数学特性（频率、振幅、连续性）直接决定了程序化材质的视觉特征，必须理解各类噪声函数的输出分布才能有效设计程序化材质的数学结构。此外，理解 UV 坐标系和着色器编程基础（GLSL/HLSL 中的 `fract`、`smoothstep`、`mix` 等内置函数）是实现程序化材质的必要前提。

程序化材质的思想进一步延伸到**程序化几何生成**（Houdini 中的程序化建模）和**程序化动画**领域，三者共同构成"程序化内容生成（PCG）"的技术美术实践体系。掌握程序化材质的数学构造思维