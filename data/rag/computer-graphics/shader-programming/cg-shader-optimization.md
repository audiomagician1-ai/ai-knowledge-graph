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
quality_tier: "B"
quality_score: 47.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.4
last_scored: "2026-03-22"
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

着色器优化是指通过调整GPU指令的类型分布、数据精度选择和控制流结构，使着色器程序在目标GPU架构上以最短时钟周期完成计算的工程实践。与CPU优化不同，GPU着色器优化的核心矛盾是**线程级并行性**与**资源占用率**之间的权衡——一个着色器如果寄存器使用量过多，会导致SM（Streaming Multiprocessor）上能同时驻留的warp数量减少，从而降低延迟掩盖能力，最终导致性能下降。

着色器优化随可编程图形管线的普及而出现。2001年NVIDIA GeForce 3引入可编程顶点着色器后，开发者首次需要手动权衡指令数量与GPU吞吐量。2004年前后，随着统一着色器架构（Unified Shader Architecture）逐渐成为主流，ALU与纹理采样单元的分配比例问题开始被系统讨论。移动GPU时代（2010年后），由于Adreno、Mali、PowerVR等架构的特殊Tiling机制，着色器优化的策略与桌面端出现了显著分歧，half精度优化的重要性也大幅提升。

着色器优化直接决定片元级渲染的帧率天花板。在现代游戏中，像素着色器往往是GPU的首要瓶颈，一个未经优化的PBR材质着色器可能消耗超过300条ALU指令，而经过精度降级和ALU/TEX重新平衡后可压缩至150条以内，帧率提升可达40%以上。

---

## 核心原理

### ALU/TEX 平衡

GPU内部存在两类主要计算资源：算术逻辑单元（ALU）负责浮点运算，纹理单元（TEX/TMU）负责纹理采样与滤波。这两类资源在硬件上**并行运作但相互独立**，若着色器完全依赖ALU运算而纹理单元空闲，则TEX吞吐量被浪费；反之亦然。

衡量着色器是否ALU/TEX平衡，通常使用GPU分析工具（如RenderDoc、Arm Mobile Studio）查看`ALU Active Cycles`与`TEX Active Cycles`的比值。以Mali-G710为例，其ALU与TEX的理论吞吐比约为 **4:1**，即每次纹理采样期间GPU可执行约4条ALU指令。若某着色器TEX占用率90%而ALU占用率仅20%，说明该着色器是TEX瓶颈，此时优化方向是：
- 将部分可用数学计算（如法线解码、颜色空间转换）移至纹理采样等待期间交错执行
- 通过纹理压缩格式（如ASTC 4x4）减少纹理带宽以降低TEX压力
- 将查找表（LUT）中的数据改用数学公式近似拟合，直接减少采样次数

反之，若ALU是瓶颈，可将部分高频运算结果预烘焙到纹理中，以TEX换ALU。

### Half 精度优化

`half`（fp16，16位浮点数）与`float`（fp32，32位浮点数）是着色器中最常见的两种数值精度。在支持fp16的GPU上（几乎所有移动GPU以及现代桌面GPU的部分管线），fp16的ALU吞吐量是fp32的**2倍**，因为同一SIMD通道可以同时处理两条fp16运算。GLSL中使用`mediump`声明、HLSL中使用`min16float`或直接在SPIR-V/MSL层面指定fp16。

Half精度的精度范围约为 $\pm 65504$，最小正规数约为 $6.1 \times 10^{-5}$，有效十进制位数约为3.3位。这意味着以下计算必须保留fp32：
- 世界坐标变换（坐标值可能超过65504）
- 深度值计算（精度不足会产生Z-fighting）
- 累积求和（多次fp16加法会导致误差放大）

适合降级为fp16的计算包括：颜色值（通常在0~1范围内）、法线向量（归一化后范围为[-1,1]）、UV坐标（通常0~1）、光照衰减系数。实践中，一个完整的移动端PBR着色器将颜色和法线计算全部切换为`mediump`后，ALU周期通常可减少**25%~35%**。

### 分支优化策略

GPU通过SIMT（Single Instruction Multiple Threads）架构执行着色器，一个warp内的所有线程必须执行相同指令路径。当着色器中出现`if-else`分支且warp内线程出现分歧（divergence）时，GPU必须串行执行两个分支并用掩码屏蔽无效线程，这称为**warp divergence**，最坏情况下会将有效执行效率降低至50%（双分支）甚至更低（多分支）。

优化分支的核心策略有三类：

**1. 使用数学替代条件分支（Math-for-branch）**
```hlsl
// 低效：产生分支
float result = (x > 0.5) ? a : b;
// 优化：step()函数无分支
float result = lerp(b, a, step(0.5, x));
```
`step()`和`lerp()`在GPU上编译为`cmp`+`mad`等条件移动指令，不产生实际跳转。

**2. 利用Uniform分支**
若分支条件来自Constant Buffer（在同一Draw Call内所有线程值相同），GPU驱动通常会将其识别为**Uniform Branch**并进行整个warp级别的预测，不产生divergence。因此，材质开关（是否启用法线贴图、是否启用自发光）应优先通过Constant Buffer传入，而非纹理通道传入。

**3. 早期退出（Early Exit）策略**
对于透明度测试（Alpha Test）场景，在片元着色器开头执行`clip()`或`discard`可提前终止大量像素的后续计算。在Arm Mali架构上，Early-Z和FPK（Forward Pixel Kill）机制要求`discard`必须出现在所有纹理采样和ALU计算之前才能触发硬件级别的像素剔除加速。

---

## 实际应用

**移动端PBR材质优化案例**：一个基于UE4的移动端PBR材质着色器，原始版本包含242条ALU指令和18次纹理采样，在Adreno 650上渲染1080p场景帧率为38fps。经过以下三步优化后帧率提升至54fps：
1. 将所有颜色计算从`float`降级为`half`（`mediump`），ALU指令减少至178条
2. 将Roughness/Metallic/AO三个独立纹理合并为一张RGB纹理（Texture Channel Packing），纹理采样从18次降至14次
3. 将`if(isEmissive)`分支改为Uniform分支，消除warp divergence

**Uber Shader的分支精简**：从Uber Shader分离出特化着色器时，应优先移除不可能触发的分支路径，而不是简单删除`#define`。编译器有时无法完全消除dead code中的寄存器占用，手动删除代码路径可将寄存器压力从52个降至38个，使warp occupancy从50%提升至75%。

---

## 常见误区

**误区1：所有变量都换成half就能提升性能**
fp16优化的前提是GPU管线确实支持native fp16运算。在某些桌面GPU（如旧版NVIDIA Kepler架构）上，fp16运算实际上被编译器自动提升为fp32执行，使用`half`不会带来任何速度收益，反而增加代码维护成本。验证方式是通过GPU厂商的着色器分析工具（如NVIDIA Nsight的Shader Instruction Stats）确认fp16指令是否真正出现在编译后的ISA中。

**误区2：避免所有分支就是最优策略**
用`lerp(a, b, step(...))`替代`if-else`并非总是正确。当两个分支都涉及高代价操作（如多次纹理采样）时，数学替换会强制GPU计算两侧结果再丢弃其中之一，总成本反而高于接受warp divergence。当分歧率较低（如一个warp内超过75%的线程走同一路径）时，保留原始分支更高效。

**误区3：TEX指令数等于性能代价**
纹理采样的实际性能代价高度依赖缓存命中率。同样是8次纹理采样，如果访问模式具有良好的空间局部性（相邻像素采样相近UV），则L1/L2缓存命中率可达90%以上，实际带宽消耗极低；若UV跳跃幅度大（如环境贴图的随机反射方向），则每次采样都可能穿透缓存直接访问显存，带宽消耗远高于ALU等价操作。

---

## 知识关联

着色器优化建立在**Uber Shader**的设计基础上。Uber Shader通过宏定义和分支整合了大量功能路径，是着色器优化的主要对象——优化工作往往始于分析Uber Shader生成的着色器变体，识别哪些分支产生了divergence，哪些精度可以安全降级。理解Uber Shader的变体编译机制是正确实施Uniform Branch优化的前提：只有在Constant Buffer驱动的分支（而非per-vertex/per-pixel的动态分支）中，Uniform Branch优化才能生效。

从优化方向延伸，掌握着色器优化后，自然进入GPU架构级的性能调