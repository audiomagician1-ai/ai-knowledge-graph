---
id: "ta-proxy-mesh"
concept: "代理网格"
domain: "technical-art"
subdomain: "lod-strategy"
subdomain_name: "LOD策略"
difficulty: 2
is_milestone: false
tags: ["核心"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "S"
quality_score: 82.9
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---


# 代理网格

## 概述

代理网格（Proxy Mesh）是一种专门为复杂三维资产手动或自动生成的超低面数替代几何体，其面数通常控制在原始资产的1%至5%之间。与保留表面细节的LOD1/LOD2不同，代理网格的设计目标是在**物理碰撞检测、极远距离渲染和实时阴影投射**这三个特定场景下，以最低的几何复杂度换取最大的性能收益。代理网格在引擎管线中走独立通道，不参与正常的LOD切换序列，而是被单独标记为"碰撞代理（Collision Proxy）"或"阴影代理（Shadow Proxy）"。

代理网格的系统化应用约始于2010年前后，随虚幻引擎4（UE4）和寒霜引擎（Frostbite）在开放世界项目中的大规模部署而成熟。传统手动LOD链通常止步于LOD3（面数在几百个三角形量级），代理网格则进一步突破极限，常见面数区间为32至512三角形。《战地4》（2013年，寒霜引擎）是最早公开讨论系统性代理网格管线的商业项目之一，其建筑资产的碰撞代理平均面数为原始资产的0.8%。

代理网格的核心价值在于物理引擎运算开销与几何体面数之间的强相关性。一座由32,000个三角形构成的哥特式建筑，若使用原始网格进行物理碰撞，每帧的碰撞检测成本可能高达使用200面代理网格的**160倍**。在包含数百栋建筑的开放世界中，这一差距直接决定游戏能否维持60fps的物理模拟帧率。

---

## 核心原理

### 凸包与包围体的几何策略

代理网格的构建通常不追求外轮廓的精确还原，而是遵循"最小凸近似（Minimal Convex Approximation）"原则。对于规则的建筑构件，技术美术师会将其分解为若干个凸多边形体（Convex Hull），每个凸包控制在20面以内。虚幻引擎的物理系统（PhysX/Chaos）对凸包碰撞的处理效率比任意网格碰撞（Arbitrary Mesh Collision）高出约4至8倍，因此将一座复杂建筑拆解为8个凸包的碰撞方案，远优于用单一1000面网格贴合建筑外形的方案。

阴影专用代理网格的构建逻辑则截然不同：阴影只关心遮挡轮廓，因此阴影代理可以忽略所有凹陷细节（门洞、窗框、雕花），只需保留从主要光源方向可见的外轮廓剪影。一根带有螺旋纹路的石柱，其可见阴影轮廓用8个面的八棱柱即可近似；而碰撞代理可能需要额外保留柱顶雕花的12面近似体。两者的面数预算和构建逻辑互不干扰，在引擎资产管线中分别挂载于不同的碰撞通道（Collision Channel）和阴影通道（Shadow Pass）。

### 面数预算与屏幕覆盖率的计算关系

代理网格的面数上限由"屏幕覆盖率阈值（Screen Coverage Threshold）"决定。当资产在屏幕上的投影面积低于屏幕总像素数的0.1%（在1080p分辨率下约为2073像素），切换至代理网格在视觉上不会被玩家察觉。此时资产的合理代理面数遵循以下经验公式（参考 Wihlidal, 2017，GDC演讲《Optimizing the Graphics Pipeline with Compute》相关方法论）：

$$T_{proxy} \approx P_{screen} \times 0.05$$

其中 $T_{proxy}$ 为代理网格目标面数，$P_{screen}$ 为当前帧该资产的屏幕投影像素数。在2073像素覆盕时，约104面的代理网格即达到肉眼极限。绝大多数代理网格在128面以下即可满足远景渲染需求，极复杂的建筑群也少有超过512面的代理网格。

以一栋占屏幕0.05%（约1036像素）的建筑为例：

$$T_{proxy} \approx 1036 \times 0.05 \approx 52 \text{ 面}$$

这意味着一个52面的代理网格在该距离下已经是视觉上的过剩精度，可进一步削减至32面。

### 自动代理生成工具的工作机制

Unreal Engine的**Hierarchical LOD（HLOD）系统**和Simplygon的**Proxy LOD功能**均支持自动代理网格生成。其核心算法分两阶段执行：

1. **体素化（Voxelization）**：将原始网格填充为空间体素格，分辨率通常设为64³至256³，对应的空间精度约为资产包围盒边长的0.4%至1.6%。
2. **等值面重建与简化**：对体素表面提取等值面（采用Marching Cubes算法，Lorensen & Cline, 1987），然后用Quadric Error Metrics（QEM）算法（Garland & Heckbert, 1997）将等值面简化至目标面数。

这种体素化重建方法有一个重要副作用：原始网格内部的隐藏几何体（如墙壁内侧的木构架、门框内的砖砌结构）会被自动剔除，代理网格天然是"实心（Solid）"的封闭体，避免了碰撞体的法线穿透（Normal Penetration）问题，也消除了Watertight检查报错的风险。

以下为在Unreal Engine 5中通过蓝图脚本批量生成HLOD代理网格的核心调用方式：

```cpp
// UE5 C++ — 触发HLOD Proxy Mesh重建
#include "HierarchicalLOD.h"

void UMyHLODTool::RebuildProxyMeshes(UWorld* World)
{
    FHierarchicalLODBuilder Builder(World);
    // 设置体素分辨率为128³，目标面数上限512
    Builder.VoxelSize = 128;
    Builder.ProxySettings.ScreenSize = 0.001f;   // 0.1% 屏幕覆盖率阈值
    Builder.ProxySettings.MergeDistance = 50.0f; // 单位: cm，合并间距
    Builder.Build();          // 执行体素化与QEM简化
    Builder.ForceBuildLODs(0); // 写入LOD0代理链
}
```

---

## 关键工作流程与工具参数

代理网格的实际制作存在手动与自动两条工作流，各有适用场景：

**手动工作流**适用于主视角可接触的高频资产（如主城建筑、玩家可进入的建筑外立面）。美术师在DCC工具（Maya/Blender）中依据原始资产的轮廓手工搭建低面数壳体，再导入引擎指定碰撞通道。手动代理的优势是可精确控制每个凸包的形状，避免自动化工具对门洞、楼梯等可行走区域的错误封堵。

**自动工作流**适用于远景填充资产（背景山脉、城市远景楼群）。Simplygon SDK提供的`ProxyLODPipeline`允许在命令行批量处理数百个资产，典型参数配置如下：

```json
{
  "ProxyLODSettings": {
    "ScreenSize": 0.001,
    "VoxelSize": 128,
    "HardEdgeAngle": 60,
    "MergeDistance": 50,
    "MaxTriangleCount": 256,
    "RecalculateNormals": true,
    "TransferNormals": false
  }
}
```

其中 `HardEdgeAngle` 设为60°可避免代理网格在棱角处产生过度光滑的球形误差，`MergeDistance` 设为50cm意味着间距小于50cm的相邻资产会被合并为单一代理，有效降低Draw Call数量。在《地平线：零之曙光》（Guerrilla Games, 2017）的技术分享中，其植被HLOD系统正是依赖类似的合并距离参数，将远景植被Draw Call从每帧12,000次压缩至400次以下。

---

## 实际应用

### 开放世界植被系统

在大型开放世界游戏中，单棵参考树木可能包含80,000个三角形（含叶片Billboard卡片）。其碰撞代理通常只用一个圆柱体（12面）表示树干，加上2至3个扁平圆柱体表示主要枝干分叉，总面数控制在**40面以内**。阴影代理则用一个由16面构成的椭球体近似整体树冠轮廓。当场景中同时存在50,000棵树时，将碰撞从原始网格切换至40面代理，物理模拟线程的CPU占用可从单帧8ms降至0.3ms以内。

### 城市建筑群的HLOD合批

在以城市为背景的游戏中（如《赛博朋克2077》，CD Projekt Red, 2020），摄像机500米以外的建筑群会被HLOD系统合并为一张包含16至32栋建筑的单一代理网格，每栋建筑的代理面数压缩至128至256三角形。这一区域的所有建筑共享一个Draw Call和一张2048×2048的合并贴图，相比逐栋渲染减少了约96%的Draw Call开销。合并后代理网格的总面数通常在2048至4096三角形之间，远低于该区域原始资产总面数（通常超过600万三角形）的0.1%。

### 实时阴影级联中的代理切换

在使用级联阴影贴图（Cascaded Shadow Maps，CSM）的管线中，阴影代理网格通常在第3至第4级联（距离摄像机50至200米区间）被激活。以分辨率为2048×2048的第4级联为例，其单像素覆盖约为20cm²，因此面数超过512的阴影代理在该距离下已无法提供比256面代理更好的阴影轮廓——多余的面数只是GPU光栅化开销，没有任何视觉回报。技术美术师在配置阴影代理时，必须以目标CSM分辨率和级联距离作为面数预算的上限参考。

---

## 常见误区

**误区一：代理网格等同于LOD最后一级。**  
实际上，LOD链（LOD0→LOD1→LOD2→LOD3）的切换由屏幕覆盖率驱动，所有级别均参与正常渲染的颜色通道。代理网格通常被挂载在独立的碰撞通道或阴影通道，不出现在主渲染颜色输出中，两者在引擎管线中是相互独立的资产槽。在UE5中，碰撞代理挂载于Static Mesh的`SimpleCollision`属性，与LOD系列的`LODData`数组完全分离。

**误区二：代理网格越简单越好。**  
当碰撞代理的近似误差超过玩家角色包围胶囊体半径（通常为34cm）时，角色会在视觉上"悬浮"于资产表面或错误地卡入几何体。因此碰撞代理的最大允许误差应小于34cm，这意味着对于细节尺度超过34cm的凹凸结构（如台阶、窗台），碰撞代理仍需保留相应的几何描述，而不能无限度简化。

**误区三：自动生成工具可完全替代手工代理。**  
自动体素化工具无法理解语义信息：一扇可开门的门洞在体素化后会被填实，导致玩家无法通过。凡是涉及可通行区域（门洞、拱桥、隧道入口）的碰撞代理，均需美术师手动干预或在自动化结果基础上进行拓扑修正，否则会产生"看得见入口却走不进去"的严重游戏性问题。

---

## 知识关联

代理网格与以下技术概念存在直接的上下游依赖关系：

- **网格简化（Mesh Simplification）**：QEM算法（Garland & Heckbert, 1997，《Surface Simplification Using Quadric Error Metrics》，SIGGRAPH 1997）是代理网格自动生成的数学基础。理解QEM的误差矩阵累积逻辑，有助于预判体素化代理在尖锐棱角处的退化行为。
- **HLOD（Hierarchical LOD）**：代理网格是HLOD系统的核心输出物。在UE5的World