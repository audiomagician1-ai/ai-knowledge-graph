---
id: "3da-env-atmosphere"
concept: "大气效果"
domain: "3d-art"
subdomain: "environment-art"
subdomain_name: "环境美术"
difficulty: 3
is_milestone: false
tags: ["效果"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "A"
quality_score: 73.0
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 大气效果

## 概述

大气效果（Atmospheric Effects）是指在3D场景中模拟真实大气散射、体积雾、天空及云层等自然现象的视觉技术，其核心目的是通过空气透视（Aerial Perspective）营造景深层次感，使远处物体呈现出色彩偏蓝、对比度降低、饱和度下降的自然现象。这种视觉衰减规律最早由达·芬奇在15世纪的绘画理论中系统描述，他将其称为"空气透视法"（Prospettiva aerea）。

大气效果在3D美术中的重要性在于，它直接影响场景的空间尺度感和情绪基调。一个没有大气效果的室外场景，即便几何体和贴图制作精良，也会因为缺乏空气感而显得"干瘪"。在Unreal Engine 5中，大气效果由**SkyAtmosphere**、**ExponentialHeightFog**和**VolumetricCloud**三个独立组件共同构成，每个组件控制不同海拔高度和视距范围内的视觉表现。

从美术设置的角度来看，大气效果是连接天空光照与地面场景的视觉桥梁，它决定了光线在大气层中的散射方式——包括瑞利散射（Rayleigh Scattering）和米氏散射（Mie Scattering）——这两种物理机制分别解释了天空为何呈蓝色以及云雾为何呈白色或灰色。

---

## 核心原理

### 体积雾（Volumetric Fog）的密度与高度衰减

体积雾的关键参数是**指数高度雾（Exponential Height Fog）**，其密度随高度呈指数衰减，公式为：

> **D(h) = FogDensity × e^(-FogHeightFalloff × (h - FogHeight))**

其中 `h` 为当前高度，`FogHeight` 为雾层基准高度，`FogHeightFalloff` 控制雾密度随高度衰减的速率——数值越大，雾层越薄且贴地。在 Unreal Engine 中，FogDensity 典型值为 0.02 至 0.05 之间；若设置超过 0.1，场景能见度会急剧下降，适合营造浓雾或低能见度的恶劣天气。

体积雾还支持**体积散射颜色（Scattering Distribution）**参数，取值范围 -1 到 1：负值偏向后散射（Backscattering），光源背后的雾呈暗色；正值偏向前散射（Forward Scattering），逆光时雾层产生明亮光晕效果，常见于晨雾或丁达尔效应场景。

### 天空大气（Sky Atmosphere）的散射参数

SkyAtmosphere 组件通过物理模型模拟地球（或外星球）大气层，核心参数包括：

- **Rayleigh Scattering Scale**：控制瑞利散射强度，默认值对应地球标准大气；降低此值会使天空变暗并偏向橙红色，适合模拟火星大气。
- **Mie Scattering Scale**：控制霾（Haze）浓度，数值增大时太阳周围光晕扩散，远山轮廓模糊度增加。
- **Atmosphere Height**：大气层顶部高度，地球默认值约 60 km；对于近未来科幻场景，调高此值可使天空呈现更深邃的深蓝色渐变。

美术人员在设置日落场景时，需将太阳仰角（Sun Elevation）调至接近 0°，此时光线穿越大气层路径最长，Rayleigh 散射将短波蓝光完全过滤，天空和云层呈现橙红色——这是日落色调的物理成因，而非单纯的颜色叠加。

### 云层的视觉层次控制

VolumetricCloud 组件使用**噪声纹理叠加**技术生成体积云形态，通常采用 Worley Noise（低频）+ Perlin Noise（高频细节）的两层叠加结构。关键美术参数包括：

- **Layer Bottom Altitude / Top Altitude**：云层底部和顶部高度，积云（Cumulus）底部通常设置在 600–2000 m，而卷云（Cirrus）设置在 6000–12000 m。
- **Cloud Coverage**：云量，0 表示晴天，1 表示全覆盖阴天；0.3–0.6 是常见的"晴间多云"效果。
- **Shadow Map Resolution**：云层对地面的投影精度，设置过低会导致地面云影边缘呈锯齿状，推荐 512 以上用于大型场景。

---

## 实际应用

### 利用大气效果构建视觉层次

专业环境美术师将场景深度划分为**前景（0–50m）、中景（50–500m）、远景（500m+）**三层。前景层大气效果几乎为零，物体颜色饱和、对比清晰；中景层加入轻微雾霾，明度略升、饱和度降低约 15%–20%；远景层受空气透视影响最强，山脉等地貌元素颜色明显偏向天空色，与天空边界柔化融合。

在《地平线：零之黎明》等开放世界游戏中，美术团队使用**距离雾（Distance Fog）**叠加**高度雾（Height Fog）**的双层雾设置，使玩家站在高处俯瞰时，山谷中的雾气与平地上方的大气散射形成明显分层，极大增强了地形的纵深感。

### 天气状态切换的大气参数过渡

动态天气系统需要在晴天、阴天、雨天三种大气状态之间做参数插值。典型的晴天大气设置中，FogDensity ≈ 0.01，MieScatteringScale ≈ 0.003，而暴雨前的阴天场景中两个参数分别上升至 0.06 和 0.02——密度增加6倍，同时 SkyAtmosphere 的天空颜色饱和度降低，云层 Coverage 推至 0.85 以上，形成压抑的低气压氛围。

---

## 常见误区

### 误区一：体积雾颜色直接使用纯白色

许多初学者习惯将 Fog Inscattering Color（雾散射颜色）设置为纯白色（RGB: 255,255,255），这会导致雾气与天空色调脱节，产生不自然的"奶雾"效果。正确做法是从 SkyAtmosphere 中采样地平线附近的天空颜色，将其作为雾散射颜色的基底，通常偏暖色（日间偏淡橙），并保持明度在 200–230 范围而非纯白。

### 误区二：云层厚度等于云层覆盖面积

Cloud Coverage 参数控制的是云量（天空被覆盖的比例），而不是单朵云的视觉厚度。若要制作厚积雨云（Cumulonimbus），需要同时增大 **Cloud Coverage** 和 **Density Multiplier**，以及扩大 **Layer Bottom 到 Top 的高度差**（可设至 8000 m）。只调高 Cloud Coverage 而不调密度，会得到一片薄薄的卷层云效果，而非具有体积感的暴风云。

### 误区三：大气效果与后处理 Bloom 的叠加顺序混淆

大气散射效果在渲染管线中发生在**几何体渲染阶段**，而 Bloom（泛光）和 Color Grading 在**后处理阶段**。若场景中太阳光晕过于强烈，错误的做法是直接降低 SkyAtmosphere 的太阳强度，正确的做法是先检查后处理体积中的 Bloom Intensity（通常控制在 0.5–1.0 之间）是否过高，避免两个阶段的光晕效果双重叠加。

---

## 知识关联

**与环境光照美术的关联**：大气效果的正确设置依赖于 Directional Light（定向光）的方向与 SkyAtmosphere 绑定——Sky Light 组件的 Real Time Capture 模式会实时捕获大气颜色并将其作为半球光注入场景。若定向光角度与 SkyAtmosphere 中太阳位置不一致，会出现地面阴影方向和天空光来源方向矛盾的穿帮问题，这是环境光照阶段必须解决的依赖关系。

**向上的拓展方向**：掌握大气效果后，美术人员可进一步学习**体积光（Volumetric Light Shafts / God Rays）**和**粒子系统模拟的局部雾效**（如丛林地面薄雾），这些效果需要在体积雾基础上叠加粒子或光束组件，实现更细腻的局部大气控制。同时，大气效果的参数化理解是制作**程序化天气系统**的前提，游戏引擎中的 Blueprint 或材质函数可驱动上述各参数随时间或游戏事件动态变化，实现完整的环境叙事。