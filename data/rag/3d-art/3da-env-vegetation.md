---
id: "3da-env-vegetation"
concept: "植被制作"
domain: "3d-art"
subdomain: "environment-art"
subdomain_name: "环境美术"
difficulty: 3
is_milestone: true
tags: ["实战"]

# Quality Metadata (Schema v2)
content_version: 4
quality_tier: "pending-rescore"
quality_score: 41.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.414
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 植被制作

## 概述

植被制作是3D环境美术中专门针对树木、灌木、草地等自然植物的建模与渲染技术体系。与硬表面建模不同，植被的有机形态、半透明叶片和大规模重复铺设带来了独特的技术挑战，需要在视觉真实度和运行效率之间精确平衡。

植被制作技术自1990年代游戏工业化以来经历了显著演变。早期采用十字面片（Cross Billboard）简单模拟树冠，到2000年代中期，《孤岛危机》（Crysis，2007年）引入了基于SpeedTree工具的分层植被系统，将单棵树的面片数精确控制在数百至数千三角面之间，并配合实时风力模拟，成为行业标杆。如今，虚幻引擎5的Nanite虽然支持高面数几何体，但植被领域仍因数量庞大而需要专门的LOD和实例化渲染方案。

植被直接决定了开放世界游戏的性能瓶颈。一片森林场景中，仅草地实例就可能达到数十万甚至数百万个，若不采用专门优化手段，GPU绘制调用（Draw Call）将成灾难性负载。掌握植被制作技术，意味着同时掌握美术规范制定、Shader编写逻辑和LOD策略设计三个层面的知识。

---

## 核心原理

### Alpha测试与半透明叶片渲染

植被叶片通常使用 **Alpha Cutout（Alpha剪切）** 而非全透明混合。原因在于：透明排序（Transparency Sorting）在大量叶片叠加时极难正确计算，而Alpha测试可在不透明渲染队列中完成，节省排序开销。标准做法是在叶片贴图的Alpha通道存储遮罩，Shader中设定一个阈值（通常为0.5或可调参数），低于阈值的像素直接丢弃（discard）。

叶片贴图规格一般为 **512×512** 或 **1024×1024**，通常将多片叶子排列在一张Atlas贴图上，一张Atlas可容纳6～16种不同叶形，以减少材质切换次数。除固有色（Albedo）贴图外，还需制作法线贴图（Normal Map）和透射贴图（Translucency Map），后者在叶片被光线从背面照射时模拟出真实的绿色透光效果。

### Billboard技术与面片树

Billboard（公告板）技术是植被远景的核心方案，分为两种：
- **摄像机朝向Billboard（Camera-Facing Billboard）**：面片始终朝向摄像机，适合草地和灌木，计算成本低。
- **八向Billboard（8-direction Billboard）**：预渲染植物8个方向的照片，根据摄像机角度切换，适合远景树木，视觉质量高于单一朝向方案。

SpeedTree的标准LOD链通常包括：全3D模型（LOD0）→ 简化3D模型（LOD1/LOD2）→ 结合面片叶簇的混合模型（LOD3）→ 纯Billboard（LOD4）→ 剔除（Cull）。每个LOD切换距离需要根据场景摄像机FOV和植被高度单独标定。

### LOD策略与实例化渲染

**层级细节（Level of Detail，LOD）** 是植被性能优化的核心机制。一棵标准游戏树的面数通常按如下比例递减：

| LOD级别 | 大约三角面数 | 适用距离参考 |
|--------|------------|------------|
| LOD0   | 3000～8000 | 0～15m     |
| LOD1   | 800～2000  | 15～40m    |
| LOD2   | 200～600   | 40～80m    |
| LOD3   | 50～150（面片混合）| 80～150m |
| Billboard | 2～4面片 | 150m以上   |

**GPU实例化（GPU Instancing）** 允许同一棵树的成千上万个副本仅占用一次Draw Call。虚幻引擎的 **Hierarchical Instanced Static Mesh（HISM）** 和Unity的 **GPU Instancer** 都基于此原理，同时结合摄像机视锥剔除和遮挡剔除，大幅降低CPU提交负担。

### 风力动画与顶点偏移

植被的风力效果通过 **顶点着色器（Vertex Shader）中的顶点偏移（Vertex Offset）** 实现，而非骨骼动画。通用公式为：

```
VertexOffset = sin(Time × WindFrequency + VertexWorldPos × PhaseOffset) × WindStrength × BendMask
```

其中`BendMask`通常存储在顶点色的R通道中，树梢顶部值为1（最大摆动），树干根部值为0（固定不动）。叶片颤动与树干弯曲使用不同频率和幅度叠加，以区分宏观摇摆和微观颤动。SpeedTree 8提供了现成的风力预设，包括Gentle（柔和）、Storm（暴风）等档位，对应不同的频率和振幅参数。

---

## 实际应用

**草地系统实现**：在虚幻引擎中，草地通常通过 `Landscape Grass Type` 资产配合地形材质自动生成。美术需要制作2～4种草丛面片变体，每种变体包含不同的颜色偏移和高度变化。草地密度参数（GrassDensity）一般设置在每平方米20～60株之间，过高则性能急剧下降，过低则地面透底明显。草地通常使用摄像机朝向Billboard，不制作LOD，而是依靠 **Cull Distance（剔除距离）** 控制渲染范围，典型值为50～80m。

**灌木制作流程**：灌木通常基于"骨干面片+叶簇面片"结构建模，骨干使用真实几何体，叶簇则为平面面片集合。一棵标准游戏灌木LOD0面数控制在500～1500三角面，贴图集（Texture Atlas）中叶形样本不少于4种以保证视觉多样性。

**与地形的整合**：地形制作完成后，植被通常通过植被绘制工具（如虚幻的Foliage Mode或Unity的Terrain Detail）叠加布置，美术需要确保植被根部与地形法线方向一致，避免出现"浮空"或"插地"的穿模问题，可在植被实例设置中启用 `Align to Normal` 选项解决。

---

## 常见误区

**误区一：所有植被都应使用透明混合（Alpha Blend）**
初学者常将叶片材质设置为半透明（Transparent）混合模式，认为这样边缘更柔和。实际上，大量透明面片叠加会导致Over-Draw（过度绘制）暴涨，在移动平台可使帧率下降50%以上。正确做法是叶片使用Alpha Cutout（Masked材质），仅边缘过渡区域在必要时结合Dither Alpha抖动技术模拟柔和效果，既保持不透明队列渲染效率，又减弱硬边感。

**误区二：LOD0越精细越好**
部分美术为了近距离效果极致，将LOD0制作到数万三角面。但植被的视觉复杂度主要由叶片数量和贴图质量决定，而非纯几何面数。分支几何体超过8000面后，视觉提升微乎其微，反而使LOD0的三角面剔除成本上升，在植被密集区造成严重的三角面瓶颈（Triangle Bottleneck）。游戏行业经验表明，LOD0面数控制在3000～6000三角面对于主流平台是最佳区间。

**误区三：风力动画可以用骨骼蒙皮实现**
少数项目尝试为树木绑定骨骼并使用骨骼动画驱动风力效果。这在单棵展示场景没有问题，但当场景中存在数百棵树时，每棵树的骨骼动画均需要独立的蒙皮计算，无法批次合并，GPU实例化完全失效，性能代价是顶点偏移方案的数十倍。植被风力必须在Vertex Shader中以数学公式实现，这是不可绕过的约束。

---

## 知识关联

**前置知识——地形制作**：植被布置建立在已完成的地形网格之上。地形的高度图精度直接影响植被根部对齐的准确性，地形材质中的混合权重（Blend Weight）数据还可作为植被密度的驱动输入，例如沙地区域自动降低草地密度。植被制作阶段需要与地形制作阶段约定坐标系比例、单位精度（通常为1单位=1厘米）以保证植被实例的Y轴缩放不出现异常。

**扩展方向——程序化植被生成**：在植被制作手工流程熟练之后，可进一步学习基于规则的程序化植被分布系统，如虚幻5的PCG（Procedural Content Generation）框架。PCG可将植被分布逻辑（坡度限制、高度区间、噪波遮罩）转化为可参数化的节点图，从而在保证手工美术质量规范的前提下，用极少人力生成覆盖数平方公里的自然植被分布。
