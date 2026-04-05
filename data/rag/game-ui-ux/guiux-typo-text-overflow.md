---
id: "guiux-typo-text-overflow"
concept: "文本溢出处理"
domain: "game-ui-ux"
subdomain: "typography"
subdomain_name: "字体排版"
difficulty: 2
is_milestone: false
tags: ["typography", "文本溢出处理"]

# Quality Metadata (Schema v2)
content_version: 2
quality_tier: "A"
quality_score: 73.0
generation_method: "ai-rewrite-v1"
unique_content_ratio: 1.0
last_scored: "2026-04-05"
sources:
  - type: "ai-generated"
    model: "claude-sonnet-4-20250514"
    prompt_version: "ai-rewrite-v1"
scorer_version: "scorer-v2.0"
quality_method: tier-s-booster-v1
updated_at: 2026-04-05
---




# 文本溢出处理

## 概述

文本溢出处理是指当字符串内容超出其容器边界时，游戏UI系统所采用的视觉呈现与交互策略。在游戏界面中，角色名称框、物品描述栏、对话气泡、任务标题、聊天频道消息等大量元素都受到固定像素尺寸的约束，而玩家输入或数据库内容的字符数量往往无法预测，因此溢出处理必须在UI设计阶段主动规划。

这一问题在游戏UI中比通用桌面软件更为突出，根本原因在于游戏内容高度多语言化。同一段英文UI文字在德语本地化后长度平均增加30%至35%，在芬兰语中可增加60%以上；而中日韩（CJK）字符在16px字号下每个字形通常占16×16像素，而同等字号的拉丁字母平均字形宽度仅约8至10像素。Unity的TextMeshPro组件（自2018.1版本起内置于Unity）和Unreal Engine的UMG文本控件均内置了溢出模式枚举（`TextOverflowModes` 和 `ETextOverflowPolicy`），说明溢出处理已被主流引擎标准化为一等公民特性。

未经处理的溢出会导致文字渲染超出UI边框、与相邻HUD元素重叠，甚至在使用Stencil裁切时触发层级错误，在移动端游戏中直接引发App Store/Google Play的用户差评。根据《游戏本地化实践》（Chandler & Deming, 2012），文本溢出是本地化QA阶段发现频率最高的排版缺陷类别之一。

---

## 核心原理

### 截断（Truncation）

截断是最简单的溢出策略：当文本宽度超出容器时，超出部分直接被裁掉，不显示任何提示符号。渲染器逐字符累加**字形前进宽度（Glyph Advance Width）**，一旦第 $N$ 个字符的右边界 $x_N > W_{container}$，第 $N$ 个及之后的所有字符全部丢弃。前进宽度存储于OpenType字体文件的 `hmtx`（Horizontal Metrics）表中，单位为字体设计单位（Font Units），需乘以缩放因子 $\frac{fontSize}{unitsPerEm}$ 转换为像素值。

截断适用于排行榜ID列、战斗浮字、地图标注点等对内容完整性要求极低且空间极度紧张的场景。其核心缺陷是用户无法感知内容被省略，因此只应用于辅助性、低信息密度的UI元素。

### 省略号（Ellipsis）

省略号策略在截断基础上，将末尾若干字符替换为"…"（Unicode U+2026，HORIZONTAL ELLIPSIS，单字形）或三个英文句点"..."（共三个U+002E字形）。设容器宽度为 $W$，省略号字形的前进宽度为 $E$，则可分配给正文字符的最大像素宽度为 $W - E$：

$$
x_{last} = \max\{ x_n \mid x_n \leq W - E,\ n \in [1, N] \}
$$

渲染器在满足该约束的最后一个完整字符后插入省略号字形。需注意，中文字符不应在省略号前被强制拆分到半个字宽处——实现时应以字符（而非字节或子像素）为粒度向前搜索截断点。

CSS标准中对应属性为 `text-overflow: ellipsis`，必须与 `overflow: hidden` 和 `white-space: nowrap` 同时声明：

```css
.item-name {
  width: 120px;          /* 容器固定宽度 */
  white-space: nowrap;   /* 禁止自动换行，否则 ellipsis 不触发 */
  overflow: hidden;      /* 裁切溢出内容 */
  text-overflow: ellipsis; /* 在截断点插入 U+2026 */
}
```

在Unity TextMeshPro中，对应枚举为 `TextOverflowModes.Ellipsis`，可通过脚本动态切换：

```csharp
// Unity TextMeshPro 动态切换省略号模式
TMP_Text label = GetComponent<TMP_Text>();
label.overflowMode = TextOverflowModes.Ellipsis;
label.text = playerName; // 超出时自动在末尾显示 "…"
```

省略号广泛用于物品名称、任务标题（《魔兽世界》任务日志标题超过约28个英文字符时自动触发省略）、角色名称标签等场景，是兼顾空间节省与内容提示的平衡方案。

### 自动换行（Word Wrap / Auto Wrap）

自动换行允许文本在到达容器右边界时折到下一行，容器高度随之扩展或保持固定（固定高度时超出行数再由截断或省略兜底）。换行算法有两种主流实现：

**贪心换行（Greedy Wrap）** 逐行从左到右填充尽可能多的单词或字符，遇到空格或CJK字符边界时尝试换行。时间复杂度为 $O(n)$，适合游戏引擎实时计算。

**Knuth-Plass最优换行算法** 由Donald Knuth和Michael Plass于1981年在TeX排版系统中提出（Knuth & Plass, 1981），通过对全段落所有可能的断行方案打分，最小化各行末尾空白的平方和（称为"坏度值 Badness"），避免出现最后一行只有单个孤字的"widow"现象。该算法的时间复杂度为 $O(n^2)$，计算开销在逐帧刷新的动态游戏UI中代价过高，因此游戏引擎普遍采用贪心换行。

中文文本由于词间无空格，换行点可在任意字符间插入，但必须遵守**行首禁则（Forbidden Start Characters）**：句号（。）、逗号（，）、顿号（、）、右括号（）」）、感叹号（！）等20余个标点禁止出现在行首；**行尾禁则**则禁止左括号（「（【）出现在行尾。违反禁则会被Unicode标准《UAX #14: Unicode Line Breaking Algorithm》标记为非法断行。

### 滚动显示（Scrolling / Marquee）

滚动显示适用于空间固定但内容必须完整呈现的场景，如NPC名称条、聊天气泡、跑马灯公告。实现上分两类：

- **水平滚动（Marquee）**：文本从容器右端进入，向左匀速移动，速度通常设置为每秒60至120像素（依字号而定）。需注意文本首尾衔接时应插入约1.5倍容器宽度的空白间隔，避免两段文本视觉粘连。
- **垂直滚动（Scroll View）**：文本在固定高度容器内上下拖拽，常见于背包物品描述面板。Unity的 `ScrollRect` 组件和Unreal的 `ScrollBox` 控件均原生支持惯性滑动（Inertia），需将 `Deceleration Rate` 调至0.135左右以匹配手机端拇指操作手感。

---

## 关键公式与计算

### 省略号截断点计算

设字符序列 $c_1, c_2, \ldots, c_N$ 的前进宽度分别为 $a_1, a_2, \ldots, a_N$，容器宽度为 $W$，省略号宽度为 $E$，字间距（Letter Spacing）为 $\delta$。省略号插入位置 $k$ 为满足下式的最大整数：

$$
k = \max\left\{ k \;\middle|\; \sum_{i=1}^{k}(a_i + \delta) + E \leq W \right\}
$$

若 $k = 0$（即省略号本身的宽度已超过容器），则直接截断省略号，仅显示空白容器，这种极端情况需在设计阶段通过设置容器最小宽度来规避。

### 多语言容器尺寸安全余量

基于Chandler & Deming（2012）提供的本地化膨胀率数据，UI容器在英文设计稿基础上应保留的安全余量为：

| 源语言 → 目标语言 | 平均膨胀率 | 推荐容器冗余系数 |
|---|---|---|
| 英语 → 德语 | +35% | ×1.4 |
| 英语 → 芬兰语 | +60% | ×1.65 |
| 英语 → 中文 | -20%（收缩） | ×1.0 |
| 英语 → 俄语 | +45% | ×1.5 |

---

## 实际应用案例

**案例1：《原神》角色名称标签**
《原神》的角色世界名称标签在宽度约80像素的容器中使用省略号策略，同时在鼠标悬停时通过Tooltip完整显示名称。中文版角色名称（通常4至6个汉字）在此容器内几乎不触发溢出，而英文版"Hu Tao"等名称同样安全；但德语或俄语本地化版本中，若角色拥有自定义昵称则可能触发省略。

**案例2：《炉石传说》卡牌描述文本**
《炉石传说》卡牌描述区域（约220×90像素）采用自动缩小字号（Auto-Size）策略，而非省略号：当文字在默认14px字号下溢出时，字号逐步缩减至最小阈值10px。这是省略号之外的第五种溢出策略——**自动缩放（Auto-Fit）**，TextMeshPro通过 `enableAutoSizing = true`、`fontSizeMin = 10`、`fontSizeMax = 14` 三个参数实现。

**案例3：MMO游戏聊天框**
大型MMO游戏（如《最终幻想XIV》）的聊天频道采用固定行数（通常12行）的滚动视图，新消息追加到底部并触发自动滚动。当玩家手动上翻时，自动滚动暂停，出现"↓新消息"提示按钮，点击后恢复自动跟随——这是滚动显示与交互设计的结合。

---

## 常见误区

**误区1：用截断代替省略号以节省计算量**
截断不显示任何省略提示，用户看到的文本可能在语义上完全错误（如"不可以攻击"被截断为"不可以"产生相反语义）。省略号的额外计算开销在现代GPU上可忽略不计，不应以性能为由放弃省略号。

**误区2：省略号位置按字节而非字符计算**
在UTF-8编码下，一个中文字符占3字节，若按字节截断会在字符中间切断，产生乱码字形（Mojibake）。TextMeshPro内部使用Unicode代码点（Code Point）遍历，开发者自行实现截断逻辑时必须使用 `string.Length`（C# 中返回UTF-16代码单元数）或更精确的 `StringInfo.GetTextElementEnumerator()` 处理代理对（Surrogate Pair）字符。

**误区3：对话气泡高度不设上限**
若对话气泡容器高度完全由文本内容决定，当玩家输入极长文本时气泡可能覆盖整个屏幕。正确做法是设置 `maxHeight` 阈值，超出时切换为滚动视图模式，并给出视觉提示（如底部渐变遮罩）。

**误区4：滚动速度对所有文本长度使用固定值**
固定60px/s的滚动速度对10个字符的短文本会显得过慢，对200个字符的长公告又太快。推荐按阅读速度（成年玩家平均中文阅读速度约600字/分钟）反算：目标展示时长 $T = \frac{N_{chars}}{600/60}$ 秒，再由容器宽度和文本总宽度计算实际像素速度。

---

## 知识关联

**前置知识：字距与行距**
省略号宽度 $E$ 的计算依赖字距（Letter Spacing）参数 $\delta$——若UI设计师调整了字距，截断点公式中的 $\delta$ 必须同步更新，否则省略号可能溢出容器右边界1至3像素，在Retina屏幕上清晰可见。行距（Line Height）则决定了自动换行模式下容器在垂直方向的扩展步长，行距设为1.2倍字号时，一个16px文本的每次换行使容器高度增加 $16 \times 1.2 = 19.2 \approx 20$ 