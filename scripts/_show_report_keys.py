import json
d = json.load(open("data/quality_report_detail.json", encoding="utf-8"))
print("Type:", type(d))
print("Keys:", list(d.keys()))
if "docs" in d:
    print("docs type:", type(d["docs"]))
    print("docs[0]:", d["docs"][0] if d["docs"] else "empty")
elif "documents" in d:
    print("documents type:", type(d["documents"]))
elif isinstance(d, dict):
    for k in d:
        v = d[k]
        if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict):
            print(f"Found list of dicts at key '{k}': {len(v)} items")
            print(f"First item keys: {list(v[0].keys())}")
            break
