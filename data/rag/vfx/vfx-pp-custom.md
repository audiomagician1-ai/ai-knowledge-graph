---
id: "vfx-pp-custom"
concept: "自定义后处理"
domain: "vfx"
subdomain: "post-process"
subdomain_name: "后处理特效"
difficulty: 4
is_milestone: false
tags: ["高级"]

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



# 自定义后处理

## 概述

自定义后处理（Custom Post Processing Pass）是指在渲染管线的图像空间阶段，由开发者编写代码插入自定义的全屏图像处理逻辑，对已完成光栅化的帧缓冲纹理进行二次加工的技术手段。与引擎内置的Bloom、景深等后处理效果不同，自定义后处理允许开发者以Material（材质）或Compute Shader两种方式，将任意图像算法注入到后处理栈（Post Process Stack）中，输出最终呈现给玩家的画面。

在Unreal Engine 4.22版本之前，自定义后处理主要依赖`Blendable`接口和Post Process Volume中的材质槽实现；从4.22和5.x系列起，官方引入了`FSceneViewExtension`扩展类和`AddPass`/`AddFullscreenPass`系列渲染函数，使Compute方式的自定义Pass得以高效融入延迟渲染管线（Deferred Rendering Pipeline）的特定阶段，如`PostProcessing_BeforeBloom`、`PostProcessing_AfterTonemapping`等具名插入点。

掌握自定义后处理的核心价值在于突破引擎预设效果的边界——例如在角色轮廓检测、热成像滤镜、屏幕空间雨滴模拟等需要访问GBuffer（深度、法线、粗糙度等通道）的场景中，内置节点无法满足跨Pass数据访问需求，而自定义Post Process Material可通过`SceneTexture`表达式节点直接采样`SceneDepth`、`GBufferA`（世界法线）等缓冲区内容。

---

## 核心原理

### Material方式：Post Process Material

在材质编辑器中将材质域（Material Domain）设置为`Post Process`，混合模式（Blend Mode）设置为`Opaque`，即可创建一个后处理材质。该材质会以全屏四边形（Fullscreen Quad）覆盖的方式执行，顶点着色器由引擎自动生成，开发者只需编写片元（像素）着色阶段的逻辑。

关键节点是`SceneTexture`，其`Scene Texture Id`参数枚举了可采样的缓冲区类型，常用的包括：
- **PostProcessInput0**：上一个Pass的输出颜色，即当前后处理栈的输入
- **SceneDepth**：线性深度（单位：厘米），值域为`[NearClipPlane, FarClipPlane]`
- **GBufferA**（世界空间法线，xyz分量范围-1到1，w通道存储Per-Object Data）
- **GBufferB**（金属度Metallic、高光度Specular、粗糙度Roughness、着色模型ShadingModelID）

材质被放置到Post Process Volume的`Blendable Materials`数组后，引擎在`r.PostProcessAAQuality`控制的阶段自动执行。通过`Blendable Weight`参数（0.0到1.0）可实现多个后处理材质之间的线性混合，适合制作可渐变的特效过渡。

### Compute Shader方式：FSceneViewExtension

当效果需要随机写入、原子操作或读取当前帧的UAV（Unordered Access View）时，Material方式受限于片元着色器的随机写禁止，必须改用Compute Shader。实现路径为：

1. 继承`FSceneViewExtensionBase`，重写`SubscribeToPostProcessingPass`函数，向对应的`EPostProcessingPass`枚举阶段（如`EPostProcessingPass::MotionBlur`之后）注册回调委托。
2. 在回调函数内调用`FRDGBuilder::AddPass`，描述符（`FRDGPassDesc`）中设置`ERDGPassFlags::Compute`标志，并在Lambda内通过`RHICmdList.SetComputeShader`绑定编译后的`.usf`着色器。
3. 全局着色器以`IMPLEMENT_GLOBAL_SHADER(FMyPostProcessCS, "/Plugin/MyPlugin/Private/MyPostProcess.usf", "MainCS", SF_Compute)`宏完成注册，Dispatch尺寸通常设为`FMath::DivideAndRoundUp(ViewRect.Width(), 8)`乘以`Height/8`的二维线程组。

RDG（Render Dependency Graph）系统负责自动推导Pass间的纹理屏障和内存别名，开发者通过`FRDGTexture*`句柄而非裸RHI指针操作资源，避免手动插入`TransitionResource`调用。

### 着色器中访问GBuffer的坐标系约定

无论Material还是Compute方式，采样屏幕空间坐标时必须注意UE使用的UV原点在左上角，而OpenGL约定为左下角。在`.usf`文件中，通过`SvPosition.xy / View.ViewSizeAndInvSize.xy`计算归一化UV（0到1范围），再乘以`View.BufferSizeAndInvSize.xy`得到缓冲区像素坐标，两者在非全屏视口（如分屏）情况下并不等价，混淆会导致采样偏移。

深度重建世界坐标公式为：

```
float4 ClipPos = float4(UV * float2(2, -2) + float2(-1, 1), DeviceZ, 1);
float4 WorldPos = mul(ClipPos, View.ScreenToWorld);
WorldPos /= WorldPos.w;
```

其中`DeviceZ`从`SceneDepthTexture`采样得到，`View.ScreenToWorld`是引擎每帧上传到GPU的逆视图投影矩阵。

---

## 实际应用

**热成像滤镜**：在后处理材质中通过`SceneTexture:WorldNormal`与`SceneTexture:SceneDepth`重建世界坐标，计算像素距光源的距离映射到冷暖色调（蓝→红）的渐变，再叠加噪声纹理模拟CCD传感器颗粒。整个效果可由一张256×1的渐变LUT纹理和约30个材质节点完成。

**屏幕空间角色轮廓检测**：在Post Process Material中，对`SceneTexture:CustomDepth`进行Sobel算子卷积，采样当前像素及其上下左右相邻四像素（偏移由`View.ViewSizeAndInvSize.zw`提供像素大小）的深度值，相差超过阈值（如5.0厘米）则输出轮廓颜色。此方案无需额外Pass，在单个Material内完成，移动端也适用。

**屏幕空间雨滴**：Compute Pass在每帧以Dispatch(1, 1, 1)的单线程组运行粒子模拟，将200个雨滴粒子的位置和速度写入Structured Buffer，下一个材质Pass读取该Buffer执行SDF（符号距离场）混合渲染，展示了Material Pass与Compute Pass在同一特效中协同工作的典型架构。

---

## 常见误区

**误区一：将后处理材质的输出误以为会自动写回PostProcessInput0**
后处理材质的输出结果会替换当前颜色缓冲，但如果材质中没有将`PostProcessInput0`颜色混入计算结果，原始场景颜色将被完全丢弃。正确做法是在材质的最终输出节点中，将自定义效果颜色与`PostProcessInput0`颜色进行`Lerp`或叠加混合，除非刻意需要全屏替换效果。

**误区二：以为Compute Post Process Pass可以在任意渲染阶段自由插入**
`EPostProcessingPass`枚举只提供了约10个预定义插入点（截至UE5.3），无法插入到GBuffer写入阶段之前，也无法在TAA（Temporal Anti-Aliasing）重投影之后、Tone Mapping之前的任意位置自由插入。如果需要在Tone Mapping前访问线性HDR颜色而非Tone Mapped的LDR颜色，必须明确选用`EPostProcessingPass::BeforeTonemap`而非默认的`AfterTonemap`，两者的颜色值域差异可达数十倍（HDR场景高光区域值可超过100.0）。

**误区三：认为Material方式与Compute方式的性能差异可忽略**
Material方式在像素着色器阶段执行，受限于光栅化流水线，无法利用GPU的共享内存（Shared Memory）和Wave指令。对于需要横跨16×16像素块进行平均亮度统计的操作，Compute方式可在线程组内使用`groupshared float`累加，避免多次全屏纹理读取，性能差距在4K分辨率下实测可达3到5倍。将本应使用Compute的算法强行用Material实现，往往会产生大量冗余采样。

---

## 知识关联

**前置概念：镜头光晕（Lens Flare）**
镜头光晕作为内置后处理特效，本质上是引擎在`PostProcessing_BeforeBloom`阶段对亮斑进行Scatter绘制后合并到颜色缓冲的操作。理解其内部Bloom提取阈值（默认`r.BloomThreshold = -1`代表自动计算）和双边高斯模糊Pass的执行顺序，有助于在自定义Post Process中正确选择插入点——若效果需要在光晕叠加之前介入（如改变光晕颜色），必须注册到Bloom之前的阶段，否则采样到的`PostProcessInput0`已包含光晕叠加结果。

**后续概念：模板缓冲应用（Stencil Buffer）**
自定义后处理的逐像素选择性执行（仅处理特定物体所在区域）常借助模板缓冲实现——物体在Base Pass中以`r.CustomDepth.Stencil`写入自定义模板值（0-255），后处理Pass中通过`SceneTex