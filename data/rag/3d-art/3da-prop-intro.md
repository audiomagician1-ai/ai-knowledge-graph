---
id: "3da-prop-intro"
concept: "道具美术概述"
domain: "3d-art"
subdomain: "prop-art"
subdomain_name: "道具美术"
difficulty: 1
is_milestone: true
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.92
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "Digital Modeling"
    author: "William Vaughan"
    year: 2011
    isbn: "978-0321700896"
  - type: "textbook"
    title: "The Complete Guide to Game Art"
    author: "Rick Emerson"
    year: 2020
  - type: "conference"
    title: "Prop Art Pipeline for AAA Games"
    authors: ["Clinton Crumpler"]
    venue: "GDC 2018"
scorer_version: "scorer-v2.0"
---
# 道具美术概述

## 概述

道具美术（Prop Art）是 3D 游戏美术中负责创建游戏世界中所有非角色、非环境的可交互或装饰性物件的专业方向。William Vaughan 在《Digital Modeling》（2011）中将 Prop 定义为"任何角色可以拿起、使用或与之互动的物体——从一把剑到一个垃圾桶"。

在 AAA 制作管线中，道具美术是体量最大的资产类别。Clinton Crumpler 在 GDC 2018 中分享：一个中型开放世界项目需要 **3,000-8,000 个独特道具**，占总美术资产的 60-70%。单个道具从概念到引擎内资产的完整流程通常需要 1-5 天（视复杂度）。

## 道具的分类体系

| 类别 | 定义 | 多边形预算 | 实例 |
|------|------|-----------|------|
| Hero Props | 特写镜头/核心剧情物品 | 10K-50K tris | 《战神》利维坦之斧 |
| Primary Props | 玩家常见/可交互 | 2K-10K tris | 武器、宝箱、门 |
| Secondary Props | 环境填充/装饰 | 500-2K tris | 桌椅、瓶罐、书本 |
| Background Props | 远景装饰 | 100-500 tris | 远处建筑装饰、树桩 |
| Modular Kit Pieces | 可重复拼接的模块 | 1K-5K tris | 墙壁模块、管道、栅栏 |

**Nanite 时代的变化**：UE5 Nanite 取消了传统多边形预算——Hero Prop 可以直接使用百万面 ZBrush 雕刻导入。但非 Nanite 平台（移动端、Switch）仍需严格控制。

## 道具制作的标准流水线

```
1. 参考收集 & 概念设计（0.5-1天）
   └─ PureRef 收集 20-50 张参考图
   └─ 确定材质、比例、风格

2. 高模雕刻（1-3天）
   └─ ZBrush/Blender 雕刻细节
   └─ 不考虑面数（可达数百万面）
   └─ 关注：轮廓剪影、表面细节、比例

3. 低模重拓扑（0.5-1天）
   └─ 手动重拓（TopoGun）或自动（ZRemesher/InstantMesh）
   └─ 目标面数：类别预算内
   └─ 关注：干净的布线、合理的UV展开

4. UV展开（0.5天）
   └─ RizomUV/UVLayout/Blender
   └─ Texel Density 统一（通常 512-1024 px/m）
   └─ 最小化接缝，隐藏接缝在不可见处

5. 烘焙（0.5天）
   └─ 高模 → 低模 烘焙法线/AO/Curvature/ID
   └─ Marmoset Toolbag / Substance Painter
   └─ 关键：确保法线贴图无接缝伪影

6. 材质制作（1-2天）
   └─ Substance Painter / Quixel Mixer
   └─ PBR 贴图集：BaseColor + Normal + Roughness + Metallic
   └─ 分辨率：1K（小道具）→ 2K（标准）→ 4K（Hero）

7. 引擎集成 & 优化（0.5天）
   └─ 导入 FBX → 设置材质实例 → LOD 生成
   └─ 碰撞体设置（简单/复杂）
   └─ 光照测试
```

总计：一个 Primary Prop 约 3-5 工作日。工业化团队可通过 Kitbash/程序化辅助压缩到 1-2 天。

## PBR 材质的四通道标准

| 贴图 | 内容 | 范围 | 注意事项 |
|------|------|------|---------|
| Base Color (Albedo) | 固有色，无光照信息 | sRGB, 30-240 亮度 | 禁止烘入 AO 或高光 |
| Normal Map | 表面法线偏移 | Tangent Space [-1,1] | OpenGL(Y+) vs DirectX(Y-) |
| Roughness | 表面粗糙度 | Linear, 0(镜面)-1(漫射) | 0.0-0.04 = 镜子, 0.8-1.0 = 粗布 |
| Metallic | 金属/非金属 | Linear, 0 或 1（极少中间值） | 现实中几乎是二值图 |

**通道打包**：UE5 默认将 Metallic(R) + Roughness(G) + AO(B) 打包为单张 ORM 贴图，节省一次纹理采样。

## Texel Density（纹素密度）

确保整个游戏中所有道具的贴图分辨率视觉一致：

```
Texel Density = 纹理像素数 / 世界空间面积
标准值（AAA, 1080p）: 512-1024 px/m
标准值（移动端）: 256-512 px/m
标准值（VR, 高清）: 1024-2048 px/m
```

**检查工具**：Substance Painter 的 Texel Density 热力图、UE5 的 Texel Density 可视化模式。

## 常见误区

1. **忽视剪影优先**：道具辨识度首先取决于剪影（轮廓），其次才是细节纹理。在《堡垒之夜》中，武器必须在 50m 外仅凭剪影可识别
2. **Texel Density 不统一**：一把剑 2K 贴图（2048px/m），旁边的桶 256px 贴图（128px/m）→ 视觉上桶看起来"糊"。同类道具应保持 ±20% 的 TD 偏差
3. **Base Color 烘入光照**：在 Albedo 中画入阴影或高光 → PBR 光照计算产生"双重光照"伪影。Base Color 只存储固有色

## 知识衔接

### 先修知识
- **3D美术基础** — 理解基本的 3D 概念（网格、UV、材质）

### 后续学习
- **高模雕刻** — ZBrush 雕刻技术和细节处理
- **低模制作** — 重拓扑、布线规范、面数优化
- **UV展开** — 高效UV展开和密度控制
- **PBR材质** — 基于物理的材质理论和制作
- **贴图烘焙** — 法线/AO/曲率的烘焙技术

## 参考文献

1. Vaughan, W. (2011). *Digital Modeling*. New Riders. ISBN 978-0321700896
2. Crumpler, C. (2018). "Prop Art Pipeline for AAA Games." GDC 2018.
3. Allegorithmic (2024). "PBR Guide." Substance 3D Documentation.
4. Epic Games (2024). "Static Mesh Pipeline." Unreal Engine 5 Documentation.
