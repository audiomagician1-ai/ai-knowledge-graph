---
id: "ta-shader-optimization"
concept: "Shader性能优化"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 3
is_milestone: false
tags: ["优化"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# Shader性能优化

## 概述

Shader性能优化是针对GPU渲染管线中着色器程序执行效率的系统性分析与改进工作，核心目标是将每帧的GPU时间消耗控制在目标帧预算以内。移动端60fps对应16.67ms帧预算，其中Shader执行时间通常不应超过6ms；主机端30fps对应33.33ms帧预算，高质量光照Shader通常被允许占用10~12ms。性能瓶颈分为三类：ALU（算术逻辑单元）计算瓶颈、纹理采样瓶颈以及内存带宽瓶颈，三类瓶颈的成因完全不同，需要用不同工具识别、用不同策略修复。盲目删减ALU指令而忽视带宽压力，往往收效甚微甚至引入新问题。

这一领域随GPU架构演进而持续发展。2001年NVIDIA GeForce3引入可编程着色器后，开发者开始关注ALU指令计数。2006年前后统一着色器架构（Unified Shader Architecture）普及，ALU资源分配更加灵活。进入移动GPU时代，Arm Mali-G系列、Qualcomm Adreno 6xx/7xx以及Apple GPU均采用Tile-Based Deferred Rendering（TBDR）架构，该架构将屏幕划分为16×16或32×32像素的Tile分块处理，对帧缓冲带宽极度敏感，使得移动端优化策略与桌面端存在根本差异。

参考文献：《GPU Gems 3》(Nguyen, 2007, NVIDIA/Addison-Wesley) 第14章系统论述了针对不同GPU架构的Shader优化方法论，是本领域的经典参考资料。

---

## 核心原理

### ALU瓶颈识别与优化

ALU瓶颈表现为GPU着色器核心（Shader Core）持续满载，纹理单元（TMU）和内存控制器相对空闲。使用RenderDoc可查看Pipeline Statistics中的Shader Invocations与执行耗时；Arm Mobile Studio（前身为DS-5 Streamline）可读取Mali GPU的`EXEC_CORE_ACTIVE`硬件计数器，若其值超过总周期数的85%，则确认为ALU瓶颈。Snapdragon Profiler中对应指标为`SP ALU Busy`，阈值同样参考80%~90%。

**精度降级（Precision Downgrade）** 是移动端最高收益的ALU优化手段。在Mali GPU上，`mediump`（对应GLSL half，16位浮点）的ALU吞吐量是`highp`（32位浮点）的2倍，寄存器占用也减少一半，进而降低寄存器溢出（Register Spilling）概率。以下是正确的精度分配原则：

```glsl
// 必须保持 highp 的数据类型
highp vec3 worldPos;       // 世界空间坐标，精度不足会导致顶点抖动
highp float depth;         // 深度值，精度损失引起Z-fighting

// 可安全使用 mediump 的数据类型
mediump vec3 normalWS;     // 法线方向，归一化后分量在[-1,1]之间
mediump vec4 albedo;       // 颜色值，人眼对颜色精度不敏感
mediump float roughness;   // PBR材质参数，范围[0,1]
```

**预计算烘焙到LUT（Look-Up Texture）** 可用一次纹理采样替换多条三角函数指令。以GGX法线分布函数（NDF）为例：

$$D_{GGX}(h) = \frac{\alpha^2}{\pi\left[(\alpha^2 - 1)\cos^2\theta_h + 1\right]^2}$$

该函数每次求值需要2次乘法、1次加法、1次平方、1次除法，在高roughness参数下逐像素执行代价可观。Epic Games在《虚幻引擎4》的移动端渲染器中，将Split-Sum近似中的环境BRDF积分预烘焙为一张128×128的RG16F贴图，在运行时用`(NdotV, roughness)`两个维度进行双线性采样，将原本约12条ALU指令压缩为1次纹理采样（参见 Karis, 2013, "Real Shading in Unreal Engine 4"）。

**避免动态分支（Dynamic Branch）** 对ALU性能至关重要。GPU以Wave（NVIDIA称Warp，32线程；AMD称Wavefront，64线程）为单位调度执行。当Wave内部分线程走if分支、另一部分走else分支时，GPU必须串行执行两个分支，有效吞吐量减半，这称为Wave Divergence。对于条件概率接近50%的分支，应改用无分支等价写法：

```hlsl
// 有分支写法（可能导致Wave Divergence）
float result;
if (roughness > 0.5)
    result = expensivePathA(roughness);
else
    result = expensivePathB(roughness);

// 无分支等价写法（lerp在GPU上编译为单条MAD指令）
float a = expensivePathA(roughness);
float b = expensivePathB(roughness);
float result = lerp(b, a, step(0.5, roughness));
```

注意：当两个分支计算量差异极大（如一支仅为`return 0`），保留分支反而更快，因为大量线程可跳过高代价分支。

### 纹理采样瓶颈识别与优化

纹理瓶颈（Texture Bound）表现为纹理单元（TMU）利用率超过80%，而ALU利用率偏低。在Mali GPU上对应硬件计数器`TEX_COORD_ISSUE`持续饱和；在Adreno GPU上，Snapdragon Profiler中`TP Busy`指标超过85%可确认纹理瓶颈。

**纹理压缩格式选择** 直接影响带宽消耗。未压缩RGBA8纹理每像素4字节，而：

- **ETC2 RGB**：每像素0.5字节，压缩比8:1，OpenGL ES 3.0强制支持，适合Android中低端设备
- **ASTC 4×4**：每像素1字节，压缩比8:1，质量优于ETC2，支持HDR和法线图，需OpenGL ES 3.2或Vulkan
- **ASTC 8×8**：每像素0.25字节，压缩比16:1，适合低频颜色区域（如天空盒、远景地形）
- **BC7（PC/主机）**：每像素1字节，压缩比4:1，质量接近无损，DirectX 11+支持

正确选择压缩格式可将纹理带宽降低60%~80%，是移动端最重要的带宽优化手段之一。

**强制开启Mipmap** 可大幅提升L1/L2 Cache命中率。未启用Mipmap时，远处物体的片元采样原始分辨率纹理，相邻像素的采样坐标跨度可能达到256+个纹素，导致Cache命中率趋近于0。启用Mipmap后，远处物体自动采样低级别Mip，相邻像素的采样坐标聚集在小范围内，L1命中率可从不足10%提升至70%以上。在Unity中，Import Settings将Mip Maps设为Enabled，并勾选Streaming Mipmaps（Unity 2018.2引入）可进一步控制内存占用。

**减少采样次数与贴图合并（Texture Packing）** 是常见优化。将4张单通道灰度图（Roughness、Metallic、AO、Height）合并打包为1张RGBA贴图的4个通道，可将4次采样合并为1次，减少75%的采样开销。Unity的Lit Shader即采用此策略，将Metallic存入A通道，Smoothness存入R通道（参见Unity官方文档，2021）。

### 内存带宽瓶颈识别与优化

带宽瓶颈（Bandwidth Bound）在移动端TBDR架构下尤为突出。当Tile内的像素处理完毕后，结果写回主存（Resolve操作）；若下一Pass又读取该结果（如后处理读取颜色缓冲），则触发额外的主存读写，代价极高。Mali-G77的主存带宽约为51.2 GB/s（LPDDR5），而On-Chip Tile Buffer带宽可达数TB/s级别，二者相差约100倍。

**避免不必要的Framebuffer Load/Store** 是TBDR优化核心。在Vulkan和Metal中，Render Pass的`loadOp`和`storeOp`直接控制Tile Buffer与主存的数据交换：

```c
// Vulkan Render Pass Attachment 配置示例
VkAttachmentDescription colorAttachment = {};
colorAttachment.loadOp  = VK_ATTACHMENT_LOAD_OP_CLEAR;    // 不从主存加载，直接清除
colorAttachment.storeOp = VK_ATTACHMENT_STORE_OP_STORE;   // 最终结果写回主存

// Depth Buffer 通常不需要保留到主存
depthAttachment.storeOp = VK_ATTACHMENT_STORE_OP_DONT_CARE; // 节省带宽
```

将Depth Buffer的`storeOp`设为`DONT_CARE`，可在1080p分辨率下节省约8MB/帧的带宽（32位深度 × 1920 × 1080 ÷ 1024² ≈ 7.9MB）。

---

## 关键公式与性能计算

### 帧预算分配计算

给定目标帧率 $f$（fps），每帧总时间预算为：

$$T_{frame} = \frac{1000}{f} \text{ ms}$$

对于60fps，$T_{frame} = 16.67\text{ ms}$。在移动端，通常将Shader执行时间预算 $T_{shader}$ 控制在总帧预算的30%~40%以内：

$$T_{shader} \leq T_{frame} \times 0.35 \approx 5.83 \text{ ms (60fps)}$$

### ALU指令密度估算

片元着色器总ALU指令数 $I_{total}$ 与像素填充率 $P$（pixels/s）以及GPU ALU峰值吞吐量 $A$（instructions/s）共同决定ALU占用率：

$$\text{ALU Utilization} = \frac{I_{total} \times P}{A}$$

例如：一个包含200条ALU指令的PBR Shader在1080p分辨率下全屏绘制（约200万像素/帧，60fps即$1.2 \times 10^8$像素/秒），若GPU ALU吞吐量为$2.0 \times 10^{10}$指令/秒，则ALU利用率为 $\frac{200 \times 1.2 \times 10^8}{2.0 \times 10^{10}} = 120\%$，即必然成为ALU瓶颈，需至少将指令数降至167条以下。

---

## 实际应用

### 案例：移动端PBR Shader从ALU瓶颈到平衡态的优化过程

某手机游戏的角色PBR Shader在Mali-G76 GPU上经Arm Mobile Studio分析，`EXEC_CORE_ACTIVE`为96%，确认ALU瓶颈。原始Shader包含以下高代价操作：

1. 逐像素计算GGX NDF（约15条ALU指令）
2. 逐像素计算Smith-GGX几何遮蔽函数 $G$（约12条ALU指令）
3. 逐像素使用`pow(NdotH, 128)`模拟高光（约8条ALU指令）
4. 3次独立的法线纹理采样（分别用于宏观法线、细节法线、布料纹理）

**优化步骤**：
- 步骤1：将GGX NDF + Smith G预积分为128×128 LUT（见前述烘焙策略），节省27条指令
- 步骤2：将3次法线采样合并为2次（宏观+细节叠加后再与布料混合），节省1次采样
- 步骤3：将视方向归一化从片元着色器移至顶点着色器（角色顶点数约8000，而屏占像素数约80000，减少10倍计算量）
- 步骤4：法线向量分量从`highp`降为`mediump`

优化后`EXEC_CORE_ACTIVE`降至58%，帧率从42fps提升至61fps，达到目标60fps。

### Unity Shader中的实际优化代码片段

```hlsl
// 优化前：逐像素计算 Fresnel，使用 highp pow
float fresnel = pow(1.0 - saturate(dot(normalWS, viewDirWS)), 5.0);

// 优化后：Schlick近似替代pow，并降低精度
mediump half fresnelApprox;
mediump half NdotV = saturate(dot(normalWS, viewDirWS));
// Schlick近似：(1-x)^5 ≈ x + (1-x)*exp(-5.55473x - 6.98316)x
fresnelApprox = NdotV + (1.0h - NdotV) * pow(max(