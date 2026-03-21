#!/usr/bin/env python3
"""Generate RAG docs for game-qa knowledge sphere."""
import json, os

SEED = os.path.join(os.path.dirname(__file__), "..", "data", "seed", "game-qa", "seed_graph.json")
RAG_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "rag", "game-qa")

with open(SEED, "r", encoding="utf-8") as f:
    data = json.load(f)

sub_map = {s["id"]: s["name"] for s in data["subdomains"]}
os.makedirs(RAG_DIR, exist_ok=True)

index_entries = []

for c in data["concepts"]:
    cid = c["id"]
    name = c["name"]
    desc = c["description"]
    sub_name = sub_map.get(c["subdomain_id"], c["subdomain_id"])
    diff = c["difficulty"]
    minutes = c["estimated_minutes"]
    is_ms = c["is_milestone"]

    diff_label = ["", "入门", "基础", "进阶", "高级", "专家"][diff]
    milestone_note = "\n> 🎯 **里程碑概念** — 掌握本概念是该子领域的关键进阶节点。\n" if is_ms else ""

    content = f"""---
id: "{cid}"
title: "{name}"
domain: "game-qa"
subdomain: "{c['subdomain_id']}"
difficulty: {diff}
estimated_minutes: {minutes}
is_milestone: {"true" if is_ms else "false"}
---

# {name}

> **子领域**: {sub_name} | **难度**: {diff_label} | **预计学习时间**: {minutes}分钟
{milestone_note}
## 概述

{desc}。

## 核心要点

### 1. 基本概念

{name}是游戏QA测试中{sub_name}领域的{"核心" if is_ms else "重要"}知识点。理解这一概念对于保证游戏质量、减少线上缺陷至关重要。

### 2. 实践方法

在实际游戏项目中，{name}通常需要：
- 制定明确的测试策略和计划
- 选择合适的工具和方法论
- 建立可量化的质量标准
- 持续迭代改进测试流程

### 3. 常见挑战

游戏{name}面临的典型挑战包括：
- 游戏系统的复杂性和状态空间爆炸
- 测试环境与真实玩家环境的差异
- 时间压力下的测试覆盖率取舍
- 不同平台和设备的差异化表现

## 与其他概念的关系

{name}与{sub_name}子领域中的其他概念紧密相关。掌握本概念有助于理解更高级的测试策略和方法论。

## 学习建议

{"作为里程碑概念，建议深入学习并在实际项目中反复练习。" if is_ms else "建议结合实际项目经验逐步掌握。"}理解{name}的原理后，尝试在自己的游戏项目中应用所学知识。
"""

    filepath = os.path.join(RAG_DIR, f"{cid}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    index_entries.append({
        "id": cid,
        "title": name,
        "file": f"{cid}.md",
        "subdomain": c["subdomain_id"],
        "difficulty": diff,
        "is_milestone": is_ms
    })

# Build stats
from collections import Counter
sub_counts = Counter(c["subdomain_id"] for c in data["concepts"])
total_chars = 0
for entry in index_entries:
    filepath = os.path.join(RAG_DIR, entry["file"])
    total_chars += os.path.getsize(filepath)

by_subdomain = {}
for sid, count in sub_counts.items():
    by_subdomain[sid] = {"docs": count, "name": sub_map.get(sid, sid)}

import datetime
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

# Write _index.json
with open(os.path.join(RAG_DIR, "_index.json"), "w", encoding="utf-8") as f:
    json.dump({
        "version": "1.0",
        "domain": "game-qa",
        "domain_name": "QA测试",
        "generated_at": now,
        "total_concepts": len(index_entries),
        "stats": {
            "total_docs": len(index_entries),
            "total_chars": total_chars,
            "by_subdomain": by_subdomain,
        },
        "documents": index_entries
    }, f, ensure_ascii=False, indent=2)

print(f"Generated {len(index_entries)} RAG docs + _index.json in {RAG_DIR}")
