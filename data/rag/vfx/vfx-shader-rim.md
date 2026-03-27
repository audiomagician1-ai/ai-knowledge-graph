---
id: "vfx-shader-rim"
concept: "边缘光"
domain: "vfx"
subdomain: "shader-vfx"
subdomain_name: "Shader特效"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.1
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 边缘光（Rim Light Shader）

## 概述

边缘光（Rim Light）是一种基于视线角度与表面法线夹角来计算光照强度的Shader技术，其核心公式为 `rimFactor = 1 - saturate(dot(normalWS, viewDir))`，当摄像机视线方向与表面法线接近垂直时，rimFactor趋近于1，产生高亮边缘；当视线正对表面时，rimFactor趋近于0，边缘消失。这种特性使得物体轮廓处会自然产生一圈发光效果，视觉上仿佛角色背后有一道逆光照射。

边缘光技术源于电影摄影中的"轮廓光"（Rim Lighting）布光手法，摄影师在被摄主体背后放置强光源以分离主体与背景。2000年代初期，游戏引擎开始将这一概念移植到实时渲染领域，早期的实现出现在《合金装备》系列等第三人称游戏中，用于增强角色在复杂背景下的可读性。在现代游戏中，边缘光已成为角色受击反馈、技能选中提示、队友标注等交互状态表达的标准手段，不依赖额外的UI元素就能传递信息。

在Shader特效体系中，边缘光的难度仅为2/9，计算成本极低，只需一次点积运算即可得到基础遮罩，但其视觉表现对游戏体验的提升非常显著，因此几乎所有3D游戏项目都会实现这一效果。

## 核心原理

### 菲涅尔近似公式

边缘光的数学基础来源于物理上的菲涅尔效应（Fresnel Effect）。完整的菲涅尔方程计算复杂，实时渲染中普遍使用Schlick近似：

```
F = F0 + (1 - F0) * pow(1 - dot(N, V), 5)
```

其中 `F0` 是材质正面的基础反射率，`N` 是世界空间法线，`V` 是归一化视线方向（从顶点指向摄像机）。对于边缘光Shader而言，通常简化为：

```
float rim = pow(1 - saturate(dot(N, V)), rimPower);
```

`rimPower` 参数控制边缘光的宽窄：值为1时边缘光扩散至整个半球；值为4到8时产生较细的轮廓光；值为10以上时边缘光极其纤薄，适合金属质感角色。

### 世界空间 vs 视图空间计算

边缘光的法线和视线向量必须在**同一空间**中计算，否则结果错误。在Unity的ShaderLab / HLSL中：

```hlsl
float3 normalWS = normalize(TransformObjectToWorldNormal(v.normal));
float3 viewDirWS = normalize(_WorldSpaceCameraPos - positionWS);
float rimFactor = pow(1 - saturate(dot(normalWS, viewDirWS)), _RimPower);
float3 rimColor = rimFactor * _RimColor.rgb * _RimIntensity;
```

使用视图空间法线也可行，但世界空间方案与光照系统的整合更自然，尤其是需要叠加方向光效果时。

### 动态边缘光与噪声扰动

静态边缘光在受击或异常状态下缺乏动感。结合前置知识**噪声生成**，可对rimFactor引入时间变化的噪声偏移：

```hlsl
float noise = tex2D(_NoiseTex, uv + _Time.y * _NoiseSpeed).r;
float rimFactor = pow(1 - saturate(dot(N, V) + (noise - 0.5) * _NoiseStrength), _RimPower);
```

噪声扰动范围建议控制在 `_NoiseStrength = 0.1 ~ 0.3`，过大会导致边缘光在正面区域出现噪点。受击闪白可通过在0.2秒内将 `_RimIntensity` 从2.0线性衰减到0来实现时间曲线控制。

## 实际应用

**角色受击反馈**：当角色HP减少时，触发边缘光颜色切换为红色（`_RimColor = (1, 0.1, 0.1, 1)`），同时Intensity在第1帧峰值2.5，经0.15秒指数衰减至0。这一时序参数在《原神》《崩坏：星穹铁道》等米哈游产品中可观察到类似处理。

**敌人/目标选中高亮**：策略游戏和RPG中，被鼠标悬停的单位轮廓显示金黄色边缘光（色温约5500K对应的RGB约为`(1, 0.9, 0.5)`），rimPower设为3以产生较宽的可见范围，确保小角色在远距离也能被识别。

**队友轮廓穿透显示**：角色被墙壁遮挡时，通过深度测试关闭（`ZTest Always`）渲染一层蓝色或绿色边缘光，rimPower设为1使其尽量铺满轮廓，让玩家感知到被遮挡队友的位置，这一应用在《守望先锋》的轮廓描边系统中有原型体现。

**技能充能状态**：角色蓄力或Buff激活时，边缘光颜色与技能属性关联（冰属性为蓝白色，火属性为橙红色），并叠加正弦波脉动：`intensity = baseIntensity + sin(_Time.y * pulseFrequency) * pulseAmplitude`，频率通常设为2～4Hz。

## 常见误区

**误区一：在切线空间中计算点积**
部分初学者在顶点着色器中用切线空间法线与视线方向做点积，导致边缘光形状随UV展开方式发生扭曲，在角色关节等UV接缝处出现明显断裂。正确做法是始终将法线转换到世界空间或视图空间后再计算。

**误区二：忘记对视线方向做归一化**
在片元着色器中，从顶点着色器插值传入的 `viewDir` 向量长度会偏离1.0，若不重新 `normalize`，靠近屏幕边缘的像素其rimFactor会系统性偏小，导致角色侧边的边缘光明显弱于中央，需在片元着色器起始处重新归一化。

**误区三：边缘光与主光源方向无关联**
物理上，边缘光强度应受光源方向影响——背光面的边缘光才真实有意义。完全忽略光源方向会使角色在黑暗场景中的受光面也出现边缘高光，破坏光照一致性。改进方案是乘以一个光照衰减因子：`rim *= saturate(dot(L, N) * rimLightBias + rimLightBias)`，其中 `rimLightBias` 通常取0.5让效果偏艺术化而非完全物理正确。

## 知识关联

**前置知识——噪声生成**：边缘光的静态版本无需噪声，但动态受击状态、能量护盾闪烁等进阶效果需要用噪声纹理对rimFactor进行逐帧扰动，噪声的平铺频率直接影响边缘光的颗粒感粗细。

**后续知识——全息效果**：全息Shader是边缘光的直接延伸，全息效果通常将边缘光作为基础层（产生轮廓发光），再叠加扫描线纹理和菲涅尔透明度，形成半透明发光外壳的视觉效果。掌握 `pow(1 - dot(N,V), power)` 这一核心公式后，全息的透明度梯度计算直接复用此遮罩，学习曲线显著降低。