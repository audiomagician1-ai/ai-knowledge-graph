"""Find Tier-C docs that are most referenced as prerequisites by other docs."""
import os, re
from collections import defaultdict

root = r'D:\EchoAgent\projects\ai-knowledge-graph\data\rag'

# Step 1: Build concept->file mapping and identify Tier-C docs
concept_to_file = {}
tier_c_concepts = set()
file_tier = {}

for dp, dn, fn in os.walk(root):
    for f in fn:
        if not f.endswith('.md'): continue
        path = os.path.join(dp, f)
        content = open(path, 'r', encoding='utf-8').read()
        # Extract concept name from frontmatter
        m = re.search(r'concept:\s*"(.+?)"', content)
        if m:
            concept = m.group(1)
            concept_to_file[concept] = os.path.relpath(path, root)
            if 'quality_tier: "C"' in content:
                tier_c_concepts.add(concept)
                file_tier[concept] = 'C'
            elif 'quality_tier: "B"' in content:
                file_tier[concept] = 'B'
            elif 'quality_tier: "S"' in content:
                file_tier[concept] = 'S'

# Step 2: Count how many docs reference each concept as prerequisite
dep_count = defaultdict(int)
for dp, dn, fn in os.walk(root):
    for f in fn:
        if not f.endswith('.md'): continue
        path = os.path.join(dp, f)
        content = open(path, 'r', encoding='utf-8').read()
        prereqs = re.findall(r'\*\*(.+?)\*\*\s*[—\-]', content)
        for p in prereqs:
            dep_count[p] += 1

# Step 3: Rank Tier-C concepts by dependency count
tier_c_ranked = [(c, dep_count.get(c, 0)) for c in tier_c_concepts]
tier_c_ranked.sort(key=lambda x: -x[1])

print(f"Total Tier-C concepts: {len(tier_c_concepts)}")
print(f"\nTop 30 most-depended-on Tier-C docs:")
for concept, count in tier_c_ranked[:30]:
    filepath = concept_to_file.get(concept, '?')
    print(f"  {count:3d} deps | {concept:30s} | {filepath}")
