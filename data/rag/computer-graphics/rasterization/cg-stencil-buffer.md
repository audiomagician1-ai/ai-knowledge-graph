---
id: "cg-stencil-buffer"
concept: "模板缓冲"
domain: "computer-graphics"
subdomain: "rasterization"
subdomain_name: "光栅化"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 3
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

# 模板缓冲

## 概述

模板缓冲（Stencil Buffer）是GPU帧缓冲区中的一个独立存储区域，通常每像素存储8位无符号整数，取值范围为0–255。它与深度缓冲和颜色缓冲并列存在，在光栅化管线的片元处理阶段介入，通过对缓冲中存储的整数值进行比较运算，决定当前片元是否允许写入颜色缓冲和深度缓冲。

模板缓冲的概念随着OpenGL 1.0（1992年发布）的规范确立而被正式引入图形API，此后DirectX也在其早期版本中采纳了相同机制。其核心价值在于：它以极低的显存带宽开销（每像素仅1字节），实现了纯GPU端的像素级遮罩逻辑，将"哪些像素该被渲染"的判断完全卸载到硬件层面，无需CPU介入或纹理采样。

## 核心原理

### 模板测试的执行流程

模板测试发生在深度测试之前（若模板测试失败则无需执行深度测试），在片元着色器输出之后。每个片元到达此阶段时，硬件将模板缓冲中对应位置的**参考值（ref）**与**当前存储值（stencil value）**按指定的**比较函数（func）**进行比较。OpenGL中通过 `glStencilFunc(func, ref, mask)` 设置：

- `func` 可选 `GL_ALWAYS`、`GL_EQUAL`、`GL_NOTEQUAL`、`GL_LESS` 等8种
- `mask` 对 ref 和存储值在比较前按位与，用于只关注部分位

测试失败则该片元被完全丢弃；测试通过则进入深度测试阶段。

### 模板写入操作（stencilOp）

通过 `glStencilOp(sfail, dpfail, dppass)` 定义三种情形下对模板缓冲的更新操作：

| 情形 | 含义 |
|------|------|
| sfail | 模板测试失败时的操作 |
| dpfail | 模板测试通过但深度测试失败时的操作 |
| dppass | 模板测试和深度测试均通过时的操作 |

可用操作包括 `GL_KEEP`（保持不变）、`GL_ZERO`（置0）、`GL_REPLACE`（写入ref值）、`GL_INCR`（加1，钳位到255）、`GL_DECR`（减1，钳位到0）、`GL_INVERT`（按位取反）等。这套"读–比较–写"的设计使模板缓冲既能作为遮罩来源，又能在渲染过程中动态更新自身。

### 8位存储的精度含义

8位存储意味着模板值范围为0–255，在阴影体算法中，这个上限限制了视锥内可叠加的阴影体层数。Carmack（卡马克）在2002年为Doom 3开发反转深度阴影体（z-fail）方法时，必须保证场景中阴影体的最大叠加计数不超过127层（因为需要同时处理正负计数），这是8位模板缓冲在实际项目中硬性约束的典型案例。

## 实际应用

### 物体轮廓描边

轮廓描边是模板缓冲最常见的教学案例。分两个渲染Pass完成：

1. **Pass 1**：启用模板写入，`glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)`，`ref=1`；正常渲染目标物体，物体覆盖的像素模板值被写为1。
2. **Pass 2**：关闭模板写入，`glStencilFunc(GL_NOTEQUAL, 1, 0xFF)`；将物体沿法线方向略微放大后重新渲染（通常在顶点着色器中沿法线偏移0.05–0.1单位），片元只在模板值≠1的位置通过测试，形成环绕原始物体的描边区域。

### 平面镜面反射

渲染镜面时，先将镜面区域写入模板缓冲（值设为1），再在后续渲染反射场景时设置 `glStencilFunc(GL_EQUAL, 1, 0xFF)`，确保反射内容只出现在镜面像素范围内，防止反射几何体渗出镜面边界。

### Carmack反转阴影体（z-fail算法）

经典的z-pass阴影体算法在摄像机处于阴影体内部时会失败，z-fail（即Carmack反转）通过以下步骤解决：

1. 渲染场景环境光部分。
2. 禁用颜色写入，对阴影体**背面**执行 `GL_INCR_WRAP`（模板加1），对阴影体**正面**执行 `GL_DECR_WRAP`（模板减1）。
3. 最后用 `glStencilFunc(GL_EQUAL, 0, 0xFF)` 仅在模板值为0的区域渲染光照——模板值不为0的区域即为阴影。`GL_INCR_WRAP` 和 `GL_DECR_WRAP` 操作采用环绕而非钳位，确保计数在超过255后从0开始循环，避免精度溢出破坏结果。

## 常见误区

### 误区一：认为模板测试在深度测试之后执行

很多初学者因为记忆混淆，认为管线顺序是"深度测试→模板测试"。实际上标准OpenGL/Vulkan规范明确规定顺序为**模板测试→深度测试→片元写入**。之所以先做模板测试，正是为了让不必要的片元在更早阶段被丢弃，节省深度比较的计算资源。

### 误区二：模板缓冲与Alpha遮罩可以互换

Alpha遮罩依赖片元着色器输出和混合单元，意味着不透明片元的完整着色计算已经执行完毕。模板测试发生在着色之后但写入之前的固定功能阶段，且其判断依据是上一帧或同帧前序Pass写入的整数值，而非当前片元的颜色信息。因此模板缓冲适合基于几何区域的像素级开关，Alpha遮罩更适合基于纹理的半透明效果，二者机制和开销完全不同。

### 误区三：`GL_INCR` 与 `GL_INCR_WRAP` 效果相同

`GL_INCR` 在值达到255时保持255（钳位），而 `GL_INCR_WRAP` 会从255变为0（环绕）。在阴影体算法中若误用 `GL_INCR`，当阴影体叠加超过255层时所有超出部分的计数都卡在255，导致本应为0（光照区域）的像素显示为阴影，产生渲染错误。

## 知识关联

模板缓冲的前置知识是**深度缓冲**：理解每像素存储一个深度值并在光栅化阶段进行逐片元比较的机制，是理解模板缓冲"每像素存储整数并逐片元比较"的直接类比。深度缓冲处理"远近遮挡"，模板缓冲处理"区域准入"，两者在GPU帧缓冲区中协同工作，共享相似的测试–写入双阶段设计。

在现代图形API中，Vulkan将模板操作封装在 `VkStencilOpState` 结构体内，作为 `VkPipelineDepthStencilStateCreateInfo` 的字段，与深度状态统一配置，体现了两个缓冲区在硬件设计层面的高度耦合。掌握模板缓冲后，可以进一步探索**早期Z剔除（Early-Z）**优化与模板测试的交互关系，以及延迟渲染（Deferred Rendering）中使用模板缓冲区分几何体类别的高级用法。