---
id: "3da-bake-ao"
concept: "AO烘焙"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: true
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# AO烘焙

## 概述

AO烘焙（Ambient Occlusion Baking）是将环境光遮蔽效果预先计算并储存为贴图的技术。环境光遮蔽（Ambient Occlusion，AO）描述的是表面上某点因被周围几何体遮挡而无法接收漫反射环境光的程度——凹缝、角落、两个曲面的接触边缘，这些区域会因射线难以到达而产生暗化效果。烘焙的目的是将本需要实时射线检测才能计算的高开销效果，提前转化为一张灰度贴图，运行时直接采样，从而使移动端或低配置设备也能呈现具有层次感的光影细节。

AO的数学描述最早来自Zhukov等人1998年提出的"Ambient Light"遮蔽积分，后由Landis（2002）在Siggraph Course《RenderMan in Production》中系统化为"环境光遮蔽"概念，并于《半条命2》（Valve, 2004）和《战争机器》（Epic Games, 2006）两款游戏中被大规模引入实时游戏的烘焙管线，迅速成为3D游戏美术的标准工序。AO贴图通常是一张8位（256阶）灰度图，纯白（线性值1.0）表示该点完全不被遮挡，纯黑（线性值0.0）表示该点被完全遮蔽。

在实际渲染管线中，AO贴图最常见的用法是与漫反射贴图（Albedo）逐像素相乘（`FinalColor = Albedo × AO`），为模型的凹陷、缝隙等位置补充视觉深度，即使全局照明（GI）系统关闭或简化，模型依然显得立体而不"塑料感"。

---

## 核心原理

### 半球积分与射线投射

AO的核心算法是从表面每个采样点，沿该点法线构成的半球（Hemisphere）方向随机发射若干条射线，统计被周围几何体遮挡的射线比例。其数学表达式为：

$$
AO(p) = \frac{1}{\pi} \int_{\Omega} V(p, \omega)\, (\hat{n} \cdot \omega)\, d\omega
$$

其中，$\Omega$ 表示法线半球，$\omega$ 为采样方向，$\hat{n}$ 为表面法线，$V(p, \omega)$ 为可见性函数（射线未被遮挡时为1，被遮挡时为0）。在实际的蒙特卡洛（Monte Carlo）近似实现中，设总发射射线数为 $N$，被遮挡射线数为 $H$，则遮蔽估计为：

$$
AO \approx 1 - \frac{H}{N}
$$

遮蔽值越接近1表示该点越开阔，越接近0表示该点越封闭。这一离散近似方法被Blender Cycles、Marmoset Toolbag 4、Substance Painter等主流工具普遍采用。

**最大射线距离（Max Distance）**是控制AO范围最关键的参数之一。以Substance Painter为例，该参数默认为模型包围盒对角线长度的0.01倍：对于一个高度为2m的角色模型，Max Distance默认约为0.02m（2cm），此时只有距采样点2cm以内的遮挡几何体才会被计入。若将其调大至0.2m，模型整体会偏灰；调小至0.002m，则仅最细微的缝隙有遮蔽效果，其余部分接近纯白。

### 烘焙空间：对象空间 vs. 世界空间

AO烘焙必须在明确的坐标空间下进行。

**对象空间AO（Object Space AO）**：射线基于模型本地法线方向发射，贴图随模型旋转而旋转，不受模型在场景中朝向的影响。适合静态道具、场景物件和不形变的刚体角色部件。Marmoset Toolbag 4和Substance Painter的AO烘焙默认均为对象空间。

**世界空间AO（World Space AO）**：射线基于世界坐标系法线发射，贴图记录的是模型在特定摆放角度下的遮蔽状况。一旦模型旋转，贴图即失效，因此极少用于可旋转物体，主要出现在地形烘焙或固定朝向的大型建筑构件中。

对于骨骼蒙皮角色，静态烘焙AO在动画过程中会出现"关节处永远暗"或"腋下出现白色漏光"等问题，因此现代角色渲染多依赖实时**SSAO（屏幕空间环境光遮蔽，Shanmugam & Orikan, 2007）**或**HBAO+（Horizon-Based Ambient Occlusion，Bavoil et al., 2008, NVIDIA）**进行运动状态下的AO补偿，而烘焙AO仅保留在角色的装备道具上。

### 采样数量与噪点控制

AO烘焙质量的核心参数是**采样数（Samples）**。采样数越高，蒙特卡洛积分的方差越小，最终贴图噪点越少，但烘焙时间随采样数线性增长。

| 工具 | 低质量预设 | 中质量预设 | 高质量预设 |
|---|---|---|---|
| Substance Painter | 16 samples | 64 samples（默认） | 512 samples |
| Marmoset Toolbag 4 | 128 rays | 512 rays | 2048 rays |
| Blender Cycles | 32 samples | 128 samples | 512+ samples |

在实际项目中，对于512×512的草稿版AO贴图，64样本通常可见明显颗粒；最终交付的2048×2048贴图，建议使用不低于256样本，关键部位（如角色面部）建议512样本。此外，在Blender中开启**降噪（Denoise）**节点可将等效质量的采样数降低4至8倍，将原本需要512采样才能达到的洁净度用64采样实现。

---

## 关键公式与参数速查

以下Python伪代码展示了AO烘焙中蒙特卡洛采样的核心逻辑，帮助理解工具背后的计算流程：

```python
import random
import math

def compute_ao(surface_point, surface_normal, scene_geometry,
               num_samples=64, max_distance=0.05):
    """
    计算单个表面点的AO值。
    surface_point: 3D采样位置
    surface_normal: 该点单位法线向量
    scene_geometry: 场景碰撞体（用于射线检测）
    num_samples: 半球采样射线数量
    max_distance: 最大遮蔽检测距离（米）
    返回值: AO遮蔽值，范围[0, 1]，1=完全开阔，0=完全遮蔽
    """
    occluded = 0
    for _ in range(num_samples):
        # 在法线半球内随机生成余弦加权采样方向
        ray_dir = cosine_weighted_hemisphere_sample(surface_normal)
        # 投射射线，检测max_distance范围内是否有遮挡
        hit = scene_geometry.raycast(surface_point, ray_dir, max_distance)
        if hit:
            occluded += 1
    ao_value = 1.0 - (occluded / num_samples)
    return ao_value
```

余弦加权采样（cosine-weighted sampling）相比均匀半球采样在相同样本数下可将方差降低约30%，这是Substance Painter和Marmoset内部采样策略的核心优化之一（参见《Physically Based Rendering: From Theory to Implementation》，Pharr, Jakob & Humphreys, 2023, MIT Press，第13章）。

---

## 实际应用

### 静态道具与场景物件

静态道具是AO烘焙最主要的应用场景。以一个石质花盆为例：其底部边缘与桌面的接触缝、花盆内壁与土壤交界面、外壁雕刻纹路的凹槽，都需要AO来表现阴影积累感。标准烘焙流程如下：

1. 高模（High Poly，通常500万面以上）与低模（Low Poly，目标3000面以内）在世界原点对齐放置；
2. 在Marmoset Toolbag 4中，为低模配置**笼体（Cage）**，向外偏移量设为0.002至0.005m，确保射线从低模表面正确射出；
3. 烘焙分辨率设置为2048×2048，采样数256，Max Distance 0.03m；
4. 输出的AO贴图在Photoshop或Substance Painter中与Albedo贴图以**正片叠底（Multiply）**混合，AO层不透明度通常设为60%至80%，避免过度变暗。

### 角色装备拼接处

角色盔甲、皮带扣、肩甲与胸甲的接缝处，是AO烘焙在角色资产中的典型应用位置。这类区域在引擎实时光照下往往"过亮"且缺乏层次，烘焙AO能在不增加实时计算开销的情况下提供稳定的接缝暗化效果。

需要注意的是，角色各部件（头部、躯干、手部）通常分属不同UV岛（UV Island），烘焙时需将各部件分批烘焙或使用Marmoset的"多对象匹配"功能，否则相邻部件的几何体会互相干扰，在接缝处产生错误的深色渗透（Light Leaking）。

### 与其他贴图的合成策略

AO贴图在PBR管线中通常有两种输入路径：

- **混入Albedo**：`Albedo_Final = Albedo × AO`，在不支持独立AO通道的旧引擎或移动端引擎（如Unity Mobile Forward渲染路径）中常用。
- **独立AO通道**：Unreal Engine 5将AO贴图输入材质节点的`Ambient Occlusion`引脚，引擎在光照计算阶段将其与间接光照相乘，不影响直接光照，物理正确性更高。

现代项目通常将AO、Roughness、Metallic三张灰度贴图合并为一张RGB贴图（即**ORM贴图**，R=Occlusion, G=Roughness, B=Metallic），节省一个贴图采样槽位，在移动端每减少一个采样槽位可节省约0.3ms的GPU采样时间（具体数值因GPU架构而异）。

---

## 常见误区与问题排查

### 误区一：黑斑（Dark Splotches）

**现象**：烘焙结果出现不规则的黑色斑块，集中在曲率较大的区域。

**原因**：低模法线（由光滑组或硬边决定）与高模实际表面法线偏差超过90°时，射线从法线半球的"反面"发射，直接穿入模型内部并立即命中几何体，记录为遮蔽，产生错误黑斑。

**解决方案**：在3ds Max或Maya中，确保低模光滑组与高模曲率分布一致；在Blender中，对应位置的面应共享光滑着色（Shade Smooth）且法线无翻转。Marmoset Toolbag 4的"Skew Normals"选项可将射线起点沿高模法线方向偏移，能消除约70%的此类黑斑。

### 误区二：接缝漏光（Seam Bleeding）

**现象**：AO贴图的UV接缝处出现白色或灰色线条，在模型上表现为明显的分割线。

**原因**：AO烘焙的边缘像素（Texel）没有被正确扩展（Dilate/Bleed），相邻UV岛的空白区域（值默认为0或1）渗入接缝像素的混合计算。

**解决方案**：在Substance Painter的烘焙设置中，将"Dilation（扩展）"值设为至少8像素（2048贴图标准）或16像素（4096贴图标准）。Marmoset Toolbag 4默认扩展为16像素，覆盖绝大多数场景。

### 误区三：Max Distance设置错误导致整体偏灰

**现象**：整个模型的AO贴图呈现均匀的灰色，没有明显的明暗对比。

**原因**：Max Distance设置过大，远处不相关的几何体（如地面、周围场景物件）被计入遮蔽计算，导致几乎每条射线都命中遮挡物。

**解决方案**：Max Distance的经验值为模型最大尺寸的1%至5%。对于一个高1.8m的角色，Max Distance建议设为0.02m至0.09m；