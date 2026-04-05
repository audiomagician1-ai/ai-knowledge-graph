---
id: "3da-tex-emissive"
concept: "自发光贴图"
domain: "3d-art"
subdomain: "texturing"
subdomain_name: "纹理绘制"
difficulty: 2
is_milestone: false
tags: ["效果"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
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



# 自发光贴图

## 概述

自发光贴图（Emissive Map）是一种用于模拟物体自身发出光亮效果的纹理通道，它告诉渲染引擎"这个表面本身在发光，不需要外部光源照射"。与BaseColor贴图依赖场景灯光才能显现颜色不同，自发光贴图中的白色区域无论场景有多黑暗都会保持可见亮度，常见于LED显示屏、霓虹灯管、魔法符文、发光眼睛、武器能量槽等视觉元素。

自发光贴图在实时渲染管线中属于PBR（基于物理的渲染）材质系统的补充通道，并非PBR核心反射模型的一部分。Unreal Engine在4.0版本（2014年）全面引入PBR工作流时，将Emissive通道定义为HDR输出，支持超过1.0的强度值（最高可达数千），配合Bloom后期效果实现真实的光晕溢出。这意味着自发光贴图不仅仅是"发光的颜色"，它的像素值直接决定发光强度的量级。

理解自发光贴图的价值在于它能以极低的性能成本模拟动态光源的视觉感受。一个场景中如果每盏霓虹灯都放置实时点光源，渲染成本会线性叠加；而将灯管本身设置Emissive贴图，再配合Lumen或屏幕空间GI捕捉其间接照明，可以大幅降低Draw Call与光照计算开销。

---

## 核心原理

### 自发光贴图的数值含义

自发光贴图在渲染引擎中以线性色彩空间存储，而非sRGB空间——这一点与BaseColor贴图不同，导入时必须关闭sRGB选项，否则引擎会对其进行两次伽马校正，使发光颜色失真变深。像素的RGB值代表光线辐射度方向：纯黑（0, 0, 0）表示该区域不发光，纯白（1, 1, 1）在引擎中为标准亮度基线，而Unreal Engine中常用的霓虹效果往往将Emissive倍增系数设为10到50之间，超过1.0的HDR值只能存储于EXR或HDR格式贴图中，普通8bit PNG的数值上限仍为1.0。

### 遮罩驱动的工作方式

自发光贴图在制作上通常分为两层结构：**发光遮罩（Emissive Mask）** 和 **发光颜色（Emissive Color）**。发光遮罩是一张灰度图，定义"哪里发光、发多强"；发光颜色则决定光的色相。在材质编辑器中，两者相乘（Mask × Color × Intensity）得到最终Emissive输出值。这种拆分的好处是：制作者可以用一张遮罩贴图配合多个颜色参数，在运行时切换霓虹灯的色彩（如游戏中玩家自定义UI颜色），而无需重新绘制贴图。

### 与Bloom后处理的联动

Bloom（光晕）效果是自发光贴图视觉表现的关键伙伴。Bloom的阈值（Threshold）通常设置为1.0，即只有亮度超过1.0的像素才会产生向外扩散的光晕。因此在制作LED屏幕时，屏幕内容的自发光强度设为5到15能产生清晰光晕；而屏幕边框的金属框架Emissive值保持为0，两者形成对比，视觉层次更清晰。如果Emissive强度设为0.5却期望有光晕效果，这在物理上是不正确的，Bloom不会响应低于阈值的像素。

### 魔法效果的动态自发光

对于游戏中的魔法符文或能量护盾，自发光贴图常与动画纹理或程序化噪声结合。具体做法是将UV坐标随时间偏移（Panner节点），或将一张Emissive流动贴图与角色的法线流向叠加，实现能量在表面流动的视觉效果。此时Emissive贴图本身通常只存储0到1范围内的灰度遮罩形状，真正的颜色和强度由材质参数实时控制，这样美术可以在不修改贴图的情况下调整魔法的颜色风格。

---

## 实际应用

**赛博朋克风格城市场景**：建筑立面的广告牌需要制作自发光贴图，广告内容区域的Emissive值设为8到20，广告牌金属边框的Emissive为0，地面接收Emissive的间接反射需要开启Lumen或烘焙光照图。

**游戏角色的发光眼睛**：眼球贴图中，虹膜区域单独绘制白色Emissive遮罩，配合发光颜色（如鬼魂蓝#4FC3F7）设强度为3，加上Bloom后角色眼睛在黑暗场景中清晰可辨，不需要额外放置点光源跟随角色移动。

**武器能量槽/充能状态**：剑身的能量纹路使用一张512×512的Emissive遮罩贴图，程序员通过材质参数控制发光强度从0渐变到15，实现武器"蓄力充能"的视觉反馈。玩家充能时Emissive增强，Bloom扩散，整个效果仅靠贴图与材质参数驱动，对性能几乎无额外消耗。

**UI屏幕与平板显示**：游戏中的计算机屏幕、雷达面板通常将屏幕内容绘制为Emissive贴图，让屏幕在黑暗房间中仍然"亮着"。屏幕内容可以是静态截图，也可以是渲染目标（Render Target）动态更新。

---

## 常见误区

**误区一：Emissive贴图就是自带光照的BaseColor**
两者根本不同。BaseColor定义反射颜色，在完全黑暗的场景中BaseColor贴图的内容完全不可见；Emissive定义自辐射颜色，在完全黑暗的场景中仍然可见。在Substance Painter中误将自发光颜色画进BaseColor通道，会导致模型在引擎里"亮着"的区域在光照下变成过曝白斑，因为那块区域同时接收了外部光照又叠加了BaseColor的高亮值。

**误区二：Emissive贴图会自动照亮周围物体**
在实时渲染中，自发光贴图本身不产生实时光源，它只影响自身表面的视觉亮度。要让Emissive物体真正照亮旁边的地板，必须在Unreal Engine中开启`Emissive for Static Lighting`（烘焙场景）或使用Lumen动态全局光照，否则发光的霓虹灯对旁边的墙壁毫无影响。

**误区三：Emissive贴图越亮越好**
过高的Emissive强度会导致Bloom过度扩散，使场景泛白、画面浑浊，尤其在HDR显示器上表现更加明显。合理的做法是根据光源类型校准：室内LED屏幕通常Emissive强度为5到15；室外太阳能量级的光源才需要超过1000的Emissive值。无限制地提升强度还会导致Lumen GI采样溢出，反而使间接光照计算出现白色噪点。

---

## 知识关联

自发光贴图以BaseColor贴图为基础前提：理解BaseColor如何定义表面的反射颜色，才能清楚Emissive通道为什么需要在线性空间工作而不能走sRGB管线。两张贴图在Substance Painter中各自对应独立的绘制层，发光区域往往需要先将BaseColor设为接近纯黑（避免接受场景灯光产生双重亮度），再在Emissive层叠加发光颜色。

在PBR材质体系中，Emissive通道与Metallic（金属度）、Roughness（粗糙度）的交互较少，但发光区域的Roughness设置影响Bloom光晕的清晰度——高Roughness表面的Emissive在部分延迟渲染管线中Bloom扩散会偏柔，低Roughness（光滑表面）的Emissive光晕边缘更锐利。掌握自发光贴图的制作后，可进一步探索Unreal Engine中的材质函数封装，将Emissive强度、颜色、动画参数统一暴露为材质实例参数，供关卡美术在场景中统一调控而不需要反复修改贴图本体。