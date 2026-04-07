# 富文本实现

## 概述

富文本（Rich Text）是指在单一文本渲染上下文中，通过标签驱动的排版指令混合使用不同字体、颜色、字号、描边样式、内嵌精灵图片与可交互超链接的技术方案。其根本价值在于"单一字符串驱动复合排版"：一条《暗黑破坏神IV》的物品词缀说明可以在同一段文字中包含橙色传奇词缀名、白色基础属性数值、红色警告文字和内嵌品质图标，若用多个独立UI控件拼接则在本地化扩展时文字长度的变化会破坏布局，而富文本方案仅需替换一条带标签的字符串即可驱动整个自动换行和对齐逻辑。

主流引擎的原生富文本实现包括：Unity的TextMeshPro（Stephan Bouchard于2016年作为独立插件首发，2018年4月随Unity 2018.2并入Package Manager正式成为标准组件）、Unreal Engine的`URichTextBlock`控件（随UE4.20在2018年引入，支持通过`RichTextBlockDecorator`扩展自定义标签）、Cocos Creator的`RichText`组件（2.x版本支持BBCode子集，3.x版本扩展了标签解析链），以及Web平台的HTML+CSS文本渲染管线。在自研引擎场景下，《魔兽世界》的聊天框架、《最终幻想XIV》的任务日志和《英雄联盟》的技能说明UI均各自实现了私有富文本系统，这说明原生方案在复杂需求下几乎必然需要扩展或替换其解析器与渲染器。

富文本实现的难度（本文评级4/9）主要集中在四个技术层面：标签的词法与语法解析、内嵌图片的基线对齐、超链接的命中检测以及自定义渲染器的扩展点设计。理解这四层的实现细节，是在游戏UI工程中稳定支撑大规模本地化内容的关键。

---

## 核心原理

### 标签解析层：词法分析与语法分析

富文本的标签格式分为两大流派：HTML风格尖括号标签（TextMeshPro采用，如 `<color=#FF4500>文本</color>`）和BBCode风格方括号标签（Cocos Creator RichText采用，如 `[color=#FF4500]文本[/color]`）。两者的解析管线在结构上完全一致，分三个阶段完成。

**阶段一：词法分析（Lexer）**

扫描原始字符串，将其拆分为Token序列。Token分为两类：**文本Token**（连续的非标签字符）和**标签Token**（从`<`或`[`到对应闭合符的完整标签字符串）。词法分析需处理以下边界情形：

- **转义字符**：`\<` 应输出字面量`<`而非触发标签开始；TextMeshPro使用 `\u003C` 作为Unicode转义替代方案。
- **多属性标签**：`<link="item:1023" color=#00CCFF>` 需将多个键值对提取到属性字典。
- **自闭合标签**：内嵌图片标签 `<sprite="icons" index=5>` 无对应闭合标签，词法层需识别此类终结符。

**阶段二：语法分析（Parser）与Span Tree构建**

将Token序列构建为**排版跨度树（Span Tree）**，每个叶节点代表一段纯文本Run，每个内部节点携带格式作用域（颜色、字号、字体资产引用、链接ID等）。解析算法维护一个**格式状态栈（Format State Stack）**：

- 遇到开标签则将当前格式状态的副本压栈，并在副本上叠加新标签的属性；
- 遇到闭标签则弹栈恢复；
- 孤立的开标签（无对应闭标签）在游戏实践中通常做**降级处理**（输出为纯文本），而非抛出异常——这一容错设计对本地化流程至关重要，防止翻译人员笔误导致整段UI在运行时崩溃。

整个解析过程的时间复杂度为 $O(n)$，其中 $n$ 为原始字符串的字符总数。

**阶段三：属性继承与字号单位换算**

子Span继承父Span的格式属性，`<b><color=red>X</color></b>` 中字符"X"同时拥有粗体与红色属性。TextMeshPro的 `<size>` 标签接受三种单位，内部统一换算为基准字号倍数：

$$\text{finalSize} = \text{baseSize} \times \begin{cases} \dfrac{v}{v_{\text{base}}} & \text{像素模式：} \texttt{<size=24>} \\ \dfrac{v}{100} & \text{百分比模式：} \texttt{<size=150\%>} \\ v & \text{em模式：} \texttt{<size=1.5em>} \end{cases}$$

其中 $v$ 为标签中给出的数值，$v_{\text{base}}$ 为字体资产（Font Asset）配置的基准像素字号。

### 内嵌图片：虚拟字形与基线对齐

内嵌图片（Inline Sprite）的核心挑战是**基线对齐（Baseline Alignment）**：图片是不可分割的矩形块，必须与周围字形的基线保持视觉一致，否则出现图文垂直错位。

实现将图片视为一个**虚拟字形（Phantom Glyph）**，其度量数据按以下规则确定：

- **宽度**：$w_{\text{sprite}} = h_{\text{line}} \times \dfrac{w_{\text{orig}}}{h_{\text{orig}}}$，即按当前行高等比缩放原始图片尺寸所得宽度；
- **上升高度（Ascender）**：默认取当前行的字体Ascender值，使图片顶端与大写字母顶端对齐；
- **超高触发重排**：若图片等比缩放后高度 $h_{\text{sprite}} > h_{\text{line}}$，则触发整行所有字形的Y坐标向下偏移 $\Delta y = h_{\text{sprite}} - h_{\text{line}}$，保证图片不被裁切。

在顶点生成阶段，渲染器为该虚拟字形预留一个四边形（Quad），UV坐标指向Sprite Atlas中对应图片的纹理区域。TextMeshPro使用 `<sprite="AtlasAsset" index=3>` 或 `<sprite="AtlasAsset" name="icon_fire">` 两种寻址方式，后者在Atlas打包后新增图片时无需修改标签字符串中的索引值，更利于迭代。

动画表情包（Animated Emoji）是内嵌图片的扩展需求：通过逐帧替换Quad的UV坐标实现帧动画，TextMeshPro原生不支持，需在自定义渲染器中每帧修改 `TMP_TextInfo.meshInfo[materialIndex].uvs2` 数组中对应字形的UV值，并调用 `textComponent.UpdateGeometry()` 提交更新。《原神》聊天框的表情动画即采用类似方案（帧率通常限制在8~12fps以降低CPU重新提交Mesh的开销）。

### 超链接：命中检测与回调路由

超链接（Hyperlink）实现分为**碰撞区域记录**和**点击事件路由**两部分。

TextMeshPro在完成排版后，每个 `<link>` 标签对应的字符范围会生成一组 `TMP_LinkInfo` 结构，存储在 `TMP_TextInfo.linkInfo` 数组中。每个 `TMP_LinkInfo` 记录链接ID字符串、起始字符索引和字符数量。在点击检测时，通过以下公式确定点击位置 $\vec{p}$ 对应的字符索引 $i$：

$$i = \texttt{TMP\_TextUtilities.FindIntersectingCharacter}(\text{textComp},\ \vec{p},\ \text{camera},\ \text{true})$$

获得 $i$ 后，遍历 `linkInfo` 数组找到包含该字符索引的链接条目，提取其 `linkID` 字符串传递给链接处理器。`linkID` 通常设计为可解析的复合键，例如 `"item:1023"` 或 `"quest:dialog_007"`，链接处理器按前缀分发到对应的业务逻辑模块，实现**超链接路由表（Link Router）**设计模式。

多行超链接存在**换行分段**问题：同一个链接跨越两行时，其碰撞区域是两个不连续的矩形，需对 `linkInfo` 中的字符范围按行分段，分别计算每段的包围盒，才能正确实现鼠标悬停高亮效果。

---

## 关键方法与公式

### 文字着色的顶点色方案

TextMeshPro的颜色系统不通过更换材质实现，而是将颜色写入每个字符四边形的**顶点色（Vertex Color）**，共享同一个材质实例。这使得一个TextMeshPro组件无论包含多少种颜色，其Draw Call数量维持在1（忽略Sprite Atlas额外材质）。顶点色在Shader中与字形纹理的Alpha通道相乘得到最终颜色：

$$C_{\text{final}} = C_{\text{vertex}} \times \alpha_{\text{SDF}}$$

其中 $\alpha_{\text{SDF}}$ 来自有向距离场（Signed Distance Field）字体纹理的采样结果，通过 $\alpha = \text{smoothstep}(0.5 - w,\ 0.5 + w,\ d)$ 控制边缘锐度，$w$ 为抗锯齿半宽，$d$ 为SDF纹理值（Lumb & Bouchard, 2018）。

### 渐变色标签的四顶点分配

`<gradient>` 标签为单个字符的四个顶点分别赋予不同颜色，实现逐字符渐变。对于从颜色 $C_0$（左上、左下顶点）到颜色 $C_1$（右上、右下顶点）的水平渐变，第 $k$ 个字符的混合权重为：

$$t_k = \frac{x_k - x_{\min}}{x_{\max} - x_{\min}}, \quad C_{\text{left},k} = \text{lerp}(C_0, C_1, t_k), \quad C_{\text{right},k} = \text{lerp}(C_0, C_1, t_{k+1})$$

其中 $x_k$ 为第 $k$ 个字符的左边界X坐标，$x_{\min}$ 和 $x_{\max}$ 为整段渐变文字的左右边界。

### BBCode解析的正则优化

在Cocos Creator等使用正则匹配解析标签的实现中，朴素的逐字符循环扫描对长字符串性能较差。工程实践中采用**单次正则扫描**代替嵌套循环：

```
/\[([a-z]+)(?:=([^\]]*))?\]|\[\/([a-z]+)\]|([^\[]+)/gi
```

该正则一次性匹配开标签（含可选属性值）、闭标签和纯文本段，时间复杂度降至 $O(n)$（单次线性扫描），比逐字符状态机实现在V8引擎上快约3~5倍（实测1000字符字符串：状态机约0.8ms，正则约0.2ms）。

---

## 实际应用

### 案例一：游戏物品描述的富文本结构

《暗黑破坏神》系列的物品描述系统是富文本的教科书级应用。以一件传奇物品的词缀描述为例，原始数据库存储的字符串可能为：

```
<color=#FF8C00>灼烧</color>：每秒对敌人造成 <color=#FF4500><b>{dmg_per_sec}</b></color> 点火焰伤害，
持续 <color=#FFFFFF>{duration}</color> 秒。
<sprite="ui_icons" name="icon_fire"> <color=#888888>（词缀等级：{affix_tier}/5）</color>
```

运行时数值填充（`{dmg_per_sec}` 替换为实际数值）在标签解析**之前**完成，使解析器只处理纯文本+标签的字符串，避免标签内出现花括号导致属性值解析错误。

### 案例二：《最终幻想XIV》的任务日志

FFXIV的任务日志使用私有富文本系统，其标签除基础颜色外还包含 `<highlight>NPC名字</highlight>` 用于NPC名字自动着色、`<item>物品名</item>` 用于物品超链接以及 `<br/>` 强制换行