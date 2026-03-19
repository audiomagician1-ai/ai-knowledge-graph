#!/usr/bin/env python3
"""Generate RAG teaching documents for Product Design knowledge sphere.

Creates one markdown file per concept in data/rag/product-design/{subdomain}/{concept}.md
"""
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SEED_PATH = SCRIPT_DIR.parent.parent / "seed" / "product-design" / "seed_graph.json"

# Templates for product-design RAG documents by subdomain
SUBDOMAIN_TEMPLATES = {
    "user-research": """---
concept: {name}
subdomain: {subdomain_name}
domain: product-design
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

用户研究是产品设计的基石。通过系统性的研究方法，我们能够深入理解用户需求、行为模式和痛点，为产品决策提供数据支撑。

## 关键要点

### 方法论基础
- **研究目标设定**: 明确要解答的核心问题，避免漫无目的的研究
- **样本选择**: 根据研究目标选择代表性用户群体
- **数据三角验证**: 结合定性和定量数据交叉验证发现

### 实践要领
- 始终保持开放心态，避免确认偏见
- 区分用户说的（态度）和做的（行为）
- 记录原始数据，避免过早下结论

## 常见误区

1. **只听用户说的**: 用户的自述未必反映真实行为，需要结合观察法
2. **样本偏差**: 只调研容易触达的用户，忽略沉默的多数
3. **过度解读**: 从少量样本中得出过于绝对的结论

## 与相关概念的联系

{name}是用户研究体系的重要组成部分。掌握这个概念有助于理解如何在产品设计流程中做出更有依据的决策。
""",

    "product-thinking": """---
concept: {name}
subdomain: {subdomain_name}
domain: product-design
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

产品思维是产品经理的核心能力，它要求我们从用户需求、商业价值和技术可行性三个维度综合思考产品决策。

## 关键要点

### 思维框架
- **以终为始**: 从用户要达成的目标反推产品形态
- **假设驱动**: 将主观判断转化为可验证的假设
- **全局视角**: 平衡短期收益与长期价值

### 决策原则
- 数据支撑但不被数据绑架
- 做减法比做加法更重要
- 好的产品决策可以被解释和复制

## 常见误区

1. **功能堆砌**: 用更多功能填补产品空白，而非聚焦核心价值
2. **竞品模仿**: 盲目跟随竞品功能而忽略自身产品定位
3. **过度分析**: 追求完美数据支撑导致决策瘫痪

## 与相关概念的联系

{name}是产品思维体系中的关键概念。理解它有助于建立系统性的产品决策能力，从"做什么"到"为什么做"的思维升级。
""",

    "interaction-design": """---
concept: {name}
subdomain: {subdomain_name}
domain: product-design
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

交互设计关注用户与产品之间的互动方式。好的交互设计让用户感觉"自然"——即无需思考就能完成目标。

## 关键要点

### 设计原则
- **一致性**: 相似的操作产生相似的结果
- **反馈**: 每个用户操作都有即时的视觉或触觉反馈
- **可预测性**: 用户能预期操作的结果

### 认知负荷
- 减少用户需要记忆的信息量
- 利用已有的心智模型
- 渐进式披露复杂功能

## 常见误区

1. **过度创新**: 为了独特性而打破用户已建立的交互习惯
2. **忽视边缘情况**: 只考虑理想路径，忽略错误状态和空状态
3. **视觉优先**: 为了美观牺牲可用性和可达性

## 与相关概念的联系

{name}是交互设计知识体系中的重要节点。它与信息架构、视觉设计和用户研究紧密关联。
""",

    "visual-design": """---
concept: {name}
subdomain: {subdomain_name}
domain: product-design
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

视觉设计不只是"好看"——它是信息传达的视觉语言。通过色彩、排版、层级和空间，引导用户的注意力并传达品牌调性。

## 关键要点

### 设计基础
- **对比**: 通过差异创造视觉焦点
- **层级**: 大小、颜色、位置传达信息重要性
- **留白**: 给内容呼吸的空间

### 系统化思维
- 建立可复用的设计组件
- 用设计令牌管理全局样式
- 确保跨平台视觉一致性

## 常见误区

1. **装饰过度**: 添加不必要的视觉元素增加认知负荷
2. **忽视可及性**: 色彩对比度不足导致部分用户无法阅读
3. **风格不一致**: 同一产品内视觉语言混乱

## 与相关概念的联系

{name}是视觉设计体系的组成部分。视觉设计需要与交互设计、品牌策略协同工作。
""",

    "prototyping": """---
concept: {name}
subdomain: {subdomain_name}
domain: product-design
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

原型是将抽象想法变为可感知、可测试的形态。好的原型能在最少投入下验证最多假设。

## 关键要点

### 原型策略
- **保真度匹配**: 根据验证目的选择合适的保真度
- **快速迭代**: 宁可做10个粗糙原型，也不做1个完美原型
- **聚焦核心**: 只构建需要验证的部分

### 测试方法
- 设计明确的任务让用户完成
- 观察行为而非仅听取意见
- 记录完成时间和错误率

## 常见误区

1. **过早高保真**: 在方向未确定时就投入精细设计
2. **原型即产品**: 把原型的代码或设计直接用于生产
3. **跳过测试**: 做了原型但没有让真实用户测试

## 与相关概念的联系

{name}是原型与测试流程的重要环节。它连接了设计构思与用户验证的闭环。
""",

    "data-driven": """---
concept: {name}
subdomain: {subdomain_name}
domain: product-design
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

数据驱动不是"数据崇拜"——而是用数据减少决策中的不确定性。关键在于选择正确的指标、正确地解读数据，并转化为行动。

## 关键要点

### 指标体系
- **北极星指标**: 反映产品核心价值的单一关键指标
- **先导指标vs滞后指标**: 能预测未来的指标 vs 反映过去的指标
- **虚荣指标vs可行动指标**: 看起来好看的数据 vs 能指导行动的数据

### 分析方法
- 对比分析: 与历史/竞品/预期比较
- 下钻分析: 从整体到细分寻找根因
- 归因分析: 确定变化的原因

## 常见误区

1. **幸存者偏差**: 只分析活跃用户，忽略流失用户
2. **因果混淆**: 将相关性当作因果性
3. **指标操纵**: 优化指标而非优化用户体验

## 与相关概念的联系

{name}是数据驱动决策体系的一部分。它需要与产品策略、用户研究和增长运营紧密配合。
""",

    "product-management": """---
concept: {name}
subdomain: {subdomain_name}
domain: product-design
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

产品管理是将愿景转化为现实的艺术。它需要平衡用户需求、商业目标和技术约束，在不确定性中做出最佳决策。

## 关键要点

### 管理框架
- **目标对齐**: 确保团队理解"为什么做"而非仅"做什么"
- **优先级排序**: 在无限需求中选择最有价值的子集
- **节奏管理**: 建立可预期的迭代和发布节奏

### 协作能力
- 跨职能沟通: 用不同语言与开发、设计、业务对话
- 期望管理: 透明沟通进度和约束
- 冲突解决: 在对立诉求中寻找共赢方案

## 常见误区

1. **需求工厂**: 沦为需求传递者而非产品决策者
2. **微观管理**: 过度干预设计和开发细节
3. **忽视技术债**: 只关注新功能而累积技术风险

## 与相关概念的联系

{name}是产品管理知识体系的关键组成。它连接了产品战略和执行落地的桥梁。
""",

    "growth": """---
concept: {name}
subdomain: {subdomain_name}
domain: product-design
difficulty: {difficulty}
---

# {name}

## 核心概念

{description}

增长不只是市场营销——它是产品、数据和运营的交叉学科。好的增长策略将用户价值和商业价值统一起来。

## 关键要点

### 增长思维
- **实验优先**: 用小规模实验验证增长假设
- **系统化**: 将增长从偶然的灵感变为可复制的流程
- **全漏斗视角**: 从获客到留存再到推荐的完整链路

### 执行要领
- 找到并优化增长杠杆点
- 关注单位经济模型(CAC/LTV)
- 建立增长实验的学习体系

## 常见误区

1. **获客至上**: 只关注拉新而忽视留存，用户如漏水桶
2. **补贴依赖**: 用折扣和补贴驱动增长而非产品价值
3. **短期主义**: 为短期指标牺牲长期用户体验

## 与相关概念的联系

{name}是增长运营体系的重要概念。增长需要产品、数据和用户研究的综合能力支撑。
""",
}


def generate_rag_docs():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        seed = json.load(f)

    sub_map = {s["id"]: s["name"] for s in seed["subdomains"]}
    created = 0

    for concept in seed["concepts"]:
        sub_id = concept["subdomain_id"]
        sub_name = sub_map[sub_id]
        template = SUBDOMAIN_TEMPLATES.get(sub_id, SUBDOMAIN_TEMPLATES["product-thinking"])

        content = template.format(
            name=concept["name"],
            description=concept["description"],
            subdomain_name=sub_name,
            difficulty=concept["difficulty"],
        )

        # Create subdomain directory
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
        file_rel = f"product-design/{sub_id}/{concept['id']}.md"
        file_abs = SCRIPT_DIR / sub_id / f"{concept['id']}.md"
        char_count = len(file_abs.read_text(encoding="utf-8"))
        documents.append({
            "id": concept["id"],
            "name": concept["name"],
            "domain_id": "product-design",
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
    from collections import Counter
    sub_counts = Counter(c["subdomain_id"] for c in seed["concepts"])
    for s in seed["subdomains"]:
        print(f"  {s['name']}: {sub_counts[s['id']]} docs")


if __name__ == "__main__":
    generate_rag_docs()
