---
id: "guiux-tech-rich-text-impl"
concept: "富文本实现"
domain: "game-ui-ux"
subdomain: "ui-tech"
subdomain_name: "UI技术实现"
difficulty: 4
is_milestone: false
tags: ["ui-tech", "富文本实现"]

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


# 富文本实现

## 概述

富文本（Rich Text）是指在单一文本渲染上下文中混合使用不同字体、颜色、大小、内嵌图片和可交互超链接的技术方案。与普通文本渲染不同，富文本需要一个**标签解析层**将带有格式标记的原始字符串拆解为若干排版指令，再由渲染器按指令逐段输出最终画面。Unity的TextMeshPro、Unreal的RichTextBlock以及各主流游戏引擎均提供了不同程度的原生富文本支持，但在复杂需求下往往需要开发者自行扩展解析器。

富文本技术在游戏UI中的重要性源于其**内容密度**需求：一条对话气泡可能同时包含NPC名字的高亮颜色、技能名称的描边样式、伤害数值的红色加粗以及物品图标的内嵌精灵图，若用多个独立控件拼接则布局复杂、本地化困难，而富文本方案只需一条带标签字符串即可驱动整个排版。

---

## 核心原理

### 标签解析（Tag Parsing）

富文本的标签格式通常分为两类：HTML风格的尖括号标签（如 `<color=#FF0000>文本</color>`）和BBCode风格的方括号标签（如 `[b]文本[/b]`）。解析流程分三步：

1. **词法分析（Lexer）**：将原始字符串扫描为Token序列，区分普通字符Token与标签Token。`<color=#FF4500>` 会被识别为一个**开标签Token**，其属性值 `#FF4500` 被提取为参数。
2. **语法分析（Parser）**：将Token序列构建为**排版指令树（Span Tree）**，每个叶节点对应一段连续的纯文本，每个内部节点携带格式属性（颜色、字号、字体资产引用等）。
3. **属性继承**：子节点继承父节点的格式属性，`<b><color=red>X</color></b>` 中"X"同时具有粗体和红色，这通过在遍历Span Tree时维护一个**格式状态栈（Format State Stack）**来实现。

TextMeshPro的标签解析器在解析 `<size>` 标签时接受像素值（`<size=24>`）、百分比（`<size=150%>`）和em单位（`<size=1.5em>`），三种单位在内部均换算为当前字体资产的基准字号倍数后再写入顶点数据。

### 内嵌图片（Inline Sprite）

内嵌图片的核心挑战是**基线对齐（Baseline Alignment）**：图片作为一个不可分割的矩形块插入文本流，需要与周围字形的基线保持视觉上的对齐。实现步骤如下：

- 将图片视为一个**虚拟字形（Phantom Glyph）**，其宽度等于图片在当前行高下的等比缩放宽度，高度占用当前行的上升高度（Ascender）。
- 在生成顶点时，为该虚拟字形预留一块四边形（Quad），并将UV坐标指向Sprite Atlas中对应的图片区域。
- 若图片高度超过当前行高，则触发**行高重排**：整行所有字形的顶点Y坐标向下偏移，保证图片不裁切。

Unity TextMeshPro使用 `<sprite="AtlasName" index=3>` 或 `<sprite name="icon_gold">` 两种语法引用SpriteAsset中的图片，Sprite数据包含 `xAdvance`、`yOffset`、`scale` 三个排版参数，分别控制图片后的光标推进量、垂直偏移和缩放比例。

### 超链接（Hyperlink）

超链接在富文本中不产生视觉格式变化，而是在排版结果中为标签内的字符范围记录一组**可点击区域（Link Bounds）**。每个超链接节点存储：

- `linkID`：字符串标识符，如 `"item_1042"` 或 `"url_https://..."`
- `firstCharacterIndex` 和 `lastCharacterIndex`：在最终字形数组中的起止索引
- 由这两个索引推导出的**包围盒列表**（一个链接可能跨行，导致多个矩形区域）

点击检测时，将屏幕坐标转换到文本控件的本地坐标系后，遍历所有超链接的包围盒列表执行AABB碰撞测试，复杂度为 O(n×m)，其中 n 为超链接数量，m 为超链接跨越的行数。

### 自定义渲染器（Custom Renderer）

当内置标签无法满足需求时（如抖动文字、波浪动画、渐变色），需要实现**自定义渲染器钩子**。在TextMeshPro中，继承 `TMP_MeshModifier` 并重写 `ModifyMesh(VertexHelper vh)` 方法，可以在顶点提交给GPU之前对四边形顶点进行任意变换。常见模式：

```
// 波浪效果：对每个字形的顶点Y坐标施加正弦偏移
float offset = Mathf.Sin(Time.time * frequency + charIndex * phase) * amplitude;
```

其中 `frequency`（频率，Hz）、`phase`（相位差，rad/字符）、`amplitude`（振幅，像素）三个参数决定波浪形态。自定义渲染器需要在每帧强制标记Mesh为Dirty（`uiText.ForceMeshUpdate()`），以确保动画帧更新。

---

## 实际应用

**技能描述面板**：暗黑破坏神类游戏的技能Tooltip通常包含关键词高亮（`<color=#FFD700>灼烧</color>`）、数值引用（`<b>150%</b>武器伤害`）以及关键词超链接（点击"灼烧"弹出状态效果说明）。整段描述存储为单一本地化字符串，翻译人员可直接在字符串中调整标签位置，不影响代码逻辑。

**聊天系统**：MMO聊天频道中，物品链接使用 `<link="item:2049"><color=#1eff00>[寒冰法杖]</color></link>` 格式，服务端下发的字符串经客户端解析后渲染为绿色可点击文字，点击后触发物品预览面板。内嵌Emoji则通过Sprite Atlas实现，每个表情码对应Atlas中一张16×16或32×32的精灵图。

**对话系统打字机效果**：逐字显示时，富文本标签不能被截断。正确做法是先完整解析字符串得到字形列表，再通过 `visibleCharacters` 属性控制显示数量，而非截断原始字符串。若截断字符串，`<color=` 标签可能在中途被切断，导致后续文本全部变色。

---

## 常见误区

**误区一：标签嵌套顺序无关紧要**
`<b><color=red>X</b></color>` 与 `<b><color=red>X</color></b>` 在某些解析器中行为不同。前者关闭粗体时颜色标签尚未关闭，严格的XML解析器会报错，而宽松解析器（如TextMeshPro）会自动修复嵌套错误，但修复策略可能导致意外的样式截断。建议始终保持**后开先关（LIFO）**的标签顺序。

**误区二：内嵌图片可以任意缩放到所需尺寸**
内嵌图片的宽高比受SpriteAsset中预烘焙的 `xAdvance` 参数约束。若在标签中指定的显示尺寸与 `xAdvance` 不匹配，光标推进量将与实际渲染宽度不符，导致图片与后续文字重叠或产生多余空白。正确做法是修改SpriteAsset资产中的排版参数，而非单纯依赖标签中的 `size` 属性覆盖。

**误区三：富文本超链接检测可以用碰撞体组件实现**
给每段超链接文字加碰撞体意味着需要在文本内容变化时动态增删碰撞体，且在文字换行后需要为同一链接创建多个碰撞体。实际上直接使用文本控件的 `TMP_Text.GetLinkAtPosition()` 方法（内部即AABB测试）在每帧输入检测时调用，性能开销极低（微秒级），不应引入额外的物理组件。

---

## 知识关联

富文本实现以**分辨率缩放实现**为基础：内嵌图片的像素尺寸和字号的点值都依赖画布的缩放因子（Canvas Scaler的 `scaleFactor`）换算为实际渲染像素，若分辨率缩放配置错误，富文本中以像素为单位的 `<size=24>` 标签在不同分辨率设备上会呈现大小不一致的结果。

在富文本的自定义渲染器钩子中，对顶点颜色、UV坐标和顶点位移的操控，直接引出下一个主题 **UI Shader效果**：自定义渲染器负责在CPU侧修改顶点数据，而UI Shader则在GPU侧的片段着色阶段实现描边、发光、溶解等效果。两者可以叠加使用——渲染器提供逐字符的波浪位移，Shader提供描边，共同构成完整的动态文字特效管线。