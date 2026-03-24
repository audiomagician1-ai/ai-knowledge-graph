---
id: "cg-udim"
concept: "UDIM"
domain: "computer-graphics"
subdomain: "texture-techniques"
subdomain_name: "纹理技术"
difficulty: 3
is_milestone: false
tags: ["流程"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 43.4
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.448
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# UDIM

## 概述

UDIM（U-Dimension）是一种用于影视级别CG资产制作的多Tile UV布局规范，由Foundry公司在其三维雕刻软件Mari中首创并推广。与传统UV映射将所有UV坐标压缩在0到1的单一空间内不同，UDIM将整个UV坐标系拓展为由多个相邻方格（Tile）构成的网格，每个Tile对应一张独立的纹理贴图，从而允许一个模型使用数十甚至上百张高分辨率纹理。

UDIM命名规则来源于Mari的内部编号系统：第一个Tile编号为1001，其水平方向（U轴）每向右移动一格，编号加1，最多排列10列（即1001至1010）；垂直方向（V轴）每向上移动一行，编号加100（即1011至1020为第二行，1021至1030为第三行，以此类推）。这套编号体系使纹理文件的组织和程序化读取变得极为清晰，文件名通常以`basecolor.1001.exr`、`basecolor.1002.exr`这样的格式存在。

UDIM之所以在影视和高端游戏制作中被广泛采用，根本原因在于它突破了单张纹理分辨率的上限。一个用于电影特效的人体角色，其皮肤细节往往需要4K甚至8K级别的精度，而头部、躯干、四肢各需要独立控制纹理密度。通过UDIM，艺术家可以给头部分配4个Tile（共8K等效精度），给手部这种高度可见区域分配更多Tile，而给不可见区域分配较少Tile，实现纹理资源的精细化分配。

## 核心原理

### UV Tile坐标规则

在UDIM坐标系中，第N个Tile的UV范围可由编号推算。对于编号为`UDIM_ID`的Tile，其水平起始位置 `U_start = (UDIM_ID - 1001) % 10`，垂直起始位置 `V_start = floor((UDIM_ID - 1001) / 10)`，该Tile覆盖的UV区间为 `[U_start, U_start+1] × [V_start, V_start+1]`。以编号1023为例：`(1023-1001)=22`，U偏移为`22%10=2`，V偏移为`floor(22/10)=2`，因此该Tile位于UV坐标`[2,3]×[2,3]`区间内。这一规则完全决定了纹理采样时引擎或渲染器如何查找对应贴图文件。

### 纹理采样机制

渲染器在处理UDIM纹理时，根据片段的UV坐标值动态决定采样哪张贴图。对于UV坐标`(u, v)`，渲染器计算`UDIM_ID = 1001 + floor(u) + floor(v) * 10`，然后加载对应编号的纹理文件进行采样，实际采样坐标为`(frac(u), frac(v))`（即取小数部分）。Arnold、RenderMan、V-Ray等主流渲染器均原生支持此机制，通常通过在文件路径中插入`<udim>`或`<UDIM>`占位符来自动匹配文件。例如路径`/textures/char_basecolor.<udim>.exr`会在渲染时被替换为`char_basecolor.1001.exr`等具体文件名。

### 与纹理图集的根本差异

纹理图集（Texture Atlas）将多个物体的UV硬性打包进同一张纹理的0-1空间，不同对象共用一张图像的不同区域，分辨率必须提前固定分配，修改某个对象的纹理区域会影响整体图集布局。UDIM则为每个Tile维护一张独立纹理文件，各Tile的分辨率可以完全不同——例如1001号Tile可以是8192×8192，而1005号Tile可以是1024×1024，各Tile修改互不干扰。这种独立性使UDIM特别适合多人协同的大型制作流程，不同部门可以同时修改同一角色的不同Tile而不产生文件冲突。

### UDIM在DCC软件中的工作流

Substance Painter、Mari、ZBrush、Mudbox等主流DCC软件均支持UDIM工作流。在Blender 2.82版本之后，UDIM支持被正式引入，用户可在UV编辑器中激活"UDIM Tiles"模式，直接在多个Tile上展开UV并分别绘制纹理。Maya的Arnold材质节点通过在`Image Name`字段填入`<udim>`标记即可自动加载所有Tile，无需手动为每个Tile建立独立纹理节点。

## 实际应用

在影视级角色制作中，一个写实人体角色通常会使用12至20个UDIM Tile。头部和手部因正面镜头出现频繁，往往各占2至4个Tile；躯干和腿部出镜较少则各占1至2个Tile，每个Tile使用4K或8K分辨率的EXR格式文件存储BaseColor、Roughness、Normal等通道。《权力的游戏》中龙的皮肤纹理据Pixomondo的技术文章记载使用了超过40个UDIM Tile，总纹理面积等效于40张8K贴图。

在游戏引擎领域，Unreal Engine 4.23版本起正式支持UDIM，但考虑到实时渲染的显存限制，工业实践中通常将UDIM Tile数量控制在4至9个，并在构建时自动将多Tile纹理合并为单张虚拟纹理（Virtual Texture）或合并图集，以平衡制作精度与运行时性能。

## 常见误区

**误区一：UDIM编号可以任意跳过** 实际上，虽然UDIM规范技术上允许不连续编号（如只有1001和1005而跳过中间编号），但许多渲染器和DCC软件在处理非连续Tile时会报错或需要额外配置。Mari中若某编号的Tile不存在，采样落在该区域的UV会返回黑色，而不是报错，这一行为常导致渲染结果出现肉眼难以察觉的黑色区域而被误认为光照问题。

**误区二：每个UDIM Tile内部的UV必须填满整个Tile空间** 这是错误的。Tile内部的UV岛（UV Island）只需落在该Tile的0-1本地空间范围之内，面积比例完全根据模型需要决定。艺术家可以在1001号Tile中只使用约30%的面积来存放某个配件的UV，剩余空间留空，这不会引发任何技术问题，只是浪费了该Tile对应纹理的部分存储空间。

**误区三：UDIM与UV贴图方向的行列顺序理解混乱** 初学者常将U轴（水平）与V轴（垂直）方向对应编号规则记反。UDIM编号增加方向：同一行内从左到右（U增大）编号+1，从下一行开始（V增大）编号+10。因此1011并不是1001右边的格子，而是1001正上方的格子，这与从左往右阅读的直觉相反，需要特别注意。

## 知识关联

**前置概念——纹理图集：** 学习UDIM之前需要掌握纹理图集（Texture Atlas）的UV打包原理，因为两者都解决了"单个模型需要超过单张纹理所能提供的信息量"的问题，而UDIM是对图集方案在独立性和可扩展性上的演进替代。理解图集中UV岛的布局逻辑，有助于更快掌握如何将UV岛分散到不同UDIM Tile的决策思路。

**衍生应用——虚拟纹理（Virtual Texturing）：** UDIM与虚拟纹理技术存在密切的工作流联系。在游戏引擎中，Unreal Engine的RVTM（Runtime Virtual Texture Mapping）可以将UDIM多Tile资产在导入时自动转换为虚拟纹理页面，使影视级别的UDIM资产能够在实时渲染环境中高效运行，这是当前影游同步制作（In-Camera VFX）工作流的关键技术衔接点。
