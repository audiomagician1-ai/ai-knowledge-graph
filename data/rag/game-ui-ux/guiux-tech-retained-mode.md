---
id: "guiux-tech-retained-mode"
concept: "Retained Mode GUI"
domain: "game-ui-ux"
subdomain: "ui-tech"
subdomain_name: "UI技术实现"
difficulty: 3
is_milestone: false
tags: ["ui-tech", "Retained Mode GUI"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 76.3
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: intranet-llm-rewrite-v2
updated_at: 2026-04-01
---


# 保留模式GUI（Retained Mode GUI）

## 概述

保留模式GUI（Retained Mode GUI，简称RMGUI）是一种UI框架架构范式，其核心特征是框架在内存中维护一棵持久化的**场景树（Scene Tree）**，该树结构保存了所有UI元素的完整状态。与即时模式GUI每帧重新描述整个界面不同，保留模式框架只在状态发生变化时才更新受影响的节点，其余时间树结构保持"保留"在内存中不变。

保留模式GUI的概念可追溯至1980年代的窗口系统设计。微软的GDI（Graphics Device Interface）以及Apple Macintosh的QuickDraw都采用了这一思路。Win32 API中的窗口消息机制（WM_PAINT等）是早期保留模式的典型实现。现代游戏引擎中的Unreal Engine UMG（Unreal Motion Graphics）、Unity uGUI，以及Web领域的DOM（Document Object Model），均是保留模式GUI的代表性系统。

保留模式GUI在游戏UI开发中的重要性体现在它天然支持**事件驱动更新**：当玩家血量从100变为95时，只有血条节点及其父节点需要重绘，而不是整个HUD界面。这一特性使其在UI元素数量庞大、静态内容占多数的情况下具有显著的性能优势。

---

## 核心原理

### 场景树结构

保留模式GUI的基础数据结构是一棵有向无环的**节点树**。每个节点（Node）通常包含以下成员：变换矩阵（Transform）、尺寸（Size）、可见性标志（Visible）、子节点列表（Children）以及渲染数据缓存（RenderData）。树的遍历顺序决定了绘制顺序——子节点在父节点之后绘制，兄弟节点按列表顺序依次绘制，从而自然实现了UI层级和遮挡关系。

在Godot引擎中，Control节点构成的场景树是保留模式的标准实现：一个Button节点持久存在于内存中，即使玩家没有与之交互，该节点的矩形区域、文字内容、样式引用等数据都完整保留在树上。

### 脏标记机制（Dirty Flag）

脏标记（Dirty Flag）是保留模式GUI避免冗余计算的关键优化手段。每个节点维护一个或多个布尔标志位，例如`layout_dirty`和`render_dirty`。当某个节点的属性发生变化时，系统将该节点及其所有祖先节点标记为"脏"（dirty = true）。在下一帧的更新阶段，系统只遍历脏节点子树进行重新计算，而干净（clean）的节点直接跳过。

脏标记的传播方向是**双向**的：属性修改向上（Up）传播布局脏标记（因为子节点尺寸变化可能影响父节点布局），同时向下（Down）传播渲染脏标记（父节点的位移会使所有子节点的屏幕坐标失效）。这种分层脏标记设计将一次属性修改的更新代价从O(N)压缩到O(log N + 受影响子树大小)。

### 布局算法

保留模式GUI的布局通常采用**两遍（Two-Pass）算法**：

- **第一遍（Measure Pass）**：自下而上遍历树，每个节点根据自身内容和子节点期望尺寸，计算出自己的`desired_size`。公式为：`desired_size = max(min_size, content_size + padding * 2)`。
- **第二遍（Arrange/Layout Pass）**：自上而下遍历树，父节点将可用空间分配给子节点，每个子节点根据分配到的`final_rect`确定自身的实际位置和尺寸。

Unity uGUI的RectTransform系统就采用了这一两遍布局模型，其中`LayoutRebuilder.ForceRebuildLayoutImmediate()`方法会强制对指定节点执行完整的两遍布局，这在动态修改UI内容后经常被调用。Web浏览器的CSS盒模型布局本质上也是相同算法的变体。

---

## 实际应用

**游戏HUD血条更新**：在采用保留模式的游戏UI中，玩家受伤时只需调用`health_bar.set_value(new_hp)`，该操作将血条节点的`render_dirty`标记置为true，下一帧渲染时系统仅重绘血条的填充区域。场景树中其他数百个静态节点（技能图标、地图背景等）不参与任何计算。

**动态列表（Virtual List）**：当背包列表有500个物品格时，保留模式框架会维护全部500个节点的状态。为优化内存和绘制开销，工程师通常结合**节点池（Node Pool）技术**：只实例化屏幕可见的约10个节点，滚动时复用节点并更新其数据，而不是在树中保留500个完整节点。Unity uGUI的Scroll View配合对象池是这一模式的标准实践。

**过渡动画**：保留模式的持久化节点状态天然支持属性插值动画。Godot的Tween系统可以直接持有对节点属性的引用，在每帧将`modulate.alpha`从0.0插值到1.0，因为节点对象在整个动画过程中一直存在于内存中——这在即时模式中需要额外的状态存储才能实现。

---

## 常见误区

**误区一：认为保留模式一定比即时模式"更重"**。保留模式的内存开销确实高于即时模式（因为要在内存中维护完整节点树），但这不等于性能更差。在UI以静态内容为主、更新频率低的典型游戏场景中，保留模式通过脏标记跳过大量无变化节点的计算，总渲染开销反而更低。即时模式每帧全量提交CPU开销在UI节点超过数千个时会成为瓶颈，而保留模式在这种情况下优势明显。

**误区二：修改节点属性后立即生效**。在大多数保留模式实现中，属性修改只是设置脏标记，实际的布局重算和重绘发生在帧末的统一"刷新阶段"（Flush Pass）。Unity uGUI中常见的错误是在同一帧内修改Text内容后立即读取其RectTransform尺寸，得到的是旧尺寸——必须调用`Canvas.ForceUpdateCanvases()`才能获得更新后的正确值。

**误区三：场景树节点越少越好**。节点数量减少固然能降低树遍历开销，但过度合并节点会破坏脏标记的精细粒度，导致一处微小变化污染大范围子树，反而增加不必要的重绘。合理的节点粒度划分应以"独立变化的最小UI单元"为准，而非一味追求节点数量最小化。

---

## 知识关联

**前置概念——即时模式GUI**：理解保留模式必须对比即时模式（IMGUI）的"每帧重新声明UI"模型。IMGUI中没有持久化节点对象，`Button("Attack")`只是每帧执行一次的函数调用；而保留模式中Button是内存中长期存在的对象，这一根本差异解释了为何保留模式需要脏标记而IMGUI不需要。

**后续概念——数据绑定模式**：保留模式的持久化节点树为数据绑定（Data Binding）提供了物质基础。数据绑定框架（如Vue.js的虚拟DOM、Unity UI Toolkit的UXML绑定）正是在保留模式场景树的基础上，为节点属性与业务数据建立响应式连接，实现"数据变化自动触发脏标记"的自动化更新链路。可以说，不理解保留模式的脏标记机制，就无法真正理解响应式数据绑定框架的工作原理。