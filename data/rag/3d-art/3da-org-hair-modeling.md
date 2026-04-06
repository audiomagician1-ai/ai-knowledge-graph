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
content_version: 5
quality_tier: "A"
quality_score: 82.1
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-06"
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
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-06
---


# 毛发建模

## 概述

毛发建模是在三维软件中通过曲线、多边形条带或专用Groom系统来构建角色毛发的技术流程。与布料或硬表面建模不同，毛发建模的核心挑战在于如何用有限的几何数据描述数量庞大的发丝，同时保证在渲染或实时引擎中的性能可控。不同于粒子毛发（直接由渲染器在曲线基础上生成管状体），毛发建模的结果是真实存在于场景中的几何体或可导出的Groom资产。

这一技术随电影工业发展而逐步成熟。2001年前后，Peter Jackson执导的《指环王：护戒使者》中，Weta Digital的技术团队率先使用手工绘制的多边形条带发片模拟角色毛发与皮毛，这一方法奠定了Card Hair在影视与游戏中长达十年的主流地位（Weta Digital, 2011）。2010年Autodesk随Maya 2011正式推出XGen插件，使曲线导向式毛发进入主流DCC工作流；同年，Side Effects Software在Houdini 11中大幅强化Grooming工具集，令程序化毛发梳理首次对中小型工作室开放。虚幻引擎5于2021年正式发布的Groom系统（基于Alembic .abc格式导入）则将高精度曲线毛发带入实时渲染领域，让游戏角色也能呈现接近影视的毛发品质。

毛发建模直接影响角色的气质与真实感——发际线疏密、发丝走向与头皮曲率的吻合程度，都能在渲染图中即刻暴露建模质量的高低，因此它是头部建模之后必须攻克的延伸技能。

---

## 核心原理

### 曲线导向毛发（Curve-based Hair）

曲线导向毛发以NURBS曲线或样条线（Spline）作为单根发丝的骨架，通过设置曲线上控制点的位置来定义发丝走向与弧度。在Maya XGen中，一根Guide Curve通常包含5～10个控制点；增殖（Density）参数决定在头皮UV上插值生成多少根渲染发丝，常见设置为每平方厘米50～300根。曲线本身在视口中显示为细线，不占用多边形面数，因此在造型阶段可以专注于发型轮廓的塑造，而不必担心几何体数量。

导出时，曲线通常被转为Alembic缓存（.abc）或USD格式，供渲染器（Arnold、Renderman、V-Ray）读取并生成渲染时管状体。管状体的厚度由`width`属性控制：根部一般设为0.06～0.1mm，梢部收细至0.02mm以下，以模拟自然锥形截面。正是这种锥形结构，使光线在发丝表面产生不对称的高光分布，从而呈现真实头发特有的"双高光"视觉效果（Marschner et al., 2003）。

**思考问题：** 如果一根长达30cm的直发导向曲线只设置2个控制点（起点和终点），会对发型造型产生什么限制？在什么场景下这样设置反而是合理的？

### 多边形条带发片（Polygon Card Hair）

多边形条带法将一撮发丝烘焙为一张贴图，贴在极薄的平面四边形（Card）上。每张Card通常只有2～6个四边形面，整体发型由数十到数百张Card拼叠而成。贴图包含三张关键通道：漫反射颜色图（记录发丝颜色变化）、Alpha透明图（裁切发丝轮廓）和法线图（模拟发丝光泽方向）。

Card法的核心建模步骤是：先在头部模型表面用Snap工具将Card吸附贴合头皮曲率，再通过顶点权重控制Card在骨骼动画中的飘动幅度。根部顶点权重设为1.0（完全跟随头骨），梢部逐渐降低至0.2～0.4以产生自然晃动。这种方法广泛用于游戏角色，单个角色头发通常控制在500～1500个Card面以内以保证实时帧率。

**例如**，《原神》中的人物角色发型普遍采用Card工作流：以大块底层Card定义发体体积，以细长Card刻画刘海飘散感，每根散发Card的宽度约为0.5～1.2mm，整套头发Card面数控制在800面以内，使角色在移动端设备上也能稳定维持30帧以上的渲染性能。

### Groom系统（程序化毛发梳理）

Groom是一种将曲线梳理流程和物理属性打包为单一资产的工作方式。在Houdini中，Groom工作流使用`guideprocess` SOP节点对导向曲线进行程序化卷曲（curl）、噪波（frizz）、成束（clump）操作，每种操作均有可量化参数：`clump_amount`控制成束紧密度（0～1），`frizz_frequency`控制乱发的空间频率（单位为每厘米的波数）。

虚幻引擎5的Groom资产在导入时需要绑定到Skeletal Mesh的头皮表面，并生成LOD链——通常Level 0保留100%曲线，Level 2降至20%用于中景，Level 4切换为低面数Card以保证性能。Groom系统还内置物理模拟参数，`stiffness`（刚度）和`damping`（阻尼）直接在资产中设定，无需额外物理骨骼链。

---

## 关键公式与物理模型

### 发丝弯曲刚度与长度的关系

毛发物理模拟中，单根发丝的弯曲刚度（bending stiffness）$k$ 与其自由端长度 $L$ 之间遵循欧拉-伯努利梁理论推导的关系：

$$k \propto \frac{EI}{L^3}$$

其中：
- $E$ 为发丝材料的杨氏模量（Young's modulus），人类头发约为 $3.6 \sim 4.5 \, \text{GPa}$
- $I$ 为截面二阶矩（second moment of area），对于圆形截面 $I = \frac{\pi r^4}{4}$，$r$ 为发丝半径（约 $35 \sim 50 \, \mu\text{m}$）
- $L$ 为发丝从根部到梢部的自由长度

这一公式揭示了一个在实际制作中极易被忽视的规律：**发丝弯曲刚度与长度的三次方成反比**。若将5cm短发的刚度参数 $k_{\text{short}}$ 直接应用于15cm长发，实际视觉上的长发将比短发僵硬约 $(15/5)^3 = 27$ 倍。因此，在Groom系统的`stiffness`滑块中，15cm长发所需的数值应约为相同视觉柔软度下5cm短发数值的 $1/27$。

### 发丝密度与UV面积的关系

在曲线导向工作流中，渲染发丝的实际生成根数 $N$ 由以下关系决定：

$$N = \rho \cdot A_{\text{UV}}$$

其中：
- $\rho$ 为设定的发丝密度（根/cm²），Maya XGen中通过`Density`属性设置
- $A_{\text{UV}}$ 为头皮UV展开后对应的实际表面积（单位cm²）

**例如**，若头顶UV展开面积为 $12 \, \text{cm}^2$，密度设置为 $150 \, \text{根/cm}^2$，则该区域渲染时将生成 $N = 150 \times 12 = 1800$ 根发丝。若UV展开时该区域被压缩为原始面积的60%（即 $7.2 \, \text{cm}^2$），则实际生成发丝降至1080根，产生肉眼可见的发量不足，这正是UV展开精度直接影响毛发质量的根本原因（Apodaca & Gritz, 1999）。

---

## 实际应用

**游戏角色写实发型（Card工作流）**：制作时，先在ZBrush或Maya中雕刻出完整的实体头发外形作为参考，再在Maya中逐层放置Card——底层Card覆盖头皮，中层Card定义发体层次，顶层Card添加散发与碎发细节。每层Card的Alpha贴图从真实发丝扫描照片或Marmoset Toolbag的Hair Texture Generator中生成，以确保发丝间的自然间距。顶层散发Card的长宽比一般控制在8:1～15:1之间，过短则显得生硬，过长则在镜头旋转时容易穿插。

**影视虚拟角色写实长发（Groom工作流）**：在DCC软件中完成头皮UV展开后，以头皮多边形法线方向生长初始导向曲线，使用XGen或Houdini逐区域梳理：刘海区域曲线向前弯曲弧度约30°，后发区曲线沿颅骨弧度自然下垂，侧发区曲线向耳后集束。最终以`density=200`根/cm²的参数预览，导出Alembic时选择`curve_type: cubic`以保持弧度精度。在Arnold渲染器中，曲线的`min_pixel_width`参数建议设为0.25～0.5像素，以在消除发丝锯齿的同时控制渲染时间。

**睫毛与眉毛建模**：睫毛通常用12～24张细长Card排布，每张Card宽约0.8mm，向眼眶外侧弯曲10°～20°；眉毛多用50～80根短曲线直接梳理，单根长度约8mm，走向从眉头沿弧线向眉梢倾斜约15°。在Groom资产中，睫毛与眉毛须单独分组，并分配独立的着色器，以便后续在不影响头发整体材质的前提下单独调整黑色素浓度（`melanin`）和粗糙度（`roughness`）参数。

**动物毛皮（Fur）建模**：Fur与Hair在工作流上共用同一套曲线系统，但参数差异显著。猫科动物体毛的导向曲线长度通常为2～4cm，密度高达500～800根/cm²，且`clump_amount`设为0.7以上以模拟毛丛结构；而人类头发的`clump_amount`通常低于0.4，以保持发丝的蓬松感。此外，动物毛皮需要额外设置底绒层（underfur）和针毛层（guard hair）两套独立Groom，分别控制体积感与表面光泽。

---

## 常见误区

**误区一：发际线处的曲线密度与头顶相同**
发际线的发丝自然稀疏，若使用与头顶相同的导向曲线密度，渲染结果会出现发际线处发量过厚、边缘生硬的问题。正确做法是在发际线区域手动将导向曲线间距扩大至头顶间距的2～3倍，并让发际线处的曲线根部方向几乎平行于头皮（角度<15°），模