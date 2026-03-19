#!/usr/bin/env python3
"""
Generate English RAG documents (Phase 9.2).
Reads seed_graph.json, generates one .md per concept + _index.json.
Usage: python data/rag/english/generate_rag.py
"""
import json, os, sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", ".."))
SEED_PATH = os.path.join(PROJECT_ROOT, "data", "seed", "english", "seed_graph.json")
TEMPLATES_PATH = os.path.join(SCRIPT_DIR, "_templates.json")
RAG_DIR = SCRIPT_DIR
INDEX_PATH = os.path.join(RAG_DIR, "_index.json")

DOMAIN_ID = "english"


def load_seed():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_templates():
    if os.path.exists(TEMPLATES_PATH):
        with open(TEMPLATES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def build_edge_map(seed):
    cmap = {c["id"]: c["name"] for c in seed["concepts"]}
    prereqs, postreqs = {}, {}
    for e in seed["edges"]:
        s, t = e["source_id"], e["target_id"]
        prereqs.setdefault(t, []).append(cmap.get(s, s))
        postreqs.setdefault(s, []).append(cmap.get(t, t))
    return prereqs, postreqs


def generic_content(c):
    """Generate English learning content for a concept."""
    name, desc, diff = c["name"], c["description"], c["difficulty"]
    sub_id = c["subdomain_id"]
    ctype = c.get("content_type", "theory")
    labels = {1: "入门", 2: "基础", 3: "基础进阶", 4: "中级", 5: "中级进阶",
              6: "中高级", 7: "高级", 8: "高级进阶", 9: "母语级"}
    dl = labels.get(diff, "中级")

    # Different content style based on subdomain
    if sub_id == "phonetics":
        core = _phonetics_content(name, desc, diff, dl)
    elif sub_id == "basic-grammar":
        core = _grammar_content(name, desc, diff, dl)
    elif sub_id == "vocabulary":
        core = _vocabulary_content(name, desc, diff, dl)
    elif sub_id == "tenses":
        core = _tenses_content(name, desc, diff, dl)
    elif sub_id == "sentence-patterns":
        core = _sentence_content(name, desc, diff, dl)
    elif sub_id == "advanced-grammar":
        core = _advanced_grammar_content(name, desc, diff, dl)
    elif sub_id == "reading":
        core = _reading_content(name, desc, diff, dl)
    elif sub_id == "writing-en":
        core = _writing_content(name, desc, diff, dl)
    elif sub_id == "speaking":
        core = _speaking_content(name, desc, diff, dl)
    elif sub_id == "idioms-culture":
        core = _culture_content(name, desc, diff, dl)
    else:
        core = _default_content(name, desc, diff, dl)

    if ctype == "practice":
        examples = (
            f"**练习建议**: \n"
            f"1. 先理解{name}的基本规则和常见用法\n"
            f"2. 通过模仿练习巩固基础\n"
            f"3. 在真实语境中反复运用，培养语感\n"
            f"4. 记录自己的常见错误，针对性改进"
        )
    else:
        examples = (
            f"**学习方法**: \n"
            f"1. 理解{name}的核心规则和概念\n"
            f"2. 通过大量例句感受其使用场景\n"
            f"3. 做针对性练习题检验掌握程度\n"
            f"4. 在阅读和写作中注意观察其应用"
        )
    return core, examples


def _phonetics_content(name, desc, diff, dl):
    return (
        f"{name}({desc})是英语语音学习的重要组成部分，难度为 {diff}/9({dl})。\n\n"
        f"### 核心要点\n\n"
        f"{name}的学习重点在于{desc.rstrip('。')}。\n\n"
        f"**发音技巧**:\n"
        f"- 注意口型、舌位和气流的配合\n"
        f"- 通过听音模仿(listen and repeat)反复练习\n"
        f"- 录音对比自己的发音与标准发音\n\n"
        f"**常见问题**:\n"
        f"- 中国学习者容易受母语影响出现发音偏误\n"
        f"- 注意英语中不存在于中文的音素\n"
        f"- 连续语流中的发音变化与孤立单词不同"
    )


def _grammar_content(name, desc, diff, dl):
    return (
        f"{name}({desc})是英语语法的基础概念，难度为 {diff}/9({dl})。\n\n"
        f"### 语法规则\n\n"
        f"{name}涉及以下核心规则：\n\n"
        f"1. **基本定义**: {desc}\n"
        f"2. **使用场景**: 掌握{name}的常见使用语境\n"
        f"3. **注意事项**: 留意特殊情况和例外规则\n\n"
        f"### 例句\n\n"
        f"通过对比正确和错误用法来理解{name}：\n"
        f"- ✅ 正确用法需要记住核心规则\n"
        f"- ❌ 常见错误通常源于母语负迁移\n\n"
        f"**提示**: 语法规则需要在大量阅读和写作中内化，不要只靠死记硬背。"
    )


def _vocabulary_content(name, desc, diff, dl):
    return (
        f"{name}({desc})是英语词汇学习的核心方法，难度为 {diff}/9({dl})。\n\n"
        f"### 学习策略\n\n"
        f"{name}帮助你系统地扩展词汇量：\n\n"
        f"1. **核心概念**: {desc}\n"
        f"2. **记忆技巧**: 将新词与已知词汇建立关联\n"
        f"3. **应用实践**: 在句子和语境中使用新词\n\n"
        f"### 常见示例\n\n"
        f"掌握{name}可以帮助你:\n"
        f"- 更高效地记忆和理解新单词\n"
        f"- 在阅读中更准确地推断词义\n"
        f"- 在写作中选择更精确的表达"
    )


def _tenses_content(name, desc, diff, dl):
    return (
        f"{name}({desc})是英语时态系统的重要组成，难度为 {diff}/9({dl})。\n\n"
        f"### 时态结构\n\n"
        f"{name}的核心在于{desc.rstrip('。')}。\n\n"
        f"**基本构成**: 注意助动词和主动词的形式变化\n\n"
        f"**使用场景**:\n"
        f"- 何时使用{name}\n"
        f"- 与其他时态的对比区分\n"
        f"- 时间标志词(time markers)的提示作用\n\n"
        f"### 例句对比\n\n"
        f"对比不同时态的使用可以帮助理解{name}的独特含义。\n"
        f"注意：中文没有严格的时态变化，因此需要特别注意英语时态的选择。"
    )


def _sentence_content(name, desc, diff, dl):
    return (
        f"{name}({desc})是英语句法结构的核心内容，难度为 {diff}/9({dl})。\n\n"
        f"### 句型分析\n\n"
        f"{name}的要点：{desc}\n\n"
        f"**结构特征**:\n"
        f"1. 基本构成要素与语序\n"
        f"2. 引导词和连接词的选择\n"
        f"3. 主句与从句的关系\n\n"
        f"### 实用技巧\n\n"
        f"- 先掌握基本句型，再逐步学习复杂变体\n"
        f"- 通过句子仿写练习巩固结构\n"
        f"- 阅读时注意分析长难句的层次"
    )


def _advanced_grammar_content(name, desc, diff, dl):
    return (
        f"{name}({desc})是英语高级语法的重要课题，难度为 {diff}/9({dl})。\n\n"
        f"### 深入解析\n\n"
        f"{name}的学习重点：\n\n"
        f"1. **规则详解**: {desc}\n"
        f"2. **细微差别**: 注意与基础用法的区别\n"
        f"3. **语用功能**: 在正式/非正式场合的不同表现\n\n"
        f"### 进阶应用\n\n"
        f"掌握{name}对提升英语表达的准确性和丰富度至关重要。\n"
        f"在学术写作和正式场合中，{name}的正确使用尤为重要。"
    )


def _reading_content(name, desc, diff, dl):
    return (
        f"{name}({desc})是英语阅读理解的关键技能，难度为 {diff}/9({dl})。\n\n"
        f"### 技能要点\n\n"
        f"{name}帮助你更高效地理解英语文本：\n\n"
        f"1. **核心方法**: {desc}\n"
        f"2. **实践步骤**: 从简单材料开始，逐步挑战复杂文本\n"
        f"3. **常见陷阱**: 避免逐字翻译，培养英语思维\n\n"
        f"### 练习建议\n\n"
        f"- 选择略高于当前水平的阅读材料\n"
        f"- 定期练习不同类型的文本(新闻/学术/文学)\n"
        f"- 做阅读笔记，记录新词和优美表达"
    )


def _writing_content(name, desc, diff, dl):
    return (
        f"{name}({desc})是英语写作能力的重要方面，难度为 {diff}/9({dl})。\n\n"
        f"### 写作指南\n\n"
        f"{name}的核心要求：\n\n"
        f"1. **结构规范**: {desc}\n"
        f"2. **语言质量**: 语法正确、用词准确、句式多样\n"
        f"3. **逻辑清晰**: 观点明确、论据充分、衔接自然\n\n"
        f"### 写作步骤\n\n"
        f"- **构思(Planning)**: 明确主题和结构\n"
        f"- **起草(Drafting)**: 快速写出初稿\n"
        f"- **修改(Revising)**: 优化内容和结构\n"
        f"- **校对(Proofreading)**: 纠正语法和拼写错误"
    )


def _speaking_content(name, desc, diff, dl):
    return (
        f"{name}({desc})是英语口语表达的实用技能，难度为 {diff}/9({dl})。\n\n"
        f"### 表达策略\n\n"
        f"{name}的练习重点：\n\n"
        f"1. **常用表达**: 掌握该场景下的高频句型和短语\n"
        f"2. **语音语调**: 注意自然的语音语调和停顿\n"
        f"3. **互动技巧**: 学会倾听、回应和话题转换\n\n"
        f"### 练习方法\n\n"
        f"- 影子跟读(Shadowing)提高语感和流利度\n"
        f"- 角色扮演(Role-play)模拟真实场景\n"
        f"- 录音回听分析自己的表现"
    )


def _culture_content(name, desc, diff, dl):
    return (
        f"{name}({desc})帮助你理解英语背后的文化内涵，难度为 {diff}/9({dl})。\n\n"
        f"### 文化背景\n\n"
        f"{name}的学习要点：\n\n"
        f"1. **含义解析**: {desc}\n"
        f"2. **使用场景**: 了解何时何地使用最为恰当\n"
        f"3. **文化链接**: 追溯其文化渊源和演变\n\n"
        f"### 实际运用\n\n"
        f"- 在合适的语境中自然使用，避免生硬套用\n"
        f"- 注意正式/非正式场合的区别\n"
        f"- 了解英美文化差异对表达的影响"
    )


def _default_content(name, desc, diff, dl):
    return (
        f"{name}({desc})是英语学习体系中的重要概念，难度为 {diff}/9({dl})。\n\n"
        f"### 核心内容\n\n"
        f"1. **基本概念**: {desc}\n"
        f"2. **实际应用**: 在听说读写中的体现\n"
        f"3. **学习重点**: 理解规则并通过练习内化"
    )


def generate_doc(concept, sub_name, prereqs, postreqs, templates):
    cid = concept["id"]
    name = concept["name"]
    desc = concept["description"]
    sub_id = concept["subdomain_id"]
    diff = concept["difficulty"]
    tags = concept.get("tags", [])
    is_ms = concept.get("is_milestone", False)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")

    # Try template, else generic
    if cid in templates:
        t = templates[cid]
        core, examples = t["core"], t["examples"]
    else:
        core, examples = generic_content(concept)

    prereq_list = prereqs.get(cid, [])
    postreq_list = postreqs.get(cid, [])
    rel = "## 关联知识\n\n"
    if prereq_list:
        joined = "、".join(prereq_list[:5])
        rel += f"- **先修概念**: {joined}\n  - 学习本概念前，建议先掌握以上概念\n"
    if postreq_list:
        joined = "、".join(postreq_list[:5])
        rel += f"- **后续概念**: {joined}\n  - 掌握本概念后，可以继续学习以上进阶内容\n"
    if not prereq_list and not postreq_list:
        rel += "本概念是基础起点概念，可直接开始学习。\n"

    pre_path = ""
    if prereq_list:
        pre_path = f"先回顾先修概念({'、'.join(prereq_list[:3])})，然后"

    hours_lo = max(3, diff * 2)
    hours_hi = max(8, diff * 4)
    ms_label = "里程碑" if is_ms else "重要"

    md = f"""---
id: "{cid}"
name: "{name}"
subdomain: "{sub_id}"
subdomain_name: "{sub_name}"
difficulty: {diff}
is_milestone: {"true" if is_ms else "false"}
tags: {json.dumps(tags, ensure_ascii=False)}
generated_at: "{now}"
---

# {name}

## 概述

{name}是{sub_name}领域中的{ms_label}概念，难度等级为 {diff}/9。

{desc}

## 核心内容

{core}

## 练习与实践

{examples}

{rel}
## 学习建议

- **推荐学习路径**: {pre_path}系统学习{name}的规则和用法
- **实践方法**: 多做练习，结合听说读写全面运用
- **常见误区**: 注意中英文表达差异，避免母语负迁移
- **预计学习时间**: 根据难度({diff}/9)，预计需要 {hours_lo}-{hours_hi} 小时
"""
    return md.strip() + "\n"


def main():
    seed = load_seed()
    templates = load_templates()
    sub_map = {s["id"]: s["name"] for s in seed["subdomains"]}
    prereqs, postreqs = build_edge_map(seed)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    index_docs = []
    total_chars = 0
    by_subdomain = {}

    for concept in seed["concepts"]:
        sub_id = concept["subdomain_id"]
        sub_name = sub_map.get(sub_id, sub_id)
        sub_dir = os.path.join(RAG_DIR, sub_id)
        os.makedirs(sub_dir, exist_ok=True)

        md = generate_doc(concept, sub_name, prereqs, postreqs, templates)
        fname = f"{concept['id']}.md"
        fpath = os.path.join(sub_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(md)

        cc = len(md)
        total_chars += cc
        by_subdomain[sub_id] = by_subdomain.get(sub_id, 0) + 1
        index_docs.append({
            "id": concept["id"],
            "name": concept["name"],
            "domain_id": DOMAIN_ID,
            "subdomain_id": sub_id,
            "subdomain_name": sub_name,
            "difficulty": concept["difficulty"],
            "is_milestone": concept.get("is_milestone", False),
            "tags": concept.get("tags", []),
            "file": f"{DOMAIN_ID}/{sub_id}/{fname}",
            "exists": True,
            "char_count": cc,
        })

    index_data = {
        "version": "1.0",
        "domain_id": DOMAIN_ID,
        "generated_at": now,
        "total_concepts": len(index_docs),
        "documents": index_docs,
        "stats": {
            "by_subdomain": by_subdomain,
            "total_docs": len(index_docs),
            "total_chars": total_chars,
        },
    }
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"Generated {len(index_docs)} RAG documents")
    print(f"Total chars: {total_chars:,}")
    print(f"Subdomains: {len(by_subdomain)}")
    for sid, cnt in sorted(by_subdomain.items()):
        print(f"  {sid}: {cnt}")


if __name__ == "__main__":
    main()
