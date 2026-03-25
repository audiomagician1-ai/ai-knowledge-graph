---
id: "vfx-shader-hologram"
concept: "全息效果"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 44.5
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---



# 全息效果

## 概述

全息效果（Hologram Effect）是一种通过Shader模拟科幻电影中蓝色半透明投影图像的视觉技术，其核心由三个叠加层构成：**扫描线（Scanline）**、**噪声扰动（Noise Distortion）** 和 **菲涅尔边缘光（Fresnel Edge Glow）**。与真实全息投影不同，这种Shader并不依赖物理光波干涉，而是通过片元着色器中的数学函数欺骗人眼，令实体三维模型看起来像电子投影光场。

该效果最早在游戏工业中被广泛使用是在2007年前后，随着《光晕3》《质量效应》等科幻AAA游戏的发布而普及，成为UI地图投影、NPC对话立体成像等场景的标配视觉语言。其重要性在于它是一种典型的**多层Pass叠加透明着色器**，掌握它能够理解Alpha混合、深度写入关闭、顶点偏移等多项透明物体渲染的核心机制。

在技术层面，全息效果要求开发者同时处理**时间驱动的动态效果**（扫描线随时间滚动）、**UV空间的噪声采样**（产生图像抖动）以及**基于观察角度的菲涅尔系数**（边缘发光），三者缺一会导致效果失真。

---

## 核心原理

### 1. 扫描线层（Scanline Layer）

扫描线通过对片元的世界坐标Y轴（或裁剪空间Y轴）进行周期性采样生成。具体公式如下：

```
scanline = sin(posY * frequency + _Time.y * scrollSpeed)
scanline = (scanline * 0.5 + 0.5)  // 映射到 [0, 1]
scanline = step(threshold, scanline) // 二值化为条纹
```

其中 `frequency` 控制条纹密度，典型取值为 **20～80**；`scrollSpeed` 控制扫描滚动速度，建议值为 **0.5～2.0**（单位：世界单位/秒）。`_Time.y` 是Unity Shader内置的时间变量（单位秒），是驱动扫描线动态滚动的关键。仅使用固定UV而不使用时间变量，会让扫描线静止，立即丢失"投影感"。

除常规等间距扫描线外，还可以叠加一条**快速移动的亮条（Glitch Scan）**，其频率约为主扫描线的 **3～5 倍**，Alpha值较高，模拟CRT显示器的刷新扫描头。

### 2. 噪声扰动层（Noise Distortion）

全息图像并不完美清晰，需要用噪声函数在UV坐标或顶点位置引入扰动。最常用的方案有两种：

- **Texture噪声**：预烘焙一张灰度噪声图（建议分辨率 64×64 或 128×128），在片元着色器中以 `uv + _Time.y * noiseSpeed` 为采样坐标，将采样值乘以 `noiseIntensity`（典型值 **0.02～0.05**）后叠加到最终颜色。
- **数学噪声（Fract-Sin噪声）**：`frac(sin(dot(uv, float2(12.9898, 78.233))) * 43758.5453)`，该公式利用正弦函数的高频特性产生伪随机值，无需额外贴图。

噪声层还可以驱动**顶点抖动（Vertex Jitter）**——在顶点着色器中沿法线方向偏移顶点位置，偏移量由噪声采样驱动，让整个模型轮廓不定期"颤动"，模拟信号干扰。

### 3. 菲涅尔边缘光层（Fresnel Edge Glow）

菲涅尔项公式为：

```
fresnel = pow(1.0 - saturate(dot(normalWS, viewDirWS)), fresnelPower)
```

`fresnelPower` 控制边缘光的硬度：值为 **1** 时边缘光非常柔和且蔓延至整个表面；值为 **4～6** 时边缘光集中在轮廓线附近，全息效果常用值为 **2～3**。最终菲涅尔值与全息主色（通常为 `float3(0.3, 0.8, 1.0)` 的青蓝色）相乘，叠加到输出颜色。

菲涅尔层与扫描线层的叠加方式建议使用 **Additive（加法混合）** 而非 Alpha混合，这样边缘越亮、越发光，更符合发光投影的物理直觉。

### 4. Alpha与深度控制

全息Shader必须关闭深度写入（`ZWrite Off`），并启用加法或透明混合（`Blend SrcAlpha One` 或 `Blend One One`）。最终Alpha值由以下三项组合：

```
alpha = baseAlpha * scanline * (1 + fresnel * fresnelAlphaBoost)
```

其中 `fresnelAlphaBoost` 取 **0.5～1.5**，使边缘处更不透明，中心更通透。

---

## 实际应用

**游戏UI中的地图投影**：在桌面地图投影场景中，全息Shader施加于一个低多边形的地形Mesh，扫描线方向沿世界Y轴向上滚动，速度约为 **1.5单位/秒**，噪声强度设为 **0.03**，搭配 `Blend One One` 让地图半透明叠加在桌面材质上而不遮挡桌面细节。

**NPC对话立体成像**：角色模型附上全息材质后，`fresnelPower` 设为 **2.5**，主色调为 `(0.2, 0.9, 1.0)` 的冷青色，并添加一条每隔 **3秒** 触发一次的快速扫描亮条动画（通过 `frac(_Time.y / 3.0)` 触发），使人物轮廓发光并带有间歇性干扰感。

**建筑蓝图显示**：建筑预览模型启用全息效果时，扫描线频率提高至 **50**，噪声扰动减弱至 **0.01**（追求清晰感），菲涅尔功率调至 **4**，使建筑边缘呈现锐利的蓝白轮廓，内部保持高透明度，整体视觉上像工业CAD投影。

---

## 常见误区

**误区一：扫描线使用UV的V坐标而非世界坐标Y轴**
若以模型UV的V坐标驱动扫描线，不同模型的UV展开方式不同，会导致球体、柱体等模型上扫描线密度不均匀、方向混乱。正确做法是在顶点着色器中传递世界坐标 `positionWS.y`，在片元着色器中以此作为扫描线的采样输入，保证所有模型的扫描线都在同一世界高度对齐，视觉上保持水平一致。

**误区二：以为关闭ZWrite会自动解决透明排序问题**
`ZWrite Off` 仅阻止全息物体写入深度缓冲，但它本身仍会受深度测试影响。当场景中有多个全息物体互相穿插时，若不按距离排序或不使用OIT（Order-Independent Transparency）方案，会出现物体互相遮挡不正确的撕裂现象。Unity中可通过设置 `Queue = Transparent+1` 等方式调整渲染队列顺序来缓解此问题。

**误区三：菲涅尔直接对切线空间法线计算**
`dot(normalWS, viewDirWS)` 要求两者都在**世界空间（World Space）**中计算。若对法线贴图采样后忘记将切线空间法线转换到世界空间，直接与世界空间视角向量做点积，菲涅尔分布会出现明显错误，在模型侧面产生异常的亮斑或暗区。

---

## 知识关联

**前置概念：边缘光（Rim Light / Fresnel）**
全息效果的菲涅尔层直接复用了边缘光Shader中 `pow(1 - dot(N, V), power)` 的计算公式。全息效果在此基础上将菲涅尔值同时驱动颜色亮度和Alpha透明度，而不仅仅驱动颜色，这是与单纯边缘光的关键区别。

**后续概念：护盾Shader（Shield Shader）**
护盾效果在全息效果的三层结构上新增了**碰撞点波纹扩散（Hit Ripple）**机制，需要通过传递碰撞世界坐标到Shader中，计算片元与碰撞点的距离并驱动圆形扫描波。可以理解为护盾Shader是全息扫描线的"极坐标版本"，其菲涅尔和噪声部分的参数体系与全息效果完全共享，因此全息效果是学习护盾Shader的直接技术前提。