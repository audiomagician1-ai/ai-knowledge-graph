import os, json
RAG = r"D:\EchoAgent\projects\AI-Knowledge-Graph\data\rag"
v2 = non_v2 = 0
for root, dirs, files in os.walk(RAG):
    for f in files:
        if not f.endswith(".md"): continue
        with open(os.path.join(root, f), "r", encoding="utf-8") as fh:
            head = fh.read(600)
        if "quality_method: intranet-llm-rewrite-v2" in head: v2 += 1
        else: non_v2 += 1
total = v2 + non_v2
print(f"v2: {v2} ({v2*100/total:.1f}%) | non-v2: {non_v2} | total: {total}")
for name, path in [("S6", r"data\tier_b_upgrade_progress_s6.json"), ("S6.5", r"data\sprint6_5_progress.json")]:
    p = os.path.join(r"D:\EchoAgent\projects\AI-Knowledge-Graph", path)
    if os.path.exists(p):
        d = json.load(open(p, "r", encoding="utf-8"))
        rem = len([s for s in d.get("queue",[]) if s not in set(d.get("completed",[]))])
        print(f"{name}: done={d['done']}, remaining={rem}, errors={len(d.get('error_slugs',[]))}")
