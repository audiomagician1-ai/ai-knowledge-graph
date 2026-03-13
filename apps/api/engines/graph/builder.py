"""
知识图谱构建器
半自动化: LLM生成候选 → 规则消歧 → 人工审核
"""


class GraphBuilder:
    """知识图谱构建引擎

    Phase 0 — 种子图谱:
    1. 用 LLM 生成编程领域概念列表 (~300节点)
    2. 生成概念间依赖关系 (PREREQUISITE 边)
    3. 生成关联关系 (RELATED_TO 边)
    4. 写入 Neo4j
    """

    # TODO: Phase 0 种子图谱构建
    pass
