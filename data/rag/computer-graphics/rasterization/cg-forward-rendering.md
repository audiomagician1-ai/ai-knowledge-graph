# 前向渲染

## 概述

前向渲染（Forward Rendering）是光栅化图形管线中最经典的光照计算方案，其基本原理是：对场景中每一个几何体的每一个片段（Fragment），在片段着色器阶段直接计算该片段受到的所有光源影响，将最终颜色写入帧缓冲。整个流程遵循"先几何变换，再逐片段着色"的顺序，光照计算与几何体绑定在一起同步完成。

前向渲染的历史可追溯至早期实时图形管线标准。OpenGL 1.x 时代（1992年前后）固定功能管线便采用此模式，彼时光源数量受硬件寄存器限制，通常最多支持 8 个固定光源（`GL_LIGHT0` 至 `GL_LIGHT7`）。1996年，id Software 发布的 Quake 引擎采用经典前向渲染架构处理静态光照，通过预烘焙光照贴图（Lightmap）来规避多光源性能瓶颈，这一思路至今仍被广泛沿用。可编程着色器随 DirectX 8.0（2000年）与 OpenGL 2.0（2004年）普及后，前向渲染的光源数量限制不再由硬件固定，而转移到着色器代码层面，但"光源数量越多，着色器越复杂或绘制调用越多"的根本矛盾依然存在。

前向渲染之所以在移动端和中低复杂度场景中仍是主流选择，原因在于其天然支持透明物体渲染、MSAA（多重采样抗锯齿）代价较低，且单个物体的光照计算局部性良好，缓存命中率高。Akenine-Möller 等人（2018）在《Real-Time Rendering》第四版中指出，前向渲染在光源数量不超过 5 个时，通常比延迟渲染具有更低的内存带宽开销，因为无需写入庞大的 G-Buffer。此外，前向渲染对硬件透明度混合（Alpha Blending）的原生支持使其在粒子系统、植被渲染、头发渲染等透明度密集场景中仍具不可替代的优势，这也是许多采用延迟渲染作为主路径的引擎（如 Unreal Engine 4/5）仍为透明物体保留独立前向渲染通道的根本原因。

## 核心原理

### 逐物体绘制与着色器执行模型

前向渲染的主循环结构是：对场景中 $N$ 个物体，每个物体执行一次或多次 Draw Call，片段着色器在每次执行时读取当前物体所受的光源列表并计算颜色。最简单的单次 Pass 前向渲染，其片段着色器伪代码形如：

```glsl
fragColor = ambient;
for (int i = 0; i < numLights; i++) {
    fragColor += calcLight(lights[i], normal, viewDir);
}
```

当场景有 $L$ 个光源、$N$ 个物体、平均每物体覆盖 $F$ 个片段时，总着色计算量可以表示为：

$$C_{\text{forward}} = O(N \times F \times L)$$

其中 $N$ 为场景中参与渲染的不透明网格总数，$F$ 为单个网格在屏幕空间覆盖的平均片段数，$L$ 为需要逐像素计算的动态光源数量。这一三重乘积是前向渲染性能瓶颈的直接根源。

例如，一个包含 200 个不透明网格、平均每网格覆盖 2000 个像素片段、场景中存在 10 个动态点光源的典型移动端关卡，每帧总着色调用量高达 $200 \times 2000 \times 10 = 4{,}000{,}000$ 次。这一数量级在中低端移动 GPU（如 Snapdragon 678 搭载的 Adreno 612）上往往会导致帧率跌破 30fps，而同场景在延迟渲染下因消除了 $N$ 维度，理论计算量结构完全不同。

### 多光源的两种实现策略

**多 Pass 前向渲染**：每个光源对每个物体单独执行一次绘制，使用加法混合（Additive Blending，`GL_ONE, GL_ONE`）叠加贡献。Unity 早期的 Forward Rendering Path（Unity 3.x 至 5.x 时代广泛使用）正是采用此策略：第一个光源为 Base Pass（同时写入深度缓冲），后续光源为 Additional Pass，总 Draw Call 数约为 $N + N \times (L-1) = N \times L$。当场景有 100 个物体、8 个像素光时，Draw Call 数可达 800 次，CPU 提交开销显著上升。在 Unity 5.6 的性能测试中，将像素光由 4 个增加至 8 个，在同等场景下 CPU 渲染线程耗时平均增加约 1.8 倍，直接体现了多 Pass 策略的线性扩展代价。

**单 Pass 前向渲染**：所有光源数据打包进 Uniform Buffer Object（UBO）或 Shader Storage Buffer Object（SSBO），着色器内用循环一次性处理所有光源。好处是 Draw Call 数保持为 $N$，但单次着色器执行时间更长，且光源数量通常被限制为编译期常量。例如，Unity URP 默认最多 8 个额外像素光，Unreal Engine 5 的 Mobile Forward Renderer 默认限制为 4 个动态光源，以保证着色器编译后代码量可控。

在 Unity URP 的 Forward Renderer 中，一个使用 Lit Shader 的材质在编译时会生成多个 Shader Variant，分别对应"0个额外像素光""1-4个额外像素光""5-8个额外像素光"等不同分支，运行时根据实际光源数量选择对应 Variant，避免了在极少光源情况下执行冗余循环迭代的开销。这种 Variant 策略是现代前向渲染引擎普遍采用的编译期优化手段。

**前向+ 渲染（Forward+）**：Forward+ 是 AMD 研究员 Takahiro Harada 等人于 2012 年提出的改进方案（Harada et al., 2012），通过 Tile-based Light Culling 将屏幕划分为 16×16 像素的 Tile，每个 Tile 通过 Compute Shader 预先计算影响该区域的光源列表，着色阶段仅遍历对应 Tile 的光源子集。这一方案将有效光源数从全局 $L$ 降低为局部 $L_{\text{tile}} \ll L$，典型场景下可支持数百个甚至上千个动态光源，同时保留前向渲染对透明物体和 MSAA 的原生支持。具体而言，Forward+ 的复杂度降为：

$$C_{\text{forward+}} = O\!\left(N \times F \times \bar{L}_{\text{tile}}\right)$$

其中 $\bar{L}_{\text{tile}}$ 为每个 Tile 的平均有效光源数，在灯光分布均匀的场景中通常仅为全局光源数 $L$ 的 5%–15%，性能提升十分可观。

### 深度缓冲与过度绘制问题

前向渲染严格依赖深度测试（Depth Test）来丢弃被遮挡片段，但在没有 Early-Z 优化的情况下，深度测试发生在片段着色器**之后**，导致被遮挡的片段仍会执行完整的光照着色器，产生无效的过度绘制（Overdraw）。设场景的平均 Overdraw 系数为 $K$，则实际着色量膨胀为：

$$C_{\text{overdraw}} = O(N \times F \times L \times K)$$

其中 $K$ 在典型城市场景中可达 2.5–4.0，在粒子特效密集场景中甚至超过 10。开启 Early-Z 需要提前进行深度预通道（Depth Pre-Pass）或保证不透明物体从前到后排序绘制（Front-to-Back Sorting）。以 Unreal Engine 4 的 Mobile Forward Renderer 为例，其默认开启基于 HiZ（Hierarchical-Z）的 Early-Z 测试，在城市场景测试中将平均 Overdraw 系数从 3.2 降低至 1.4，帧时间减少约 22%。

值得注意的是，Depth Pre-Pass 本身也有额外开销：它需要先以极简着色器（仅输出深度，不计算颜色）渲染一遍全部不透明几何体，消耗额外的顶点处理与光栅化时间。通常只有当 Overdraw 系数 $K > 2$ 时，Depth Pre-Pass 引入的顶点处理额外开销才能被 Early-Z 节省的着色器开销所覆盖。这一阈值判断是引擎渲染架构决策的重要依据之一。

思考一下：在同一个场景中，若将不透明物体的绘制顺序从"随机顺序"改为"严格从前到后排序"，理论上 Early-Z 的命中率应该显著提升——但实际工程中为何很多引擎并不对所有物体做精确的深度排序，而是退而求其次采用粗粒度的分桶排序（Bucket Sort by Depth Range）？这背后隐藏着 CPU 排序开销与 GPU Early-Z 收益之间怎样的权衡？精确排序需要对数百乃至数千个物体做完整的 CPU 端排序，在 1ms 帧预算极为紧张的移动端，这笔 CPU 开销是否真的值得？

## 关键公式与复杂度分析

前向渲染的核心性能模型涉及以下几个量化指标，掌握它们对于做出正确的渲染架构选型至关重要。

**基础着色复杂度**：$C_{\text{forward}} = O(N \times F \times L)$，其中每一维度都应独立分析优化空间：$N$ 可通过视锥体裁剪（Frustum Culling）和遮挡剔除（Occlusion Culling）压缩；$F$ 可通过 LOD 和 Depth Pre-Pass 管控；$L$ 可通过光源影响范围裁剪和 Forward+ 分 Tile 处理。

**带宽开销估算**：设屏幕分辨率为 $W \times H$，帧缓冲格式为 RGBA8（每像素 4 字节），深度缓冲为 D24S8（每像素 4 字节），则每帧最低帧缓冲读写带宽为：

$$B_{\text{min}} = 2 \times W \times H \times 8 \text{ 字节}$$

上式中因子 $2$ 来自颜色缓冲和深度缓冲各需一次完整的读写操作。以 1080p（$1920 \times 1080$）分辨率为例：

$$B_{\text{min}} = 2 \times 1920 \times 1080 \times 8 \approx 31.6 \text{ MB/帧}$$

在 60fps 下约为 1.9 GB/s，而中端移动 GPU（如 Adreno 660）的峰值内存带宽约为 42 GB/s，留有相对充足的余量；但若叠加多 Pass 光照导致帧缓冲被反复读写，带宽利用率将快速攀升至瓶颈区间。对于配备 TBDR 架构的 GPU（如 Apple A 系列、Imagination PowerVR），片上 Tile Memory 可将帧缓冲读写完全局限在片内 SRAM，实际外部带宽可降至理论最低值的 1/10 以下，这也是 Apple M 系列芯片能在极低功耗下维持高帧率的关键原因之一。

**延迟渲染对比**：延迟渲染（Deferred Rendering）将复杂度降为 $O(F \times L)$，但引入了 G-Buffer 写入带宽开销：

$$B_{\text{GBuffer}} = W \times H \times S_{\text{GBuffer}}$$

其中 $S_{\text{GBuffer}}$ 通常为 32–64 字节（3–4 张 RGBA16F 纹理），存储法线（16位×3通道）、漫反射颜色（8位×3通道）、金属度/粗糙度（8位×2通道）等 PBR 材质属性。当 $N \times F \times L$ 远大于 $F \times L + W \times H \times S_{\text{GBuffer}} / (W \times H)$ 时，延迟渲染才在总体带宽上占优。简化估算：在 1080p 下，使用 4 张 RGBA16F 纹理（每张 4MB）的 G-Buffer 每帧写入开销