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
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 大气效果

## 概述

大气效果（Atmospheric Effects）是在3D场景中模拟真实大气散射、体积雾、天空及云层等自然现象的视觉技术，核心目标是通过空气透视（Aerial Perspective）营造景深层次感，使远处物体呈现色彩偏蓝、对比度降低、饱和度下降的视觉衰减。这一规律最早由达·芬奇在约1490年的手稿《绘画论》（Trattato della Pittura）中系统描述，他将其命名为"空气透视法"（Prospettiva aerea），并指出物体每增加一定距离，其蓝色分量约增加整体色相偏移量的1/5。

在Unreal Engine 5中，大气效果由三个相互独立又协同工作的组件构成：**SkyAtmosphere**（负责整层大气的物理散射模拟）、**ExponentialHeightFog**（负责地表至中空的体积雾密度控制）、**VolumetricCloud**（负责云层的三维体积渲染）。三者的垂直作用范围各不相同：ExponentialHeightFog主要影响海拔0至2000米内的近地层；SkyAtmosphere控制整个大气柱的散射色调；VolumetricCloud通常设置在海拔1500至8000米的对流层中层。

大气效果的视觉权重在大尺度室外场景中占据举足轻重的地位。Epic Games在2021年发布的《The Matrix Awakens》演示中，大气效果的计算开销约占整体渲染帧预算的18%，足以说明其对最终画质的贡献程度。缺少大气效果的室外场景，远景轮廓与近景轮廓对比度相同，会令场景深度感坍塌，视觉上类似一张缺乏景深的平面照片。

---

## 核心原理

### 瑞利散射与米氏散射的物理机制

大气散射由两种物理机制主导，它们共同决定了天空与雾的色彩（《计算机图形学：原理与实践》，Foley et al., 1995）：

**瑞利散射（Rayleigh Scattering）**由直径远小于可见光波长的气体分子（氮气、氧气）引发，散射强度与波长的四次方成反比：

$$I_{散射} \propto \frac{1}{\lambda^4}$$

其中 $\lambda$ 为光波长。蓝光波长约450 nm，红光波长约700 nm，代入计算可得蓝光散射强度约为红光的 $(700/450)^4 \approx 5.8$ 倍，这正是晴天天空呈蓝色的定量解释。

**米氏散射（Mie Scattering）**由直径与光波长相当的悬浮颗粒（水滴、灰尘、霾）引发，其散射强度对波长的依赖性极低，因此雾和云呈现接近白色或灰色的外观。在Unreal Engine 5的SkyAtmosphere参数面板中，**Mie Scattering Scale**默认值为0.003996，将其提升至0.02以上可显著模拟工业雾霾或沙尘天气，远山轮廓会出现明显的白色光晕扩散。

### 体积雾的指数高度衰减模型

ExponentialHeightFog的密度随高度呈指数衰减，完整公式为：

$$D(h) = \text{FogDensity} \times e^{-\text{FogHeightFalloff} \times (h - \text{FogHeight})}$$

各参数的美术含义如下：

| 参数 | 典型取值范围 | 视觉效果 |
|---|---|---|
| FogDensity | 0.005 – 0.05 | 基础能见度，0.02为晴朗白天参考值 |
| FogHeightFalloff | 0.1 – 0.8 | 值越大雾层越薄贴地，0.2适合山谷晨雾 |
| FogHeight | 场景地面高度 | 雾层基准海拔，单位为虚幻引擎的cm |
| StartDistance | 0 – 5000 cm | 摄像机前方无雾区域，防止画面前景过雾 |

例如，制作山谷清晨薄雾效果时，可将FogDensity设置为0.015，FogHeightFalloff设置为0.25，FogHeight设置为地面以上200 cm，使雾气集中在低洼地带并随高度迅速消散，视觉上形成"雾在脚踝处飘动"的自然感。

**散射分布（Scattering Distribution）**参数取值范围为-1至1：设为0.9时趋向强前散射，逆光拍摄时雾层产生丁达尔光柱效果；设为-0.5时趋向后散射，顺光情况下雾层显现灰暗厚重感，适合阴天或暴风雪场景。

### 云层的噪声叠加与视觉层次

VolumetricCloud组件使用多层噪声纹理的分形叠加（Fractal Noise Compositing）生成云的体积形态，基础噪声（Base Noise）决定云的整体轮廓，细节噪声（Detail Noise）在边缘添加蓬松的卷积细节。云层材质本质上是一张控制**消光系数（Extinction Coefficient）**的3D密度场，光线步进（Ray Marching）算法以每帧64至128步（步进精度越高GPU开销越大）采样沿光线方向的密度积分，计算最终的散射颜色。

视觉层次控制的关键是**云层高度分层**：积云（Cumulus）通常分布在1500至2500米，层云（Stratus）分布在0至2000米，卷云（Cirrus）分布在6000至8000米。在Unreal Engine 5中，通过调整VolumetricCloud的**Layer Bottom Altitude**（层底海拔，默认5 km）和**Layer Height**（层厚，默认8 km）可精确匹配不同云型的自然高度分布。

---

## 关键公式与参数速查

在实际美术工作流中，以下参数组合可快速命中常见天气状态：

```
// 晴朗午后（高能见度，淡薄积云）
ExponentialHeightFog:
  FogDensity = 0.005
  FogHeightFalloff = 0.5
  SkyAtmosphere Mie Scattering Scale = 0.003996

// 清晨山谷薄雾（低海拔浓雾，雾层顶部明显）
ExponentialHeightFog:
  FogDensity = 0.025
  FogHeightFalloff = 0.2
  FogHeight = WorldGroundZ + 100cm

// 沙尘暴/工业霾（全场景能见度压缩至500m以内）
ExponentialHeightFog:
  FogDensity = 0.08
SkyAtmosphere:
  Mie Scattering Scale = 0.025
  Mie Absorption Scale = 0.011
  Rayleigh Scattering Scale = 0.0331（降低以压暗天空）
```

日落时分的色温迁移遵循大气路径长度与散射的关系。当太阳仰角（Sun Elevation）从90°降至0°时，光线穿越大气柱的路径长度从约1倍增加至约38倍（地球大气层标准模型），Rayleigh散射将绝大部分蓝光滤除，剩余的红橙波段构成日落色调。美术人员在UE5中可通过调整DirectionalLight的**Rotation Y轴**从-90°至0°来模拟此过程，同时SkyAtmosphere会自动实时更新天空散射颜色，无需手动关键帧调节天空颜色。

---

## 实际应用

### 视觉层次的"三段式"景深构建

专业环境美术师使用大气效果构建"前景—中景—远景"三段式视觉层次：

- **前景（0–50m）**：无雾，贴图细节和法线贴图完整呈现，饱和度最高，色温最接近直接光源色温。
- **中景（50–300m）**：ExponentialHeightFog开始介入，对比度下降约15%–25%，色调轻微偏向雾的颜色（通常为淡蓝或淡灰）。
- **远景（300m以上）**：SkyAtmosphere的空气透视效果主导，远山的固有色饱和度可降至原值的30%以下，轮廓边缘与天空融合。

例如，《地平线：零之曙光》（Guerrilla Games, 2017）的环境美术团队在GDC演讲中披露，他们对不同距离带分别设置了独立的雾颜色梯度，使近景草地的绿色和远景山脉的蓝紫色形成受控的色相渐变，避免了色彩在某一距离突变的"硬边"问题。

### 天气系统的参数过渡与时间轴驱动

在有动态天气需求的项目中，大气参数通过Sequencer时间轴驱动关键帧动画实现天气切换。关键帧间距建议不小于300帧（以30fps计为10秒），过短的过渡会令玩家察觉天气的"机械切换感"。FogDensity的变化曲线应使用Ease-In-Out缓动，避免线性插值导致的雾层密度突变。

---

## 常见误区

**误区1：将FogDensity设置过高以"快速增加氛围感"**
FogDensity超过0.06时，近景（20m以内）物体会出现明显的雾色污染，贴图细节被遮蔽。正确做法是将**StartDistance**设为200–500 cm，使雾从摄像机前方一定距离才开始积累，保护近景的视觉清晰度。

**误区2：忽略SkyAtmosphere与DirectionalLight的绑定**
SkyAtmosphere需要在组件属性中将**Atmosphere Sun Light**指定为场景的DirectionalLight，否则散射计算不会响应太阳方向变化，日出日落时天空颜色保持静止。许多初次使用UE5的美术人员在新建场景时遗漏此步骤，导致天空颜色与光照方向不匹配。

**误区3：在室内场景保留全局ExponentialHeightFog**
室内场景中全局雾会通过建筑的开口渗入室内，造成室内空间出现不自然的雾蒙蒙感。应在室内场景中将FogDensity设为0，并改用**局部体积雾（Local Volumetric Fog）**配合粒子系统控制室内烟雾或灰尘效果。

**误区4：VolumetricCloud与距离的性能误判**
VolumetricCloud的光线步进开销与视距成正比，而非与云层面积成正比。在摄像机正对云层仰视时，步进路径最短；而接近地平线时步进路径大幅增加，GPU耗时可增加3至5倍。因此在性能敏感的项目中，应在摄像机仰角低于5°时降低步进精度（Sample Count Per Slice从8降至4）。

---

## 知识关联

大气效果的正确设置依赖对**环境光照美术**的深入掌握，二者的交叉点体现在以下两个具体方面：

1. **SkyLight与SkyAtmosphere的捕获关系**：SkyLight的Capture Mode设为**Real Time Capture**时，会将SkyAtmosphere的散射结果实时烘入环境光Cubemap，这意味着大气散射色调会直接影响场景所有物体的环境光颜色。日落时橙红色的SkyAtmosphere会令整个场景的阴影区域偏暖橙，而非保持中性灰——这是物理正确的结果，但若与美术风格目标冲突，需要通过SkyLight的**Tint**参数（偏向蓝色）手动修正。

2. **体积雾与光源的Volumetric Scattering Intensity**：DirectionalLight和SpotLight的**Volumetric Scattering Intensity**参数决定这些光源在体积雾中产生的光轴（God Ray）强度。默认值为1.0；在晨雾穿林场景中，可将DirectionalLight的此参数提升至2.0–3.0以获得明显的丁达尔光柱，但PointLight的此参数在密度较大的雾中极容易过曝，通常应保持在0.3以下。

此外，大气效果与**色调映射（Tone Mapping）**密切相关：UE5默认使用ACES色调映射曲线，该曲线对高亮区域（如太阳盘面、云边缘高光）有较强的压缩，而大气散射产生的大面积中灰亮度区域会被较为线性地映射。美术人员在HDR显示器上预览与在SDR显示器上预览大气效