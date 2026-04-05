---
id: "cg-pp-stack"
concept: "后处理栈设计"
domain: "computer-graphics"
subdomain: "post-processing"
subdomain_name: "后处理"
difficulty: 3
is_milestone: false
tags: ["架构"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "A"
quality_score: 76.3
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-30
---

# 后处理栈设计

## 概述

后处理栈（Post-Processing Stack）是指将多个全屏图像处理效果按特定顺序组合在单一渲染管线中依次执行的架构设计。与单一效果的独立应用不同，后处理栈的核心挑战在于：当 Bloom、色调映射（Tonemapping）、环境光遮蔽（SSAO）、景深（DoF）等十余种效果叠加时，执行顺序的错误会导致在感知上完全错误的画面输出——例如在 LDR 空间中执行 Bloom 会使高亮区域的辉光颜色饱和度失真。

后处理栈的概念随着延迟渲染（Deferred Rendering）在 2005 年前后的普及而系统化。Valve 在《传送门 2》（2011）的技术文档中首次公开描述了基于"效果依赖图"的栈排序策略，随后 Unity 于 2017 年推出的 Post-Processing Stack v2 和 Unreal Engine 的 Post Process Volume 系统将这一概念标准化为商业引擎的内置功能。正确的栈设计能将多个全屏 Pass 合并为更少的渲染目标（Render Target）切换次数，直接影响 GPU 带宽消耗和帧率稳定性。

## 核心原理

### 效果排序的依赖规则

后处理栈中每个效果对输入数据的格式有严格要求，决定其在栈中的合法位置。整个栈通常分为三个阶段：

- **HDR 阶段**（色调映射之前）：Bloom、镜头耀斑（Lens Flare）、曝光调整、SSAO 必须在此阶段执行。因为这些效果依赖线性 HDR 颜色值（通常为 fp16 格式，范围远超 [0,1]），若在色调映射之后处理，辉光强度将被 Gamma 压缩截断。
- **色调映射节点**：ACES、Filmic、Reinhard 等算子在此将 HDR 转换为 LDR，是 HDR 阶段与 LDR 阶段的唯一分界点，每个栈中有且仅有一个此节点。
- **LDR 阶段**（色调映射之后）：色差（Chromatic Aberration）、胶片颗粒（Film Grain）、暗角（Vignette）、FXAA/TAA 抗锯齿在此阶段执行。其中抗锯齿必须是 LDR 阶段的最后一个效果，因为颗粒和色差在抗锯齿后会被平滑掉，导致效果减弱。

景深（DoF）是排序中最特殊的效果：它需要深度缓冲（Depth Buffer）作为输入，且必须在 Bloom 之前执行，否则虚化区域会二次叠加辉光，导致焦外区域过曝。

### 性能预算管理

后处理栈的性能预算以毫秒（ms）为单位分配在目标帧时间内。以 60fps 为目标（总帧时间约 16.67ms），通常将后处理预算限定为 **2–4ms**，其中单个全屏效果的 GPU 时间开销参考值如下：

| 效果 | 1080p 典型开销 |
|------|--------------|
| Bloom（双向模糊，5次降采样） | ~0.8ms |
| SSAO（半分辨率） | ~1.2ms |
| TAA | ~0.5ms |
| DoF（Bokeh散景） | ~1.5ms |
| 色调映射 + 颜色分级（Color Grading） | ~0.3ms |

**Render Target 合并**是关键的优化手段：若两个相邻效果的输入/输出格式相同，可通过 MRT（Multiple Render Targets）或像素着色器内联合并，消除中间纹理采样。Unity URP 的 `RenderGraph` API 允许声明效果间的资源依赖，自动分析哪些 Pass 可以合并为同一 `RenderPass`，减少 `LoadAction`/`StoreAction` 带来的带宽开销——在移动端 TBDR 架构（如 Mali、Apple GPU）上，这一优化可节省 15%–30% 的后处理帧时间。

### 分辨率缩放策略

后处理栈中不同效果对分辨率的敏感度不同，按效果特性采用差异化分辨率可节省大量填充率（Fill Rate）：

- **必须全分辨率**：TAA、FXAA（因为其核心功能即消除像素级锯齿）
- **可用半分辨率（0.5x）**：SSAO、Bloom 的模糊 Pass（人眼对低频信息分辨率不敏感）
- **可用四分之一分辨率（0.25x）**：雾效（Fog）的散射计算

使用半分辨率执行 SSAO 后，需通过双边上采样（Bilateral Upsample）将结果混合回全分辨率，避免锯齿状遮蔽边界。

## 实际应用

**移动端栈裁剪**：在 Android 中档机（GPU 性能约 50 GFLOPS）上，完整后处理栈往往超出 4ms 预算。实践中通过后处理体积的 `Quality` 参数将 DoF 替换为更廉价的径向模糊（Radial Blur，约 0.3ms），并禁用 Bloom 的最高两级降采样 Pass，将整体预算压至 2.5ms 以内。

**URP 中的 Renderer Feature 注册顺序**：在 Unity URP 中，自定义后处理效果通过 `ScriptableRendererFeature` 注册到栈时，必须显式指定 `RenderPassEvent` 枚举值（如 `BeforeRenderingPostProcessing`、`AfterRenderingPostProcessing`），系统依据此枚举而非脚本挂载顺序决定执行序，错误地将色调映射前效果设置为 `AfterRenderingPostProcessing` 是最常见的颜色空间错误来源。

**色彩分级 LUT 的合并**：将颜色分级（Color Grading）与色调映射合并为单个 Pass 是通用优化：预先将 LUT（Look-Up Table，典型尺寸为 32×32×32 的 3D 纹理）烘焙进色调映射着色器，一次采样即完成色调映射和 LUT 查找，相比分两个 Pass 节省约 0.2ms 及一次全屏纹理读写。

## 常见误区

**误区一：认为效果越多叠加越好，只需靠 Pass 合并优化即可**。实际上，即使所有 Pass 都合并到最少的 Render Target 切换，10 个效果的像素着色器计算量本身仍然是线性叠加的。在移动端，纹理采样次数（而非 ALU 计算）往往是瓶颈，Bloom 的高斯模糊每次降采样需要 4–9 次纹理采样，5 级降采样合计约 40 次采样，这是不可合并的固有开销。

**误区二：认为 TAA 可以放在任何位置**。TAA 依赖相邻帧的历史缓冲（History Buffer），必须在几何信息（如 DoF 模糊、运动模糊）叠加之前的原始清晰图像上采样，否则历史帧的模糊信息会在累积中产生"鬼影"（Ghosting）。同时 TAA 又必须在 LDR 转换后执行以避免 HDR 高亮像素对混合权重产生偏差——这一矛盾是 TAA 在复杂后处理栈中位置争议的根本来源，Unreal Engine 5 通过 TSR（Temporal Super Resolution）将时域采样提前至 HDR 阶段来解决此问题。

**误区三：后处理体积的 Blend Distance 不影响性能**。Blend Distance 控制体积边界外的效果权重插值区域，当摄像机在插值区域内时，引擎需同时计算两组参数并在 CPU 上插值，若场景中存在 8 个以上相互重叠的后处理体积，每帧的参数混合计算开销可超过 0.1ms（CPU 侧），在移动端这是不可忽视的额外负担。

## 知识关联

后处理栈设计以**后处理体积（Post-Processing Volume）**为前提：体积定义了各效果参数的空间分布和优先级，栈则负责将这些参数以正确顺序转化为实际渲染指令。没有对体积混合规则（权重、优先级覆盖）的理解，就无法正确评估运行时栈中每个效果的参数来源，从而导致性能预算估算偏差。

在图形管线的上游，**GBuffer 设计**和**深度缓冲精度**（16-bit vs 24-bit）直接约束后处理栈中 SSAO 和 DoF 的实现质量与开销——DoF 的 CoC（Circle of Confusion）半径计算公式 `CoC = A × |d_focus - d_pixel| / d_pixel × f / (f - d_focus)` 中，`d` 值直接来自深度缓冲的重建精度。在渲染管线学习路径上，后处理栈设计是将各类单一全屏效果知识整合为工程决策能力的汇集点，要求学习者同时具备图形 API（Render Target 管理）、视觉感知（效果优先级判断）和性能分析（GPU 帧分析工具使用）三方面的复合能力。