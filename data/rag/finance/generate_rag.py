#!/usr/bin/env python3
"""Generate RAG teaching documents for Finance knowledge sphere.

Creates one markdown file per concept in data/rag/finance/{subdomain}/{concept}.md
"""
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SEED_PATH = SCRIPT_DIR.parent.parent / "seed" / "finance" / "seed_graph.json"

# Templates for finance RAG documents by subdomain
SUBDOMAIN_TEMPLATES = {
    "personal-finance": """---
concept: {name}
subdomain: {subdomain_name}
domain: finance
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

个人理财是每个人都应掌握的基本技能。通过科学的财务规划，我们能够更好地管理收入支出、积累财富并实现财务目标。

## 关键要点

### 基础原则
- **量入为出**: 支出永远不超过收入，建立健康的现金流
- **优先自己**: 先储蓄再消费（Pay Yourself First）
- **长期视角**: 利用复利的时间价值，越早开始越好

### 实践指南
- 建立并坚持预算系统，定期审视支出结构
- 维持3-6个月的应急储备金
- 合理利用税收优惠，优化税后收入

## 常见误区

1. **忽视小额消费**: 拿铁因子效应——日常小额消费长期累积影响巨大
2. **过度储蓄不投资**: 现金在通胀下持续贬值，需要合理投资
3. **盲目跟风理财**: 不了解产品就投入，忽视自身风险承受能力

## 与相关概念的联系

{name}是个人理财知识体系的重要组成部分。掌握这一概念有助于建立健全的财务基础，为更高阶的投资决策做好准备。
""",

    "investment-basics": """---
concept: {name}
subdomain: {subdomain_name}
domain: finance
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

投资是实现财富增值的核心手段。理解投资的基本原理，包括风险收益关系、资产配置和市场运作机制，是成为成功投资者的第一步。

## 关键要点

### 理论基础
- **风险与收益的权衡**: 高收益伴随高风险，没有免费的午餐
- **分散化投资**: 不把鸡蛋放在一个篮子里，降低非系统性风险
- **时间价值**: $1今天的价值大于$1未来的价值

### 投资原则
- 明确投资目标和风险承受能力后再行动
- 理解所投资产品的底层逻辑
- 定期审视和再平衡投资组合

## 常见误区

1. **追涨杀跌**: 被市场情绪左右，在高点买入低点卖出
2. **忽视费用**: 长期投资中管理费和交易成本对收益的侵蚀显著
3. **过度交易**: 频繁买卖不仅增加成本，还容易做出情绪化决策

## 与相关概念的联系

{name}属于投资基础知识的核心内容。它为理解更复杂的投资策略和金融产品奠定了理论基础。
""",

    "stock-market": """---
concept: {name}
subdomain: {subdomain_name}
domain: finance
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

股票市场是资本市场的重要组成部分，也是普通投资者接触最多的投资渠道。掌握股票分析的方法，有助于做出更理性的投资决策。

## 关键要点

### 分析方法
- **基本面分析**: 通过财务数据评估公司内在价值
- **技术分析**: 通过价格和成交量模式判断市场趋势
- **量化分析**: 使用数学模型系统性筛选投资标的

### 实操要点
- 建立明确的买入和卖出纪律
- 持续跟踪公司基本面变化
- 保持投资组合的合理集中度

## 常见误区

1. **只看股价不看估值**: 低价股不等于便宜，高价股不等于昂贵
2. **忽视安全边际**: 即使是好公司，买入价格过高也会亏损
3. **频繁调仓**: 交易越多不代表收益越高，经常适得其反

## 与相关概念的联系

{name}是股票市场分析体系的重要组成部分。理解这一概念有助于构建完整的投资分析框架。
""",

    "fixed-income": """---
concept: {name}
subdomain: {subdomain_name}
domain: finance
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

固定收益证券是资产配置中不可或缺的组成部分。债券提供了相对稳定的现金流和较低的波动率，是对冲权益市场风险的重要工具。

## 关键要点

### 核心原理
- **债券价格与收益率反向变动**: 利率上升→债券价格下降
- **信用风险定价**: 信用评级越低，要求的风险溢价越高
- **久期风险**: 期限越长，对利率变动越敏感

### 投资考量
- 关注收益率曲线的形态和变化趋势
- 分散信用风险，避免集中于单一发行人
- 根据利率预期调整久期暴露

## 常见误区

1. **认为债券无风险**: 债券同样面临利率风险、信用风险和流动性风险
2. **只关注票息**: 忽视债券价格波动对总回报的影响
3. **忽视通胀**: 固定票息在高通胀环境下实际购买力下降

## 与相关概念的联系

{name}是固定收益投资知识的关键内容。理解这一概念有助于在资产配置中合理运用债券类资产。
""",

    "corporate-finance": """---
concept: {name}
subdomain: {subdomain_name}
domain: finance
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

公司金融关注企业如何做出最优的投资、融资和分配决策，以最大化股东价值。这些原理也是估值分析和财务管理的理论基础。

## 关键要点

### 核心框架
- **NPV法则**: 接受所有净现值为正的投资项目
- **资本结构权衡**: 债务的税盾收益vs财务困境成本
- **代理问题**: 管理层与股东利益的对齐机制

### 决策要点
- 使用加权平均资本成本（WACC）作为项目折现率
- 区分沉没成本和机会成本
- 考虑项目的战略价值和实物期权

## 常见误区

1. **IRR陷阱**: 多重IRR和互斥项目排序中IRR可能误导
2. **忽视资本成本**: 使用不当的折现率导致投资决策偏差
3. **过度杠杆**: 追求税盾收益而忽视财务困境风险

## 与相关概念的联系

{name}是公司金融体系的核心内容。掌握这些概念对于企业财务分析和投资银行业务至关重要。
""",

    "risk-management": """---
concept: {name}
subdomain: {subdomain_name}
domain: finance
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

风险管理是金融行业的核心职能。有效识别、度量和管理各类风险，是维持金融系统稳定和保护投资者利益的关键。

## 关键要点

### 风险度量
- **VaR（在险价值）**: 在给定置信水平下的最大预期损失
- **压力测试**: 极端情景下的组合表现评估
- **希腊字母**: 衍生品各维度风险的精确度量

### 管理策略
- 通过衍生品对冲特定风险敞口
- 设定风险限额和止损纪律
- 建立风险监控和预警系统

## 常见误区

1. **混淆风险与不确定性**: 可量化的是风险，不可量化的是不确定性
2. **尾部风险忽视**: 黑天鹅事件发生概率低但影响巨大
3. **过度对冲**: 对冲成本可能侵蚀大部分预期收益

## 与相关概念的联系

{name}是金融风险管理框架的重要组成部分。理解风险管理工具和方法对于任何金融从业者都是必备技能。
""",

    "fintech": """---
concept: {name}
subdomain: {subdomain_name}
domain: finance
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

金融科技正在重塑传统金融行业的每个环节。从支付到借贷，从投资到保险，技术创新正在提升金融服务的效率、可及性和用户体验。

## 关键要点

### 技术驱动
- **区块链与分布式账本**: 实现去中心化的信任和价值传递
- **人工智能**: 智能投顾、风控模型、自然语言处理
- **大数据**: 精准营销、信用评估、欺诈检测

### 行业趋势
- 从牌照壁垒到技术壁垒的竞争范式转变
- 嵌入式金融：金融服务嵌入非金融场景
- 监管科技（RegTech）助力合规自动化

## 常见误区

1. **技术万能论**: 技术只是工具，金融的本质是风险管理
2. **忽视合规**: 金融创新必须在监管框架内进行
3. **过度去中心化**: 完全去中心化可能牺牲效率和用户保护

## 与相关概念的联系

{name}是金融科技知识体系的重要内容。了解金融科技的发展趋势有助于把握行业未来方向。
""",

    "quantitative-finance": """---
concept: {name}
subdomain: {subdomain_name}
domain: finance
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

量化金融将数学、统计学和计算机科学应用于金融市场。通过系统性的量化方法，可以发现市场中的定价异常并构建自动化交易策略。

## 关键要点

### 理论基础
- **因子投资**: 通过风险因子暴露获取超额收益
- **统计推断**: 区分真实信号和随机噪声
- **随机过程**: 资产价格的数学建模

### 实践要点
- 样本外验证防止过拟合
- 交易成本和滑点对策略的真实影响
- 组合构建中的约束优化

## 常见误区

1. **回测过拟合**: 在历史数据上表现优异不代表未来有效
2. **忽视市场冲击**: 策略容量受限于流动性和市场冲击
3. **黑盒交易**: 不理解模型假设就盲目使用

## 与相关概念的联系

{name}是量化金融体系的关键组成部分。掌握量化方法有助于以更科学的方式进行投资决策和风险管理。
""",
}

# Generic fallback template
GENERIC_TEMPLATE = """---
concept: {name}
subdomain: {subdomain_name}
domain: finance
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

## 关键要点

### 基础知识
- 理解核心定义和基本原理
- 掌握主要的分析方法和工具
- 了解实际应用场景和局限性

### 进阶思考
- 与其他金融概念的关联关系
- 在不同市场环境下的适用性
- 历史案例的经验教训

## 常见误区

1. 概念理解片面，忽视前提假设
2. 理论与实践脱节，忽视市场摩擦
3. 过度简化，忽视尾部风险

## 与相关概念的联系

{name}是金融理财知识体系的有机组成部分。深入理解这一概念有助于构建更完整的金融知识框架。
"""


def generate_rag_docs():
    """Generate RAG documents for all finance concepts."""
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        seed = json.load(f)

    sub_map = {s["id"]: s["name"] for s in seed["subdomains"]}

    created = 0
    for concept in seed["concepts"]:
        sub_id = concept["subdomain_id"]
        sub_name = sub_map[sub_id]

        # Pick template
        template = SUBDOMAIN_TEMPLATES.get(sub_id, GENERIC_TEMPLATE)
        content = template.format(
            name=concept["name"],
            description=concept["description"],
            subdomain_name=sub_name,
            difficulty=concept["difficulty"],
        )

        # Ensure subdomain directory exists
        sub_dir = SCRIPT_DIR / sub_id
        sub_dir.mkdir(parents=True, exist_ok=True)

        # Write markdown file
        file_path = sub_dir / f"{concept['id']}.md"
        file_path.write_text(content, encoding="utf-8")
        created += 1

    print(f"Generated {created} RAG documents across {len(sub_map)} subdomains")

    # Generate _index.json
    documents = []
    for concept in seed["concepts"]:
        sub_id = concept["subdomain_id"]
        sub_name = sub_map[sub_id]
        file_rel = f"finance/{sub_id}/{concept['id']}.md"
        file_abs = SCRIPT_DIR / sub_id / f"{concept['id']}.md"
        char_count = len(file_abs.read_text(encoding="utf-8"))
        documents.append({
            "id": concept["id"],
            "name": concept["name"],
            "domain_id": "finance",
            "subdomain_id": sub_id,
            "subdomain_name": sub_name,
            "difficulty": concept["difficulty"],
            "is_milestone": concept.get("is_milestone", False),
            "tags": concept.get("tags", []),
            "file": file_rel,
            "exists": True,
            "char_count": char_count,
        })

    index = {
        "documents": documents,
        "stats": {
            "total_docs": len(documents),
            "total_chars": sum(d["char_count"] for d in documents),
            "by_subdomain": {},
        },
    }
    from collections import Counter
    sub_counts = Counter(c["subdomain_id"] for c in seed["concepts"])
    for s in seed["subdomains"]:
        index["stats"]["by_subdomain"][s["id"]] = sub_counts[s["id"]]

    index_path = SCRIPT_DIR / "_index.json"
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Generated _index.json with {len(documents)} entries")

    # Print stats per subdomain
    for s in seed["subdomains"]:
        print(f"  {s['name']}: {sub_counts[s['id']]} docs")


if __name__ == "__main__":
    generate_rag_docs()
