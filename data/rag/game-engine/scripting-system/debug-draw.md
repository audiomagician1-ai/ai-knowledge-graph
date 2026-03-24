---
id: "debug-draw"
concept: "调试绘制"
domain: "game-engine"
subdomain: "scripting-system"
subdomain_name: "脚本系统"
difficulty: 2
is_milestone: false
tags: ["调试"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 41.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.444
last_scored: "2026-03-24"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 调试绘制

## 概述

调试绘制（Debug Draw）是游戏引擎脚本系统提供的一组运行时可视化工具，允许开发者在游戏运行过程中动态绘制线条、球体、盒体、文字等几何图元，这些图元仅在开发阶段可见，不会出现在最终发布版本中。调试绘制的输出直接渲染到屏幕上，叠加在游戏画面之上，无需创建任何游戏实体或材质资源。

调试绘制最早在早期3D游戏开发工具链中以简单的线框渲染形式出现，随着游戏引擎的成熟，Unreal Engine、Unity等主流引擎将其标准化为脚本API的固定组成部分。Unreal Engine 4中对应的函数前缀为`DrawDebug`（如`DrawDebugLine`、`DrawDebugSphere`），Unity中则通过`Debug.DrawLine`和`Gizmos.DrawWireSphere`等静态方法调用。

调试绘制对于脚本开发至关重要的原因在于：AI导航路径、碰撞检测范围、物理射线投射（Raycast）的命中点等逻辑数据在引擎默认视图中完全不可见，而调试绘制能够将这些抽象的数值数据转化为直观的几何形状，将一个坐标`(x, y, z)`变成屏幕上一个可见的红色球体，使程序员在数秒内定位到原本需要数小时才能发现的逻辑错误。

## 核心原理

### 绘制持续时间与帧生命周期

调试绘制的图元默认生命周期为**单帧（0秒）**，即每次调用后仅在当前帧显示一次，下一帧自动消失。若要持续显示，需传入`duration`（持续时间）参数，例如Unreal Engine中`DrawDebugSphere(World, Center, Radius, Segments, Color, false, 5.0f)`中第7个参数`5.0f`表示该球体持续显示5秒。在`Tick`函数（每帧执行一次）中调用绘制函数且`duration=0`，效果等同于每帧刷新，适合追踪移动中的对象位置。

### 常用图元类型及参数

不同图元对应不同的空间概念，各有专用参数：

- **线段（Line）**：需要起点`Start`和终点`End`两个三维坐标向量，常用于可视化射线投射的方向和距离。`DrawDebugLine(World, Start, End, FColor::Red, false, -1.f, 0, 2.f)`中最后一个参数`2.f`控制线条粗细（单位：像素）。
- **球体（Sphere）**：需要球心坐标和半径，还需要`Segments`参数控制球体的分段数，通常取12或16，分段数越高球体越平滑但绘制开销越大。
- **盒体（Box）**：通过中心点和`Extent`（半边长向量）定义，`Extent=(50,50,50)`表示一个边长为100单位的正方体。
- **文字（Text）**：在指定三维坐标处渲染字符串，Unreal中对应`DrawDebugString`，常用于在NPC头顶显示当前AI状态名称（如"Patrol"、"Chase"）。

### 颜色与深度测试

调试绘制通常可通过参数控制是否启用**深度测试**（Depth Test）。启用深度测试时，被场景几何体遮挡的调试图元不会显示；禁用深度测试（传入`bDepthIsForeground=true`或类似参数）时，调试图元始终绘制在所有物体之上，即使它们在墙壁后面也完全可见，常用于追踪穿越障碍物的AI路径点。颜色参数通常使用引擎内置的颜色常量，如`FColor::Green`（绿色，常表示正常状态）和`FColor::Red`（红色，常表示警告或命中状态）。

## 实际应用

**射线检测可视化**：在编写角色攻击判定脚本时，开发者对`LineTraceSingleByChannel`（Unreal的单射线检测函数）的起点和终点各绘制一个半径为5单位的绿色球体，并在两点之间绘制一条蓝色线段。若射线命中目标，则在命中坐标处额外绘制一个半径为10单位的红色球体并持续显示0.5秒，从而直观确认命中点是否符合预期。

**AI行为状态标注**：在行为树脚本的每个节点执行时，通过`DrawDebugString`在NPC头顶上方50单位处显示当前执行的行为节点名称，如"SearchForPlayer"或"ReturnToBase"，使测试人员无需打开控制台输出也能直接观察每个NPC的实时行为。

**碰撞体积验证**：当角色的碰撞胶囊体（Capsule）参数调整后，通过脚本在`BeginPlay`中调用`DrawDebugCapsule`，传入实际的碰撞半径（如`Radius=42`）和半高（如`HalfHeight=96`）并持续显示30秒，直观对比碰撞体积与角色模型之间是否存在穿模或间隙。

## 常见误区

**误区一：调试绘制函数在发布版本中会被自动剔除**
部分开发者误认为只要使用调试绘制就不影响性能，实际上在Unreal Engine中，`DrawDebug`系列函数在`Shipping`（发布）构建配置下会被宏`UE_BUILD_SHIPPING`自动编译剔除，但在`Development`和`Test`构建中均会执行实际的渲染开销。若在`Tick`函数中大量调用（如同时绘制数百个球体），即使在开发阶段也会产生可测量的帧率下降，建议通过自定义布尔变量或控制台变量（CVar）控制调试绘制的开关。

**误区二：调试文字坐标与屏幕坐标相同**
`DrawDebugString`的坐标参数是**世界空间三维坐标**，而非屏幕像素坐标。将一个对象在世界中的位置`(0, 0, 100)`直接传入即可让文字悬浮在该位置，引擎内部自动完成世界坐标到屏幕坐标的投影变换。若需要在屏幕固定位置显示文字，应改用UI系统（如Unreal的`HUD::DrawText`）而不是调试绘制。

**误区三：调试绘制可以替代正式的可视化系统**
调试绘制的渲染采用无光照的纯色线框，不支持透明度混合、阴影或自定义着色器。它只适用于开发阶段的诊断，若游戏玩法本身需要向玩家展示辅助线或范围指示器，必须使用正式的程序化网格体（Procedural Mesh）或粒子系统来实现，而不能直接将调试绘制代码保留在发布版本中。

## 知识关联

调试绘制建立在**脚本系统概述**中介绍的`Tick`函数和引擎API调用机制之上——理解每帧回调的执行时机是正确使用`duration=0`持续刷新模式的前提。调试绘制与**物理系统**的射线检测（Raycast/LineTrace）高度协同使用，几乎每一个射线检测脚本都会配套使用调试线段来可视化检测路径。此外，调试绘制的坐标体系与引擎的**坐标系与变换**概念直接相关，世界坐标、局部坐标的转换错误是导致调试球体出现在错误位置的最常见原因。掌握调试绘制后，开发者在编写任何涉及空间逻辑的脚本（导航、碰撞、感知系统）时都能以数倍的效率进行验证和迭代。
