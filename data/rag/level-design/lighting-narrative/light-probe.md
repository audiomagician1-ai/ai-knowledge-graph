---
id: "light-probe"
concept: "光照探针"
domain: "level-design"
subdomain: "lighting-narrative"
subdomain_name: "光照叙事"
difficulty: 3
is_milestone: false
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 6
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
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 光照探针

## 概述

光照探针（Light Probe）是一种在三维场景中采样并存储周围环境光照信息的技术手段。它通过在空间中放置若干采样点，记录该点处来自各个方向的入射光线信息，并将这些信息以球谐函数（Spherical Harmonics，缩写为 SH）的形式压缩存储。当动态物体（如角色、移动道具）经过相邻探针之间的区域时，引擎对相邻探针的 SH 数据进行插值，为该动态物体提供近似准确的间接光照效果。

光照探针技术最早在电影离线渲染领域被系统化使用。Ramamoorthi 与 Hanrahan 于 2001 年在 SIGGRAPH 发表的论文《An Efficient Representation for Irradiance Environment Maps》奠定了以球谐函数编码环境光照的理论基础，该论文指出 L2 阶（三阶）球谐即可捕捉 99% 以上的漫反射光照能量，为游戏引擎后来的实现提供了直接依据（Ramamoorthi & Hanrahan, 2001）。进入实时引擎领域后，Unity 于 2012 年在 Unity 4.0 版本中正式引入可视化编辑的 Light Probe Group 工具；Unreal Engine 则以"间接光照缓存"（Indirect Lighting Cache，ILC）形式实现类似功能，UE5 进一步以 Lumen 全局光照部分替代，但 ILC 仍保留用于移动端和静态烘焙工作流。

光照探针解决了烘焙光照贴图无法作用于动态物体这一根本矛盾。静态几何体可将间接光照烘焙到光照贴图（Lightmap）纹素中，但会移动的角色无法使用静态贴图，探针成为填补这一空白的关键工具。在关卡设计的光照叙事语境下，探针的布局质量直接决定了角色穿越不同光照区域时的视觉连贯性：若探针稀疏，角色从橙色火把区域步入蓝色月光区域时，身上的间接光照会发生离散跳变，破坏沉浸感；布局合理的探针网络则能让角色身上的颜色与亮度随场景氛围平滑过渡，强化关卡的光照叙事。

---

## 核心原理

### 球谐函数编码与阶数限制

光照探针存储的并非一张完整的 360° 高动态范围图像，而是将各方向的辐照度（Irradiance）投影到球谐函数基上。Unity 光照探针默认使用 **L2 三阶球谐**，在每个颜色通道（R/G/B）上各有 9 个系数，合计 27 个 float32 浮点数，单个探针的内存占用仅约 108 字节。这种编码极为紧凑，但代价是只能表达低频光照变化——即大面积漫反射色调和软阴影——无法捕捉尖锐高光或细小阴影边界（高频信息）。

L2 球谐重建辐照度的公式为：

$$E(\mathbf{n}) = \sum_{l=0}^{2} \sum_{m=-l}^{l} L_l^m \cdot Y_l^m(\mathbf{n})$$

其中 $\mathbf{n}$ 为表面法线方向，$Y_l^m$ 为实值球谐基函数，$L_l^m$ 为对应的光照系数。对 L2 阶展开共产生 $(2+1)^2 = 9$ 个基函数，分别对应 $l=0$（1个）、$l=1$（3个）、$l=2$（5个）阶项。该公式告诉我们，探针所能还原的法线方向辐照度，本质上是对真实光场在球面上的低通滤波结果，截止频率由最高阶 $l=2$ 决定。

这一特性意味着光照探针天然适合漫反射间接光照，而不适合替代反射探针处理镜面高光。若将探针数据强行用于高光计算，会产生明显的"塑料感"漫反射泛光，破坏材质真实感。

### 探针插值与 Delaunay 四面体化

当动态物体在场景中移动时，引擎需确定它应"感受"到哪些探针的光照贡献。Unity 使用 **Delaunay 四面体化（Tetrahedral Tessellation）** 算法将所有探针连接成三维四面体网格。物体质心所落入的四面体决定了参与插值的四个探针顶点，系统以**重心坐标（Barycentric Coordinates）**为权重对四个探针的 SH 系数进行线性混合：

$$L_{interp} = \lambda_1 L_1 + \lambda_2 L_2 + \lambda_3 L_3 + \lambda_4 L_4, \quad \sum_{i=1}^{4}\lambda_i = 1$$

这就解释了若探针分布出现"悬空"（如仅在地板平面布置探针而忽略垂直方向），或场景边缘只有单侧探针时，物体质心可能落在四面体网格之外，引擎会将其回退到最近外表面并插值到场景边界的"虚拟黑色探针"（Ambient Black Probe），导致角色在靠近关卡边界时身体突然变暗，即俗称的"边缘漏黑"问题。

### 反射探针的工作方式与光照探针的区别

反射探针（Reflection Probe）与光照探针是功能互补但原理不同的工具。反射探针在其放置位置捕捉一张完整的 **Cubemap**（六面体立方贴图，分辨率通常为 128×128 至 1024×1024 像素），用于为周围物体提供镜面反射信息；光照探针存储的是压缩后的 SH 系数，专服务于漫反射间接光照（Diffuse GI）。

两者在 Unity 渲染管线中独立运作：反射探针写入材质的 `unity_SpecCube0` 采样器影响高光通道，光照探针数据通过 `ShadeSH9()` 函数（HLSL 内置）写入漫反射通道。在布局实践中，反射探针的 **Blend Distance** 参数（混合距离）建议设置为探针 Box 尺寸的 10%～20%，防止物体跨越两个反射探针边界时产生反射图像的硬切换；光照探针间距过大时则表现为漫反射色调的离散跳跃，二者失效的视觉表现不同，排查时需分别检查。

---

## 关键公式与代码实践

在 Unity Editor 中，可通过脚本批量生成规则网格的探针组，避免手动逐点摆放的低效操作：

```csharp
using UnityEngine;
using UnityEditor;

public class LightProbeGridGenerator : MonoBehaviour
{
    [MenuItem("Tools/Generate Light Probe Grid")]
    static void GenerateGrid()
    {
        // 在 10m×3m×10m 空间内以 2m 间距生成探针网格
        float spacingX = 2.0f, spacingY = 1.5f, spacingZ = 2.0f;
        int countX = 5, countY = 2, countZ = 5;

        LightProbeGroup lpg = new GameObject("LightProbeGrid")
            .AddComponent<LightProbeGroup>();
        var positions = new System.Collections.Generic.List<Vector3>();

        for (int x = 0; x < countX; x++)
        for (int y = 0; y < countY; y++)
        for (int z = 0; z < countZ; z++)
        {
            positions.Add(new Vector3(
                x * spacingX, 
                y * spacingY + 0.3f,  // 距地 0.3m 起始层
                z * spacingZ));
        }
        lpg.probePositions = positions.ToArray();
        Debug.Log($"已生成 {positions.Count} 个探针");
    }
}
```

上述代码在 10m×3m×10m 区域内生成 50 个探针，总内存占用约 50×108 = 5400 字节（约 5.3 KB），是一张 512×512 Lightmap（约 1 MB）内存代价的 0.5% 左右，印证了探针方案极低的存储开销。

---

## 实际应用：关卡光照叙事布局策略

### 走廊与房间过渡区的探针加密

以一条长 20 米、宽 3 米的地下走廊为例：推荐在走廊两侧地板上方约 0.3 米（角色脚踝处）和 1.8 米（角色头顶处）各布置一排探针，水平间距 2～3 米。在以下位置须将间距压缩至 0.5～1 米：
- **光色突变处**：如火把橙色区域（色温约 2000K）向月光蓝色窗口区域（色温约 6500K）的过渡带；
- **门洞与拐角**：室内外亮度差可达 3～5 个 EV 级别，探针需在门框两侧各额外布置 2 个；
- **顶棚高度突变处**：低矮地牢（高 2.2 米）连接高耸大厅（高 8 米）时，垂直方向须增补中间层探针。

**反例说明**：若整条走廊仅在两端各放 1 个探针，当角色行进至走廊中点时，其身上的间接光照将是两端光照的 50% 线性混合——意味着角色同时呈现橙色与蓝色的均匀混合灰，完全丧失光照的叙事定向感。

### 开放场景（Open World）的分层布局

在开放世界关卡中，不应在整个地图均匀撒布探针（会产生数十万个探针导致烘焙时间暴增）。推荐采用**三层密度策略**：
1. **玩家高频活动区**（如主路、营地）：探针间距 2～4 米，同时设置高低两层；
2. **玩家低频经过区**（如山坡、林地边缘）：间距扩大至 8～12 米，仅保留单层地面探针；
3. **纯远景装饰区**（玩家不可进入）：完全移除探针，动态物体不会出现在此区域。

Unreal Engine 的 ILC（Indirect Lighting Cache）在 UE4 中默认以 200 cm（2 米）的体素格进行自动插值，可通过 `r.IndirectLightingCache.Quality 2` 控制台命令将其提升为高质量模式（体素分辨率×2），但会使内存占用翻倍，需根据目标平台显存预算决定是否启用。

### 反射探针的布局配合

在地下室或室内场景中，每个独立封闭房间至少放置 1 个反射探针，分辨率设置为 256×256（较低亮度变化区域）或 512×512（含明显镜面反射的区域，如水面、金属地板）。反射探针的 **Importance** 值（Unity）应从外到内递增——走廊设为 1，房间设为 2，重要叙事房间（Boss 房、关键道具房）设为 3，确保物体进入更小的空间时优先采样局部反射而非大范围走廊反射，避免在 Boss 房中出现走廊回廊的镜像残影。

---

## 常见误区

**误区一：只在地面平面布置探针。** 四面体化算法要求探针在三维空间中形成体积性分布。若所有探针的 Y 坐标相同（平面分布），四面体化将退化为平面三角剖分，任何高于该平面的物体（如空中飞行的敌人）都会落在网格外部，被映射到黑色探针上变为全黑。修正方法：至少布置高低两层探针，高度差建议不小于 1.5 米。

**误区二：将反射探针误用于角色漫反射光照。** 反射探针的 Cubemap 分辨率虽高，但其设计用途是镜面反射，对角色漫反射无贡献。在 Unity URP 中，角色漫反射 GI 完全由光照探针的 SH 数据驱动，即使场景中摆满反射探针，若无光照探针，角色身体的漫反射 GI 将固定使用天空盒 SH——在室内昏暗场景下表现为角色身上出现不合理的室外天空蓝色调。

**误区三：在光照烘焙前摆好探针即万事大吉，忽略烘焙后的 Validity 检查。** Unity 的光照探针烘焙完成后，可在 Scene 视图开启 **Light Probe Visualization** 模式，观察每个探针球的