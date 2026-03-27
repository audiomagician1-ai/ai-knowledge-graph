---
id: "3da-bake-thickness"
concept: "厚度烘焙"
domain: "3d-art"
subdomain: "baking"
subdomain_name: "烘焙"
difficulty: 2
is_milestone: false
tags: ["技巧"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 44.2
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.464
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---


# 厚度烘焙

## 概述

厚度烘焙（Thickness Baking）是一种将三维网格体积信息压缩为二维灰度贴图的烘焙技术，其输出的 Thickness Map（厚度贴图）记录了模型表面某点沿法线方向向内穿透到对面表面之间的距离。贴图中白色像素代表该区域物体较薄（内外表面距离短），黑色像素代表该区域物体较厚（内外表面距离长），或者部分软件约定恰好相反——因此在导入引擎前需确认软件的编码方向。

厚度烘焙技术最早随着次表面散射（Subsurface Scattering，SSS）材质在实时渲染管线中的普及而被广泛采用。2012年前后，随着 PBR 工作流的兴起，Marmoset Toolbag 和 Substance Painter 等工具将厚度烘焙列为标准烘焙通道之一，使它从离线渲染领域进入游戏美术的日常生产流程。

厚度贴图之所以重要，是因为实时渲染无法逐帧追踪光线在半透明介质（如人体皮肤、蜡烛、树叶、耳廓）内部的真实散射路径，必须用预计算的厚度数据来近似模拟光线穿透衰减量。没有厚度贴图时，皮肤材质的耳朵或手指在强背光下看起来和不透明岩石完全相同，缺乏透光质感。

---

## 核心原理

### 射线投射计算逻辑

烘焙软件在生成厚度贴图时，会从高模（或低模）每个表面像素点沿**反法线方向**（即朝向网格内部）发射射线，检测该射线第一次击中对面内壁的距离 *d*。这个距离随后被归一化到 0–1 的灰度范围并写入贴图。计算公式可以简写为：

> **T = 1 − clamp(d / MaxDistance, 0, 1)**

其中 *d* 为实测穿透距离，*MaxDistance* 为用户设定的最大采样深度（Marmoset 中默认为模型包围盒对角线长度的 10%）。缩小 MaxDistance 会使薄壁区域的灰度差异更明显；设置过大则薄厚区域的对比度降低。

### 与 AO 贴图的本质区别

环境光遮蔽（AO）烘焙时射线朝**外部半球**发射，统计外部空间被遮挡的比例；厚度烘焙时射线朝**内部**发射，统计体积厚薄。二者在贴图观感上容易混淆，但物理含义完全相反——AO 描述外部空间的遮挡，Thickness 描述内部介质的体积密度。在 Substance Painter 中两者位于不同的烘焙通道，不可互相替代使用。

### 在次表面散射材质中的驱动方式

在 Unreal Engine 5 的 Subsurface Profile 材质中，Thickness 贴图通常接入 **Opacity** 输入插槽，引擎用该值来缩放 SSS 剖面的透光量：Opacity 值越高（越薄），背光穿透颜色越饱和；Opacity 值越低（越厚），光线几乎无法穿透。Unity HDRP 的 Subsurface Scattering 材质则将厚度贴图接入 **Thickness Map** 专用插槽，并配合 Diffusion Profile 中设定的平均自由程（Mean Free Path，单位毫米）共同决定散射距离。人体皮肤的平均自由程在红色通道约为 3.67mm，绿色通道约为 1.37mm，蓝色通道约为 0.68mm，这些数值直接决定厚度贴图对最终颜色的影响幅度。

---

## 实际应用

**角色皮肤耳廓透光效果**：制作写实人体角色时，耳廓部位的网格极薄（通常 2–4 毫米），烘焙后该区域 Thickness Map 呈现接近白色的高值。当主光源从角色脑后照射时，引擎读取该高值，将 SSS 剖面的红橙色散射光叠加到耳廓正面，产生真实的皮下透光效果。

**蜡烛与蜡质道具**：游戏中的蜡烛模型通常为厚度不均的圆柱体，烘焙后烛体上部（因融化磨损较薄）的 Thickness 值高于底部。将贴图接入 UE5 的 Opacity 后，点燃状态下薄壁区域呈现温暖的透光橙黄色，而底部厚壁区域颜色较深，物理感强烈。

**植被叶片半透明**：树叶通常使用单面面片建模，"厚度"约等于零，因此叶片的 Thickness Map 全图接近纯白。但若制作厚质肉感叶片（如多肉植物），叶脉处网格较薄、叶肉中央较厚，此时烘焙得到的灰度渐变能驱动叶脉处更强的透光效果，与现实中逆光观察植物叶片时叶脉明显的现象一致。

**Marmoset Toolbag 4 操作步骤**：在 Bake Project 面板中勾选 Thickness，将 Max Distance 设置为模型最大厚度的 1.2 倍，Ray Count 建议设为 128 以上以减少噪点，烘焙完成后导出 16-bit PNG 可保留更多灰度精度。

---

## 常见误区

**误区一：Thickness Map 与 Translucency Map 是同一张贴图**
部分美术会将二者混用，实际上 Translucency Map 通常是美术手绘或从颜色信息中提取的透明度遮罩，代表材质的透射率分布；Thickness Map 是由几何体积计算得到的物理厚度数据。将手绘 Translucency 直接替代 Thickness 接入 SSS Opacity 插槽，会导致厚实区域也出现不合理的透光，因为手绘值未反映真实几何厚度。

**误区二：厚度越大，贴图越亮**
这取决于具体软件的编码约定。Marmoset Toolbag 默认**白色=薄，黑色=厚**（即 T = 1 − 归一化距离），而部分自定义着色器或手动烘焙脚本可能使用**白色=厚，黑色=薄**的相反约定。若约定混淆，接入 SSS 材质后效果完全颠倒——原本薄透的耳朵变得不透光，厚实的躯干反而发光。解决方法是在材质节点中添加一个 One Minus（1−x）反转节点进行纠正，或在导出前在 Photoshop 中执行 Ctrl+I 反相。

**误区三：厚度烘焙必须使用高模烘到低模**
对于厚度烘焙，高低模的差异影响远小于普通法线烘焙。因为厚度贴图捕捉的是体积穿透深度，而非表面微细节，即使直接对低模自身烘焙（Self-Bake），只要网格整体体积比例正确，得到的厚度分布仍然有效。大多数角色制作流程中，Thickness Map 直接从低模烘焙，无需高模参与。

---

## 知识关联

厚度烘焙以**烘焙概述**中介绍的射线投射基本流程为基础，但投射方向从向外翻转为向内，是射线方向参数的一种特化应用。学习厚度烘焙后，有助于更直观地理解 AO 烘焙为何专注于外部半球、曲率烘焙为何只关注表面曲率——三种烘焙通道的射线方向各不相同，对应不同的物理量。厚度贴图在实际项目中几乎专为 SSS 材质服务，因此它与次表面散射着色模型的参数调节密切绑定；若后续深入学习 Subsurface Profile 或 Diffusion Profile 的参数配置，会频繁回到厚度贴图的灰度分布来诊断和修正材质效果。