---
id: "cg-specular-workflow"
concept: "高光工作流"
domain: "computer-graphics"
subdomain: "pbr-materials"
subdomain_name: "PBR材质"
difficulty: 2
is_milestone: false
tags: ["实践"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 高光工作流

## 概述

高光工作流（Specular-Glossiness Workflow，简称 SG 工作流）是 PBR 材质系统中的一种贴图方案，由 Adobe/Allegorithmic 公司在 Substance 工具链早期版本中大力推广。它通过三张核心贴图来描述材质的物理属性：**漫反射颜色贴图（Diffuse）**、**高光颜色贴图（Specular）** 和 **光泽度贴图（Glossiness）**，分别控制材质的次表面散射颜色、镜面反射颜色和表面粗糙程度。

该工作流最早在 Unreal Engine 3 时代以非 PBR 形式存在，后来随着基于物理的渲染理论普及，Allegorithmic 将其升级为物理正确的 SG 版本，并在 Substance Painter 1.x 系列中作为主要工作流提供。相比后来崛起的金属度工作流（Metalness-Roughness Workflow），SG 工作流历史更早、美术人员过渡成本更低，因此在影视、建筑可视化等行业中至今仍有广泛使用。

理解 SG 工作流的意义在于：现实项目往往同时存在两套资产，引擎需要支持两种工作流的导入和转换。此外，SG 工作流在处理非金属材质的彩色高光（如人皮肤、漆面木材）时具备天然优势，可以直接在 Specular 贴图中绘制该颜色，而金属度工作流则无法直接做到这一点。

---

## 核心原理

### 三张贴图的物理含义

**Diffuse 贴图**存储的是材质的漫反射颜色，即光线经过次表面散射后离开表面的颜色。对于金属材质，Diffuse 值应当设置为纯黑（0, 0, 0），因为金属几乎不产生漫反射；对于非金属（电介质），Diffuse 代表材质的固有色。这一约定使得美术人员必须手动区分金属区域与非金属区域。

**Specular 贴图**存储 RGB 颜色值，直接描述材质的镜面反射率 F0（法向入射菲涅耳反射率）。对于电介质材质，F0 通常处于 0.02–0.05 的线性值范围（约对应 sRGB 下的 40–80 灰度），例如玻璃的 F0 约为 0.04，即 4%。对于金属，F0 可以是彩色值，例如金的 F0 约为 (1.0, 0.766, 0.336)，铜的 F0 约为 (0.955, 0.637, 0.538)，这些具体数值可以从真实材质测量数据库中查到。

**Glossiness 贴图**是粗糙度的反转版本，计算关系为：`Glossiness = 1.0 - Roughness`。白色（1.0）表示完全光滑的镜面，黑色（0.0）表示完全粗糙的漫反射表面。部分引擎（如 Unity 的 Standard Shader Legacy 模式）直接读取 Glossiness；而 Unreal Engine 5 则在内部统一使用 Roughness，导入 SG 资产时会自动执行这一反转计算。

### 与金属度工作流的核心差异

金属度工作流（MR 工作流）使用 **Base Color + Metalness + Roughness** 三张贴图。两者的本质差异在于**信息编码方式**不同：

| 属性 | SG 工作流 | MR 工作流 |
|------|-----------|-----------|
| 漫反射控制 | Diffuse 贴图（独立通道） | Base Color × (1 - Metalness) |
| 高光 F0 控制 | Specular 贴图（RGB，直接存储） | Base Color × Metalness + 0.04 × (1-M) |
| 粗糙度表达 | Glossiness（反转） | Roughness（正向） |
| 每像素数据量 | 3+3+1 = 7 通道 | 3+1+1 = 5 通道 |

SG 工作流总计需要 **7 个有效通道**（Diffuse RGB + Specular RGB + Glossiness），而 MR 工作流只需要 **5 个有效通道**，这意味着 SG 工作流的贴图存储成本更高，但对非标准材质的表达自由度更大。

### 菲涅耳约束与能量守恒

SG 工作流在物理正确性上存在一个内生风险：美术人员可以随意填写 Diffuse 和 Specular 的值，从而违反能量守恒定律。具体约束为：对于任意像素，`Diffuse + Specular ≤ 1.0`（各通道分量均需满足）。如果将金属材质的 Diffuse 错误设置为非零值，或者使 Diffuse + Specular 之和超过 1.0，最终渲染结果会出现物理上不可能存在的"发光"效果。MR 工作流通过算法约束消除了这一风险，这也是 MR 工作流逐渐成为游戏行业标准的重要原因之一。

---

## 实际应用

**Unity 引擎的 Standard Shader（Legacy）**默认支持 SG 工作流，通过勾选 "Specular Setup" 模式激活，Specular 贴图存储在 RGB 通道，Smoothness（即 Glossiness）存储在 Specular 贴图的 Alpha 通道中，节省一张贴图的采样开销。

**Unreal Engine 4/5** 本身不直接支持 SG 工作流，但 UE 的材质蓝图中可以通过手动节点将 SG 贴图转换为 MR 参数：Roughness = 1 - Glossiness，Metalness 根据 Specular 亮度阈值推断（通常亮度 > 0.5 的彩色 Specular 视为金属）。

**影视与 VFX 流程**中，Maya 的 Arnold 渲染器和 SideFX Houdini 的 Mantra 渲染器均支持直接输入 Specular Color 和 Roughness（等价于 SG 工作流中的 Specular + 1-Glossiness），因为离线渲染不受贴图通道数量限制，SG 工作流在该场景下非常自然。

在**贴图格式**上，SG 工作流的 Specular 贴图通常以 sRGB 空间存储（因为它是颜色数据），而 Glossiness 贴图则以线性空间存储，混淆两者的色彩空间设置是常见的管线配置错误。

---

## 常见误区

**误区一：认为 SG 工作流的 Diffuse 等同于传统 Phong 模型的漫反射贴图**
SG 工作流中的 Diffuse 是物理正确的次表面散射颜色，必须满足能量守恒，即金属区域的 Diffuse 必须为黑色。传统 Phong 流程的 Diffuse 贴图并无此约束，不能直接将旧资产的 Diffuse 贴图挪用进 SG 工作流而不做修改。

**误区二：Glossiness = Roughness 的反转，因此两者可以直接互换**
虽然数学关系为 `Glossiness = 1 - Roughness`，但两者描述的感知分布并不完全线性等价。不同渲染引擎对 Roughness/Glossiness 的内部映射可能采用平方处理（如 Unreal 内部使用 `α = Roughness²` 作为 GGX 的粗糙度参数），直接将 SG 资产的 Glossiness 贴图反转后不加修正地输入 MR 流程，可能导致高光范围偏差。

**误区三：SG 工作流已经过时，无需学习**
Substance 3D Painter 至今（2024 版）仍然提供 SG 工作流模板；glTF 2.0 规范虽以 MR 为主，但其扩展 `KHR_materials_specular` 专门为 SG 工作流提供了官方支持；大量历史资产（尤其是 2010–2016 年制作的影视级资产）均采用 SG 工作流存储。

---

## 知识关联

学习 SG 工作流之前，需要掌握**金属度工作流**的 Base Color / Metalness / Roughness 三通道含义以及菲涅耳 F0 的物理定义，因为 SG 工作流的 Specular 贴图本质上就是 F0 的直接存储，而 MR 工作流的 F0 则由引擎从 Base Color 和 Metalness 混合计算得出（公式：`F0 = lerp(0.04, BaseColor, Metalness)`）。

在实际管线中，SG 与 MR 之间的**双向转换算法**是衔接两种工作流的关键技术点，Allegorithmic 在 2016 年的技术白皮书《Substance PBR Conversion》中给出了完整的转换推导。掌握 SG 工作流后，可以进一步研究 glTF 扩展规范和多工作流混合管线的引擎实现，理解不同平台（游戏引擎、离线渲染器、Web 渲染器）如何统一处理异构 PBR 资产。