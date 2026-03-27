---
id: "3da-uv-rizom-workflow"
concept: "RizomUV工作流"
domain: "3d-art"
subdomain: "uv-unwrapping"
subdomain_name: "UV展开"
difficulty: 2
is_milestone: false
tags: ["工具"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.6
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.448
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# RizomUV工作流

## 概述

RizomUV 是由法国公司 Rizom-Lab 于 2016 年从 UVLayout 独立发展出的专业 UV 展开软件，目前分为 Virtual Spaces（VS）和 Real Space（RS）两个版本，前者面向游戏和影视通用场景，后者专注于工业贴图应用。与 Maya 或 3ds Max 内置的 UV 编辑器相比，RizomUV 的核心优势在于其基于张力最小化算法的自动展开引擎，能够在保持面积比例的同时大幅减少手动调整时间。

RizomUV 的工作流以"切缝（Seam）→ 展开（Unfold）→ 打包（Pack）"三步为骨架，整个流程可以在软件内部全程完成，也可以通过官方提供的 Bridge 插件与 Maya、3ds Max、Blender、ZBrush 等主流 DCC 工具实现热链接同步。对于需要频繁迭代 UV 的游戏美术而言，这种跨软件的实时传输能力可以将往返操作从数分钟压缩到数秒。

掌握 RizomUV 工作流对游戏美术和影视 Look Dev 艺术家而言意义直接：在 1024×1024 贴图分辨率下，UV 面积浪费率每降低 10%，等效纹素密度即可提升约 11%，而 RizomUV 的自动打包算法在实际测试中普遍可将 UV 空间利用率维持在 85%～95% 之间，远高于手动排布的 60%～70% 平均水平。

---

## 核心原理

### 切缝策略与自动切缝工具

切缝是 RizomUV 工作流的起点，决定了 UV 展开后的变形程度。RizomUV 提供三种切缝方式：手动绘制（Paint Seams）、基于曲率的自动切缝（Auto Seams by Curvature）和基于角度阈值的自动切缝（Auto Seams by Angle）。其中角度阈值模式以边的二面角（Dihedral Angle）为判据，默认阈值通常设置为 88°，超过该角度的边将被标记为候选切缝，适合硬表面模型的快速处理。

对于有机体（如角色皮肤、植物），推荐优先使用曲率自动切缝并配合"Protect Quads"选项，这可以避免切缝落在视觉显眼的正面区域，将接缝集中到背侧或遮挡处。切缝布置完毕后，可在 3D 视口中以红色高亮实时预览切缝走向，便于在展开前做最后调整。

### 展开算法：ABF++ 与 LSCM

RizomUV 的展开核心是改进版的 ABF++（Angle-Based Flattening Plus Plus）算法，该算法以最小化角度变形为优化目标，其能量函数为：

**E = Σ (α_ij − β_ij)²**

其中 α_ij 为 2D 展开后三角形内角，β_ij 为对应 3D 网格内角。当该能量值趋近于 0 时，展开结果接近等角映射（Conformal Mapping），意味着形状失真最小，但面积比例可能发生缩放。RizomUV 在 ABF++ 之外还集成了 LSCM（Least Squares Conformal Maps）算法，用户可在 Unfold 面板中通过"Method"下拉菜单切换两者，通常 ABF++ 更适合形状复杂的有机体，LSCM 则对低多边形模型更为高效。

展开完成后，界面右侧的"Stretch Map"着色器会以蓝色（压缩）到红色（拉伸）的渐变色显示每个面片的形变程度，数值显示为 0.00～1.00，目标是使大多数面片处于绿色（接近 0.1 的低变形区间）。

### 自动打包（Auto Pack）与 UDIM 支持

RizomUV 的打包引擎采用基于离散旋转的矩形装箱算法，默认旋转步长为 90°，启用"Pixel Perfect"模式后可细化至任意角度，但会显著增加运算时间。打包时关键参数包括：

- **Spacing（间距）**：以像素为单位，游戏资产通常设置为 2～4 像素（基于目标贴图分辨率），防止相邻 UV 岛在 Mip 贴图生成时产生颜色渗透。
- **Margin（边距）**：UV 岛到 UV 空间边缘的安全距离，建议不低于 2 像素。
- **Target Resolution**：告知打包引擎计算 Spacing 时的参考分辨率，需与最终输出贴图尺寸一致。

RizomUV VS 版本原生支持 UDIM 工作流，可在 Pack 面板中指定 UDIM 分块数量（如 4×4 = 16 块），软件会自动将不同 UV 岛分配至对应 UDIM 瓦片并在 1001～1016 的瓦片编号范围内排布，与 Mari、Substance 3D Painter 的 UDIM 管线直接兼容。

---

## 实际应用

**游戏角色头部 UV 实例**：在为一个约 8000 面的角色头部模型做 UV 时，典型流程如下：①通过 Bridge 插件将模型从 Maya 发送至 RizomUV（快捷键 Ctrl+Alt+R）；②使用"Auto Seams by Curvature"在耳后、下颌底部和头顶区域自动生成切缝；③执行 ABF++ 展开，Stretch Map 显示大部分面片变形值低于 0.15；④在 Pack 面板中设置 Spacing=2px、Target Resolution=2048，点击"Pack All"；⑤通过 Bridge 将结果同步回 Maya，整个流程约 3～5 分钟。

**硬表面道具 UV 实例**：对于一把枪械模型，切缝策略改为"Auto Seams by Angle（阈值 85°）"，这样所有锐利边缘都会成为切缝，各个平面零件被切为独立的矩形 UV 岛。打包时开启"Orient to Bounding Box"选项，确保矩形岛以最优方向排列，最终空间利用率可达 91%。

**Python/Lua 脚本批处理**：RizomUV 内置 Lua 脚本接口，允许将上述参数设置录制为脚本并批量处理同类资产，例如游戏场景中数十个使用相同参数规范的道具模型可通过一段约 20 行的 Lua 脚本完成全自动展开与打包。

---

## 常见误区

**误区一：展开后直接打包，忽略 Stretch Map 检查**。许多初学者在 ABF++ 展开完成后立即进入打包阶段，忽略了 Stretch Map 中显示为红色的高变形区域。这些区域在烘焙法线贴图时会产生明显的错误切线方向，导致光照计算失真。正确做法是对 Stretch 值超过 0.3 的岛片手动追加切缝并重新展开，直至全图绿色占主导。

**误区二：将 Spacing 像素值固定为绝对数值而非相对于目标分辨率**。例如，有人习惯在任何项目中都将 Spacing 设为 4 像素，但如果目标贴图是 512×512，4 像素间距占总贴图宽度的 0.78%，在 Mip Level 3（64×64）时该间距只剩半个像素，依然可能出现渗色。应当在"Target Resolution"中准确填写目标尺寸，由 RizomUV 据此自动换算合理间距。

**误区三：认为"岛数量越少越好"而过度合并 UV 岛**。RizomUV 的打包算法对不规则形状的利用率并不随岛数量减少而线性提升。强行合并两个形状差异大的岛片会引入严重的展开变形，实际上将若干小型矩形岛保持独立，打包利用率反而更高，并且便于后续在 Substance 3D Painter 中使用智能材质时对各岛片进行单独调整。

---

## 知识关联

RizomUV 工作流建立在对**切缝工具**使用逻辑的理解之上，若对"二面角阈值"和"曲率切缝"概念陌生，需先在 Maya UV Editor 或 Blender 的 UV Unwrap 工具中建立手动切缝经验，才能理解 RizomUV 自动切缝背后的判断依据。

在参数层面，RizomUV 中的 ABF++ 算法与通用 3D 数学中的等角映射理论直接对应，理解其能量函数 **E = Σ(α_ij − β_ij)²** 有助于预判哪类模型（曲率变化剧烈 vs 平缓）需要更密集的切缝才能压低变形值。

从工作流下游看，RizomUV 打包输出的 UV 布局直接影响后续在 Substance 3D Painter 中的烘焙质量（尤其是法线贴图和 AO 贴图的 Cage 精度）以及 Mari 中 UDIM 绘制的分辨率分配策略，是连接建模阶段与纹理绘制阶段的实质性技术节点。