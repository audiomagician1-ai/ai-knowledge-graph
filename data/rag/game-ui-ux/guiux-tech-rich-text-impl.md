# 富文本实现

## 概述

富文本（Rich Text）是指在单一文本渲染上下文中混合使用不同字体、颜色、大小、内嵌图片和可交互超链接的技术方案。与普通文本渲染不同，富文本需要一个**标签解析层**将带有格式标记的原始字符串拆解为若干排版指令，再由渲染器按指令逐段输出最终画面。Unity的TextMeshPro（Stephan Bouchard, 2016年首次发布为独立插件，2018年并入Unity Package Manager）、Unreal Engine的`URichTextBlock`控件（UE4.20引入）以及Cocos Creator的RichText组件均提供了不同程度的原生富文本支持，但在复杂需求下往往需要开发者自行扩展解析器和自定义渲染器。

富文本技术在游戏UI中的重要性源于其**内容密度**需求：一条对话气泡可能同时包含NPC名字的高亮颜色、技能名称的描边样式、伤害数值的红色加粗以及物品图标的内嵌精灵图，若用多个独立控件拼接则布局复杂、本地化困难，而富文本方案只需一条带标签字符串即可驱动整个排版。《最终幻想XIV》的任务日志、《暗黑破坏神IV》的物品词缀说明和《魔兽世界》的聊天频道都是大规模依赖富文本系统的典型案例。

---

## 核心原理

### 标签解析（Tag Parsing）

富文本的标签格式通常分为两类：HTML风格的尖括号标签（如 `<color=#FF0000>文本</color>`）和BBCode风格的方括号标签（如 `[b]文本[/b]`）。TextMeshPro采用前者，而Cocos Creator的RichText组件采用后者，两者解析流程在结构上一致，分三步完成：

1. **词法分析（Lexer）**：将原始字符串扫描为Token序列，区分普通字符Token与标签Token。`<color=#FF4500>` 会被识别为一个**开标签Token**，其属性值 `#FF4500` 被提取为参数存入Token的属性字典。词法分析需处理转义字符（如 `\<` 表示字面量尖括号），以及嵌套属性（如 `<link="url" color="blue">`）的多属性解析。

2. **语法分析（Parser）**：将Token序列构建为**排版指令树（Span Tree）**，每个叶节点对应一段连续的纯文本，每个内部节点携带格式属性（颜色、字号、字体资产引用等）。未匹配的开标签（孤立标签）通常被降级处理为纯文本输出，而非抛出异常——这一容错设计在游戏本地化流程中尤为重要，防止翻译人员的笔误导致整段UI崩溃。

3. **属性继承**：子节点继承父节点的格式属性，`<b><color=red>X</color></b>` 中"X"同时具有粗体和红色，这通过在遍历Span Tree时维护一个**格式状态栈（Format State Stack）**来实现。每进入一个内部节点则将当前格式副本压栈，退出时弹栈恢复，其时间复杂度为 $O(n)$，其中 $n$ 为字符串中标签与字符Token的总数量。

TextMeshPro的标签解析器在解析 `<size>` 标签时接受三种单位格式：像素值（`<size=24>`）、百分比（`<size=150%>`）和em单位（`<size=1.5em>`）。三种单位在内部均换算为当前字体资产基准字号的倍数：

$$\text{finalSize} = \text{baseSize} \times \begin{cases} \dfrac{v}{v_{\text{base}}} & \text{像素模式} \\ \dfrac{v}{100} & \text{百分比模式} \\ v & \text{em模式} \end{cases}$$

其中 $v$ 为标签中给出的数值，$v_{\text{base}}$ 为当前字体资产配置的基准像素字号。

### 内嵌图片（Inline Sprite）

内嵌图片的核心挑战是**基线对齐（Baseline Alignment）**：图片作为一个不可分割的矩形块插入文本流，需要与周围字形的基线保持视觉上的对齐。实现步骤如下：

- 将图片视为一个**虚拟字形（Phantom Glyph）**，其宽度等于图片在当前行高下的等比缩放宽度，高度占用当前行的上升高度（Ascender）。
- 在生成顶点时，为该虚拟字形预留一块四边形（Quad），并将UV坐标指向Sprite Atlas中对应的图片区域。
- 若图片高度超过当前行高，则触发**行高重排**：整行所有字形的顶点Y坐标向下偏移，保证图片不裁切。

Unity TextMeshPro使用 `<sprite="AtlasName" index=3>` 或 `<sprite name="icon_gold">` 两种语法引用SpriteAsset中的图片。SpriteAsset的每条精灵记录包含 `xAdvance`（图片后的光标推进量）、`yOffset`（垂直偏移，用于微调与基线的相对位置）和 `scale`（缩放因子，默认1.0）三个排版参数，这三个值在SpriteAsset的Inspector面板中需逐条手动标定，这是内嵌图片最耗费美术协作成本的环节。

Unreal Engine的`FRichTextDecorator`扩展接口允许开发者为自定义标签（例如 `<itemicon id="potion"/>`）注册专属装饰器，装饰器的 `CreateDecoratorWidget` 方法返回一个任意`UWidget`，该Widget被内嵌进`SRichTextBlock`的Slate布局中作为行内Widget处理，其基线偏移通过 `FSlateWidgetRun::FWidgetRunInfo::Baseline` 字段显式指定（Epic Games, Unreal Engine 5.3 Documentation）。

### 超链接（Hyperlink）

超链接在富文本中并非单一渲染概念，而是涉及**命中测试（Hit Testing）**与**渲染装饰**的复合功能。其实现分两个独立层面：

**渲染层**：超链接文字通常有下划线修饰，下划线并非字形轮廓的一部分，而是在排版完成后额外绘制的水平线段。TextMeshPro使用 `<link="id">` 标签，在顶点生成阶段将链接范围内所有字形的包围盒X范围记录于 `TMP_LinkInfo` 数组，以供后续命中测试使用。

**交互层**：每帧在 `OnPointerClick` 或触摸事件回调中，调用 `TMP_TextUtilities.FindIntersectingLink(textComponent, position, camera)` 查询当前点击坐标命中的链接索引，时间复杂度为 $O(L)$（$L$ 为当前文本中链接段的数量）。命中后通过 `TMP_LinkInfo.GetLinkID()` 取回链接ID字符串，由业务逻辑层决定后续行为（打开URL、触发对话分支、展示物品Tooltip等）。

例如，在《星球大战：旧共和国》的任务日志实现中，超链接被用于在同一富文本段落内既渲染NPC名称高亮，又支持点击该名称弹出NPC详情卡片，链接ID直接存储NPC的数据库主键，实现了UI展示与数据逻辑的完全解耦。

---

## 关键方法与公式

### 排版坐标系

富文本排版的基础坐标系沿用OpenType字体规范（OpenType Specification 1.9, Microsoft & Adobe, 2021）定义的五条参考线：

- **基线（Baseline）**：$y = 0$，字形排布的基准水平线。
- **上升线（Ascender）**：$y = +\text{ascender}$，大写字母顶部（如"H"的顶边）。
- **下降线（Descender）**：$y = -\text{descender}$，小写字母尾部（如"g"的底边）。
- **行间距（LineGap）**：两行基线间距 $= \text{ascender} + \text{descender} + \text{lineGap}$。
- **x高度（x-height）**：小写字母"x"顶部高度，用于内嵌图片的视觉居中对齐时的参考值。

在实际富文本布局中，行高（Line Height）的计算公式为：

$$H_{\text{line}} = \max_{i \in \text{glyphs}} \left( A_i + D_i \right) \times \text{lineSpacingMultiplier}$$

其中 $A_i$ 为第 $i$ 个字形（或内嵌图片）的上升高度，$D_i$ 为其下降高度，`lineSpacingMultiplier` 为设计师可调节的行距倍率（TextMeshPro默认1.0，推荐游戏UI使用1.0–1.2区间）。

### 自定义渲染器接口

在需要超越引擎原生能力的场景下（例如文字描边宽度超过TextMeshPro的单Pass SDF限制，或需要逐字渐变动画），开发者需实现**自定义渲染器（Custom Renderer）**。以TextMeshPro的Mesh顶点后处理为例，核心接口为：

```
TMP_TextInfo.characterInfo[i].vertex_BL / BR / TL / TR
```

每个字形由四个顶点构成的Quad表示，每个顶点包含 `position`（$\mathbb{R}^3$）、`color`（`Color32`）和 `uv0`/`uv1`（$\mathbb{R}^2$）。自定义渲染器在 `OnPreRenderText` 回调中遍历 `characterInfo` 数组，按业务规则修改顶点数据后调用 `textComponent.UpdateVertexData()` 提交修改，整个过程无需重新解析标签字符串，性能开销仅为顶点数据的CPU写入成本。

例如，实现**逐字打字机动画**时，只需在每帧将已显示字符数之后的所有字符顶点的 `color.a` 强制设为0，而非操作字符串本身，避免了每帧重新触发标签解析的 $O(n)$ 开销。

---

## 实际应用

### 案例一：技能描述动态数值高亮

《暗黑破坏神IV》风格的技能描述需要将数值（如伤害量、冷却时间）以不同颜色区分于说明文字。实现方案是在服务器或本地计算完成后，将数值填入预设的富文本模板字符串：

```
"造成 <color=#FF6B35>{0}</color> 点火焰伤害，冷却时间 <color=#7EC8E3>{1}</color> 秒"
```

`String.Format` 或 `StringBuilder` 替换占位符后传入TextMeshPro，总字符串构建开销通常在0.1ms以下（在Unity 2022 LTS，i7-11700K测试），适合每秒更新频率不超过30次的UI场景。若更新频率更高（如每帧更新的伤害跳字），则应改用顶点颜色后处理方案，绕开字符串重解析。

### 案例二：聊天系统的BBCode过滤与安全沙箱

在MMO游戏的玩家聊天频道中，玩家输入的文本必须经过**标签白名单过滤**，防止恶意注入（例如通过 `<link>` 标签携带钓鱼URL，或通过 `<size=9999>` 撑大布局）。安全的实现策略是：

1. 接收原始字符串后，先转义所有 `<` 和 `>` 字符为HTML实体（`&lt;` / `&gt;`）。
2. 仅对白名单格式（粗体 `<b>`、颜色 `<color>`、内嵌图片 `<sprite>`）执行反转义恢复。
3. 所有 `<link>` 标签及其 `href` 属性在玩家输入路径上被永久过滤，仅系统消息可生成超链接。

### 案例三：多语言自动换行与CJK处理

日文、中文、韩文（CJK）字符的换行规则与拉丁文本不同：CJK字符可在任意字符间换行，但标点符号（如 `。`、`、`、`）`）不能出现在行首（行首禁则，Kinsoku Shori，Unicode Standard Annex #14）。TextMeshPro 3.0+内置了`Line Breaking Rules`资产，允许为每种语言配置行首禁则字符集和行尾禁则字符集，富文本解析器在