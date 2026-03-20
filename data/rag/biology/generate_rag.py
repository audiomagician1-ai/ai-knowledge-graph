#!/usr/bin/env python3
"""Generate RAG teaching documents for Biology knowledge sphere.

Creates one markdown file per concept in data/rag/biology/{subdomain}/{concept}.md
"""
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SEED_PATH = SCRIPT_DIR.parent.parent / "seed" / "biology" / "seed_graph.json"

SUBDOMAIN_TEMPLATES = {
    "cell-biology": """---
concept: {name}
subdomain: {subdomain_name}
domain: biology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

细胞是生命的基本单位。理解细胞的结构和功能是整个生物学的基础，从分子事件到有机体层面的现象都可以追溯到细胞水平。

## 关键要点

### 结构与功能
- **膜系统**: 细胞膜及内膜系统（内质网、高尔基体、溶酶体）构成细胞的区室化结构
- **能量转换**: 线粒体（有氧呼吸）和叶绿体（光合作用）是细胞的能量工厂
- **遗传信息中心**: 细胞核存储DNA，控制基因表达和细胞命运

### 进化视角
- 原核细胞→真核细胞的进化是生命史上最重要的跃迁之一
- 内共生学说解释了线粒体和叶绿体的起源
- 多细胞生物的出现依赖于细胞间通讯和分化机制

## 常见误区

1. **细胞是静态结构**: 细胞内部高度动态，蛋白质和细胞器持续运动和更新
2. **所有细胞都一样**: 同一有机体中不同类型细胞的结构和功能差异巨大
3. **原核细胞"低等"**: 细菌在极端环境中表现出惊人的适应能力和代谢多样性

## 与相关概念的联系

{name}是细胞生物学知识体系的重要组成部分。掌握这一概念有助于理解生命活动的分子和细胞基础。
""",

    "molecular-biology": """---
concept: {name}
subdomain: {subdomain_name}
domain: biology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

分子生物学揭示了生命现象的分子机制。从DNA复制到蛋白质合成，从基因调控到信号转导，分子水平的理解是现代生物学和医学的基石。

## 关键要点

### 中心法则
- **DNA→RNA→蛋白质**: 遗传信息的流动方向，但存在例外（逆转录、RNA复制）
- **基因调控**: 并非所有基因同时表达，精确调控是细胞分化和发育的基础
- **表观遗传**: 不改变DNA序列的可遗传变化，扩展了经典遗传学的范畴

### 技术革命
- PCR、基因克隆和测序技术革新了生物学研究
- CRISPR基因编辑开启了精确改造基因组的新时代
- 组学技术（基因组学、蛋白质组学）提供了系统生物学视角

## 常见误区

1. **一个基因=一个蛋白质**: 选择性剪接使一个基因可以编码多种蛋白质
2. **"垃圾DNA"无功能**: 非编码DNA中包含大量调控元件和功能性RNA
3. **基因决定一切**: 表观遗传和环境因素在基因表达调控中发挥重要作用

## 与相关概念的联系

{name}是分子生物学知识体系的重要组成部分。理解这一概念有助于把握生命活动的分子基础。
""",

    "genetics": """---
concept: {name}
subdomain: {subdomain_name}
domain: biology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

遗传学研究基因的结构、功能与传递规律。从孟德尔的豌豆实验到人类基因组计划，遗传学的进展深刻影响了医学、农业和法医学等领域。

## 关键要点

### 遗传规律
- **孟德尔定律**: 分离定律和自由组合定律是经典遗传学的基石
- **染色体理论**: 基因位于染色体上，连锁和交换产生重组
- **群体遗传**: Hardy-Weinberg平衡描述了理想群体中基因频率的稳定性

### 应用前沿
- 遗传咨询帮助家庭了解遗传风险并做出知情决策
- 药物基因组学实现个体化精准用药
- 基因治疗为遗传病提供了根治的希望

## 常见误区

1. **显性=优势/隐性=劣势**: 显隐性仅描述表型表达模式，与"好坏"无关
2. **遗传决定论**: 绝大多数性状由遗传和环境共同决定
3. **突变总是有害的**: 突变是进化的原材料，中性突变最为常见

## 与相关概念的联系

{name}是遗传学知识体系的重要组成部分。掌握这一概念有助于理解生物多样性的遗传基础。
""",

    "evolution": """---
concept: {name}
subdomain: {subdomain_name}
domain: biology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

进化是生物学的统一理论。正如Dobzhansky所言："除了在进化的光照下，生物学中的一切都毫无意义。"理解进化有助于我们理解生命的多样性和统一性。

## 关键要点

### 进化机制
- **自然选择**: 环境对可遗传变异的差异性选择，是适应性进化的主要驱动力
- **遗传漂变**: 小种群中随机事件导致的基因频率变化
- **基因流和突变**: 为种群提供新的遗传变异，是进化的原材料

### 宏观进化
- 物种形成通常需要地理或生殖隔离
- 适应辐射展示了进化在新生态位中的爆发性多样化
- 大灭绝事件重塑了地球生命的格局

## 常见误区

1. **"进化=进步"**: 进化没有方向或目标，只是对环境的适应
2. **"适者生存=最强者生存"**: 适应性取决于具体环境，而非绝对"强弱"
3. **"人类从猴子进化而来"**: 人类和现代猿类共享共同祖先，而非直系后代

## 与相关概念的联系

{name}是进化生物学知识体系的重要组成部分。理解这一概念有助于从进化视角看待一切生物现象。
""",

    "human-physiology": """---
concept: {name}
subdomain: {subdomain_name}
domain: biology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

人体生理学研究人体各器官系统的功能及其协调机制。稳态（homeostasis）是生理学的核心概念——人体通过精密的反馈调节维持内环境的相对稳定。

## 关键要点

### 系统协调
- **神经-内分泌调节**: 快速的神经信号和持久的激素信号协同工作
- **反馈调节**: 负反馈维持稳态，正反馈放大特定生理过程
- **器官系统整合**: 循环、呼吸、消化等系统相互依赖、协同运作

### 临床关联
- 理解正常生理功能是理解疾病的基础
- 生理学指标（血压、血糖、体温）是健康监测的核心
- 运动、营养和生活方式通过影响生理功能维护健康

## 常见误区

1. **大脑只使用10%**: 脑成像研究表明大脑各区域都有功能，全脑都在使用
2. **抗生素能治病毒感染**: 抗生素仅对细菌有效，对病毒无作用
3. **免疫力越强越好**: 过度免疫反应会导致自身免疫病和过敏

## 与相关概念的联系

{name}是人体生理学知识体系的重要组成部分。掌握这一概念有助于理解人体如何维持生命活动。
""",

    "ecology": """---
concept: {name}
subdomain: {subdomain_name}
domain: biology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

生态学研究生物与环境之间的相互关系。从个体到生态系统，生态学帮助我们理解自然界的复杂网络，也为保护生物多样性和应对环境危机提供科学基础。

## 关键要点

### 生态层次
- **种群**: 同种生物在特定区域的集合，研究增长、调节和波动
- **群落**: 不同物种在同一环境中的共存，研究多样性和种间关系
- **生态系统**: 生物群落及其非生物环境，研究能量流动和物质循环

### 保护意义
- 生物多样性是生态系统服务（净化空气、水源涵养等）的基础
- 气候变化正在重塑全球生态格局
- 可持续发展需要生态学理论的指导

## 常见误区

1. **自然界处于平衡状态**: 生态系统是动态的，干扰和演替持续发生
2. **食物链是线性的**: 现实中是复杂的食物网而非简单的链
3. **保护就是不干预**: 许多退化生态系统需要积极的恢复管理

## 与相关概念的联系

{name}是生态学知识体系的重要组成部分。理解这一概念有助于我们更好地保护和管理自然环境。
""",

    "microbiology": """---
concept: {name}
subdomain: {subdomain_name}
domain: biology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

微生物学研究肉眼不可见的微小生物——细菌、病毒、真菌和原生生物。微生物无处不在，它们既是致病的元凶，也是生态系统的关键参与者和生物技术的重要工具。

## 关键要点

### 微生物多样性
- **细菌**: 最丰富的微生物类群，在几乎所有环境中都能找到
- **病毒**: 非细胞结构的感染性因子，必须寄生于宿主细胞才能复制
- **真菌与原生生物**: 真核微生物，在生态系统中扮演分解者和初级生产者角色

### 人类健康
- 人体微生物组包含数万亿微生物，对消化、免疫和代谢至关重要
- 抗生素耐药性是当今最严峻的公共卫生挑战之一
- 疫苗是人类对抗传染病最有效的工具

## 常见误区

1. **所有细菌都有害**: 绝大多数细菌对人体无害或有益
2. **病毒是活的生物**: 病毒处于生命与非生命的边界，无法独立代谢
3. **抗菌皂比普通肥皂更好**: 研究表明普通肥皂+正确洗手同样有效

## 与相关概念的联系

{name}是微生物学知识体系的重要组成部分。理解这一概念有助于认识微生物在健康、疾病和生态中的关键角色。
""",

    "botany-zoology": """---
concept: {name}
subdomain: {subdomain_name}
domain: biology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

植物与动物学研究多细胞生物的多样性、结构、功能和行为。从简单的苔藓到复杂的哺乳动物，多细胞生物展示了进化的无穷创造力。

## 关键要点

### 比较生物学
- **同源与类比**: 同源结构揭示共同祖先，趋同进化产生相似功能解决方案
- **适应与多样性**: 不同环境压力塑造了生物的形态和生理适应
- **发育与进化**: evo-devo揭示了发育基因变化驱动形态多样性

### 生态关系
- 植物是陆地生态系统的初级生产者，通过光合作用固定碳
- 动物行为（觅食、求偶、迁徙）是自然选择的产物
- 物种间的共生、寄生和捕食关系驱动协同进化

## 常见误区

1. **植物是被动的生物**: 植物能主动响应环境、进行化学防御甚至"沟通"
2. **动物行为完全由本能决定**: 许多动物展示出学习、问题解决和文化传承
3. **越复杂的生物越"高等"**: 进化没有高低之分，每个物种都适应其特定生态位

## 与相关概念的联系

{name}是植物与动物学知识体系的重要组成部分。理解这一概念有助于欣赏生命的多样性和适应性。
""",
}

SUBDOMAIN_NAMES = {
    "cell-biology": "细胞生物学",
    "molecular-biology": "分子生物学",
    "genetics": "遗传学",
    "evolution": "进化生物学",
    "human-physiology": "人体生理学",
    "ecology": "生态学",
    "microbiology": "微生物学",
    "botany-zoology": "植物与动物学",
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

        template = SUBDOMAIN_TEMPLATES.get(subdomain, SUBDOMAIN_TEMPLATES["cell-biology"])
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
            "domain_id": "biology",
            "subdomain_id": subdomain,
            "subdomain_name": subdomain_name,
            "difficulty": c["difficulty"],
            "is_milestone": c.get("is_milestone", False),
            "tags": c.get("tags", []),
            "file": f"biology/{subdomain}/{c['id']}.md",
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

    print(f"✅ Generated {total} biology RAG documents")
    print(f"   Index: {index_path}")
    for sub_id, sub_name in SUBDOMAIN_NAMES.items():
        count = sum(1 for c in concepts if c["subdomain_id"] == sub_id)
        print(f"   {sub_id}: {count} docs")


if __name__ == "__main__":
    main()
