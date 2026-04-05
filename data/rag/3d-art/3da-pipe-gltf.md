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
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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

glTF（GL Transmission Format）是由Khronos Group于2015年首次发布、2017年正式推出2.0版本的开放标准3D文件格式，专为实时渲染和网络传输场景设计。与FBX不同，glTF并非由某一家商业公司主导，而是一个完全开放的行业规范，源码和规范文档均可在GitHub上免费获取。其设计目标可以用Khronos官方给出的定位来概括——glTF是"3D资产的JPEG格式"，意即像JPEG图片一样轻量、通用、易于传输。

glTF 2.0相较于1.0版本最重要的改变是引入了PBR（基于物理的渲染）材质模型作为核心规范，并将着色器硬编码从格式中移除，使其不再依赖GLSL代码的直接嵌入。这一设计让glTF天然兼容WebGL、Metal、Vulkan等多种图形API，而无需修改内容本身。在Web和移动端3D内容快速增长的背景下，glTF已成为Three.js、Babylon.js、模型查看器（`<model-viewer>`）等主流Web 3D框架的首选导入格式。

## 核心原理

### 文件结构：glTF与GLB的区别

glTF格式有两种存储形式。`.gltf`文件是纯文本的JSON描述文件，记录场景层级、网格数据索引、材质参数等结构信息；与之配套的是`.bin`二进制缓冲文件（存储顶点坐标、法线、UV等几何数据）以及独立的纹理图片文件（通常为PNG或JPEG）。这种分离结构便于按需异步加载各部分资源。

`.glb`（GL Binary）是glTF的单文件打包形式，将JSON、二进制缓冲和纹理全部合并进一个二进制容器文件。GLB文件以12字节的文件头（magic number为`0x46546C67`，即ASCII的"glTF"）开头，随后是版本号和总文件长度，之后是若干Chunk块交替排列JSON内容和二进制数据。在实际项目部署中，GLB因为只需一次HTTP请求即可加载完整资产，更适合移动端和Web场景。

### glTF的JSON节点结构

glTF的JSON层级由以下几类核心对象组成：`scenes`定义顶层场景入口，`nodes`构成场景树（每个node包含平移/旋转/缩放或4×4矩阵），`meshes`与`accessors`共同描述几何体数据，`materials`存储PBR参数，`animations`保存关键帧动画数据，`skins`记录蒙皮骨骼权重。所有几何数据通过`bufferViews`和`accessors`间接引用`.bin`文件中的字节偏移量，这种设计允许GPU直接映射内存而无需额外解析。

### PBR材质模型

glTF 2.0的核心材质模型为**metallic-roughness工作流**，材质参数包括：
- `baseColorFactor`：基础颜色（RGBA）
- `metallicFactor`：金属度，0.0~1.0
- `roughnessFactor`：粗糙度，0.0~1.0
- `emissiveFactor`：自发光颜色
- `normalTexture`：法线贴图
- `occlusionTexture`：环境遮蔽贴图

金属度与粗糙度被合并存储在同一张贴图的不同通道中（B通道=金属度，G通道=粗糙度），这一设计将纹理采样次数减少了一次，对移动端GPU性能有直接意义。glTF规范还定义了若干官方扩展（Extensions），例如`KHR_materials_unlit`用于不计算光照的卡通风格材质，`KHR_draco_mesh_compression`用于网格压缩，`KHR_texture_basisu`支持KTX2/Basis Universal纹理格式。

## 实际应用

**Web 3D展示**：电商平台产品3D预览（如Shopify的AR Quick Look功能）普遍采用GLB格式，配合`<model-viewer>`组件实现浏览器内的PBR实时渲染，单个产品GLB文件通常控制在2MB以内以确保移动网络加载速度。

**游戏引擎导入**：Godot 4原生支持glTF 2.0作为首选3D场景导入格式；Unity通过官方UnityGLTF插件或第三方GLTFast插件支持GLB运行时加载；Unreal Engine 5.0起内置了glTF导入器，支持将glTF资产直接转换为UAsset。

**XR与移动端AR**：Apple的Reality Composer和Android的Scene Viewer均支持GLB格式作为AR内容来源。苹果在iOS 12后通过Safari原生支持USDZ，但Android生态几乎统一采用GLB，这使得GLB成为跨平台AR内容分发最实际的选择。

**从Blender导出GLB**：在Blender 2.83及更高版本中，File > Export > glTF 2.0菜单下可选择导出为`.glb`或`.gltf + .bin`形式，导出选项中需注意勾选"Apply Modifiers"和"Export Deformation Bones Only"以精简骨骼数量。

## 常见误区

**误区一：认为glTF等同于FBX的替代品，可以完全覆盖所有3D管线需求。**  
glTF设计目标是"传输与显示"而非"创作与编辑"，它不存储编辑历史、修改器堆栈、非破坏性节点网络等DCC软件特有的创作数据。FBX在影视动画制作管线（如Maya到Unreal的动画传递）中仍是主流，glTF的优势集中在最终交付阶段的轻量化传输，而不是替代FBX作为中间交换格式参与完整制作流程。

**误区二：以为GLB文件天然就很小，不需要额外压缩处理。**  
未经压缩的GLB文件中的几何体数据量与FBX相当，网格本身并不会自动压缩。要获得真正的体积优化，必须在导出时启用`KHR_draco_mesh_compression`扩展（通常可将几何数据体积压缩60%~80%），并对纹理应用Basis Universal（KTX2）格式转换。两种优化都需要接收端（浏览器/引擎）具备对应解码器支持。

**误区三：混淆glTF的"扩展（Extensions）"等级，导致兼容性问题。**  
glTF扩展分为"必需（required）"和"可用（used）"两类。若将某扩展标记为`extensionsRequired`，则不支持该扩展的渲染器必须拒绝加载整个文件；若标记为`extensionsUsed`则可降级忽略。在面向广泛平台部署时，错误地将`KHR_draco_mesh_compression`设为Required会导致部分旧版浏览器完全无法显示模型。

## 知识关联

学习glTF格式需要具备FBX导出的操作经验，因为实际工作流中往往需要比较两种格式在骨骼动画、材质通道和文件大小方面的具体差异，判断在哪个阶段切换格式最合适。理解glTF的PBR metallic-roughness参数与Substance Painter等贴图软件的输出预设直接对应，是正确配置贴图通道的前提——Substance Painter内置的"glTF PBR Metal Roughness"导出预设会自动将金属度和粗糙度打包进同一张贴图的正确通道。掌握glTF格式后，进一步学习KTX2纹理压缩格式和Draco几何压缩工具链，可以将Web端3D资产的传输体积优化至生产级标准。