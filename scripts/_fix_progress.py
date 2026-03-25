#!/usr/bin/env python3
"""One-shot: sync progress file with actual completed slugs from git."""
import json
from pathlib import Path

PROGRESS = Path(__file__).resolve().parent.parent / "data" / "tier_b_upgrade_progress_s6.json"

new_slugs = [
    'apoptosis','framing-effects','new-institutional','regional-integration','trade-wars',
    'factor-markets','articles-advanced','infinitive-phrases','simple-future','latin-greek-roots',
    'smart-contracts','credit-spread','capm-model','quant-finance-overview','pb-ratio',
    'stock-market-overview','level-scaling','power-curve','design-pillars','design-review',
    'one-pager','pitch-deck','battle-pass','ui-feedback','variable-reward','roguelike-design',
    'social-hooks','social-space','quest-system','playable-path','asset-list','handoff-doc',
    'iteration-log','macro-pacing','theme-variation','natural-numbers','gradient-directional',
    'inverse-matrix','null-column-row-spaces','quadratic-residues','law-of-sines','art-form',
    'democritus','foundationalism','paradigm-shift','mind-body-problem','deconstruction',
    'hermeneutics','wittgenstein','twin-paradox','value-proposition','ethnographic-research',
    'think-aloud-protocol','sexual-behavior-biology','mindfulness','flash-fiction','genre-fiction',
    'fact-checking','dialogue-writing','narrative-arc','pacing-rhythm','travel-writing',
    'call-to-action','logos-strategies','proposal-writing','style-consistency','writing-process',
    'navier-stokes-intro','thermodynamic-processes','quantum-computing-intro',
    'quantum-harmonic-oscillator','marketplace-growth','product-metrics-review',
    'qualitative-methods','obedience','skimming','small-talk','digital-banking','digital-currency',
    'version-control-docs','social-insurance','quadratic-functions','biofilm',
    'industrial-microbiology','postmodernism','review-writing','plant-hormones',
    'active-passive-voice','vorticity','general-relativity-intro','experiment-design',
    'cohort-analysis','flow-theory',
]

p = json.load(open(PROGRESS, 'r', encoding='utf-8'))
existing = set(p.get('completed', []))
added = 0
for s in new_slugs:
    if s not in existing:
        p['completed'].append(s)
        added += 1
p['done'] = len(p['completed'])
json.dump(p, open(PROGRESS, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"Added {added} slugs, total completed now: {p['done']}")
