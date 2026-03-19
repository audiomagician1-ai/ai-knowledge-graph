#!/usr/bin/env python3
"""Generate RAG teaching documents for Psychology knowledge sphere.

Creates one markdown file per concept in data/rag/psychology/{subdomain}/{concept}.md
"""
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SEED_PATH = SCRIPT_DIR.parent.parent / "seed" / "psychology" / "seed_graph.json"

SUBDOMAIN_TEMPLATES = {
    "cognitive-psychology": """---
concept: {name}
subdomain: {subdomain_name}
domain: psychology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

认知心理学研究人类如何获取、加工、存储和使用信息。理解认知过程有助于我们认识学习、记忆、思维和决策的心理机制。

## 关键要点

### 理论基础
- **信息加工模型**: 将心智比作信息处理系统，包括输入、加工、存储和输出
- **认知结构**: 图式、心理模型等知识组织方式影响信息的理解和记忆
- **注意资源有限性**: 认知资源有限，需要选择性地分配注意力

### 实践应用
- 利用认知原理优化学习策略（深层加工、间隔重复）
- 识别认知偏差，改善日常决策质量
- 理解认知负荷，设计更有效的教学和界面

## 常见误区

1. **左脑/右脑神话**: 虽然存在偏侧化，但大多数认知任务需要双侧协作
2. **多任务处理高效**: 研究表明任务切换会降低效率和准确性
3. **记忆如录像机**: 记忆是建构性的，每次回忆都可能发生变形

## 与相关概念的联系

{name}是认知心理学知识体系的重要组成部分。掌握这一概念有助于理解人类心智的运作方式，并将这些知识应用到教育、设计和自我提升中。
""",

    "developmental-psychology": """---
concept: {name}
subdomain: {subdomain_name}
domain: psychology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

发展心理学研究人类从出生到老年的心理变化过程。理解发展规律有助于我们更好地养育孩子、理解自身变化，并为不同年龄阶段提供适当支持。

## 关键要点

### 发展原则
- **连续性与阶段性**: 发展既有渐进变化也有质的飞跃
- **关键期与敏感期**: 某些能力在特定时期更容易发展
- **遗传与环境交互**: 基因提供蓝图，环境塑造表达

### 实践意义
- 了解年龄特征，对儿童行为建立合理预期
- 创造丰富的早期环境，促进认知和社会性发展
- 终身发展视角：成年和老年期也有持续发展和积极变化

## 常见误区

1. **发展只在儿童期**: 毕生发展观认为人在整个生命周期都在变化
2. **关键期一旦错过就不可逆**: 大脑具有可塑性，虽然敏感期很重要但不是绝对的
3. **教养方式决定一切**: 基因、同伴和文化同样发挥重要作用

## 与相关概念的联系

{name}是发展心理学知识体系的重要组成部分。理解这一概念有助于我们更好地理解人类成长和变化的规律。
""",

    "social-psychology": """---
concept: {name}
subdomain: {subdomain_name}
domain: psychology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

社会心理学研究个体在社会情境中的思想、感受和行为。它揭示了社会影响的强大力量，帮助我们理解为什么人们在群体中的行为可能与独处时大不相同。

## 关键要点

### 核心原则
- **情境力量**: 社会情境对行为的影响往往超出我们的意识
- **社会建构**: 我们对现实的理解很大程度上由社会互动塑造
- **归因过程**: 我们如何解释他人行为影响我们的反应和态度

### 应用场景
- 理解说服与影响力的心理机制，提升沟通效果
- 识别群体思维和从众压力，培养独立判断力
- 减少偏见和歧视，促进群际和谐

## 常见误区

1. **基本归因错误**: 过度强调个人因素而忽视情境力量
2. **认为自己不受社会影响**: 每个人都受到从众和规范的影响
3. **偏见只是无知的产物**: 偏见有深层的认知和社会根源

## 与相关概念的联系

{name}是社会心理学知识体系的重要组成部分。掌握这一概念有助于理解人际互动、群体行为和社会影响的心理机制。
""",

    "clinical-psychology": """---
concept: {name}
subdomain: {subdomain_name}
domain: psychology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

临床心理学关注心理障碍的评估、诊断和治疗。理解心理健康问题的性质和治疗方法，有助于我们减少对心理疾病的误解，更好地关注自身和他人的心理健康。

## 关键要点

### 核心知识
- **生物-心理-社会模型**: 心理障碍是生物、心理和社会因素共同作用的结果
- **分类系统**: DSM-5和ICD-11提供标准化的诊断框架
- **循证治疗**: 基于研究证据选择最有效的治疗方法

### 关键原则
- 心理障碍具有连续性，正常与异常之间没有绝对界限
- 早期识别和干预显著改善预后
- 治疗关系的质量是疗效的重要预测因子

## 常见误区

1. **心理疾病是软弱的表现**: 心理障碍有明确的神经生物学基础
2. **药物能解决所有心理问题**: 心理治疗对许多障碍同样或更加有效
3. **精神分裂症等于多重人格**: 这是两种完全不同的心理障碍

## 与相关概念的联系

{name}是临床心理学知识体系的重要组成部分。掌握这一概念有助于理解心理健康问题的成因和治疗方法。
""",

    "behavioral-psychology": """---
concept: {name}
subdomain: {subdomain_name}
domain: psychology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

行为心理学研究可观察行为的学习和变化规律。从经典条件反射到社会学习，行为原理不仅解释了我们如何习得新行为，还为行为改变和治疗提供了科学基础。

## 关键要点

### 核心原理
- **条件反射**: 行为通过与环境刺激的关联而习得
- **强化与惩罚**: 行为的后果决定了它在未来出现的频率
- **观察学习**: 通过观察他人的行为及其后果来学习

### 实践应用
- 理解习惯形成机制，建立良好习惯和打破不良习惯
- 将强化原理应用于教育、管理和自我改变
- 系统脱敏等行为技术治疗恐惧和焦虑

## 常见误区

1. **行为主义忽视内心世界**: 现代行为心理学已整合认知因素
2. **惩罚是最有效的行为改变方式**: 研究表明正强化往往更有效且副作用更少
3. **行为完全由环境决定**: 遗传、认知和情感也影响行为

## 与相关概念的联系

{name}是行为心理学知识体系的重要组成部分。理解行为原理有助于我们科学地改变行为、培养习惯和设计有效的干预方案。
""",

    "biological-psychology": """---
concept: {name}
subdomain: {subdomain_name}
domain: psychology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

生物心理学探索心理过程的生物学基础，包括大脑结构、神经递质系统和遗传因素如何影响我们的思维、情感和行为。

## 关键要点

### 核心知识
- **神经系统**: 中枢和外周神经系统协同调控行为
- **神经递质**: 化学信使在神经元之间传递信号，调节情绪和行为
- **大脑可塑性**: 大脑终身保持一定程度的重组和适应能力

### 研究方法
- 脑成像技术（fMRI、PET、EEG）揭示脑功能分区
- 双生子研究和收养研究分离遗传与环境因素
- 精神药理学研究药物对神经递质系统的作用

## 常见误区

1. **我们只使用了大脑的10%**: 整个大脑都在持续活跃
2. **大脑在成年后不再变化**: 神经可塑性贯穿整个生命周期
3. **基因决定命运**: 基因-环境交互作用才是行为的真正基础

## 与相关概念的联系

{name}是生物心理学知识体系的重要组成部分。理解行为的生物学基础有助于我们全面认识心理现象。
""",

    "personality-psychology": """---
concept: {name}
subdomain: {subdomain_name}
domain: psychology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

人格心理学研究使每个人独特的持久思维、情感和行为模式。不同理论流派从特质、精神分析、人本主义和社会认知等角度解释人格。

## 关键要点

### 主要理论
- **特质理论**: 用有限的维度（如大五人格）描述人格差异
- **精神分析理论**: 强调无意识动机和早期经历对人格的塑造
- **人本主义理论**: 关注自我实现和个人成长潜力

### 应用领域
- 人格评估用于职业匹配、心理咨询和人才选拔
- 理解自己和他人的人格特征，改善人际关系
- 人格特质与心理健康的关系指导预防和干预

## 常见误区

1. **人格测试能精确预测行为**: 人格只是影响行为的因素之一
2. **MBTI是科学的人格测量**: MBTI的信度和效度受到学界质疑，大五模型更受推荐
3. **人格一旦形成就不会改变**: 研究表明人格在成年后仍有渐进变化

## 与相关概念的联系

{name}是人格心理学知识体系的重要组成部分。理解人格理论有助于我们更好地认识自己和他人。
""",

    "research-methods": """---
concept: {name}
subdomain: {subdomain_name}
domain: psychology
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

研究方法是心理学的科学基石。掌握研究设计、数据收集和统计分析方法，才能正确评估心理学研究的质量和结论的可靠性。

## 关键要点

### 科学方法论
- **实证主义**: 心理学结论必须基于可观察、可重复的证据
- **可证伪性**: 科学假设必须能够被经验检验
- **操作性定义**: 将抽象概念转化为可测量的操作定义

### 研究设计
- 实验法通过操纵自变量建立因果关系
- 相关研究揭示变量间的关联但不能证明因果
- 纵向和横断研究各有优缺点，适用于不同问题

## 常见误区

1. **相关等于因果**: 两个变量相关不意味着一个导致了另一个
2. **统计显著就意味着重要**: 需要同时关注效应量和实际意义
3. **样本越大越好**: 质量（代表性）比数量更重要

## 与相关概念的联系

{name}是心理学研究方法知识体系的重要组成部分。掌握研究方法有助于培养批判性思维，正确理解和评估心理学研究发现。
""",
}

# Subdomain name mapping
SUBDOMAIN_NAMES = {
    "cognitive-psychology": "认知心理学",
    "developmental-psychology": "发展心理学",
    "social-psychology": "社会心理学",
    "clinical-psychology": "临床心理学",
    "behavioral-psychology": "行为心理学",
    "biological-psychology": "生物心理学",
    "personality-psychology": "人格心理学",
    "research-methods": "研究方法",
}


def generate():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        seed = json.load(f)

    concepts = seed["concepts"]
    documents = []
    total = 0
    total_chars = 0
    by_subdomain = {}

    for c in concepts:
        subdomain = c["subdomain_id"]
        subdomain_name = SUBDOMAIN_NAMES.get(subdomain, subdomain)

        # Ensure subdomain directory exists
        sub_dir = SCRIPT_DIR / subdomain
        sub_dir.mkdir(parents=True, exist_ok=True)

        template = SUBDOMAIN_TEMPLATES.get(subdomain, SUBDOMAIN_TEMPLATES["research-methods"])
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
            "domain_id": "psychology",
            "subdomain_id": subdomain,
            "subdomain_name": subdomain_name,
            "difficulty": c["difficulty"],
            "is_milestone": c.get("is_milestone", False),
            "tags": c.get("tags", []),
            "file": f"psychology/{subdomain}/{c['id']}.md",
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

    print(f"✅ Generated {total} psychology RAG documents")
    print(f"   Index: {index_path}")
    for sub_id, sub_name in SUBDOMAIN_NAMES.items():
        count = sum(1 for c in concepts if c["subdomain_id"] == sub_id)
        print(f"   {sub_id}: {count} docs")


if __name__ == "__main__":
    generate()
