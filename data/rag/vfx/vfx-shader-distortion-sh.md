---
id: "vfx-shader-distortion-sh"
concept: "折射扭曲"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 3
is_milestone: false
tags: ["进阶"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 折射扭曲

## 概述

折射扭曲（Refraction Distortion）是一种通过对已渲染场景的纹理进行偏移采样，模拟光线穿过玻璃、水面、热空气等介质时发生弯折的Shader特效技术。其核心操作是获取屏幕空间的场景颜色缓冲（Scene Color Buffer），再用法线图或噪声图驱动UV偏移，从而让"背后"的像素错位显示，产生视觉上的扭曲折射感。

该技术在图形学中源于对斯涅尔定律（Snell's Law）的近似模拟：`n₁·sin(θ₁) = n₂·sin(θ₂)`，其中n₁、n₂分别为两种介质的折射率，θ₁为入射角，θ₂为折射角。在实时渲染中，完整的物理折射计算代价过高，因此折射扭曲以屏幕空间采样偏移作为廉价近似，折射率差值越大，偏移强度越高，例如水的折射率约为1.33，玻璃约为1.5。

在游戏和影视特效中，折射扭曲广泛用于制作水晶球、玻璃瓶、水下视角、火焰热浪、隐身斗篷、魔法传送门等效果。其性能代价远低于光线追踪折射，却能以极低成本产生令人信服的视觉欺骗。

## 核心原理

### GrabPass 与 Scene Color 节点的工作机制

在Unity的Built-in管线中，`GrabPass { "_GrabTexture" }` 指令会在当前物体渲染前将屏幕内容复制到一张名为 `_GrabTexture` 的渲染纹理中，分辨率默认与屏幕一致。URP/HDRP则通过 `_CameraOpaqueTexture`（需在渲染器中开启Opaque Texture选项）或Shader Graph中的 **Scene Color** 节点实现等效功能。Unreal Engine材质中对应节点为 **SceneTexture:SceneColor**。

关键限制：GrabPass只能采样到**当前Pass之前已渲染完成**的不透明物体，因此折射扭曲材质必须设置为透明队列（Queue=Transparent），且渲染顺序必须晚于背景物体。

### UV偏移的驱动方式

折射扭曲的视觉效果完全由UV偏移量决定。标准做法是采样一张切线空间法线图（Normal Map），提取其RG通道作为偏移向量，再乘以强度系数 `_DistortionStrength`：

```
float2 normalSample = tex2D(_NormalTex, uv).rg * 2.0 - 1.0;
float2 offset = normalSample * _DistortionStrength;
float2 distortedUV = screenUV + offset;
float4 sceneColor = tex2D(_GrabTexture, distortedUV);
```

其中 `_DistortionStrength` 通常取值范围为 0.01～0.1，过大会导致采样超出屏幕边界，产生明显的拉伸或黑边伪影。为避免边界问题，可用 `clamp(distortedUV, 0.001, 0.999)` 约束采样坐标。

### 屏幕空间UV的计算

将顶点裁剪空间坐标转换为屏幕UV需要进行透视除法：

```
float4 clipPos = UnityObjectToClipPos(v.vertex);
float4 screenPos = ComputeGrabScreenPos(clipPos);
// 在片元着色器中：
float2 screenUV = screenPos.xy / screenPos.w;
```

注意 `screenPos.w` 是透视除法的关键，若直接使用 `screenPos.xy` 不除以w，在透视相机下会产生错误的近大远小拉伸。Unity内置函数 `ComputeGrabScreenPos` 已对平台差异（DX/OpenGL的Y轴翻转）进行了处理。

### 动态扭曲与时间驱动

静态折射扭曲往往用于玻璃材质；动态扭曲（如热浪、水流）则需结合时间变量 `_Time.y` 滚动法线图UV，或叠加两张不同速度滚动的法线图以增加随机感。双层法线叠加时，第二层偏移量通常为第一层的0.7倍左右，方向错开约45°，可有效消除明显的周期性重复感。

## 实际应用

**水晶/玻璃材质**：采样一张高斯模糊法线图，`_DistortionStrength` 设为0.03～0.05，配合菲涅尔效果控制边缘反射强度，即可制作清透的玻璃瓶或水晶球。

**火焰热浪扭曲**：使用Perlin噪声图（R通道）替代法线图，仅在Y轴方向施加向上的正偏移，同时让噪声图UV以约0.3 units/s的速度向上滚动，模拟热空气上升导致的景象扭曲。火焰区域的Alpha遮罩限制扭曲范围，避免影响火焰以外的区域。

**水下扭曲后处理**：对全屏Quad应用折射扭曲Shader，使用低频大幅度（`_DistortionStrength ≈ 0.08`）法线动画，同时叠加蓝绿色调的色调映射，10行Shader代码即可实现令人信服的水下氛围。

**隐身斗篷效果**：将角色网格的折射扭曲强度设为0.02，法线图使用角色表面的切线空间法线，让背景发生轻微扭曲而非完全消失，比Alpha透明更具科幻感。《半条命2》中的"反重力枪"界面和《英雄联盟》中多个技能特效均使用此类原理。

## 常见误区

**误区一：强度越大效果越好**。许多初学者将 `_DistortionStrength` 调至0.3以上，认为扭曲越剧烈越震撼。实际上超过0.1后，屏幕边缘的采样UV会超出0～1范围，导致纹理Clamp或Repeat模式下产生明显的屏幕边缘图像重复伪影。真实水面折射扭曲在平静状态下强度约为0.02～0.04，只有剧烈波动的水面才会到0.08以上。

**误区二：GrabPass可以采样到同层半透明物体**。GrabPass捕获的是不透明Pass渲染完成后的缓冲区，同处于Transparent队列的其他半透明物体（如粒子、其他玻璃）在GrabPass执行时尚未渲染，因此不会出现在采样结果中。若场景中有多个折射扭曲物体叠加，需通过渲染顺序（`RenderQueue` 数值差异）或分层GrabPass手动管理采样时序。

**误区三：折射扭曲与深度偏差无关**。实际上，当折射物体与背景物体的深度差较小（如薄玻璃紧贴墙面）时，偏移后的UV可能采样到折射物体自身背面的像素，导致出现"自采样"伪影。解决方法是在采样前用深度缓冲对比，若采样点深度小于当前像素深度则回退到未偏移的UV坐标。

## 知识关联

折射扭曲建立在**UV滚动**的基础上：UV滚动提供了对纹理坐标进行时间驱动偏移的基本操作，折射扭曲将偏移目标从普通纹理扩展到了屏幕空间的场景颜色缓冲，偏移量的来源也从简单的 `_Time * _Speed` 升级为法线图的向量信息。**运动矢量**则提供了另一种偏移驱动来源：在拥有运动矢量缓冲的管线中，可以用前一帧与当前帧的运动差值来驱动扭曲，使折射变形与物体运动方向相关联，制作更物理的果冻形变或高速运动拖影折射。

向前延伸，折射扭曲自然引出**菲涅尔效果**：真实介质的折射率随观察角度变化（菲涅尔方程），正视玻璃时折射明显、反射弱，斜视时反射强、折射弱。在Shader中将折射扭曲的贡献权重与菲涅尔项 `pow(1 - dot(N, V), 5)` 相乘，可以让玻璃材质在掠射角度自动降低折射贡献、增加反射高光，从而达到物理正确的半透明介质外观。