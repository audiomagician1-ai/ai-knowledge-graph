---
id: "guiux-tech-atlas-batching"
concept: "图集与合批"
domain: "game-ui-ux"
subdomain: "ui-tech"
subdomain_name: "UI技术实现"
difficulty: 3
is_milestone: false
tags: ["ui-tech", "图集与合批"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "B"
quality_score: 49.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 0.433
last_scored: "2026-03-22"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-03-27
---

# 图集与合批

## 概述

图集（Sprite Atlas）是将多张独立贴图打包成一张大贴图的技术手段，其核心目的是让GPU在一次DrawCall中渲染多个使用同一纹理的UI元素，从而降低CPU提交渲染命令的频次。在Unity的UGUI体系中，若两个Image组件引用了同一个Sprite Atlas中的精灵，渲染器会将它们合并为一个批次（Batch），只触发一次DrawCall；反之，若它们引用不同的Atlas或散图，则必然产生两次独立的DrawCall。

Sprite Atlas功能在Unity 2017.1版本中作为Sprite Packer的替代方案正式引入，并在Unity 2020.1版本中完成了V2版本的升级，支持更细粒度的打包策略控制。相比旧版Sprite Packer，Atlas V2允许开发者在编辑时直接查看打包结果，并支持"Always Include in Build"与"Include in Build"两种不同的构建包含策略。

理解图集与合批的意义在于：移动端GPU的DrawCall开销远比桌面端敏感，一帧内超过200次DrawCall在中端Android设备上可能导致帧率从60fps跌至30fps以下。通过合理的图集规划，通常可以将HUD界面的DrawCall数量从50+压缩至个位数。

## 核心原理

### DrawCall合批的触发条件

UGUI的合批系统基于**Canvas的Rebuild机制**，由`CanvasRenderer`组件收集同一Canvas下的所有可渲染元素，按照材质（Material）、纹理（Texture）、渲染层级（z-order）三个维度进行排序和分组。只有当相邻渲染元素满足**材质相同且纹理相同**的条件时，才会被合入同一批次。因此，两个Image使用同一Atlas中不同Sprite时，它们共享同一张底层纹理（`Texture2D`），满足合批条件；而即便两张图片视觉上完全相同，若属于不同Atlas，底层Texture实例不同，合批也会中断。

### 图集打包规则与UV偏移原理

打包工具将多张小图拼合到一张Atlas贴图（尺寸通常为1024×1024、2048×2048或4096×4096像素）时，会记录每张小图在大图中的**UV坐标偏移量（UV Offset）和缩放比（UV Scale）**。Sprite的UV数据公式为：

```
UV_final = UV_local × scale + offset
```

其中 `UV_local` 是原始精灵的归一化坐标（0~1范围），`scale` 是该精灵在Atlas中所占面积的比例，`offset` 是其左下角在Atlas中的归一化位置。渲染时Shader直接使用这套UV数据采样Atlas贴图，无需额外的运行时计算，性能开销与直接引用散图完全相同。

### 动态图集（Dynamic Atlas）

静态图集在编辑时打包完成，但动态图集允许在**运行时**动态插入新纹理。Unity的`DynamicAtlas`方案（以及第三方库如FairyGUI的动态合图）通过维护一个空闲区域列表（Free Rect List），使用**矩形装箱算法（Bin Packing，如Shelf-FF或MaxRects算法）**在运行时将新图片插入已有Atlas的空闲区域。动态图集适用于道具图标、头像等运行时才能确定内容的场景，但频繁的插入操作会触发`Texture2D.Apply()`，这是一次从CPU到GPU的纹理上传操作，耗时通常在0.5ms~5ms之间，需要避免在每帧高频调用。

### 图集层级打断与层叠问题

UGUI的合批是按照**Canvas层级树的深度优先顺序**依次检测的。当两个本可合批的元素之间插入了一个使用不同纹理的元素时，合批链会被**打断（Interleave Break）**，此后的元素即便纹理相同也无法合入前序批次。例如：ImageA（Atlas1）→ TextB（Font Atlas）→ ImageC（Atlas1），由于TextB打断了合批链，ImageA和ImageC产生2次DrawCall而非1次。解决方案是将相同Atlas的元素在层级树中相邻排列，或使用独立的Canvas隔离字体渲染层。

## 实际应用

**HUD界面优化案例**：典型的移动端游戏HUD包含血条、技能图标、货币图标约30个元素。优化前，每个技能图标来自独立PNG文件，30个元素产生28次DrawCall。将所有技能图标和UI装饰元素打包进一个2048×2048的Atlas后，DrawCall降至4次（HUD底图1次 + 技能图标合批1次 + 字体1次 + 血条Shader特殊材质1次）。

**图集分组策略**：按照"同屏出现频率"而非"功能类别"分组是业界推荐做法。主城界面的建筑图标和战斗界面的技能图标永远不会同时显示，应分入不同Atlas；而同一个Panel上的背景框、按钮、标签图标，无论功能差异，应强制归入同一Atlas。Unity的Sprite Atlas组件提供`Pack Preview`按钮，可在Editor中直接验证分组效果和纹理利用率（推荐利用率>75%）。

**动态图集的实际使用**：FairyGUI框架的动态合图功能（`UIConfig.dynamicAtlas = true`）会在运行时自动将散图合并，开发者无需手动建立Atlas。但需注意，动态图集的图片在退出某个UI页面后不会自动从Atlas中移除，需要调用`GComponent.Dispose()`确保图集内存正确回收，否则会出现图集纹理内存无法释放的泄漏问题。

## 常见误区

**误区一：图集越大越好**。许多开发者认为将所有UI图片塞入一个4096×4096的Atlas能最大化合批。实际上，4096×4096 RGBA32格式纹理占用内存64MB，在低端移动设备上会直接触发系统内存告警。且超大图集在首次加载时会产生长达数百毫秒的解码和上传延迟。正确做法是按照界面模块划分Atlas，单个Atlas控制在2048×2048以内，压缩格式使用ETC2（Android）或ASTC 4×4（iOS）将内存降低至8~16MB。

**误区二：所有元素都放入图集就能消除DrawCall**。图集只解决了纹理不一致的问题，但如果UI元素使用了不同的Material（如某个Image开启了`Mask`组件，Mask会创建一个新的材质实例），或者在元素之间存在不同纹理的元素打断合批链，DrawCall数量仍然无法降低。因此图集优化必须配合**层级结构的合理排布**和**避免不必要的Mask嵌套**才能发挥完整效果。

**误区三：动态图集与静态图集可以随意混用**。在同一Canvas中混合使用动态图集和静态图集时，若动态图集在运行时重新打包（Atlas Rebuild），会导致静态图集依赖的Canvas批次也发生Dirty，触发全量重建，产生单帧内明显的CPU峰值（通常表现为帧时间突增5~15ms）。

## 知识关联

图集与合批建立在**UI渲染管线**的基础上：UGUI的`Mesh`生成、`CanvasRenderer`的批次收集、以及最终的`DrawCall`提交流程，是理解为何图集能减少DrawCall的前置知识。掌握`SetPass Call`与`DrawCall`的区别（前者在材质切换时触发，后者在每次绘制命令时触发），有助于更精确地使用Frame Debugger分析图集优化效果。

从**图标图集管理**的工程实践角度，Addressable Asset System与Sprite Atlas的集成需要特别注意Atlas的依赖关系：若Atlas被多个Scene引用，应将其设置为独立的Addressable Group，避免重复加载占用冗余内存。

在学习后续的**事件系统**时，会接触到`GraphicRaycaster`的射线检测逻辑——该系统遍历所有`IPointerClickHandler`组件时与合批系统完全解耦，但错误使用大量全屏透明Image来扩展点击区域会意外影响合批效率，因为透明Image也会参与渲染批次计算，这是连接两个知识点的典型工程陷阱。