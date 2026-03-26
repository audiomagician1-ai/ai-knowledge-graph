---
id: "cg-surface-shader"
concept: "表面着色器"
domain: "computer-graphics"
subdomain: "shader-programming"
subdomain_name: "Shader编程"
difficulty: 2
is_milestone: false
tags: ["引擎"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---

# 表面着色器

## 概述

表面着色器（Surface Shader）是Unity引擎在2009年版本中引入的一种高级着色器抽象机制，它并非独立的GPU着色器类型，而是Unity编译器的预处理层——开发者编写描述材质表面属性的代码，Unity自动将其展开为包含完整光照计算的顶点/片元着色器HLSL代码。这意味着一份不足50行的表面着色器代码，在编译后会自动生成数百行针对不同光照模式（前向渲染、延迟渲染）和阴影Pass的完整着色器代码。

表面着色器使用`.shader`文件格式编写，代码放置在`CGPROGRAM`块中，并通过`#pragma surface surf Standard fullforwardshadows`这类编译指令触发展开机制。其中`surf`是开发者自定义的表面函数名，`Standard`指定内置的基于物理的光照模型（PBR），`fullforwardshadows`则告诉Unity生成完整的阴影支持代码。

表面着色器的价值在于它将Albedo、Normal、Metallic、Smoothness等PBR材质属性与光照积分计算彻底解耦。开发者只需填充`SurfaceOutputStandard`结构体的字段，光照模型如何将这些属性与场景光源结合计算最终颜色，完全由Unity的自动展开机制处理，无需手写每个光源的衰减、阴影采样和球谐光照（Spherical Harmonics）接收代码。

## 核心原理

### SurfaceOutputStandard 结构体与输出约定

表面函数的输出类型决定了使用哪套光照模型。`SurfaceOutputStandard`对应Unity的Standard（金属工作流）光照模型，其关键字段包括：`Albedo`（基础色，float3）、`Normal`（切线空间法线，float3）、`Emission`（自发光，float3）、`Metallic`（金属度，0-1范围float）、`Smoothness`（光滑度，0-1范围float）、`Occlusion`（环境遮蔽，float）和`Alpha`（透明度，float）。若使用高光工作流则改用`SurfaceOutputStandardSpecular`，其中`Metallic`字段被替换为`Specular`（float3，描述高光颜色）。

表面函数的签名固定为`void surf(Input IN, inout SurfaceOutputStandard o)`，其中`Input`是开发者自定义的输入结构体，可以声明`uv_MainTex`获取主纹理UV坐标，声明`float3 worldPos`获取世界空间顶点位置，声明`float3 worldRefl`获取反射向量——这些特殊名称由Unity的展开器自动识别并注入正确的插值数据。

### 自动生成的Pass结构

Unity的表面着色器展开器会根据渲染管线设置自动生成多个Pass。对于前向渲染路径，至少生成`ForwardBase` Pass（处理主方向光、环境光、第一个点光源、球谐光照）和`ForwardAdd` Pass（处理额外的逐像素光源，每个光源独立调用一次）。对于延迟渲染路径，生成`Deferred` Pass将材质属性写入G-Buffer的四个RenderTexture（Albedo+Occlusion、Specular+Smoothness、Normal、自发光+光照）。此外还自动生成`ShadowCaster` Pass用于深度图渲染，这是手写着色器经常遗漏的部分。

### 编译指令的控制粒度

`#pragma surface`指令后可附加多个修饰词精确控制代码展开行为。`noambient`禁止环境光计算以节省指令数；`noforwardadd`删除ForwardAdd Pass，将额外光源降级为逐顶点计算；`addshadow`在自定义顶点修改函数存在时重新为阴影Pass生成顶点变换代码；`vertex:vert`指定自定义顶点函数名，可在表面函数执行前修改顶点位置实现顶点动画。通过`approxview`近似视角方向计算可在移动端减少单位约20%的数学运算量。

## 实际应用

**角色皮肤材质**：在`surf`函数中，从三张纹理分别采样Albedo、法线贴图和Smoothness/Metallic贴图，将法线贴图解码后（`UnpackNormal`函数）赋值给`o.Normal`，Smoothness存储在Metallic贴图的Alpha通道中。整个函数体约10行代码，Unity自动处理次表面散射近似（若光照模型选用`SkinShading`扩展）与阴影接收。

**溶解效果**：通过`clip()`函数在surf内根据噪声纹理的采样值丢弃像素，`clip(tex2D(_NoiseTex, IN.uv_NoiseTex).r - _Cutoff)`这一行代码即可实现。由于表面着色器自动为ShadowCaster Pass展开了相同的clip逻辑，溶解边界的阴影形状也会正确更新，而手写着色器需要在ShadowCaster中重复这段代码。

**交互式雪地覆盖**：在Input结构体中声明`float3 worldNormal`，在surf函数中计算`dot(IN.worldNormal, float3(0,1,0))`的值来混合雪白色与基础颜色，同时调整Smoothness值。利用表面着色器对世界空间法线的自动插值，无需手动在顶点着色器和片元着色器间传递法线数据。

## 常见误区

**误区一：认为表面着色器性能优于手写片元着色器**。表面着色器展开后包含完整的多Pass结构和所有光照特性，对于只需简单效果（如UI特效、粒子）的场合，其生成代码远超实际需求。Unity官方文档明确指出，表面着色器主要针对"需要与场景光照交互的不透明或半透明物体"，对于不需要动态光照的情况，手写无光照片元着色器的性能更高。

**误区二：认为自定义顶点函数`vertex:vert`中可以随意修改法线方向**。表面着色器的展开器在前向渲染BasePass中通过切线空间矩阵将surf函数输出的切线空间法线转换到世界空间参与光照计算。若在顶点函数中修改了顶点法线但未同步修改切线（`v.tangent`），切线空间矩阵将产生错误，导致法线贴图效果偏斜。正确做法是同步旋转`normal`和`tangent`字段。

**误区三：将表面着色器用于URP或HDRP管线**。表面着色器仅在Built-in渲染管线中受支持，在URP中`#pragma surface`指令会被忽略或报错。Unity在2020年已明确表示不会为URP/HDRP添加表面着色器支持，迁移新管线时需改用ShaderGraph或手写URP的`UniversalForward` Pass结构。

## 知识关联

学习表面着色器需要理解片元着色器中的纹理采样（`tex2D`）、坐标插值和`clip()`透明裁剪的概念，因为这些操作直接在surf函数体内使用，只是开发者不再需要手写光照积分部分。表面着色器的`SurfaceOutputStandard`结构体中Metallic和Smoothness的物理含义，来自Cook-Torrance BRDF模型——理解Roughness参数如何控制GGX法线分布函数的波瓣宽度，有助于在surf函数中正确设置Smoothness值（Smoothness = 1 - Roughness）。

掌握表面着色器后，迁移到ShaderGraph的学习成本极低：ShaderGraph中的PBR Master节点（Built-in管线）和Lit Master节点（URP）的输入端口与`SurfaceOutputStandard`的字段完全对应，只是由连线代替了赋值语句。若需要深入优化性能或实现延迟渲染中不支持的半透明效果，则需转向手写顶点/片元着色器，此时表面着色器自动展开的代码可作为参考起点——Unity允许通过`Show generated code`按钮在Inspector中查看完整的展开结果。