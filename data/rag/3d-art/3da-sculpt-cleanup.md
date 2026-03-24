---
id: "3da-sculpt-cleanup"
concept: "雕刻清理"
domain: "3d-art"
subdomain: "sculpting"
subdomain_name: "数字雕刻"
difficulty: 2
is_milestone: false
tags: ["流程"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "pending-rescore"
quality_score: 42.8
generation_method: "intranet-llm-rewrite-v2"
unique_content_ratio: 0.433
last_scored: "2026-03-25"
sources:
  - type: "ai-generated"
    model: "mihoyo.claude-4-6-sonnet"
    prompt_version: "intranet-llm-rewrite-v2"
scorer_version: "scorer-v2.0"
---
# 雕刻清理

## 概述

雕刻清理（Sculpt Cleanup）是指在数字雕刻工作完成后，对高模网格进行法线修复、几何噪点消除和拓扑问题矫正的流程阶段。与雕刻过程中随意堆叠细节不同，雕刻清理要求艺术家以"质检员"的眼光审视整个模型表面，消除因笔刷叠加、动态拓扑（DynaMesh/DynaTopo）生成而留下的伪影与破面。

这一概念在ZBrush 3.0时代开始被系统化，当时DynaMesh功能的引入使雕刻者可以随意增删多边形，但随之而来的是大量三角面混入四边形区域、法线朝向不一致等问题，促使工作室将"清理"单独列为流程节点。在Blender Sculpt Mode和ZBrush中，清理工作通常在Sub-Division Level最高层级完成，随后才交付给拓扑师进行Retopology。

雕刻清理直接决定了后续法线烘焙（Normal Map Baking）的质量。若高模表面存在法线翻转或凹陷孔洞，烘焙出的法线贴图会在对应区域产生黑点或光照异常，而这类错误在低模阶段几乎无法通过手动修改贴图来弥补，因此必须在高模清理阶段彻底解决。

---

## 核心原理

### 法线修复（Normal Repair）

法线是每个顶点或面片的垂直向量，用N表示，计算方式为相邻面的叉积归一化：**N = normalize(AB × AC)**。当雕刻笔刷（如Inflate或Flatten）以极端强度拖拽网格时，部分面的法线会翻转至模型内部，呈现负法线（Inverted Normals）状态。在ZBrush中可通过`Tool > Display Properties > Flip`快速检测翻转面；在Blender中开启Overlay面板的"Face Orientation"选项后，红色面片即为法线朝内的问题区域。修复手段包括：对选中面执行Recalculate Outside（快捷键Shift+N），或使用ZBrush的`Reconstruct Normals`功能对整个SubTool重新计算法线方向。

### 几何噪点消除（Geometry Noise Reduction）

高强度反复涂抹同一区域会产生"搓泥"效应——微小的三角形碎面堆积，形成肉眼几乎不可见但法线贴图烘焙时会呈现的高频噪点。针对这类问题，ZBrush的`Smooth`笔刷（快捷键Shift+拖拽）以拉普拉斯平滑（Laplacian Smoothing）为算法基础，对顶点坐标进行加权平均：**P_new = (ΣP_neighbor) / n**，其中n为相邻顶点数量。对于需要保留锐边的区域（如铠甲边缘），应改用`hPolish`笔刷配合低强度（Intensity约8-15）选择性平滑，避免硬边倒角特征被磨平。

### 孔洞与破面修复（Hole and Non-Manifold Fix）

动态拓扑在模型边缘或尖端处容易留下Non-Manifold边（即一条边连接超过两个面），这类几何错误会导致网格在布尔运算或烘焙时报错。ZBrush的`Geometry > Mesh Integrity > Fix Mesh`可自动检测并缝合小于阈值面积的孔洞，阈值建议设置在0.005-0.01模型单位之间；Blender则可通过`Mesh > Clean Up > Fill Holes`搭配`Merge by Distance`（合并距离0.0001m）两步操作完成同等修复。对于跨越较大面积的孔洞（如角色胸腔穿模区域），需手动切换至Edit Mode，用F键补面后再返回雕刻层级重新细化。

---

## 实际应用

**角色脸部雕刻清理案例：**  
在游戏角色脸部高模制作中，眼眶内侧、鼻孔边缘和嘴唇夹缝是法线翻转的高发区域，原因是艺术家在这些凹陷处使用了`Dam Standard`笔刷进行深度刻画，笔刷压力超过90%时极易将薄面拉穿。清理流程建议按"从整体到局部"顺序执行：① 先用`Smooth All`以强度5%对全脸过一遍消除高频噪点；② 开启Face Orientation叠加层逐区检查；③ 对眼眶区域单独Mask后执行`Recalculate Normals`；④ 最终导出前以Decimation Master压缩至原多边形数的60%并再次检查。

**硬表面装备清理案例：**  
机甲零件雕刻完成后，使用`Clip Curve`裁切出的切面边缘常残留非流形边。在ZBrush中执行`Tool > Geometry > Mesh Integrity`扫描后，将发现的Non-Manifold边数量控制在0才可提交。同时需用`ZRemesher`以当前多边形数量的1.5倍进行一次轻量化重拓扑，再手动在硬边处添加`Crease`标记，防止平滑后锐角消失。

---

## 常见误区

**误区一：雕刻清理等于无差别全局平滑**  
许多初学者将清理误理解为"对全模型执行多次Smooth"。实际上全局高强度平滑会连同有意设计的皮肤褶皱、肌肉走向等细节一并磨平。正确做法是在ZBrush中使用`Smooth Peaks`笔刷（专门对凸起顶点施加平滑，不影响凹陷纹理）或在Blender中配合顶点权重遮罩（Vertex Weight Mask）限制平滑范围。

**误区二：高模多边形数越多，清理后效果越好**  
部分学习者认为保留所有动态拓扑生成的高密度网格（如2000万面以上）可以储存更多细节。然而超过GPU显存承载上限（通常为1500-2000万面）后，多余的细节密度并不能被法线烘焙分辨率（通常为4096×4096，约1600万像素）所捕获，反而会在清理阶段增加运算时间并提高法线噪点概率。建议最终高模多边形数控制在满足烘焙分辨率需求的最低值。

**误区三：清理后无需再次验证法线**  
执行`Reconstruct Normals`操作本身也可能在高曲率区域（如耳廓、手指关节）引入新的法线错误。因此雕刻清理的最后一步必须是将模型导出OBJ后，在Marmoset Toolbag或Substance Painter中进行一次快速预烘焙验证，而不能仅凭ZBrush内部视口判断法线是否正确。

---

## 知识关联

**前置概念衔接：**  
雕刻清理承接自**细节雕刻**阶段——正是细节雕刻中高强度笔刷的使用产生了需要清理的法线翻转和几何噪点。了解`Dam Standard`、`Inflate`等笔刷的法线影响机制，是判断哪些区域需要重点清理的前提知识。

**后续概念衔接：**  
清理完毕的高模是**雕刻展示**的直接素材——展示用渲染需要干净的法线才能在Marmoset或KeyShot中得到准确的光照反馈；同时，无孔洞、无非流形边的高模也是**拓扑重构概述**所描述的Retopology工作的标准输入条件，拓扑师需要以高模表面为参考吸附新网格，破面或孔洞会导致吸附工具（如ZBrush ZRemesher Target Polygon Count）产生错误的面分布。
