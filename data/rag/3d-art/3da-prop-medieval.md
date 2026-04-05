---
id: "3da-prop-medieval"
concept: "中世纪道具"
domain: "3d-art"
subdomain: "prop-art"
subdomain_name: "道具美术"
difficulty: 3
is_milestone: false
tags: ["风格"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 82.9
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



# 中世纪道具

## 概述

中世纪道具是3D美术中专注于公元500年至1500年欧洲历史时期器物的建模与材质还原工作，核心对象包括单手剑（Arming Sword）、双手大剑（Zweihänder，刃长约100–120 cm）、锁子甲（Hauberk）、哥特式板甲（Gothic Plate Armor）、圆盾（Buckler，直径30–45 cm）和骑士盾（Heater Shield）等具有鲜明时代特征的战斗用品。与幻想风格道具不同，中世纪道具的制作要求参照真实历史文物的物理属性——熟铁（Wrought Iron）、高碳钢、皮革、橡木与椴木的具体表面质感——而非依赖设计师的想象力重新发明材料外观。

这一方向在游戏美术领域伴随着写实风格RPG的兴起而专业化。《骑马与砍杀》（TaleWorlds，2008年）对500+种中世纪武器的还原需求，以及《黑暗之魂》系列（FromSoftware，2011年起）对盔甲套装精细分件的要求，促使3D美术师形成了一套专门的材质分层与磨损系统工作流。大英博物馆（British Museum）自2018年启动的3D扫描馆藏计划已将中世纪文物数字化，其中包括维京长剑、诺曼盾等精确参考资产，为艺术家提供了比图片参考更精确的几何与材质基准。

制作中世纪道具的关键挑战在于**历史真实性与视觉可读性之间的平衡**：真实的12世纪铁器往往布满红锈、暗斑与不规则磨损，但过度写实会导致道具在游戏画面中失去轮廓辨识度。因此需要在PBR工作流中精确控制金属度（Metallic）与粗糙度（Roughness）的空间分布，而非简单套用统一数值。参考资料可见 Alan Williams 所著《The Knight and the Blast Furnace: A History of the Metallurgy of Armour in the Middle Ages》（Brill, 2003），该书详细记录了中世纪锻造工艺对钢铁表面质感的影响，是材质数值校准的重要文献依据。

---

## 核心原理

### 金属材质的PBR参数体系

中世纪铁制武器与现代不锈钢在PBR材质上存在根本性参数差异，不可混用现代金属的预设值。中世纪熟铁（Wrought Iron）和高碳钢的金属度（Metallic）值通常设置在 **0.85–0.95** 之间，但粗糙度（Roughness）因锻造工艺远高于现代抛光钢：

| 材质区域 | Metallic | Roughness | Base Color（HSV V值） |
|---|---|---|---|
| 刀身主体（锻铁面） | 0.90 | 0.45–0.60 | 0.18–0.25 |
| 刀锋磨砺带（约5%宽） | 0.92 | 0.15–0.22 | 0.35–0.45 |
| 护手边缘碰撞区 | 0.85 | 0.65–0.75 | 0.12–0.18 |
| 氧化锈斑区域 | 0.10–0.20 | 0.80–0.92 | 暖褐色，V≈0.30 |

刀锋区域（Blade Edge）需要单独绘制一条粗糙度较低（约0.18–0.22）的高光带，模拟研磨后的锋利斜面（Bevel），该高光带宽度通常仅为刀身可见宽度的 **5%–8%**，在1024×1024贴图中对应约20–40像素宽度。若使用2K贴图则加倍，像素宽度需同比缩放以保持视觉比例一致。

### 磨损分层的力学逻辑

中世纪道具的磨损遵循接触力学规律，而非随机分布，这是区分专业美术与新手的核心标准之一。以骑士长剑（Longsword）为例，其磨损分布具有以下力学依据：

- **刀身1/3处（Strong，强段）**：格挡主力区，横向滑动划痕密集，Roughness局部提高0.15–0.25，并有约0.5–2 mm深度的缺口法线信息；
- **刀身中段**：使用频率较低，基础材质最接近原始锻造状态；
- **刀身前1/3（Weak，弱段）至刀尖**：刺击墙缝与地面的碰撞区，尖端有碎裂缺口，法线贴图中需要手工雕刻3–5个不规则缺口而非用随机噪波代替；
- **护手（Quillon）末端**：格挡碰撞集中区，Base Color明度降低，凹痕内部积灰（AO遮罩驱动积灰层透明度）；
- **剑柄（Grip）皮革包裹处**：掌心油脂渗透后皮革颜色向深棕色偏移，Roughness降低约0.08–0.12（皮革变光滑），同时皮革条带边缘出现开裂法线细节。

在Substance Painter的图层堆栈中，标准的中世纪武器分层结构如下：

```
Layer Stack（从底到顶）:
1. [Fill] Base Metal        — Metallic 0.90, Roughness 0.50
2. [Fill + Mask: AO]        — 凹槽积灰，Roughness +0.20
3. [Fill + Mask: Curvature] — 凸起磨光，Roughness -0.20，Color +0.08亮
4. [Fill + Mask: 手绘遮罩]  — 刀锋高光带，Roughness 0.18
5. [Fill + Mask: 手绘遮罩]  — 氧化层，Metallic -0.70，Roughness +0.35
6. [Fill + Mask: 手绘遮罩]  — 刃部划痕（Alpha划痕笔刷）
7. [Fill + Mask: 手绘遮罩]  — 柄部皮革油污，Color向暖褐偏移
```

该图层结构确保磨损在语义上可解释：每一层对应一种物理成因，而非将所有效果混合在同一层中导致后期难以修改。

### 锁子甲的高频细节处理

锁子甲（Chainmail/Hauberk）是中世纪道具中多边形面数与贴图分辨率矛盾最突出的对象：一件全身锁子甲由约15,000–30,000个铁环组成，若逐一建模会导致面数超过1,000万，完全不适合实时渲染。标准解决方案是**法线贴图烘焙 + Roughness变化模拟**的二合一方法：

1. 在ZBrush中制作一块约8×8环的锁子甲瓦片高模（Tile），烘焙为Tileable Normal Map（分辨率至少1024×1024，Texel密度建议128 px/unit）；
2. 在Substance Painter中将该法线贴图以Tile方式叠加在低模（平面或曲面）上；
3. 在Roughness通道叠加对应的铁环边缘高光遮罩，铁环接触点（受力集中）Roughness约0.40，铁环中部（磨损较少）约0.60；
4. 整体氧化层遮罩使用 Grunge Map（Substance库中的 Grunge Rust Fine 图层效果，强度约0.25–0.40）均匀叠加。

---

## 关键公式与贴图分辨率计算

在制作中世纪道具时，贴图分辨率与模型屏幕占比之间的关系决定了细节是否可见。游戏行业常用的 **Texel Density（纹素密度）** 标准公式为：

$$
TD = \frac{TextureResolution}{UVArea_{world}}
$$

其中 $TD$ 单位为 px/unit（像素/世界单位），$TextureResolution$ 为贴图像素边长，$UVArea_{world}$ 为该 UV 岛对应的世界空间面积（单位²）。

对于第三人称游戏中手持武器（通常屏幕占比约5%–15%），推荐 $TD = 512$ px/m。以一把刃长 90 cm、刃宽 4 cm 的骑士剑为例：

$$
UVArea_{blade} = 0.90 \times 0.04 \times 2 = 0.072 \text{ m}^2
$$

$$
TextureResolution_{min} = 512 \times \sqrt{0.072} \approx 512 \times 0.268 \approx 137 \text{ px}
$$

这意味着刃部的 UV 岛在 1024 贴图中至少需要占用约 **137 像素的线性尺寸**，若 UV 展开时刃部岛过小，锻铁划痕等高频细节将在目标分辨率下模糊不可见。实际制作中建议将刃部单独拆分 UV 组并适当放大，而将剑柄（视觉焦点较低）缩小，以在同一张贴图内优化像素分配。

---

## 实际应用

### 骑士长剑全流程示范

**高模阶段（ZBrush）**：首先在 ZBrush 中对照历史参考（推荐使用 Oakeshott 剑型分类系统，其中 Type XIII 为13世纪标准骑士剑，刃长 83–95 cm，剑柄长 16–18 cm）建立基础形态。护手（Quillon）的铸造接缝线需在高模阶段用 ZBrush 的 Dam_Standard 笔刷刻入，宽度约 0.3–0.5 mm（对应世界尺度），深度约 0.15 mm，而非依赖法线贴图假装有接缝。

**低模阶段（Maya/Blender）**：整剑低模面数控制在 800–1500 三角面（游戏实机标准），UV 展开时刃部、护手、剑柄各占独立 UV 岛，硬边（Hard Edge）必须在 UV 缝合处断开以避免法线烘焙漏光。

**烘焙阶段（Marmoset Toolbag 4）**：使用 Cage 烘焙方式，Cage Offset 设置为 0.03–0.05（视高低模间距调整），建议开启 **Skew Correction** 以减少护手曲面处的法线偏差。烘焙分辨率使用 4096×4096 作为工作贴图，交付时下采样至 2048×2048。

**材质阶段（Substance Painter）**：按照前文"磨损分层的力学逻辑"所述的7层图层结构逐层构建，最终导出至引擎所需格式（UE5使用ORM打包通道：Occlusion→R，Roughness→G，Metallic→B）。

### 案例：《骑马与砍杀：领主》的武器材质策略

《骑马与砍杀：领主》（Bannerlord，TaleWorlds，2022年正式版）中大量武器采用了**模块化部件系统**——剑柄、护手、刃部分件单独制作贴图，在运行时组合。这要求每个部件的材质风格必须在色调（Base Color 色温统一在 5500–6500K 冷调金属范围内）、Roughness 基准值（锻铁统一在 0.45 ± 0.10 范围浮动）上保持一致，否则随机组合后各部件会产生视觉脱节感。这一工业化策略是大规模历史类游戏中解决道具多样性与制作成本矛盾的典型方案。

---

## 常见误区

**误区一：对所有金属使用相同的高Metallic值。** 中世纪铁器并非纯净金属，其表面普遍存在氧化层、碳化层和杂质斑点。将护手上的碰撞凹痕区域 Metallic 设为 0.95 是错误的——凹痕内部积尘区域的 Metallic 应降低至 0.20–0.40，否则凹痕将呈现为"高亮坑"而非"暗色伤痕"。

**误区二：木质盾牌使用垂直木纹。** 历史上中世纪盾牌（如诺曼 Kite Shield）的木板为横向拼接工艺，木纹方向为水平走向。使用垂直木纹是对历史工艺的误读，会被具备历史知识的玩家和美术总监立即识别。

**误区三：锁子甲用噪波贴图代替烘焙法线。**