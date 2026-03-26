---
id: "3da-bake-marmoset"
concept: "Marmoset烘焙"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 45.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.464
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-26
---


# Marmoset烘焙

## 概述

Marmoset烘焙是指使用Marmoset Toolbag软件中的Baker模块，将高模细节投射到低模上，生成法线贴图、AO贴图、曲率贴图等多种纹理通道的工作流程。Toolbag的核心优势在于其实时PBR预览功能——烘焙完成后，贴图结果可以立即应用到场景材质球上，无需切换到其他软件即可看到最终渲染效果。这一特性使美术师能在烘焙、调整、预览之间快速迭代，显著缩短了从高模到最终效果的验证时间。

Marmoset Toolbag的烘焙功能从3.0版本开始大幅加强，Toolbag 4版本引入了GPU加速烘焙，将原本需要数分钟的任务压缩到数秒内完成。相比Substance Painter内置烘焙或xNormal的纯命令行式操作，Toolbag Baker以独立模块形式集成在实时渲染环境中，用户可以在同一界面内完成模型导入、笼体调整、烘焙执行和效果预览全流程。

对于法线贴图烘焙质量要求较高的硬表面模型（如武器、机甲、道具），Marmoset烘焙因其精准的射线投射控制和即时可视化反馈，已成为游戏和影视行业美术团队的主流选择之一，尤其适合需要频繁对比多套烘焙参数的项目。

## 核心原理

### Baker模块与项目结构

打开Toolbag后，通过菜单`Baker > New Baker`创建烘焙项目，界面中会出现专用的Baker面板。Baker项目以`.tbscene`格式保存，内部维护一张**烘焙组（Bake Group）**列表，每个组对应一对高模与低模的映射关系。每个烘焙组中需要分别指定：

- **High（高模）**：包含细节雕刻或倒角的高面数网格
- **Low（低模）**：实际游戏使用的低面数网格，需已展开UV
- **Cage（笼体，可选）**：用于手动控制射线投射范围的偏移网格

这种分组结构允许一个场景内同时存在多个独立烘焙对，例如角色头部、躯干、手部各使用不同的烘焙组，互不干扰。

### 射线投射与笼体控制

Marmoset烘焙的投射原理是从低模表面法线方向发射射线，击中高模表面后采样颜色或法线信息。`Max Frontal Distance`和`Max Rear Distance`两个参数分别控制射线向外和向内的最大探测距离，单位为场景单位（通常是厘米）。

当模型局部结构复杂（如管线交叉、内嵌细节）导致投射错误时，可启用**Paint Skew**功能，用笔刷在低模表面手动绘制投射方向偏移，精度可达单个三角面级别。这一功能是Toolbag相较于xNormal的显著技术优势——xNormal只支持全局笼体偏移，而Toolbag支持局部手绘修正。

### 可烘焙贴图通道

Toolbag Baker支持在单次烘焙中同时输出以下通道：

| 通道 | 说明 |
|------|------|
| Normals（法线） | 切线空间或物体空间，16位精度可选 |
| Ambient Occlusion | 环境光遮蔽，可设置采样数（8到2048） |
| Curvature（曲率） | 凸起/凹陷信息，用于程序化纹理叠加 |
| Height（高度） | 相对高度差，范围映射至0-1 |
| Thickness | 次表面散射厚度图 |
| Vertex Color | 直接从高模顶点颜色采样 |

AO的采样数建议生产环境设为512或1024，预览时可降至64以加快速度。

### 实时预览与材质联动

Toolbag烘焙完成后，贴图可以直接拖入同场景的材质槽。法线贴图连接到`Surface > Normals`，AO连接到`Surface > Occlusion`，软件使用物理正确的GGX着色模型实时计算光照结果。这意味着美术师可以立即在Toolbag的Viewport中看到该法线贴图在实际PBR材质下的表现，而非在灰模预览下猜测最终效果。

## 实际应用

**硬表面武器烘焙**：以一把科幻步枪为例，工作流程如下：将高模（约200万面）和低模（约8000面）分别导出为单独OBJ文件，在Toolbag中新建Baker，将枪身、枪托、瞄准镜各建立独立烘焙组。调整每组的`Max Distance`参数至约0.3厘米，勾选`Ignore Backfaces`避免内部结构穿透。一次烘焙同时输出2048×2048的法线图和AO图，耗时约8秒（RTX 3080级显卡）。烘焙完成后立即在场景中新建材质球，赋予金属Roughness为0.4、Metalness为1.0，将法线和AO贴图接入，30秒内即可完成效果验证。

**角色头部烘焙**：有机体形状（如人脸）常出现鼻梁、耳廓等区域投射错误，此时使用Paint Skew功能，将鼻梁区域的射线方向手动偏移约15度，可消除典型的"阴影漏边"瑕疵，比重新建笼体节省约20分钟。

## 常见误区

**误区一：认为Toolbag烘焙只能处理法线贴图**。实际上如前述，Toolbag Baker支持十余个通道同步烘焙，尤其是曲率图（Curvature）在Toolbag中的算法与Substance Painter有所不同——Toolbag的曲率图中凸起区域默认为白色（值为1），凹陷区域为黑色（值为0），而某些工具的定义相反。将Toolbag曲率图导入其他软件使用时，需要在着色器中反转该通道。

**误区二：以为提高Max Distance就能解决所有投射错误**。盲目增大投射距离会导致射线穿透相邻几何体，产生"漏光"（bleed）瑕疵，在两块平行面板之间距离较小时尤为明显。正确做法是将Max Distance保持尽量小，用烘焙组分离或Paint Skew处理局部问题区域。

**误区三：认为Toolbag烘焙结果和Substance Painter烘焙结果完全一致**。两者在AO的衰减算法和法线切线计算上存在微小差异，尤其是UV接缝处的切线平滑处理方式不同。如果项目最终在Substance Painter中贴图绘制，建议在Toolbag完成精度验证后，用Substance Painter再执行一次同参数烘焙作为正式生产文件。

## 知识关联

Marmoset烘焙建立在**法线烘焙**的基础知识之上——理解切线空间法线贴图的RGB通道编码方式（X轴映射到R，Y轴映射到G，Z轴映射到B，静止法线对应颜色约为(128,128,255)的紫蓝色）是正确判断烘焙结果质量的前提。熟悉"高低模对齐"和"UV展开无重叠"等前置要求，才能有效使用Toolbag Baker的各项参数。

在Toolbag烘焙工作流中积累的笼体调整和多通道管理经验，可以直接迁移到Substance Painter烘焙、Arnold烘焙等其他工具的类似操作，因为射线投射的底层逻辑在各工具中是一致的。Toolbag由于其实时反馈特性，也常被用作检验其他工具烘焙结果的"验收环境"——将贴图导入Toolbag的PBR材质中预览，是许多工作室最终QA流程的标准步骤。