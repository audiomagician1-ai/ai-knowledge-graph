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
quality_tier: "A"
quality_score: 79.6
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---



# 厚度烘焙

## 概述

厚度烘焙（Thickness Baking）是一种将三维网格的体积信息压缩为二维灰度贴图的烘焙技术。其输出的 Thickness Map（厚度贴图）记录了模型表面某一点沿**反法线方向**向内穿透，直至击中对面内壁之间的距离值。贴图中白色像素代表该区域网格较薄（内外表面距离短），黑色像素代表该区域网格较厚（内外表面距离长）——但部分软件约定恰好相反，因此在将贴图导入引擎前，必须确认烘焙工具的灰度编码方向，避免厚薄关系颠倒。

厚度烘焙技术最早随次表面散射（Subsurface Scattering，SSS）材质在实时渲染管线中的普及而被广泛采用。2012 年前后，随着基于物理的渲染（PBR）工作流的兴起，Marmoset Toolbag 2 和 Substance Painter 首个正式版本将厚度烘焙列为标准烘焙通道之一，使其从离线渲染领域正式进入游戏美术的日常生产流程。实时渲染无法逐帧追踪光线在半透明介质（如皮肤、蜡烛、树叶、耳廓）内部的真实散射路径，必须依赖预计算的厚度数据来近似模拟光线穿透衰减量。若缺少厚度贴图，皮肤材质在强背光下与不透明岩石几乎无法区分，完全丧失透光质感。

参考资料：Akenine-Möller 等人《Real-Time Rendering》第四版（CRC Press, 2018）第14章对次表面散射的实时近似方法有详细论述，厚度贴图方案即属于其中的"预积分 SSS"思路的延伸实现。

---

## 核心原理

### 射线投射计算逻辑

烘焙软件生成厚度贴图时，从每个表面像素点沿**反法线方向**（朝向网格内部）发射射线，检测该射线第一次击中对面内壁的距离 $d$，再将其归一化到 0–1 的灰度范围写入贴图。完整计算公式为：

$$
T = 1 - \text{clamp}\!\left(\frac{d}{D_{\max}},\ 0,\ 1\right)
$$

其中 $d$ 为实测穿透距离（单位与模型世界单位一致），$D_{\max}$ 为用户设定的最大采样深度。在 Marmoset Toolbag 4 中，$D_{\max}$ 默认值为模型轴对齐包围盒（AABB）对角线长度的 10%。缩小 $D_{\max}$ 会使薄壁区域的灰度差异更明显；设置过大则薄厚区域之间的对比度被压缩，导致贴图整体偏暗、细节丢失。

为减少单条射线的噪点，部分工具（如 Substance Painter 的"Thickness"烘焙器）支持设定**射线数量（Ray Count）**，默认 128 条射线在半球锥角内均匀采样后取平均值，锥角（Cone Angle）可在 0°–180° 之间调整：锥角为 0° 时退化为单条正反法线射线，锥角为 180° 时等价于半球全方向采样，此时结果接近反向 AO，而非严格的"沿法线"厚度。游戏生产中常用 30°–60° 锥角配合 64–256 条射线，以兼顾精度与烘焙速度。

### 与 AO 贴图的本质区别

环境光遮蔽（AO）烘焙时，射线朝**表面法线外侧的半球**发射，统计外部空间被几何体遮挡的比例，描述的是**外部空间的可见性**；厚度烘焙时，射线朝**反法线方向的内部**发射，统计网格体积的厚薄程度，描述的是**内部介质的密度**。二者在灰度图像上外观相似，但物理含义完全相反。在 Substance Painter 中两者属于不同烘焙通道（"Ambient Occlusion"与"Thickness"），若将 AO 贴图误接入引擎材质的 Thickness 插槽，SSS 效果将出现厚薄反转：原本应透光的薄壁区域反而变得不透明，原本不透光的厚实区域反而发出散射光。

### 与曲率贴图的区别

曲率贴图（Curvature Map）记录的是表面**曲率半径**——凸起区域为白，凹陷区域为黑（或相反）——用于描述表面形状的弯曲程度，常用于边缘磨损效果。厚度贴图记录的是**体积深度**，与表面曲率无关：一个扁平的薄板，其曲率贴图几乎全灰（曲率为零），但厚度贴图会正确显示出均匀的高亮度（极薄）。混淆两者是初学者常见的操作错误。

---

## 关键公式与参数设置

### 归一化厚度与线性空间

厚度贴图应始终存储在**线性色彩空间**（Linear Color Space）中，而非 sRGB 空间。若错误地将贴图设置为 sRGB 导入，引擎会对其进行 Gamma 2.2 解码，导致厚度值被非线性压缩：原本 0.5 的灰度值在 sRGB 解码后变为约 0.214，SSS 的透光量因此大幅衰减，耳廓、手指等薄壁区域的散射效果变弱。在 Unreal Engine 5 中，导入 Thickness Map 时须在贴图属性中将"sRGB"选项**关闭**，"Compression Settings"设为"Masks (no sRGB)"。

### 在 SSS 材质中的数学驱动关系

以 Unity HDRP 的 Subsurface Scattering 材质为例，厚度值 $T \in [0, 1]$ 与散射透射颜色 $C_{\text{transmit}}$ 的关系由 Diffusion Profile 中的**平均自由程（Mean Free Path，MFP）**决定：

$$
C_{\text{transmit}} = \exp\!\left(-\frac{T \cdot d_{\max}}{\lambda_{\text{MFP}}}\right) \cdot C_{\text{SSS}}
$$

其中 $\lambda_{\text{MFP}}$ 为各颜色通道的平均自由程（单位毫米）。根据 d'Eon 和 Irving（2011）的皮肤散射测量数据，人体皮肤的 MFP 在红色通道约为 **3.67 mm**，绿色通道约为 **1.37 mm**，蓝色通道约为 **0.68 mm**。这意味着红光能穿透更厚的组织，因此皮肤背光区域呈现红橙色散射光，而非白色。这些 MFP 数值在 Unity HDRP 的 Diffusion Profile Asset 中直接输入，厚度贴图的灰度值将按上式缩放最终散射强度。

---

## 实际应用

### 角色皮肤耳廓透光效果

制作写实人体角色时，耳廓部位的网格厚度通常为 2–4 毫米，烘焙后该区域 Thickness Map 接近纯白（归一化值约 0.85–1.0）。当主光源从角色脑后照射时，引擎读取该高值，将 SSS Diffusion Profile 的红橙色散射光叠加到耳廓正面，产生真实的透光效果。若不使用厚度贴图而仅依赖通用 SSS 强度，耳廓与脸颊的厚度差异无法体现，二者散射强度相同，失去立体感。

### 树叶半透明效果

植被树叶网格极薄（单片叶子厚度约 0.2–0.5 mm），烘焙时厚度贴图几乎全白。在 Unreal Engine 5 的 Two Sided Foliage 材质中，Thickness 贴图接入 **Subsurface Color** 驱动的蒙版，控制叶脉遮挡区域（深色叶脉处厚度相对较高，贴图较暗）与叶肉区域（较薄，贴图较亮）之间透光量的差异，使叶脉在背光时产生清晰的深色遮光条纹。

### 蜡烛与宝石材质

蜡烛模型从芯部向外厚度递增，Thickness Map 呈现中心黑、边缘白的渐变。在 Blender Cycles 的 BSSRDF 节点网络中，该贴图可接入 **Scale** 参数（控制散射尺度），中心厚实区域散射尺度更大，光线穿透更困难，蜡烛表现出真实的蜡质质感而非均匀发光的塑料感。

```python
# Blender Python：批量为选中物体烘焙厚度贴图并保存为 OpenEXR（线性空间）
import bpy

for obj in bpy.context.selected_objects:
    if obj.type != 'MESH':
        continue
    # 新建 2048x2048 厚度贴图
    img = bpy.data.images.new(
        name=f"{obj.name}_Thickness",
        width=2048, height=2048,
        float_buffer=True  # 保持线性浮点精度
    )
    # 为所有材质槽添加图像节点并选中
    for slot in obj.material_slots:
        mat = slot.material
        if mat and mat.use_nodes:
            nodes = mat.node_tree.nodes
            tex_node = nodes.new("ShaderNodeTexImage")
            tex_node.image = img
            nodes.active = tex_node
    # 烘焙（需在 Cycles 渲染器下）
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.ops.object.bake(type='DIFFUSE')  # 替换为插件扩展的 Thickness 烘焙类型
    # 保存为线性 EXR
    img.filepath_raw = f"//{obj.name}_Thickness.exr"
    img.file_format = 'OPEN_EXR'
    img.save()
```

---

## 常见误区

**误区一：将 Thickness Map 设置为 sRGB 导入**
如前所述，厚度贴图必须以线性空间导入。在 Substance Painter 中导出时，若选择了"8-bit sRGB"而非"8-bit Linear"或"16-bit Linear"，贴图数据已在导出阶段被 Gamma 编码，即便引擎侧关闭 sRGB 标记也无法完全还原，建议导出时直接选择线性色彩空间或使用 16-bit/32-bit EXR 格式。

**误区二：在开放式网格（Open Mesh）上烘焙厚度**
厚度烘焙要求网格必须是**封闭流形（Closed Manifold Mesh）**——即没有破洞、所有边都被两个多边形共享。若模型存在开放边（如裙摆底部未封口），烘焙射线从内部发出后无法击中对面，返回值为 0（最厚），导致该区域贴图全黑，SSS 效果完全消失。解决方法是在烘焙前临时封闭所有开放边，烘焙完成后再删除封口面。

**误区三：把厚度烘焙当作透明度贴图使用**
Thickness Map 的灰度值代表体积厚薄，**不等于**透明度（Alpha）。透明度决定表面是否被渲染，而厚度影响光线在介质内部的衰减。将厚度贴图直接接入 Opacity 插槽（而非 SSS 专用插槽）会使模型在薄壁区域呈现半透明镂空效果，而非散射透光效果，两者视觉结果截然不同。

**误区四：高低模法线方向不一致导致烘焙错误**
如果低模的法线朝向与高模存在大角度偏差（超过 90°），反法线射线会朝向网格外部而非内部，导致射线立即击中外部空间的其他几何体，产生异常的黑色条纹。解决方法是在烘焙前统一检查低模所有面的法线方向，确保向外一致，并适当调小笼子（Cage）的偏移量。

---

## 知识关联

### 与法线贴图的协作关系

法线贴图（Normal Map）负责在不增加多边形的前提下模拟表面凹凸细节，影响光照方向的计算；厚度贴图则描述体积信息，影响光线穿透量的计算。二者分别作用于表面着色