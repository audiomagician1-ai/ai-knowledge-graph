#!/usr/bin/env python3
"""Phase 37: Add missing cross-sphere links and validate."""
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
LINKS_PATH = ROOT / "data" / "seed" / "cross_sphere_links.json"

def load_seed(domain):
    p = ROOT / "data" / "seed" / domain / "seed_graph.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def get_concept_ids(domain):
    data = load_seed(domain)
    return {c["id"] for c in data.get("concepts", [])}

# New links to add
NEW_LINKS = [
    # === physics <-> computer-graphics ===
    {
        "source_domain": "physics",
        "source_id": "geometric-optics",
        "target_domain": "computer-graphics",
        "target_id": "cg-rt-intro",
        "relation": "foundational_theory",
        "description": "几何光学是光线追踪的物理理论基础，光线直线传播/反射/折射定律直接映射为CG中的ray generation和intersection算法"
    },
    {
        "source_domain": "physics",
        "source_id": "reflection-refraction",
        "target_domain": "computer-graphics",
        "target_id": "cg-rt-reflection",
        "relation": "foundational_theory",
        "description": "反射定律(入射角=反射角)和折射定律(Snell定律)是光追反射/折射着色器的直接物理依据"
    },
    {
        "source_domain": "physics",
        "source_id": "reflection-refraction",
        "target_domain": "computer-graphics",
        "target_id": "cg-rt-refraction",
        "relation": "foundational_theory",
        "description": "Snell定律(n1·sinθ1=n2·sinθ2)是光追折射计算的核心公式，全内反射判定也来自物理光学"
    },
    {
        "source_domain": "physics",
        "source_id": "collisions",
        "target_domain": "computer-graphics",
        "target_id": "cg-ray-intersection",
        "relation": "applies_concept",
        "description": "碰撞检测的几何判定方法(射线-球、射线-平面)直接用于光线求交算法"
    },
    {
        "source_domain": "physics",
        "source_id": "wave-basics",
        "target_domain": "computer-graphics",
        "target_id": "cg-subsurface",
        "relation": "foundational_theory",
        "description": "波动光学中的散射理论是次表面散射(SSS)模型的物理基础，描述光在半透明介质中的传播行为"
    },
    # === ai-engineering <-> game-design ===
    {
        "source_domain": "ai-engineering",
        "source_id": "decision-tree",
        "target_domain": "game-design",
        "target_id": "ai-behavior",
        "relation": "applies_concept",
        "description": "决策树是游戏AI行为树的理论前身，行为树(Behavior Tree)直接扩展了决策树的条件分支模式用于NPC行为决策"
    },
    {
        "source_domain": "ai-engineering",
        "source_id": "agent-overview",
        "target_domain": "game-design",
        "target_id": "enemy-design",
        "relation": "applies_concept",
        "description": "AI Agent的感知-推理-行动循环直接映射到游戏敌人AI设计: 感知(视野/仇恨)→推理(策略选择)→行动(攻击/撤退)"
    },
    {
        "source_domain": "ai-engineering",
        "source_id": "neural-network-basics",
        "target_domain": "game-design",
        "target_id": "procedural-gen",
        "relation": "applies_concept",
        "description": "神经网络(特别是GAN/Diffusion)越来越多用于程序化内容生成(PCG): 地图生成、纹理合成、关卡布局"
    },
    {
        "source_domain": "ai-engineering",
        "source_id": "agent-planning",
        "target_domain": "game-design",
        "target_id": "ai-behavior",
        "relation": "applies_concept",
        "description": "Agent规划与任务分解技术(GOAP/HTN)广泛应用于游戏NPC的战术AI和策略决策系统"
    },
    # === ai-engineering <-> technical-art ===
    {
        "source_domain": "ai-engineering",
        "source_id": "neural-network-basics",
        "target_domain": "technical-art",
        "target_id": "ta-pcg-terrain",
        "relation": "applies_concept",
        "description": "神经网络驱动的地形生成(如terrain diffusion models)正在革新程序化地形工作流，补充传统噪声方法"
    },
    {
        "source_domain": "ai-engineering",
        "source_id": "deep-learning-intro",
        "target_domain": "technical-art",
        "target_id": "ta-procedural-material",
        "relation": "applies_concept",
        "description": "深度学习用于材质生成(如text-to-material)和材质参数推断(从照片反推PBR参数)正在改变程序化材质工作流"
    },
    {
        "source_domain": "ai-engineering",
        "source_id": "code-generation",
        "target_domain": "technical-art",
        "target_id": "ta-batch-tool",
        "relation": "applies_concept",
        "description": "AI代码生成Agent可辅助TA编写批处理工具脚本(Maya Python, Houdini VEX, UE Blueprint)，加速工具开发和资产处理自动化"
    },
]

def main():
    # Validate all concept IDs exist
    print("=== Validating new links ===")
    all_valid = True
    domains_cache = {}
    
    for link in NEW_LINKS:
        for side in ["source", "target"]:
            domain = link[f"{side}_domain"]
            cid = link[f"{side}_id"]
            if domain not in domains_cache:
                domains_cache[domain] = get_concept_ids(domain)
            if cid not in domains_cache[domain]:
                print(f"  ERROR: {cid} not found in {domain}")
                all_valid = False
            else:
                print(f"  OK: {cid} @ {domain}")
    
    if not all_valid:
        print("\nABORTED: Fix invalid concept IDs first!")
        return
    
    # Load existing links
    with open(LINKS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    existing_count = len(data["links"])
    
    # Check for duplicates
    existing_set = set()
    for l in data["links"]:
        key = (l["source_domain"], l["source_id"], l["target_domain"], l["target_id"])
        existing_set.add(key)
    
    added = 0
    for link in NEW_LINKS:
        key = (link["source_domain"], link["source_id"], link["target_domain"], link["target_id"])
        rev_key = (link["target_domain"], link["target_id"], link["source_domain"], link["source_id"])
        if key in existing_set or rev_key in existing_set:
            print(f"  SKIP (duplicate): {key[1]} -> {key[3]}")
            continue
        data["links"].append(link)
        existing_set.add(key)
        added += 1
        print(f"  ADDED: {link['source_domain']}:{link['source_id']} -> {link['target_domain']}:{link['target_id']}")
    
    # Update metadata
    data["metadata"] = data.get("metadata", {})
    data["metadata"]["total_links"] = len(data["links"])
    data["metadata"]["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    data["metadata"]["phase"] = "37"
    
    # Write back
    with open(LINKS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n=== DONE ===")
    print(f"Previous: {existing_count} links")
    print(f"Added: {added} links")
    print(f"Total: {len(data['links'])} links")

if __name__ == "__main__":
    main()
