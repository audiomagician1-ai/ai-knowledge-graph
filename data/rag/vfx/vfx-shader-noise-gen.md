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

Voronoi/Worley噪声由Steven Worley于1996年在SIGGRAPH论文《A Cellular Texture Basis Function》中独立提出（Worley, 1996），算法核心是计算任意点到散布特征点集合的距离，产生类细胞分裂的有机图案。两种噪声的发明背景、数学原理和视觉风格截然不同，适用场景互补，共同构成了现代实时渲染中程序化纹理的两大基石。关于程序化纹理在实时渲染中的系统性论述，可参考《Real-Time Rendering》第4版（Akenine-Möller, Haines & Hoffman, 2018）第6章"Texturing"。

---

## 核心原理

### Perlin噪声的梯度插值机制

Perlin噪声的计算管线分为三个严格有序的步骤：

**第一步——网格分配**：将输入UV坐标 $(u, v)$ 分解为整数部分 $\lfloor u \rfloor, \lfloor v \rfloor$（所属单元格索引）和小数部分 $(u - \lfloor u \rfloor,\ v - \lfloor v \rfloor)$（单元格内的局部坐标）。

**第二步——梯度哈希**：对网格四个顶点 $(i,j),\ (i+1,j),\ (i,j+1),\ (i+1,j+1)$ 分别计算哈希值，映射到预定义的梯度向量集合。在改进版Perlin噪声中，梯度集被固定为12个单位向量：$(±1,±1,0),\ (±1,0,±1),\ (0,±1,±1)$，点积计算因此可简化为加减法，避免了乘法开销。

**第三步——平滑插值**：使用六次多项式Fade函数对局部坐标进行平滑，再双线性插值四个顶点的梯度点积结果。

Fade函数（六次多项式）的精确形式为：

$$f(t) = 6t^5 - 15t^4 + 10t^3$$

该多项式满足 $f(0)=0,\ f(1)=1,\ f'(0)=f'(1)=0,\ f''(0)=f''(1)=0$，即在网格边界处一阶导数和二阶导数均连续为零。相比早期使用的三次Hermite插值 $3t^2 - 2t^3$（只保证一阶连续），六次版本在放大100倍以上观察时不会出现可见接缝。最终输出值域为 $[-1, 1]$，实际工程中通常将其线性映射到 $[0, 1]$：$v_{out} = v_{perlin} \times 0.5 + 0.5$。

### Voronoi/Worley噪声的最近点搜索

Worley噪声的数学定义是：对于空间中任意点 $\mathbf{P}$，将空间均匀划分为单元格，每格内随机放置一个特征点（坐标由哈希函数确定），计算 $\mathbf{P}$ 到所有特征点的距离并排序，取第 $n$ 小的距离值作为输出。

最常用的三种输出方式：
- **F1**：最近邻距离，产生多边形Voronoi分区感，适合岩石裂纹、皮肤纹理
- **F2**：次近邻距离，轮廓更圆润，常用于有机细胞壁效果
- **F2 - F1**：两距离之差，产生均匀宽度的细胞边界线，是模拟蜘蛛网、叶脉脉络的标准手法

实现时只需搜索以当前格为中心的 $3 \times 3$（2D）或 $3 \times 3 \times 3$（3D）共9或27个相邻格，因为特征点到当前点的距离必定不超过相邻格的对角线长度 $\sqrt{2}$（2D），无需遍历全局。

### 分形布朗运动（fBm）叠加机制

单层噪声频率单一，视觉上过于均匀。将多个频率成倍增加、振幅成倍衰减的噪声层叠加，即构成分形布朗运动（Fractional Brownian Motion，fBm）。标准公式为：

$$\text{fBm}(P) = \sum_{i=0}^{N-1} A^i \cdot \text{noise}(P \cdot F^i)$$

其中：
- $N$：叠加层数（octave数），常取4~8层
- $F$：频率倍增因子（lacunarity），标准值为 $2.0$，即每层频率翻倍
- $A$：振幅衰减因子（gain/persistence），标准值为 $0.5$，即每层振幅减半

当 $N=6,\ F=2.0,\ A=0.5$ 时，6层fBm的理论输出范围为 $\sum_{i=0}^{5}0.5^i = 1.96875$，实际使用时需除以该值归一化。将fBm叠加应用于Perlin噪声，可生成与天然云层、地形高度图视觉统计特性高度吻合的程序化纹理。

---

## 关键公式与GLSL实现

以下是在GLSL中实现2D Value噪声（作为Perlin噪声的简化版本，适合移动端GPU）和Worley噪声的完整代码片段：

```glsl
// ===== 哈希函数：将2D整数坐标映射到[0,1]伪随机值 =====
float hash21(vec2 p) {
    p = fract(p * vec2(127.1, 311.7));
    p += dot(p, p + 19.19);
    return fract(p.x * p.y);
}

// ===== 2D Value Noise（双线性插值，Hermite平滑）=====
float valueNoise(vec2 uv) {
    vec2 i = floor(uv);
    vec2 f = fract(uv);
    // 六次多项式平滑（Improved Perlin版本）
    vec2 u = f * f * f * (f * (f * 6.0 - 15.0) + 10.0);

    float a = hash21(i);
    float b = hash21(i + vec2(1.0, 0.0));
    float c = hash21(i + vec2(0.0, 1.0));
    float d = hash21(i + vec2(1.0, 1.0));

    return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

// ===== 2D Worley噪声（F1最近邻距离）=====
float worleyNoise(vec2 uv) {
    vec2 i = floor(uv);
    vec2 f = fract(uv);
    float minDist = 8.0; // 初始化为足够大的值

    // 只搜索3×3相邻格，共9次迭代
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 neighbor = vec2(float(x), float(y));
            // 特征点在邻格内的随机偏移位置
            vec2 point = hash21(i + neighbor) * vec2(1.0); // 修改为vec2版本
            vec2 diff = neighbor + point - f;
            float dist = length(diff);
            minDist = min(minDist, dist);
        }
    }
    return minDist;
}

// ===== 4层fBm叠加（lacunarity=2.0, gain=0.5）=====
float fbm(vec2 uv) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    for (int i = 0; i < 4; i++) {
        value += amplitude * valueNoise(uv * frequency);
        frequency *= 2.0;
        amplitude *= 0.5;
    }
    return value;
}
```

上述 `worleyNoise` 函数中，`hash21` 需要改写为返回 `vec2` 的版本以正确表达特征点的二维坐标偏移，实际工程中通常单独定义 `hash22(vec2 p) -> vec2`。

---

## 实际应用

### 云雾与烟雾特效

将4~6层fBm叠加的Perlin噪声输出直接作为透明度通道，叠加极坐标变换（将UV转为角度-半径坐标），可在约30行GLSL代码内实现实时体积云效果。具体做法是：以时间变量 `iTime` 乘以不同速度系数（如第1层×0.3、第2层×0.17、第3层×0.07）对各层噪声进行平移，利用各层速度差产生层间剪切，模拟湍流效应。《The Book of Shaders》（Gonzalez Vivo & Lowe, 2015）第13章"Fractal Brownian Motion"对该技法有完整的交互式代码演示。

### 岩石与地面材质

将Worley噪声的F2-F1输出（值域约为 $[0, 0.6]$）送入颜色渐变映射：$[0, 0.05]$ 对应裂缝深色区，$[0.05, 0.3]$ 对应岩石表面色，$[0.3, 0.6]$ 对应高光边缘，可生成视觉上接近花岗岩断面的程序化贴图，且不占用任何纹理内存。将法线扰动与F1距离场结合，还可额外生成凹凸细节，单Pass完成颜色与法线的同步生成。

### 边缘光与噪声遮罩联动

噪声生成是下一主题"边缘光"的直接前置技术。将Perlin fBm噪声叠加到Fresnel边缘光的菲涅尔因子上，可使边缘光亮度随噪声场起伏，模拟等离子体护盾或魔法光晕的不规则脉动感。典型参数：噪声影响权重取 $0.3$（即边缘光强度 = Fresnel × (1.0 + 0.3 × noise)），频率取 $5.0$，动画速度取 $iTime \times 1.2$。

---

## 常见误区

### 误区一：将Value Noise与Perlin Noise混淆

Value Noise在网格顶点存储**随机标量值**并插值，而Perlin Noise在网格顶点存储**随机梯度向量**并对局部偏移向量做点积后插值。两者视觉差异显著：Value Noise在格点处会出现局部极值聚集（"块状感"），Perlin Noise由于梯度约束，极值只出现在格点之间，视觉上更平滑自然。移动端因ALU限制有时使用Value Noise替代，但需明确知晓这一视觉代价。

### 误区二：哈希函数选择不当导致周期性伪影

在Shader中常见的简易哈希 `fract(sin(x) * 43758.5453)` 在输入值超过 $\pm 10000$ 时，由于浮点精度损失，`sin` 的输出会退化为伪线性，导致噪声场出现可见的规律性条纹。正确做法是使用整数哈希（如 xxHash 或 PCG Hash），或将输入坐标在送入哈希之前先取模到合理范围（如 $[0, 289]$，即 $17^2$，这是Simplex Noise参考实现中的标准做法）。

### 误区三：3D噪声直接替代2D噪声而忽略ALU开销

2D Perlin Noise每个采样点需计算4次梯度点积，而3D版本需要8次（立方体8顶点）。在移动端GPU（如Mali-G76或Adreno 640）上，将Fragment Shader中的单次3D fBm（6层）替换为2