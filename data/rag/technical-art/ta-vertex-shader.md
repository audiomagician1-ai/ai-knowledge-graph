---
id: "ta-vertex-shader"
concept: "顶点着色器编写"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 顶点着色器编写

## 概述

顶点着色器（Vertex Shader）是GPU渲染管线中第一个可编程阶段，它对每一个输入顶点独立执行一次，将模型空间（Object Space）中的顶点位置变换到裁剪空间（Clip Space）。最关键的职责是输出 `SV_POSITION` 语义的齐次坐标，使光栅化器能够正确插值生成片元。这个阶段无法创建或销毁顶点，只能读取并修改每个顶点的属性。

顶点着色器概念随可编程管线的诞生而出现。DirectX 8.0（2000年）首次引入可编程顶点着色器1.0，取代了固定管线中的变换和光照（T&L）单元。此后HLSL随DirectX 9（2002年）正式推出，顶点着色器从汇编语言升级为高级着色语言，极大降低了编写难度。

顶点着色器是实现非标准几何变形、顶点动画和屏幕空间特效的唯一入口。CPU无法高效地并行处理数百万顶点，而GPU通过顶点着色器以数千个线程同时执行变换计算，是实现旗帜飘动、水面波浪、蒙皮骨骼等效果的基础技术路径。

## 核心原理

### MVP矩阵变换链

顶点着色器的核心运算是将顶点坐标依次经过模型矩阵（Model）、视图矩阵（View）、投影矩阵（Projection）三次变换，最终输出裁剪空间坐标：

```
posClip = mul(UNITY_MATRIX_MVP, float4(posOS, 1.0));
```

其中 `posOS` 是模型空间中的顶点位置，`UNITY_MATRIX_MVP` 是三个矩阵的预乘结果。在HLSL中，`mul(矩阵, 向量)` 执行列向量乘法，而 `mul(向量, 矩阵)` 执行行向量乘法，两者结果不同，混用会导致坐标系变换错误。投影矩阵输出的w分量是深度透视除法的基础，光栅化器会用 `posClip.xyz / posClip.w` 得到NDC坐标。

### 法线变换的特殊处理

法线向量不能直接乘以模型矩阵进行变换。当模型发生非均匀缩放时（例如x轴缩放2倍、y轴缩放1倍），直接变换法线会导致其不再垂直于对应表面。正确做法是使用**法线矩阵**（Normal Matrix），即模型矩阵左上角3×3子矩阵的逆转置矩阵：

```
float3 normalWS = normalize(mul(normalOS, (float3x3)unity_WorldToObject));
// unity_WorldToObject 已经是 unity_ObjectToWorld 的逆矩阵
```

Unity中直接使用 `unity_WorldToObject` 的转置形式（即 `mul(normal, inverseModelMatrix)`）等效于乘以逆转置矩阵。切线向量（Tangent）则可以直接用模型矩阵变换，因为切线与缩放方向一致，不需要特殊处理。

### 顶点动画实现

顶点动画通过在顶点着色器中修改顶点的模型空间坐标实现几何形状的动态变化，完全在GPU端完成，不消耗CPU和内存带宽。一个经典的旗帜飘动效果公式如下：

```
float wave = sin(posOS.x * _Frequency + _Time.y * _Speed) * _Amplitude;
posOS.y += wave * (posOS.x / _FlagWidth); // 越靠近旗端，振幅越大
```

`_Time.y` 是Unity自动提供的着色器时间变量（单位秒）。顶点动画的关键约束是：**修改顶点位置不会自动更新法线**，如果需要光照正确，必须同步重新计算法线，通常用有限差分法（Finite Difference）在周围采样两个偏移点来近似计算新法线。

### 屏幕空间投影（Screen Space Projection）

将世界空间坐标映射到屏幕UV用于采样屏幕空间纹理（如折射、扫描线特效）时，需要进行透视除法并变换到[0,1]范围：

```
float4 screenPos = ComputeScreenPos(posClip);
// 在片元着色器中: float2 screenUV = screenPos.xy / screenPos.w;
```

`ComputeScreenPos` 输出的 `w` 分量保留了透视深度，必须在片元着色器中用 `VPOS` 或手动除以 `w` 才能得到正确UV。如果在顶点着色器中提前做透视除法，插值过程会因为线性插值与透视校正插值的差异产生扭曲——这是屏幕空间投影最常见的错误来源。

## 实际应用

**GPU蒙皮（GPU Skinning）**：骨骼动画通过顶点着色器实现，每个顶点存储最多4个骨骼索引（BLENDINDICES语义）和对应权重（BLENDWEIGHT语义），着色器从骨骼矩阵数组中采样并加权混合变换矩阵，最终变换顶点位置。Unity的Standard着色器在开启蒙皮时自动使用带`SKINNED_MESH`变体的顶点着色器。

**视差遮蔽中的切线空间构建**：顶点着色器负责计算从切线空间到世界空间的TBN矩阵（Tangent-Bitangent-Normal），将切线向量（Tangent.xyz）和法线叉乘得到副切线（Bitangent），并将视线方向转换到切线空间传给片元着色器，从而使片元着色器能高效地进行高度图采样偏移。

**基于深度的软粒子**：顶点着色器输出裁剪空间坐标后，使用`ComputeScreenPos`计算屏幕UV，片元着色器再采样深度缓冲，通过比较粒子深度与场景深度实现边缘软化。此技术要求顶点着色器正确传递屏幕空间坐标且不提前执行透视除法。

## 常见误区

**误区一：将法线当做普通向量直接用MVP矩阵变换**。法线只需变换到世界空间（或视图空间），绝对不能乘以投影矩阵。更关键的是，非均匀缩放模型时必须用逆转置矩阵，而非模型矩阵本身。许多初学者在模型等比缩放时这个错误被掩盖（等比缩放的法线矩阵等于缩放归一化后的模型矩阵），一旦出现非等比缩放立即暴露问题。

**误区二：在顶点着色器中执行透视除法后再传递屏幕坐标**。顶点着色器的输出在传递给片元着色器之前会经过光栅化器的透视校正插值。若提前做了 `xy/w` 的操作，后续插值将变为线性插值而非透视正确插值，导致屏幕空间纹理在透视角度下出现可见的变形扭曲。正确做法是保留 `w` 分量，在片元着色器中完成除法。

**误区三：认为顶点着色器修改顶点位置会影响碰撞体**。GPU端的顶点动画（如顶点着色器实现的草地弯曲）只改变渲染几何形状，对CPU端的物理碰撞系统完全没有影响。需要碰撞跟随动画时，必须在CPU端额外维护碰撞体数据，或使用物理模拟替代纯顶点着色器动画。

## 知识关联

顶点着色器编写依赖HLSL基础中的向量/矩阵运算、语义（Semantics）声明和常量缓冲区（CBuffer）语法。MVP矩阵、空间变换和法线矩阵推导涉及线性代数中的仿射变换和逆转置矩阵的几何意义。

学习顶点着色器后，可以进入**曲面细分着色器**（Tessellation Shader）——曲面细分在顶点着色器之后执行，Hull Shader消耗顶点着色器的输出并生成控制点数据，能将低模细分为高模以添加更多几何细节。同样，**几何着色器**接收顶点着色器（或曲面细分阶段）输出的完整图元（三角形、线段），可以在运行时增减顶点，实现法线可视化调试、阴影体生成等顶点着色器单独无法完成的效果。