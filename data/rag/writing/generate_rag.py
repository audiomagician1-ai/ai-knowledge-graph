#!/usr/bin/env python3
"""Generate RAG teaching documents for Writing knowledge sphere.

Creates one markdown file per concept in data/rag/writing/{subdomain}/{concept}.md
"""
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SEED_PATH = SCRIPT_DIR.parent.parent / "seed" / "writing" / "seed_graph.json"

SUBDOMAIN_TEMPLATES = {
    "writing-fundamentals": """---
concept: {name}
subdomain: {subdomain_name}
domain: writing
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

写作是思维的外化，是通过文字与读者建立联系的艺术与技能。掌握写作基础是所有高级写作能力的前提。

## 关键要点

### 语言基础
- **句子**: 写作的基本单位，清晰的句子是好文章的基石
- **段落**: 围绕一个中心思想展开，有主题句、支撑句和总结句
- **连贯性**: 句与句、段与段之间需要逻辑连接和过渡

### 写作策略
- 明确写作目的：告知、说服、表达还是娱乐
- 了解目标读者：调整语言风格、深度和专业程度
- 遵循写作过程：构思→起草→修改→校对

## 常见误区

1. **好文章一次写成**: 优秀的写作都经过反复修改，初稿允许不完美
2. **华丽辞藻等于好文章**: 清晰、准确比华丽更重要
3. **写作是天赋**: 写作是可以通过练习提高的技能

## 与相关概念的联系

{name}是写作基础知识体系的重要组成部分。掌握这一概念有助于建立扎实的写作功底。
""",

    "narrative-writing": """---
concept: {name}
subdomain: {subdomain_name}
domain: writing
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

叙事写作是人类最古老的表达形式，通过讲述故事来传递意义、情感和人生体验。

## 关键要点

### 叙事要素
- **人物**: 读者通过人物进入故事，人物的欲望和冲突驱动情节
- **情节**: 故事的骨架——起因、经过、高潮、结局
- **场景**: 时间和空间的设定，为人物和事件提供背景

### 叙事技巧
- 展示而非告知：用具体细节代替抽象概括
- 感官描写：调动五感让读者身临其境
- 对话推进：通过对话展现人物性格和推进情节

## 经典示范

> "他不再说什么了。我在黑暗中望着她的眼睛。"——海明威
> 海明威用极简的语言创造了巨大的情感张力，这就是"冰山理论"。

## 常见误区

1. **事无巨细地描述**: 叙事需要选择和聚焦，不是记流水账
2. **直接告诉读者感受**: 应通过动作和细节让读者自己感受
3. **忽视视角一致性**: 叙事视角的突然切换会让读者困惑

## 与相关概念的联系

{name}是叙事写作的重要组成部分。掌握这一概念有助于提升故事的表现力和感染力。
""",

    "expository-writing": """---
concept: {name}
subdomain: {subdomain_name}
domain: writing
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

说明文以传递信息、解释概念为目的，要求准确、清晰、有条理。科普文章、新闻报道、使用说明都属于说明文范畴。

## 关键要点

### 组织策略
- **时间顺序**: 按照事件发展或操作步骤排列
- **空间顺序**: 按照位置关系描述事物
- **逻辑顺序**: 由浅入深、由因到果、由总到分

### 说明方法
- 定义：界定概念的内涵和外延
- 分类：按标准将事物分为不同类别
- 比较：找出事物间的异同点
- 举例：用具体实例说明抽象概念

## 常见误区

1. **混淆说明与议论**: 说明文解释"是什么"，议论文论证"应该怎样"
2. **缺乏客观性**: 说明文应基于事实，避免主观判断
3. **组织混乱**: 缺少清晰的逻辑线索，读者难以跟随

## 与相关概念的联系

{name}是说明文写作的重要组成部分。掌握这一概念有助于写出信息准确、结构清晰的说明性文章。
""",

    "persuasive-writing": """---
concept: {name}
subdomain: {subdomain_name}
domain: writing
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

论说文以说服读者接受某种观点为目的，需要清晰的论点、充分的论据和严密的论证。

## 关键要点

### 论证三要素
- **论点(Thesis)**: 作者要论证的核心主张，应明确、可辩论
- **论据(Evidence)**: 支持论点的事实、数据、权威引证
- **论证(Reasoning)**: 从论据到论点的逻辑推理过程

### 修辞诉求
- **逻辑诉求(Logos)**: 通过数据、推理说服
- **情感诉求(Pathos)**: 通过故事、意象打动
- **人格诉求(Ethos)**: 通过可信度、专业性建立权威

## 常见误区

1. **观点等于论证**: 仅仅表达观点不等于论证，需要证据支撑
2. **忽视反对意见**: 强有力的论证会预设并反驳反对观点
3. **诉诸情感替代逻辑**: 情感可以辅助但不能替代逻辑论证

## 与相关概念的联系

{name}是论说文写作的重要组成部分。掌握这一概念有助于写出逻辑严密、说服力强的论说性文章。
""",

    "creative-writing": """---
concept: {name}
subdomain: {subdomain_name}
domain: writing
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

创意写作是文学创作的核心领域，包括诗歌、小说、剧本等形式，强调想象力、原创性和艺术表现。

## 关键要点

### 创意原则
- **独特声音**: 发展属于自己的写作风格和观察视角
- **想象力**: 突破现实限制，创造新的可能性
- **情感真实**: 即使在虚构中，情感体验必须真实可信

### 文学手法
- 意象：用具体可感的事物表达抽象的思想和情感
- 象征：赋予事物超越字面意义的深层含义
- 节奏：通过句式长短和词语选择创造音乐感

## 经典示范

> "面朝大海，春暖花开"——海子
> 简单的意象组合传达了对美好生活的向往和诗人内心的矛盾。

## 常见误区

1. **创意写作不需要技巧**: 创意需要以技巧为基础，规则的突破建立在理解规则之上
2. **灵感等于创作**: 创作需要持续的练习和纪律，不能只等灵感
3. **模仿就是抄袭**: 学习经典作家的技法是成长的必经之路

## 与相关概念的联系

{name}是创意写作的重要组成部分。掌握这一概念有助于提升文学创作的艺术性和表现力。
""",

    "academic-writing": """---
concept: {name}
subdomain: {subdomain_name}
domain: writing
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

学术写作是知识生产和交流的核心形式，要求严谨、客观、规范，遵循学术共同体的写作惯例。

## 关键要点

### 学术规范
- **引用规范**: 所有借鉴的观点和数据必须标明出处
- **客观立场**: 使用中性语言，避免主观判断和情绪化表达
- **证据支撑**: 每个论断都需要数据、文献或理论支撑

### 论文结构
- IMRAD格式：引言(Introduction)、方法(Methods)、结果(Results)、讨论(Discussion)
- 文献综述：梳理研究领域的已有成果和知识空白
- 摘要与关键词：论文的精华浓缩

## 常见误区

1. **学术写作必须艰涩难懂**: 好的学术写作应该是清晰且精确的
2. **引用越多越好**: 引用应精选与论点直接相关的高质量文献
3. **写完即完成**: 学术写作需要反复修改和同行反馈

## 与相关概念的联系

{name}是学术写作的重要组成部分。掌握这一概念有助于在学术环境中进行有效的知识交流。
""",

    "professional-writing": """---
concept: {name}
subdomain: {subdomain_name}
domain: writing
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

职业写作服务于工作场景，以效率、清晰和专业性为核心目标。从商务邮件到技术文档，每种形式都有其特定的规范。

## 关键要点

### 职业写作原则
- **目的明确**: 每篇文档都有明确的沟通目标
- **读者导向**: 根据读者的背景和需求调整内容
- **格式规范**: 遵循行业和组织的文档标准
- **简洁高效**: 用最少的文字传达最多的信息

### 常见场景
- 商务邮件：开门见山、一事一议、行动导向
- 报告写作：数据支撑、结构清晰、建议明确
- 技术文档：步骤详尽、用词准确、示例充分

## 常见误区

1. **职业写作不需要写作技巧**: 清晰有效的职业写作需要训练
2. **越长越显示认真**: 简洁是职业写作的美德
3. **只关注内容忽略格式**: 格式影响可读性和专业形象

## 与相关概念的联系

{name}是职业写作的重要组成部分。掌握这一概念有助于在职业环境中进行高效的书面沟通。
""",

    "revision-craft": """---
concept: {name}
subdomain: {subdomain_name}
domain: writing
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

修改是写作过程中最关键的阶段。好文章不是写出来的，是改出来的。修改分为宏观（结构）和微观（语言）两个层次。

## 关键要点

### 修改层次
- **结构层**: 文章整体架构、段落组织是否合理
- **段落层**: 各段是否围绕中心展开、过渡是否自然
- **句子层**: 句子是否清晰、简洁、有力
- **词语层**: 用词是否精准、是否有冗余

### 修改方法
- 搁置法：写完后放一段时间再修改，获得"陌生化"视角
- 朗读法：朗读全文，用听觉发现节奏和流畅度问题
- 逆向大纲：对已写完的文章列大纲，检查逻辑结构
- 同行反馈：请他人阅读并提供建设性意见

## 常见误区

1. **修改等于校对**: 校对只是修改的最后一步，不等于修改
2. **舍不得删**: 大胆删除与主题无关或冗余的内容（"杀死你的宠儿"）
3. **一遍修改解决所有问题**: 每遍修改聚焦一个层次效果更好

## 与相关概念的联系

{name}是修改与文体技巧的重要组成部分。掌握这一概念有助于提升文章的整体质量和表达效果。
""",
}

SUBDOMAIN_NAMES = {
    "writing-fundamentals": "写作基础",
    "narrative-writing": "叙事写作",
    "expository-writing": "说明文写作",
    "persuasive-writing": "论说文写作",
    "creative-writing": "创意写作",
    "academic-writing": "学术写作",
    "professional-writing": "职业写作",
    "revision-craft": "修改与文体",
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

        template = SUBDOMAIN_TEMPLATES.get(subdomain, SUBDOMAIN_TEMPLATES["writing-fundamentals"])
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
            "domain_id": "writing",
            "subdomain_id": subdomain,
            "subdomain_name": subdomain_name,
            "difficulty": c["difficulty"],
            "is_milestone": c.get("is_milestone", False),
            "tags": c.get("tags", []),
            "file": f"writing/{subdomain}/{c['id']}.md",
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

    print(f"✅ Generated {total} writing RAG documents")
    print(f"   Index: {index_path}")
    for sub_id, sub_name in SUBDOMAIN_NAMES.items():
        count = sum(1 for c in concepts if c["subdomain_id"] == sub_id)
        print(f"   {sub_id}: {count} docs")


if __name__ == "__main__":
    main()
