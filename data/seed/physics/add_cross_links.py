#!/usr/bin/env python3
"""Add physics cross-sphere links to cross_sphere_links.json."""
import json, os

LINKS_PATH = os.path.join(os.path.dirname(__file__), "..", "cross_sphere_links.json")

with open(LINKS_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Check if physics links already added
existing_physics = [l for l in data["links"] if l.get("source_domain") == "physics" or l.get("target_domain") == "physics"]
if existing_physics:
    print(f"Physics links already exist ({len(existing_physics)}), skipping")
else:
    physics_links = [
        {"source_domain": "mathematics", "source_id": "derivative-concept", "target_domain": "physics", "target_id": "kinematics-1d", "relation": "enables", "description": "导数的概念直接对应物理中的速度和加速度——瞬时变化率"},
        {"source_domain": "mathematics", "source_id": "definite-integrals", "target_domain": "physics", "target_id": "work-energy", "relation": "enables", "description": "定积分用于计算物理中的功（力对位移的积分）"},
        {"source_domain": "mathematics", "source_id": "differential-equations-intro", "target_domain": "physics", "target_id": "simple-harmonic-motion", "relation": "enables", "description": "简谐运动的方程mx''+kx=0是典型的二阶常微分方程"},
        {"source_domain": "mathematics", "source_id": "vectors-intro", "target_domain": "physics", "target_id": "vectors-in-physics", "relation": "same_concept", "description": "数学中的向量理论是物理向量分析的数学基础"},
        {"source_domain": "mathematics", "source_id": "eigenvalues-eigenvectors", "target_domain": "physics", "target_id": "schrodinger-equation", "relation": "enables", "description": "薛定谔方程本质是求解算符的本征值问题"},
        {"source_domain": "mathematics", "source_id": "probability-basics", "target_domain": "physics", "target_id": "wave-function", "relation": "enables", "description": "概率论为量子力学的概率诠释提供数学基础"},
        {"source_domain": "mathematics", "source_id": "gradient-directional", "target_domain": "physics", "target_id": "electric-potential", "relation": "enables", "description": "电场是电势的负梯度 E=-nabla V"},
        {"source_domain": "mathematics", "source_id": "greens-theorem", "target_domain": "physics", "target_id": "maxwells-equations", "relation": "enables", "description": "格林定理、斯托克斯定理是麦克斯韦方程组积分形式的数学基础"},
        {"source_domain": "mathematics", "source_id": "fourier-intro", "target_domain": "physics", "target_id": "wave-equation", "relation": "enables", "description": "傅里叶分析用于分解和求解波动方程"},
        {"source_domain": "mathematics", "source_id": "taylor-series", "target_domain": "physics", "target_id": "simple-harmonic-motion", "relation": "related", "description": "泰勒展开用于将复杂势能函数近似为二次型，导出简谐运动"},
        {"source_domain": "physics", "source_id": "statistical-mechanics", "target_domain": "ai-engineering", "target_id": "loss-functions", "relation": "related", "description": "物理中的统计力学熵与AI中交叉熵损失函数具有相同的数学形式"},
        {"source_domain": "physics", "source_id": "entropy", "target_domain": "ai-engineering", "target_id": "loss-functions", "relation": "related", "description": "热力学熵的玻尔兹曼定义S=kB*ln(Omega)启发了信息论与交叉熵损失"},
        {"source_domain": "physics", "source_id": "quantum-computing-intro", "target_domain": "ai-engineering", "target_id": "deep-learning-intro", "relation": "related", "description": "量子计算可能为深度学习带来革命性加速"},
        {"source_domain": "physics", "source_id": "sound-waves", "target_domain": "english", "target_id": "vowel-sounds", "relation": "related", "description": "声波的物理属性（频率、振幅）决定了元音的音调和响度"},
        {"source_domain": "physics", "source_id": "band-theory", "target_domain": "ai-engineering", "target_id": "neural-network-basics", "relation": "enables", "description": "能带理论是半导体和GPU等神经网络硬件加速器的物理基础"},
    ]
    data["links"].extend(physics_links)
    data["meta"]["total_links"] = len(data["links"])
    data["meta"]["domain_pairs"]["mathematics_physics"] = 10
    data["meta"]["domain_pairs"]["physics_ai-engineering"] = 4
    data["meta"]["domain_pairs"]["physics_english"] = 1

    with open(LINKS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Added {len(physics_links)} physics cross-sphere links")
    print(f"Total links: {len(data['links'])}")
