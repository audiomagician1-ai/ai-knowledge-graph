---
id: "cg-shader-optimization"
concept: "着色器优化"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 3
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 着色器优化

## 概述

着色器优化是针对GPU着色器程序进行性能调优的系统性工程，核心目标是降低每帧着色器执行所消耗的GPU时钟周期数。与CPU程序优化不同，GPU的大规模并行架构使得着色器的瓶颈往往集中在ALU（算术逻辑单元）吞吐量、纹理采样带宽（TEX）以及寄存器占用率三个维度上，而非传统的缓存命中率或分支预测失败。

着色器优化的概念随可编程管线的普及而成熟。2001年NVIDIA推出GeForce3（NV20）引入可编程顶点着色器后，开发者很快发现朴素的着色器代码在复杂场景下会导致严重的GPU停顿。2007年前后，随着统一着色器架构（Unified Shader Architecture）在DirectX 10硬件上落地，ALU与TEX之间的平衡问题从"顶点着色器 vs. 像素着色器"的资源分配问题，演变为同一流处理器内ALU指令与纹理指令的调度竞争问题。

着色器优化直接影响游戏或实时渲染应用的帧率上限。一个未经优化的PBR材质着色器在移动端GPU上可能消耗超过200个ALU指令，而经过half精度替换和纹理采样合并后，可以压缩至80条以内，帧率提升幅度在中低端移动设备上可达40%以上。

## 核心原理

### ALU/TEX 平衡

现代GPU的着色器执行单元将ALU指令（加法、乘法、三角函数等）与纹理指令（`texture2D`、`textureCubeLod`等）分配在不同的执行管道中。当一个着色器的ALU指令数量与纹理采样数量严重失衡时，某一条管道会长时间空闲等待另一条，导致整体吞吐率下降。

**平衡策略**：若着色器ALU密集（如复杂光照计算），可将部分计算结果预烘焙到纹理中（Bake），用一次纹理采样替换多条ALU指令；反之，若纹理采样过多，可通过将多张贴图打包进单张RGBA纹理的不同通道（Channel Packing）来减少采样次数。例如，将金属度（Metallic）、粗糙度（Roughness）、AO三张单通道贴图合并为一张RGB贴图，可将3次纹理采样减少为1次。

PowerVR的Imagination Technologies曾公开数据：在其Rogue架构上，每个USC（Unified Shader Cluster）同时发射ALU与纹理指令时，理论吞吐量比单独执行任一类型指令高约30%，这直接量化了ALU/TEX平衡的价值。

### half 精度优化

`half`精度即16位浮点数（FP16），其数值范围约为±65504，精度约为小数点后3位有效数字。相对于`float`（32位FP32），`half`在支持FP16 MAD（Multiply-Add）的GPU上理论吞吐量翻倍，且寄存器占用减半，有助于提升着色器的occupancy（占用率）。

在GLSL/HLSL中，声明`half`变量需注意：在移动端GLSL ES中使用`mediump`限定符，桌面端HLSL中使用`min16float`或`half`。选择哪些变量降精度有明确规则：
- **适合降精度**：颜色值（0~1范围）、归一化方向向量、UV坐标（仅在没有大幅度纹理平铺时）、线性插值权重
- **不适合降精度**：世界空间坐标（大场景下精度损失会导致抖动，称为Catastrophic Cancellation）、深度值、粒子寿命计时器

Qualcomm Adreno 640的官方优化指南明确指出，将像素着色器中颜色运算从FP32改为FP16后，着色器吞吐率提升可达1.6×~2.0×，视具体指令组合而定。

### 分支优化策略

GPU着色器中的`if/else`分支在硬件层面的代价与CPU截然不同。由于GPU以Warp（NVIDIA）或Wavefront（AMD）为单位并行执行，一个Warp内通常包含32个线程（NVIDIA）或64个线程（AMD）。若同一Warp内的线程走向不同分支（Divergence，分支发散），GPU必须串行执行两个分支路径并用掩码屏蔽不活跃的线程，最坏情况下效率降至1/2（两路分支）或更低（多路分支）。

**三种分支优化手段**：

1. **静态分支（Compile-time Branch）**：使用`#ifdef`宏或着色器变体（Shader Variant）在编译阶段消除分支。Unity的Shader Keywords机制即基于此，为不同材质特性（是否启用法线贴图、是否透明等）生成独立的着色器编译产物，运行时无分支判断开销。

2. **Coherent分支（一致性分支）**：若分支条件由Uniform变量决定（如全局时间、灯光数量），整个Draw Call内所有像素走相同分支，GPU可以在Warp级别统一跳过，开销接近零。因此应尽量将随像素变化的条件（如`if(uv.x > 0.5)`）改写为随Draw Call统一的条件。

3. **算术替代分支**：将简单的`if/else`逻辑改写为`step()`、`mix()`、`saturate()`等无分支算术指令。例如：
   ```glsl
   // 有分支版本
   float result = (value > threshold) ? a : b;
   // 无分支算术版本
   float result = mix(b, a, step(threshold, value));
   ```
   后者在ALU密集型着色器中避免了分支发散，代价是始终计算`a`和`b`两个值，因此仅当`a`和`b`的计算开销低于分支发散代价时适用。

## 实际应用

**移动端PBR着色器精简**：标准PBR着色器通常包含GGX法线分布函数、Smith几何遮蔽和菲涅尔项，全精度实现约需150~200条ALU指令。移动端常见优化是将GGX替换为近似公式（如ARM的Mobile PBR采用`D_GGX`的近似展开），并将所有颜色和方向相关运算降至`mediump`，最终ALU指令数可降至70~90条。

**延迟渲染G-Buffer写入优化**：延迟渲染的GBuffer Pass中需要同时写入法线、漫反射颜色、金属度等数据。通过Channel Packing将法线的XY分量（Z可从XY重建）与漫反射颜色打包进两张RGBA8纹理，避免采样第三张贴图，TEX带宽占用降低约33%。

**粒子着色器的分支消除**：粒子系统中常见"粒子淡出"逻辑，原始写法为`if(age > lifetime * 0.9) alpha *= fade`。将其改为`alpha *= saturate((lifetime - age) / (lifetime * 0.1))`后，消除了每个粒子像素的分支，在粒子数量超过10万时帧率提升约8%（测试于Mali-G76）。

## 常见误区

**误区一：纹理采样数量越少越好**。实际上，在ALU密集型着色器中，增加一次纹理采样可能反而提高整体性能，因为TEX管道长时间空闲会浪费并行吞吐量。优化目标是ALU与TEX的平衡，而非单纯最小化任一类型的指令数。

**误区二：所有变量降为half精度都能提升性能**。在某些桌面GPU（如部分AMD RDNA1架构）上，FP16指令与FP32指令的吞吐量相同，降精度不带来速度提升，反而可能引入精度问题。使用half精度前应查阅目标硬件的架构文档，或通过GPU性能分析工具（如Snapdragon Profiler、Mali Offline Compiler）验证实际收益。

**误区三：用`mix()`替换所有`if/else`总是正确的**。当`mix()`的两个分支中任意一个包含昂贵运算（如纹理采样或复杂数学函数）时，算术替代分支会强制计算本可跳过的昂贵操作，反而比存在轻度分支发散的原始写法更慢。

## 知识关联

着色器优化建立在Uber Shader的架构基础上：Uber Shader通过`#ifdef`变体机制将大量运行时分支转移到编译阶段，这是静态分支优化的典型实现形态，理解Uber Shader的变体管理机制有助于掌握分支优化的编译期策略。

在渲染管线层面，着色器优化需与Draw Call批处理、Early-Z剔除协同考虑：即使着色器本身优化完善，若Early-Z未能正确剔除被遮挡像素，优化过的着色器仍然会对不可见像素执行计算，造成无效开销。着色器occupancy优化（通过降低寄存器使用数来允许更多Warp同时驻留）与GPU内存带宽优化（纹理压缩格式如ASTC的选择）共同构成GPU性能调优的完整链条。