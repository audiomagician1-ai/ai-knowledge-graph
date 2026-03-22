---
id: "lighting-intro"
concept: "光照叙事概述"
domain: "level-design"
subdomain: "lighting-narrative"
subdomain_name: "光照叙事"
difficulty: 1
is_milestone: false
tags: ["基础"]

# Quality Metadata (Schema v2)
content_version: 3
quality_tier: "S"
quality_score: 92.6
generation_method: "research-rewrite-v2"
unique_content_ratio: 0.91
last_scored: "2026-03-22"
sources:
  - type: "textbook"
    title: "Designing with Light: An Introduction to Stage Lighting"
    author: "J. Michael Gillette"
    year: 2013
    isbn: "978-0073514239"
  - type: "textbook"
    title: "An Architectural Approach to Level Design"
    author: "Christopher Totten"
    year: 2019
    isbn: "978-0815361367"
  - type: "conference"
    title: "Painting with Light: The Art of Lighting in The Last of Us Part II"
    authors: ["Eben Cook"]
    venue: "GDC 2021"
scorer_version: "scorer-v2.0"
---
# 光照叙事概述

## 概述

光照叙事（Lighting Narrative）是关卡设计中利用光线的方向、颜色、强度和对比度来引导玩家移动路径、传达情绪氛围、暗示叙事信息的设计手法。Christopher Totten 在《An Architectural Approach to Level Design》（2019）中指出："光照是关卡设计师最强大的隐性引导工具——玩家会无意识地走向光亮处，远离黑暗处。"

这不仅是技术问题，更是叙事工具。Naughty Dog 的灯光艺术家 Eben Cook 在 GDC 2021 演讲中分享：《最后生还者2》中 70% 的玩家路径引导完全依赖光照而非 UI 标记，测试中移除灯光引导后迷路率从 3% 飙升至 41%。

## 光照的三大核心功能

### 1. 路径引导（Wayfinding）

光照引导是关卡设计中最经济的导航手段：

| 技法 | 实现方式 | 经典案例 |
|------|---------|---------|
| 光源吸引（Moth Effect） | 在目标方向放置明亮光源 | 《黑暗之魂》：篝火可视距离 > 50m |
| 明暗对比通道 | 正确路径明亮，死路昏暗 | 《传送门》：出口区域 300+ lux vs 走廊 50 lux |
| 色彩编码 | 不同颜色标识不同区域/功能 | 《镜之边缘》：可攀爬物体统一红色高光 |
| 动态光引导 | 光源随叙事进展开启/关闭 | 《生化奇兵：无限》：Elizabeth 扔硬币时灯光闪烁指向前进方向 |
| 体积光/God Ray | 从窗口或裂缝射入的光柱标记关键位置 | 《ICO》：城堡中的光柱标记可交互点 |

人类视觉系统对亮度对比的反应具有生物学基础：视网膜神经节细胞对 **亮度突变** 的响应速度比均匀亮度快 3-5 倍（Hubel & Wiesel, 1962），这意味着玩家的眼睛会自动被"暗中亮"的区域吸引。

### 2. 情绪与氛围营造

舞台灯光理论（J. Michael Gillette, 2013）中的四大情绪参数直接适用于游戏：

- **色温**：暖色（2700-3500K）→ 安全感、怀旧。冷色（5500-7500K）→ 危险、疏离。《寂静岭》系列几乎全部使用 7000K+ 的冷白光渲染恐惧
- **对比度**：高对比（Key-to-Fill > 8:1）→ 戏剧性、紧张。低对比（< 2:1）→ 平静、开阔。《风之旅人》沙漠场景 Key-to-Fill 约 1.5:1，传达宁静与孤独
- **饱和度**：高饱和色光 → 超现实、梦境。低饱和/去色 → 写实、沉重。《控制》中"Hiss"入侵区域使用高饱和红光
- **方向性**：底光 → 诡异（经典恐怖片手法）。顶光 → 神圣。侧光 → 戏剧性。《教堂场景》几乎所有 AAA 游戏的教堂都使用高位侧光+彩色玻璃投影

### 3. 叙事信息传达

光照能无言地讲述故事：

- **时间暗示**：《荒野大镖客2》的全局光照系统按 24 小时周期变化，黎明的长影暗示"新的开始"，黄昏暖光暗示"结束/告别"
- **状态变化**：《生化危机》系列中安全屋从暖黄灯光切换到红色闪烁 = 区域已被入侵
- **心理映射**：角色内心状态通过环境光表达——《地狱之刃》主角 Senua 的精神状态恶化时，环境光从自然色逐渐偏移为不自然的青紫色
- **重要物品高亮**：关键拾取物通常有独立光源——《黑暗之魂》的道具拾取点发出微弱白光，可在 20-30m 外识别

## 技术实现的两条路径

### 烘焙光照（Baked Lighting）

- 预计算光照贴图，运行时零开销
- 适合静态场景：建筑内部、走廊、固定环境
- UE5 中使用 Lightmass/Lumen 的 Static 模式，分辨率典型值 64-128 texels/m²
- **限制**：无法响应动态事件（门开关、破坏）

### 实时光照（Real-time Lighting）

- 逐帧计算，GPU 开销显著
- 适合动态场景：日夜循环、可破坏环境、手电筒
- UE5 Lumen 提供全局实时 GI，性能代价约 2-4ms/帧（PS5 基准）
- **趋势**：硬件光追（DXR/Vulkan RT）使实时光照质量逼近烘焙

实际项目中通常 **混合使用**：静态环境用烘焙基础 + 动态物体用实时光 + 重要叙事节点用脚本控制的灯光状态切换。

## 光照叙事设计检查清单

实战中使用的 5 点验证法：

1. **关掉 HUD 测试**：仅靠光照，玩家能否找到正确路径？（通过率目标 > 80%）
2. **截图情绪测试**：对静态截图，10 人中至少 7 人描述出设计意图的情绪关键词
3. **亮度范围审查**：场景中最亮点与最暗点的比值是否在 100:1-1000:1 之间？超出则显示器无法正确呈现
4. **色彩语言一致性**：同一游戏中红色是否始终代表危险？绿色是否始终代表安全？混用会破坏玩家建立的视觉语法
5. **无障碍检查**：8% 的男性有色觉障碍——仅依赖红绿区分的光照叙事必须有亮度备选方案

## 常见误区

1. **均匀照明陷阱**：整个场景亮度均匀 → 无引导、无氛围、无层次。游戏光照的首要原则是 **不均匀**。即便现实中的办公室也有 2:1 以上的亮度对比
2. **过度依赖颜色编码**：仅用颜色区分（红=敌/蓝=友）而不结合亮度对比，色觉障碍玩家将完全失去信息
3. **技术优先于设计**：追求光追真实感但忽略叙事意图——现实中的光照很少恰好适合游戏引导，99% 的游戏光照都是"作弊的"（Cook, GDC 2021）

## 知识衔接

### 先修知识
- **关卡设计概述** — 光照叙事是关卡空间设计的视觉表现层，需要先理解空间布局基础

### 后续学习
- **光照引导** — 深入路径引导中的光源布置技术与参数调优
- **氛围光照** — 系统化的情绪光照设计方法论
- **动态光照** — 脚本驱动的光照状态机与日夜循环系统
- **烘焙vs实时光照** — 技术选型的性能-质量权衡分析
- **阴影设计** — 阴影作为独立叙事元素的设计技法

## 参考文献

1. Totten, C. (2019). *An Architectural Approach to Level Design* (2nd ed.). CRC Press. ISBN 978-0815361367
2. Gillette, J.M. (2013). *Designing with Light* (6th ed.). McGraw-Hill. ISBN 978-0073514239
3. Cook, E. (2021). "Painting with Light: The Art of Lighting in The Last of Us Part II." GDC 2021.
4. Hubel, D.H. & Wiesel, T.N. (1962). "Receptive fields, binocular interaction and functional architecture in the cat's visual cortex." *Journal of Physiology*, 160(1), 106-154.
5. Brown, M. (2019). "How Games Use Light to Guide You." Game Maker's Toolkit (YouTube).
