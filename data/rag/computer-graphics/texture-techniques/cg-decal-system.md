---
id: "cg-decal-system"
concept: "贴花系统"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.8
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 贴花系统

## 概述

贴花系统（Decal System）是一种将额外纹理图案动态叠加到已有几何体表面的渲染技术，常用于实现弹孔、血迹、涂鸦、道路标线等需要在运行时动态添加到场景中的视觉细节。与直接修改基础网格纹理不同，贴花不改变原始几何信息，而是通过独立的渲染通道将投影纹理混合到目标表面的颜色、法线或粗糙度等属性上。

贴花技术最早在前向渲染管线中以"投影贴图"形式出现，通过一个长方体（Decal Volume）将纹理投影到其覆盖范围内的所有几何体上。随着延迟渲染（Deferred Rendering）在2005年前后成为游戏引擎主流，Deferred Decal作为其天然配套方案迅速普及，Unreal Engine 3、CryEngine 2等引擎在2007至2008年间正式将其纳入标准管线。

贴花系统之所以重要，是因为它以极低的几何开销实现了场景细节的高密度动态叠加。一个弹孔贴花仅需渲染一个立方体包围盒，却能在任意复杂曲面上产生正确投影，这对于战斗场景中可能同时存在数百个弹孔的情形至关重要。

---

## 核心原理

### Deferred Decal 的工作机制

Deferred Decal在G-Buffer填充完成后、光照计算开始之前执行。渲染器提交一个轴对齐或任意朝向的单位立方体（OBB，Oriented Bounding Box）作为贴花体积，顶点着色器将该立方体变换到裁剪空间后光栅化，片元着色器利用当前像素的屏幕坐标和深度值重建其世界坐标：

```
WorldPos = InvViewProj × vec4(NDC.xy, depth, 1.0)
```

将重建的世界坐标变换到贴花的本地空间后，UV坐标即为本地坐标的XZ分量（归一化到[0,1]范围）：

```
DecalUV = (LocalPos.xz + 0.5)
```

若 LocalPos 的任意分量超出[-0.5, 0.5]，则该片元被裁剪（discard），从而实现贴花在几何体表面的精确边界。最终，片元着色器将贴花纹理（颜色、法线、金属度等）写入G-Buffer对应通道，后续光照计算自动应用贴花结果，无需额外pass。

### Screen-Space Decal 的工作机制

Screen-Space Decal同样依赖深度缓冲重建世界坐标，但其混合目标是**屏幕空间的后处理缓冲**而非G-Buffer，因此通常在光照后阶段执行。这意味着Screen-Space Decal无法直接修改法线或金属度，只能叠加颜色层。其核心步骤是对深度缓冲采样获取场景深度，逆变换获得世界坐标，再计算贴花UV并使用Alpha混合写入最终颜色缓冲。

Screen-Space Decal的优点是对渲染管线侵入性最小，在前向渲染引擎或移动端等无G-Buffer环境下也可使用；缺点是贴花边缘会随摄像机角度变化出现拉伸（Stretching），且无法正确表现法线细节。

### 法线重定向与混合策略

在Deferred Decal中写入法线时，不能简单覆盖G-Buffer中的原始法线，否则曲面几何法线将丢失。常见做法是使用**Partial Derivative混合**（Reoriented Normal Mapping，RNM），将贴花法线 n_d 与底层法线 n_b 按以下方式合并：

```
n_result = normalize( n_b.xy + n_d.xy, n_b.z )
```

此方法保留了底层几何的宏观弯曲特征，同时叠加贴花带来的微观细节（如弹孔边缘凹陷）。另一种策略是在G-Buffer中预留单独的贴花法线通道，光照阶段再合并，但代价是增加G-Buffer带宽约8字节/像素。

---

## 实际应用

**战术射击游戏弹孔系统**：以《使命召唤》系列为例，场景中最多同时维持约250个贴花，超出限制时采用FIFO（先入先出）策略回收最旧的贴花。每个弹孔贴花包含Albedo（颜色/烟熏）、Normal（凹陷法线）和Roughness（金属光泽变化）三张纹理，打包进一张2048×512的图集以减少DrawCall切换。

**湿地与天气系统**：《地平线：零之曙光》使用Deferred Decal投影积水、泥浆等动态天气效果，贴花的Roughness通道被设为接近0以模拟水坑反射，法线通道写入涟漪法线贴图。该系统中贴花体积会随雨量参数动态缩放，实现水坑随时间扩大的视觉效果。

**道路标线与地面细节**：UE5的道路工具将停车线、斑马线等预烘焙为Decal资产，以`DBuffer`模式写入G-Buffer，这样在下一帧的基础Pass中底层地面材质仍可接受实时光照计算，不产生额外照明误差。

---

## 常见误区

**误区一：认为Deferred Decal可以直接应用于透明物体**。Deferred Decal读取G-Buffer深度时，透明物体通常不写入深度缓冲（或写入行为不确定），导致贴花在透明玻璃、粒子等物体上表现异常——贴花会穿透到玻璃后方的实体表面上，而非停在玻璃表面。解决方案是对透明物体关闭贴花接收，或使用Mesh Decal（将贴花网格与透明物体一起提交前向Pass）。

**误区二：将法线通道直接覆盖写入G-Buffer**。这会完全抹去底层几何体的曲面法线，导致弹孔贴在球体上时球面的高光消失，整个贴花区域看起来像一块平板。正确做法必须采用上文提到的RNM混合，或在着色器中将贴花法线Alpha设为小于1以保留底层法线权重。

**误区三：误以为Screen-Space Decal比Deferred Decal性能更高**。Screen-Space Decal虽然不写G-Buffer，但若在光照后阶段叠加大量贴花，反而会增加Overdraw，且每次采样都需要一次额外的深度重建逆变换（包含矩阵乘法），在片元密集区域GPU消耗不低于Deferred Decal。实际工程中，Deferred Decal通常性能更优，Screen-Space Decal适合管线受限的特殊场景。

---

## 知识关联

**前置概念——纹理投影**：贴花系统的UV生成本质上是纹理投影的一种变体。理解如何将三维坐标映射为二维UV（即将贴花本地坐标的XZ平面作为投影平面）是实现贴花体积裁剪和UV计算的直接基础。纹理投影中的透视除法和矩阵变换步骤在贴花片元着色器中几乎逐字复用。

**关联概念——G-Buffer结构**：Deferred Decal的写入目标是G-Buffer中的具体通道（Albedo/Normal/PBR参数），需要理解延迟渲染管线中各通道的布局格式（如RGBA8存Albedo、RG16F存法线等），才能正确设置渲染状态（RenderTargetWriteMask）使贴花只写入目标通道而不污染其他数据。

**关联概念——深度重建**：无论Deferred Decal还是Screen-Space Decal，核心步骤都依赖从深度缓冲逆变换重建世界坐标。深度值的线性化方式（近平面 `z_near`、非线性NDC到线性view-space的转换）直接影响贴花投影的准确性，是调试贴花位置偏移问题时最常见的排查点。