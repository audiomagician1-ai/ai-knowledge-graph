---
id: "3da-pipe-gltf"
concept: "glTF格式"
domain: "3d-art"
subdomain: "asset-pipeline"
subdomain_name: "资产管线"
difficulty: 2
is_milestone: false
tags: ["格式"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 50.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.467
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# glTF格式

## 概述

glTF（GL Transmission Format）是由Khronos Group于2015年发布、2017年正式推出2.0版本的三维资产传输格式，被誉为"3D界的JPEG"。与FBX或OBJ等传统格式不同，glTF专门针对实时渲染场景设计，其核心目标是最小化运行时的解析与处理开销，使浏览器或移动端应用能以接近零的转换代价直接加载并渲染模型。

glTF 2.0规范将资产数据分为JSON描述文件（`.gltf`）与二进制数据块（`.bin`）两部分，纹理则以独立图像文件存储。GLB是其单文件变体，将JSON、二进制几何数据和纹理打包进一个`.glb`文件，文件头以魔数`0x46546C67`开头，便于网络传输与移动端分发。glTF支持WebGL、Vulkan、Metal等多种图形API的直接映射，这使得它成为Web 3D（three.js、Babylon.js）和AR/VR应用（ARCore、ARKit、WebXR）的首选格式。

## 核心原理

### JSON场景描述与二进制缓冲区分离

glTF使用JSON文件描述场景图（Scene Graph），包含节点层级、网格引用、材质参数、动画通道和相机定义。几何数据（顶点坐标、法线、UV、蒙皮权重）存储在`.bin`二进制缓冲区中，通过`bufferView`和`accessor`对象进行索引访问。`accessor`精确定义了数据类型（如`FLOAT`、`UNSIGNED_SHORT`）、分量数量（`VEC3`、`MAT4`）和偏移量，GPU可以直接读取这些数据而无需格式转换，这是glTF实现高效加载的根本机制。

### PBR材质模型内置支持

glTF 2.0原生支持基于物理渲染（PBR）的金属粗糙度工作流（Metallic-Roughness Workflow）。材质参数直接存储为`pbrMetallicRoughness`对象，包含`baseColorFactor`（基础色，RGBA四分量）、`metallicFactor`（金属度，0.0–1.0）和`roughnessFactor`（粗糙度，0.0–1.0）。法线贴图、遮蔽贴图（Occlusion Map）和自发光贴图也有标准化字段，不像FBX需要依赖DCC软件的私有材质扩展，接收端程序能以一致方式解读材质而无需猜测着色器逻辑。

### 扩展机制（Extensions）

glTF通过官方扩展（Official Extensions）和厂商扩展（Vendor Extensions）满足超出核心规范的需求。例如`KHR_draco_mesh_compression`启用Draco几何压缩，可将网格文件体积缩小高达90%；`KHR_texture_basisu`支持Basis Universal超级压缩纹理，使纹理在GPU上以压缩态（ETC1S或UASTC）直接采样，不占用大量显存；`EXT_mesh_gpu_instancing`支持GPU实例化绘制，适合植被或建筑重复资产。使用扩展时需在JSON的`extensionsRequired`字段声明，加载器若不支持则明确报错而非静默错误。

### 动画数据结构

glTF动画由`animation`对象管理，内含多个`channel`（通道）和`sampler`（采样器）。每个channel指定动画目标节点和属性路径（`translation`、`rotation`、`scale`或`weights`），sampler则引用时间轴关键帧的输入accessor与变换数据的输出accessor，并支持`LINEAR`、`STEP`、`CUBICSPLINE`三种插值方式。这种结构与WebGL的渲染循环高度契合，JavaScript引擎无需额外转换即可直接驱动骨骼动画或形变目标（Morph Target）。

## 实际应用

**Web端产品展示**：电商平台（如Shopify、IKEA官网）使用GLB格式展示家具或消费品3D模型。设计师在Blender中完成建模与PBR材质制作后，通过"File > Export > glTF 2.0"导出，勾选"Apply Modifiers"与"Include > Selected Objects"，最终上传GLB至CDN，用户浏览器通过`<model-viewer>`标签即可渲染，无需插件。

**AR应用资产分发**：苹果的Reality Composer和谷歌的Scene Viewer均支持GLB格式。Android设备通过Chrome浏览器的`intent://`链接唤起Scene Viewer加载GLB，整个流程无需安装App。为控制移动端加载时间，行业实践建议单个GLB文件不超过15MB，纹理分辨率不超过2048×2048。

**游戏引擎导入**：Godot 4原生支持glTF 2.0导入；Unity和Unreal通过插件（UnityGLTF、glTF-UE4）导入，但需注意glTF的Y轴向上坐标系与Unity（Y轴向上）兼容，与Unreal（Z轴向上）需在导入时执行轴转换。

## 常见误区

**误区一：GLB等于压缩格式**。GLB只是将glTF的多个文件合并为单一二进制文件，本身并不压缩几何或纹理数据。若不启用`KHR_draco_mesh_compression`扩展，GLB内的网格数据以原始浮点数存储，文件体积不会比分离式`.gltf+.bin`更小。

**误区二：glTF可以替代FBX用于DCC软件间交换**。glTF的设计目标是"运行时传输"而非"创作数据交换"。它不保存编辑历史、细分曲面控制笼（Subdivision Control Cage）、NURBS曲线或非烘焙修改器，这些信息在导出时已被烘焙丢弃。DCC软件之间的资产交换仍应首选FBX或USD格式，glTF适合作为最终交付格式。

**误区三：glTF支持所有PBR工作流**。glTF 2.0核心规范仅支持金属粗糙度（Metallic-Roughness）工作流，Substance Painter的高光光泽度（Specular-Glossiness）工作流需通过`KHR_materials_specular`等扩展实现，且并非所有加载器都支持这些扩展。

## 知识关联

学习glTF格式前应先掌握FBX导出流程，因为实际资产管线中通常先在DCC软件（Maya、3ds Max、Blender）内以FBX格式制作和验证资产，确认骨骼、蒙皮和动画正确后，再转换或直接导出为glTF交付使用。理解FBX的节点层级概念有助于映射到glTF的`node`树结构，而FBX材质烘焙经验也直接适用于glTF导出前的PBR纹理准备工作。glTF格式的理解为后续学习WebXR资产优化、Draco压缩工作流以及实时渲染管线集成提供了直接的格式规范基础。