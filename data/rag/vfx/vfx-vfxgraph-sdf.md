---
id: "vfx-vfxgraph-sdf"
concept: "SDF交互"
domain: "vfx"
subdomain: "vfx-graph"
subdomain_name: "VFX Graph"
difficulty: 4
is_milestone: false
tags: ["高级"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.5
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.429
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# SDF交互

## 概述

SDF（Signed Distance Field，有向距离场）交互是VFX Graph中一种利用三维距离场数据来驱动粒子行为的技术机制。其核心在于"有向"二字——距离值带有正负符号，正值表示粒子处于形状外部，负值表示粒子处于形状内部，零值则精确标记形状表面。这种数学表达方式使粒子系统能够以极低的运算成本感知复杂三维形状的空间关系。

在Unity VFX Graph中，SDF数据以3D纹理（Texture3D）的形式存储，每个体素保存该位置到最近表面的有符号距离。Unity提供了SDF Baker工具（在Package Manager中随VFX Graph包附带），可以将任意Mesh烘焙为SDF纹理，分辨率通常设置为32³到128³之间，分辨率越高精度越好但内存占用也越大。

SDF交互之所以在VFX Graph中具有重要价值，是因为它解决了粒子与任意形状碰撞时的性能瓶颈问题。传统Mesh碰撞需要逐三角面检测，而SDF将整个几何体预计算为一个查询O(1)复杂度的数据结构——给定任意三维坐标，只需采样一次纹理即可得到该点与目标形状之间的精确距离，从而在GPU上并行处理数百万粒子与复杂形状的空间交互。

---

## 核心原理

### 有向距离的数学含义与存储格式

SDF纹理中每个体素存储的浮点值 `d` 表示：空间点 `p` 到最近表面的距离，其中 `d > 0` 为外部，`d < 0` 为内部，`d = 0` 为表面。Unity SDF Baker默认将距离值归一化到 `[-1, 1]` 范围，并映射为 `[0, 1]` 的纹理值（存储值 = `d / maxDist * 0.5 + 0.5`）。读取时需要反算：实际距离 = `(采样值 - 0.5) * 2 * 包围盒半径`。在VFX Graph的Operator面板中，**Sample SDF** 节点自动处理这套解码逻辑，输出直接可用的世界空间距离值。

### VFX Graph中SDF交互的节点结构

VFX Graph通过以下节点链完成SDF交互：

1. **SDF属性绑定**：在Blackboard中声明一个 `Texture3D` 类型属性，并绑定烘焙好的SDF纹理资产。
2. **Sample SDF节点**：接受粒子位置（Position）和SDF纹理、SDF变换矩阵（Transform）作为输入，输出该粒子位置处的有符号距离值 `float`。
3. **梯度计算**：通过对SDF沿X、Y、Z方向各偏移约0.01个单位分别采样，计算数值梯度向量 `∇SDF`，该梯度方向恒指向最近表面的法线方向，可直接用作粒子反弹或滑动的法向量。
4. **条件响应Block**：将距离值与阈值（通常为粒子半径）比较，当 `d < radius` 时触发位置修正、速度反射或消亡等逻辑。

### 碰撞响应计算

最典型的SDF碰撞响应是速度反射，公式如下：

```
V_reflect = V - 2 * dot(V, N) * N
```

其中 `V` 为粒子当前速度向量，`N` 为SDF梯度归一化后的表面法线，`dot(V, N)` 为速度在法线方向上的分量。VFX Graph的 **Conform to SDF** Block直接封装了这套计算，并额外提供 `Attraction Speed`（吸引速度）和 `Stick Distance`（粘附距离）参数，控制粒子在接近表面时是被吸附还是被排斥，两个参数均以世界空间单位（米）表示。

### SDF变换矩阵的动态绑定

SDF纹理本身存储的是局部空间中的距离信息，当绑定的GameObject发生位移或旋转时，需要将粒子世界坐标变换到SDF局部空间再采样。VFX Graph的 **Transform** 属性（类型为 `Transform`）可直接绑定场景中的GameObject，Graph会自动提取其TRS矩阵，实现SDF随角色或道具的实时移动而联动——这是SDF交互支持动态形状跟随的关键机制。

---

## 实际应用

**角色周围粒子的形变效果**：将角色Mesh烘焙为64³分辨率的SDF纹理，在VFX Graph的Update Context中添加 **Conform to SDF** Block，设置 `Attraction Speed = 2.0`，`Stick Distance = 0.05`。粒子会在角色表面0.05米范围内被吸附，形成沿角色体表流动的能量粒子效果。将SDF的Transform绑定到角色骨骼根节点后，整套效果可跟随角色移动，常用于ARPG中角色技能动画的VFX表现。

**粒子填充三维形状**：利用 `d < 0` 的条件判断粒子是否处于SDF内部，配合 **Set Position（Sequential）** 模式在形状内部随机生成粒子，实现"液体注入容器"的视觉效果。容器形状可以是任意复杂Mesh，只需提前烘焙SDF纹理即可，无需编写任何自定义HLSL代码。

**SDF驱动的粒子湍流**：将SDF梯度方向乘以噪声扰动值后叠加到粒子速度，可生成粒子沿表面曲率方向流动的有机形态。具体做法是采样SDF后手动计算三轴偏导得到法线，再与Curl Noise输出做向量叉积（Cross Product），结果即为切线方向的湍流力，常用于烟雾绕过障碍物的视觉模拟。

---

## 常见误区

**误区一：直接使用Mesh碰撞替代SDF**
部分开发者在VFX Graph中尝试通过Collision Shape节点的Mesh模式处理复杂形状碰撞。但VFX Graph的Mesh碰撞节点实际上仅支持凸包（Convex Hull）近似，对凹形表面精度极差。而SDF可以精确表达任意拓扑形状（包括空心体、镂空结构），且GPU采样成本固定为一次Texture3D查找，与Mesh的多边形数量无关。错误地相信"Mesh碰撞更精确"会导致凹形区域穿模且性能下降。

**误区二：SDF烘焙分辨率越高越好**
将SDF分辨率设置为256³时，一张单通道16位浮点SDF纹理的内存占用为 256×256×256×2 字节 = 32MB，远超多数特效的合理开销。对于角色级别的道具，64³（0.5MB）通常已足够，128³（4MB）适合精度要求较高的场景。SDF精度不足体现为表面碰撞点出现锯齿状跳动，此时应优先检查包围盒尺寸与分辨率的比值，而非无节制提升分辨率。

**误区三：SDF可以实时烘焙用于蒙皮动画**
SDF烘焙是一个离线预计算过程，Unity的SDF Baker无法在运行时对蒙皮网格的每一帧姿态重新烘焙。因此SDF交互只能精确描述刚体形状，对骨骼动画形变的角色只能使用绑定根节点的整体平移旋转跟随，而无法逐帧更新形变后的距离场。若需要蒙皮变形的精确SDF，需要借助第三方插件或自定义Compute Shader实现运行时SDF更新，这超出了VFX Graph内建节点的能力范围。

---

## 知识关联

**前置概念——输出模式**：理解输出模式（Output Context的Mesh/Billboard/Strip等类型）是使用SDF交互的基础，因为SDF的 `Conform to SDF` Block只能放置在Update Context中，其结果作用于粒子的速度和位置属性，最终由Output Context中选定的输出模式渲染。若不理解Update和Output两个Context的职责分工，会错误地将SDF采样节点放置在Output中导致逻辑无效。

**后续概念——GPU事件**：SDF交互为GPU事件（GPU Event）提供了精确的触发条件。当粒子通过 `Sample SDF` 判断到距离值低于阈值（如 `d < 0.01`）时，可以触发GPU事件生成子粒子系统——例如粒子撞击SDF表面后，在碰撞点处喷射火花子粒子。GPU Event接收来自SDF碰撞的位置、法线和速度数据作为子粒子的初始属性，形成完整的碰撞响应特效链路，而SDF的梯度向量正好提供了子粒子所需的精确表面法线。
