---
id: "shadow-mapping"
concept: "阴影映射"
domain: "game-engine"
subdomain: "rendering-pipeline"
subdomain_name: "渲染管线"
difficulty: 2
is_milestone: false
tags: ["阴影"]

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



# 阴影映射

## 概述

阴影映射（Shadow Mapping）是一种通过从光源视角预渲染深度信息来判断场景中哪些片段处于阴影中的实时渲染技术。其基本原理由Lance Williams于1978年在论文《Casting Curved Shadows on Curved Surfaces》中首次提出，至今仍是游戏引擎实时阴影的主流基础算法。

该技术的核心思路是：若某个片段从光源视角看去，其深度值大于光源深度贴图中记录的最小深度值，则该片段被遮挡，处于阴影中。这一判断过程称为深度比较（Depth Comparison），整个流程需要两次渲染Pass：第一次从光源视角生成深度贴图（Shadow Map），第二次在正常相机视角渲染时采样该贴图进行阴影判断。

阴影映射在游戏引擎中被广泛采用，是因为它完全运行在GPU上且与场景几何复杂度解耦——无论场景有多少三角形，只要能在光源视角完成光栅化，阴影计算开销相对可控。Unity HDRP、Unreal Engine 5的Lumen以前的传统阴影系统均基于此原理构建。

## 核心原理

### 基础阴影映射与深度偏移

基础Shadow Map算法中，光源视角的深度值存储在一张深度纹理中，通常使用16位或32位浮点精度。在着色阶段，将世界空间片段坐标变换到光源裁剪空间（Light Clip Space），得到NDC坐标后采样深度图，若片段深度 `d_frag > d_shadow + bias`，则判定为阴影。

然而，由于深度贴图分辨率有限，会产生"阴影粉刺"（Shadow Acne）伪影：同一平面的自遮挡导致条纹状错误。解决方案是添加深度偏移（Depth Bias），通常公式为：`bias = max(0.05 * (1.0 - dot(N, L)), 0.005)`，其中N为法线，L为光源方向。偏移过大又会导致"Peter Panning"现象（物体与阴影脱离地面）。

### 级联阴影映射（CSM）

级联阴影映射（Cascaded Shadow Maps，CSM）解决单张Shadow Map无法同时覆盖近处细节和远处范围的问题。CSM将视锥体（Frustum）沿深度方向分割为N个子视锥体（通常为4级），每级使用独立的Shadow Map。分割位置由对数-线性混合公式决定：

```
C_i = λ * C_log_i + (1 - λ) * C_uniform_i
```

其中λ（Lambda）是混合系数，通常取0.5~0.75。距离相机越近的级联使用分辨率越高、覆盖范围越小的Shadow Map，从而在近处获得高质量阴影同时保持远处覆盖。Unreal Engine 4默认使用4级CSM，每级分辨率为2048×2048。

### 软阴影技术：PCSS与VSM

基础Shadow Map产生的是硬阴影（Hard Shadow），边缘锯齿明显。**PCF（Percentage Closer Filtering）**通过对深度比较结果进行多次采样取平均来模拟软阴影，例如在3×3邻域做9次深度比较并平均。

**PCSS（Percentage Closer Soft Shadows）**由Randima Fernando于2005年提出，在PCF基础上根据遮挡体（Blocker）到接收面的距离动态调整采样半径，实现接触处硬、远处软的物理准确软阴影。其遮挡搜索半径公式为：`w_penumbra = (d_receiver - d_blocker) / d_blocker * w_light`，计算开销较高，常用泊松分布采样盘（Poisson Disk）降低采样数量。

**VSM（Variance Shadow Maps）**由William Donnelly与Andrew Lauritzen于2006年提出，存储深度的均值E(d)和平方均值E(d²)，利用切比雪夫不等式估计片段处于阴影中的概率：`P(x ≥ t) ≤ σ² / (σ² + (t - μ)²)`，其中σ²为方差。VSM的优点是可以对Shadow Map进行纹理滤波（Mipmap、各向异性过滤），但存在"漏光"（Light Bleeding）问题，即相邻深度差较大时出现错误的亮区。

## 实际应用

**定向光（Directional Light）**使用正交投影矩阵生成Shadow Map，配合CSM覆盖整个场景深度范围，适合太阳光等平行光源，是室外场景阴影的标准方案。

**点光源（Point Light）**需要Cube Shadow Map，即向6个方向各生成一张深度图，组成立方体贴图，着样时计算光源到片段的方向向量来采样对应面，计算量是定向光的6倍。

在Unity URP中，可通过`ShadowCasterPass`自定义投影物体的Shadow Map渲染，通过`_ShadowBias`控制全局偏移。Unreal Engine中，`r.Shadow.MaxCSMResolution`命令行参数可调整CSM最大分辨率，直接影响阴影质量与显存占用的平衡。

移动端游戏通常将CSM级联数减少到2级，并降低每级分辨率至512×512以控制带宽，同时使用简化的PCF（2×2 tap）替代PCSS。

## 常见误区

**误区1：增大Shadow Map分辨率可以解决所有阴影问题。**  
分辨率仅影响"透视锯齿"（Perspective Aliasing），即近处阴影边缘的像素化。然而Depth Bias不足导致的Shadow Acne、VSM的漏光、以及PCSS的噪点，均不能通过提升分辨率解决，需要针对性调整对应参数。

**误区2：PCF是一种模糊Shadow Map贴图本身的操作。**  
PCF对比较结果（0或1的二值）进行滤波，而非对深度值进行滤波。直接对深度值进行双线性插值会产生错误的中间深度，导致比较出错，这正是VSM引入概率模型存储统计量的原因所在。

**误区3：CSM的级联数越多越好。**  
每增加一级CSM，需要额外一次从光源视角的场景渲染Pass，DrawCall数量线性增长。当场景Draw Call总量较多时，4级CSM可能导致CPU提交开销翻倍以上。实际项目需根据场景规模和目标帧率，在级联数（通常2~4级）与质量间取得平衡。

## 知识关联

阴影映射依赖**延迟渲染（Deferred Rendering）**的G-Buffer中存储的世界空间位置或深度重建能力，在延迟管线中阴影计算通常在光照Pass中将片段世界坐标变换至光源空间完成采样，避免了前向渲染中每个物体单独计算阴影的开销。延迟管线下Shadow Map的生成Pass（光源视角的几何渲染）独立于G-Buffer生成，是渲染管线中较早执行的离屏渲染步骤。

理解阴影映射的深度比较与偏移机制，是进一步学习屏幕空间阴影（Screen Space Shadows）和光线追踪阴影（Ray-Traced Shadows）的基础——后者可视为对Shadow Map深度查询局限性的直接改进方案，通过逐片段发射Shadow Ray来完全规避透视锯齿与偏移参数调优的问题。