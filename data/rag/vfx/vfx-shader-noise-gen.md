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
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-06
---


# 噪声生成

## 概述

噪声生成是Shader编程中用于创建有机感纹理的程序化技术，核心思想是在GPU上通过纯数学运算实时生成伪随机数值场，无需任何外部纹理资源。其输出是一个连续可微的标量场（或向量场），在任意UV坐标下均可求值，天然支持无限平铺且精度与分辨率无关。

Perlin噪声由Ken Perlin于1983年为迪士尼电影《电子世界争霸战》（*Tron*）开发特效时首次实现，并于1985年在SIGGRAPH会议上以论文《An Image Synthesizer》正式发表（Perlin, 1985）。该论文当年获得SIGGRAPH最佳论文奖，Perlin本人也因此于1997年获得奥斯卡科学技术奖。1999年，Perlin发表改进版（Improved Perlin Noise），将梯度插值的平滑函数从三次Hermite曲线升级为六次多项式，同时将梯度向量集缩减为12个固定方向，消除了原版在轴对齐45°方向上产生的视觉条纹伪影。

Voronoi/Worley噪声则由Steven Worley于1996年在SIGGRAPH论文《A Cellular Texture Basis Function》中独立提出（Worley, 1996），算法核心是计算任意点到散布特征点集合的距离，产生类细胞分裂的有机图案。两种噪声的发明背景、数学原理和视觉风格截然不同，适用场景互补，共同构成了现代实时渲染中程序化纹理的两大基石。

---

## 核心原理

### Perlin噪声的梯度插值机制

Perlin噪声的计算管线分为三个严格有序的步骤：

**第一步——网格分配**：将输入UV坐标 $(u, v)$ 分解为整数部分 $\lfloor u \rfloor, \lfloor v \rfloor$（所属单元格索引）和小数部分 $(u - \lfloor u \rfloor, v - \lfloor v \rfloor)$（单元格内的局部坐标）。

**第二步——梯度哈希**：对网格四个顶点 $(i,j), (i+1,j), (i,j+1), (i+1,j+1)$ 分别计算哈希值，映射到预定义的梯度向量集合。在改进版Perlin噪声中，梯度集被固定为12个单位向量：$(±1,±1,0), (±1,0,±1), (0,±1,±1)$，点积计算因此可简化为加减法，避免了乘法开销。

**第三步——平滑插值**：使用六次多项式Fade函数对局部坐标进行平滑，再双线性插值四个顶点的梯度点积结果。

Fade函数（六次多项式）的精确形式为：

$$f(t) = 6t^5 - 15t^4 + 10t^3$$

该多项式满足 $f(0)=0,\ f(1)=1,\ f'(0)=f'(1)=0,\ f''(0)=f''(1)=0$，即在网格边界处一阶导数和二阶导数均连续为零。相比早期使用的三次Hermite插值 $3t^2 - 2t^3$（只保证一阶连续），六次版本在放大100倍以上观察时不会出现可见接缝。

### Voronoi/Worley噪声的最近点搜索

Worley噪声的数学定义是：对于空间中任意点 $\mathbf{P}$，将空间均匀划分为单元格，每格内随机放置一个特征点（坐标由哈希函数确定），计算 $\mathbf{P}$ 到所有特征点的距离并排序，取第 $n$ 小的距离值作为输出。

最常用的三种输出方式：
- **F1**：最近邻距离，产生多边形Voronoi分区感，适合岩石裂纹、皮肤纹理
- **F2**：次近邻距离，轮廓更圆润，常用于有机细胞壁效果
- **F2 − F1**：两者之差，产生均匀宽度的细胞边界线，常用于气泡、肥皂泡、熔岩灯Shader

为避免遗漏跨越单元格边界的近邻特征点，2D情况下必须检查当前格及**周围8个相邻格**（共9格），3D情况则需检查**27个相邻格**。若只检查4邻域或6邻域，会在单元格边界产生明显的距离跳变断层。

使用欧氏距离（Euclidean）产生圆形泡状轮廓；改用曼哈顿距离（Manhattan，$|dx|+|dy|$）产生菱形网格图案；使用Chebyshev距离（$\max(|dx|,|dy|)$）产生矩形方块图案。同一套Worley算法更换距离度量即可获得截然不同的视觉风格。

### 分形布朗运动（fBm）多层叠加

单层Perlin噪声频率单一、细节扁平，实际使用中通过分形布朗运动（Fractional Brownian Motion，fBm）叠加多个倍频层：

$$\text{fBm}(\mathbf{x}) = \sum_{i=0}^{N-1} g^i \cdot \text{noise}(l^i \cdot \mathbf{x})$$

其中 $l$ 为频率倍增因子（lacunarity，标准值 = **2.0**），$g$ 为振幅衰减因子（gain，标准值 = **0.5**），$N$ 为叠加层数（octaves，常用 **4~8**）。

当 $g=0.5$ 时，fBm的功率谱密度 $S(f) \propto f^{-2}$，与自然界中大量随机过程（云层、山脉轮廓、湍流）的功率谱一致，这正是fBm噪声视觉上"真实自然"的数学原因。每增加一个octave，GPU采样计算量线性增加，在移动端通常限制在4层以内。

---

## 关键代码实现

以下是GLSL中完整的2D Perlin噪声实现，包含哈希函数、Fade函数和梯度插值：

```glsl
// 哈希函数：将整数网格坐标映射为伪随机梯度方向
vec2 hash2(vec2 p) {
    // 魔数 127.1, 311.7, 43758.5453 在 GPU 单精度下分布均匀
    p = vec2(dot(p, vec2(127.1, 311.7)),
             dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}

// 六次多项式 Fade 函数（Improved Perlin Noise, 1999）
vec2 fade(vec2 t) {
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0);
}

// 2D Perlin 噪声，输出范围约 [-1, 1]
float perlinNoise(vec2 uv) {
    vec2 i = floor(uv);      // 整数网格坐标
    vec2 f = fract(uv);      // 单元格内局部坐标

    // 四角梯度点积
    float va = dot(hash2(i + vec2(0,0)), f - vec2(0,0));
    float vb = dot(hash2(i + vec2(1,0)), f - vec2(1,0));
    float vc = dot(hash2(i + vec2(0,1)), f - vec2(0,1));
    float vd = dot(hash2(i + vec2(1,1)), f - vec2(1,1));

    vec2 u = fade(f);
    // 双线性插值
    return mix(mix(va, vb, u.x), mix(vc, vd, u.x), u.y);
}

// 4层 fBm 叠加
float fbm(vec2 uv) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    for (int i = 0; i < 4; i++) {
        value += amplitude * perlinNoise(uv * frequency);
        frequency *= 2.0;   // lacunarity = 2.0
        amplitude *= 0.5;   // gain = 0.5
    }
    return value;
}
```

上述代码中，`hash2` 使用 `sin` 函数配合魔数产生伪随机值。注意：在某些移动GPU（如Mali-400）上，`sin` 精度不足会导致哈希分布出现周期性条纹，此时应改用整数位运算哈希（如 PCG Hash）代替。

---

## 实际应用案例

**案例一：云雾效果**
将4~6层fBm噪声输出映射为透明度，配合时间偏移 `uv + vec2(_Time * 0.05, 0)` 使噪声场随时间平移，产生流动云层效果。云朵的蓬松感来自高层数fBm（octaves=6），而薄雾的柔和感只需2层。Unity内置的`Simple Noise`节点即采用此方案。

**案例二：熔岩/细胞材质**
使用Worley噪声的F2−F1输出作为自发光遮罩：F2−F1值接近0处（细胞边界）赋予高亮橙色自发光，值较大处（细胞中心）赋予深红色漫反射，叠加时间扭曲后产生熔岩流动感。《英雄联盟》地狱火皮肤的地面材质采用了类似技术路线。

**案例三：地形高度图生成**
在顶点着色器中，用5层fBm噪声采样结果直接修改顶点Y坐标，配合`lacunarity=2.17`（非整数倍可避免频率重合产生的周期感）生成程序化地形。Minecraft的新地形生成算法（Java Edition 1.18，2021年发布）从原版3D Perlin噪声迁移至3D Simplex噪声，性能提升约3倍。

**案例四：UV扰动（Domain Warping）**
将一次fBm的输出作为UV偏移量，再用扰动后的UV计算第二次fBm，称为Domain Warping（领域扭曲）。Inigo Quilez于2002年在Shadertoy上首次展示此技术，产生极具流体感的卷曲湍流效果，两次fBm叠加仅需约8次噪声采样，GPU开销可接受。

---

## 常见误区

**误区一：将噪声输出范围误认为 [0, 1]**
Perlin噪声的理论输出范围是 $[-1, 1]$，但受梯度方向分布影响，实际极值约在 $[-0.7, 0.7]$ 左右，而非精确的 $±1$。直接将其作为颜色输出时必须先执行 `value * 0.5 + 0.5` 的重映射，否则负值会被GPU截断为0，产生大片纯黑区域。Worley噪声的F1输出范围同样依赖特征点密度，并非自动归一化到 [0, 1]。

**误区二：3×3邻域搜索足够覆盖所有Worley情况**
仅当特征点始终位于单元格中心附近时，3×3邻域才足够。但若哈希函数将特征点映射到单元格边缘，最近邻特征点完全可能来自距离2格以上的位置，必须扩展到5×5邻域（2D）才能保证正确性。实际工程中常见的做法是将特征点坐标乘以缩放因子（如 `0.7`）限制在单元格内侧，以此保证3×3邻域充分，同时换取更紧凑的细胞排布。

**误区三：fBm层数越多越好**
每增加一层octave，高于奈奎斯特频率的细节在最终渲染分辨率下无法被像素区分，只会增加GPU计算量和数值噪声（浮点精度损失），并不产生可见的视觉增益。在1920×1080分辨率下，通常第6层octave（频率 = $2^6 = 64$ 倍基础频率）已接近单像素尺度，继续叠加属于无效计算。

**误区四：Simplex噪声与Perlin噪声完全等价**
Ken Perlin于2001年提出Simplex噪声作为Perlin噪声的替代方案。在2D情况下，Simplex噪声每次求值只需访问**3个**顶点（而Perlin需要4个），3D情况下只需4个顶点（Perlin需要8个），且不存在轴对齐方向性伪影。但2D和3D Simplex噪声的原始专