"""Fix software-engineering seed_graph.json: add edges for disconnected nodes + improve topology."""
import json
import os
from collections import defaultdict, Counter

SEED_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "seed", "software-engineering", "seed_graph.json")


def main():
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    concepts = data["concepts"]
    edges = data["edges"]
    id_to_c = {c["id"]: c for c in concepts}

    # Find connected nodes
    connected = set()
    for e in edges:
        connected.add(e["source"])
        connected.add(e["target"])

    disconnected = set(id_to_c.keys()) - connected
    print(f"Before fix: {len(concepts)} concepts, {len(edges)} edges, {len(disconnected)} disconnected")

    # Group all concepts by subdomain, sorted by difficulty then order in list
    by_sub = defaultdict(list)
    for c in concepts:
        by_sub[c["subdomain_id"]].append(c)

    # Build edge set for dedup
    edge_set = {(e["source"], e["target"]) for e in edges}

    new_edges = []

    def add_edge(src, tgt, etype="prerequisite"):
        if (src, tgt) not in edge_set and (tgt, src) not in edge_set and src != tgt:
            new_edges.append({"source": src, "target": tgt, "type": etype})
            edge_set.add((src, tgt))
            connected.add(src)
            connected.add(tgt)
            return True
        return False

    # Phase 1: Connect disconnected nodes to closest difficulty neighbor in same subdomain
    for sub_id, sub_concepts in by_sub.items():
        # Sort by difficulty, then by position in the original list
        sorted_c = sorted(sub_concepts, key=lambda x: (x["difficulty"], sub_concepts.index(x)))

        for i, c in enumerate(sorted_c):
            if c["id"] not in disconnected:
                continue

            # Find the nearest connected predecessor (lower difficulty or same difficulty earlier)
            best = None
            for j in range(i - 1, -1, -1):
                prev = sorted_c[j]
                if prev["id"] in connected:
                    best = prev
                    break

            if best:
                add_edge(best["id"], c["id"])
            else:
                # No predecessor found, try connecting to next connected node
                for j in range(i + 1, len(sorted_c)):
                    nxt = sorted_c[j]
                    if nxt["id"] in connected:
                        add_edge(c["id"], nxt["id"])
                        break

    # Phase 2: Add sequential chains within each subdomain to improve topology spread
    # For each subdomain, add chain links between same-difficulty consecutive nodes
    for sub_id, sub_concepts in by_sub.items():
        sorted_c = sorted(sub_concepts, key=lambda x: (x["difficulty"], sub_concepts.index(x)))
        for i in range(len(sorted_c) - 1):
            a = sorted_c[i]
            b = sorted_c[i + 1]
            if a["difficulty"] == b["difficulty"]:
                add_edge(a["id"], b["id"], "related")

    # Report
    still_disc = set(id_to_c.keys()) - connected
    data["edges"] = edges + new_edges
    new_total = len(data["edges"])
    ratio = new_total / len(concepts)
    print(f"After fix: {len(concepts)} concepts, {new_total} edges (+{len(new_edges)}), ratio={ratio:.2f}")
    print(f"Disconnected: {len(still_disc)}")

    # Check hub degree
    deg = Counter()
    for e in data["edges"]:
        deg[e["source"]] += 1
        deg[e["target"]] += 1
    top5 = deg.most_common(5)
    print("Top 5 degree nodes:")
    for nid, cnt in top5:
        c = id_to_c[nid]
        print(f"  {nid}: degree={cnt} milestone={c.get('is_milestone')} sub={c['subdomain_id']}")

    with open(SEED_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved!")


if __name__ == "__main__":
    main()
