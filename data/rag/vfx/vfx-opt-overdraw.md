---
id: "vfx-opt-overdraw"
concept: "Overdraw控制"
domain: "vfx"
subdomain: "vfx-optimization"
subdomain_name: "特效优化"
difficulty: 2
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.424
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# Overdraw控制

## 概述

Overdraw（过度绘制）是指屏幕上同一像素被GPU多次绘制的现象。在半透明粒子特效中，由于粒子必须从后往前排序叠加渲染，每一个覆盖同一屏幕区域的粒子都会触发一次完整的片段着色器计算，使该像素的绘制次数成倍增加。当一个爆炸特效中几十个半透明烟雾粒子同时重叠时，中心区域的像素可能被绘制20次甚至更多。

Fill rate（填充率）是GPU每秒能够渲染的像素总量，是衡量Overdraw压力的核心指标。移动端GPU（如Mali-G77、Adreno 640）的fill rate远低于桌面端，一个中等规模的粒子特效在PC上毫无压力，但在移动设备上却可能因fill rate耗尽而导致帧率骤降至30fps以下。Overdraw控制的目标就是在视觉效果可接受的前提下，将每帧的像素总绘制次数压缩至合理范围。

Overdraw问题在特效优化中独具针对性，因为半透明渲染本身无法使用Early-Z剔除——GPU必须完整执行片段着色器才能完成Alpha混合，这意味着任何像素级别的遮挡关系对半透明粒子都不起作用。这一硬件特性决定了Overdraw的控制只能从粒子的几何形状、粒子数量、发射位置和纹理设计这几个维度入手。

## 核心原理

### Overdraw的量化测量方法

Unity的Frame Debugger和Overdraw可视化模式可以直观呈现每个像素的绘制次数，颜色越亮表示Overdraw越高。Unreal Engine则通过`Shader Complexity`视图显示pass叠加情况，绿色为低Overdraw，红色至白色表示极高Overdraw。

量化Overdraw的基本公式为：

**Overdraw比率 = 总着色像素数 / 屏幕分辨率像素数**

例如屏幕分辨率为1920×1080（约207万像素），一帧中GPU共处理了830万次像素着色，则Overdraw比率为4×，意味着平均每个像素被绘制4次。移动端特效的目标通常是将Overdraw比率控制在2×以下，PC端可放宽至4×以内。

### 粒子Billboard形状裁剪

最直接降低Overdraw的方法是减少每张粒子贴图中透明像素所占的面积比。默认粒子使用正方形Quad，即便火焰纹理四角全为纯透明，这些透明区域仍然会进入片段着色器参与计算，构成无效Overdraw。

解决方案是使用**紧密贴合纹理形状的多边形网格**替代正方形Quad。以一个圆形火球贴图为例，使用正方形Quad时约有21.5%的面积（四角）为纯透明无效区域；若改用8顶点的八边形Mesh，透明区域可压缩至约2%，fill rate消耗同步减少近20%。在Unity的Particle System中可通过`Custom Vertex Streams`配合`Mesh`渲染模式实现这一优化。

### 减少粒子层叠深度

当多个粒子系统同时从同一发射点向相机方向喷射时，粒子会高度集中在屏幕中央形成深度叠加。拉大粒子在Z轴方向的分布范围，或限制同屏存在的最大粒子数（Max Particles参数），可以有效打散叠加。

具体策略包括：将粒子的`Start Speed`增加随机性以使粒子在空间中分散；对于烟雾类特效，将单个包含100个小粒子的系统拆解为2个包含30个较大粒子的系统，总Overdraw面积可减少约40%，同时视觉效果几乎无变化。

### 纹理Alpha通道与Cutoff优化

对于边缘羽化程度极低的粒子（如火花、光点），可以在材质的Shader中启用**Alpha Test（AlphaClip）**模式。AlphaClip会将alpha值低于阈值（如0.1）的片段直接discard，被丢弃的片段不会写入Color Buffer，也不消耗混合带宽，但代价是牺牲边缘软化效果。

对于必须保留软边缘的烟雾粒子，可在纹理制作阶段主动压缩半透明过渡区宽度。将烟雾贴图的Alpha羽化距离从贴图边缘的30%压缩至10%，Overdraw贡献面积可减少约15%至20%，而在快速运动的烟雾粒子中，这一视觉差异几乎不可察觉。

## 实际应用

**角色死亡烟雾特效优化案例**：某手游角色死亡时触发一个包含80个粒子的大型烟雾系统，在低端机上造成帧率从60fps跌至22fps。通过Overdraw分析工具发现烟雾中心区域Overdraw比率高达11×。优化步骤：① 将粒子Max Particles从80降至35；② 将正方形Quad替换为六边形Mesh，无效透明面积从22%降至4%；③ 在材质中将烟雾贴图Alpha通道的边缘羽化区域从贴图面积的35%压缩至12%。三步优化后Overdraw比率降至3.2×，帧率恢复至55fps，视觉质量下降不明显。

**移动端法术特效的LOD Overdraw控制**：对距相机超过15米的粒子特效启用低Overdraw版本，将原本8层叠加的光晕粒子简化为3层，并降低粒子的屏幕占比，在该距离下人眼无法分辨层数差异，但fill rate消耗降低约60%。

## 常见误区

**误区一：减少粒子数量一定能降低Overdraw**。粒子数量与Overdraw之间并非线性关系。若将100个小粒子替换为10个覆盖相同屏幕面积的大粒子，总着色像素数基本不变，Overdraw比率几乎相同。真正影响fill rate的是所有粒子在屏幕上的**总覆盖像素面积**与**平均叠加层数**的乘积，而非粒子个数本身。

**误区二：使用Additive混合模式可以减少Overdraw**。部分开发者认为Additive（加法混合）不需要读取背景色，因此比Alpha混合更省fill rate。实际上GPU在执行Additive混合时同样需要进行完整的片段着色器计算并读取目标缓冲区的颜色，其fill rate消耗与Alpha混合几乎完全相同。Additive模式的优势在于不需要排序而非减少Overdraw。

**误区三：Overdraw只影响移动端**。即便是高端PC，大规模全屏粒子特效（如覆盖整个屏幕的暴风雪）在超高分辨率（如4K）下同样会造成显著的fill rate压力，因为4K分辨率的像素总量是1080P的4倍，同等Overdraw比率下GPU工作量是后者的4倍。

## 知识关联

Overdraw控制以**软粒子**为前提：软粒子通过深度采样解决了粒子与场景几何体的硬边问题，但深度采样本身不影响Overdraw比率，两者是独立的优化维度。理解**混合模式**（Alpha Blend、Additive、Premultiplied Alpha）是正确分析Overdraw来源的前提，因为不同混合模式决定了粒子是否需要排序，进而影响粒子在Z轴方向的实际叠加方式。

在掌握Overdraw控制的原理与测量方法后，**粒子数量控制**是下一个自然延伸的优化方向——尽管减少粒子数不等于减少Overdraw，但合理控制同屏粒子总数可以间接降低叠加层数，是整体fill rate预算管理的重要组成部分。