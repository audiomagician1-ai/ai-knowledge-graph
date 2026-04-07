# 无缝贴图制作

## 概述

无缝贴图（Seamless Texture / Tileable Texture）是指将纹理在水平与垂直方向四方连续平铺时，边界处像素值满足周期性连续条件，观察者无法辨别单张贴图边界的纹理资产。其数学本质是图像 $f(x, y)$ 满足 $f(x + W, y) = f(x, y)$ 以及 $f(x, y + H) = f(x, y)$，其中 $W, H$ 分别为纹理的像素宽度与高度——即图像在空间频域中不存在非整数倍分辨率的低频泄漏分量。

这一需求的工程背景直接源自实时渲染的显存约束：1996年 id Software 发布的 Quake 使用大量 128×128 和 256×256 的可平铺纹理覆盖地形与墙面，以单张小尺寸贴图换取大面积表面覆盖，该范式沿用至今。随着 PBR（Physically Based Rendering）工作流在 2012—2013 年间因 Disney Principled BRDF 和 Substance 工具链普及，无缝要求从单张 Albedo 贴图扩展至 BaseColor、Metallic、Roughness、Normal、AO、Height 整套 Texture Set，每张贴图均须独立满足无缝条件，制作成本呈线性增长。

无缝贴图技术的演进可清晰划分为三代：第一代基于手工偏移修补（Offset & Clone Stamp），依赖美术师手动消除缝隙；第二代基于 Wang Tiles 与 Stochastic Tiling 算法，在运行时通过多子块查表或着色器随机化打散视觉重复；第三代基于深度学习纹理合成（如 Adobe Project Stager 及 NVIDIA Texture GAN 方案），实现端到端的无缝生成。本文重点覆盖前两代技术及其工程实现细节。

## 核心原理

### 偏移修补法：周期边界的手工实现

最基础的制作方法利用模运算将接缝从图像边界转移至中心。以一张 $1024 \times 1024$ 的纹理为例，对其施加 $(+512, +512)$ 像素偏移（即分辨率的 $\frac{1}{2}$）：

$$
f'(x, y) = f\left((x + \frac{W}{2}) \bmod W,\ (y + \frac{H}{2}) \bmod H\right)
$$

该运算将原始图像四个角的像素移至中心，同时将原边界缝隙暴露在图像正中央，便于使用仿制图章（Clone Stamp）或修复画笔（Healing Brush）进行局部修复。Photoshop 中的路径为 **Filter → Other → Offset**，勾选"Wrap Around"选项即实现上述模运算。

此方法对 Normal Map 存在严重的固有缺陷：仿制图章在 Normal Map 的切线空间向量上执行像素混合时，会产生非单位化的法线向量（$|\vec{n}| \neq 1$），导致渲染中出现异常高光斑块，因此修复 Normal Map 后必须重新归一化，或在 Substance Designer 中使用 **Normal Normalize** 节点进行后处理。

### Wang Tiles：组合数学的纹理应用

Wang Tiles 由数学家王浩（Hao Wang）于 1961 年提出，原始命题是：给定一组带有彩色边缘的方形砖块（每块四条边各附一色），能否按照"相邻砖块共享边颜色匹配"的规则铺满无限平面？王浩最初猜测所有 Wang Tile 集合都具有周期性铺法，但 Robert Berger 于 1966 年构造了非周期性 Wang Tile 集，证明该猜想不成立（Berger, 1966）。

游戏技术研究者 Michael Cohen、Jonathan Shade、John Snyder 与 Hugues Hoppe 于 2003 年在 SIGGRAPH 发表论文 *"Wang Tiles for Image and Texture Generation"*，将 Wang Tiles 引入纹理合成领域（Cohen et al., 2003）。其构造方式如下：

- 使用 2 种水平边色（标记为 $H_0, H_1$）与 2 种垂直边色（标记为 $V_0, V_1$），理论上需要 $2^4 = 16$ 张子块覆盖所有边色组合，但实际只需 **8 张**即可满足随机性要求（Lagae & Dutré, 2006）
- 每张子块的四条边带（edge strip，通常宽度为子块分辨率的 $\frac{1}{4}$）须与同色标记的标准过渡图案匹配，使得相邻子块拼接时像素值在边带宽度内平滑过渡
- 运行时，根据铺贴坐标 $(i, j)$ 通过预计算查表选取满足边色约束的子块索引，相邻格子的重复规律被有效打散

Ares Lagae 与 Philip Dutré 在 2006 年发表的 *"An Alternative for Wang Tiles: Colored Edges versus Colored Corners"* 进一步将最小 Wang Tile 集压缩至 8 张，并给出了 O(1) 时间复杂度的查表算法，显著降低了实时使用的性能开销（Lagae & Dutré, 2006）。

### Stochastic Tiling：着色器层面的随机化

Stochastic Tiling 的核心思路是在着色器内部，以哈希函数为每个铺贴单元生成独立的随机变换，使同一张无缝纹理的相邻平铺单元在旋转、偏移和色调上各不相同，从而消除大面积平铺时人眼敏感的重复网格状纹路。

Benedikt Bitterli 于 2019 年在其博客发布了完整的 GLSL/HLSL 实现（Bitterli, 2019），核心 UV 变换公式为：

$$
\mathbf{UV}_{\text{final}} = \mathbf{R}(\theta_c) \cdot \mathbf{UV}_{\text{local}} + \mathbf{t}_c
$$

其中：
- $\mathbf{UV}_{\text{local}}$ 为当前像素在所属铺贴格子内的局部坐标，通过 $\text{frac}(\mathbf{UV}_{\text{world}})$ 求得
- $c = \lfloor \mathbf{UV}_{\text{world}} \rfloor$ 为格子整数坐标
- $\mathbf{R}(\theta_c)$ 为由 $c$ 哈希生成的旋转矩阵，旋转角 $\theta_c$ 通常限定在 $\{0°, 90°, 180°, 270°\}$ 四个离散值以保持各向同性
- $\mathbf{t}_c$ 为随机平移偏移，使每格对应纹理的不同区域

由于旋转后格子边界处的 UV 不连续，Bitterli 方案在格子边界附近对多个相邻格子的采样结果进行**三线性混合**，混合权重由到边界的距离决定，确保视觉连续性。完整 HLSL 实现约 40 行代码，额外纹理采样次数为 3 次（对比普通采样的 1 次），性能开销可接受。

Jorge Jimenez 在 Activision 发表的 *"Practical Stochastic Tiling"*（2016）以及 Epic Games 在 UE4.26 中内置的 **Stochastic Sample** 材质节点，均采用了此类方案的变体，其中 Epic 的实现额外引入了色调方差（Hue Variation）参数，允许美术师在材质编辑器内直接调节每格随机色调偏移量 $\Delta H \in [0°, 360°]$。

## 关键方法与公式

### Substance Designer 中的自动无缝节点图

在 Substance Designer 工作流中，**Tile Sampler** 与 **Non Uniform Blur** 节点组合是最常见的程序化无缝贴图方案：Tile Sampler 提供随机散布的实例，Non Uniform Blur 使用 Mask 控制边界过渡，最终通过 **Slope Blur** 节点在边界区域实现基于法线方向的各向异性模糊，消除周期性边界硬边。

法线贴图的无缝处理需要额外注意：经过偏移修补或 Tile 拼接后，Normal Map 在边界处须满足：

$$
\vec{n}_{\text{left-edge}}(y) = \vec{n}_{\text{right-edge}}(y), \quad \forall y \in [0, H]
$$

在 Substance Designer 中，**Make It Tile Patch** 节点专门处理此类连续性问题，其内部使用了基于泊松方程的梯度域融合（Gradient Domain Fusion），比简单 Clone Stamp 保留更多高频法线细节。

### 频域分析：为何不能直接复制边缘

若直接将纹理左右两侧各 $k$ 像素的边带互相覆盖以"强制连续"，会在边带宽度处产生高频不连续（阶跃函数），在频域中表现为宽频谱的吉布斯（Gibbs）振铃现象，渲染时在边界附近产生明暗条纹。正确做法是在边带内做加权混合：

$$
f_{\text{blend}}(x) = w(x) \cdot f(x) + (1 - w(x)) \cdot f(x + W)
$$

其中权重函数 $w(x) = \frac{1}{2}\left(1 - \cos\left(\frac{\pi x}{k}\right)\right)$（余弦插值），保证一阶导数在边带两端连续，避免吉布斯效应。

## 实际应用

### 案例：UE5 地形中的 Stochastic Tiling 配置

在 Unreal Engine 5 的 Landscape Material 中，启用 Stochastic Tiling 的标准流程为：在 Material 编辑器中调用 **StochasticTextureSample** 节点（材质函数库路径：`/Engine/Functions/Engine_MaterialFunctions02/Texturing/StochasticTextureSample`），传入原始无缝纹理和 UV 坐标，调节 **Variation Scale**（建议初始值 1.0，即每格 $1m \times 1m$）和 **Hue Variation**（建议 $\pm 5\%$ 以内避免色差突兀）。与普通 Texture Sample 相比，该节点在 GBuffer 填充阶段额外增加约 3 次纹理采样，在 RTX 3080 上对 $4096 \times 4096$ 的地形渲染影响约 0.3ms，性能代价极低。

例如：对一张 $2048 \times 2048$ 的岩石地面纹理使用普通平铺时，在 $100m \times 100m$ 的地形上以 UV Scale = 0.1 平铺，每 10m 可见一次重复，形成明显的"格子感"；切换至 Stochastic Tiling 后，相同贴图下重复规律消失，视觉复杂度接近使用 4 张不同纹理混合的效果。

### 案例：Photoshop 工作流的 Normal Map 无缝处理

对一张从 Megascans 下载的非无缝扫描纹理进行 Normal Map 无缝化时，推荐流程为：① 在 Photoshop 中对 Normal Map 施加 $(+512, +512)$ 偏移；② 将 RGB 通道拆分，分别对 R、G、B 通道独立修复接缝（禁止跨通道混合修复）；③ 修复完成后对全图执行 **Normalize** 处理（可使用 Photoshop 的 3D Normal Map Filter 或导入 Marmoset Toolbag 中通过 Bake → Normalize Normals 完成）；④ 导入引擎前用 Compressonator 验证 BC5 压缩后法线方向偏差不超过 $1°$。

## 常见误区

**误区一：将偏移修补法应用于 Height Map 后不重新烘焙 Normal Map**
Height Map 修复后，从 Height Map 推导出的 Normal Map 与直接修复的 Normal Map 会在修复区域产生 $5°\sim15°$ 的法线方向不一致，导致视差遮蔽贴图（Parallax Occlusion Mapping）在缝隙处出现高度跳变。正确做法是先完成 Height Map 无缝修复，再通过 **Gradient** 节点重新从 Height Map 生成 Normal Map，而非独立修复两张贴图。

**误区二：认为 Stochastic Tiling 可以替代无缝贴图的制作**
Stochastic Tiling 要求输入贴图本身必须是无缝的；若对非无缝贴图使用 Stochastic Tiling，格子旋转后边界