#!/usr/bin/env python3
"""Add cross-sphere links connecting psychology to other domains."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
CROSS_LINKS_PATH = os.path.join(ROOT, "data", "seed", "cross_sphere_links.json")

NEW_LINKS = [
    # psychology → ai-engineering (cognition ↔ AI)
    {
        "source_domain": "psychology",
        "source_id": "cognitive-biases",
        "target_domain": "ai-engineering",
        "target_id": "prompt-basics",
        "relation": "related",
        "description": "认知偏差理解有助于设计更有效的AI提示词，避免偏差放大"
    },
    {
        "source_domain": "psychology",
        "source_id": "decision-making",
        "target_domain": "ai-engineering",
        "target_id": "reinforcement-learning",
        "relation": "related",
        "description": "人类决策过程为强化学习的奖励函数设计提供心理学基础"
    },
    {
        "source_domain": "psychology",
        "source_id": "working-memory",
        "target_domain": "ai-engineering",
        "target_id": "attention-mechanism",
        "relation": "related",
        "description": "注意力机制的设计灵感部分来自人类工作记忆的注意力分配"
    },

    # psychology → mathematics (statistics & research methods)
    {
        "source_domain": "psychology",
        "source_id": "descriptive-statistics",
        "target_domain": "mathematics",
        "target_id": "descriptive-statistics",
        "relation": "same_concept",
        "description": "描述统计在心理学与数学中是完全相同的概念"
    },
    {
        "source_domain": "psychology",
        "source_id": "inferential-statistics",
        "target_domain": "mathematics",
        "target_id": "hypothesis-testing",
        "relation": "related",
        "description": "心理学的推断统计大量使用数学假设检验方法"
    },
    {
        "source_domain": "psychology",
        "source_id": "correlational-research",
        "target_domain": "mathematics",
        "target_id": "correlation",
        "relation": "requires",
        "description": "心理学相关研究需要数学中相关系数的计算和解释能力"
    },

    # psychology → english (language & cognition)
    {
        "source_domain": "psychology",
        "source_id": "language-cognition",
        "target_domain": "english",
        "target_id": "grammar-in-context",
        "relation": "related",
        "description": "语言认知研究为理解语法习得和语言加工提供理论基础"
    },
    {
        "source_domain": "psychology",
        "source_id": "language-development",
        "target_domain": "english",
        "target_id": "vowel-sounds",
        "relation": "related",
        "description": "语言发展心理学解释了语音习得的敏感期和学习机制"
    },

    # psychology → product-design (UX & behavioral design)
    {
        "source_domain": "psychology",
        "source_id": "persuasion",
        "target_domain": "product-design",
        "target_id": "growth-overview",
        "relation": "enables",
        "description": "说服心理学原理是产品增长策略和用户转化的理论基础"
    },
    {
        "source_domain": "psychology",
        "source_id": "cognitive-load",
        "target_domain": "product-design",
        "target_id": "interaction-design-overview",
        "relation": "enables",
        "description": "认知负荷理论指导交互设计降低用户认知负担"
    },
    {
        "source_domain": "psychology",
        "source_id": "maslow-hierarchy",
        "target_domain": "product-design",
        "target_id": "user-research-overview",
        "relation": "related",
        "description": "马斯洛需求层次为用户需求分析提供经典心理学框架"
    },

    # psychology → finance (behavioral finance)
    {
        "source_domain": "psychology",
        "source_id": "cognitive-biases",
        "target_domain": "finance",
        "target_id": "behavioral-finance",
        "relation": "enables",
        "description": "认知偏差是行为金融学的核心理论基础"
    },
    {
        "source_domain": "psychology",
        "source_id": "heuristics",
        "target_domain": "finance",
        "target_id": "investment-psychology",
        "relation": "enables",
        "description": "启发式思维解释了投资者为何做出非理性决策"
    },

    # psychology → physics (perception & neuroscience)
    {
        "source_domain": "psychology",
        "source_id": "neuron-structure",
        "target_domain": "physics",
        "target_id": "electric-potential",
        "relation": "related",
        "description": "神经元的动作电位基于物理学的电流和电压原理"
    },
    {
        "source_domain": "psychology",
        "source_id": "brain-imaging",
        "target_domain": "physics",
        "target_id": "electromagnetic-waves",
        "relation": "related",
        "description": "脑成像技术（fMRI、EEG）依赖物理学的电磁波和核磁共振原理"
    },
]


def main():
    with open(CROSS_LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Verify concept IDs exist in respective domain seed graphs
    seed_dir = os.path.join(ROOT, "data", "seed")
    domain_concepts = {}
    for link in NEW_LINKS:
        for role in ["source", "target"]:
            d = link[f"{role}_domain"]
            if d not in domain_concepts:
                seed_path = os.path.join(seed_dir, d, "seed_graph.json")
                with open(seed_path, "r", encoding="utf-8") as f:
                    seed = json.load(f)
                domain_concepts[d] = {c["id"] for c in seed["concepts"]}

    for link in NEW_LINKS:
        src_d, src_id = link["source_domain"], link["source_id"]
        tgt_d, tgt_id = link["target_domain"], link["target_id"]
        assert src_id in domain_concepts[src_d], f"Missing source: {src_d}:{src_id}"
        assert tgt_id in domain_concepts[tgt_d], f"Missing target: {tgt_d}:{tgt_id}"

    # Add new links
    data["links"].extend(NEW_LINKS)
    data["total"] = len(data["links"])

    with open(CROSS_LINKS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Added {len(NEW_LINKS)} psychology cross-sphere links")
    print(f"   Total cross-sphere links: {data['total']}")


if __name__ == "__main__":
    main()
