#!/usr/bin/env python3
"""Generate RAG teaching documents for Philosophy knowledge sphere.

Creates one markdown file per concept in data/rag/philosophy/{subdomain}/{concept}.md
"""
import json
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
SEED_PATH = SCRIPT_DIR.parent.parent / "seed" / "philosophy" / "seed_graph.json"

SUBDOMAIN_TEMPLATES = {
    "ancient-philosophy": """---
concept: {name}
subdomain: {subdomain_name}
domain: philosophy
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

古代哲学是人类思想的源头。无论是古希腊的理性追问还是中国先秦的智慧传统，古代哲学家们提出的根本问题——什么是存在？什么是善？如何认识世界？——至今仍是哲学探究的核心。

## 关键要点

### 思想脉络
- **古希腊哲学**: 从自然哲学(泰勒斯)到苏格拉底的伦理转向，再到柏拉图与亚里士多德的体系建构
- **中国哲学**: 儒家的仁义之道、道家的自然无为、墨家的兼爱非攻、法家的法治秩序
- **印度哲学**: 佛教的缘起性空、婆罗门教的梵我一如

### 方法论遗产
- 苏格拉底式诘问：通过连续追问揭示概念的深层含义
- 辩证思维：在对立观点的交锋中推进思想
- 道家的直觉体悟：超越概念分析的另一种认知方式

## 常见误区

1. **古代哲学已经过时**: 古代哲学提出的基本问题在现代哲学中仍然活跃
2. **东西方哲学完全对立**: 二者在许多核心问题上有深刻的共鸣和互补
3. **古代哲学只是"智慧"不是"学问"**: 古代哲学家已建立了系统的论证和推理方法

## 与相关概念的联系

{name}是古代哲学知识体系的重要组成部分。理解古代思想传统是把握后世哲学发展脉络的基础。
""",

    "epistemology": """---
concept: {name}
subdomain: {subdomain_name}
domain: philosophy
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

认识论是哲学的核心分支之一，追问"我们能知道什么？如何知道？知识的界限在哪里？"这些问题不仅关乎学术理论，也直接影响我们对科学、教育和日常推理的理解。

## 关键要点

### 核心问题
- **知识的本质**: 知识区别于信念和意见的条件是什么？
- **认知的来源**: 理性推理与感觉经验各自的角色和局限
- **怀疑的挑战**: 我们能否确定自己不是在做梦或被欺骗？

### 主要立场
- 理性主义强调先天理性在知识中的作用
- 经验主义将感觉经验视为知识的最终来源
- 康德尝试综合两者：先验范畴组织感觉材料
- 当代认识论关注辩护、可靠性和社会因素

## 常见误区

1. **知识必须百分百确定**: 大多数当代认识论者接受可错论立场
2. **科学方法是获取知识的唯一途径**: 数学、逻辑和道德知识有不同的认知路径
3. **怀疑论意味着什么都不能知道**: 怀疑论者只是追问知识的根据，不一定否认所有知识

## 与相关概念的联系

{name}是认识论知识体系的重要组成部分。掌握认识论基础有助于培养批判性思维和对知识主张的合理评估能力。
""",

    "metaphysics": """---
concept: {name}
subdomain: {subdomain_name}
domain: philosophy
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

形而上学探究实在的根本结构：什么存在？事物的本质是什么？因果关系的本质是什么？这些看似抽象的问题实际上与我们对自由意志、个人同一性和物理世界的理解密切相关。

## 关键要点

### 核心议题
- **存在论**: 什么类型的实体存在——物质、心灵、抽象对象？
- **因果性**: 因果关系是客观的必然联系还是主观的习惯性期待？
- **自由与决定**: 如果一切由先前原因决定，人的自由选择如何可能？

### 当代进展
- 可能世界语义学为模态概念提供了精确的分析框架
- 心灵哲学与神经科学的交叉深化了心身问题的讨论
- 量子力学对传统因果观和决定论提出了新挑战

## 常见误区

1. **形而上学是空洞的玄思**: 形而上学问题直接关系到科学基础和日常概念
2. **科学已经取代了形而上学**: 科学预设了许多形而上学假定(如因果律)
3. **自由意志问题已经解决**: 这仍是哲学和科学中最活跃的争论之一

## 与相关概念的联系

{name}是形而上学知识体系的重要组成部分。理解形而上学议题有助于我们反思最基本的世界观假设。
""",

    "ethics": """---
concept: {name}
subdomain: {subdomain_name}
domain: philosophy
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

伦理学追问"我们应该怎样行动？什么是好的生活？"这些问题不仅是抽象的理论探讨，更直接关系到个人决策、社会政策和全球议题。

## 关键要点

### 规范伦理学的三大传统
- **后果论(功利主义)**: 行为的对错取决于其后果——是否最大化了总体福祉
- **义务论**: 某些行为本身就是对或错的，不取决于后果
- **美德伦理**: 关注行为者的品格和实践智慧，而非孤立的行为

### 应用伦理的关键领域
- 生命伦理(安乐死、基因编辑)要求我们面对生死抉择
- 环境伦理要求我们思考对非人类存在的责任
- 技术伦理(AI偏见、隐私)提出了前所未有的新问题

## 常见误区

1. **道德就是主观的偏好**: 即使道德判断有主观成分，仍然可以进行合理的道德论证
2. **功利主义只关心数字**: 密尔区分了快乐的质与量，关注人的尊严
3. **伦理学只有唯一正确答案**: 不同理论框架可能对同一问题给出不同但各有道理的答案

## 与相关概念的联系

{name}是伦理学知识体系的重要组成部分。伦理学训练帮助我们在复杂的道德处境中做出更审慎的判断。
""",

    "logic-reasoning": """---
concept: {name}
subdomain: {subdomain_name}
domain: philosophy
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

逻辑学是哲学的基础工具，研究有效推理的形式和规则。掌握逻辑不仅能帮助我们避免推理错误，还能培养严密思维的习惯，这在学术研究和日常生活中都至关重要。

## 关键要点

### 逻辑基础
- **有效性与健全性**: 有效论证形式正确，健全论证还要求前提为真
- **演绎与归纳**: 演绎保证真前提导出真结论，归纳只提供概率支持
- **形式化**: 将自然语言论证翻译为符号语言，使结构一目了然

### 实践价值
- 识别论证中的谬误，避免被不当推理误导
- 构建清晰有力的论证，有效表达和捍卫观点
- 分析复杂问题的逻辑结构，找出关键假设

## 常见误区

1. **逻辑等于死板的规则**: 逻辑是创造性思维的工具，帮助评估而非限制思想
2. **直觉比逻辑更可靠**: 直觉有用但容易受到认知偏差的影响，逻辑提供纠错机制
3. **日常生活不需要逻辑**: 每次做出推理和决策时，我们都在隐式地使用逻辑

## 与相关概念的联系

{name}是逻辑与推理知识体系的重要组成部分。逻辑训练是哲学学习和批判性思维的基石。
""",

    "political-philosophy": """---
concept: {name}
subdomain: {subdomain_name}
domain: philosophy
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

政治哲学追问政治权威的合法性基础：国家为什么有权力？权利的界限在哪里？正义的社会应该是什么样的？这些问题直接关系到我们如何理解和评价政治制度。

## 关键要点

### 核心问题
- **合法性**: 什么使得政治权威是正当的？社会契约论如何回答这个问题？
- **正义**: 如何公平地分配社会资源和机会？
- **自由与平等**: 个人自由与社会平等之间如何平衡？

### 主要传统
- 自由主义强调个人权利和有限政府
- 社会主义关注经济平等和集体福祉
- 保守主义重视传统秩序和渐进改革
- 当代理论探讨全球正义、多元文化和身份政治

## 常见误区

1. **政治哲学等于政党政治**: 政治哲学探讨原则，超越党派之争
2. **民主就是多数决定**: 宪政民主包含对少数权利的保护
3. **正义只有一种理解**: 不同理论对正义有截然不同但各有理据的解释

## 与相关概念的联系

{name}是政治哲学知识体系的重要组成部分。理解政治哲学有助于我们更理性地参与公共讨论和评价社会制度。
""",

    "aesthetics": """---
concept: {name}
subdomain: {subdomain_name}
domain: philosophy
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

美学探究美、艺术和审美经验的本质。什么使一件作品成为艺术？审美判断是纯粹主观的还是有客观标准？这些问题帮助我们深入理解人类对美的追求和创造力的本质。

## 关键要点

### 核心议题
- **美的客观性**: 美是事物的客观属性还是主体的主观反应？
- **艺术的边界**: 什么使某物成为艺术品？杜尚的"泉"挑战了传统定义
- **审美价值**: 审美价值与道德价值、认知价值之间是什么关系？

### 东西方美学对话
- 西方美学从模仿论到表现论再到制度论，关注艺术的定义和评价
- 中国美学强调气韵、意境和留白，关注审美体验的深层意蕴
- 当代美学探讨数字艺术、环境美学和日常生活的审美化

## 常见误区

1. **美就是好看**: 崇高、悲剧和荒诞同样是重要的审美范畴
2. **审美完全是主观的**: 康德和休谟都论证了审美判断中的普遍性要素
3. **艺术哲学只关心高雅艺术**: 当代美学广泛关注流行文化、设计和日常审美

## 与相关概念的联系

{name}是美学知识体系的重要组成部分。美学训练帮助我们更深入地欣赏和理解艺术与审美现象。
""",

    "modern-philosophy": """---
concept: {name}
subdomain: {subdomain_name}
domain: philosophy
difficulty: {difficulty}
---

# {name}

## 核心内容

{description}

近现代哲学从笛卡尔的"我思故我在"开始，经历了理性主义与经验主义的争论、德国观念论的系统建构、存在主义的自由呼唤，直到后现代思潮对宏大叙事的质疑。这一历程深刻塑造了我们今天的思维方式。

## 关键要点

### 重要运动
- **分析哲学**: 通过语言和逻辑分析澄清哲学问题
- **现象学与存在主义**: 回到"事物本身"，关注人的存在处境
- **后结构主义与后现代**: 质疑固定意义、元叙事和二元对立

### 当代前沿
- 心灵哲学与认知科学的交叉：意识的"难问题"
- AI哲学：机器能思考吗？什么是理解？
- 全球哲学：非西方传统的重新发现和跨文化对话

## 常见误区

1. **哲学已经终结**: 当代哲学比以往任何时候都更活跃和多元
2. **分析哲学和大陆哲学完全对立**: 两个传统有越来越多的交叉和对话
3. **后现代主义否认一切真理**: 后现代思潮更多是质疑真理的单一性和权力关系

## 与相关概念的联系

{name}是近现代哲学知识体系的重要组成部分。了解现代哲学的发展有助于理解当代学术和文化中的核心争论。
""",
}

# Subdomain name mapping
SUBDOMAIN_NAMES = {
    "ancient-philosophy": "古代哲学",
    "epistemology": "认识论",
    "metaphysics": "形而上学",
    "ethics": "伦理学",
    "logic-reasoning": "逻辑与推理",
    "political-philosophy": "政治哲学",
    "aesthetics": "美学",
    "modern-philosophy": "近现代哲学",
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

        template = SUBDOMAIN_TEMPLATES.get(subdomain, SUBDOMAIN_TEMPLATES["modern-philosophy"])
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
            "domain_id": "philosophy",
            "subdomain_id": subdomain,
            "subdomain_name": subdomain_name,
            "difficulty": c["difficulty"],
            "is_milestone": c.get("is_milestone", False),
            "tags": c.get("tags", []),
            "file": f"philosophy/{subdomain}/{c['id']}.md",
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

    print(f"✅ Generated {total} philosophy RAG documents")
    print(f"   Index: {index_path}")
    for sub_id, sub_name in SUBDOMAIN_NAMES.items():
        count = sum(1 for c in concepts if c["subdomain_id"] == sub_id)
        print(f"   {sub_id}: {count} docs")


if __name__ == "__main__":
    generate()
