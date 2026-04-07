---
id: "rock-placement"
concept: "岩石放置"
domain: "level-design"
subdomain: "terrain-design"
subdomain_name: "地形设计"
difficulty: 2
is_milestone: false
tags: ["环境"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
generation_method: "intranet-llm-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 岩石放置

## 概述

岩石放置（Rock Placement）是关卡设计地形细化阶段的具体工序，指设计师在完成生态区划分（Biome Zoning）之后，通过手动摆放或程序辅助工具将岩石资产（Rock Assets）分布到场景中，并同步配置碰撞体积（Collision Volume）与顶点混合材质（Vertex Blend Material），使地形从"平坦贴图"转变为具有真实厚度感、遮蔽功能与可行走边界的三维空间。

这一工序在20世纪90年代末随3D关卡编辑器的普及而成为独立的设计步骤。1998年《半条命》（Half-Life）使用的Valve Hammer Editor要求设计师为每块岩石手动绘制凸包碰撞体（Convex Hull Collision）；2004年前后Unreal Engine 3引入Landscape系统与Foliage Painter，让岩石散布进入半自动化阶段；2022年Unreal Engine 5的PCG（Procedural Content Generation）框架进一步允许按规则图（Rule Graph）驱动岩石的程序化分布，但手动精调仍是保证可玩性的必要环节。岩石同时承担三种不可分离的功能——**几何功能**（改变地形轮廓）、**碰撞功能**（划定可行走区域与掩体边界）、**视觉融合功能**（通过材质混合消除与地面的接缝）——这三种功能必须同时被管理，任何一项失调都会产生"漂浮石头"、"隐形墙"或"材质违和"等典型缺陷，因此岩石放置自成一道独立工序，而非并入通用"道具摆放"流程。

参考文献：《Level Design: Processes and Experiences》（Kremers, 2009, Taylor & Francis）对地形细化工序有系统论述，其第8章专门讨论岩石与植被的密度层级逻辑。

---

## 核心原理

### 散布逻辑与三级密度模型

岩石散布遵循"焦点—填充—地基"三级密度模型（Hero-Filler-Debris Hierarchy）：

- **焦点岩石（Hero Rocks）**：体积最大，尺寸为玩家角色身高的1.5至3倍（以标准角色身高1.8米计，即2.7米至5.4米高）。每个独立视觉区域内放置1至3块，充当空间锚点，同时可用作高掩体或路径分叉的视觉引导物。
- **填充岩石（Filler Rocks）**：尺寸约为角色身高的0.3至0.8倍（0.54米至1.44米），分布在焦点岩石周围构成岩石群，推荐密度为每100平方米8至15块，块间距保持至少0.3米以防止网格互穿（Mesh Interpenetration）。
- **地基碎石（Debris）**：直径小于30厘米的小石块与岩屑，通常不赋予独立碰撞体，仅作为地面贴图的"噪声层"用于打断重复感，单块面数建议控制在200三角面以内以节省Draw Call。

三级模型的核心依据是视觉感知的**尺度对比原理**：大中小岩石同时出现时，人眼会将大岩石识别为"地形特征"、中等岩石识别为"障碍物"、小碎石识别为"地表纹理"，三者叠加才能产生自然岩石地貌的视觉层次感（Kremers, 2009）。若三级尺寸差异不足——例如所有岩石直径均在0.5米至1米之间——场景会呈现出人工铺设的单调感，俗称"停车场岩石综合征"。

### 碰撞体配置规范

岩石的碰撞体不应与其视觉网格完全贴合。标准规范如下：

1. **内缩偏移（Inward Offset）**：碰撞体表面相对视觉网格内缩5至10厘米，防止玩家走近时被网格边缘的微小凸起钩住产生"卡步"（Snag）现象。
2. **掩体高度分级**：用于掩体的岩石需满足双态遮蔽条件——玩家蹲姿胶囊体高度约0.9米时完全被遮挡，站姿胶囊体高度约1.8米时头部暴露约0.3米以上，形成"蹲下安全、站立有风险"的掩体博弈空间。因此掩体岩石的有效遮挡高度应介于0.95米至1.5米之间。
3. **碰撞类型分配**：
   - 焦点岩石与填充岩石：使用简化凸包碰撞（Simple Convex Hull），面数不超过26面。
   - 地基碎石（直径<30厘米）：设为"无碰撞"（No Collision），在移动端平台单场景具完整碰撞的岩石数量建议上限为200个。
4. **斜面可行走判定**：岩石表面坡度超过45度（部分引擎默认阈值为46度）时，角色应无法站立并产生滑落效果。需在引擎物理设置中将 `WalkableSlopeAngle` 设为45.0，并检查岩石侧面三角面的法线朝向是否触发该阈值。

### 材质混合与地面融合技术

岩石底部与地面之间的接缝（Seam）是视觉破绽高发区，有三种处理手段：

**① 顶点混合着色器（Vertex Blend Shader）**：在岩石网格底部顶点处，将岩石表面材质与地面泥土/草地材质按顶点色权重混合，过渡带宽度通常设为15至25厘米。顶点色R通道控制混合权重，当 R=1.0 时显示纯岩石材质，R=0.0 时显示地面材质。

**② 倾斜角随机化（Rotation Randomization）**：岩石放置时X轴与Y轴的旋转角度不应归零，而应在 ±3° 至 ±15° 范围内随机倾斜，模拟岩石因重力嵌入土地的自然沉降态。完全水平放置（Rotation = 0,0,0）的岩石在视觉上会立即被识别为人工摆放。Z轴（垂直轴）旋转则建议在 0° 至 360° 全范围随机，以消除岩石方向的一致性。

**③ 法线混合（Normal Blending）**：Unreal Engine 5 Nanite流程支持将岩石底面法线与地面法线进行插值对齐，混合权重公式为：

$$N_{blend} = \text{normalize}\left((1-\alpha) \cdot N_{rock} + \alpha \cdot N_{terrain}\right), \quad \alpha \in [0.0,\ 0.4]$$

其中 $\alpha$ 为混合系数，通常取0.2至0.3可在视觉融合与法线正确性之间取得平衡；$\alpha > 0.4$ 时岩石底面会呈现异常平坦感。

---

## 关键参数与工作流程

在Unreal Engine 5的PCG岩石散布流程中，以下代码展示了一个按密度层级生成岩石的PCG Graph节点逻辑片段：

```python
# PCG Graph伪代码：三级岩石密度散布规则
# 输入：地形高度图 HeightMap，生态区掩码 BiomeMask

def scatter_rocks(heightmap, biome_mask):
    # 第一级：焦点岩石，泊松盘采样，最小间距 15m
    hero_points = poisson_disk_sample(
        mask=biome_mask,
        min_distance=15.0,   # 单位：米
        max_points=3         # 每100m×100m区域上限3块
    )
    place_assets(hero_points, asset_tag="HeroRock",
                 scale_range=(2.7, 5.4),       # 高度范围（米）
                 rotation_x=(-10, 10),
                 rotation_y=(-10, 10),
                 rotation_z=(0, 360))

    # 第二级：填充岩石，围绕焦点岩石径向散布，间距 2m
    filler_points = radial_scatter(
        centers=hero_points,
        radius_range=(1.5, 6.0),
        count_per_center=(4, 8),
        min_distance=2.0
    )
    place_assets(filler_points, asset_tag="FillerRock",
                 scale_range=(0.54, 1.44),
                 rotation_x=(-8, 8),
                 rotation_y=(-8, 8),
                 rotation_z=(0, 360))

    # 第三级：地基碎石，全区域噪声散布，无碰撞
    debris_points = noise_scatter(
        mask=biome_mask,
        density=0.15,        # 每平方米0.15块
        min_distance=0.3
    )
    place_assets(debris_points, asset_tag="Debris",
                 collision=False,
                 scale_range=(0.1, 0.3))
```

上述流程中，`poisson_disk_sample` 保证焦点岩石之间不会过于拥挤，而 `radial_scatter` 则模拟自然界中大岩石风化崩落形成周围碎石群的地质现象。

---

## 实际应用案例

**案例一：《战争机器》系列的掩体岩石放置**
Epic Games在《战争机器》（Gears of War, 2006）的关卡设计中，将掩体岩石严格分为80厘米低掩体（玩家蹲伏可完全遮蔽）与110厘米高掩体（站立遮蔽）两类，并规定两块掩体岩石的纵深间距不得小于3米，以确保进攻方有可乘之机。设计师Rod Fergusson在GDC 2007演讲中披露，该系列每张地图平均包含约120块具备完整碰撞的掩体岩石，均经过手动高度校准。

**案例二：《荒野大镖客：救赎2》的岩石密度分区**
Rockstar Games在《荒野大镖客：救赎2》（Red Dead Redemption 2, 2018）的西部荒漠生态区中，采用了明显的三级密度分区策略：靠近河床的区域焦点岩石密度为每公顷6至9块，远离水源的平原区域降至每公顷2至3块，真实还原了河流侵蚀与沉积作用下的岩石分布规律。

**案例三：移动端密度上限的实际影响**
例如在Unity移动端项目中，一个300×300米的峡谷场景若放置超过250块具有MeshCollider的岩石，在中端设备（如2019年高通骁龙730芯片）上会导致物理线程帧时间超过4毫秒，引发明显卡顿。将直径小于0.4米的碎石全部改为无碰撞后，碰撞岩石数量降至180块，物理帧时间恢复至1.8毫秒以内。

---

## 常见误区

**误区一："岩石越多越自然"**
岩石密度超过每100平方米20块时，玩家的移动路径会被过度分割，产生"迷宫化"的地形，破坏战术移动的流畅性。自然界的岩石分布因侵蚀和沉积作用呈现明显的聚集-稀疏交替节律，而非均匀高密度铺满。

**误区二："小碎石也要加碰撞以提高真实感"**
直径小于30厘米的碎石赋予碰撞不会带来任何可感知的游戏体验提升，反而会在玩家步行其上时产生细微的"台阶感"抖动，同时显著增加物理计算开销。专业规范明确建议此类资产设为No Collision。

**误区三："岩石底部不需要特殊处理，埋进地面就行了"**
将岩石底部直接下沉进地面（Y轴负向移动）会导致两个问题：其一，岩石网格与地形网格在交叉处产生Z-fighting（深度闪烁）；其二，岩石侧面与地面之间仍存在明显材质断层。正确做法是使用顶点混合着色器处理过渡带，同时将岩石底面仅略微下沉3至5厘米（而非完全埋入）以遮挡底部边缘。

**误区四："旋转归零让场景更整洁"**
所有岩石Rotation归零是新手最常见的失误之一。人眼对水平放置物体的"人工感"极为敏感，即使 ±5° 的轻微倾斜也能大幅提升"自然嵌入地面"的视