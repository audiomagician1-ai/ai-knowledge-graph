---
id: "ta-gpu-pipeline"
concept: "GPU渲染管线"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.406
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# GPU渲染管线

## 概述

GPU渲染管线（Graphics Rendering Pipeline）是GPU将三维场景数据转换为二维屏幕像素的固定处理流程。这条流程由NVIDIA、AMD等GPU厂商在硬件层面实现，开发者通过编写Shader程序来控制其中的可编程阶段。理解管线的各个阶段是编写任何Shader代码的前提——无论是HLSL还是GLSL，本质上都是在针对管线的特定阶段插入自定义逻辑。

现代GPU渲染管线的形态基本定型于DirectX 9（2002年）到DirectX 11（2009年）这一时期。DirectX 9引入了可编程顶点着色器和像素着色器，彻底取代了此前固定功能管线（Fixed Function Pipeline）的模式。DirectX 11则在此基础上增加了曲面细分阶段（Tessellation）和几何着色器（Geometry Shader）。目前Unity、Unreal Engine底层都基于这套管线模型运行。

管线对技术美术的意义在于：渲染结果的每一个视觉特性——反射、透明度、描边、扭曲——都对应管线中某个具体阶段的操作。一旦渲染效果出现Bug，能够判断问题属于顶点阶段还是片元阶段，可以将排查时间缩短80%以上。

## 核心原理

### 顶点处理阶段（Vertex Stage）

顶点着色器（Vertex Shader）对网格的每一个顶点执行一次，这是管线中最先经过的可编程阶段。它的核心任务是坐标变换：将顶点从模型本地空间（Object Space）依次变换到世界空间（World Space）、观察空间（View Space），最终变换到裁剪空间（Clip Space）。这个过程用矩阵乘法表达为：

**顶点着色器输出位置 = 投影矩阵 × 视图矩阵 × 模型矩阵 × 顶点本地坐标**

在HLSL中写作 `mul(UNITY_MATRIX_MVP, v.vertex)`，其中MVP即Model-View-Projection三个矩阵的合并。顶点着色器的输出除了位置之外，还可以携带自定义插值数据（如UV坐标、顶点颜色、法线方向）传递给后续阶段。

### 光栅化阶段（Rasterization Stage）

光栅化是管线中唯一完全固定、不可编程的核心阶段，由GPU硬件自动完成。它将顶点着色器输出的几何图元（通常是三角形）转化为屏幕上的离散像素覆盖区域，并对顶点间的插值数据进行线性插值计算。例如，若三角形三个顶点的UV坐标分别为(0,0)、(1,0)、(0,1)，光栅化会计算三角形内部每个像素对应的UV值。

光栅化阶段还执行背面剔除（Back-face Culling）和视锥体裁剪（Frustum Clipping）——超出相机视锥体的三角形在此处被丢弃，这是GPU渲染性能的关键优化来源之一。

### 片元处理阶段（Fragment Stage）

光栅化生成的每个像素候选单元称为片元（Fragment），片元着色器（Fragment Shader / Pixel Shader）对每个片元执行一次，负责计算该位置的最终颜色值。这是实现光照计算、纹理采样、特效的主战场。在Unity的ShaderLab中，顶点着色器写在`vert`函数中，片元着色器写在`frag`函数中，两者通过结构体传递插值数据。

片元着色器的计算开销远高于顶点着色器，因为屏幕上的像素数量（通常100万至800万）远超场景中的顶点数量（通常几千至几十万）。这也是为什么技术美术优化Shader时，首要策略是将计算从`frag`移至`vert`。

### 输出合并阶段（Output Merger Stage）

片元着色器的结果并不直接写入屏幕，而是进入输出合并阶段。这一阶段执行深度测试（Depth Test）——用Z-Buffer记录每个像素的深度值，若当前片元深度大于已有深度则丢弃，实现遮挡关系。透明物体的Alpha混合（Alpha Blending）也在此处发生，按照公式 `输出颜色 = 源颜色 × 源Alpha + 目标颜色 × (1 - 源Alpha)` 与帧缓冲中已有颜色合并。模板测试（Stencil Test）同样在此阶段生效，用于实现描边、遮罩等效果。

## 实际应用

**角色描边效果**需要利用两个管线阶段的配合：第一个Pass中在顶点着色器将顶点沿法线方向向外偏移（扩大模型），在输出合并阶段开启正面剔除（Cull Front）只渲染背面；第二个Pass正常渲染角色正面。这种双Pass描边方案在日式卡通渲染中极为常见。

**溶解特效（Dissolve）**完全在片元着色器中实现：采样一张噪声纹理获得灰度值，与一个0到1之间的`_DissolveAmount`参数比较，使用`clip()`函数丢弃低于阈值的片元。`clip()`在管线层面触发的是片元的提前丢弃，不进入输出合并阶段，因此不产生Alpha混合的排序问题。

**顶点动画（Vertex Animation）**将物体形变计算放在顶点着色器中，例如草地随风摆动：对顶点的X、Z坐标施加基于时间参数`_Time`和顶点世界坐标的正弦函数偏移，整个计算在顶点级别完成，避免了大量片元级别的计算开销。

## 常见误区

**误区一：认为片元着色器直接对应屏幕像素**。实际上片元（Fragment）与像素（Pixel）并不等同。在开启MSAA（多重采样抗锯齿）时，一个屏幕像素会对应多个采样点，产生多个片元；即使不抗锯齿，片元也可能在深度测试或模板测试中被丢弃，永远不会写入屏幕。

**误区二：以为顶点着色器输出的UV坐标会原样传入片元着色器**。光栅化阶段对所有插值数据进行透视校正插值（Perspective-Correct Interpolation），而非简单的线性插值。在透视投影下，若不做透视校正，贴图在靠近摄像机的一侧会产生明显拉伸。这个校正由GPU硬件自动处理，但理解这一点有助于解释为何在某些极端角度下纹理坐标会出现异常。

**误区三：认为Alpha Blend透明和Alpha Test透明都在同一管线阶段处理**。Alpha Test使用`clip()`在片元着色器阶段直接丢弃片元，不写入Z-Buffer，没有排序问题；Alpha Blend则在输出合并阶段与帧缓冲混合，依赖正确的绘制顺序（从后向前）。两者在管线中的位置不同，导致使用场景和优化策略截然不同。

## 知识关联

学习本概念需要具备基础的三维空间变换概念（矩阵乘法、坐标系）以及对Shader是"运行在GPU上的程序"这一基本认知，这些内容在"Shader开发概述"中已有铺垫。

掌握管线各阶段的职责之后，学习**HLSL基础**时会清楚每个内置语义（如`POSITION`、`TEXCOORD0`、`SV_Target`）对应管线的哪个阶段的哪种数据。学习**GLSL基础**时同样适用，两者语法不同但管线模型一致。进入**UE材质编辑器**和**Unity Shader Graph**后，编辑器中的节点连线本质上是可视化地编写顶点着色器和片元着色器的逻辑，理解管线阶段有助于正确使用WorldPosition节点、VertexNormal节点等区分阶段的功能节点，避免将片元阶段才可用的屏幕坐标数据错误地连接到顶点阶段。
