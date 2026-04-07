---
id: "3da-org-hair-modeling"
concept: "毛发建模"
domain: "3d-art"
subdomain: "organic-modeling"
subdomain_name: "有机建模"
difficulty: 3
is_milestone: true
tags: ["技术"]

# Quality Metadata (Schema v2)
content_version: 6
quality_tier: "S"
quality_score: 95.9
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-07"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
  - type: "reference-book"
    citation: "Apodaca, A. A., & Gritz, L. (1999). Advanced RenderMan: Creating CGI for Motion Pictures. Morgan Kaufmann."
  - type: "reference-book"
    citation: "Weta Digital (2011). The Art of Visual Effects in The Lord of the Rings. Weta Workshop Publications."
  - type: "academic-paper"
    citation: "Marschner, S. R., Jensen, H. W., Cammarano, M., Worley, S., & Hanrahan, P. (2003). Light Scattering from Human Hair Fibers. ACM SIGGRAPH 2003 Papers, 780–791."
  - type: "reference-book"
    citation: "Cem Yuksel, Scott Schaefer, & John Keyser. (2009). Hair Meshes. ACM Transactions on Graphics (TOG), 28(5), Article 166."
  - type: "reference-book"
    citation: "Bertails, F., Audoly, B., Cani, M.-P., Querleux, B., Leroy, F., & Lévêque, J.-L. (2006). Super-helices for Predicting the Dynamics of Natural Hair. ACM SIGGRAPH 2006 Papers, 1180–1187."
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# 毛发建模

## 概述

毛发建模是在三维软件中通过曲线、多边形条带或专用Groom系统来构建角色毛发的技术流程。与布料或硬表面建模不同，毛发建模的核心挑战在于如何用有限的几何数据描述数量庞大的发丝，同时保证在渲染或实时引擎中的性能可控。不同于粒子毛发（直接由渲染器在曲线基础上生成管状体），毛发建模的结果是真实存在于场景中的几何体或可导出的Groom资产。

这一技术随电影工业发展而逐步成熟。2001年前后，Peter Jackson执导的《指环王：护戒使者》中，Weta Digital的技术团队率先使用手工绘制的多边形条带发片模拟角色毛发与皮毛，这一方法奠定了Card Hair在影视与游戏中长达十年的主流地位（Weta Digital, 2011）。2010年Autodesk随Maya 2011正式推出XGen插件，使曲线导向式毛发进入主流DCC工作流；同年，Side Effects Software在Houdini 11中大幅强化Grooming工具集，令程序化毛发梳理首次对中小型工作室开放。虚幻引擎5于2021年正式发布的Groom系统（基于Alembic .abc格式导入）则将高精度曲线毛发带入实时渲染领域，让游戏角色也能呈现接近影视的毛发品质。此外，Pixar于2012年在《勇敢传说》制作过程中内部研发了专用毛发流水线"Taz"，首次实现了角色头部10万根以上曲线发丝的全帧渲染，标志着影视级曲线毛发正式取代Card成为高端长片的标配技术。

毛发建模直接影响角色的气质与真实感——发际线疏密、发丝走向与头皮曲率的吻合程度，都能在渲染图中即刻暴露建模质量的高低。一位有经验的角色TD在审阅毛发资产时，通常首先检查三处细节：发际线边缘的曲线角度是否平行于头皮、刘海前端是否有碎发层拉开虚实对比、以及侧脸轮廓处的发丝是否有自然的半透光漏光感。这三项标准几乎囊括了Card工作流与曲线工作流在视觉质量上的全部核心要求，因此毛发建模是头部建模之后必须攻克的延伸技能。

---

## 核心原理

### 曲线导向毛发（Curve-based Hair）

曲线导向毛发以NURBS曲线或样条线（Spline）作为单根发丝的骨架，通过设置曲线上控制点的位置来定义发丝走向与弧度。在Maya XGen中，一根Guide Curve通常包含5～10个控制点；增殖（Density）参数决定在头皮UV上插值生成多少根渲染发丝，常见设置为每平方厘米50～300根。曲线本身在视口中显示为细线，不占用多边形面数，因此在造型阶段可以专注于发型轮廓的塑造，而不必担心几何体数量。

导出时，曲线通常被转为Alembic缓存（.abc）或USD格式，供渲染器（Arnold、Renderman、V-Ray）读取并生成渲染时管状体。管状体的厚度由`width`属性控制：根部一般设为0.06～0.1mm，梢部收细至0.02mm以下，以模拟自然锥形截面。正是这种锥形结构，使光线在发丝表面产生不对称的高光分布，从而呈现真实头发特有的"双高光"视觉效果——主高光（R分量）由角质层表面的镜面反射形成，副高光（TRT分量）由光线透过发丝内部髓质折射后再折射出表面形成，两者之间存在约2°～5°的偏移角（Marschner et al., 2003）。

**思考问题：** 如果一根长达30cm的直发导向曲线只设置2个控制点（起点和终点），会对发型造型产生什么限制？在什么场景下这样设置反而是合理的？对于需要表现卷发或波浪发型的角色，最少需要几个控制点才能避免曲线产生不自然的直线段折痕？

### 多边形条带发片（Polygon Card Hair）

多边形条带法将一撮发丝烘焙为一张贴图，贴在极薄的平面四边形（Card）上。每张Card通常只有2～6个四边形面，整体发型由数十到数百张Card拼叠而成。贴图包含三张关键通道：漫反射颜色图（记录发丝颜色变化）、Alpha透明图（裁切发丝轮廓）和法线图（模拟发丝光泽方向）。部分高精度工作流还会额外烘焙一张AO遮蔽图（Ambient Occlusion），专门描述发丝之间相互遮挡产生的暗部层次，使Card在强侧光下依然维持层次感而非平坦化。

Card法的核心建模步骤是：先在头部模型表面用Snap工具将Card吸附贴合头皮曲率，再通过顶点权重控制Card在骨骼动画中的飘动幅度。根部顶点权重设为1.0（完全跟随头骨），梢部逐渐降低至0.2～0.4以产生自然晃动。这种方法广泛用于游戏角色，单个角色头发通常控制在500～1500个Card面以内以保证实时帧率。Card贴图分辨率通常设置为512×512或1024×512，使用BC3（DXT5）格式压缩以保留Alpha通道精度，在移动端则进一步降为256×256的ETC2压缩格式以减少显存占用。

**例如**，《原神》中的人物角色发型普遍采用Card工作流：以大块底层Card定义发体体积，以细长Card刻画刘海飘散感，每根散发Card的宽度约为0.5～1.2mm，整套头发Card面数控制在800面以内，使角色在移动端设备上也能稳定维持30帧以上的渲染性能。据公开的技术分析，《原神》PC端角色头发贴图分辨率通常为1024×512，同时使用了自定义的各向异性高光着色器以在低面数Card上模拟发丝高光带的效果。

### Groom系统（程序化毛发梳理）

Groom是一种将曲线梳理流程和物理属性打包为单一资产的工作方式。在Houdini中，Groom工作流使用`guideprocess` SOP节点对导向曲线进行程序化卷曲（curl）、噪波（frizz）、成束（clump）操作，每种操作均有可量化参数：`clump_amount`控制成束紧密度（0～1），`frizz_frequency`控制乱发的空间频率（单位为每厘米的波数）。

虚幻引擎5的Groom资产在导入时需要绑定到Skeletal Mesh的头皮表面，并生成LOD链——通常Level 0保留100%曲线，Level 2降至20%用于中景，Level 4切换为低面数Card以保证性能。Groom系统还内置物理模拟参数，`stiffness`（刚度）和`damping`（阻尼）直接在资产中设定，无需额外物理骨骼链。在Houdini的Groom流程中，每个`guideprocess`节点可叠加多层效果，设计师通常按照"梳理方向→成束→卷曲→添加乱发"的固定顺序排列节点，以确保每一步的造型效果不被后续操作覆盖（Bertails et al., 2006）。

---

## 关键公式与物理模型

### 发丝弯曲刚度与长度的关系

毛发物理模拟中，单根发丝的弯曲刚度（bending stiffness）$k$ 与其自由端长度 $L$ 之间遵循欧拉-伯努利梁理论推导的关系：

$$k \propto \frac{EI}{L^3}$$

其中：
- $E$ 为发丝材料的杨氏模量（Young's modulus），人类头发约为 $3.6 \sim 4.5 \, \text{GPa}$
- $I$ 为截面二阶矩（second moment of area），对于圆形截面 $I = \frac{\pi r^4}{4}$，$r$ 为发丝半径（约 $35 \sim 50 \, \mu\text{m}$）
- $L$ 为发丝从根部到梢部的自由长度

这一公式揭示了一个在实际制作中极易被忽视的规律：**发丝弯曲刚度与长度的三次方成反比**。若将5cm短发的刚度参数 $k_{\text{short}}$ 直接应用于15cm长发，实际视觉上的长发将比短发僵硬约 $(15/5)^3 = 27$ 倍。因此，在Groom系统的`stiffness`滑块中，15cm长发所需的数值应约为相同视觉柔软度下5cm短发数值的 $1/27$。许多初学者在制作长发角色时发现头发"像铁棍一样不动"，根本原因正在于此——他们沿用了短发预设的刚度数值，而未根据发丝长度进行相应的三次方缩放。

### 发丝密度与UV面积的关系

在曲线导向工作流中，渲染发丝的实际生成根数 $N$ 由以下关系决定：

$$N = \rho \cdot A_{\text{UV}}$$

其中：
- $\rho$ 为设定的发丝密度（根/cm²），Maya XGen中通过`Density`属性设置
- $A_{\text{UV}}$ 为头皮UV展开后对应的实际表面积（单位cm²）

**例如**，若头顶UV展开面积为 $12 \, \text{cm}^2$，密度设置为 $150 \, \text{根/cm}^2$，则该区域渲染时将生成 $N = 150 \times 12 = 1800$ 根发丝。若UV展开时该区域被压缩为原始面积的60%（即 $7.2 \, \text{cm}^2$），则实际生成发丝降至1080根，产生肉眼可见的发量不足，这正是UV展开精度直接影响毛发质量的根本原因（Apodaca & Gritz, 1999）。基于此，专业的头部模型UV拆分规范通常要求头顶区域的UV拉伸率（stretch ratio）不超过1.15，即UV展开后的面积不能小于真实曲面面