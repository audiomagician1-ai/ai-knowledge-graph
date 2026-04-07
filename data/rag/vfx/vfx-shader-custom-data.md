---
id: "vfx-shader-custom-data"
concept: "自定义数据"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

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
updated_at: 2026-03-26
---



# 自定义数据

## 概述

自定义数据（Custom Data）是Unity粒子系统中一套专用的数据传递管线，允许开发者将每个粒子的个性化数值（最多两组Vector4，即8个float通道）通过粒子渲染器直接写入Shader的顶点数据流。与粒子的内置属性（位置、颜色、生命周期）不同，Custom Data完全由开发者定义语义，可以驱动UV动画偏移、溶解阈值、发光强度等任意视觉效果。

这一功能自Unity 5.5版本引入，解决了此前只能通过MaterialPropertyBlock或脚本逐帧SetFloat来修改粒子材质属性的性能瓶颈问题。旧方式每帧需要CPU向GPU发起独立的Draw Call参数更新，而Custom Data将数据打包进粒子的顶点流，使得GPU可以在同一个实例化批次内读取每个粒子的差异化参数，批渲染效率大幅提升。

理解自定义数据管线的关键在于它涉及三个配置层的联动：粒子系统的**Custom Data模块**、粒子渲染器（Particle System Renderer）的**Custom Vertex Streams**，以及Shader中对应的**顶点输入语义**。三者任意一环配置不匹配，数据就会静默失效或写入错误通道，这是初学者最常踩到的陷阱。

---

## 核心原理

### Custom Data模块的两个槽位

粒子系统的Custom Data模块提供**Custom1**和**Custom2**两个独立槽位，每个槽位可设置为**Vector**或**Color**模式。Vector模式下可分别为X、Y、Z、W四个分量配置曲线或常量，Color模式则将RGBA映射为4个float写入同一槽位。每个槽位本质上是一个XYZW四元组，合计8个独立float通道，在Shader中对应`float4 custom1`和`float4 custom2`两个变量。

若将Custom1设置为Vector模式并仅激活XY两个分量，则Z和W通道会写入0值占位，Shader端仍能接收到完整的float4，只是后两个分量无实际意义。

### Custom Vertex Streams的绑定机制

粒子渲染器组件中的**Custom Vertex Streams**是连接粒子数据与Shader顶点输入的桥梁。在Renderer组件的Custom Vertex Streams列表中，可将`Custom1.xyzw`或`Custom1.xy`等分量拖入流列表，Unity会将其打包进顶点属性。Shader端需要用**TEXCOORD**语义接收这些数据，例如：

```hlsl
struct appdata {
    float4 vertex   : POSITION;
    float4 color    : COLOR;
    float4 texcoord : TEXCOORD0;   // UV + Custom1.xy
    float4 custom1  : TEXCOORD1;   // Custom1.zw + Custom2.xy
};
```

注意Unity的顶点流是**顺序打包**的，即流列表中靠上的项先填充TEXCOORD的x分量，依次向下填充y、z、w。如果TEXCOORD0已被UV占用了xy，那么Custom1.xy就会自动对齐到zw，而不是另起一个新的TEXCOORD语义。此打包顺序必须与Shader结构体完全一致，否则数据偏移。

### 数据类型与精度限制

Custom Data中所有通道均以**float32**精度存储在粒子的模拟数据中，但经过顶点流传递到Shader后，精度受顶点格式限制。如果渲染器的顶点压缩选项开启了`UV Channels`的半精度（float16），则Custom Data如果复用了TEXCOORD通道，其精度会降至16位，适合0~1范围的归一化值，但不适合大数值坐标。若需要传递世界空间坐标等大值，需要在Project Settings → Player → Vertex Compression中关闭对应通道的压缩。

### 脚本驱动Custom Data

除模块曲线外，还可通过C#脚本用`ParticleSystem.SetCustomParticleData(List<Vector4>, ParticleSystemCustomData.Custom1)`在运行时为每个粒子写入差异化的Vector4值，配合`GetCustomParticleData`读取。此接口每帧操作整个粒子数组，时间复杂度为O(n)，适合粒子数量在1000以内的场景，超过该量级建议改用Compute Shader方案。

---

## 实际应用

**UV序列帧动画的帧索引传递**：将Custom1.x配置为0到15的曲线（代表4×4序列帧的帧编号），在Shader中用`floor(custom1.x)`取整后计算UV偏移量`float2(col/4.0, row/4.0)`，实现每个粒子独立的序列帧播放进度，避免所有粒子同步切帧。

**溶解特效的阈值控制**：Custom1.y存储每个粒子从0到1的溶解进度曲线，Shader中将其与噪声贴图采样值做比较：`clip(noiseVal - custom1.y)`，粒子在生命周期末尾时custom1.y接近1，溶解面积扩大至完全消失，每个粒子的溶解速率可以通过曲线独立控制。

**颜色渐变叠加**：Custom2设置为Color模式，在粒子生命周期内定义一条从蓝色到橙色的渐变，Shader中将Custom2.rgba与主颜色相乘后叠加自发光，实现与粒子颜色模块颜色独立的双层颜色动画效果。

---

## 常见误区

**误区一：认为Custom Data可以不配置Vertex Streams直接在Shader中读取**。Custom Data模块只负责计算和存储每个粒子的数据，如果不在Renderer的Custom Vertex Streams中显式添加对应条目，这些数据就不会被写入顶点缓冲区，Shader中读到的将是未定义数值（通常为0或上一帧的残留数据）。两个面板必须同时配置。

**误区二：Shader中TEXCOORD语义编号可以任意指定**。Unity粒子顶点流是线性顺序填充的，开发者无法控制某项数据"跳过"填充到TEXCOORD3。如果流列表中前四项数据恰好填满了TEXCOORD0，第五项数据会自动进入TEXCOORD1的x分量。Shader结构体中的语义声明必须严格按照这个顺序，若随意跳跃语义编号会导致数据错位，且Unity不会给出任何编译报错。

**误区三：Custom Data与材质属性块（MaterialPropertyBlock）等价**。MaterialPropertyBlock的SetFloat作用于整个渲染器组件，所有粒子共用同一个材质参数值；Custom Data则为粒子系统中**每一个独立粒子**存储不同的值，两者粒度根本不同。用MaterialPropertyBlock无法实现同一粒子系统中不同粒子各自具有不同溶解阈值的效果。

---

## 知识关联

学习自定义数据之前，需要理解**渲染器类型**的选择逻辑——Billboard、Mesh、Stretched Billboard等渲染器类型决定了顶点流中Position、Normal等内置语义的存在形式，这会影响Custom Data实际占用的TEXCOORD编号起始位置。此外，**拖尾Shader**中已经演示了如何在粒子相关材质中手写顶点输入结构体，该基础使开发者能够理解appdata中增加TEXCOORD1声明的语法规范。

掌握Custom Data管线之后，自然过渡到**混合模式**的深入配置——当Custom Data驱动透明度或溶解系数时，必须根据溶解边缘的半透明需求选择Additive、Alpha Blend或Premultiplied等混合模式，才能让Custom Data控制的视觉效果在最终合成中呈现正确的叠加关系。