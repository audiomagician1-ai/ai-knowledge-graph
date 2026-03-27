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

高光工作流（Specular-Glossiness Workflow，简称 S/G 工作流）是 PBR 材质系统中用于描述表面反射特性的一种参数化方案，由 Adobe 与 Allegorithmic 在 2014 年前后共同推广，并被纳入 glTF 1.0 的扩展规范 `KHR_materials_pbrSpecularGlossiness` 中。它通过两张贴图——**漫反射颜色图（Diffuse/Albedo）** 和 **高光颜色图（Specular）** 加上**光泽度图（Glossiness）**——来完整描述材质的物理响应。

与金属度工作流（Metallic-Roughness）不同，高光工作流将漫反射与镜面反射颜色作为两个**独立可控**的输入量，使艺术家可以直接指定非金属介质（如皮肤、木材、涂层）的精确 F0（零度入射角菲涅耳反射率）值，而不必依赖引擎从金属度参数中间接推导。这一特性让该工作流在旧一代 AAA 游戏项目和 CG 影视制作中积累了大量存量资产。

高光工作流之所以值得专门学习，在于大量遗留管线（如早期 Unity 5 的 Legacy Shaders、Substance Painter 1.x 版本的默认导出模板）仍输出 S/G 贴图，资产迁移和项目维护时必须理解其内部逻辑，否则会在转换时引入严重的能量守恒错误。

---

## 核心原理

### 三张贴图的物理含义

高光工作流的信息由三张贴图承载：

- **Diffuse 图**：存储非金属材质的漫反射颜色，对金属材质此通道应为纯黑（0,0,0），因为金属无漫反射。
- **Specular 图**：以 sRGB 存储 F0 反射率颜色，非金属材质的 F0 通常落在 0.02–0.05（线性值）范围内，对应灰阶约为 40–60/255；金属材质的 F0 则是其特征颜色（如金的 F0 约为 (1.0, 0.71, 0.29) 线性值）。
- **Glossiness 图**：光泽度 `g = 1 - roughness`，因此 Glossiness = 255 对应完全光滑镜面，Glossiness = 0 对应完全粗糙漫反射表面。与金属度工作流的 Roughness 图相比，两者是简单的数值取反关系：`Roughness = 1.0 - Glossiness`。

### 能量守恒约束

高光工作流的核心物理约束是：漫反射分量与镜面反射分量之和不得超过 1。即对任意像素：

$$\text{Diffuse}_{\text{linear}} + \text{Specular}_{\text{linear}} \leq (1, 1, 1)$$

若艺术家同时将 Diffuse 和 Specular 通道设为高亮颜色，渲染器将输出超出物理范围的亮度，产生"发光"伪影。Substance Painter 的 S/G 验证工具（Validate Material）正是检测这一约束是否被违反。

### BRDF 中的作用方式

在 Cook-Torrance BRDF 中，高光工作流对渲染方程的代入方式如下：镜面反射项的 F0 直接来自 Specular 图采样值；漫反射项的 Albedo 直接来自 Diffuse 图采样值；法线分布函数（NDF，通常为 GGX/Trowbridge-Reitz）所需的粗糙度参数由 `α = (1 - Glossiness)²` 转换得到（部分引擎使用 `α = 1 - Glossiness` 的线性映射，具体需查阅引擎文档确认）。

---

## 实际应用

### 与金属度工作流互转

将 S/G 贴图转换为 M/R（Metallic-Roughness）贴图时，常用的算法步骤如下：

1. 根据 Specular 图的亮度判断金属度：若某像素的 Specular 值（线性）高于阈值 0.04（约 sRGB 值 60/255），则该像素倾向于金属，否则为非金属。
2. 对于被判定为金属的像素，Metallic = 1，BaseColor = Specular 颜色。
3. 对于非金属像素，Metallic = 0，BaseColor = Diffuse 颜色。
4. Roughness = 1 - Glossiness（逐像素取反）。

此转换为有损操作，在金属与非金属混合边界（如生锈金属）处会出现边缘精度损失，因此 glTF 2.0 的核心规范最终选择 M/R 作为官方标准，并将 S/G 降级为扩展。

### Substance Painter 中的工作流选择

在 Substance Painter 2023 中，新建项目时可在"Template"下拉菜单选择"PBR - Specular/Glossiness"模板，此时导出配置将自动生成 `diffuse`、`specular`、`glossiness` 三张贴图。选择此工作流后，材质层的"Base Color"槽位语义变为漫反射颜色，"Specular"槽位可直接输入 F0 颜色，这与选择 Metallic 模板时的行为有本质不同。

### Unity 的遗留材质支持

Unity 早期版本（5.x）内置的 `Standard (Specular setup)` Shader 使用 S/G 工作流。该 Shader 的 Specular 贴图存储 F0 颜色，Smoothness 滑块对应 Glossiness 值（即 Unity 中 Smoothness = Glossiness，而非 Roughness）。在将旧项目迁移至 URP/HDRP 时，需将 Smoothness 贴图取反才能正确对应 HDRP 使用的 Roughness 参数。

---

## 常见误区

### 误区一：Specular 图可以任意填色

许多初学者将 Specular 图当作普通颜色层涂抹，结果非金属材质的 F0 值远超真实范围（如将非金属的 Specular 设为 (0.8, 0.8, 0.8)，线性值约 0.6，是真实非金属 F0 的 10 倍以上）。真实非金属介质的 F0 集中在 2%–5% 反射率，只有宝石类（如钻石约 5.7%，水晶约 6.4%）才接近 8%，不应随意将非金属 Specular 设为高亮颜色。

### 误区二：Glossiness 与 Roughness 数值含义相同

部分工具（如某些版本的 3ds Max 导出插件）会将 Roughness 值直接写入文件名含"glossiness"的通道而不做取反处理，导致导入目标引擎时材质完全反转——原本的粗糙混凝土看起来像镜面，原本的光滑金属看起来像磨砂纸。检验方法是用纯白（1.0）和纯黑（0.0）的参数值分别渲染，观察哪端对应高光集中的镜面效果。

### 误区三：S/G 工作流比 M/R 工作流"更精确"

高光工作流提供更多自由度，但这正是其风险所在：艺术家可以指定物理上不存在的 F0 颜色（例如给非金属赋予金属色 F0），使能量守恒被破坏。M/R 工作流通过将金属度参数限制为 0 或 1（实践中推荐不使用 0–1 之间的中间值，除模拟过渡区如锈迹），从机制上减少了这类人为错误的概率。

---

## 知识关联

**前置概念——金属度工作流**：学习 S/G 工作流前需理解 M/R 工作流的 BaseColor 与 Metallic 参数含义，才能对照出两种工作流在"Albedo 含义"和"F0 来源"上的本质差异。M/R 工作流中 F0 由引擎根据金属度插值自动计算（非金属固定取 0.04），而 S/G 工作流由 Specular 图直接给定，这是两者在信息编码方式上的根本分歧。

**横向关联——法线贴图与粗糙度贴图**：无论使用 S/G 还是 M/R 工作流，法线贴图的使用方法完全相同；Glossiness 图与 Roughness 图携带等价信息，仅值域方向相反，替换时只需在着色器中做 `1.0 - x` 运算即可，不需要重新烘焙。

**延伸实践——glTF 格式兼容性**：glTF 2.0 核心规范（2017年发布）不再原生支持 S/G 工作流，若需导出 S/G 资产到 glTF，必须启用 `KHR_materials_pbrSpecularGlossiness` 扩展，而该扩展自 2022 年起已被 Khronos 标注为"Archived"（存档状态），新项目不建议依赖此扩展，应优先转换为 M/R 工作流。