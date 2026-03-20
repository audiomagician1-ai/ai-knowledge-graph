#!/usr/bin/env python3
"""Generate RAG teaching documents for Economics knowledge sphere.

Creates one markdown file per concept in data/rag/economics/{subdomain}/{concept}.md
"""
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SEED_PATH = SCRIPT_DIR.parent.parent / "seed" / "economics" / "seed_graph.json"

SUBDOMAIN_TEMPLATES = {
    "microeconomics": """---
concept: {name}
subdomain: {subdomain_name}
domain: economics
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

微观经济学研究个体经济单位（消费者、企业、市场）的决策行为和资源配置。理解供需、弹性、市场结构等基本概念是分析经济现象的起点。

## 关键要点

### 市场机制
- **供给与需求**: 价格由供需交互决定，均衡价格使市场出清
- **弹性分析**: 衡量经济变量之间的敏感程度（价格弹性、收入弹性、交叉弹性）
- **消费者选择**: 在预算约束下最大化效用，无差异曲线与预算线的切点为最优

### 市场结构
- 完全竞争→垄断竞争→寡头→垄断：市场力量递增，效率递减
- 博弈论分析策略互动：纳什均衡、囚徒困境、重复博弈
- 市场失灵需要政府干预：外部性、公共品、信息不对称

## 常见误区

1. **价格只由成本决定**: 价格由供需共同决定，成本只影响供给侧
2. **垄断一定低效**: 自然垄断可能比竞争更有效率（如公用事业）
3. **理性人假设=自私**: 理性指偏好一致性和最优化行为，不等于自私

## 与相关概念的联系

{name}是微观经济学知识体系的重要组成部分。掌握这一概念有助于理解市场运行机制和资源配置效率。
""",

    "macroeconomics": """---
concept: {name}
subdomain: {subdomain_name}
domain: economics
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

宏观经济学研究经济体整体运行规律，关注GDP、通胀、失业、经济增长等总量指标，以及财政政策和货币政策的效果。

## 关键要点

### 总量分析框架
- **GDP核算**: 支出法（C+I+G+NX）、收入法、生产法三种等价视角
- **总供给-总需求模型**: 短期与长期的区别，价格粘性的重要性
- **经济波动**: 商业周期（扩张→顶峰→衰退→谷底）的原因和应对

### 政策工具
- 财政政策：政府支出和税收调节总需求，乘数效应与挤出效应
- 货币政策：央行通过利率和货币供给影响经济，泰勒规则
- 供给侧政策：结构性改革、减税激励投资和创新

## 常见误区

1. **GDP越高越好**: GDP不衡量福利、不平等、环境成本等
2. **通胀一定有害**: 温和通胀（2%目标）有利于经济运行，通缩可能更危险
3. **政府债务=家庭债务**: 政府可以发行货币且永续存在，与家庭本质不同

## 与相关概念的联系

{name}是宏观经济学知识体系的重要组成部分。掌握这一概念有助于理解经济运行的整体规律和政策效果。
""",

    "behavioral-econ": """---
concept: {name}
subdomain: {subdomain_name}
domain: economics
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

行为经济学结合心理学研究发现人类实际决策偏离理性假设的系统性方式。前景理论、认知偏差和有限理性是理解真实经济行为的关键。

## 关键要点

### 决策偏差
- **前景理论**: 人们对损失比收益更敏感（损失厌恶），且参考点依赖
- **框架效应**: 同一问题的不同表述方式会改变人们的选择
- **启发式**: 人们使用简化规则（可得性、代表性、锚定）做决策，导致系统性偏差

### 行为干预
- **助推**: 设计选择架构引导更好的决策（默认选项、简化选择）
- **心理账户**: 人们在心理上将金钱分账管理，违反可替代性原则
- **时间偏好**: 现在偏差导致过度消费和储蓄不足

## 常见误区

1. **行为经济学否定理性**: 它补充而非替代传统理论，指出理性的边界条件
2. **偏差意味着愚蠢**: 启发式在大多数情况下是高效的决策策略
3. **助推是操纵**: 好的助推保留选择自由，增强决策质量

## 与相关概念的联系

{name}是行为经济学知识体系的重要组成部分。掌握这一概念有助于理解真实人类决策的心理机制。
""",

    "international-econ": """---
concept: {name}
subdomain: {subdomain_name}
domain: economics
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

国际经济学研究国家间的贸易、投资和货币关系。比较优势理论、贸易政策和汇率制度是分析全球经济的基本框架。

## 关键要点

### 贸易理论
- **比较优势**: 即使一国在所有商品上都有绝对劣势，仍可通过贸易获益
- **赫克歇尔-俄林模型**: 贸易模式取决于要素禀赋差异
- **新贸易理论**: 规模经济和产品差异化解释产业内贸易

### 国际金融
- 汇率制度：固定vs浮动vs中间制度，蒙代尔不可能三角
- 国际收支：经常账户+资本与金融账户=0的恒等式
- 货币危机：投机攻击、自我实现预期、传染效应

## 常见误区

1. **贸易是零和博弈**: 贸易创造互利的专业化收益，但分配效应确实存在
2. **贸易逆差=输家**: 美国长期贸易逆差反映了资本流入和消费偏好
3. **汇率贬值一定有害**: 贬值可以提高出口竞争力，各有利弊

## 与相关概念的联系

{name}是国际经济学知识体系的重要组成部分。掌握这一概念有助于理解全球经济的互联互通。
""",

    "development-econ": """---
concept: {name}
subdomain: {subdomain_name}
domain: economics
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

发展经济学研究发展中国家如何实现经济增长和减少贫困。制度、人力资本、结构转型和外部援助是分析发展问题的核心视角。

## 关键要点

### 发展挑战
- **贫困陷阱**: 低储蓄→低投资→低增长→低储蓄的恶性循环
- **制度因素**: 产权保护、法治和治理质量对发展至关重要（Acemoglu & Robinson）
- **结构转型**: 从农业到制造业到服务业的经济结构演进

### 政策与实践
- 人力资本投资（教育、健康）的长期回报
- 随机对照实验（RCT）革新了发展政策评估（Banerjee & Duflo）
- 微型金融（Grameen Bank）为穷人提供金融服务

## 常见误区

1. **经济增长自动减贫**: 增长的分配效应决定减贫效果
2. **发展=工业化**: 服务业跨越式发展（如印度IT）提供另一条道路
3. **外援一定有效**: 援助有效性取决于受援国制度环境（Easterly vs Sachs之争）

## 与相关概念的联系

{name}是发展经济学知识体系的重要组成部分。掌握这一概念有助于理解全球不平等和发展路径。
""",

    "econometrics": """---
concept: {name}
subdomain: {subdomain_name}
domain: economics
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

计量经济学将统计学方法应用于经济数据分析。回归分析、因果推断和时间序列是现代经济学实证研究的核心工具。

## 关键要点

### 核心方法
- **回归分析**: OLS（最小二乘法）估计变量间的线性关系
- **因果推断**: 工具变量、双重差分、断点回归识别因果效应
- **面板数据**: 结合截面和时间维度，控制不可观测的个体异质性

### 方法论挑战
- 内生性：遗漏变量、反向因果、测量误差导致估计偏误
- 异方差和自相关：违反OLS经典假设需要修正
- 大数据时代：机器学习方法进入经济学（LASSO、随机森林）

## 常见误区

1. **相关=因果**: 没有适当的识别策略，回归系数不能解释为因果效应
2. **显著=重要**: 统计显著性不等于经济显著性，需关注效应大小
3. **更多控制变量更好**: 过度控制可能引入坏控制变量偏误

## 与相关概念的联系

{name}是计量经济学知识体系的重要组成部分。掌握这一概念有助于进行严谨的经济学实证研究。
""",

    "public-econ": """---
concept: {name}
subdomain: {subdomain_name}
domain: economics
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

公共经济学研究政府在经济中的角色，包括税收、公共支出、社会保障和环境政策。市场失灵与政府失灵的权衡是核心议题。

## 关键要点

### 政府角色
- **公共品提供**: 非竞争性和非排他性的物品（国防、基础研究）市场无法有效供给
- **外部性矫正**: 庇古税/补贴或可交易许可证内化外部效应
- **收入再分配**: 税收和转移支付体系实现社会公平目标

### 税收分析
- 税收原则：效率（最小化超额负担）与公平（能力原则vs受益原则）
- 税收归宿：法定纳税人和实际承担者可能不同（取决于供需弹性）
- 最优税收：Ramsey规则（反弹性法则）与Mirrlees最优所得税

## 常见误区

1. **政府干预总是改善市场**: 政府也会失灵（信息不对称、寻租、官僚效率低）
2. **税收越低越好**: 拉弗曲线有最优税率点，过低的税率无法提供必要公共品
3. **公共品只能政府提供**: Coase定理表明私人协商在某些条件下可解决外部性

## 与相关概念的联系

{name}是公共经济学知识体系的重要组成部分。掌握这一概念有助于理解政府经济政策的设计和效果。
""",

    "economic-thought": """---
concept: {name}
subdomain: {subdomain_name}
domain: economics
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

经济思想史追溯经济学理论的演进，从古典政治经济学到现代学派之争。理解思想史有助于把握理论的局限性和适用条件。

## 关键要点

### 重大理论转向
- **古典经济学**: 亚当·斯密（看不见的手）→李嘉图（比较优势）→马克思（剩余价值）
- **边际革命**: 1870s 三位先驱（杰文斯、门格尔、瓦尔拉斯）用边际分析取代古典价值论
- **凯恩斯革命**: 1930s 大萧条催生宏观经济学，总需求管理成为政策主流

### 现代学派
- 货币主义（弗里德曼）vs 凯恩斯主义：货币政策vs财政政策的优先性
- 奥地利学派：强调自发秩序、知识分散和创业精神
- 制度经济学：制度是理解经济绩效的关键（诺斯、科斯、威廉姆森）

## 常见误区

1. **亚当·斯密只主张自由放任**: 斯密也强调政府在国防、司法和公共工程中的角色
2. **凯恩斯主张无限制财政扩张**: 凯恩斯主张反周期政策，繁荣期应紧缩
3. **马克思只是革命家**: 马克思对资本积累和商业周期的分析具有重要学术价值

## 与相关概念的联系

{name}是经济思想史知识体系的重要组成部分。掌握这一概念有助于理解经济学理论的演进脉络和当代争论。
""",
}

SUBDOMAIN_NAMES = {
    "microeconomics": "微观经济学",
    "macroeconomics": "宏观经济学",
    "behavioral-econ": "行为经济学",
    "international-econ": "国际经济学",
    "development-econ": "发展经济学",
    "econometrics": "计量经济学",
    "public-econ": "公共经济学",
    "economic-thought": "经济思想史",
}


def main():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        seed = json.load(f)

    concepts = seed["concepts"]
    documents = []
    by_subdomain = {}
    total_chars = 0
    total = 0

    for c in concepts:
        subdomain = c["subdomain_id"]
        subdomain_name = SUBDOMAIN_NAMES.get(subdomain, subdomain)

        # Ensure subdomain directory exists
        sub_dir = SCRIPT_DIR / subdomain
        sub_dir.mkdir(parents=True, exist_ok=True)

        template = SUBDOMAIN_TEMPLATES.get(subdomain, SUBDOMAIN_TEMPLATES["microeconomics"])
        content = template.format(
            name=c["name"],
            description=c["description"],
            subdomain_name=subdomain_name,
            difficulty=c["difficulty"],
        ).strip() + "\n"

        filepath = sub_dir / f"{c['id']}.md"
        filepath.write_text(content, encoding="utf-8")

        char_count = len(content)
        documents.append({
            "id": c["id"],
            "name": c["name"],
            "domain_id": "economics",
            "subdomain_id": subdomain,
            "subdomain_name": subdomain_name,
            "difficulty": c["difficulty"],
            "is_milestone": c.get("is_milestone", False),
            "tags": c.get("tags", []),
            "file": f"economics/{subdomain}/{c['id']}.md",
            "exists": True,
            "char_count": char_count,
        })

        by_subdomain[subdomain] = by_subdomain.get(subdomain, 0) + 1
        total_chars += char_count
        total += 1

    # Write index in standard format
    index_path = SCRIPT_DIR / "_index.json"
    index_data = {
        "documents": documents,
        "stats": {
            "total_docs": total,
            "total_chars": total_chars,
            "by_subdomain": by_subdomain,
        },
    }
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"✅ Generated {total} economics RAG documents")
    print(f"   Index: {index_path}")
    for sub_id, sub_name in SUBDOMAIN_NAMES.items():
        count = sum(1 for c in concepts if c["subdomain_id"] == sub_id)
        print(f"   {sub_id}: {count} docs")


if __name__ == "__main__":
    main()
