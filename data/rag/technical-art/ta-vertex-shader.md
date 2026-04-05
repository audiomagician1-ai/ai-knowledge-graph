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
quality_tier: "A"
quality_score: 79.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
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

顶点着色器（Vertex Shader）是GPU可编程管线中第一个可编程阶段，负责对网格的每个顶点执行一次用户自定义的变换程序。它的核心职责是将顶点从模型本地空间（Object Space）经过世界空间（World Space）最终变换到裁剪空间（Clip Space），这一变换链直接决定几何体在屏幕上的投影形状。顶点着色器不能创建或销毁顶点，只能读取并输出同一个顶点的属性。

DirectX 8.0（2000年发布）首次引入了可编程顶点着色器，取代了固定功能管线中的顶点变换单元，使开发者得以用汇编指令自定义顶点处理逻辑。此后，HLSL在DirectX 9中引入，顶点着色器的编程从汇编语法演进为高级语言，`vs_2_0`着色器模型支持最多256条算术指令。现代Shader Model 5.0（DirectX 11）对顶点着色器几乎取消了指令数量上限。

顶点着色器对于技术美术的意义在于：所有基于顶点位移的视觉效果——旗帜飘动、角色蒙皮、水面波纹、卡通描边的外扩——都依赖顶点着色器实现，而无需修改网格资源本身。

---

## 核心原理

### MVP变换矩阵链

顶点着色器最基础的任务是将顶点位置乘以MVP矩阵（Model-View-Projection Matrix）：

```hlsl
output.positionCS = mul(UNITY_MATRIX_MVP, float4(input.positionOS, 1.0));
```

完整变换链为：

**P_clip = M_proj × M_view × M_model × P_local**

- `M_model`：将顶点从模型本地空间变换到世界空间，包含平移、旋转、缩放信息
- `M_view`：将顶点从世界空间变换到摄像机空间（Camera Space），等效于摄像机的逆变换
- `M_proj`：将顶点从摄像机空间变换到裁剪空间，透视投影矩阵会对远处物体产生缩小效果（w分量不为1）

裁剪空间坐标经过透视除法（除以`w`分量）后得到NDC（Normalized Device Coordinates），范围在`[-1,1]`（DirectX的z轴范围为`[0,1]`）。

### 法线变换的特殊处理

法线向量不能直接使用Model矩阵变换，因为当模型存在非均匀缩放时，普通矩阵乘法会使法线方向偏斜，导致光照计算错误。正确做法是使用**法线矩阵（Normal Matrix）**，即模型矩阵左上角3×3子矩阵的逆转置矩阵：

```hlsl
float3 normalWS = normalize(mul((float3x3)transpose(unity_WorldToObject), input.normalOS));
```

`unity_WorldToObject`在Unity中已预先存储了模型矩阵的逆矩阵，转置后即为法线矩阵。切线向量（Tangent）则可以直接使用模型矩阵的3×3部分变换，因为切线与表面共面，不受非均匀缩放的法线偏斜影响。

### 顶点动画技术

顶点着色器中，通过在输出裁剪空间坐标之前修改顶点的本地空间或世界空间位置，可以实现无骨骼的程序化动画。最典型的例子是使用正弦函数模拟植被摆动：

```hlsl
float wave = sin(_Time.y * _WindFrequency + input.positionOS.x * _WindScale);
input.positionOS.x += wave * _WindStrength * input.color.r;
```

其中`_Time.y`是Unity内置的以秒为单位的时间变量，`input.color.r`用顶点颜色红通道控制受风区域的遮罩强度（根部顶点赋值为0，叶梢赋值为1）。这种技术常见于《原神》《塞尔达传说》等游戏的草地系统。

### 屏幕空间投影与深度重建

在顶点着色器中将裁剪空间坐标传递给片元着色器，可以利用`ComputeScreenPos`函数将顶点的裁剪坐标转换为屏幕UV，从而在片元阶段采样屏幕空间纹理（如深度图或反射图）：

```hlsl
output.screenUV = ComputeScreenPos(output.positionCS);
```

片元着色器中用`screenUV.xy / screenUV.w`完成透视除法，得到正确的屏幕空间UV坐标。这是水体、折射、软粒子等效果的底层实现机制。

---

## 实际应用

**卡通描边外扩**：在顶点着色器中沿法线方向将顶点位置向外偏移固定距离，并设置正面剔除（Cull Front），渲染一个比原模型略大的纯色背壳，产生手绘轮廓感：
```hlsl
input.positionOS.xyz += input.normalOS * _OutlineWidth;
```
外扩量`_OutlineWidth`通常在0.01到0.05个单位之间，过大会导致描边在凹陷处穿帮。

**GPU蒙皮（Skinning）**：角色骨骼动画在现代引擎中通过顶点着色器实现，每个顶点存储最多4根骨骼的索引和权重（`BLENDINDICES`和`BLENDWEIGHT`语义），着色器对4个骨骼矩阵进行加权混合：
```hlsl
float4x4 skinMatrix = input.weights.x * _BoneMatrices[input.indices.x]
                    + input.weights.y * _BoneMatrices[input.indices.y]
                    + input.weights.z * _BoneMatrices[input.indices.z]
                    + input.weights.w * _BoneMatrices[input.indices.w];
```

**UV滚动实现流体效果**：对顶点的纹理坐标加上基于时间的偏移，配合流向贴图实现水流、岩浆等效果，计算量仅涉及顶点数（通常远少于像素数），比在片元着色器中偏移UV更高效。

---

## 常见误区

**误区一：混淆法线变换方式**。初学者常直接使用`mul((float3x3)unity_ObjectToWorld, normalOS)`变换法线，当模型存在非均匀缩放（如X轴缩放2倍、Y轴不变）时，变换后的法线会不再垂直于表面。必须使用逆转置矩阵才能保持法线的几何正确性。

**误区二：认为顶点着色器输出的坐标是屏幕坐标**。顶点着色器输出的`SV_POSITION`是裁剪空间坐标，GPU在光栅化之前还需要完成透视除法和视口变换两步操作，最终才得到像素坐标。直接在顶点着色器中手动除以`w`分量是错误的。

**误区三：在顶点着色器中采样纹理会失效**。HLSL中顶点着色器可以使用`tex2Dlod`采样纹理（需要显式提供mip级别），不能使用`tex2D`，因为后者依赖光栅化阶段计算的偏导数（`ddx`/`ddy`）来自动选择mip级别，而顶点阶段尚未光栅化。

---

## 知识关联

顶点着色器编写以HLSL基础（变量类型、语义声明、内置函数）为前提，特别依赖对`float4x4`矩阵乘法的熟练掌握以及对`SV_POSITION`语义的正确理解。

学习顶点着色器后，**曲面细分着色器**（Hull Shader + Domain Shader）在概念上是其延伸：Hull Shader决定如何细分patch，Domain Shader对细分后的每个新顶点执行类似顶点着色器的位置变换，可以理解为"运行时生成更多顶点后再做顶点着色"。**几何着色器**则接收顶点着色器输出的顶点图元（点、线或三角形），可以生成新的图元或丢弃图元，常用于粒子展开（Billboard）和草地生成，是顶点着色器单顶点处理能力的图元级拓展。