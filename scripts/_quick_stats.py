"""Quick quality stats checker."""
import json, os, glob

tiers = {'S': 0, 'A': 0, 'B': 0, 'C': 0}
scores = []
total = 0

for detail_file in glob.glob('data/rag/*/quality_details.json'):
    with open(detail_file) as f:
        details = json.load(f)
    for doc in details:
        total += 1
        score = doc.get('score', 0)
        scores.append(score)
        if score >= 80: tiers['S'] += 1
        elif score >= 60: tiers['A'] += 1
        elif score >= 40: tiers['B'] += 1
        else: tiers['C'] += 1

avg = sum(scores)/len(scores) if scores else 0
print(f'Total docs: {total}')
print(f'Average score: {avg:.1f}')
print(f'S (80+): {tiers["S"]} ({tiers["S"]*100/total:.1f}%)')
print(f'A (60-79): {tiers["A"]} ({tiers["A"]*100/total:.1f}%)')
print(f'B (40-59): {tiers["B"]} ({tiers["B"]*100/total:.1f}%)')
print(f'C (<40): {tiers["C"]} ({tiers["C"]*100/total:.1f}%)')

# Count Tier-B remaining
tier_b_ids = []
for detail_file in glob.glob('data/rag/*/quality_details.json'):
    with open(detail_file) as f:
        details = json.load(f)
    for doc in details:
        score = doc.get('score', 0)
        if 40 <= score < 60:
            tier_b_ids.append(doc.get('id', '?'))

print(f'\nTier-B remaining: {len(tier_b_ids)}')

# Check what was already upgraded
progress_file = 'data/tier_b_upgrade_progress.json'
if os.path.exists(progress_file):
    with open(progress_file) as f:
        progress = json.load(f)
    completed = set(progress.get('completed', []))
    print(f'Already upgraded: {len(completed)}')
    # How many Tier-B are NOT yet in completed?
    still_tier_b = [x for x in tier_b_ids if x not in completed]
    print(f'Tier-B not yet upgraded (still scoring 40-59): {len(still_tier_b)}')
