---
id: "ta-custom-lighting"
concept: "自定义光照模型"
domain: "technical-art"
subdomain: "shader-dev"
subdomain_name: "Shader开发"
difficulty: 3
is_milestone: false
tags: ["进阶"]

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


# 自定义光照模型

## 概述

自定义光照模型是指在Shader代码中绕过引擎内置的PBR或Blinn-Phong管线，由开发者手动定义表面对光线的响应方式。与Unity的Standard或Unreal的默认材质球不同，自定义光照模型允许把物理上"错误"但视觉上正确的光照算法写入着色器，例如让暗部保持饱和色彩、让高光产生彩虹色散射，或让布料纤维的高光呈现出椭圆形拉伸。

该领域的实践可追溯至1994年日本动画产业对赛璐珞渲染的数字化需求。Ken Perlin在1985年提出的程序纹理概念为光照函数的可编程化埋下伏笔，而1998年RenderMan着色语言中的`surface shader`接口首次将光照计算完全交还给开发者。在实时渲染时代，Unity的Surface Shader（2009年引入）和HLSL `LightingXXX`函数接口让这一能力进入技术美术的日常工具箱。

对技术美术而言，自定义光照模型的价值在于它是连接"美术想要的效果"与"图形管线实际行为"之间的直接手段。赛璐珞风格游戏《罪恶装备Xrd》的开发团队公开说明，其卡通着色器的核心正是替换了引擎的漫反射计算函数，用一张一维Ramp贴图的查找结果代替兰伯特余弦值，而非依靠后处理描边来模拟。

---

## 核心原理

### 兰伯特到Ramp：漫反射的离散化

标准兰伯特漫反射公式为 `diffuse = max(0, dot(N, L))`，其中 N 是表面法线，L 是归一化光源方向，结果是0到1之间连续的浮点值。自定义卡通光照的关键操作是将这个连续值映射为离散跳变值。最常见的实现是把该浮点值作为U坐标，对一张1×256的Ramp贴图进行`tex2D`采样：

```hlsl
float NdotL = dot(normalize(normalWS), normalize(lightDir));
float halfLambert = NdotL * 0.5 + 0.5; // 映射到[0,1]避免负值截断
float3 diffuse = tex2D(_RampTex, float2(halfLambert, 0.5)).rgb * _LightColor0.rgb;
```

Half Lambert（`NdotL * 0.5 + 0.5`）是Valve在2004年开发《半条命2》时提出的改良，目的是保留球体背光面的形状信息而不让其全部变黑。Ramp贴图采样方法在此基础上进一步给美术提供了逐像素的色彩控制能力。

### 各向异性高光：Kajiya-Kay模型

标准Blinn-Phong高光依赖法线向量，但头发、拉丝金属等各向异性表面的高光实际上由切线方向决定。1989年James Kajiya与Timothy Kay提出的模型用切线T代替法线N参与高光计算：

```hlsl
float sinTH = sqrt(1.0 - pow(dot(tangentWS, halfVec), 2.0));
float dirAtten = smoothstep(-1.0, 0.0, dot(tangentWS, halfVec));
float spec = dirAtten * pow(sinTH, _Shininess);
```

其中 `halfVec = normalize(lightDir + viewDir)`，`_Shininess`控制高光锐度。与各向同性高光的圆形光斑不同，此模型产生的高光沿切线方向拉伸为带状，与头发光泽的物理成因（光在平行角质层表面的衍射）吻合。在Unity中实现时需额外在顶点数据中引入`TANGENT`语义并在片元着色器中重建世界空间切线。

### NPR轮廓光与Rim光的精确控制

Fresnel效应的标准公式由Schlick近似给出：`fresnel = pow(1.0 - saturate(dot(N, V)), _FresnelPower)`，其中V为视线向量，`_FresnelPower`通常设为4或5。在NPR流程中，美术往往不希望Fresnel平滑过渡，而是需要一条宽度可控的硬边轮廓光：

```hlsl
float rimMask = step(_RimThreshold, 1.0 - saturate(dot(normalVS, float3(0,0,1))));
```

此处将Fresnel计算移入观察空间（View Space），使用法线Z分量的补值来定义"朝向屏幕边缘"的程度，再用`step`函数产生硬截断。将`_RimThreshold`从0.3调整到0.8可以直观地控制轮廓光宽度，这是Fresnel公式的幂次调节无法精确对应的行为。

---

## 实际应用

**赛璐珞游戏角色**：《原神》的角色着色器在DiffuseRamp基础上加入了一张`_LightMap`（RGBA四通道），其中R通道存储高光强度阈值，G通道存储高光类型（金属/非金属），A通道存储描边宽度权重。这使得同一套自定义光照函数可以驱动布料、皮革、金属等不同材质的差异化表现，而无需切换着色器Pass。

**拉丝金属材质**：在UE5的材质编辑器中，通过将Kajiya-Kay各向异性高光节点接入自定义光照输出，并在切线贴图上绘制环形或径向的切线流向，可以实现表盘上常见的同心圆拉丝效果。关键参数`AnisotropyRotation`（各向异性旋转角）需要逐像素从切线贴图中读取，而非使用全局统一值。

**皮毛（Fur Shell）着色**：通过在自定义光照中加入基于切线的前向散射项 `scatter = pow(max(0, dot(lightDir, -viewDir)), _ScatterPower)`，可以模拟光线穿透毛发后向观察者方向散射的效果，使毛发在逆光时产生发光的"光晕边缘"。

---

## 常见误区

**误区1：认为Half Lambert在物理上更正确**
Half Lambert（NdotL × 0.5 + 0.5）是一种视觉欺骗手段，它让背光面保持可见度的代价是违反能量守恒——对半球积分后其总能量输出高于标准Lambert。这意味着Half Lambert不能直接用于需要烘焙GI的写实项目，因为它会导致间接光照比直接光照更亮的错误结果。

**误区2：各向异性效果只需旋转UV即可实现**
旋转UV能改变贴图纹理的方向，但无法改变高光的物理行为。各向异性高光的拉伸程度由切线向量与半角向量的夹角余弦值决定（Kajiya-Kay中的`dot(T, H)`项），若仅旋转UV而不修改切线向量，高光形状不会随之改变，只有贴图内容会旋转。

**误区3：Ramp贴图采样需要使用双线性过滤**
对于卡通着色器，Ramp贴图的采样过滤模式应设为`Point`（最近邻），而非默认的`Bilinear`。双线性过滤会在Ramp的颜色跳变边界处产生1-2像素的模糊过渡，破坏硬边风格。若确实需要可控的柔和过渡，应在Shader代码中用`smoothstep`精确定义过渡宽度，而不是依赖纹理过滤的副作用。

---

## 知识关联

自定义光照模型建立在**片元着色器编写**的基础上，特别依赖对`SV_Target`输出、纹理采样函数`tex2D`/`SAMPLE_TEXTURE2D`以及向量点积运算的熟练运用。掌握片元着色器中坐标空间变换（世界空间、观察空间、切线空间的互相转换）是正确实现Kajiya-Kay各向异性模型的前提。

从自定义光照模型出发，下一个进阶方向是**皮肤材质**。皮肤的次表面散射（SSS）可以视为自定义光照的特殊扩展——它在标准漫反射基础上加入了光线在皮肤多层结构中折射后重新出射的模拟，其中最常用的预积分SSS方法同样使用一张二维Ramp查找表（以NdotL和曲率为双轴）来近似真实的散射积分，与本文卡通Ramp的采样结构直接相通。