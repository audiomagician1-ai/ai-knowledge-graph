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
content_version: 4
quality_tier: "A"
quality_score: 92.5
generation_method: "ai-rewrite-v3"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v3"
  - type: "academic"
    citation: "Valient, M. (2007). Deferred Rendering in Killzone 2. Guerrilla Games GDC Presentation."
  - type: "academic"
    citation: "Kajalin, V. (2009). Screen-Space Ambient Occlusion. ShaderX7: Advanced Rendering Techniques, Charles River Media."
  - type: "academic"
    citation: "Hargreaves, S. & Harris, M. (2004). Deferred Shading. NVIDIA Developer Conference, GDC 2004."
  - type: "academic"
    citation: "Pranckevičius, A. (2012). Stable SSAO in Battlefield 3 with Selective Temporal Filtering. GDC 2012, DICE."
  - type: "book"
    citation: "Akenine-Möller, T., Haines, E., & Hoffman, N. (2018). Real-Time Rendering, 4th Edition. CRC Press. Chapter 6: Texturing."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v3
updated_at: 2026-04-06
---


# 贴花系统

## 概述

贴花系统（Decal System）是一种将额外纹理图案动态叠加到已有几何体表面的渲染技术，常用于实现弹孔、血迹、涂鸦、道路标线等需要在运行时动态添加到场景中的视觉细节。与直接修改基础网格纹理不同，贴花不改变原始几何信息，而是通过独立的渲染通道将投影纹理混合到目标表面的颜色、法线或粗糙度等属性上。

贴花技术最早在前向渲染管线中以"投影贴图"（Projective Texturing）形式出现，通过一个长方体（Decal Volume）将纹理投影到其覆盖范围内的所有几何体上。随着延迟渲染（Deferred Rendering）在2005年前后成为游戏引擎主流，Deferred Decal作为其天然配套方案迅速普及。Shawn Hargreaves与Mark Harris于2004年在GDC演讲"Deferred Shading"中系统阐述了延迟渲染的G-Buffer架构（Hargreaves & Harris, 2004），为Deferred Decal的工程化奠定了理论基础；Michal Valient在2007年GDC演讲"Deferred Rendering in Killzone 2"中详细披露了Deferred Decal在PS3 Cell处理器与RSX图形芯片上的具体实现细节，包括如何将贴花数据压缩进有限的G-Buffer带宽（Valient, 2007）。此后，Unreal Engine 3（版本3.0，2006年）、CryEngine 2（2007年随《孤岛危机》发布）等引擎在2007至2008年间正式将Deferred Decal纳入标准管线，并向广大开发者公开了完整工具链。

贴花系统之所以重要，是因为它以极低的几何开销实现了场景细节的高密度动态叠加。一个弹孔贴花仅需渲染一个立方体包围盒（约36个顶点的索引绘制），却能在任意复杂曲面上产生正确投影，这对于战斗场景中可能同时存在数百个弹孔的情形至关重要。以《使命召唤：现代战争》（2019，Infinity Ward）为例，其场景同时激活的贴花峰值超过300个，全部采用Deferred Decal模式，GPU帧时间占用控制在0.8ms以内（60fps目标帧预算约16.7ms，贴花系统仅占约4.8%）。

现代引擎中贴花系统按渲染时机和写入目标可分为三大类型：**Deferred Decal**（写入G-Buffer，光照前执行）、**Screen-Space Decal**（写入后处理颜色缓冲，光照后执行）以及**Mesh Decal**（作为标准网格提交渲染，适用于透明物体或移动端）。三种方案在功能覆盖、性能开销和管线兼容性上各有取舍，工程选型需根据目标平台的G-Buffer带宽、实时光照需求和贴花密度综合判断。

---

## 核心原理

### Deferred Decal 的工作机制

Deferred Decal在G-Buffer填充完成后、光照计算开始之前执行。渲染器提交一个轴对齐或任意朝向的单位立方体（OBB，Oriented Bounding Box）作为贴花体积，顶点着色器将该立方体变换到裁剪空间后光栅化，片元着色器利用当前像素的屏幕坐标和深度值重建其世界坐标：

$$\mathbf{P}_{world} = \mathbf{M}_{InvViewProj} \cdot \begin{pmatrix} x_{NDC} \\ y_{NDC} \\ d \\ 1 \end{pmatrix}$$

其中 $d$ 为从深度缓冲采样的非线性深度值，$\mathbf{M}_{InvViewProj}$ 为视图投影矩阵的逆矩阵，$x_{NDC}$ 和 $y_{NDC}$ 为归一化设备坐标（范围$[-1,1]$），由像素的屏幕坐标除以分辨率并重映射得到。将重建的世界坐标变换到贴花的本地空间后，UV坐标即为本地坐标的XZ分量（归一化到$[0,1]$范围）：

$$UV_{decal} = \mathbf{P}_{local}.xz + 0.5$$

若 $\mathbf{P}_{local}$ 的任意分量超出 $[-0.5,\ 0.5]$，则该片元被裁剪（`discard`），从而实现贴花在几何体表面的精确边界。最终，片元着色器将贴花纹理（颜色、法线、金属度等）写入G-Buffer对应通道，后续光照计算自动应用贴花结果，无需额外Pass。

例如，在Unreal Engine 5的DBuffer实现中，Deferred Decal被分配到独立的`DBufferA/B/C`三张渲染目标（分别存储Albedo、Normal和Roughness），以`Min/Max Blend`而非简单Alpha混合方式写入，确保多个重叠贴花的合并顺序无关性。DBuffer在UE5中默认启用，对应工程设置为`r.DBuffer=1`，关闭该选项则贴花退化为Scene Color混合，失去法线与粗糙度修改能力。

### Screen-Space Decal 的工作机制

Screen-Space Decal同样依赖深度缓冲重建世界坐标，但其混合目标是**屏幕空间的后处理颜色缓冲**而非G-Buffer，因此通常在光照后阶段执行。这意味着Screen-Space Decal无法直接修改法线或金属度，只能叠加颜色层。其核心步骤是对深度缓冲采样获取场景深度，逆变换获得世界坐标，再计算贴花UV并使用Alpha混合写入最终颜色缓冲。

Screen-Space Decal的优点是对渲染管线侵入性最小，在前向渲染引擎或移动端等无G-Buffer环境下也可使用；缺点是贴花边缘会随摄像机角度变化出现拉伸（Stretching），且无法正确表现法线细节。Kajalin（2009）在讨论屏幕空间技术的通用局限性时指出，一切依赖深度重建世界坐标的屏幕空间算法，在掠射角（Grazing Angle，即摄像机视线与表面法线夹角接近90°）条件下均会产生不可避免的精度退化，Decal Stretching正是这一规律的直接体现。

具体而言，当摄像机以接近水平的视线观察地面时，深度缓冲中相邻两像素对应的世界坐标差值在水平方向可达数米，而UV空间中仅相差1像素，导致贴花在该方向被极度压缩；而垂直方向因视线与地面接近平行，坐标差值极小，纹素反而被拉伸数十倍，产生明显的纹理扭曲（Akenine-Möller et al., 2018, Chapter 6）。

> **思考问题**：Screen-Space Decal在摄像机以极低仰角（接近平行于地面）观察地面弹孔时，为什么贴花纹理会出现强烈的拉伸变形？这一现象与纹理投影的哪个数学步骤直接相关？若要在低仰角场景中保持贴花形状正确，你会如何修改投影策略？

### 法线重定向与混合策略

在Deferred Decal中写入法线时，不能简单覆盖G-Buffer中的原始法线，否则曲面几何法线将丢失。常见做法是使用**Reoriented Normal Mapping（RNM）**混合，将贴花法线 $\mathbf{n}_d$（切线空间，解码自贴花法线纹理）与底层法线 $\mathbf{n}_b$（同样在切线空间表示）按以下方式合并：

$$\mathbf{n}_{result} = \text{normalize}\!\left(\mathbf{n}_b.xy + \mathbf{n}_d.xy,\ \mathbf{n}_b.z\right)$$

此方法保留了底层几何的宏观弯曲特征，同时叠加贴花带来的微观细节（如弹孔边缘凹陷）。另一种策略是在G-Buffer中预留单独的贴花法线通道，光照阶段再合并，但代价是增加G-Buffer带宽约8字节/像素——以1080p分辨率（约207万像素）、60fps计算，额外带宽开销约为 $2,073,600 \times 8 \times 60 \approx 995\ \text{MB/s}$，在显存带宽受限的移动GPU（如Adreno 750理论带宽约77 GB/s）上需谨慎权衡，995 MB/s虽仅占约1.3%，但叠加其他G-Buffer通道后总带宽压力不可忽视。

### Mesh Decal 的工作机制

Mesh Decal是将贴花内容烘焙为独立网格（通常是紧贴目标表面、略微偏移的多边形片）并提交到普通渲染队列的方式。其UV坐标在离线阶段直接展开，无需运行时投影计算，因此完全避免了掠射角拉伸问题，也天然支持透明物体（可与透明Pass共用）。代价是需要预先制作网格资产，无法用于完全动态的场景（如任意位置的运行时弹孔），通常用于路面标线、固定装饰徽章等静态美术内容。在移动端（如使用OpenGL ES 3.1或Vulkan的Android平台），因缺少MRT（Multiple Render Targets）支持，Mesh Decal往往是唯一实用的贴花方案。

---

## 关键公式与数学模型

贴花系统的核心运算涉及四个关键公式，构成完整的投影-混合数学框架：

**公式一：深度线性化**（将非线性NDC深度转换为线性视图空间深度）：

$$z_{linear} = \frac{z_{near} \cdot z_{far}}{z_{far} - d \cdot (z_{far} - z_{near})}$$

其中 $d \in [0, 1]$ 为深度缓冲采样值（Direct3D约定，OpenGL中需先将$d$从$[0,1]$重映射到$[-1,1]$），$z_{near}$ 和 $z_{far}$ 为近远裁剪面距离（典型值：$z_{near}=0.1\text{m}$，$z_{far}=10000\text{m}$）。非线性化是透视投影的固有属性，导致深度缓冲在近处精度高、远处精度低，这正是贴花在远距离出现Z-Fighting的根本原因。

**公式二：贴花UV生成**（从本地空间坐标提取投影UV）：

$$UV = \mathbf{P}_{local}.xz + \begin{pmatrix}0.5 \\ 0.5\end{pmatrix}, \quad \mathbf{P}_{local} \in [-0.5, 0.5]^3$$

此公式假设