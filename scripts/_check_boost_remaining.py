"""Check remaining low-score RAG documents for Legacy Boost."""
import json, os

prog_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'legacy_boost_progress.json')
scores_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'rag_quality_scores.json')

prog = json.load(open(prog_path, 'r', encoding='utf-8'))
done = set(prog.get('completed', []))
print(f"Already boosted: {len(done)}")

if not os.path.exists(scores_path):
    print("No scores file found — run quality_scorer.py first")
    exit(1)

scores = json.load(open(scores_path, 'r', encoding='utf-8'))
new_domains = {'systems-theory','cybernetics','information-theory','dissipative-structures','synergetics','catastrophe-theory'}

legacy = []
for k, v in scores.items():
    domain = k.split('/')[0]
    if domain in new_domains:
        continue
    if k in done:
        continue
    score = v.get('score', v) if isinstance(v, dict) else v
    legacy.append((k, score))

legacy.sort(key=lambda x: x[1])

print(f"\nBottom 30 remaining:")
for k, s in legacy[:30]:
    print(f"  {s:5.1f}  {k}")

below_75 = sum(1 for _, s in legacy if s < 75)
below_70 = sum(1 for _, s in legacy if s < 70)
print(f"\nRemaining below 75: {below_75}")
print(f"Remaining below 70: {below_70}")
print(f"Total remaining (non-boosted legacy): {len(legacy)}")
