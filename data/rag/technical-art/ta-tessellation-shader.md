# 曲面细分着色器

## 概述

曲面细分着色器（Tessellation Shader）是DirectX 11（2009年发布）与OpenGL 4.0（2010年发布）正式纳入可编程渲染管线的几何细分阶段，其设计目标是以低面数输入网格为基础，在GPU端动态生成高密度三角形，从而在不增加磁盘或内存带宽负担的前提下实现精细的运行时几何细节。AMD与NVIDIA于同期分别以Cypress（HD 5870）和Fermi（GTX 480）架构首批完整实现了该硬件阶段，使曲面细分真正进入游戏实时渲染的工程实践范畴（Uralsky, 2011）。

曲面细分管线由三个连续单元构成：**Hull Shader（壳着色器，HLSL）/ Tessellation Control Shader（TCS，GLSL）**、固定功能**Tessellator（细分器）**硬件单元，以及**Domain Shader（域着色器，HLSL）/ Tessellation Evaluation Shader（TES，GLSL）**。这三者在渲染管线中位于顶点着色器之后、几何着色器之前，任何一个阶段缺失均会导致整条曲面细分管线失效。其核心工程价值在于**位移贴图（Displacement Mapping）**：通过在 Domain Shader 中对高度图进行采样，将灰度值转化为沿法线方向的顶点偏移量，使低面数地形、岩石、角色皮肤等表面呈现出视差遮挡贴图（Parallax Occlusion Mapping）无法实现的真实轮廓剪影（silhouette）。

---

## 核心原理

### Hull Shader 的双重输出结构

Hull Shader 每次调用处理一个**Patch（图元块）**，其 `[outputcontrolpoints]` 属性决定输出控制点数量（三角形 Patch 通常为 3，四边形 Patch 为 4，B 样条曲面最多支持 32 个控制点）。Hull Shader 的输出分为两个独立部分：

**① 逐控制点输出（Per-Control-Point Output）**：以 `[outputcontrolpoints(3)]` 声明的函数对每个输入控制点进行处理，通常执行世界空间变换或切线空间计算，结果直接传递给 Domain Shader。  
**② Patch 常量输出（Patch-Constant Output）**：通过 `[patchconstantfunc("PatchHS")]` 属性标记的独立函数计算**细分因子（Tessellation Factor）**，其中包含：

- `SV_TessFactor`：三角形三条边各自的细分段数（三元素浮点数组），控制边缘密度。
- `SV_InsideTessFactor`：三角形内部的径向细分密度（单浮点值）。

当任意一条边的 `SV_TessFactor` 被设置为 0.0 时，该 Patch 在 Tessellator 阶段即被完全剔除，不产生任何输出顶点——这是曲面细分管线实现视锥体剔除与背面剔除的主要手段，可将背对摄像机或超出视锥的 Patch 开销降为零。

Hull Shader 中通过 `[partitioning]` 属性指定细分的离散化模式，共三种：  
- `integer`：细分因子向上取整为整数，LOD 切换时出现跳变。  
- `fractional_odd`：在最近奇数之间平滑插值，LOD 过渡平滑，适合地形。  
- `fractional_even`：在最近偶数之间平滑插值，行为略有差异。  
工程实践中 `fractional_odd` 是地形和角色细分的常用选项，因为它能消除 LOD 切换时"顶点突然冒出"的视觉抖动现象（Tatarchuk et al., 2010）。

### 固定功能 Tessellator 的参数空间细分

固定功能 Tessellator 不可编程，它接收 Hull Shader 的细分因子，在**参数空间（Parametric Space / UV Domain）**内生成新顶点的无量纲坐标。对于三角形 Patch，使用**重心坐标（Barycentric Coordinates）**表示，每个新顶点满足：

$$u + v + w = 1, \quad u,v,w \in [0,1]$$

对于四边形 Patch，则直接使用 $(u, v) \in [0,1]^2$ 的均匀或分数细分网格。DirectX 11 规定细分因子的有效范围为 **1.0 到 64.0 的浮点数**，超出此范围的值会被硬件夹紧（clamp）处理。硬件在相同细分因子下保证生成拓扑确定的三角形网格，因此两个相邻 Patch 如果在共享边上使用相同的 `SV_TessFactor`，其边缘顶点位置完全吻合，不会产生裂缝（cracking）。

### Domain Shader 的顶点还原与位移

Domain Shader 每个调用对应 Tessellator 输出的**一个新顶点**，输入参数包含：

1. 该顶点的参数坐标（重心坐标 `(u,v,w)` 或 UV 坐标 `(u,v)`）
2. Hull Shader 输出的全部控制点数据
3. Patch 常量数据

Domain Shader 利用这些信息通过**插值**重建世界空间位置，经典的三角形线性插值公式为：

$$\mathbf{P}_{world} = u \cdot \mathbf{CP}_0 + v \cdot \mathbf{CP}_1 + w \cdot \mathbf{CP}_2$$

若使用 **Phong 细分（Phong Tessellation）** 而非平面插值，则每个控制点还需额外提供法线，最终顶点位置为线性插值结果向法线平面的投影混合：

$$\mathbf{P}_{phong} = \alpha \cdot \mathbf{P}_{linear} + (1-\alpha) \cdot \mathbf{P}_{projected}$$

其中 $\alpha$ 是平滑强度参数（通常取 0.75），$\mathbf{P}_{projected}$ 是将线性插值点投影到每个控制点切平面后再插值的结果。Phong 细分无需贝塞尔曲面的复杂控制网格，却能以极低的额外计算量使低面数模型呈现出圆滑的有机轮廓（Boubekeur & Schlick, 2008）。

**位移贴图**是 Domain Shader 最常见的应用场景。在插值得到世界空间位置后，额外采样一张 R8 或 R16 精度的高度图，将采样值乘以位移强度系数后沿插值法线偏移顶点：

$$\mathbf{P}_{displaced} = \mathbf{P}_{world} + \mathbf{N}_{interp} \cdot h(uv) \cdot d_{scale}$$

其中 $h(uv)$ 为高度图在当前 UV 坐标的采样值（归一化到 $[0,1]$），$d_{scale}$ 为世界空间位移量级（单位：米）。注意 Domain Shader 中的纹理采样必须使用带显式 LOD 的采样函数（HLSL 中的 `SampleLevel`），因为 GPU 无法在该阶段自动计算 mip 梯度。

---

## 关键方法与公式

### 基于屏幕空间的自适应细分因子计算

为使细分因子与视觉效果挂钩而非仅与距离挂钩，工业界常用**边缘屏幕投影长度**驱动细分因子：

$$TF_{edge} = \frac{L_{screen}}{target\_pixels\_per\_edge}$$

具体实现：将边缘两端点分别变换到裁剪空间，计算 NDC 下的屏幕像素距离 $L_{screen}$，除以目标像素密度（例如每段 20 像素），得到该边所需细分段数。该方法保证近处大三角形高度细分、远处小三角形少量细分，在保持视觉均匀性的同时将 GPU 开销控制在最优（Lorach, 2010）。

**视锥体剔除**在 Hull Shader 的 Patch 常量函数中实现：将 Patch 的 AABB 与摄像机视锥体做相交测试，若完全在视锥外则将所有 `SV_TessFactor` 设为 0，从而零成本丢弃该 Patch。

### PN 三角形（Point-Normal Triangles）

PN 三角形（Vlachos et al., 2001）是曲面细分历史上最早的实用方案之一，在 Hull Shader 阶段利用三个顶点的位置和法线构造一个**三次贝塞尔三角形**（Cubic Bézier Triangle），共 10 个控制点：

$$\mathbf{P}(u,v,w) = \sum_{i+j+k=3} \frac{3!}{i!j!k!} u^i v^j w^k \mathbf{b}_{ijk}$$

其中 $\mathbf{b}_{ijk}$ 为贝塞尔控制点，由三个顶点的位置和法线按几何约束条件解析计算。PN 三角形的优点是仅需原始网格的顶点法线即可生成曲面，无需美术修改拓扑；缺点是曲率控制有限，锐利折角处需要通过 crease weight 参数约束。

---

## 实际应用

### 地形与岩石位移

**案例：UE4 地形曲面细分**  
Unreal Engine 4 在其地形系统中集成了曲面细分位移管线（Unreal Engine Docs, 2014）：美术人员在材质编辑器中将高度图连接至 `World Displacement` 和 `World Tessellation Multiplier` 引脚，引擎自动生成 Hull/Domain Shader。地形 Patch 尺寸通常为 2m×2m，基础网格精度较低（约每 Patch 4 个三角形），在摄像机 5m 以内细分因子可达 32，每 Patch 生成约 1024 个三角形，位移幅度 0 至 50cm，使地形石块呈现真实的凹凸轮廓而非依赖法线贴图模拟。

### 角色皮肤与有机表面

《刺客信条：大革命》（Ubisoft Montreal, 2014）在角色面部使用了 Phong 细分配合曲率图位移，将 5000 面的基础头部网格在近景下细分至约 80000 面，同时通过曲率图控制皮肤褶皱区域的位移量，使面部表情动画的几何细节达到接近影视级别的效果，而中景与远景则回退至低细分因子以节省 GPU 开销。

### 海洋波浪模拟

基于 FFT 的海洋着色器（Tessendorf, 2001）中，曲面细分用于动态调节水面网格密度：摄像机视线方向的水面 Patch 接受最高细分因子（64），水平线附近的 Patch 细分因子降至 4，配合 Domain Shader 中采样 FFT 高度图的位移，实现从近景米级波浪细节到远景大幅波形的无缝过渡。

---

## 常见误区

**误区 1：将 Domain Shader 等同于顶点着色器**  
Domain Shader 确实负责最终的顶点变换（MVP 矩阵乘法在此处执行），但它的输入不是原始网格的顶点，而是 Tessellator 在参数空间中生成的浮点坐标。忽略这一点导致开发者将顶点着色器的逻辑直接复制到 Domain Shader，遗漏控制点插值步骤，最终产生所有新顶点堆叠在原点的错误。

**误区 2：认为细分因子越高性能开销线性增长**  
三角形曲面细分的顶点数随细分因子 $n$ 的增长约为 $O(n^2)$，面数增长同样为 $O(n^2)$。将细分因子从 8 提升至 16 并非开销翻倍，而是约四倍。这意味着细分因子超过 32 后每个 Patch 产生超过 1024 个三角形，若 Patch 在屏幕上仅占数十像素，大量三角形将小于单像素，造成严重过绘制。

**误区 3：认为 Hull Shader 和 Domain Shader 可以独立使用**  
在 DirectX 11 下，三个曲面细分阶段必须同时启用或同时禁用。若只绑定 Hull Shader 而不绑定 Domain Shader（或反之），管线验证会失败并产生运行时错误。

**误区 4：忽略相邻 Patch 的接缝（Cracking）问题**  
当两个相