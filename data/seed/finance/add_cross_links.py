#!/usr/bin/env python3
"""Add finance cross-sphere links to cross_sphere_links.json"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent.parent
CROSS_LINKS_PATH = ROOT / "data" / "seed" / "cross_sphere_links.json"

NEW_LINKS = [
    # finance ↔ mathematics (5 links)
    {
        "source_domain": "finance", "source_id": "compound-interest",
        "target_domain": "mathematics", "target_id": "exponential-functions",
        "relation": "applies", "description": "复利公式是指数函数在金融中的核心应用"
    },
    {
        "source_domain": "finance", "source_id": "portfolio-theory",
        "target_domain": "mathematics", "target_id": "descriptive-statistics",
        "relation": "applies", "description": "投资组合理论依赖方差、协方差等统计概念进行风险度量"
    },
    {
        "source_domain": "finance", "source_id": "time-value-of-money",
        "target_domain": "mathematics", "target_id": "geometric-sequence",
        "relation": "applies", "description": "货币时间价值的折现计算基于等比数列求和公式"
    },
    {
        "source_domain": "finance", "source_id": "black-scholes-model",
        "target_domain": "mathematics", "target_id": "conditional-probability",
        "relation": "applies", "description": "Black-Scholes期权定价模型建立在概率论和随机过程基础上"
    },
    {
        "source_domain": "finance", "source_id": "portfolio-optimization",
        "target_domain": "mathematics", "target_id": "convex-optimization",
        "relation": "applies", "description": "投资组合优化本质是凸优化问题"
    },

    # finance ↔ ai-engineering (4 links)
    {
        "source_domain": "finance", "source_id": "machine-learning-finance",
        "target_domain": "ai-engineering", "target_id": "deep-learning-intro",
        "relation": "applies", "description": "深度学习在量化金融中的alpha生成和风控建模"
    },
    {
        "source_domain": "finance", "source_id": "sentiment-analysis-finance",
        "target_domain": "ai-engineering", "target_id": "linear-regression",
        "relation": "applies", "description": "金融情绪分析利用NLP和回归技术从新闻文本提取交易信号"
    },
    {
        "source_domain": "finance", "source_id": "algorithmic-trading",
        "target_domain": "ai-engineering", "target_id": "kmp-algorithm",
        "relation": "related", "description": "算法交易需要高效的数据结构和算法知识来处理实时市场数据"
    },
    {
        "source_domain": "finance", "source_id": "blockchain-basics",
        "target_domain": "ai-engineering", "target_id": "token-economics",
        "relation": "related", "description": "区块链技术中的代币经济学连接了金融理论和分布式系统"
    },

    # finance ↔ physics (2 links)
    {
        "source_domain": "finance", "source_id": "stochastic-calculus",
        "target_domain": "physics", "target_id": "statistical-mechanics",
        "relation": "related", "description": "金融随机微积分与统计力学共享布朗运动和随机过程的数学基础"
    },
    {
        "source_domain": "finance", "source_id": "systemic-risk",
        "target_domain": "physics", "target_id": "entropy",
        "relation": "related", "description": "系统性风险的传导机制与热力学熵增的不可逆性有类比关系"
    },

    # finance ↔ english (2 links)
    {
        "source_domain": "finance", "source_id": "financial-modeling",
        "target_domain": "english", "target_id": "business-vocabulary",
        "relation": "related", "description": "财务建模需要大量英文商业术语（EBITDA、DCF、IRR等）"
    },
    {
        "source_domain": "finance", "source_id": "ipo-process",
        "target_domain": "english", "target_id": "compound-sentences",
        "relation": "related", "description": "IPO招股书和财务报告需要复杂英文句式的阅读理解能力"
    },

    # finance ↔ product-design (2 links)
    {
        "source_domain": "finance", "source_id": "behavioral-finance",
        "target_domain": "product-design", "target_id": "behavioral-economics",
        "relation": "related", "description": "行为金融学与产品设计中的行为经济学共享非理性决策理论基础"
    },
    {
        "source_domain": "finance", "source_id": "robo-advisor",
        "target_domain": "product-design", "target_id": "data-driven-overview",
        "relation": "related", "description": "智能投顾产品设计需要数据驱动的用户体验和交互设计"
    },
]


def main():
    # Load all domain IDs for validation
    domains = {}
    for d in ["ai-engineering", "mathematics", "english", "physics", "product-design", "finance"]:
        seed_path = ROOT / "data" / "seed" / d / "seed_graph.json"
        with open(seed_path, "r", encoding="utf-8") as f:
            seed = json.load(f)
        domains[d] = {c["id"] for c in seed["concepts"]}

    # Validate
    for link in NEW_LINKS:
        sd, si = link["source_domain"], link["source_id"]
        td, ti = link["target_domain"], link["target_id"]
        assert si in domains[sd], f"Missing source: {sd}/{si}"
        assert ti in domains[td], f"Missing target: {td}/{ti}"

    print(f"All {len(NEW_LINKS)} new links validated OK")

    # Load existing
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    old_count = len(data["links"])
    data["links"].extend(NEW_LINKS)
    print(f"Links: {old_count} → {len(data['links'])}")

    with open(CROSS_LINKS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Written successfully")


if __name__ == "__main__":
    main()
